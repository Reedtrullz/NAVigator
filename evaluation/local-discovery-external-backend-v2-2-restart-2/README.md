# V2.2 RESTART-2 - EXTERNAL BACKEND SELECTION (EXECUTED)

Task: `NAV-EXPLORE-LOCAL-DISCOVERY-EXTERNAL-BACKEND-SELECTION-V2_2-RESTART-2`

## Terminal status

`NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES`

The credential gate passed for exactly one candidate (Tavily, via
`.env.local` mode 0600). Brave Search API remained
`NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL`. The full frozen contract was
executed: benchmark freeze -> thin Tavily adapter + 20-test suite ->
failure simulations (fail-closed, 0 false NO_RESULTS) -> secret-leak QA
(0 leaks / 30 files) -> config freeze -> official 117-query two-mode
benchmark -> frozen comparison -> selection decision.

## Result

Tavily failed the preregistered GENERAL-mode gates: execution 87.18%
(< 95%), recall 80.34% (< 90%). Bot-block, failure-semantics, contract,
and secret gates all passed. Incremental recovery over site-direct:
0/117 - site-direct already covers every municipality in the burned
corpus, so the external fallback adds zero targets here.

## Consequence

No backend was selected; the V2.2 runtime integration, burned
integration run, forced-fallback tests, and candidate-runtime freeze
were deliberately not executed. Production lineage remains V2.1.
provider-config-v2-2.json stays frozen as benchmark-time config and is
superseded by this outcome.

## Key artifacts

- `backend-comparison-official.json` - frozen metrics + gate evaluation
- `provider-config-v2-2.json` - frozen config (SHA 376c2f3c...)
- `tavily-general-rows.json` / `tavily-official_domain_constrained-rows.json`
- `selection-decision.md`, `final-report.md`, `hashes.txt`
