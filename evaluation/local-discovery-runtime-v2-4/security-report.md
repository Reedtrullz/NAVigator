# Security Report - V2.4 Root-Resolution Repair

## Network controls

- validate_url SSRF rules apply to every fetched or derived URL (frozen runtime/discovery/security.py, reused unchanged). Inline re-check for this run: 10/10 blocked (localhost, 127.0.0.1, 10.0.0.1, 192.168.1.1, 172.16.0.1, 169.254.1.1, 0.0.0.0, [::1], file://, ftp://); 4/4 canonical allowed URLs (www.ralingen.kommune.no, ralingen.bedreinnsats.no, helsenorge.no, hadir.no) pass.
- tests_v23 SSRF/localhost coverage remains in effect (TestSecurityBlocklist*); tests_v24 adds only root-resolution assertions, no security relaxation.
- Official network-call audit: external_search_calls = 0; 260 logged steps across 19 distinct hosts, all municipal or registry/helsenorge.
- Render fallback bounded as frozen in V2.3: max 4 renders per municipality, 45 s timeout, process-group kill. In the V2.4 official run render_fallback_events = 0 and render_events_by_municipality is empty for all 117 rows; platform roots responded directly. DNS-rebinding hardening remains out of scope as frozen in the contract; the localhost/private-IP block is covered by tests_v23.

## Credential handling

- scrub_credentials() applied on every official artifact; values_read=false and values_persisted=false verified by grep across benchmark-results.json, replay-results.json, access-regression.json, live-burned-results.json, and network-call-audit.json.
- .env.local in the repo root was never opened by any V2.4 runner or test. No secret value appears in any artifact, log, or report.
- No Brave/Tavily provider is constructed anywhere on the V2.4 path (external_backends empty in provider-config-v2-4.json).

## Hygiene

- tests_v23.TestCodeHygiene asserts no RC1B/RC2B case IDs and no make_brave_provider/make_tavily_provider references in reused V2.3 code; tests_v24 extends the test count with 4 root-resolution cases.
- No secrets, credentials, or tokens in any V2.4 artifact.

