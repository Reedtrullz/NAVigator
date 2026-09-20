# Security Report - Local Discovery Runtime Prototype V1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-PROTOTYPE-V1
Date: 2026-09-09

## Posture

- Replay-first runtime; live mode is opt-in and bounded.
- No LLM in control flow. No model calls anywhere in the runtime.
- No municipality names or case IDs in runtime code (id_guard test + grep: 0 hits in non-test runtime modules).
- Frozen protocol SHA verified at load: `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca`.

## SSRF Protection

- `validate_url` blocks: file://, ftp://, localhost, private/link-local/loopback IP ranges, non-HTTP(S) schemes.
- `is_official_domain` gates link extraction: navigation stays within official source types; private/unknown domains are dropped.
- Redirect targets are re-validated: the live search provider's redirect-style result URLs (`uddg=`) failed closed under the validator during smoke testing; nothing was fetched from unvalidated hosts.

## Fetch Bounds

- Per-request timeout: 15 s (curl `--max-time`), subprocess timeout 20 s.
- Response size cap: 2 MiB (`HttpFetchProvider.MAX_SIZE`).
- Crawl bounds: max depth 2, max 20 pages per run.
- User agent identifies as research bot (`NAVExploreDiscovery/1.0`).

## Live Smoke Behavior

- Search layer: all attempted public backends (DuckDuckGo HTML/Lite, Mojeek, searx.be, paulgo.io) returned bot-protection pages or 429. Reported as `SEARCH_PROVIDER_UNAVAILABLE`; no evasion attempted (prohibited by security doctrine).
- Fetch layer: 3/3 known official URLs fetched or correctly classified; SPA shell detected -> `RENDER_REQUIRED` rather than garbage extraction.

## Data Handling

- No credentials, tokens, or personal data are transmitted. Queries contain only municipality name + generic service terms.
- Content hashes retained per fetch for provenance; raw HTML is not persisted by the runtime.

## Known Limitations

- No renderer: JS-only sites cannot be evaluated (documented gap, fail-closed).
- Live search depends on a public backend; production use requires a licensed search API with the same fail-closed validation applied to results.

