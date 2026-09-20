# Corpus Loader Design

Evaluator-side module: evaluation/full-sut-implementation/sut_runner/loader.py
(created in Phase 1; not part of the product runtime). The loader is the only
component that touches gold before scoring, and its only gold operation is
stripping.

## Responsibilities

1. Load a dev-corpus-v1 case file (JSON object with corpus, family,
   data_status, scoring_model, case_count, cases[]).
2. Verify integrity: case_count matches len(cases); corpus and family match
   the file registry; per-file SHA-256 matches the pinned manifest
   (data-status registry in this directory).
3. For each case, build the SUT input:

       {
         "case_id": case["id"],
         "user_query": case["utterance"],
         "profile": case["profile"],
         "context": {},
         "location_context": {},
         "timestamp_context": {"executed_at": harness execution timestamp}
       }

4. Strip gold: the gold object and scorer metadata do not enter the SUT input
   object at all. location_context is deliberately empty in Phase 1 (discovery
   corpus cases are adversarial about missing locality; the loader never
   fabricates municipalities).
5. Emit (gold_stripped_input, gold_envelope) pairs where gold_envelope is
   opaque bytes stored encrypted-at-rest by the harness and unread by the
   runner process until scoring.

## API

    load_corpus(case_file, *, sha_registry) -> CorpusFile
    strip_gold(case) -> SutInput        # raises GoldLeakError on unknown keys
    iter_inputs(corpus_file) -> Iterator[SutInput]

GoldLeakError fires if a stripped object contains any key from
GOLD_FIELDS (safety_priority, acceptable_routes, forbidden_claims,
required_uncertainty, required_evidence_fields, critical_error_if) or the key
gold itself. The guard runs on the serialized JSON of the object, not the
Python view, so nested leaks cannot slip through.

## Hard invariant

    GOLD_VISIBLE_TO_SUT = 0

Enforced by: (a) strip_gold key guard, (b) harness self-test that runs a
probe input through the SUT factory with a monkeypatched knowledge layer
asserting no gold key appears in any SUT-side structure, (c) prediction files
store gold only in the separate encrypted envelope.

## Future holdout compatibility

Future holdout corpora use the same case shape (id, utterance, profile, gold).
The loader accepts any file matching the shape + integrity registry; no
corpus-specific branching beyond the family registry mapping
(GOLD_KEY_BY_CORPUS equivalent stays scorer-side).

## Individual case execution

    python -m sut_runner.load_case --case-file ... --case-id ROUT-021

prints the gold-stripped SUT input JSON. This is the interactive debug path
for Phase 2/3 development; it physically cannot print gold because the input
never contains it.
