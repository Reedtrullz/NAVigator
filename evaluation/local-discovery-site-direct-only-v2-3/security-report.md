# Security Report - V2.3 Site-Direct-Only

## Credential handling

- scrub_credentials() removes every TAVILY/BRAVE environment key before any run; values_read=false and values_persisted=false in all official artifacts (benchmark, live, replay, access, audit).
- .env.local in the repo root (user-provided) was never opened by any V2.3 runner or test. No secret value appears in any artifact, log, or report.
- No Brave/Tavily provider is constructed anywhere on the V2.3 path (external_backends is empty in provider config).

## Network controls

- validate_url SSRF rules applied to every fetched or derived URL; the official audit shows 19 distinct hosts, all municipal or registry.
- external_search_calls = 0 in the official network audit (260 logged steps across benchmark and live).
- Render fallback is bounded: max 4 renders per municipality, 45 s timeout, process-group kill on timeout (render.py fix). DNS-rebinding hardening remains out of scope as frozen in the contract; the localhost/private-IP block is covered by tests_v23.

## Hygiene

- tests_v23.TestCodeHygiene asserts no RC1B/RC2B case IDs and no make_brave_provider/make_tavily_provider references in V2.3 code.
- No secrets, credentials, or tokens in any V2.3 artifact.
