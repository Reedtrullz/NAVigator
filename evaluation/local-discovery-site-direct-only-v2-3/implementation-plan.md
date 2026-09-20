# Implementation Plan — V2.3 Site-Direct-Only (frozen design)

Status: design frozen 2026-09-09 before any code. Task sections 5, 11, 12,
19, 20 and 26 map onto the items below.

## New files only (HISTORICAL_FILES_MODIFIED = 0)

- runtime/discovery_v2/render.py — RenderFetchFn adapter. Wraps any
  (status_code, body) fetch_fn: when the underlying fetch returns an SPA
  shell (200, ""), it renders the same URL once via headless Chrome
  (--headless=new --dump-dom, bounded timeout, bounded DOM size) and returns
  the rendered body in the same contract. Also exposed as an HttpFetchProvider
  subclass (RenderAwareFetchProvider) so the orchestrator-level
  render_required outcome is converted the same way. Renders only after
  validate_url passes; render failure maps to (0, "") / failed fetch, never
  to content-free success.
- runtime/discovery_v2/tests_v23.py — tests for task section 12 items A-H
  plus root-rule and no-external-calls invariants.
- runtime/discovery_v2/cli_v23.py — V2.3 entrypoint: site_direct only, no
  external providers constructed at all (not merely disabled).
- evaluation/local-discovery-site-direct-only-v2-3/run_official.py — official
  runners: 117-query site-direct benchmark, 13-municipality live burned,
  22-cell replay, 9 access targets, with network instrumentation.

## Frozen design decisions

1. Root rule (task section 20, generalizable, no gold):
   candidates = [https://www.<slug>.kommune.no/, https://<slug>.kommune.no/].
   Optionally verified against Brreg Enhetsregisteret (official Norwegian
   registry; Raelingen homepage listed as www.ralingen.kommune.no/). The
   registry is a canonical identity source, not a service-URL lookup. The
   runtime root rule itself stays pattern-based; Brreg is documented as the
   registry evidence for the root pattern, and no municipality->service URL
   table exists anywhere in V2.3.
2. Render path: Chrome headless, single attempt per URL, ~45 s cap,
   user-data-dir in a fresh temp dir per process, --disable-gpu
   --no-first-run --virtual-time-budget=12000, DOM output capped at 2 MiB.
   No Playwright dependency (module not installed); Chrome binary already
   present and verified.
3. Provider chain: SiteDirectProvider only. No Brave/Tavily provider is
   constructed in V2.3 paths. Provider abstraction (ExternalSearchProvider,
   CompositeDiscoveryProvider) is preserved untouched for historical use.
4. Credentials absent test: V2.3 official runs execute with
   TAVILY_API_KEY/Brave keys unset in the runner environment (os.environ
   scrubbed before provider construction); the suite asserts no code path
   reads them.
5. Raelingen legacy-host deviation: gold host ralingen.bedreinnsats.no is
   legacy; V2.3 reaches www.ralingen.kommune.no service content via render.
   This is reported as a documented equivalent baseline per task section 14,
   never special-cased in code.
6. Failure semantics (task section 22): unchanged frozen behavior — fetch
   failure -> DISCOVERY_INCOMPLETE / provider_failures; no failure maps to a
   service-less "no offer" statement; PUBLIC_DATA_EXHAUSTED only via frozen
   terminal-state logic after site-direct levels were attempted.
7. Network audit: every official runner wraps the fetch_fn to log
   (method, url) tuples; audit proves external web-search hosts = 0.
   Municipality-internal fetches are logged and distinguished by host.
