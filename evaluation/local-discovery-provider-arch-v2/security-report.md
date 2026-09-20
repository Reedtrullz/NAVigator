# SECURITY REPORT - DISCOVERY RUNTIME V2

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2. Date: 2026-09-09.

## Scope

New code: runtime/discovery_v2/ (providers, brave adapter, sitemap fetch,
orchestrator, cli, tests). Reused unchanged from V1: security.py, engine.py,
classification.py, protocol.py, serialize.py, HttpFetchProvider.

## SSRF / URL validation

PASS. Every URL entering any fetch path passes runtime.discovery.security.validate_url:
schemes limited to http/https, localhost and private/loopback/link-local IP
literal ranges blocked, max URL length 2048. Verified by usage scan: 4
validate_url call sites in providers.py (candidate filter, nav links,
sitemap URLs, per-municipality root get).

## Untrusted provider input

PASS. External search results are treated as untrusted discovery hints:
- parsed results are URL strings only; no HTML/JS from results is executed
- every candidate URL is re-validated and filtered by _official() before fetch
- snippets are not used as evidence; final evidence requires a fetched page
  with content hash (provenance invariant, tested in test_unsupported_fully_verified_impossible)

## Fetch bounds

PASS.
- HttpFetchProvider (V1, reused): 15 s timeout, 2 MiB cap, SPA-shell detection
- sitemap_fetch.bounded_fetch: 15 s timeout, 2 MiB cap, single attempt
- SiteDirectProvider URL budget: max 8 URLs per municipality run; budget
  exhaustion returns RATE_LIMITED (fail closed, never fabricated results)

## Rate limiting / no retry storms

PASS. External fallback: max 3 queries per run, minimum 10 s interval
(live burned test used 2 / 5 s), single attempt per query, budget exhaustion
-> RATE_LIMITED. No automatic retries anywhere in V2.

## Bot evasion

PASS (none present). No captcha bypass, no stealth browser, no identity or
proxy rotation, no fingerprint spoofing. Standard static user agent string
only. Verified by code scan of runtime/discovery_v2/.

## Redirect handling

PASS. curl -L with effective-URL capture (V1 HttpFetchProvider reused);
final_url preserved in FetchResult. No fetch path bypasses validate_url.

## Subprocess surface

PASS. curl-only subprocess calls with fixed argument vectors (no shell=True,
no string interpolation into shell). URLs enter argv positionally.

## Test evidence

- V2 suite: 27/27 pass (includes SSRF-adjacent: private root rejected,
  file:// root rejected via validate_url)
- V1 suite: 49/49 pass (unchanged security tests)
- Live burned run: 0 bot blocks, 0 unexpected fetch failures, 13/13 executed
