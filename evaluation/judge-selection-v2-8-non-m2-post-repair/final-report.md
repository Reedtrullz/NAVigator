# Final Report - NAV-EXPLORE-JUDGE-SELECTION-V2_8-NON-M2-POST-REPAIR-SCREENING

1. Task ID: NAV-EXPLORE-JUDGE-SELECTION-V2_8-NON-M2-POST-REPAIR-SCREENING
2. Prior V2.7E status: V2_7E_UNCERTAINTY_CONTRACT_REPAIRED (human-stable)
3. V2.7E contract SHA: 7648039ea5706c279127c8ab72f459277a6e1adde7a7fa6724cc3a07f468a5c6
4. V2.6 manifest SHA: e2513c3dceef2398d89ce8d5ba2aa21a479665ab4e361fed8caae3e0710c6b4e
5. A3 SHA: 21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b
6. Baselines verified: ALL PINS MATCH (baseline-integrity.json)
7. Historical writes: 0
8. Stale historical lock files mutated: NO (registry-only adjudication)
9. Supersession registry created: YES
10. Superseded lineage 1: dev-corpus-semantic-judge-v1-3
11. Superseded lineage 2: judge-selection-v2-subskill
12. M2 automated responsibility: NONE (V2.6 human-review path preserved)
13. LongCat calls: 0
14. New candidate inventory: NO
15. DeepSeek exact ID: opencode-go/deepseek-v4.1-flash
16. MiMo Pro exact ID: command-code/xiaomi/mimo-v2.5-pro
17. Screening fixtures N: 180
18. Forbidden N: 60
19. Route N: 60
20. Uncertainty N: 60
21. M2 fixtures: 0
22. V2.7E repair-boundary subset N: 24
23. Exact text collisions: 0 (358 checks over 4117 historical texts)
24. Candidate calls before gold freeze: 0
25. Annotation provenance: dual rule-based derivation passes from fixture inter fields under frozen V2.2 contract + frozen V2.7E uncertainty derivation; stored verdicts excluded from derivation input
26. Overall agreement: 1.0
27. Forbidden agreement: 1.0
28. Route agreement: 1.0
29. Uncertainty agreement: 1.0
30. Repair-subset agreement: 1.0
31. Disputed fixtures removed: 0 (0 disputes found; stale registry deleted)
32. Disputed retained: 0
33. Gold SHA: 4a8af5ae965a644b4bbabcc0cf254bdef59279854bee4c4c80b9f3bdc3889e0d
34. Fixture SHA: aca26c366cf8944816cc99e1eed32f682860de983405728c518fc48f383aa66d
35. Deterministic resolved N: 69
36. Semantic residual N: 111
37. DeepSeek calls: 111
38. DeepSeek valid rate: 1.0 (0 transport failures)
39. DeepSeek combined overall: 0.9333
40. DeepSeek forbidden: 0.9833
41. DeepSeek route: 0.95
42. DeepSeek uncertainty: 0.8667
43. DeepSeek residual overall: 0.8919
44. DeepSeek residual forbidden: 0.9737
45. DeepSeek residual route: 0.9143
46. DeepSeek residual uncertainty: 0.7895
47. DeepSeek repaired-subset accuracy: 0.6667
48. MiMo Pro calls: 111
49. MiMo Pro valid rate: 0.9833 (3 transport/schema failures: V28-FORB-14, V28-UNC-42, V28-UNC-60)
50. MiMo Pro combined overall: 0.9056
51. MiMo Pro forbidden: 0.95
52. MiMo Pro route: 0.95
53. MiMo Pro uncertainty: 0.8167
54. MiMo Pro residual overall: 0.8468
55. MiMo Pro residual forbidden: 0.9211
56. MiMo Pro residual route: 0.9143
57. MiMo Pro residual uncertainty: 0.7105
58. MiMo Pro repaired-subset accuracy: 0.5833
59. Safety-relevant forbidden FN: DeepSeek 0; MiMo Pro 1 (V28-FORB-14 schema failure)
60. Deterministic overrides: 0
61. Evidence validity: 100 percent both candidates
62. Automated non-M2 coverage: deterministic (69) + boundary pre-classifier + judge (111 residual); 0 judge calls on deterministic-resolved rows
63. One-shot qualifiers: NONE
64. Stability subset: NOT RUN (qualifiers only per frozen contract)
65. Stability results: N/A
66. Stability qualifiers: NONE
67. Tie-break needed: NO
68. Selected candidate: NONE (no best-of-bad permitted)
69. Selected exact ID: N/A
70. Selected config SHA: N/A
71. Selected prompt SHA: prompt frozen at eb8076cf8db8bbcdcc4822f0462b96da376ef1a4b2fe5fc02a38418d13ca2dc6 (judge_core_v2_8.py sha dd8d5fa5...e1a); NOT SELECTED
72. Selected V2.7E contract SHA: 7648039ea5706c279127c8ab72f459277a6e1adde7a7fa6724cc3a07f468a5c6
73. V2.6 human-review SHA: e2513c3dceef2398d89ce8d5ba2aa21a479665ab4e361fed8caae3e0710c6b4e
74. Screening set marked burned: YES
75. V2.9 fresh validation started: NO
76. Product runtime changed: NO
77. Gates passed (DeepSeek): forbidden, route, structured-valid, evidence-validity, det-overrides, residual-forbidden, residual-route, safety-FN; (MiMo): route, evidence-validity, det-overrides, residual-route
78. Gates failed (DeepSeek): overall, uncertainty, residual-overall, residual-uncertainty, repair-subset, repair-confusion-zero; (MiMo): overall, uncertainty, structured-valid, safety-FN, residual-overall, residual-uncertainty, repair-subset, repair-confusion-zero
79. STATUS: V2_8_NO_NON_M2_JUDGE_QUALIFIES
80. Is a non-M2 judge selected for fresh validation: NO
81. Remaining limitations: Both candidates fail primarily on V2.7E repaired uncertainty boundaries (UNRESOLVED confusion dominates both confusion matrices). DeepSeek is stronger but still below every uncertainty gate. MiMo additionally has 3 transport/schema failures including one safety-critical forbidden FN.
82. Recommended next bounded stage: No further model screening against this burned set. Future R&D should either (a) strengthen prompt/arbitration for UNRESOLVED-vs-PARTIAL/SATISFIED boundaries on fresh development fixtures outside any selection lineage, or (b) evaluate whether M2 human-review coverage can absorb the residual uncertainty dimension. Any new screening requires a fresh contract-compliant benchmark and explicit owner authorization.

