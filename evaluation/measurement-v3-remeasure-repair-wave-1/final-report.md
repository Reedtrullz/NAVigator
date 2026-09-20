# Final Report - NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1

## 1. Task ID

NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1

## 2. Wave-1 candidate manifest SHA

e19dd2d6d5329ef3fe85e1719fdc879717563a2e18dc561812b5e6d2a7035f27 (evaluation/full-sut-repair-wave-1-v1/repaired-sut-manifest.json)

## 3. Wave-1 prediction-set SHA

Frozen replay prediction manifests:

- safety: 2f8fb5dbb392a8481024f6947f769737c4ed69fda2a85b2bf6f14f79706b5839
- routing: 7a4939c35760c2c74727e700d37a4ff1cea75397157b23c6b72dcc42ffeed588
- discovery_adversarial: d8cc213c677d59e3de9487d133f96b108274d7aae49326be5c8ee42b086b42a3

## 4. Measurement V3 manifest SHA

Frozen measurement engine pins (input-integrity.json, all match on recompute):

- combined engine: ce7277aa365d4143563cfaa09dfd52712a89a0abd8515f075658b1d683964a29
- review lane: 5ba5ad693a329054e59fc6bfd1d346fbd784e9d3bd7b79cdaf8e383914c86e7c
- judge_core_v2_13: 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682

## 5. Repaired corpus/gold manifest SHA

0df5c956e8a5d340b90df91d6c0ccb689dccc9a6700b252b7c602c3047cfca17 (evaluation/dev-corpus-v1-1-repair/manifest.json)

## 6. Old baseline manifest SHA

e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf (evaluation/measurement-v3-final-authority-provenance-repair-v1/combined-measurement-results-complete-provenance-corrected.json, status MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED)

## 7. Input integrity

PASS. SHA-256 recompute from disk on all upstream pins: Wave-1 task lock, candidate manifest, all three replay prediction manifests, structural replay diagnostics, all three frozen measurement modules, repaired corpus manifest, old baseline results/hashes/freeze manifest. Hard flags: WAVE1_SOURCE_CHANGED=false, WAVE1_PREDICTIONS_CHANGED=false, MEASUREMENT_CHANGED=false, GOLD_CHANGED=false, CORPUS_CHANGED=false, OLD_BASELINE_CHANGED=false. Free disk at gate: 49 GiB.

## 8. Prediction count

120/120 (20 safety, 75 routing, 25 discovery_adversarial). Execution status: 120 SUCCESS, 0 EXECUTION_FAILED, 0 runtime crashes.

## 9. Total criteria

600 (5 per case x 120 cases).

## 10. Deterministic owner count

508 criteria scored deterministically.

## 11. Semantic owner count

88 criteria LLM_REVIEWED (dual-pass Astra consensus). 0 LLM_ADJUDICATED. HUMAN_REVIEWED = 0 (hard constraint held).

## 12. Semantic packet count

92 semantic-review packets, all tied to frozen prediction SHAs.

## 13. Packet leakage result

PASS. Primary packet leakage audit: 0 forbidden keys, 0 verdict-token content hits. Residual input leakage audit: 4/4 packets clean, 0 prior-meta hits (primary A/B results, disagreement reasons, prior Astra results, old baseline outcomes, and gold outcomes all excluded from residual inputs).

## 14. Packet reviewability result

PASS: 92/92 packets reviewable.

## 15. Astra model

gpt-6-astra via local proxy (127.0.0.1:10100), owner-directed.

## 16. Astra reasoning

LOW (hard enforcement; astra-config.json reasoning_effort=LOW with MEDIUM/HIGH/MAX forbidden).

## 17. Primary A calls

92/92 packets called in pass A; 90 valid (2 INVALID_MODEL_REVIEW stored-status records with canonical validity OK; 1 canonical INVALID_ENUM: PKT-ESC-ROUT-026-F01).

## 18. Primary B calls

92/92 packets called in pass B; 91 valid (8 INVALID_MODEL_REVIEW stored-status records with canonical validity OK; 1 canonical INVALID_ENUM: PKT-ESC-ROUT-037).

## 19. Transport retries

Primary: 0 transport failures, 0 retries (astra-transport-log.jsonl empty). Adjudication: 0 transport failures, 0 retries (adjudication-transport-log.json events=[]). One technical retry was allowed by policy; it was never needed.

## 20. Primary valid-pass counts

184 passes checked (92 x 2); valid_astra_a=90, valid_astra_b=91; 24 invalid records total (22 stored-status INVALID_MODEL_REVIEW with canonical validity OK, 2 canonical INVALID_ENUM). Evidence validation: 0 violations.

