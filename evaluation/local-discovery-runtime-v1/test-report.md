# Test Report - Local Discovery Runtime Prototype V1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-PROTOTYPE-V1
Date: 2026-09-09
Runner: stdlib `python3 -m unittest runtime.discovery.tests` (no pytest in environment; Python 3.14.6)

## Summary

- Total tests: 49, all passing.
- New tests this task: 5 generalized-marker tests + 2 schema-validation tests = 7 added (42 pre-existing from earlier implementation sessions in this task family).

## Test Coverage by Area

| Area | Tests | Notes |
|---|---|---|
| Protocol loading | 4 | SHA verification, mismatch detection, missing file fail-closed |
| Planner | 2 | All levels present; frozen query templates used |
| URL security | 6 | file/ftp/localhost/private IP blocked; official-domain classification |
| Providers | 3 | Replay fetch success/missing; SPA shell detection |
| Link explorer | 2 | Official-domain link filter; max depth |
| Stop states | 2 | Short-circuit on ACCESS_VERIFIED; protocol exhaustion |
| Extraction markers | 5 | Contact, form, referral, drop-in, age |
| Self-referral doctrine | 3 | Phone alone != YES; contact invitation = CONDITIONAL; form = YES |
| Intermunicipal guard | 1 | No INTERMUNICIPAL_GATEWAY without evidence |
| Route states | 4 | FULLY_VERIFIED / ACCESS_PARTIAL / EXISTENCE_ONLY / UNVERIFIED |
| Provenance | 2 | Edge trace, edges first-class |
| Serialization | 1 | Sorted, byte-stable |
| Determinism | 1 | 3 identical replay runs |
| E2E replay | 2 | Raelingen EXISTENCE_ONLY; fetch failure -> DISCOVERY_INCOMPLETE |
| False-no-match invariant | 1 | Uncertainty wording never claims "service does not exist" |
| Historical integrity | 2 | Frozen files exist + protocol SHA OK; id_guard 0 runtime hits |
| Generalized markers (new) | 5 | Nynorsk negated referral; "bruk skjema"; service-connected email; capacity closure -> NO; system-targeted -> NO |
| Schema validation (new) | 2 | Valid result passes; invalid route_state rejected |

## Key Behavioral Assertions

- A bare phone number never yields self_referral YES (ACCESS-E3).
- Capacity-closed or system-targeted services classify self_referral NO even when contact info exists.
- Runtime failures produce DISCOVERY_INCOMPLETE, never a user-facing "no service exists".
- Determinism: 3 runs byte-identical after `started_at` normalization (see determinism-check.json, all_deterministic: true).

## Replay Matrix

22 cells (11 municipalities x 2 scenarios): 21/22 exact route match against frozen predictions. Single mismatch (Askoy D) classified FIXTURE_INCOMPLETE; fixture lacks the separate adult-service contact page. See replay-results.json.

## Access Regression (real replay with fixtures)

T1-T9 historical targets: 5/9 exact route match on replay; 4 mismatches all FIXTURE_INCOMPLETE (evidence sentences absent from fixture pages). Doctrine-level consistency 9/9. See access-regression-results.json.

