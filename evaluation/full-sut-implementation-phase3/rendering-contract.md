# Phase 3 Rendering Contract

All rendering is template-based. Dynamic strings pass through
ascii_text (ae/oe/aa transliteration) before interpolation. Sections
are joined with blank lines. Output is byte-identical for identical
input state.

## Route state wording (epistemic contract)

| Route state | Rendered wording |
|---|---|
| FULLY_VERIFIED | verifisert i oppslaget |
| ACCESS_PARTIAL | finnes og er relevant, men tilgang er ikke verifisert |
| EXISTENCE_ONLY | registrert i oppslaget. Aldersgrense og tilgang er ikke verifisert |
| UNVERIFIED | ikke verifisert (never emitted as a route block) |

FULLY_VERIFIED wording is synthetic-only in the current replay corpus
(no strong_access services in burned data). Component-level test
coverage exists; natural-replay coverage will follow real data.

## Block rendering

- SAFETY_INSTRUCTION (suppressed or ACUTE_RISK_NOW): four frozen acute
  lines (113; 116 123; police 02800 / 112; legevakt 116 117).
- SAFETY_INSTRUCTION (URGENT_NOT_ACUTE): urgency lead line.
- FAILURE_NOTICE terminal: Svaret er ufullstendig fordi et obligatorisk
  trinn feilet (<stage>). Ingen tjeneste anbefales.
- INFO: Nasjonal informasjon: <claim>.
- FAILURE_NOTICE conflict: Kildene sier motstridende ting om <subject>;
  konflikten er ikke lost.
- PRIMARY_ROUTE header: Anbefalt neste steg: then '<name>' er <wording>.
- SECONDARY_ROUTE header: Andre aktuelle tilbud: then '<name>' er
  <wording>.
- PROVENANCE_LIST: Kilde P-Dxxx: <url> (verifisert 2026-09-09) per
  record; Ingen kilde kunne verifiseres for dette svaret. if none.

## Uncertainty wording (fixed precedence from span_refs)

- discovery_incomplete: Lokalt oppslag for minst ett omraade ble ikke
  fullfoert. Dette er ikke det samme som at kommunen ikke har tilbud.
- no_route_found: Fant ingen registrerte kommunale tilbud for denne
  henvendelsen. Det betyr ikke at tilbudet ikke finnes; det kan bety at
  oppslaget ikke dekker kommunen eller at soeket ikke ga treff.
- state_<route_id>: per-route access caveat line.
- top_state_<X>: Ingen del av dette svaret er fullstendig verifisert.

## Negative-existence guard

The finalizer rejects any rendered answer containing 'har ikke tilbud',
'mangler tilbud', or 'finnes ikke' when discovery is incomplete or
no-route was found. This makes NO_ROUTE_FOUND != NO_SERVICE_EXISTS
mechanically enforced, not just a wording convention.