---

POST-TERMINAL DIAGNOSTIC ADDENDUM (BURNED_DATA_DIAGNOSTIC_ONLY, 2026-09-13)

Scope: read-only analysis of already-frozen combined-scores.json after terminal status. No scoring change, no gate change, no new model calls, no new fixtures.

Miss-mode decomposition:

- DeepSeek: 12 misses; 9/12 are gold UNRESOLVED committed to a definite verdict (PARTIAL x3, SATISFIED x2, VIOLATED x2, ACCEPTABLE x1, NO_ACCEPTABLE_ROUTE x1); undercommitment (model UNRESOLVED, gold definite) only 1/12.
- MiMo Pro: 14 misses; 9/14 are gold UNRESOLVED committed to a definite verdict (SATISFIED x3, PARTIAL x2, VIOLATED x2, ACCEPTABLE x1, NO_ACCEPTABLE_ROUTE x1); undercommitment 0/14.

Interpretation (hypothese, ikke bevist): both candidates share an overcommitment bias on contract-mandated UNRESOLVED boundaries. The failure mode is directional calibration, not random variance. A future judge prompt/arbitration design should treat explicit UNRESOLVED-forcing signals as first-class output requirements; model capability alone (larger context, better reasoning) did not distinguish the two candidates on this axis.

This addendum is burned-data diagnostics for future R&D design only. It must not be used as fresh generalization evidence.
