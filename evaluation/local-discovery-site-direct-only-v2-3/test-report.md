# Test Report - V2.3 Site-Direct-Only

All suites run 2026-09-09 with PYTHONPATH=$PWD, repo root, python3 -m.

| Suite | Tests | Result |
|---|---|---|
| runtime.discovery_v2.tests_v23 | 15 | OK |
| runtime.discovery_v2.tests (V2) | 27 | OK |
| runtime.discovery_v2.tests_v21 | 19 | OK |
| runtime.discovery_v2.tests_v22 | 20 | OK |
| runtime.discovery.tests (V1) | 49 | OK |

Total: 130 tests, 0 failures. Suites re-run after the historical-file remediation (providers.py restore + SiteDirectProviderV23 subclass) with identical results.
