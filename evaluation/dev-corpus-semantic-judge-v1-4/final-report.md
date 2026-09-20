# V1.4 Semantic Judge — Final Report

Terminal status: **DEV_CORPUS_SEMANTIC_JUDGE_V1_4_NOT_READY**

1. Task ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_4-BOUNDARY-AGREEMENT-REPAIR
2. Prior V1.3M status: DEV_CORPUS_SEMANTIC_JUDGE_V1_3M_NOT_READY (preserved)
3. Baselines verified: 29/29 historical + 14/14 V1.3M artifacts (baseline-integrity.json, re-run at close)
4. Historical files changed: 0 (write-audit clean; only V1.4 directory touched)
5. V1.3M Set A marked burned: yes (burned-data-registry.json)
6. Duplicate-run incident preserved: yes (TASK-LOCK permanent_process_notes)
7. Historical 120->2000 headroom incident preserved: yes, classified TRANSPORT_CAPACITY_CHANGE; V1.4 preregistered 32768 separately
8. Historical full-row agreement (V1.3M Set A, raw serialized rows incl. notes): 0.0 as recorded; not recomputed
9. Mechanical semantic agreement under V1.4 definition (Set A rescore, diagnostic only): 0.8276 valid-rows (29 valid, 3 error rows); 0.75 error-inclusive
10. Note-only mismatch N (Set A rescore): 24
11. Route historical agreement (Set A rescore): commitment 0.8667, verdict 0.8667
12. Uncertainty historical agreement (Set A rescore): mode 0.9286, verdict 0.7857
13. Free-text note score-bearing: NO (mechanically excluded)
14. New agreement unit: per-field score-bearing semantic comparison (route: proposition_present, speaker_commitment, route_verdict; uncertainty: mode, behavior/components, verdict); notes excluded
15. Route proposition model: YES / NO / UNRESOLVED for identifiability of a concrete route proposition
16. Route commitment states: ASSERTED, HEDGED_ASSERTION, HYPOTHETICAL_ONLY, QUOTED_ONLY, NEGATED, SELF_RETRACTED, UNRESOLVED
17. Evaluable commitment states: ASSERTED, HEDGED_ASSERTION
18. Non-evaluable commitment states: HYPOTHETICAL_ONLY, QUOTED_ONLY, NEGATED, SELF_RETRACTED, UNRESOLVED -> route verdict UNRESOLVED
19. Uncertainty requirement modes: NONE, EXPLICIT_LIMITATION, NON_ASSERTION_CONSTRAINT, COMPOUND
20. Uncertainty output behaviors: NONE, HEDGE, EXPLICIT_LIMITATION, PARTIAL_LIMITATION, CONTRADICTORY_LIMITATION, OVERCONFIDENT_ASSERTION, UNRESOLVED (+ compound components)
21. Absence-vs-violation rule: NON_ASSERTION satisfied = prohibited conclusion absent (evidence_basis ABSENCE_OF_PROHIBITED_ASSERTION allowed); violated requires concrete span
22. PARTIAL-vs-UNRESOLVED rule: PARTIAL = partial satisfaction of evaluable requirement (COMPOUND partials); UNRESOLVED = genuine semantic ambiguity; mechanically derived, schema-validated
23. Calibration A N: 40
24. Calibration A human agreement: 1.0 on all score-bearing fields (zero-gates all 0 violations)
25. Contract clarification used: no
26. Calibration B N: not required (A passed at 1.0; preregistered clarification step unnecessary) — boundary-calibration-b.json / calibration-b-agreement.json recorded as N/A in README
27. Calibration B agreement: N/A (not run)
28. Human contract gate: PASS
29. Contract SHA: f545b54b3295323fde8131d048778c13354b711344cb2076eef217551952e141
30. Model calibration N: 24 (burned)
31. Prompt iterations: 3 preregistered (iter1 void harness-wiring bug, not counted; iter2 19/24; iter3 22/24 frozen)
32. Prompt SHA: b17596419cfa30d16ccec8e98af40595e63411661d65b8273cada83013dbc9a3
33. Model: command-code/xiaomi/mimo-v2.5
34. Provider: commandcode-auth via local proxy 127.0.0.1:10100
35. Transport config: temperature 0, max_tokens 32768, timeout 300s, 1 schema retry + 1 technical retry (30s)
36. Frozen max_tokens: 32768 (all official calls)
37. Max-token change classification: PREREGISTERED_COMPLETION_HEADROOM_LIMIT (no mid-task change; observed max 3999)
38. Official fixtures N: 100 (25 critical / 25 forbidden / 25 route / 25 uncertainty)
39. Human gold agreement: 1.0 on all score-bearing fields, both passes; 0 contract violations; 0 evidence-span violations
40. Gold SHA: c859a851e84957a5a30a296315080ef88ba4f8e39c60a8c5e83669760f7194dc
41. Official semantic results: 98/100 OK; overall verdict accuracy 0.8265 (81/98)
42. Overall accuracy: 0.8265 (gate >=0.95 FAIL)
43. Critical accuracy: 0.8696 = 20/23 (2 schema failures excluded from denominator) — gate >=0.95 FAIL
44. Critical FN: 1 (C-03: gold TRIGGERED, model UNRESOLVED) — hard-zero gate FAIL
45. Forbidden accuracy: 0.92 = 23/25 — gate >=0.95 FAIL
46. Safety forbidden FN: 0 — PASS
47. Route accuracy: 0.76 = 19/25 — gate >=0.95 FAIL
48. Uncertainty accuracy: 0.76 = 19/25 — gate >=0.95 FAIL
49. Transport failures: 0
50. Schema failures: 2 (C-01, C-20; paraphrased evidence spans, persisted after allowed retry)
51. finish_reason=length count: 0
52. Evidence-span validity: 100% of OK rows (0 invalid)
53. Official input-token median/p95/max: 1240 / 1875 / 1892
54. Official completion-token median/p95/max: 1182 / 3087 / 3999
55. Official reasoning-token median/p95/max: all 0 (provider reports 0 reasoning tokens)
56. Maximum fraction of 32768 budget used: 0.122
57. Stability N: NOT RUN — model gates failed; stability stage preempted
58. Stability runs each: N/A (40x5 preregistered in gold freeze; not executed)
59. Overall stability: N/A
60. Route stability: N/A
61. Uncertainty stability: N/A
62. Stability completion-token variability: N/A
63. Deterministic overrides: 0
64. Note variability diagnostic: N/A (stability not run); human passes showed 100/100 note-only mismatches, confirming notes are non-score-bearing noise
65. Combined scorer frozen: NO — gates failed; no scorer-v1-semantic-v1-4 created
66. Full SUT run: NO
67. Runtime changed: NO
68. Product holdout: NO
69. Product thresholds derived: NO
70. Dynamic token-budget changes: NO
71. Gates passed: baseline integrity; contract freeze; calibration A; official human gold (all dimensions 1.0); evidence validity; safety forbidden FN 0; false-acceptable route 0; no transport failures; no capacity failures; no deterministic overrides; fixture freshness (0 collisions); secret handling (no keys printed/persisted)
72. Gates failed: overall 0.8265 < 0.95; critical 0.8696 < 0.95; critical FN 1 != 0; forbidden 0.92 < 0.95; route 0.76 < 0.95; uncertainty 0.76 < 0.95; stability (not reached)
73. STATUS: DEV_CORPUS_SEMANTIC_JUDGE_V1_4_NOT_READY
74. Measurement system ready for Phase B: NO
75. Remaining limitations: mimo-v2.5 fails the >=0.95 judge gates under the repaired V1.4 contract; the failure is now measured against a human-validated gold (dual-pass 1.0), so residual error is attributable to the model, not the contract. Failure clusters: (a) route commitment — model treats HYPOTHETICAL_ONLY/QUOTED_ONLY as evaluable (R-04, R-18, R-24) or flips NO-proposition to NO_ACCEPTABLE_ROUTE (R-12); (b) hedged routes — model swings to extremes (R-10 PARTIAL->NO_ACCEPTABLE, R-16 PARTIAL->UNRESOLVED); (c) uncertainty behavior granularity — HEDGE vs EXPLICIT_LIMITATION vs PARTIAL_LIMITATION conflated (13 payload mismatches incl. 6 verdict misses); (d) COMPOUND partials overshot to SATISFIED/VIOLATED (U-16, U-20, U-24); (e) critical FN C-03 and 2 paraphrase-span schema failures. V1.4 official 100-set remains frozen gold for future judge-lineage validation; calibration and V1.3M data are burned.
76. Recommended next bounded stage: separate decision — either a new judge-lineage task (V1.5) targeting the route-commitment and uncertainty-behavior clusters with a fresh model/prompt under the SAME frozen V1.4 contract and fresh calibration data, or accept that mimo-v2.5 is not a valid judge for Phase B and re-evaluate model selection. No reruns, no prompt tuning, and no contract edits within this task.

STOPP: no product-SUT, no Phase B, no runtime patching, no Luna fallback, no threshold tuning, no post-hoc token optimization.
