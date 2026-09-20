# V2.3 Site-Direct-Only - NAV-EXPLORE-LOCAL-DISCOVERY-SITE-DIRECT-ONLY-V2_3

Terminal status: LOCAL_DISCOVERY_RUNTIME_V2_3_READY_FOR_FRESH_EVAL
(TASK-LOCK CLOSED_TERMINAL 2026-09-09).

V2.3 removes the external search dependency honestly: discovery is
site-direct only (canonical kommune.no root patterns -> keyword-gated
navigation -> sitemap, with bounded headless-Chrome render fallback). The
frozen SiteDirectProvider is untouched; the URL-budget raise to 16 lives in
the new-lineage subclass SiteDirectProviderV23 (cli_v23.py).

Key artifacts:

- site-direct-benchmark.json - official burned benchmark, 117/117
  executed, 108/117 gold-domain, 0 bot-blocks (9 failures = 9 Raelingen
  queries; external CMS migration, documented).
- replay-regression.json - 22/22 route matches on frozen V1 fixtures.
- access-regression.json - 9 live targets, 0 existence-safety regressions;
  2 route mismatches verified as external content drift.
- live-burned-results.json - 12/13 COMPLETE, runtime_failures=0.
- network-call-audit.json - external_search_calls=0, 260 steps logged.
- candidate-runtime-v2-3/ - frozen candidate (manifest + hashes).
- final-report.md - 53-point sluttrapport.

Historical integrity: HISTORICAL_FILES_MODIFIED=0 after in-task remediation
(providers.py restored byte-identical to the V2.1 snapshot; see
implementation-report.md). No fresh municipalities, no protocol change, no
secrets in artifacts.
