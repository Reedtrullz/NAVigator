# NAV-EXPLORE-MEASUREMENT-V3-ASTRA-INTEGRATION-AND-RESIDUAL-ADJUDICATION-V1

Terminal status: MEASUREMENT_V3_BURNED_BASELINE_RESIDUAL_HUMAN_ADJUDICATION_REQUIRED
Baseline label: BURNED_DEV_BASELINE_ONLY (mixed authority; 2 criteria intentionally pending human adjudication)

## Entry points

- final-report.md: full 52-point terminal report
- review-freeze-manifest.json: SHA pins for all review observations, frozen BEFORE final score derivation (spec section 21)
- derived-measurement-results.json: mechanical derivation of 72 LLM criteria via frozen judge_core_v2_13.derive_final
- combined-measurement-results.json: 600-criterion combined result (526 deterministic rows copied byte-untouched + 74 updated)
- combined-aggregate-metrics.json: criterion-level and case-level coverage, per-dimension verdict distributions
- human-residual-adjudication-packets.json: the 2 pending packets (ROUT-025, ROUT-066), reviewer-permitted fields only
- adjudication-validation.json: enum/enum-invalid details for the residual adjudication
- TASK-LOCK.json: terminal state with freeze-manifest and hashes.txt pins

## Authority model (mixed, explicit)

| Authority class | Criteria |
|---|---|
| DETERMINISTIC | 526 (copied untouched from frozen burned baseline) |
| LLM_REVIEWED | 64 (original Astra A/B dual-pass consensus, Batch 1) |
| LLM_ADJUDICATED | 8 (residual ADJ-A/ADJ-B consensus, gpt-6-astra reasoning_effort=low) |
| HUMAN_REVIEWED | 0 |
| PENDING_HUMAN_ADJUDICATION | 2 (ROUT-025::forbidden:01, ROUT-066::forbidden:01) |
| AUTHORITATIVE_TOTAL | 598/600 = 99.67% |

Case-level coverage: 118/120 fully authoritative (ROUT-025, ROUT-066 pending).

## Key findings during integration

1. The stored status fields in the Batch-1 jsonl files used a stricter in-run span rule
   (55/74 flagged INVALID per pass). The authoritative frozen validator is validate()
   in evaluation/measurement-v3-astra-review-batch-1/build_consensus.py, which treats
   empty spans as legal where the contract does not require them. Recomputing with the
   frozen validator reproduced consensus-results.json exactly: valid A=70, B=71,
   consensus=64, disagreements=3, invalid-pass=7. Documented in batch1-revalidation.json.
2. Residual adjudication: 20/20 calls OK, 0 retries. ADJ-A valid 8 (ROUT-025 and
   ROUT-066 enum-invalid), ADJ-B valid 9 (ROUT-066 enum-invalid). Consensus 8,
   disagreements 0. Enum-invalid packets were preserved, NOT repaired (no third pass).
3. Model invariant verified across all jsonl passes in this lineage:
   model=gpt-6-astra, reasoning_effort=low only; MEDIUM/HIGH/MAX calls = 0.
4. Dual-pass Astra agreement and adjudication consensus are MODEL CONSISTENCY
   EVIDENCE only - not human validation, not certification, not generalization evidence.

## Next task (do not start automatically)

Human adjudication of the 2 pending frozen packets using human-residual-adjudication-packets.json
(reviewer-permitted fields only; no AI verdicts included), then mechanical derivation of those
2 criteria via the same frozen judge_core_v2_13.derive_final.
No SUT rerun, no re-scoring of resolved criteria, no packet repair, no third automated pass.
