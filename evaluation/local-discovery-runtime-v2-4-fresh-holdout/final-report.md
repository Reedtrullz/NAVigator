# FINAL REPORT - V2.4 FRESH HOLDOUT

Task: `NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-FRESH-HOLDOUT`
Status: **LOCAL_DISCOVERY_RUNTIME_V2_4_FRESH_HOLDOUT_FAIL**
Official score SHA256: `0aa3fb08e0cc0a32df6151bdcfe72bacdc0cf829862123221d2d566f9dec11e4`

## 1-11. Provenance and setup

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-FRESH-HOLDOUT
2. Prior status: LOCAL_DISCOVERY_RUNTIME_V2_4_READY_FOR_FRESH_EVAL
3. Candidate manifest SHA256: `6f7e7ab3fe5f1576a5ca03f9509aa5fd06928b607cebc462702ca1e3ec393a2d`
4. Candidate files verified: 14/14 components matched (candidate-integrity.json)
5. Candidate changes: 0 (re-verified after run; 0 files modified under candidate-runtime-v2-4/ during task)
6. Protocol SHA256: `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca`
7. Protocol changes: 0
8. TDD historical deviation preserved: yes (`tdd_sequence_deviation_preserved = true` in historical-integrity.json); metadata only, not a holdout failure
9. Class-1 exhaustion artifact: `data/local-discovery-generalization-sample-v1.json`
10. Class-1 exhaustion code: `SAMPLE_DEVIATION_KLASSE1_POOL_EXHAUSTED`
11. Fresh class-1 pool: 0 (preregistered exclusion, not a sample deviation)

## 12-19. Readiness (burned data only)

12. Readiness municipalities: Raellingen (3224, platform), Drammen (3301), Bamble (4012), Bjerkreim (1114), Alstahaug (1820)
13. Root readiness: 5/5
14. Fetch readiness: 5/5
15. Navigation readiness: PASS (Drammen level-2 NAVIGATION_LINK case)
16. Sitemap readiness: PASS (Raellingen platform path)
17. Render readiness: PASS (capability present, bounded probe OK; no burned case required render)
18. Readiness passed before sample burn: yes
19. Failure policy frozen before sample: yes (SHA `cb10e4be4321511b70dc3b48f7b7ccd055f0e11a4176fe062ed9ec965a98264d`)

## 20-36. Fresh sample

20. Freshness audit method: project-wide search on municipality name + number over full NAV Explore repo; classification UNSEEN / INCIDENTAL_MENTION_ONLY / PREVIOUSLY_RESEARCHED; burned exclusion sources per contract section 19
21. Eligible pool class 2: 15 (registry total 21)
22. Eligible pool class 3: 48 (registry total 54)
23. Eligible pool class 4: 59 (registry total 65)
24. Eligible pool class 5: 95 (registry total 104)
25. Eligible pool class 6: 97 (registry total 108)
26. Fresh municipalities: Eigersund 1101, Haå 1119, Tysvær 1146, Sandnes 1108, Sola 1124, Moss 3103, Klepp 1120, Time 1121, Gjesdal 1122, Sokndal 1111, Lund 1112, Hjelmeland 1133, Suldal 1134, Kvitsøy 1144, Utsira 1151
27-31. Distribution: class 2 = 3, class 3 = 3, class 4 = 3, class 5 = 3, class 6 = 3
32. Selection method: ORDINAL_MUNICIPALITY_NUMBER_ASC_FIRST_3 (no seed, no judgment)
33. Sample substitutions: 0
34. Previously researched selected: 0
35. Geographic spread: 14 Rogaland + 1 Østfold (Moss) - deterministic outcome, no geography override
36. Sample SHA256: `714f9b1b10bbea40d814943df18bf076631948ccbd74f96a5c8a4cecd8b82e45`

## 37-46. Execution

37. Execution order: municipality_number ASC, scenario C (19) before D (22); frozen before first cell
38. Runtime cells attempted: 30/30
39. Complete discovery: 24/30 (gate >= 29/30: **FAIL**)
40. Discovery incomplete: 6 (Klepp C/D, Kvitsoy C/D, Tysvaer C/D)
41. DNS failures: 0
42. Fetch failures: 0
43. Timeout failures: 0
44. Render failures: 0 (render_fallbacks = 0 across all cells)
45. Parse failures: 0
46. Internal runtime failures: 0