## 21. Primary consensus count

88 packets reached dual-pass consensus and were accepted as LLM_REVIEWED observations; 4 went to residual adjudication.

## 22. Residual count

4 (PKT-ESC-DIS-118, PKT-ESC-ROUT-026-F01, PKT-ESC-ROUT-031-F01, PKT-ESC-ROUT-037).

## 23. Adjudication A calls

4/4 residual packets called; 3 valid (PKT-ESC-ROUT-031-F01 adj_a INVALID_ENUM).

## 24. Adjudication B calls

4/4 residual packets called; 3 valid (PKT-ESC-ROUT-037 adj_b INVALID_ENUM).

## 25. Adjudication consensus count

0. All 4 residuals ended at HUMAN_ADJUDICATION_REQUIRED (2 semantic disagreements: DIS-118 MATCH/ASSERTED vs NO_MATCH/UNRESOLVED, ROUT-026-F01 NONCOMMITTAL vs UNRESOLVED; 2 invalid-pass: ROUT-031-F01 adj_a, ROUT-037 adj_b).

## 26. Human-adjudication-required count

4 criteria pending human adjudication: DIS-118::forbidden:01, ROUT-026::forbidden:01, ROUT-031::forbidden:01, ROUT-037::forbidden:01.

## 27. Semantic review freeze SHA

d63cdb0aad9094bd9439a97eadd1c5c12ca825ef00a470034b14ad21030fcd50 (semantic-review-freeze-manifest.json; frozen before gold derivation).

## 28. Derivation kernel SHA

66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682 (judge_core_v2_13.py, frozen unmodified).

## 29. LLM calls during derivation

0. Derivation ran mechanically over frozen observations via judge_core_v2_13.

## 30. Deterministic authority count

508.

## 31. LLM_REVIEWED count

88.

## 32. LLM_ADJUDICATED count

0.

## 33. HUMAN_REVIEWED count

0.

## 34. Pending count

4 (DIS-118::forbidden:01, ROUT-026::forbidden:01, ROUT-031::forbidden:01, ROUT-037::forbidden:01; cases DIS-118, ROUT-026, ROUT-031, ROUT-037).

## 35. Authoritative total

596/600 = 99.33%.

## 36. Old PASS/FAIL/DEGRADED/UNRESOLVED

Old applicable = 588: PASS 284, FAIL 265, DEGRADED 34, UNRESOLVED 5 (plus 12 NOT_APPLICABLE excluded from denominators).

## 37. New PASS/FAIL/DEGRADED/UNRESOLVED

New authoritative = 588: PASS 287, FAIL 243, DEGRADED 36, UNRESOLVED 5, plus 4 PENDING excluded from authoritative rates.

## 38. Old failure rate

51.70% (1 - 284/588).

## 39. New failure rate

51.19% (1 - 287/588), authoritative-only (4 pending excluded).

## 40. Criteria improved

8 (6 critical-condition FAIL->PASS: ROUT-022, ROUT-026, ROUT-047, ROUT-052, ROUT-068, ROUT-088; 2 uncertainty FAIL->DEGRADED: SAF-009, SAF-019).

## 41. Criteria regressed

0.

## 42. Unchanged criteria

575 of 600 (21 changed: 8 improvements, 13 fail-closed lateral FAIL->UNRESOLVED, 4 -> PENDING).

## 43. Cases improved

8 cases contain the 8 improved criteria: ROUT-022, ROUT-026, ROUT-047, ROUT-052, ROUT-068, ROUT-088, SAF-009, SAF-019.

## 44. Cases regressed

0.

## 45. RC-01 effect

Repaired. Old phase-3 run logs: 9 EXECUTION_FAILED (SAF-007, SAF-009, SAF-011, SAF-013, SAF-019, ROUT-078, ROUT-087, ROUT-088, DIS-120). New replay: 120/120 SUCCESS, 0 EXECUTION_FAILED. Every crash-failing case now produces a real scored output.

## 46. RC-02 effect

Structural mismatch unchanged: 19/20 safety priority rows still cannot pass because the scorer exact-matches the 12-value gold taxonomy while the candidate emits the collapsed ACUTE/URGENT/NOT_ACUTE enum. Emitted distribution moved 18/2/0 -> 16/3/1 (ACUTE/URGENT/NOT_ACUTE); 12 distinct safety_class values emitted; no under-escalation observed; uncertainty VIOLATED 2 -> 0.

## 47. RC-03 effect

