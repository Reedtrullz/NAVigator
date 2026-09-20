# NAV-EXPLORE-MEASUREMENT-V3-RESIDUAL-HUMAN-ADJUDICATION-V1

Completed residual human adjudication lineage for the Measurement V3 burned baseline.

Terminal status: MEASUREMENT_V3_BURNED_BASELINE_COMPLETE.
Classification: BURNED_DEV_BASELINE_ONLY (not certification, not production readiness, not generalization evidence).

## What this lineage did

1. Verified upstream integrity: evaluation/measurement-v3-astra-integration-residual-v1/ (review-freeze manifest SHA 108fef5664311432f8b8a1232e734097653bd7730f7baf0c1f9faf0139e071e4; upstream hashes 19/19 OK).
2. Presented the 2 remaining residual packets blindly to OWNER-01: PKT-ESC-ROUT-025, PKT-ESC-ROUT-066.
3. Received and mechanically validated 2/2 owner adjudications (MATCH + NEGATED for both; evidence spans verbatim-verified).
4. Froze raw human observations before any gold comparison: human-adjudication-freeze-manifest.json (SHA 0eb01485615aaf18d6df1ae618eb230d72113bc0bc202d23a1be06f72e96206c).
5. Derived final verdicts with the frozen deterministic kernel judge_core_v2_13.py (SHA 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682): MATCH+NEGATED -> ABSENT (M1:NEGATED) for both criteria. Zero LLM calls in review and derivation.
6. Integrated into combined-measurement-results-complete.json: exactly 2 rows changed vs upstream (proven mechanically); 598 rows byte-identical.
7. Froze the complete 600/600 baseline and closed TASK-LOCK with terminal status.

## Final coverage

- Total criteria: 600/600 authoritative (100%)
- Authority mix: 526 DETERMINISTIC, 64 LLM_REVIEWED, 8 LLM_ADJUDICATED, 2 HUMAN_REVIEWED (OWNER-01)
- Case coverage: 120/120 (100%)
- Pending: 0

## Files

- TASK-LOCK.json — task contract, closed with terminal status
- present-ROUT-025.md, present-ROUT-066.md — blind presentation packets
- adjudication-*-raw-observation.json — raw owner submissions with validation results
- human-adjudications.jsonl — frozen raw observations (authoritative human input)
- human-adjudication-validation.json — mechanical validation results
- human-adjudication-freeze-manifest.json — pre-derivation freeze record
- derived-residual-results.json — kernel derivation record for both criteria
- combined-measurement-results-complete.json — full 600/600 results (authoritative)
- combined-aggregate-metrics-complete.json — recomputed aggregate metrics
- final-freeze-manifest.json — final freeze manifest (14 pins)
- hashes.txt — SHA256 pins, repo-root relative, verified via shasum -c at final freeze
- final-report.md — 33-item owner-spec report

## Integrity boundaries

- Upstream lineages and artifacts untouched (SHA-verified before and after)
- No SUT rerun, no prediction change, no gold change, no packet change, no contract change
- Human review was performed by OWNER-01 only; no AI served as human reviewer
- Zero LLM calls in this lineage (review: 0, derivation: 0)

## Entry point

Read final-report.md for the complete closure report.
