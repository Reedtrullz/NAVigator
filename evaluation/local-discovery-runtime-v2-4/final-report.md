# V2.4 Root-Resolution Repair - Final Report

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-ROOT-RESOLUTION-REPAIR
Date: 2026-09-09. All official artifacts in evaluation/local-discovery-runtime-v2-4/.

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-ROOT-RESOLUTION-REPAIR
2. Prior status: V2_3_CERTIFICATION_FAIL_RUNTIME_CHANGE_REQUIRED (V2.3 remains a historically failed certification candidate; untouched).
3. Root cause reproduced? YES, before any code change (root-cause-verification.md; historical resolver output https://ralingen.bedinnsats.no/ corroborated by 4 sources).
4. Historical incorrect root: https://<slug>.bedinnsats.no/ (platform roots).
5. Expected canonical root: https://<slug>.bedreinnsats.no/ (platform roots; kommune.no pass-through untouched).
6. Root-cause evidence: root-cause-verification.md, 4-source corroboration; re-observed RED in tdd-red-result.json.
7. Fresh municipalities used = 0 (hard gate).
8. Historical write guard enabled? YES (TASK-LOCK allowed_write_paths + SHA snapshot before any edit).
9. Historical files written during task? NO. V2.4 lives entirely in new-lineage files (roots_v24.py, cli_v24.py, tests_v24.py) plus this evaluation directory.
10. Historical SHA integrity: 13/13 snapshot module SHAs byte-match disk; additionally all 19 pins in frozen V2.3 candidate-runtime-v2-3/hashes.txt byte-match disk (zero drift). One 63-char transcription typo in the snapshot's sitemap_fetch.py entry was corrected to the authoritative frozen pin; disk matched the authoritative pin before and after.
11. Protocol SHA before: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca (protocol document data/local-service-discovery-protocol-v1.json; verified at runtime by ProtocolLoader).
12. Protocol SHA after: identical, unchanged.
13. Protocol changes: NONE.
14. TDD regression test written before fix? DEVIATION, disclosed: tests and fix landed in the same patch; RED was then re-observed by temporarily removing roots_v24.py (tdd-red-result.json).
15. RED observed? YES (re-observed; assertion-level RED against the historical resolver also recorded).
16. RED failure reason: ModuleNotFoundError with roots_v24.py removed; the forbidden-root assertion (no .bedinnsats.no URL for any input) fails against the historical resolver.
17. Production fix location: runtime/discovery_v2/roots_v24.py (canonical_roots_v24), used via cli_v24.py; frozen V2.3 SiteDirectProviderV23 reused unchanged.
18. Historical roots.py modified? NO (SHA e2ee31ee...abdf0bf unchanged, byte-verified).
19. Generalized fix? YES: deterministic suffix rewrite for platform roots; no case IDs, no gold lookup, no injected URLs.
20. Municipality-specific branching? NO (hygiene greps in test-report.md).
21. V2.4 root tests: 4/4 OK.
22. V1 tests: 49/49 OK.
23. V2 tests: 27/27 OK.
24. V2.1 tests: 19/19 OK.
25. V2.2 tests: 20/20 OK.
26. V2.3 tests: 15/15 OK.
27. Total tests: 134/134 OK (no existing test modified or deleted).
28. Raellingen targeted queries: 9.
29. Raellingen successes: 9/9, all gold URLs on ralingen.bedreinnsats.no, 0 external calls, 0 runtime errors.
30. Benchmark attempted: 117.
31. Benchmark successes: 117/117.
32. Gold-domain recovery: 117/117 (100%); gold-URL-exact 18/117 (15.38%) - unchanged semantics vs V2.3 scoring.
33. Runtime/provider failures: 0; bot blocks 0; external_search_calls 0.
34. Replay: 22/22 MATCH.
35. Critical false-no-route: 0.
36. Unsupported FULLY_VERIFIED: 0.
37. Access targets: 9; matches 7/9.
38. Access safety regressions: 0 (existence_safety_regressions = 0).
39. Source-drift cases: 2, the exact documented V2.3 source-drift pair (Alta T2 downgrade FV->EXISTENCE_ONLY; Hasvik upgrade EXISTENCE_ONLY->FV). No method-drift or self-referral changes beyond those already recorded for the frozen fixture.
40. Live burned N: 13.
41. Live complete: 13/13 COMPLETE, 0 runtime failures, 0 bot blocks, 0 render fallbacks.
42. Raellingen live complete? YES (COMPLETE, gold domain, provenance true).
43. Provenance completeness: complete; every route's provenance resolves to the original public URL via the frozen fetch chain.
44. External search calls: 0 (benchmark, live, and 260-step network audit across 19 municipal/registry/helsenorge hosts).
45. External credential required? NO.
46. Hidden gold URL lookup? NO (deterministic root rule only; gold URLs used solely for after-the-run scoring).
47. Security: PASS (SSRF re-check 10/10 blocked, 4/4 canonical URLs pass; credential scrub values_read=false/values_persisted=false in all five official artifacts; render bounds frozen, render_fallback_events=0 in this run; see security-report.md).
48. Median pages (result_count): 3.
49. Max pages: 20.
50. Median runtime: per-row latency field median 0 ms (below runner resolution); max row latency 203,132 ms on one row. Diagnostic only; no tuning performed. Sitemap steps: 36 of 189 attempt steps.
51. Provider config SHA: 6b7f35fc805a92ab28c472dbbfda6dd9b3b92e1d0ce7e9a33c76edfedd706b92.
52. Candidate frozen? YES: LOCAL_DISCOVERY_RUNTIME_V2_4_CANDIDATE_FROZEN.
53. Candidate manifest SHA: 6f7e7ab3fe5f1576a5ca03f9509aa5fd06928b607cebc462702ca1e3ec393a2d.
54. Historical write incident this task? historical_write_incident_this_task = false.
55. Gates passed: root-cause reproduction; Raellingen 9/9; benchmark 117/117; replay 22/22; access 7/9 with 0 existence-safety regressions; live 13/13; historical integrity (13/13 + 19/19 pins); security; hygiene; protocol freeze; total tests 134/134.
56. Gates failed: NONE. (Access carries the 2 documented source-drift cells; they are fixture-drift observations, not safety failures.)
57. STATUS: LOCAL_DISCOVERY_RUNTIME_V2_4_READY_FOR_FRESH_EVAL.
58. Is fresh V2.4 holdout justified? YES - all hard gates are directly proven (contract section 29), so no extra certification task is needed; but fresh evaluation is FORBIDDEN in this task (section 30) and must be a separate bounded task.
59. Remaining limitations: (a) site-direct-benchmark.json carries the inherited task_id "NAV-EXPLORE-LOCAL-DISCOVERY-SITE-DIRECT-ONLY-V2_3" from the frozen runner - cosmetic only, metrics are V2.4's fresh run; (b) the 2 documented source-drift cells; (c) TDD sequence deviation (tests+fix same patch, RED re-observed); (d) DNS-rebinding hardening remains out of scope as frozen in V2.3; (e) per-row latency field granularity.
60. Recommended next bounded stage: fresh V2.4 holdout evaluation in a separate task, frozen Protocol V1 unchanged, no external search, candidate-runtime-v2-4 as the pinned entry point.

## Root-resolution provenance (section 22)

canonical platform root = canonical_roots_v24(municipality): the frozen V2.3 resolver runs unchanged; if its resolved host ends with .bedinnsats.no and the slug part is not "kommune", the host is rewritten to .bedreinnsats.no (platform roots only). Deterministic, case-ID-free, no service-page gold lookup, no auditor-injected URL. kommune.no candidates pass through byte-identically.

