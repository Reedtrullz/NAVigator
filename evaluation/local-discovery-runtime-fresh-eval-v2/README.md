# Local Discovery Runtime Fresh Eval V2

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-FRESH-EVAL-V2 (2026-09-09).

STATUS: RUNTIME_FRESH_EVAL_V2_BLOCKED_BY_PROVIDER

One-shot holdout of the frozen V2 runtime candidate on fresh municipalities.
Blocked at E1 provider readiness (burned data only): site-direct 5/5 PASS,
external fallback adapter 0/5 FAIL (persistent HTTP 429 challenge from the
brave backend, misreported as NO_RESULTS by the frozen adapter). Per the
strict sequence, no fresh sample was created and no fresh municipality was
burned.

Artifacts: TASK-LOCK.json (terminal status), candidate-integrity.json,
provider-readiness.json, eval-provider-config.json, security-observations.json,
historical-integrity.json/.md, final-report.md (79-point template).

Next bounded stage: separate provider R&D task (adapter status-mapping fix +
bot-marker scan), then re-attempt this fresh eval with a new task ID.
