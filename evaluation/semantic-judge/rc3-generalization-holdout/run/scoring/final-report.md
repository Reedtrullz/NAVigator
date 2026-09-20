# G2 SLUTTRAPPORT - RC3 GENERALIZATION HOLDOUT

1. Task ID: NAV-EXPLORE-RC3-GENERALIZATION-G2
2. Prediction SHA verified: 6923c66c8abafde0bd0e3e58a282e2b40a3da4adefd3a364b25cddcd3a88a361 (159 outcomes)
3. Scoring-policy SHA verified: 89abe4c2097ea97352e1133c600b4c70cf6a83afbb351744f27764cc5fff9e99
4. Scorer SHA verified: 866f83786e8a9de7528e7c88f9d0d3e5951f47466f819a747e6913c610a53c2b
5. Snapshot hashes before: NAV-EXPLORE-RC3-GEN-SNAPSHOT-A, 14/14 components OK
6. Holdout hashes before: cases 3f22c19b...720d4, sealed key e25b3ab8...2498a, sealed audit 2b26675d...3863b1
7. Key authenticated: TRUE (AES-256-GCM, AAD = cases SHA; key from env only)
8. Key persisted: NO (repo, shell history, and /tmp scans all clean after run)
9. Answer-key rows: 159 labels; adjudication: 140 PASS1_PASS2_AGREE, 9 ADJUDICATED_P2, 6 ADJUDICATED_P1, 4 ADJUDICATED_ATOM
10. ID equality: PASS (159 prediction IDs == 159 label IDs)
11. Overall denominator: 159
12. Semantic correct/N: 26/159
13. Semantic accuracy: 16.35 percent
14. Semantic CI (Wilson 95): 11.41 - 22.88
15. Semantic gate: FAIL (threshold 90)
16. Proof-safe correct/N: 44/159
17. Proof-safe accuracy: 27.67 percent
18. Proof-safe CI: 21.31 - 35.09
19. Proof-safe gate: FAIL (threshold 95)
20. Product correct/N: 60/159
21. Product accuracy: 37.74 percent
22. Product CI: 30.57 - 45.48
23. Product gate: FAIL (threshold 95)
24. Predicted auto N: 24
25. Auto coverage: 15.09 percent
26. Auto coverage floor: 20 percent
27. Auto coverage gate: FAIL (predetermined in G1.5 freeze before this run)
28. AUTO_SUPPORTED precision: 7/13 = 53.85 percent
29. AUTO_CONTRADICTED precision: 3/11 = 27.27 percent
30. Combined auto precision: 10/24 = 41.67 percent (CI 24.47 - 61.17)
31. Auto precision gate: FAIL (threshold 99)
32. Emitted proof objects: 137
33. Structurally valid proofs: all accepted proofs structurally valid (0 invalid of 64 accepted)
34. Accepted proofs: 64 (atom-level, auto-routed)
35. Structurally invalid accepted proofs: 0
36. Ungrounded accepted proofs: 0
37. Semantically unsound accepted proofs: 53 of 64 accepted atoms
38. Proof-safe unsound autos: 14 of 24 auto cases
39. Proof gates pass: NO. Preregistered gate artifacts print PASS on all four zero-tolerance gates, but the frozen scorer's gate_results has a denominator-0 short-circuit making those gates unable to fail. Recomputed from raw counts: structural 0 (true pass), ungrounded 0 (true pass), semantically unsound 53 (FAIL), proof-safe unsound autos 14 (FAIL). Registered as scorer defect; official score artifact preserved unpatched.
40. Necessary-review TP/FN: TP 34, FN 10
41. Necessary-review recall: 77.27 percent
42. Review recall gate: FAIL (threshold 95)
43. Unnecessary reviews: 82 of 116 predicted reviews
44. Unnecessary-review rate: 70.69 percent
45. Unnecessary-review gate: FAIL (limit 15)
46. Expected abstains: 35
47. Predicted abstains: 17
48. Abstain TP/FN: TP 16, FN 19
49. Abstain recall: 45.71 percent
50. Abstain gate: FAIL (threshold 90)
51. Review-vs-abstain macro F1: 0.520
52. Macro-F1 gate: FAIL (threshold 0.90)
53. Compound cases: 52
54. Expected atoms: 119
55. Predicted atoms (compound cases): 106
56. Atom-count exact: 35/52 = 67.31 percent
57. Atom semantic correct/N: 53/119
58. Atom semantic accuracy: 44.54 percent
59. Missing atom rate: 15/119 = 12.61 percent
60. Extra atom rate: 2/119 = 1.68 percent
61. Aggregation correctness: 29/52 = 55.77 percent
62. Compound product correct/N: 29/52
63. Compound product accuracy: 55.77 percent
64. Compound gates: atom semantic FAIL (44.54 vs 90), compound product FAIL (55.77 vs 90)
65. Critical subgroup: semantic 4/25, proof-safe 6/25, product 16/25 (64.0 percent)
66. Track A representative: semantic 13/75 (17.33), proof-safe 22/75 (29.33), product 16/75 (21.33)
67. Track B stress: semantic 13/84 (15.48), proof-safe 22/84 (26.19), product 44/84 (52.38)
68. Other preregistered subgroups: none beyond critical/track_A/track_B in g2-subgroup-index.json
69. Runtime failures: 0
70. Runtime gate: PASS
71. Number of hard gates: 16
72. Gates passed: 5 gate artifacts (runtime_exceptions, structural_invalid, ungrounded; semantically_unsound and proof_safe_unsound print PASS via the gate defect but numerically FAIL)
73. Gates failed: 11 (semantic, proof_safe, product, auto_precision, auto_coverage, necessary_review_recall, unnecessary_review_rate, abstain_recall, review_abstain_macro_f1, compound_atom_semantic, compound_product) plus the two numerically-failed zero-tolerance proof gates masked by the gate defect
74. Official score SHA: 384e1a21798001041d961ab06b0f5111f3b3077d6e3b519f56fff7aa739a61bb
75. Official score frozen before error inspection: YES (freeze timestamp precedes error-analysis artifacts; error_analysis_started = false in official artifact)
76. Error severity counts: CRITICAL 14, HIGH 85, MEDIUM 34, LOW 0, OK 26
77. Major root causes: (a) semantic default collapse to REVIEW_REQUIRED on novel phrasing (118 of 133 semantic misses), (b) semantic unsoundness of accepted proofs (53/64 atoms) driven by negation/deontic scope at atom level, (c) under-decomposition on compounds (15 missing atoms), (d) abstain under-triggering (45.71 recall), (e) arbitration never exercised (reviewer_used = 0, keyless engine-only run)
78. Potential label errors: 0 registered (POTENTIAL_GENERALIZATION_LABEL_ERROR count = 0)
79. Alternate sensitivity: identical to official scores (product 37.74 percent, auto 41.67 percent) since no candidates
80. Construction audit accessed: YES, once, pre-freeze, for critical-membership derivation only; logged in run_g2_scoring.py and label-audit.md
81. Snapshot hashes after: 14/14 OK (re-verified post-scoring)
82. Prediction SHA after: unchanged, 6923c66c...a88a361
83. Holdout hashes after: unchanged (cases, sealed key, sealed audit all match pre-run values)
84. Policy/scorer hashes after: unchanged (89abe4c2... / 866f8378...)
85. Reruns: 0 (frozen scorer executed exactly once; unit self-test does not touch predictions)
86. Tuning: NO
87. Runtime modified: NO
88. Key/plaintext cleanup: key never written to disk; no plaintext labels on disk; repo, shell history, and /tmp scans clean
89. QA: prediction/policy/scorer/cases/keys SHA re-verified; snapshot 14/14; 159 ID equality; confusion totals 159/159/159; gates all evaluated; freeze-before-inspection verified; frozen-scorer unit test 1/1 passed
90. READINESS VERDICT: GENERALIZATION_FAIL
91. Did proof-soundness generalize: NO (53/64 accepted atoms semantically unsound; structural validity and grounding held at 0 failures)
92. Did auto precision generalize: NO (41.67 percent vs 99 percent gate)
93. Did routing generalize: NO (coverage 15.09 percent, unnecessary review 70.69 percent)
94. Did abstention generalize: NO (recall 45.71 percent; macro F1 0.520)
95. Did compound decomposition generalize: NO (atom-count exact 67.31 percent; atom semantic 44.54 percent; under-decomposition dominant)
96. Did semantic/proof/product exactness generalize: NO (16.35 / 27.67 / 37.74 percent)
97. Main architectural conclusion: The deterministic proof scaffolding (structural validation, span grounding, runtime stability) transferred to novel data; the semantic-judgment, decomposition, and routing-calibration layers did not. RC3's auto path is unsound on novel inputs, and its non-auto default over-triggers REVIEW. The evaluator remains a tuned-development artifact, not a generalizing evaluator.
98. Should evaluator R&D continue: YES - architecture repair continues, but routing/calibration-only work is contraindicated while the auto path is semantically unsound
99. Should RC3 candidate be frozen next: NO - the current architecture must not be re-frozen; repair soundness and decomposition first
100. Recommended next step: One bounded R&D task: (1) fix the scorer's zero-tolerance gate denominator defect, (2) atom-level semantic soundness validator with clause-scope negation/deontic handling, (3) decomposition coverage (missing-atom class), then re-gate on development before any future generalization retest. No new blind set until development gates pass again.

Integrity statement: official-generalization-score.json is byte-for-byte the frozen artifact (SHA 384e1a21...1bb). Error analysis is post-freeze, aggregate-only, and non-mutating. No tuning, no rerun, no runtime changes, no new blind set, no certification claim. This result is a BLIND GENERALIZATION HOLDOUT measurement, not a certification.
