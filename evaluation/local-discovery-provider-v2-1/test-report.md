# TEST REPORT V2.1

| Suite | Result | Note |
|---|---|---|
| V2.1 regression (runtime/discovery_v2/tests_v21.py) | 19/19 PASS | Red before fix: 9 failures + 4 errors (cases C/D/E/F/H, FIXTURE-001, T1-T5) |
| V2 baseline (runtime/discovery_v2/tests.py) | 27/27 PASS | Untouched file; legacy (status, body) contract intact |
| V1 baseline (runtime/discovery/tests.py) | 49/49 PASS | Includes SSRF/private-IP/scheme/redirect security tests |

Coverage of frozen test plan (`adapter-correctness-tests-v2-1.json`):

- Cases A-H: all implemented and green (A SUCCESS, B NO_RESULTS, C 429->RATE_LIMITED incl. archived challenge body, D 403->BOT_BLOCKED, E transport failure->PROVIDER_UNAVAILABLE, F challenge after 5000 chars->BOT_BLOCKED, G long plain HTML->NO_RESULTS, H malformed->INVALID_RESPONSE).
- FIXTURE-001: real archived 429 challenge (73,731 bytes, marker at 17276, SHA-verified) classifies RATE_LIMITED via classify and via provider discover; false NO_RESULTS = 0.
- Transport contract T1-T5: dict/tuple dual support, attempts metadata, structural -w capture (exit0+429 never HTTP 200), exit 28->TIMEOUT, 2 MiB truncation + scan cap.
- Invariants INV1/INV2: failure statuses never fold to NO_RESULTS; all-provider-failure composite run yields DISCOVERY_INCOMPLETE with per-provider failure classes preserved.
