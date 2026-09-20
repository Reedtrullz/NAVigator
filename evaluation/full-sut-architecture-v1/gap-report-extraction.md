# Gap Report Extraction

Source read in full:
evaluation/measurement-v3-combined-freeze/full-sut-gap-report.md

## 1. Expected SUT interfaces (measurement -> SUT)

1. Raw answer object per item with minimum fields: routes (list), claims
   (list), uncertainty_expressed (list), evidence (dict field to value),
   execution_status. Consumed by dev-corpus-scorer-v1 scorer.py via
   _normalize_raw_answer, which rejects the item (returns None) if any of the
   four collection fields are missing or mistyped.
2. Capability flags per domain: safety / routing / local_discovery. The scorer
   maps corpus family to capability key via GOLD_KEY_BY_CORPUS
   (safety_cases -> safety, routing_cases -> routing,
   discovery_adversarial_cases -> local_discovery) and emits
   NOT_APPLICABLE_TO_SUT when the flag is absent or false.
3. SUT output text per semantic item (sut_output) for the M2 and V2.15
   human-review lanes. V3 run_scorer_item serializes the raw answer JSON as
   sut_output. Evidence spans in those lanes are validated as verbatim
   substrings of sut_output.
4. Case/gold metadata per item: safety_priority, critical_error_if,
   acceptable_routes, forbidden_claims, required_uncertainty,
   required_evidence_fields (scorer contract v1 GOLD_FIELDS).
5. M2-workflow classification for critical-condition items (which cases enter
   the M2 lane rather than the generic lane).
6. Item identity + provenance sufficient for single-owner routing and audit.

## 2. Missing product runtime pieces

Per the gap report, confirmed against the repo:

- The product runtime itself: query handling, retrieval / local-discovery
  integration, answer generation, and the glue that emits the raw answer
  object. The frozen discovery lineages (V2.x) cover evidence discovery only
  and are not wired to any answer path.
- A corpus loader that turns dev-corpus-v1 into scored cases with gold
  metadata at runtime.
- M2-workflow routing metadata on corpus items (currently synthetic).

## 3. Missing corpus/data loader

dev-corpus-v1 cases live in evaluation/dev-corpus-v1/cases/ as three JSON
files (safety_cases 20, routing_cases 75, discovery_adversarial_cases 25;
120 total). Each file is an object with keys corpus, family, data_status,
scoring_model, case_count, cases. Each case has id, source_line, utterance,
profile, gold. The loader must strip the gold object (and only it) before SUT
execution; the scorer is the only gold reader.

## 4. Missing routing metadata

M2-workflow classification for critical-condition items does not exist as
corpus metadata. Until it does, the combined engine cannot route M2 items
from corpus data alone. Architecture decision (ADR-004 / measurement mapping):
classification is an evaluator-side concern; the SUT never emits it. Phase 3
or a follow-up evaluator task owns adding it to the corpus files.

## 5. Gap report proposed phases (authoritative starting point)

1. Phase 1: corpus loader + answer-schema adapter so the frozen scorer can run
   against the existing 120-case dev corpus end to end.
2. Phase 2: wire the frozen local-discovery V2.4 candidate as the evidence
   provider behind the answer generator, keeping provenance and fail-closed
   semantics.
3. Phase 3: human-review lane ingestion UI/CLI for M2 + generic lanes. Only
   after those exist does a full SUT baseline become runnable, at which point a
   new blind/holdout task can be drafted separately.

Adaptation adopted in this architecture: gap-report Phase 1 (loader + schema
adapter) and Phase 2 (discovery wiring) are kept. The gap-report Phase 3
(human-review ingestion UI/CLI) is an evaluator-side tool, so the SUT
implementation plan keeps three product-side phases (skeleton, pipeline,
end-to-end) and moves lane ingestion to a separate follow-up evaluator task.
This preserves the gap-report phase 1-2 intent and its ordering without
letting evaluator tooling leak into the product runtime.

## 6. Prerequisites named by the gap report

- Measurement V3 combined freeze intact (verified: baseline-integrity.json).
- Frozen scorer contract v1 intact (not modified in this task).
- Frozen discovery V2.4/V2.5 lineages intact (reused, not modified).
- dev-corpus-v1 integrity (120 cases; loader will verify counts and SHAs).

## 7. Unresolved architecture questions answered by this task

| Question from gap-report space | Resolved in |
|---|---|
| What exactly is the SUT boundary? | sut-boundary.md, ADR-001 |
| How does output map to scorer/V3 inputs? | measurement-v3-mapping.md |
| How is discovery reused without copying? | local-discovery-interface.md, ADR-005 |
| Where does safety routing live? | canonical-pipeline.md, ADR-002/006 |
| Who reads gold? | corpus-loader-design.md, execution-harness-design.md |
| Does product need human review? | product-vs-measurement-boundary.md (no) |
