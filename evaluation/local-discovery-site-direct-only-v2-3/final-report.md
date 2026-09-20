# Final Report - V2.3 Site-Direct-Only

Task: NAV-EXPLORE-LOCAL-DISCOVERY-SITE-DIRECT-ONLY-V2_3, 2026-09-09.

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-SITE-DIRECT-ONLY-V2_3
2. Prior terminal status: NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES
3. Fresh municipalities used: 0
4. Protocol SHA before: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca
5. Protocol SHA after: same (byte-verified)
6. Protocol changes: 0
7. External search optional under Protocol V1: yes; protocol gates are discovery-method agnostic (protocol-compatibility.md)
8. Protocol compatibility verdict: PASS
9. Historical candidate integrity: V2.1 snapshot 7/7 files byte-match; candidate-runtime-v2 manifest 21/21 files byte-match; V2.2 artifacts untouched. One transient violation (providers.py max_urls edit) was remediated in-task (implementation-report.md).
10. Baseline benchmark N: 117 burned queries (frozen corpus)
11. Site-direct baseline recovery: 108/117 SUCCESS (92.31 percent), gold-domain 108/117; 9 failures = 9 Raelingen queries (external site failure)
12. V2.3 architecture: site-direct only (root patterns -> nav keywords -> sitemap), bounded headless-Chrome render fallback, new-lineage SiteDirectProviderV23 (URL budget 16), frozen V1 semantics untouched
13. External search runtime dependency: none
14. External credentials required: no
15. External search calls during official regression: 0 (audit: 260 steps, 19 municipal/registry hosts)
16. Municipality-root resolution method: generalizable pattern rule (www.slug.kommune.no, bare domain, ae-compressed variant, slug.bedinnsats.no last), corroborated by Brreg registry as identity source; no lookup table
17. Hidden gold URL lookup present: no
18. Navigation implemented: yes (frozen NAV_KEYWORDS gate)
19. Sitemap implemented: yes (protocol level 3)
20. Render fallback implemented: yes, bounded (max 4 renders per municipality, 45 s, process-group kill)
21. Failure semantics: honest (NO_RESULTS / RATE_LIMITED / PROVIDER_UNAVAILABLE propagate; no fabricated success)
22. New V2.3 tests: 15/15 pass
23. V1 tests: 49/49 pass
24. V2 tests: 27/27 pass
25. V2.1 tests: 19/19 pass (V2.2 suite: 20/20)
26. Site-direct benchmark execution: 117/117 executed, 0 runtime failures
27. Site-direct target recovery: gold-domain 108/117 = 92.31 percent
28. Replay cells: 22
29. Replay regressions: 0 (22/22 MATCH)
30. Critical false-no-route: 0
31. Unsupported FULLY_VERIFIED: 0
32. Access targets: 9
33. Access regressions: 0 existence-safety regressions; 2 route mismatches verified as external content drift (T2 Alta down, T9 Hasvik up), documented in regression-report.md
34. Live burned municipalities: 13 attempted
35. Complete discovery: 12/13 (gate at least 12)
36. External search calls: 0
37. Provenance completeness: 12/13 (Raelingen honest failure)
38. Render fallback events: 0 (bounded path armed, no SPA needed)
39. Sitemap events: 27 OK / 18 unavailable across 117 benchmark queries
40. Median pages fetched (live): 3
41. Max pages fetched (live): 10
42. Median runtime (live): 1.86 s per municipality (max 520 s = Raelingen dead-shell renders)
43. Security: PASS (credential scrub presence-only; SSRF rules; 0 external calls; no secrets in artifacts)
44. Provider config SHA: frozen in candidate-runtime-v2-3/manifest.json and hashes.txt
45. Candidate V2.3 frozen: yes
46. Candidate manifest SHA: registered in candidate-runtime-v2-3/manifest.json
47. Historical files modified: 0 after in-task remediation (providers.py restored byte-identical to V2.1 snapshot; budget raise moved to the V2.3 subclass)
48. Gates passed: protocol compatibility, historical integrity, no fresh data, burned benchmark, replay 22/22, access 0 safety regressions, live 12/13 COMPLETE, security, no phantom fallback, 130 tests
49. Gates failed: none
50. STATUS: LOCAL_DISCOVERY_RUNTIME_V2_3_READY_FOR_FRESH_EVAL
51. Is fresh V2.3 eval justified: yes, but it is a separate task; STOP here per contract
52. Remaining limitations: ralingen.kommune.no serves a JS shell no client can crawl (Googlebot sees the same shell); the bedreinnsats platform has intermittent DNS. Both are external-site conditions, not runtime defects. Access route-state drift on live pages will recur by design as municipalities edit content.
53. Recommended next bounded stage: separate V2.3 fresh holdout task (new municipalities), no protocol change, no external backends.
