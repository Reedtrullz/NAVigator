# Final Report - Wave-4 Quota Resume V1

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1
Classification: COMPLETE_MEASUREMENT_BURNED_DEV_BASELINE_ONLY. This is a burned dev baseline measurement, not certification, generalization evidence, or production readiness.

## Report (spec section 24)

1. Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1
2. Quota-safe source freeze SHA: ff0b7a41a2c30168f87695801cebc7225a4d3269eb1786f3b03694147caaf62e (partial results 30999cb8b4c135acce255bdd83effe98935fcbbe657f1b6ecc90d8380bba8dc5)
3. Resume packet count: 110
4. Resume packets verified: 110/110 (packets SHA b7f6821a5be117b5ee7aa5a992bd7a210aa7f71ec3ba604456c7f99b91d13d9d)
5. Previously authoritative rows: 490 (482 DETERMINISTIC + 8 REUSED_LLM_ADJUDICATED); none changed by the resume
6. Astra model: gpt-6-astra
7. Astra reasoning: LOW (owner instruction; config asserted)
8. Astra A calls: 110
9. Astra B calls: 110
10. Astra transport retries: 0
11. Primary valid-pass counts: A 109/110, B 108/110; 3 stored-OK records failed canonical enum validation (PKT-ESC-ROUT-028 B, PKT-ESC-ROUT-065 A, PKT-ESC-ROUT-091 B), documented in astra-validation.json
12. Astra semantic consensus count: 106
13. Residual count: 4
14. Sol model: gpt-5.6-sol
15. Sol A calls: 4
16. Sol B calls: 4
17. Sol retries: 0
18. Sol consensus count: 4
19. Remaining pending: 0
20. New LLM_REVIEWED count: 106
21. New LLM_ADJUDICATED count: 4
22. Previously authoritative rows changed: 0
23. Total authoritative criteria: 600
24. Authority coverage: 100 percent (482 DETERMINISTIC, 106 LLM_REVIEWED, 4 LLM_ADJUDICATED, 8 REUSED_LLM_ADJUDICATED)
25. Semantic review freeze SHA: 70a5cb7e19e56093dfc448d855064c4db9471d5ca47f1ecb8065c998770eea7e (semantic-review-freeze-manifest.json)
26. Derivation kernel SHA: 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682 (judge_core_v2_13)
27. LLM calls during derivation: 0
28. Wave-4 PASS: 332
29. FAIL: 193
30. DEGRADED: 36
31. UNRESOLVED: 27 (plus 12 ABSENT_OR_NOT_APPLICABLE, total 600)
32. Hard-fail rate: 193/588 = 0.3282 (evaluated authoritative states; Wave 3 was 214/588 = 0.3639)
33. Non-pass rate: 220/588 = 0.3741 (FAIL + UNRESOLVED; Wave 3 was 232/588 = 0.3946). The frozen delta_report additionally emits failure_rate 0.4354 = (FAIL + UNRESOLVED + DEGRADED)/588; separate definition per the Wave-3 lineage convention, not mixed with hard-fail/non-pass.
34. Adapter-only effect (Wave-3 historical to compat bridge): 0 changes; all 588 comparable states byte-identical; failure rate 0.4558 on both sides. The measurement adapter changed no product outcome.
35. Product-only effect (compat bridge to Wave 4): 14 improvements (13 FAIL-to-PASS plus 1 UNRESOLVED-to-PASS, all critical_condition: DIS-098, DIS-108, DIS-119, ROUT-021/022/025/033/034/035/043/046/047/058/077), 1 regression (DIS-118::forbidden:01, ABSENT to PRESENT, P1), 10 lateral fail-closed FAIL-to-UNRESOLVED transitions, and ROUT-085 PASS-to-UNRESOLVED. Verdict transitions: FAIL-to-PASS 13, PASS-to-FAIL 1, FAIL-to-UNRESOLVED 9, PASS-to-UNRESOLVED 1, UNRESOLVED-to-PASS 1.
36. Route criteria: 120 total, 108 evaluated, 12 not applicable
37. Wave-3 bridge route PASS: 0 (108 FAIL: 106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL)
38. Wave-4 route PASS: 0 (108 FAIL: 106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL)
39. Dominant residual route stage: R0_NO_STRUCTURED_ROUTE (54), then R6_PROVENANCE_OR_EVIDENCE (30); R1 9, R3 11, R5 4
40. Safety result (critical_condition, 120 criteria): PASS 48, FAIL 57, UNRESOLVED 15
41. Forbidden result (forbidden_claim, 120 criteria): PASS 116, FAIL 4 (PRESENT 2, CLAIM_PRESENT 2)
42. Evidence result (evidence_completeness, 120 criteria): PASS 97, FAIL 23
43. RC-04 still indicated: YES (evidence joins 0/125 route entries; label-to-evidence binding unresolvable)
44. RC-06 still indicated: YES (58 no_route_asserted cases; 104 presented_as_complete cases; unchanged)
45. Fresh holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT (fresh-holdout-readiness.md)
46. Astra MEDIUM calls: 0
47. Astra HIGH calls: 0
48. Astra MAX calls: 0
49. Fallback model calls: 0
50. Fresh cases consumed: 0
51. STATUS: MEASUREMENT_V3_REMEASURE_WAVE_4_COMPLETE (terminal)
52. Recommended next bounded task: NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1 (owner authorization required before start)

## Freeze and provenance notes

- Completed measurement freeze: completed-wave4-measurement-freeze-manifest.json, SHA 30abe921d5d79a49e2827aa6da8c80cb1d5214646062434d376928d279a54fab, frozen_utc 2026-09-18T13:39:14Z, freeze_order MEASUREMENT_FROZEN_BEFORE_DEFERRED_COMPARISONS.
- Completed results SHA: 912a8410080b83eea19cd116fcba2eac3209345f3c4787c42d8776a8f22a47c7 (22 artifacts pinned in hashes.txt).
- The completed results header embeds the semantic-review freeze manifest SHA as 70a5cb7e...ea7e, which matches semantic-review-freeze-manifest.json. primary-review-freeze-manifest.json is a separate Astra-only artifact with SHA 47e8ec53...7b3da; both are pinned in the freeze manifest.
- Source quota-safe lineage is untouched: evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1 remains terminal MEASUREMENT_V3_REMEASURE_WAVE_4_QUOTA_DEFERRED.
- Hard invariants at freeze: SUT_RERUN false, MEASUREMENT_CHANGED false, GOLD_CHANGED false, PACKETS_REGENERATED false, QUOTA_SAFE_FREEZE_MUTATED false, NO_CONSENSUS_HUNTING true, FRESH_CASES_CONSUMED 0.
- Comparison artifacts were produced after the freeze by read-only analysis scripts over frozen inputs, per the frozen ordering; hashes.txt intentionally does not pin them.
- No further model calls of any kind are permitted in this task.
