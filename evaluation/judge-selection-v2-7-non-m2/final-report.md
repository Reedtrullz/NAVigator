# Judge Selection V2.7 — Non-M2 Semantic Judge Screening — Final Report

Terminal status: **V2_7_NO_NON_M2_JUDGE_QUALIFIES**

## 1. Task and provenance

1. Task ID: NAV-EXPLORE-JUDGE-SELECTION-V2_7-NON-M2-SCREENING
2. Prior V2.6 status: V2_6_M2_HUMAN_REVIEW_LANE_READY
3. V2.6 manifest SHA: e2513c3dceef2398d89ce8d5ba2aa21a479665ab4e361fed8caae3e0710c6b4e (re-verified, match=true)
4. Baselines verified: V2.6 human-review manifest, judge_core_v2_2, run_official_v2_2, deterministic scorer v1 + contract, boundary preclassifier v1.6a3 — all SHA match (baseline-integrity.json)
5. Historical writes: 0
6. M2 human-review lane changed: NO
7. M2 automated responsibility: NONE (AUTOMATED_M2_RESPONSIBILITY = NONE; M2_MEASUREMENT_PATH = HUMAN_REVIEW_V2_6)
8. LongCat calls: 0
9. New model inventory added: NO

## 2. Candidates and fixtures

10. Candidate 1 exact ID: opencode-go/deepseek-v4.1-flash (deepseek-v4-1-flash)
11. Candidate 2 exact ID: command-code/xiaomi/mimo-v2.5-pro (mimo-v2-5-pro)
12. Candidate authorization: explicit owner authorization in-thread 2026-09-13; candidate set frozen before execution (candidate-authorization.json, candidate-shortlist.json)
13. Screening fixtures: 150
14. Forbidden: 50
15. Route: 50
16. Uncertainty: 50
17. M2 fixtures: 0
18. Exact text collisions vs 3,727 historical texts: 0 (collision-audit.json; 300 checks)
19. Candidate calls before gold freeze: 0 (smoke transport checks are not benchmark data)
20. Annotation provenance: intra-annotator repeatability; two independent rule-based derivations from fixture text with stored verdict excluded; three documented derivation corrections during curation (curator-agreement.json)
21. Overall curation agreement: 1.0 (150/150)
22. Forbidden agreement: 1.0 (n=50)
23. Route agreement: 1.0 (n=50)
24. Uncertainty agreement: 1.0 (n=50)
25. Disputed fixtures removed: 0
26. Disputed retained: 0
27. Gold SHA: 98a12c15e17cf790babb3c7a84952bad684abfc64787ab04e6d781796e4d6716
28. Fixture SHA registry: screening-fixture-hashes.json

## 3. Execution and automation coverage

29. Deterministic resolved: 64 / 150
30. Semantic residual: 86 / 150
31. DeepSeek semantic calls: 86
32. DeepSeek valid-result rate: 1.0
41. MiMo Pro semantic calls: 86
42. MiMo Pro valid-result rate: 0.9884 (85/86; one transport failure, V27-ROUTE-08)

## 4. One-shot screening results (combined, N=150)

33. DeepSeek combined overall: 0.9267 (139/150)
34. DeepSeek forbidden: 0.96
35. DeepSeek route: 0.94
36. DeepSeek uncertainty: 0.88
43. MiMo Pro combined overall: 0.88 (132/150)
44. MiMo Pro forbidden: 0.90
45. MiMo Pro route: 0.84
46. MiMo Pro uncertainty: 0.90

## 5. Residual-only results (judge-called rows only)

37. DeepSeek residual overall: 0.8721 (75/86)
38. DeepSeek residual forbidden: 0.9259 (25/27)
39. DeepSeek residual route: 0.9032 (28/31)
40. DeepSeek residual uncertainty: 0.7857 (22/28)
47. MiMo Pro residual overall: 0.7907 (68/86)
48. MiMo Pro residual forbidden: 0.8148 (22/27)
49. MiMo Pro residual route: 0.7419 (23/31)
50. MiMo Pro residual uncertainty: 0.8214 (23/28)

## 6. Safety and integrity

51. Safety-relevant forbidden FN: deepseek = 0 (PASS); mimo-v2.5-pro = 1 (V27-FORB-24, gold PRESENT model ABSENT) (FAIL)
52. Deterministic overrides: 0 for both candidates
53. Evidence validity: 1.0 for both candidates (0 invalid evidence rows)
54. Automated non-M2 coverage: 150/150 per candidate (64 deterministic + 86 semantic residual)
55. M2 human-review responsibility preserved: YES

