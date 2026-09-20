# Runtime Failure Policy V2.4 - Frozen Before Sample (Holdout Section 9)

Frozen at: 2026-09-09, BEFORE H2 exposure registry and H4 sample freeze.
Applies to: all 30 holdout cells (15 municipalities x scenarios C/D).
Authority: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-FRESH-HOLDOUT contract sections 9-15.

## One official execution per cell

- Exactly ONE official runtime execution per cell. The frozen V2.4 runtime's own internal retry/fallback behavior (fetch retries=0 per provider config; root-candidate cycling; bounded render fallback) is part of that one execution and is NOT an operator retry.
- NO operator-initiated rerun for any reason: odd-looking results, network flakiness, provider swap, manual URL injection, changed query, adjusted timeout, or changed page budget.

## Preregistered failure states

Every non-COMPLETE cell outcome is classified as exactly one of:

BOT_BLOCKED, DNS_FAILURE, FETCH_FAILURE, TIMEOUT, RENDER_FAILURE, PARSE_FAILURE, SOURCE_UNAVAILABLE, INTERNAL_RUNTIME_ERROR, SECURITY_REJECTION, OTHER_EXECUTION_FAILURE.

Mapping rule: the runtime's own terminal/error state is recorded verbatim; the classification above is derived mechanically from it (e.g. connection refused/DNS resolution errors -> DNS_FAILURE; HTTP non-200 across all root candidates -> SOURCE_UNAVAILABLE; Chrome render path failure with SPA shell -> RENDER_FAILURE; unexpected exception -> INTERNAL_RUNTIME_ERROR).

## Failure semantics

1. A failed cell is NEVER converted to NO_RESULT, NO_LOCAL_MATCH, ROUTE_UNVERIFIED-as-completed, or "no municipal offer". The canonical state is DISCOVERY_INCOMPLETE (or the frozen V2.4 equivalent execution state).
2. Every failure counts against COMPLETE_DISCOVERY (>= 29/30 gate) and stays in the official denominator of 30. No post-hoc removal.
3. NO post-hoc availability adjudication: if a public source is unavailable during the official run, that is the genuine end-to-end holdout result. The audit may explain the cause afterwards; the denominator remains 30.
4. DISCOVERY_INCOMPLETE is not false-no-route: it counts against execution completeness only (contract section 48).

## Security

Security rejections (SSRF/private-IP/scheme blocks) are recorded as SECURITY_REJECTION and count as execution failure. Security is never weakened to improve holdout scores.

## External search

External search calls must remain 0 for the whole task. Any external search call -> V2_4_FRESH_HOLDOUT_INVALID.

