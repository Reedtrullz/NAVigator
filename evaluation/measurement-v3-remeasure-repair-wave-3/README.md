# Measurement V3 - Remeasure Repair Wave 3

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3

Status: MEASUREMENT_V3_REMEASURE_WAVE_3_COMPLETE (600/600 criteria authoritative; 0 pending)

Classification: BURNED_DEV_BASELINE_ONLY. Nothing in this lineage is certification, production readiness, or generalization evidence.

## What this task did

1. Verified frozen inputs (Wave-3 W3-RC-A v1 predictions, Wave-2 measurement, Wave-1 measurement, original burned baseline, Measurement V3 components, corpus/gold) by SHA recompute from disk. All pins matched; hard_flags all false. The Wave-3 repair-lineage close-out provenance deviation (TASK-LOCK report pin c9506c33... vs actual d0554619...) is documented in input-integrity.json; candidate integrity rests on the frozen manifest and component pins.
2. Scored the 120 frozen Wave-3 predictions against the 600 frozen gold criteria with frozen Measurement V3 (combined engine, review lane v2-15, judge_core_v2_13), deterministic first.
3. Created fresh semantic-review packets for the 96 non-deterministic criteria, leakage-audited and reviewability-audited (96/96 reviewable, all leakage hard flags 0; no packet reuse from prior waves).
4. Ran blind dual-pass Astra review (gpt-6-astra, reasoning LOW only) producing 89 semantic consensuses; 7 residual criteria remained after invalid-record and disagreement routing. Deviation: pass files contain concurrent-invocation duplicate records (123/124 lines vs 96 unique packets per pass); per-record validation counts are authoritative (192 pass-records checked, 24 invalid records).
5. Ran bounded residual adjudication with gpt-5.6-sol LOW (7 + 7 calls, all valid, 0 retries): 7/7 dual-pass consensus, all LLM_ADJUDICATED, including the Wave-2 pending criterion ROUT-026::forbidden:01 (resolved ABSENT).
6. Derived final verdicts mechanically (0 LLM calls during derivation) and froze the Wave-3 measurement BEFORE comparison: wave3-measurement-freeze-manifest.json, 26 artifacts, frozen 2026-09-16T21:51:31Z, manifest self-SHA 6385bcd98596350ac4f12fa612bacbacf92d625d81105d3cf7dbe3e2f5d05d54.
7. Compared frozen Wave-3 against frozen Wave-2 (primary), Wave-1 and the original baseline (secondary) mechanically (transition matrices, regression inventory), then wrote the seven analysis deliverables, this README, and final-report.md.

## Headline result (authoritative 600/600)

- States W2 to W3: PASS 317 to 320, FAIL 218 to 214, UNRESOLVED 16 to 18, DEGRADED 36 to 36, PENDING 1 to 0.
- Hard-fail rate 0.3714 (218/587) to 0.3639 (214/588); non-pass rate 0.4532 to 0.3946. The delta_report also emits 1 - PASS/applicable (0.4609 to 0.4558); label these separately, they are different definitions.
- 5 criteria improved (5 cases), 5 regressed (5 cases, all critical_condition P0), 6 lateral fail-closed, 572 unchanged of 588 old-applicable.
- Authority mix W3: 504 DETERMINISTIC, 89 LLM_REVIEWED, 7 LLM_ADJUDICATED, 0 HUMAN_REVIEWED, 0 PENDING.
- Route PASS remains 0/108; the emission funnel moved (20 to 24 structured cases, 24 to 39 entries, 14 to 24 labels, R0 89 to 84) but label-to-evidence binding is still unresolvable (0/24), so W3-RC-A is PARTIALLY_EFFECTIVE. 5 P0 safety regressions carry a 4/5 judgment-layer authority confound (LLM_REVIEWED to DETERMINISTIC); only ROUT-069 is a clean deterministic regression.

## Reading order

1. final-report.md - 104 numbered items per spec section 44, the complete factual record.
2. input-integrity.json, wave3-measurement-freeze-manifest.json, hashes.txt - integrity and freeze basis.
3. wave3-aggregate-metrics.json, wave2-wave3-transition-matrix.json, regression-inventory.json - results and movement.
4. rc-a-effect-analysis.md, routing-funnel.json, route-failure-stage-classification.json - route emission effect and remaining R0/R5 bottleneck.
5. safety-analysis.md, retrieval-evidence-analysis.md, forbidden-claim-analysis.md - safety, evidence, forbidden lanes.
6. w3-res-assessment.md, remaining-rc04-06-assessment.md, fresh-holdout-readiness.md - residuals, what is still indicated, and why fresh holdout is NOT_READY.

## Honest history notes

- Wave-1 comparison basis: this lineage's frozen TASK-LOCK and input-integrity use the wave1-consensus-comparator-repair lineage (results 1f4aac89...e7c1, freeze e3d65105...8479, verified from pinned disk state). The Wave-2 README compared against the earlier Wave-1 lineage (results 4f407672...fbb7). Both are historical Wave-1 measurements; this task used its frozen pin and did not re-adjudicate the discrepancy.
- The Astra pass files contain duplicate concurrent-invocation records (123 lines pass A / 124 lines pass B vs 96 unique packets per pass). This is a documented harness deviation; blindness was not affected (pass B saw no pass A), and all validation/consensus counts are per-record and authoritative.
- The measurement freeze pins TASK-LOCK.json at its pre-terminal SHA (50cfdac3...7f7d). The terminal status was added to TASK-LOCK after the freeze, per the established precedent from the Wave-2 and provenance-repair lineages; the final TASK-LOCK SHA therefore differs from the pinned value and this deviation is documented in final-report.md. hashes.txt was not modified after freeze.
- Spec section 43 requires primary-validation.json; the canonical equivalent primary-review-validation.json from prior waves is used.

## Hard stop

After terminal status: no Wave-4, no RC-04/RC-06 implementation, no W3-RES fixes, no fresh holdout, no SUT changes, no rerun of residual semantic cases, no prompt tuning. The next owner decision must use the frozen Wave-3 measurement and routing delta.