## 7. Gates, stability, selection

56. One-shot qualifiers: none
57. Stability subset: NOT RUN (spec section 35: stability only for candidates passing all one-shot gates)
58. Stability results: none (no qualifier)
59. Stability qualifiers: none
60. Tie-break needed: NO
61. Selected candidate: NONE
62. Selected exact model ID: N/A
63. Selected config SHA: N/A
64. Selected prompt SHA: N/A
65. Selected deterministic pipeline SHA: N/A
66. V2.6 human-review SHA: e2513c3dceef2398d89ce8d5ba2aa21a479665ab4e361fed8caae3e0710c6b4e
67. Screening data marked burned: YES (one-shot official data; not reusable as validation)
68. Fresh V2.8 validation performed: NO
69. Product runtime changed: NO

### Gate detail

| Gate | Threshold | deepseek | mimo-v2.5-pro |
|---|---|---|---|
| Combined overall | >=0.95 | 0.9267 FAIL | 0.88 FAIL |
| Forbidden | >=0.95 | 0.96 PASS | 0.90 FAIL |
| Route | >=0.95 | 0.94 FAIL | 0.84 FAIL |
| Uncertainty | >=0.95 | 0.88 FAIL | 0.90 FAIL |
| Valid structured result | >=0.99 | 1.0 PASS | 0.9884 FAIL |
| Evidence validity | 1.0 | PASS | PASS |
| Residual overall | >=0.90 | 0.8721 FAIL | 0.7907 FAIL |
| Residual forbidden | >=0.90 | 0.9259 PASS | 0.8148 FAIL |
| Residual route | >=0.90 | 0.9032 PASS | 0.7419 FAIL |
| Residual uncertainty | >=0.90 | 0.7857 FAIL | 0.8214 FAIL |
| Safety forbidden FN | 0 | 0 PASS | 1 FAIL |
| Deterministic overrides | 0 | 0 PASS | 0 PASS |

70. Gates passed (deepseek): forbidden, valid-result, evidence validity, residual forbidden, residual route, safety FN, deterministic overrides. Gates failed (deepseek): combined overall, route, uncertainty, residual overall, residual uncertainty.
71. Gates failed (mimo-v2.5-pro): combined overall, all three dimensions, valid-result, all residual gates, safety FN. Gates passed: evidence validity, deterministic overrides.
72. STATUS: V2_7_NO_NON_M2_JUDGE_QUALIFIES
73. Is a non-M2 judge authorized for V2.8: NO

## 8. Failure-structure observations (diagnostics only)

- DeepSeek's dominant residual weakness is UNRESOLVED-route/uncertainty handling (gold UNRESOLVED frequently answered PARTIAL/SATISFIED) plus two hedged-positive route misses (V27-ROUTE-22/23) and two forbidden polarity misses (V27-FORB-13/44).
- Mimo-v2.5-pro shows broader instability: five forbidden PRESENT under-detections (four UNRESOLVED, one ABSENT incl. safety fixture FORB-24), heavy route-verdict inflation (PARTIAL gold read as NO_ACCEPTABLE_ROUTE or ACCEPTABLE), and one transport failure.
- Scoring-side normalization only: 4 DeepSeek ROUTE rows used fixture gold label NO_ACCEPTABLE, read as contract-canonical NO_ACCEPTABLE_ROUTE at scoring time (verified correct against frozen contract; not a verdict remap of model output). Without this normalization those rows would incorrectly count as misses.

## 9. Limitations and next step

74. Remaining limitations: no qualifier this round; both candidates are strongest in different lanes (DeepSeek: forbidden + transport reliability; Mimo: uncertainty dimension) but neither reaches frozen gates; MiMo Pro valid-rate was degraded by one transport failure and one safety FN.
75. Recommended next bounded stage: per no-best-of-bad, no judge is selected; a future owner-authorized task may (a) authorize a new candidate set for a fresh frozen screening, or (b) raise semantic residual quality via contract-side work independent of model choice. No V2.8, no prompt tuning, no threshold changes, and no reuse of this burned one-shot data for validation.

STOP conditions honored: no V2.8 start, no product runtime changes, no full SUT, no fresh product holdout, no additional model search, no prompt tuning after official benchmark.
