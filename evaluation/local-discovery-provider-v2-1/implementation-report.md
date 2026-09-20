# IMPLEMENTATION REPORT V2.1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-V2_1-ADAPTER-CORRECTNESS

## Root cause (pre-fix)

1. `brave_fetch_fn` returned `(proc.returncode if != 0 else 200, stdout)`: curl exit 0 on an HTTP 429 became HTTP 200, so the response never reached the 429 classification path.
2. `classify_http_response` scanned only `body[:5000]` for bot/challenge markers; the archived Brave challenge has its first marker at position 17276, so challenge pages fell through to `NO_RESULTS`.

## Implementation pass (single bounded pass, as frozen)

`runtime/discovery_v2/brave.py` (rewritten):

- curl `-w` write-out (`%{http_code} %{url_effective} %{num_redirects}`) appended behind a control-character sentinel; body and transport metadata split structurally. Exit code captured separately; HTTP status trusted only when exit == 0; transport failure -> http_status 0.
- curl exit 28 raises `TimeoutError` (provider layer classifies TIMEOUT).
- Body capped at 2 MiB with `body_truncated` flag; returns structured transport dict `{curl_exit, http_status, body, initial_url, final_url, num_redirects, body_truncated}`.

`runtime/discovery_v2/providers.py` (three targeted changes):

- `MAX_SCAN_BYTES = 2 MiB` bound; `classify_http_response` scans the full bounded body (not 5000 chars).
- Frozen classification order: transport failure -> explicit HTTP status (429 RATE_LIMITED, 403 BOT_BLOCKED, 401 AUTH_REQUIRED, 5xx PROVIDER_UNAVAILABLE, other 4xx INVALID_RESPONSE) -> challenge content (bounded scan) -> parsed results SUCCESS -> validity (`_has_html_structure`, MIN_VALID_BODY_BYTES) -> NO_RESULTS last.
- `ExternalSearchProvider.discover` accepts dict transport results (legacy tuples still supported) and attaches transport metadata to `resp.attempts`.

## Bounded bugfix pass

Not needed for runtime code. Test-authoring corrections only (composite last-provider semantics in INV2; T4 kept entirely inside the monkeypatched window after exit 28 became a raised TimeoutError - the previous trailing assertion made a live network call; T5 marker placed fully beyond the 2 MiB scan cap).

## Verification

- V2.1 new suite: 19/19 PASS (was 9 failures + 4 errors red before fix)
- V2 baseline: 27/27 PASS; V1 baseline: 49/49 PASS (both suites untouched)
- E1 re-run on burned data: site-direct 5/5 PASS; Brave 0/5 BOT_BLOCKED (correct classification, backend still not ready)
