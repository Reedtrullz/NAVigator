# Measurement V3 - Remeasure Repair Wave 2

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2

Status: MEASUREMENT_V3_REMEASURE_WAVE_2_RESIDUAL_ADJUDICATION_REQUIRED (valid terminal state; 1 criterion remains pending by frozen design, no resampling allowed)

Classification: BURNED_DEV_BASELINE_ONLY. Nothing in this lineage is certification, production readiness, or generalization evidence.

## What this task did

1. Verified frozen inputs (Wave-2 Candidate-2 predictions, Wave-1 measurement, original burned baseline, Measurement V3 components, corpus/gold) by SHA recompute from disk. All pins matched; hard_flags all false.
2. Scored the 120 frozen Wave-2 v2 predictions against the 600 frozen gold criteria with frozen Measurement V3 (combined engine, review lane v2-15, judge_core_v2_13), deterministic first.
3. Created fresh semantic-review packets for the 94 non-deterministic criteria, leakage-audited and reviewability-audited (94/94 reviewable, all leakage hard flags 0).
4. Ran blind dual-pass Astra review (gpt-6-astra, reasoning LOW only, 94 + 94 calls, 0 technical retries) producing 90 semantic consensuses and 1 disagreement; 3 pass-records were invalid.
5. Ran bounded residual adjudication with gpt-5.6-sol LOW (4 + 4 calls, 0 retries) on the 4 residual criteria: 3 resolved as LLM_ADJUDICATED, 1 (ROUT-026::forbidden:01) remains PENDING because Sol dual-pass disagreed semantically.
6. Derived final verdicts mechanically (0 LLM calls during derivation) and froze the Wave-2 measurement BEFORE comparison: wave2-measurement-freeze-manifest.json, 26 artifacts, frozen 2026-09-16T15:50:42Z, manifest self-SHA f5e0a0193d9ddb4da7046ba9719c0d52dafa2982eee1bcac6c11393d5391fc30.
7. Compared frozen Wave-2 against frozen Wave-1 and the original baseline mechanically (transition matrix, regression inventory), then wrote the eight analysis deliverables, this README, and final-report.md.

## Headline result (authoritative 599/600)

- States W1 to W2: PASS 287 to 317, FAIL 243 to 218, UNRESOLVED 18 to 16, DEGRADED 36 to 36, PENDING 4 to 1.
- Hard-fail rate 0.4133 to 0.3714; non-pass rate 0.5051 to 0.4532. The delta_report also emits 1 - PASS/applicable (0.5119 to 0.46); label these separately, they are different definitions.
- 31 criteria improved (24 cases), 9 regressed (9 cases), 8 lateral, 540 unchanged (of 588 old-applicable).
- Authority mix W2: 506 DETERMINISTIC, 90 LLM_REVIEWED, 3 LLM_ADJUDICATED, 0 HUMAN_REVIEWED, 1 PENDING.
- Prompt warnings: 2 P0 under-triage candidates (ROUT-026, ROUT-088) and a scorer-judgment-layer sensitivity between W1 LLM-reviewed and W2 deterministic evidence rows. Route PASS remains 0/108 with the funnel bottleneck moved, not removed.

## Reading order

1. final-report.md - 99 numbered items per spec section 41, the complete factual record.
2. input-integrity.json, wave2-measurement-freeze-manifest.json, hashes.txt - integrity and freeze basis.
3. wave2-aggregate-metrics.json, wave1-wave2-transition-matrix.json, regression-inventory.json - results and movement.
4. rc08-effect-analysis.md, routing-funnel.json, rc07-routing-analysis.md - retrieval/routing effect and remaining bottleneck.
5. rc10-evidence-analysis.md, rc11-safety-analysis.md, forbidden-claim-analysis.md - evidence, safety, forbidden lanes.
6. remaining-rc04-06-assessment.md, fresh-holdout-readiness.md - what is still indicated and why fresh holdout is NOT_READY.

## Honest history notes

- The prior handoff and TASK-LOCK upstream_pins cited a Wave-1 results SHA of 1f4aac89...e7c1, which does not exist on disk. The authoritative Wave-1 results SHA is 4f407672...fbb7, verified against Wave-1's own freeze manifest pin (e6d91a81...2abb). All comparisons in this lineage use the verified artifacts.
- The freeze manifest pins TASK-LOCK.json at its pre-terminal SHA (3000631d...007f). The terminal status was added to TASK-LOCK after the freeze, per the established precedent from the provenance-repair lineage; the final TASK-LOCK SHA therefore differs from the pinned value and this deviation is documented in final-report.md. hashes.txt was not modified after freeze.
- Candidate-1 (99/120 SUCCESS, 21 EXECUTION_FAILED fail-closed due to duplicate per-track evidence IDs) is superseded engineering history only and was never measured.

## Hard stop

After terminal status: no SUT changes, no Candidate 3, no RC-04/RC-06 implementation, no fresh holdout, no resampling of the pending criterion, no prompt tuning. Next work requires a new explicit owner authorization.
