# Test Report - Certification Clean Re-Run

Task: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION
Date: 2026-09-09. Clean process, repo root, PYTHONPATH=$PWD, no fixes applied.

| Suite | Tests | Result |
|---|---|---|
| runtime.discovery.tests (V1) | 49 | OK |
| runtime.discovery_v2.tests (V2) | 27 | OK |
| runtime.discovery_v2.tests_v21 | 19 | OK |
| runtime.discovery_v2.tests_v22 | 20 | OK |
| runtime.discovery_v2.tests_v23 | 15 | OK |

Total: 130/130, 0 failures (contract Section 20: expected 130/130).

No implementation fixes were made or needed. The suites were run against
the frozen candidate; no source file changed between the historical V2.3
run and this certification run (verified by candidate manifest SHA and
per-file hashes in candidate-integrity.json).

## Replay certification re-run (Section 19)

Clean-process replay via the frozen runner semantics (output redirected to
this certification directory; no runtime or harness code modified):

- 22/22 route matches, 0 mismatches
- critical_false_no_route = 0
- unsupported_fully_verified = 0

Artifact: replay-certification.json (frozen runner output, renamed from the
runner's default filename to avoid confusion with historical artifacts).

## Security regression (Section 24)

Frozen security suite (part of the 130 tests: tests_v21 SSRF/secret-safety
cases, tests_v23 hygiene and localhost/private-IP blocks) passes unchanged;
no security rule changes were made in this task. Credential scrub ran on
every certification process (presence-only; .env.local never opened).