## 47-53. Freeze and audit

47. Predictions frozen before audit: yes (status marker `V2_4_RUNTIME_PREDICTIONS_FROZEN_BEFORE_AUDIT`)
48. Prediction SHA256: `dea6c21567c75751a1d1fc668a7a2e51fd37e77a581cfcf7e7a6b410b8b31fda`
49. Auditors used: 2 GPT-5.6-Luna subagents (Auditor A 8 municipalities, Auditor B 7 municipalities, disjoint sets)
50. Auditor independence: blind - no access to runtime outputs, routes, states or failures before H8 freeze; audit-side public research only
51. Audit cells complete: 30/30
52. Audit unresolved: 0
53. Audit SHA256: `6b2ff2fbd9ae6631527f7a6a92697c358c9793186d38e403ce21ae617eacb720`

## 54-70. Hard metrics (frozen contracts)

54. Auditor-verified routes: 30/30 cells had documented relevant route
55. Runtime recovered routes: 24/30
56. Route recovery: 24/30 = 80.0% (gate >= 90%: **FAIL**)
57. FULLY_VERIFIED cells: 10
58. Confirmed FULLY_VERIFIED: 3 (Lund C/D, Utsira C)
59. FULLY_VERIFIED precision: 3/10 = 30.0% (gate >= 95%: **FAIL**)
60. Unsupported FULLY_VERIFIED: 7 (gate = 0: **FAIL**)
61. Access assertions evaluated: 15 (exact audit-cited pages only)
62. Confirmed access assertions: 8
63. Access precision: 8/15 = 53.3% (gate >= 95%: **FAIL**)
64. Route-unverified: 6 ROUTE_UNVERIFIED (all DISCOVERY_INCOMPLETE) + 14 EXISTENCE_ONLY
65. Critical false-no-route: 0 (gate = 0: **PASS**)
66. Noncritical false-no-route: 0 (6 incomplete cells are canonical DISCOVERY_INCOMPLETE, excluded per section 48)
67. Provenance-authorizing assertions: 10/10
68. Provenance completeness: 100% (gate 100%: **PASS**)
69. Epistemic-state accuracy: 3/30 = 10.0% (gate >= 90%: **FAIL**); classes: correct 3, overclaim 7, underclaim_access_documented 14, underclaim_audit_resolved 6
70. Materially overconfident outputs: 14 (certain-access wording on EXISTENCE_ONLY cells; gate = 0: **FAIL**)

## 71-87. Descriptive routing and structure

71. Both-age routable municipalities: 12
72. Only-19: 0
73. Only-22: 0
74. Neither: 3 (Klepp, Kvitsoy, Tysvaer - all discovery misses, not documented no-offer)
75. Routing-cliff cases: 0 detected (no only-19/only-22 splits; the neither-cases are execution failures)
76. Auditor intermunicipal routes: 4 non-municipal (3 intermunicipal: Kvitsoy C/D, Tysvaer C; 1 specialist: Klepp D)
77. Runtime intermunicipal routes: 0 recovered
78. Level 0-1 recovery: 0
79. Level 2: 24
80-82. Level 3 / 4 / 5: 0 / 0 / 0
83. Class 2 (Moss, Sandnes, Sola): 6/6 complete, 6/6 recovered (2 EXISTENCE_ONLY, 4 FV)
84. Class 3 (Gjesdal, Klepp, Time): 4/6 complete, 4/6 recovered (Klepp C/D incomplete)
85. Class 4 (Eigersund, Ha, Tysvaer): 4/6 complete, 4/6 recovered (Tysvaer C/D incomplete)
86. Class 5 (Sokndal, Lund, Hjelmeland): 6/6 complete, 6/6 recovered (4 EXISTENCE_ONLY, 2 FV)
87. Class 6 (Suldal, Kvitsoy, Utsira): 4/6 complete, 4/6 recovered (Kvitsoy C/D incomplete)

