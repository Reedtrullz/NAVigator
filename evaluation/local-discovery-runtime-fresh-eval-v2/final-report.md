# FINAL REPORT - NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-FRESH-EVAL-V2

Date: 2026-09-09. STATUS: RUNTIME_FRESH_EVAL_V2_BLOCKED_BY_PROVIDER.
Fresh sample created = false. Fresh municipalities burned = 0.

The evaluation stopped at E1 (provider readiness on burned data) per the strict
sequence. Nothing downstream (E1.5 through E7) was started; the items below are
reported as NOT REACHED where the spec asks for them.

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-FRESH-EVAL-V2.
2. Prior status: LOCAL_DISCOVERY_PROVIDER_V2_READY_FOR_FRESH_EVAL.
3. Candidate manifest SHA: 74329662e2df1e8bffb69165b3c39820af6313e7a3096fe6754d78f80977a678.
4. Candidate files verified: 21/21 match (candidate-integrity.json); manifest SHA exact.
5. Candidate changes: 0.
6. Protocol SHA: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca.
7. Protocol changes: 0.
8. Provider config SHA: d6890b5f97c8dd12eb915114c571a8ba930b75aa00fdd0c5a373965c5423cbc3 (frozen, unchanged).
9. Site-direct readiness: 5/5 PASS (Alta, Farsund, Sor-Varanger, Alstahaug, Hasvik; frozen run_v2 stack, Stage-A roots from benchmark corpus; all COMPLETE with provenance).
10. External fallback readiness: 0/5 FAIL (gate >= 4/5).
11. Bot blocks observed: site-direct 0; external backend served HTTP 429 challenge pages (73 KB, captcha/challenge markers) on raw probe and through the adapter path on all attempts; persistent after 90 s backoff.
12. Provider readiness PASS: NO - external fallback gate failed.
13. Fresh sample created only after readiness: not reached; sample never created.
14. Class-1 exhaustion recorded: preregistered as CENTRALITY_CLASS_1_FRESH_POOL_EXHAUSTED in the task spec; sample stage not reached.
15. Exposure pool N: not reached (0).
16. Fresh municipalities N: 0.
17-21. Class 2/3/4/5/6 N: 0 each (not reached).
22. Geographic spread: not reached.
23. Previously researched N: 0 (nothing sampled).
24. Sample SHA: none (no sample created).
25. Runtime cells attempted: 0/30 (one-shot run never started).
26. Complete discovery N: 0 (not reached; gate >= 29/30 not evaluable).
27. Discovery incomplete N: 0 (not reached).
28. Predictions frozen before audit: not reached.
29. Prediction SHA: none.
30. Auditor independence: not reached (no subagents used).
31. Audit cells completed: 0.
32. Audit SHA: none.
33. Auditor-verified routes N: 0.
34. Runtime recovered routes N: 0.
35. Route recovery raw/%: not evaluable (denominator 0).
36. FULLY_VERIFIED N: 0.
37. Confirmed FULLY_VERIFIED: 0.
38. FULLY_VERIFIED precision: not evaluable.
39. Unsupported FULLY_VERIFIED: 0 (trivially; nothing ran).
40. Access assertions N: 0.
41. Confirmed access assertions: 0.
42. Access precision: not evaluable.
43. Route-unverified N: 0.
44. False-no-route N: 0.
45. Critical false-no-route N: 0.
46. Provenance-authorizing assertions: 0.
47. Provenance completeness: not evaluable (E1 site-direct paths: provenance captured on all successful paths).
48. Epistemic-state accuracy: not evaluable.
49. Overconfident uncertainty outputs: 0.
50. Site-direct recovered routes: not reached (E1 site-direct technical runs: 5/5 COMPLETE, Farsund ROUTE_FULLY_VERIFIED).
51. External fallback activations: 0.
52. External fallback successes: 0.
53. Incremental routes from fallback: 0.
54. Site-direct provider failures: 0.
55. External provider failures: 5/5 readiness probes + 1 confirmation probe (persistent 429 challenge misreported as NO_RESULTS by frozen adapter).
56. Fetch failures: 0 on site-direct paths.
57. Render failures: 0.
58-62. Discovery depth L0-1/L2/L3/L4/L5: not reached.
63. Intermunicipal auditor routes: not reached.
64. Intermunicipal runtime routes: not reached.
65-68. Both-age routability: not reached.
69. Centrality findings: not reached.
70. Miss taxonomy: PROVIDER_FAILURE (external backend persistent 429 challenge); plus a frozen-adapter classification defect (curl exit code 0 mapped to HTTP 200, so 429 and the 73 KB challenge body never reach the 429 classification or the 5000-char bot-marker scan head) - documented, NOT patched, per task lock.
71. Security observations: 0 security rejections in E1; no security behavior weakened (security-observations.json).
72. Historical files modified: 0 (historical-integrity.md / .json: Protocol V1, candidate V1, candidate V2, docs 71-74, prior reports/fixtures/samples all verified unchanged).
73. Gates passed: candidate integrity; protocol integrity; site-direct readiness 5/5; fetch 5/5; provenance on all successful E1 paths; site-direct bot blocks 0; historical files modified 0.
74. Gates failed: external fallback readiness 0/5 (requires >= 4/5); systematic bot block zero (external backend blocked).
75. Official-score SHA: none (E6 not reached).
76. STATUS: RUNTIME_FRESH_EVAL_V2_BLOCKED_BY_PROVIDER.
77. Does fresh evidence support V2 runtime generalization: NO - no fresh evidence exists; nothing was generalized or tested on fresh municipalities.
78. Remaining limitations: (a) external fallback capability is not operational in practice - brave_html serves persistent 429 challenge pages at current volumes; (b) frozen adapter misclassifies that failure as NO_RESULTS (curl exit 0 -> HTTP 200; challenge markers beyond the 5000-char scan head), which contradicts the V2 no-conflation intent and is invisible to the composite health model; (c) site-direct path alone remains healthy (5/5) but is a single capability until the fallback is repaired in a future R&D task.
79. Recommended next bounded stage: a new provider-architecture R&D task (V2.1) - fix the adapter's HTTP status mapping so real 429/challenge responses reach classify_http_response, extend the BOT_MARKERS scan to the full body (or at minimum beyond the current head-only scan), re-run E1 gates on burned data, and only then re-attempt this fresh eval with a new task ID. The frozen V2 candidate is NOT patched in this task.

STOP. No fresh eval performed. No runtime patching. No deployment. No decision-engine integration.

