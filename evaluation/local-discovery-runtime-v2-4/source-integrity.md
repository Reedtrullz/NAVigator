# Gate 0 - Source Integrity (read-only verification)

Generated before any code change. Python 3.14.6.

- py_compile on runtime/discovery_v2/roots.py: PASS
- Import smoke test: PASS; imported module resolves to the repo file
  /Users/reidar/Projectos/NAV Explore/runtime/discovery_v2/roots.py (no shadow copy)
- Historical resolver live output for Raelingen, last candidate root:
  https://ralingen.bedinnsats.no/ (the defect, reproduced without code change)
- C0/control-character scan over all 12 runtime/test modules: 0 findings
- Working-tree diff of immutable paths (runtime/, protocol, V2.3 dir): clean

Baseline suites before any edit (clean processes):

- runtime.discovery.tests (V1): 49/49 OK
- runtime.discovery_v2.tests (V2): 27/27 OK
- runtime.discovery_v2.tests_v21: 19/19 OK
- runtime.discovery_v2.tests_v22: 20/20 OK
- runtime.discovery_v2.tests_v23: 15/15 OK

SHA-256 snapshot (full values in historical-integrity.json):

| File | SHA-256 |
|---|---|
| runtime/discovery_v2/roots.py | e2ee31eece7eeabcdb5886e8436ec26f3a7a6c511120ab156182323cbabdf0bf |
| runtime/discovery_v2/providers.py | 54b38921b02736763d3baef25e7bb860f1bf1b9f8d3b0fb3ac58b0808083806a |
| runtime/discovery_v2/cli_v23.py | b498a0859df1edb99e791a371b6ca9661bbf4b925259b49bd137b9e2718a5fd8 |
| runtime/discovery_v2/render.py | 953a23dbc27e0552e95b50128e8ab4d3308a8f9b73295112d043a87ac5b1b36c |
| runtime/discovery_v2/orchestrator.py | 1c9545b16357ab413baf0b36bbcb3617a6a35baa67a81b99a56902208db62b95 |
| runtime/discovery_v2/sitemap_fetch.py | 7e6b677edb43de726f3678d7df2b6cce1d4bf3b38cf34161c9fc14a698f25bc (full SHA in historical-integrity.json) |
| data/local-service-discovery-protocol-v1.json | fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca |
| provider-config-v2-3.json | 51ee5b28f62fea423e0f83bfb28eaa3ebe652ea91aefad7ed2ddbbbe2a714586 |
