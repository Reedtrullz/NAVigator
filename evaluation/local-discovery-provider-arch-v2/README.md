# Local Discovery Provider Architecture V2

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2 (2026-09-09).

Removed the external search engine as a single point of failure without
touching the frozen discovery doctrine. Result: site-direct-first composite
provider architecture with a budgeted, replaceable external fallback.

STATUS: LOCAL_DISCOVERY_PROVIDER_V2_READY_FOR_FRESH_EVAL

Key artifacts:
- TASK-LOCK.json (terminal status recorded)
- benchmark-corpus.json / benchmark-baseline.json (117 queries, 13 burned municipalities)
- provider-comparison.json / external-backend-probe.json (provider R&D evidence)
- provider-failure-tests.json (failure classes never collapse to NO_LOCAL_MATCH)
- live-burned-results.json (13/13 live, site-direct only)
- replay-regression.json (21/22 matches, Askoy FIXTURE_INCOMPLETE preserved)
- provider-config-v2.json (frozen config, hashed)
- candidate-runtime-v2/ (frozen V2 candidate manifest + hashes)
- final-report.md (57-point final report)

Historical integrity: Protocol V1 and candidate V1 unchanged
(HISTORICAL_FILES_MODIFIED = 0). Fresh municipalities used: 0.
Fresh evaluation is a separate, later task.
