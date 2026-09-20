# Wave-4 Quota Resume V1

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1
Terminal status: MEASUREMENT_V3_REMEASURE_WAVE_4_COMPLETE
Classification: COMPLETE_MEASUREMENT_BURNED_DEV_BASELINE_ONLY

## Purpose

The frozen quota-safe lineage (evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1) stopped at MEASUREMENT_V3_REMEASURE_WAVE_4_QUOTA_DEFERRED with 490/600 authoritative criteria and 110 frozen semantic packets waiting on quota. This task resumed exactly that state: dual-pass Astra (LOW) review of the 110 packets, Sol (LOW) dual-pass adjudication of the 4 Astra residuals, mechanical derivation, merge into the frozen partial results, freeze of the complete 600/600 measurement, and the deferred comparisons. No packets were regenerated or edited, no consensus hunting, no product or gold changes, no fresh cases.

## Result summary

- Coverage: 600/600 authoritative (482 DETERMINISTIC, 106 LLM_REVIEWED, 4 LLM_ADJUDICATED, 8 REUSED_LLM_ADJUDICATED, 0 pending).
- Calls: Astra 110 A + 110 B (0 retries, valid 109/108, consensus 106, residual 4); Sol 4 A + 4 B (0 retries, consensus 4/4). Derivation used 0 LLM calls (judge_core_v2_13).
- Semantic states: PASS 332, FAIL 193, DEGRADED 36, UNRESOLVED 27, ABSENT_OR_NOT_APPLICABLE 12.
- Rates: hard-fail 193/588 = 0.3282; non-pass (FAIL + UNRESOLVED) 220/588 = 0.3741; frozen delta_report failure_rate 0.4354 (includes DEGRADED; separate definition per Wave-3 convention).
- Adapter-only effect: 0 (W3 historical to compat bridge byte-identical on all 588 comparable states).
- Product-only effect (bridge to Wave 4): 14 improvements (all critical_condition), 1 regression (DIS-118::forbidden:01, P1), 10 lateral fail-closed FAIL-to-UNRESOLVED, ROUT-085 PASS-to-UNRESOLVED.
- Route correctness: unchanged at 0 PASS / 108 evaluated (106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL); evidence joins 0/125; RC-04 and RC-06 still indicated.
- Fresh holdout: NOT_READY_FOR_FRESH_HOLDOUT (see fresh-holdout-readiness.md).

## Artifacts

- Lock and integrity: TASK-LOCK.json, input-integrity.json, resume-source-manifest.json
- Review configs and outputs: astra-config.json, astra-pass-a.jsonl, astra-pass-b.jsonl, astra-validation.json, primary-consensus.json, primary-review-freeze-manifest.json, sol-config.json, sol-pass-a.jsonl, sol-pass-b.jsonl, sol-transport-log.json, sol-validation.json, residual-validation.json, residual-consensus.json, semantic-review-freeze-manifest.json
- Derivation and measurement: derived-measurement-results.json, derived-resume-results.json, completed-wave4-measurement-results.json, completed-wave4-aggregate-metrics.json, merge-invariants.json
- Freeze: completed-wave4-measurement-freeze-manifest.json, hashes.txt (22 pinned artifacts; freeze manifest SHA 30abe921d5d79a49e2827aa6da8c80cb1d5214646062434d376928d279a54fab)
- Deferred comparisons (post-freeze, read-only over frozen inputs): measurement-adapter-effect.json, wave3bridge-wave4-transition-matrix.json, original-wave4-transition-matrix.json, routing-funnel.json, route-failure-stage-classification.json, regression-inventory.json
- Closure: fresh-holdout-readiness.md, final-report.md

## Lineage and provenance

- Source (immutable): evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1, freeze ff0b7a41a2c30168f87695801cebc7225a4d3269eb1786f3b03694147caaf62e, partial results 30999cb8b4c135acce255bdd83effe98935fcbbe657f1b6ecc90d8380bba8dc5.
- Complete measurement freeze: 2026-09-18T13:39:14Z, freeze_order MEASUREMENT_FROZEN_BEFORE_DEFERRED_COMPARISONS; comparison artifacts deliberately produced after the freeze and not pinned in hashes.txt.
- The completed results header embeds the semantic-review freeze manifest SHA (70a5cb7e...ea7e), matching semantic-review-freeze-manifest.json; primary-review-freeze-manifest.json (47e8ec53...7b3da) is the separate Astra-only freeze.
- Model policy: gpt-6-astra LOW primary, gpt-5.6-sol LOW residual adjudicator only, no fallbacks, no MEDIUM/HIGH/MAX calls, no GPT-5.5.

## Hard rules

No further model calls. No packet regeneration or editing. No SUT, product, gold, or measurement-contract changes. No fresh holdout. The source quota-safe lineage and all frozen artifacts are immutable. Next bounded task candidate (NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1) requires separate owner authorization.
