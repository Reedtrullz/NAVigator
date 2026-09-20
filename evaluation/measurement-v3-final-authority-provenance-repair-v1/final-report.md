# MEASUREMENT V3 - FINAL AUTHORITY PROVENANCE REPAIR V1

Task ID: NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1
Date: 2026-09-16
Authorization: explicit owner authorization (provenance-only repair)
Baseline classification: BURNED_DEV_BASELINE_ONLY

## Finding

The terminal frozen baseline
(evaluation/measurement-v3-residual-human-adjudication-v1/,
terminal status MEASUREMENT_V3_BURNED_BASELINE_COMPLETE) classified two criteria
as HUMAN_REVIEWED with reviewer attribution OWNER-01:

- ROUT-025::forbidden:01
- ROUT-066::forbidden:01

Post-freeze owner audit established that the semantic observations for both
criteria originated from ChatGPT/LLM: the adjudication payloads were produced
by ChatGPT in the conversation and transcribed by the owner, not decided by
the human owner. The historical misclassification is preserved, not erased.

## Scope Discipline

This task corrected authority provenance only.

- SEMANTIC_OBSERVATIONS_CHANGED = false
- DERIVED_VERDICTS_CHANGED = false
- AGGREGATE_RESULT_VALUES_CHANGED = false (semantic values unchanged)
- SUT_RERUN = false
- GOLD_CHANGED = false
- PACKETS_CHANGED = false
- MEASUREMENT_CONTRACT_CHANGED = false
- LLM semantic review calls = 0
- Human review calls = 0

The derivation script asserts that, with authority and provenance fields
removed, the two corrected rows are identical to the frozen originals, that
verdict/status are unchanged (both ABSENT via M1:NEGATED), and that no other
row differs from the upstream freeze.

## Verified Frozen State (pre-repair)

- Old lineage hashes: shasum -a 256 -c over
  evaluation/measurement-v3-residual-human-adjudication-v1/hashes.txt
  re-verified 16/16 OK before correction; old lineage not mutated.
- Old combined-complete SHA-256: 5c87bf07b59e58af3d78222500b94153d6db8b72892f978d1a0d585c4893fc12
- Old aggregate-complete SHA-256: 46ff5ee83e12f6462e5e3ca2c5c37c1d69afa9017842dccd6991ee748e276c82
- Old TASK-LOCK: CLOSED / MEASUREMENT_V3_BURNED_BASELINE_COMPLETE (preserved, now superseded historical freeze)
- Derivation kernel judge_core_v2_13.py SHA-256:
  66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682
- Upstream Astra combined SHA-256:
  45d078d6c8ee4e962e987381670d3ea412df5a6fbf326df0f728119137aed18d

## Correction Applied

Existing canonical fields expressed the correction; no schema change was
required, so the stop condition
AUTHORITY_PROVENANCE_SCHEMA_REPAIR_REQUIRED was not triggered.

For both target rows:

- authority: HUMAN_REVIEWED -> LLM_ADJUDICATED
- authority_subtype: CHATGPT_SINGLE_REVIEW_RESIDUAL
- observation_source: CHATGPT_SINGLE_REVIEW_RESIDUAL
- observation_model: chatgpt
- provenance_correction markers: PROVENANCE_CORRECTED_FROM_HUMAN_REVIEWED_2026-09-16,
  prior_misclassified_as HUMAN_REVIEWED/OWNER-01
- reviewer field removed; prior human-attribution hashes marked SUPERSEDED
  with pointer to repair-record.json (files retained as historical trace)

Semantic observations retained unchanged:

- ROUT-025: criterion_semantic_match=MATCH, speaker_commitment=NEGATED
- ROUT-066: criterion_semantic_match=MATCH, speaker_commitment=NEGATED

Derived verdicts retained unchanged: ABSENT (M1:NEGATED) for both.

## Final Authority Mix

- DETERMINISTIC: 526
- LLM_REVIEWED: 64
- LLM_ADJUDICATED: 10
  - DUAL_PASS_ASTRA_RESIDUAL: 8
  - CHATGPT_SINGLE_REVIEW_RESIDUAL: 2
- HUMAN_REVIEWED: 0
- PENDING: 0
- TOTAL: 600

Total LLM authority = 74. No criterion in this baseline was decided by a
human.

## Aggregates

Only authority-dependent aggregate metadata was recomputed:

- TOTAL_CRITERIA = 600
- AUTHORITATIVE_TOTAL = 600 (100%)
- Case coverage 120/120, 0 pending cases
- Semantic verdict counts unchanged

## Historical Trace Preservation

- The original terminal freeze remains on disk and is referenced as
  SUPERSEDED_HISTORICAL_NOT_DELETED.
- human-adjudications.jsonl in the old lineage is retained unchanged as the
  historical trace of the LLM-origin observations and the incorrect
  human attribution.
- repair-record.json in this lineage states the finding, discovery,
  correction, invariants, and old-lineage integrity verification.

## Freeze

Terminal freeze artifacts in this lineage:

- combined-measurement-results-complete-provenance-corrected.json
- authority-map-provenance-corrected.json
- combined-aggregate-metrics-provenance-corrected.json
- repair-record.json
- TASK-LOCK.json (closed)
- README.md, final-report.md
- final-freeze-manifest.json, hashes.txt, closure-log.json

See hashes.txt for SHA-256 pins and closure-log.json for the freeze
verification record. All pins verified from repo root.

## Status

MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED

## Non-Claims

This baseline remains BURNED_DEV_BASELINE_ONLY. It is not a human-reviewed
baseline, not fully human validated, not fresh evidence, not certification,
and not production readiness. No fresh holdout, SUT fix, or tuning against
burned results was performed or authorized by this task.