## 88-99. Miss taxonomy (after H10 freeze)

88. Root-resolution misses: 0
89. Site-direct discovery misses: 6 (primary: Klepp C/D, Kvitsoy C/D, Tysvaer C/D - root+sitemap attempts only, 0 content pages, renderer never triggered)
90. Navigation misses: 1 contributing (Klepp C: auditor found HFU via same betreinnsats platform runtime reached)
91. Sitemap misses: 0 primary (sitemap fetched OK but yielded zero candidates - extraction/scope failure counted as site-direct)
92. Render misses: 0 (renderer never invoked; no candidate pages produced)
93. Extraction misses: 0 primary
94. Age misses: 2 contributing (Gjesdal D, Utsira D overclaim without confirmed age)
95. Access misses: 0 primary (7/15 access token failures recorded under access precision)
96. Intermunicipal misses: 3 contributing (all intermunicipal/specialist routes missed)
97. Route-evaluation misses: 7 primary (FV overclaims: 1122 C/D, 1124 C/D, 1151 D, 3103 C/D)
98. Provenance failures: 0
99. Source-availability failures: 0 (all sources responded; misses are extraction/discovery scope, not availability)

## 100-107. Security, integrity, verdict

100. Security observations: 0 SSRF blocks, 0 private-IP blocks, 0 scheme/redirect/malformed rejects; security layer unchanged throughout
101. External search calls: **0** (requirement met)
102. Historical writes this task: **0** (requirement met)
103. Candidate SHA after run: `6f7e7ab3fe5f1576a5ca03f9509aa5fd06928b607cebc462702ca1e3ec393a2d` (unchanged)
104. Gates passed: 14 of 21
105. Gates failed: complete_discovery, route_recovery, fully_verified_precision, access_precision, unsupported_fully_verified, epistemic_state_accuracy, materially_overconfident_outputs
106. Official-score SHA256: `0aa3fb08e0cc0a32df6151bdcfe72bacdc0cf829862123221d2d566f9dec11e4`
107. STATUS: **LOCAL_DISCOVERY_RUNTIME_V2_4_FRESH_HOLDOUT_FAIL**

## 108-110. Assessment and next step

108. Does fresh evidence support V2.4 generalization? **No.** Burned-benchmark performance (117/117) did not transfer: 6/30 cells failed discovery on Rogaland platform/sectioned sites, FV precision collapsed to 30%, and uncertainty wording contradicted route states. Correct fail-closed behavior held (no fabricated routes, 0 critical false-no-route, DISCOVERY_INCOMPLETE preserved).
109. Remaining limitations: (a) sitemap-only extraction is brittle on betreinnsats/sectioned platforms and renderer fallback never triggers because no candidate pages are produced; (b) FULLY_VERIFIED state semantics accept section-level provenance; (c) access extraction misses concrete contacts on EXISTENCE_ONLY cells; (d) user-facing certainty wording is inconsistent with epistemic state; (e) intermunicipal/specialist gateways are outside site-direct scope; (f) deterministic selection yielded heavy Rogaland skew - by design, no override. Documented deviations preserved: H5 operator kill of 1146-C (no evidence consumed before authorized identical rerun, h5-kill-deviation.json) and crash-resume SKIP lines (one official run per cell retained).
110. Recommended next bounded stage: separate engineering task with fresh lineage (no holdout reuse): (1) discovery fallback chain - navigation-link discovery when sitemap yields zero candidates, renderer trigger on empty extraction; (2) tighten FULLY_VERIFIED to require service-specific provenance; (3) access extraction from section pages; (4) harmonize uncertainty wording with epistemic state. Then a NEW fresh holdout task. No patching performed in this task.

## Deviations register

- `H5_OPERATOR_KILL_1146_C`: operator polling error killed the frozen process at 175s (frozen timeout 900s). No output existed and no evidence was consumed before the kill; one identical authorized rerun of only that cell. Preserved permanently in `h5-kill-deviation.json`. Not treated as runtime failure or protocol break.
- `H5_CRASH_RESUME_SKIPS`: batch log shows SKIP-existing-output lines during crash-resume; each cell retained exactly one official execution.
