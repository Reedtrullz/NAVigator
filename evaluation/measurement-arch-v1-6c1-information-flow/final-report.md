# Final Report - NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR

1. **Task ID**: NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR
2. **Prior A4 status**: patch verified in-place on A3 lineage (authorization task V1.6A.4); no regression to boundary green.
3. **Prior V1.6B status**: screening completed; mimo-v2.5-pro checkpoint frozen (92 judge-stage rows on residual strata).
4. **Baselines verified**: 14 SHAs in `baseline-integrity.json` - PASS; re-checked after run.
5. **Historical writes**: 0 (git status + SHA re-verification clean).
6. **A3 SHA**: 21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b
7. **A4 SHA**: checkpoint `a5e9d87a18e649cf...` (V1.6B screening, mimo-v2.5-pro)
8. **A3 changed**: NO
9. **A4 changed**: NO
10. **New boundary rules**: NO
11. **New lexical guard**: NO
12. **Current judge input fields**: unchanged V1.4 JSON (RAW text + criterion) in OLD arm; identical + `deterministic_structure` + neutral note in NEW arm.
13. **Information-loss categories**: clause grouping, marker spans (negation/retraction/quote/hedge), route candidates, A3 verdict - all discarded by OLD flow (13/13 wrong rows).
14. **Structured packet fields**: clause_spans, quote/negation/retraction/hedge/assertion/conditional/attribution/vague spans, route_candidates, deterministic_evidence, a3 (inventory-stripped).
15. **Gold-derived packet fields**: 0 (`gold-leakage-audit.json` PASS)
16. **Packet schema validity**: PASS (40/40 builder fixtures)
17. **Span validity**: 100% NEW-arm evidence spans verbatim in SUT text (92/92)
18. **Deterministic provenance**: all packet fields a3_*; builder refuses A3 SHA drift - PASS
19. **Packet-builder fixture N**: 40
20. **Packet-builder PASS**: 40/40
21. **Packet contract frozen before A/B**: YES (builder/schema/contract SHAs in manifest; TDD RED->GREEN before any call)
22. **Reference model**: command-code/xiaomi/mimo-v2.5-pro via local proxy 127.0.0.1:10100
23. **Model config**: temp 0, max_tokens 32768, V1.4 retry policy; runner sha in manifest
24. **Burned A/B criteria N**: 92 rows (30 critical, 30 forbidden, 18 route, 14 uncertainty)
25. **OLD residual overall**: 79/92 = 85.87%
26. **NEW residual overall**: 78/92 = 84.78%
27. **Absolute improvement**: -1.09 pp (gate: >= +10 pp) - FAIL
28. **Relative error reduction**: -7.69% (gate: >= 25%) - FAIL
29. **OLD critical FN**: 0
30. **NEW critical FN**: 0
31. **OLD forbidden safety FN**: 0
32. **NEW forbidden safety FN**: 0
33. **OLD route**: 15/18 = 83.33%
34. **NEW route**: 16/18 = 88.89% (+5.56 pp)
35. **OLD uncertainty**: 12/14 = 85.71%
36. **NEW uncertainty**: 11/14 = 78.57% (-7.14 pp)
37. **Largest dimension regression**: uncertainty -7.14 pp (gate -3.00) - FAIL
38. **Wrong->right**: 2 (F-02, R-11)
39. **Right->wrong**: 3 (C-27, F-08, U-14)
40. **Unchanged-right**: 79
41. **Unchanged-wrong**: 11 (C-28, C-29, C-30, F-09, F-23, F-26, F-27, R-13, R-26, U-19, U-23)
42. **Valid-result OLD**: 92/92
43. **Valid-result NEW**: 92/92
44. **Evidence validity**: 100% both arms
45. **Information-flow attribution**: wrong->right rows carried route_candidates (F-02) and hedge/vague markers (R-11); right->wrong rows had negation/conditional spans present - structural context shifted uncertainty and condition judgments. Full map: `information-attribution.json`.
46. **Token overhead**: median +816.5 (+42.2%); p95 4300 -> 4990
47. **Latency overhead**: median +3.99 s (+18.6%)
48. **Packet-builder complexity**: 99 LOC, 6 functions, 11 branches, 0 deps, fail-closed A3 SHA guard
49. **Fresh validation performed**: NO
50. **Model screening performed**: NO
51. **A5 started**: NO
52. **Lexical fallback started**: NO
53. **Gates passed**: valid rate 1.0; evidence validity 1.0; critical FN 0; safety forbidden FN 0
54. **Gates failed**: absolute improvement; relative error reduction; max dimension regression (uncertainty -7.14 pp)
55. **STATUS**: `V1_6C1_INFORMATION_FLOW_NOT_SUPPORTED`
56. **C2 calibration-weighted screening justified**: NO - no positive signal to calibrate on
57. **Remaining limitations**: single model, single burned-residual set; packet proved redundant with what the model infers from RAW text; uncertainty classification is the fragile dimension.
58. **Recommended next bounded stage**: attack the 11 unchanged-wrong rows and 3 right->wrong rows directly (failure-cluster report), e.g. targeted uncertainty/conditional adjudication contract work - not more context injection.

STOPP: ingen C2, ingen A5, ingen lexical fallback, ingen full SUT, ingen product holdout.
