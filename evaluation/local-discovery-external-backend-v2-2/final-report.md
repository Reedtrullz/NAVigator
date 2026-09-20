# FINAL REPORT - LOCAL DISCOVERY EXTERNAL BACKEND SELECTION V2.2

Date: 2026-09-09. Workdir: `/Users/reidar/Projectos/NAV Explore`.
Subagents used: 0 (no GPT-5.5; none needed for a documentation-only task).

## Blocking outcome

`BACKEND_SELECTION_BLOCKED_BY_CREDENTIALS` (task section 9).

The credential gate ran first and found no authorized credential for either
structured external candidate, so the comparative benchmark was never
started. Per task section 8 this is not a backend failure, and per section
9 no account creation, plan activation, or key generation was attempted.

## Report points

1. Task ID: `NAV-EXPLORE-LOCAL-DISCOVERY-EXTERNAL-BACKEND-SELECTION-V2_2`.
2. Prior status: `LOCAL_DISCOVERY_PROVIDER_V2_1_ADAPTER_FIXED_BACKEND_NOT_READY`.
3. Fresh municipalities used: 0.
4. Protocol V1 unchanged: yes - SHA `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca` re-verified.
5. Candidate V2 unchanged: yes - manifest SHA `74329662e2df1e8bffb69165b3c39820af6313e7a3096fe6754d78f80977a678` re-verified.
6. V2.1 snapshot integrity: 7/7 files match manifest sha256 values.
7. Brave HTML negative control preserved: yes; not re-probed or re-evaluated.
8. Candidate backends considered: BASELINE A (site-direct-only), CANDIDATE B (Brave Search API), CANDIDATE C (Tavily Search API). No additional backend.
9. Brave Search API credential available: NO (`NOT_AVAILABLE`).
10. Tavily credential available: NO (`NOT_AVAILABLE`).
11. Additional backend: none; optional-candidate criteria (existing authorized credential, structured API) not met by any further backend.
12. Accounts created: 0.
13. Paid plans activated: 0.
14. Benchmark queries N: 0 (not started; gate blocked).
15. Benchmark municipalities N: 0 (not started; gate blocked).
16. Site-direct execution: not run in this task; prior V2.1 evidence stands at 5/5 PASS on burned data.
17. Site-direct relevant-target recall: not measured in this task.
18. Brave API testable: NO (`NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL`).
19. Brave API execution rate: not measured.
20. Brave API target recall: not measured.
21. Brave API top-3/top-5/top-10 recall: not measured.
22. Brave API official-domain precision: not measured.
23. Brave API bot-block rate: not measured (official API not probed; Brave HTML remains disqualified).
24. Brave API provider errors: none observed (no calls made).
25. Tavily testable: NO (`NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL`).
26. Tavily execution rate: not measured.
27. Tavily target recall: not measured.
28. Tavily top-3/top-5/top-10 recall: not measured.
29. Tavily official-domain precision: not measured.
30. Tavily bot-block rate: not measured (no calls made).
31. Tavily provider errors: none observed (no calls made).
32. Additional backend metrics: N/A.
33. Site-direct recovery: not re-run; V2.1 result preserved.
34. Brave incremental recovery over site-direct: N/A.
35. Tavily incremental recovery over site-direct: N/A.
36. Failure simulations: not run (no adapter code exists to test).
37. False failure->NO_RESULTS: 0 (no runs; invariant remains enforced by V2.1 tests for the brave_html adapter).
38. Secret leak scan: 0 - no keys exist; presence-only checks; no values printed, logged, or persisted.
39. Eligible backends: none testable.
40. Selection rule: frozen for restart (recall > execution reliability > official-domain precision > incremental recovery > operational simplicity > latency/cost).
41. Selected backend: none.
42. Qualified alternate: none.
43. Selection rationale: credential gate blocked before benchmark; per section 9 this is a blocker, not a gate failure.
44. V2.2 adapter implemented: no (task section 9 stops before candidate work; adapter budget applies only to testable candidates).
45. V1 tests: 49/49 OK (re-run this task).
46. V2 tests: 27/27 OK (re-run this task).
47. V2.1 tests: 19/19 OK (re-run this task).
48. V2.2 tests: 0 (no runtime V2.2 code exists; task scope for this terminal was documentation-only).
49. Burned integration: 0/13 (not run; gate blocked).
50. Critical route regressions: 0 (no runtime changes).
51. Unsupported FULLY_VERIFIED: 0 (no runtime changes).
52. Forced fallback tests: 0 (not run; gate blocked).
53. Forced fallback discovery: N/A.
54. Final authoritative provenance preserved: yes - provenance doctrine untouched; search-output-is-discovery-only invariant unchanged.
55. Security tests: not re-run (no new code); V2.1 security regression artifacts remain valid and untouched.
56. Provider config V2.2 SHA: none (artifact not created - frozen config requires a selected backend).
57. Candidate V2.2 frozen: NO.
58. Candidate V2.2 manifest SHA: none.
59. Historical files modified: 0.
60. Gates passed: credential discovery (section 7), historical integrity (section 1), no-fresh-data (section 2), secret safety (section 26), regression suites (section 40).
61. Gates failed: none failed outright; benchmark, integration, fallback, and freeze gates were NOT_REACHED (blocked, not failed).
62. STATUS: `BACKEND_SELECTION_BLOCKED_BY_CREDENTIALS`.
63. Is fresh V2.2 evaluation justified: no - no new runtime exists; fresh eval would test nothing new.
64. Remaining limitations: no working external search fallback exists in this lineage; Brave HTML stays bot-blocked; backend selection deferred until an authorized credential is supplied by the user.
65. Recommended next bounded stage: user decision on supplying an authorized Brave Search API or Tavily credential, then a new bounded task executing the frozen restart contract in `backend-selection-contract-restart.md`; otherwise remain site-direct-first with external fallback disabled.

## Deliverable notes

Of the task section 46 deliverables, the credential-gate-relevant artifacts
were produced (this report, TASK-LOCK, README, historical-integrity,
credential-availability, the two backend-result files carrying the allowed
`NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL` marker, the selection decision, and
the restart contract). Benchmark/integration/security/config artifacts were
intentionally NOT fabricated: they require the benchmark run that the
credential gate blocked.
