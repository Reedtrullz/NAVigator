# TEST REPORT - DISCOVERY RUNTIME V2

Date: 2026-09-09. Runner: stdlib unittest (no pytest).

## Existing V1 suite

49/49 PASS (python3 -m unittest discover -s runtime/discovery -p tests.py).
Unchanged; no tests deleted, skipped, or weakened.

## New V2 suite (runtime/discovery_v2/tests.py)

27/27 PASS (python3 -m unittest runtime.discovery_v2.tests).

Coverage map to task requirements:

| Requirement | Tests |
|---|---|
| Provider contract / canonical statuses | test_canonical_statuses_complete, ProviderResponse usage across suite |
| BOT_BLOCKED distinct from NO_RESULTS | test_403_is_bot_blocked, test_anomaly_page_is_bot_blocked_not_no_results (DDG 202 anomaly shape), test_bot_blocked_root_is_not_no_results |
| RATE_LIMITED classification + budget | test_429_is_rate_limited, test_budget_exhaustion_is_rate_limited |
| TIMEOUT / malformed backend | test_timeout_classified, test_backend_exception_fail_closed |
| Provider health model | TestProviderHealth (untested ready, blocked unhealthy, majority-success healthy) |
| Composite fallback, no silent switch | test_no_silent_fallback_logged, test_all_failures_preserved |
| Site-direct path (nav + sitemap + Stage A roots) | test_nav_link_discovery, test_sitemap_fallback, test_known_roots_stage_a |
| Failure simulation -> no false NO_LOCAL_MATCH | test_provider_failure_is_not_no_local_match (+ composite tests) |
| Provenance invariant (no unsupported FULLY_VERIFIED) | test_unsupported_fully_verified_impossible, test_provenance_edges_present |
| Frozen protocol compliance | test_protocol_unchanged (SHA), test_no_municipality_names_in_v2_code (id guard) |
| End-to-end semantics unchanged | test_end_to_end_service_found (ROUTE_FULLY_VERIFIED / ACCESS_VERIFIED via frozen V1 classifier/evaluator) |

## Replay regression

replay-regression.json: 22 cells rerun from frozen V1 fixtures.
21/22 expected-route matches (the single mismatch is the historical Askoy
FIXTURE_INCOMPLETE cell, preserved unchanged with its historical
classification). 0 doctrine regressions, 0 critical false-no-route,
0 unsupported FULLY_VERIFIED.

## Determinism

determinism-check.json: two serialized replay runs byte-identical
(route_state, terminal_state, execution_status, services, candidates,
provider_chain); only the wall-clock executed_at field is excluded.

## N/A tests

None removed. V1 live-DDG behavior is intentionally not exercised in tests
(external backend verified bot-blocked; covered by V2 BOT_BLOCKED fixtures).
