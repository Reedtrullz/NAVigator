# FINAL REPORT - NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2

Date: 2026-09-09. All work on burned data. No fresh municipalities, no Protocol V1 changes, no deploy.

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2.
2. Prior status: RUNTIME_FRESH_EVAL_BLOCKED_BY_PROVIDER (immutable historical artifact, not rewritten).
3. Why fresh eval was blocked: frozen DDG HTML external search was a single point of failure - cumulative search success 1/10, last 5/5 responses verified anomaly/bot-block pages; direct fetch 5/5 healthy.
4. Fresh municipalities used: 0.
5. Protocol SHA before: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca.
6. Protocol SHA after: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca (unchanged).
7. Protocol modifications: none.
8. V1 candidate integrity: manifest SHA 573f77348a75a750542e05a5f5c18a2b033643773b24df73a2fa827716f15af7 unchanged; all 14 frozen files re-hashed post-task, 14/14 match.
9. Provider compatibility audit: protocol-provider-compatibility.md - direct landing, navigation traversal, sitemap discovery, and external web search are allowed/implicitly compatible; internal search and rendered fallback are not specified by Protocol V1 (internal search not implemented; render behavior kept detect-and-log).
10. Site-direct compatible with V1: yes, first-class (roots, NAVIGATION_LINK, sitemap.xml within existing discovery-level semantics).
11. External search compatible: yes, as discovery-level E fallback with budget; not doctrine.
12. Protocol gap found: none; no HARD PROTOCOL GATE triggered.
13. Provider architecture: SiteDirectProvider + ExternalSearchProvider (replaceable backend) + CompositeDiscoveryProvider with deterministic logged fallback (site-direct first, brave_html budgeted fallback).
14. Provider contract: ProviderResponse with canonical statuses SUCCESS / NO_RESULTS / RATE_LIMITED / BOT_BLOCKED / AUTH_REQUIRED / PROVIDER_UNAVAILABLE / TIMEOUT / INVALID_RESPONSE / INTERNAL_ERROR; NO_RESULTS and BOT_BLOCKED never conflated; ProviderHealth exposes healthy/failure_class/attempted vs successful queries.
15. Provider candidates evaluated: site-direct only; ddg_html, ddg_lite, bing_html, mojeek, brave_html external backends (external-backend-probe.json, provider-comparison.json).
16. Benchmark municipalities: 13 burned.
17. Benchmark queries: 117 frozen (benchmark-corpus.json, corpus SHA 40b0b9c3b0b915a71b36866b182c04ef00b4774569bfadea2414c61e9bee29f2).
18. Query execution by provider: site-direct 117/117 SUCCESS (1.0). External: ddg/mojeek BOT_BLOCKED, bing NO_RESULTS, brave 3/6 at probe volume and 429 RATE_LIMITED at 117-query volume (documented, no retry storm).
19. Relevant-target recall: gold-domain 1.000 (117/117); gold-URL-exact 0.154 (18/117) reported separately with definition.
20. Official-domain precision: 0.9846 mean.
21. Bot-block rate: 0.0 on site-direct benchmark; external backends verified bot-blocked (documented as provider health, not folded into NO_RESULTS).
22. Provider-error rate: 0.0 (site-direct).
23. Site-direct recovery: SITE_DIRECT_RECOVERY_RATE = 117/117 benchmark targets without external search.
24. External fallback incremental recovery: 0 in benchmark and live run (fallback never triggered); retained as budgeted capability per architecture implication note.
25. Selected architecture: composite site-direct-first with budgeted external fallback (provider-config-v2.json).
26. Selected external backend: brave_html, fallback only, budget 3 queries/run, 10s min interval (frozen config).
27. Authentication required: no.
28. Provider fallback order: site_direct -> brave_html_external_fallback (deterministic, logged).
29. Retry policy: single attempt per provider per query; no automatic retries.
30. BOT_BLOCKED handling: canonical failure class, regression fixtures; never NO_RESULTS, ROUTE_UNverified, or NO_LOCAL_MATCH; triggers only preregistered fallback; preserved in observability.
31. NO_RESULTS handling: genuine empty parse only (HTTP 200, no bot markers).
32. RATE_LIMITED handling: canonical; includes external budget exhaustion and 429.
33. Provider-unavailable handling: canonical (e.g. HTTP 404 root classified PROVIDER_UNAVAILABLE, not NO_RESULTS).
34. False NO_LOCAL_MATCH under simulated failures: 0 (provider-failure-tests.json: BOT_BLOCKED, RATE_LIMITED, TIMEOUT, NO_RESULTS, malformed response, provider unavailable).
35. Provenance invariant: snippets are discovery evidence only; final evidence requires fetched page + content hash; tested (test_unsupported_fully_verified_impossible) - unsupported FULLY_VERIFIED = 0.
36. V2 architecture: runtime/discovery_v2/ (providers.py, brave.py, sitemap_fetch.py, orchestrator.py, cli.py, tests.py); reuses frozen V1 classification/engine/protocol/security/serialize components unchanged.
37. LLM in control flow: no.
38. Existing tests result: V1 suite 49/49 PASS (unchanged).
39. New tests: 27/27 PASS (V2 suite; stdlib unittest).
40. Replay regression: 22 cells, 21/22 route matches; single mismatch is the historical Askoy FIXTURE_INCOMPLETE cell preserved unchanged; 0 doctrine regressions.
41. Critical route regressions: 0.
42. Unsupported FULLY_VERIFIED: 0.
43. Live burned municipalities: 13.
44. Live execution success: 13/13 executed without error, all site-direct (>= 11/12 gate met).
45. Live bot blocks: 0.
46. Render fallbacks: 0 (0 render-required municipalities).
47. Security tests: PASS (security-report.md: SSRF guard on all 4 fetch entry points, bounded fetch 2 MiB/15s, curl argv-only, no evasion, budget exhaustion fail-closed).
48. Provider config SHA: d6890b5f97c8dd12eb915114c571a8ba930b75aa00fdd0c5a373965c5423cbc3.
49. Candidate V2 frozen: yes - candidate-runtime-v2/ with manifest.json, hashes.txt, README.md; status LOCAL_DISCOVERY_RUNTIME_V2_CANDIDATE_FROZEN.
50. Candidate V2 manifest SHA: 74329662e2df1e8bffb69165b3c39820af6313e7a3096fe6754d78f80977a678 (computed from frozen manifest.json; 21 files hashed).
51. Historical files modified: 0.
52. Gates passed: protocol unchanged; V1 candidate unchanged; fresh municipalities 0; benchmark execution 1.0 (>= 0.95); relevant-target recall 1.0 gold-domain (>= 0.90); systematic bot block 0; false NO_LOCAL_MATCH 0; unsupported authoritative evidence 0; burned live execution 13/13 (>= 11/12); critical route regressions 0; unsupported FULLY_VERIFIED 0; security tests PASS; historical modifications 0; determinism byte-stable.
53. Gates failed: none.
54. STATUS: LOCAL_DISCOVERY_PROVIDER_V2_READY_FOR_FRESH_EVAL.
55. Is a new fresh runtime eval justified: yes - as a separate task with a new task ID and new fresh evaluation artifacts; the blocked V1 fresh-eval task is not reused.
56. Remaining limitations: gold-URL-exact recall 0.154 on benchmark (domain recall 1.0); Raelingen gold target only reachable via sitemap of a retired domain, so exact-URL fragility on retired domains is known; external fallback is unproven at volume (brave 429 at 117-query volume) and must stay budgeted; fresh-generalization evidence remains zero until a fresh eval runs.
57. Recommended next bounded stage: LOCAL-DISCOVERY-RUNTIME-FRESH-EVAL-V2 as a separate task - pick fresh municipalities, freeze evaluation contract, run the frozen V2 candidate, and score with the existing metrics. No new R&D on the runtime before that eval.

STOP. No fresh eval performed in this task. No Protocol V1 changes. No fresh municipalities. No deploy.
