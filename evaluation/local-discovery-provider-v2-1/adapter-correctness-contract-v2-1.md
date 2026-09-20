# ADAPTER CORRECTNESS CONTRACT V2.1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-V2_1-ADAPTER-CORRECTNESS. Frozen before implementation (2026-09-09).

## Layer distinction

1. PROCESS EXECUTION STATUS: curl process exit code. Describes whether curl
   managed to execute the request (transport), never the HTTP result.
2. HTTP RESPONSE STATUS: the actual HTTP status code of the response
   (captured structurally via curl write-out metadata, not parsed from
   human-readable text).
3. RESPONSE CLASSIFICATION: canonical mapping of (transport, HTTP status,
   body content, parsed results) to a provider contract status.
4. PROVIDER SEMANTIC STATUS: the canonical statuses consumed by the runtime
   (SUCCESS / NO_RESULTS / RATE_LIMITED / BOT_BLOCKED / AUTH_REQUIRED /
   PROVIDER_UNAVAILABLE / TIMEOUT / INVALID_RESPONSE / INTERNAL_ERROR).

## Frozen rules

R1. curl exit 0 + HTTP 429 = successful transport + HTTP 429. Never HTTP 200.
R2. Real HTTP status is captured with curl -w write-out (%{http_code},
    %{url_effective}, %{num_redirects}); process exit code is captured
    separately. Transport failure is represented as http_status = 0.
R3. Redirect metadata: initial URL, final URL, final HTTP status, and
    redirect count are attached to the provider response (observability),
    inside existing URL/security guards. Guards are not weakened.
R4. Classification order (frozen):
    A. transport/runtime failure (curl exit != 0 with no HTTP status, or
       fetch exception) -> PROVIDER_UNAVAILABLE / TIMEOUT / INTERNAL_ERROR
    B. explicit HTTP status: 429 -> RATE_LIMITED; 403 -> BOT_BLOCKED;
       401 -> AUTH_REQUIRED; 5xx -> PROVIDER_UNAVAILABLE; other 4xx ->
       INVALID_RESPONSE
    C. bot/challenge content classification (applies to 2xx bodies):
       BOT_MARKERS scan over the full body within the existing bounded
       response-size policy (2 MiB cap; larger bodies are truncated before
       scan) -> BOT_BLOCKED
    D. parsed external results -> SUCCESS
    E. validity: body below minimum valid size, or without basic HTML
       document structure, -> INVALID_RESPONSE
    F. NO_RESULTS last: 2xx, no challenge markers, no parsed results,
       valid HTML body -> NO_RESULTS
    NO_RESULTS must never be produced merely because a parser found no
    links on a challenge page.
R5. HTTP 429 mapping: RATE_LIMITED (consistent with the existing frozen
    contract test test_429_is_rate_limited). Challenge markers in a 429 body
    are recorded as evidence, but the status stays RATE_LIMITED; 403 carries
    BOT_BLOCKED. Documented here as the frozen mapping.
R6. BOT_MARKERS are the existing general markers, unchanged. No Brave-case
    specific literals are added.
R7. Response-size protection is preserved: external fetch bodies are capped
    at 2 MiB (truncation recorded in transport metadata) before any scan.
    Scanning more body never disables the cap.
R8. The fix is generic: no readiness query IDs, no municipality names, no
    archived filenames, no exact challenge length, no exact five failed
    queries in runtime logic.
R9. Site-direct path, discovery protocol, query semantics, route semantics,
    access classifier, and uncertainty doctrine are unchanged.
R10. Legacy fetch_fn contract (status_code, body) tuples remain supported;
     dict-shaped transport results are the new richer form.

