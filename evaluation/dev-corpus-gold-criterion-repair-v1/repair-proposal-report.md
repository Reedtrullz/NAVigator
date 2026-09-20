# Repair proposal report - NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1

## Terminal status

DEV_CORPUS_GOLD_CRITERION_REPAIR_PROPOSAL_READY_AWAITING_OWNER_APPROVAL

## Scope and authorization

Phase A proposal generation only. Phase B (gold rewrite, packet regeneration, review ingest, re-scoring) is NOT authorized in this lineage and requires a new explicit owner task.

## Defects

The frozen criterion-semantic-completeness audit (sha256 30617325610982be4131fbca8c4cc7a7f5b25312c9e0194bc455fdca9d9571bb) found 3 SEMANTICALLY_UNDERSPECIFIED forbidden_claim criteria, all noun-phrase fragments without a predicate:

- PKT-ESC-ROUT-061 / ROUT-061: "barnevernet automatisk"
- PKT-ESC-ROUT-070 / ROUT-070: "barnevernet automatisk"
- PKT-ESC-ROUT-073 / ROUT-073: "barnevern automatisk"

## Historical gold preservation

The historical frozen strings are preserved verbatim in this report, in the TASK-LOCK, in the repair-input-manifest, and in the frozen corpus. No claim is made that any historical frozen artifact contained the full propositions proposed here. The proposed propositions are repair candidates, not recovered historical text.

## Deterministic results impact

Verified against evaluation/measurement-v3-burned-baseline-v1/deterministic-scores.json: all three criteria are HUMAN_REVIEW_PENDING, so no deterministic verdict exists for them.

DETERMINISTIC_RESULTS_AFFECTED = 0

## Candidate inventory

9 candidates across 3 packets are proposed in criterion-repair-candidates.json:

- 3 FROZEN_SUPPORTED_DIRECTION candidates (R061-A, R070-A, R073-A), one per case, recommended.
- 4 NEW_GOLD_AUTHORING candidates (R061-B, R070-B, R070-C, R073-B), requiring explicit owner authorization as new gold.
- 2 NOT_RECOMMENDED_ACCIDENTAL_BROADENING candidates (R070-D, R073-C), any-mention readings, documented and rejected.

Cross-case analysis is in cross-case-consistency.json: three separate scenario-specific conditions in one behavior family; identical global wording rejected; 0 duplicates and 0 contradictions across the corpus; the ROUT-061 overlap between the forbidden lane and critical_error_if is documented, not silently merged.

## Owner decision required

The owner must choose exactly one candidate per case (recommended: R061-A, R070-A, R073-A). Any NEW_GOLD_AUTHORING choice must be explicitly accepted as new gold authoring, not as recovered semantics.

## Phase B preconditions (not started here)

Phase B, if separately authorized, must: rewrite exactly the three chosen gold fields in a new lineage, regenerate the three packets, re-run leakage and integrity checks, ingest OWNER-01 human reviews against the new packets, and only then re-run scoring. None of that has happened in this task.

## Invariants

- ORIGINAL_CORPUS_MUTATED = false
- ORIGINAL_GOLD_MUTATED = false
- ORIGINAL_REVIEW_PACKETS_MUTATED = false
- ORIGINAL_BASELINE_MUTATED = false
- EXPECTED_GOLD_FIELDS_CHANGED = 3 (only if owner approves and a Phase B task rewrites them; 0 changed so far)
- DETERMINISTIC_RESULTS_AFFECTED = 0
- OWNER_01_REVIEWS_COMPLETED = 0
- SEMANTIC_VERDICTS_DERIVED = 0
- SUT_RERUN = false
- PREDICTIONS_CHANGED = false
- WEB_RESEARCH_USED = false
- GPT_5_5_USED = false
- SUBAGENTS_USED = 0