Route emission repaired: non-empty structured routes 0 -> 23 cases (30 entries, 13 distinct labels), no_route_asserted 120 -> 97, 0 consistency mismatches, 0 routes without provenance, PREMATURE_ABSENCE flags 88 -> 69 (the 19 lost flags are exactly the route-gaining cases). Verdicts unchanged: 108/108 scored route criteria remain NO_ACCEPTABLE_ROUTE.

## 48. Safety regressions

0. No safety, critical-condition, or uncertainty criterion regressed.

## 49. Routing result

0 verdict-level changes: 108/108 NO_ACCEPTABLE_ROUTE unchanged, 12 NOT_APPLICABLE unchanged. Structural emission improved without changing any scored route outcome. Report-only anomaly: empty evidence arrays on DIS-106 and ROUT-069 route rows (old rows carried PREMATURE_ABSENCE); verdict impact none.

## 50. Uncertainty result

VIOLATED 2 -> 0 (SAF-009 and SAF-019: FAIL -> DEGRADED, deterministic authority). New distribution: 83 NOT_REQUIRED, 36 PARTIAL, 1 SATISFIED, 0 VIOLATED.

## 51. Evidence result

Unchanged: 38/120 at 0.0, 82/120 at 1.0, mean 0.6833 identical to old baseline. No evidence criterion improved or regressed.

## 52. RC-04 still indicated?

No. Descoped and indirectly resolved by RC-01: the failure-path outputs that carried its observed family no longer occur (0 EXECUTION_FAILED). The failure-path canary should be kept in future regression suites.

## 53. RC-05 still indicated?

Yes. 38/120 evidence rows remain at 0.0 with identical distribution to the old baseline; provenance linkage exists (308/645 claims) but the scored evidence-completeness distribution did not move.

## 54. RC-06 still indicated?

Yes. Repeated national-information blocks: 104/120 answers with >=2 blocks (old 98), 645 occurrences (old 610). Raw counts slightly worsened while route emission improved; linkage is hypothesis, not proven root cause. No frozen scoring criterion captures this defect.

## 55. Source changes during measurement

0.

## 56. SUT rerun

NO. Scoring used the frozen Wave-1 replay predictions; no prediction was regenerated.

## 57. Gold changes

0. Note: ROUT-061/070/073 gold wording differs between lineages (changed in the upstream repair lineage before this task); within this task gold was frozen and unchanged. Their state changes are gold-wording effects, not product-caused regressions.

## 58. Measurement changes

0. Combined engine, review lane, and judge_core_v2_13 all SHA-verified unchanged.

## 59. Astra MEDIUM calls

0.

## 60. Astra HIGH calls

0.

## 61. Astra MAX calls

0.

## 62. Burned-development classification retained?

Yes. BURNED_DEV_BASELINE_ONLY. All results are measurement-system evidence for the burned dev baseline only; not certification, production readiness, or generalization evidence.

## 63. Measurement freeze manifest SHA

e6d91a813dbf69fa647b15e683638a69a14bb9870e8ffbf7da801fd0615e2abb (wave1-measurement-freeze-manifest.json, frozen_utc 2026-09-16T08:40:13Z, freeze order MEASUREMENT_FROZEN_BEFORE_OLD_BASELINE_COMPARISON).

## 64. Final hashes verified?

Yes. All 23 pins in hashes.txt recomputed from disk and matched (0 mismatches). Post-freeze analysis artifacts are pinned separately in post-freeze-analysis-hashes.txt (6 files: wave1-effect-analysis.json, regression-inventory.json, safety-comparison.md, routing-comparison.md, remaining-rc04-06-assessment.md, baseline-transition-matrix.json), deliberately excluded from the frozen measurement hashes because they were created after the freeze by design.

## 65. STATUS

MEASUREMENT_V3_REMEASURE_WAVE_1_RESIDUAL_ADJUDICATION_REQUIRED

Valid partial terminal per spec section 37: 596/600 criteria have authoritative outcomes, 4 frozen residual packets require human adjudication in a separate owner-authorized lineage. Residuals must not be rerun.

## 66. Recommended next bounded task

Human adjudication of the 4 frozen residual packets (PKT-ESC-DIS-118, PKT-ESC-ROUT-026-F01, PKT-ESC-ROUT-031-F01, PKT-ESC-ROUT-037) in a new owner-authorized lineage, working only from the frozen packet SHAs in residual-consensus.json. After adjudication completes the 600/600 authoritative baseline, the next owner decision is the RC-05/RC-06 repair-wave question based on the frozen Wave-1 remeasurement.
