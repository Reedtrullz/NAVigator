# Annotation Summary - RC3.3.2 Fresh Micro-Validation

Task: NAV-EXPLORE-RC3_3_2-FRESH-MICROVALIDATION-CONSTRUCTION
Final annotation status: ANNOTATION_CONTRACT_NOT_READY / MICROVALIDATION_NOT_READY

## Method

30 fresh cases (RC33M2-001..030) authored mechanically with embedded pass-1
gold, KB spans verified 64/64, novelty max similarity 0.375, quota exact.
Pass 2 was run as an independent GPT-5.6-Luna annotation via the local proxy
(model command-code/gpt-5.6-luna, temperature 0), seeing only public case
data. Pass 1 was never exposed to pass 2.

Two pass-2 implementations were run (the bounded one-repair allowance):

1. Original contract: semantic enum SUPPORTED / CONTRADICTED /
   PARTIALLY_SUPPORTED / INSUFFICIENT_EVIDENCE.
2. Repaired contract: REVIEW_REQUIRED added to the enum with explicit
   guidance, plus an aggregate-arithmetic rule for sum claims.

## Agreement Results (spec 15)

Repaired pass 2 (authoritative run, 2026-09-08):

| Field | Agreement | Applicable | Gate | Verdict |
|---|---|---|---|---|
| semantic_relation | 66.67% (20/30) | 30 | >=90% | FAIL |
| semantic_quantity_identity | 50.00% (12/24) | 24 | >=95% | FAIL |
| temporal_applicability | 70.00% (21/30) | 30 | >=90% | FAIL |
| comparator_applicable | 54.17% (13/24) | 24 | >=95% | FAIL |
| comparator_relation | 15.38% (2/13) | 13 | >=95% | FAIL |
| aggregate_component_role | 93.33% (28/30) | 30 | (none) | - |

The first (pre-repair) pass-2 run produced identical semantic agreement
(20/30, 66.67%).

## Dispute Taxonomy

Semantic relation disputes (10):

- 9 cases where pass-1 gold is REVIEW_REQUIRED (the RBI bucket):
  Luna answered INSUFFICIENT_EVIDENCE (7), PARTIALLY_SUPPORTED (2),
  CONTRADICTED (1). Even with REVIEW_REQUIRED explicitly offered in the
  repaired enum, Luna used it 0 times across all 30 cases. These are
  quota-driven RBI cases the independent model does not reproduce.
- 1 genuine engine-judgment dispute: RC33M2-003 (aggregate total 2392 vs
  component sum 2292). Luna declined to compute the component sum even
  with the explicit arithmetic rule, answering INSUFFICIENT_EVIDENCE.

Non-semantic dispute kinds (counts across 30 cases):

- 4 quantity "disputes" are format artifacts only: pass-1 gold uses the
  4-segment form TYPE:VALUE:UNIT:QUALIFIER while the pass-2 prompt
  documented TYPE:VALUE:UNIT (e.g. MONEY:2292:NOK:AGGREGATE vs
  MONEY:2292:NOK). The agreement script compares strings verbatim.
- 8 substantive quantity disputes (wrong component or central value).
- 9 temporal disputes (Luna systematically over-answered UNKNOWN where
  the packet establishes the applicable rule).
- 11 comparator-applicability disputes (Luna under-flagged claims whose
  wording asserts a comparison, e.g. "minst"/"na").
- 2 aggregate-component-role disputes.

Even after excluding the 4 pure format artifacts, every gated field
remains well below its gate.

## Decision

Spec 15 is a hard stop: semantic pre-adjudication agreement <90% requires
ANNOTATION_CONTRACT_NOT_READY and forbids adjudicating an unclear
contract to green. Spec 40 therefore yields MICROVALIDATION_NOT_READY.

Not done, deliberately:

- Pass-1 gold was NOT rewritten toward pass-2 (would destroy the RBI
  quota design from the approved case plan).
- No third pass-2 prompt iteration (two implementations are the bounded
  allowance; further prompt tuning toward agreement would be
  tuning-to-green).
- No adjudication run (forbidden while the pre-adjudication gate fails).
- Nothing sealed; no answer key created; no key material exists.

Plaintext pass-1 and pass-2 labels remain in construction-audit/ as
construction evidence; cleanup is a seal-path step that was not reached.

## What a Retry Requires

The failure is a contract mismatch between annotators, not a case-set
defect. Before any future pass-2 rerun, a shared written field contract
must be frozen first, covering at minimum:

1. semantic_relation enum: whether REVIEW_REQUIRED is in the annotation
   vocabulary and, if so, its exact boundary vs INSUFFICIENT_EVIDENCE
   and PARTIALLY_SUPPORTED, with worked examples.
2. semantic_quantity_identity canonical form (3- vs 4-segment) and
   which quantity is "central" for multi-quantity claims.
3. temporal_applicability: precise UNKNOWN criteria vs CURRENT_MATCH
   when the packet states a current rule without dates.
4. comparator_applicability: enumerated claim-wording triggers
   ("na", "minst", "mer enn", "ikke over", "innen") with positive and
   negative examples, including that age thresholds in rule text do
   not make a comparator applicable.
5. Aggregate arithmetic duty: annotator must compute component sums.

The pass-1 gold author and pass-2 model must annotate against that same
frozen contract text; the prompt should embed it verbatim rather than
paraphrasing it.
