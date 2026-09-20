# LOCAL DISCOVERY EXTERNAL BACKEND SELECTION V2.2

Task: `NAV-EXPLORE-LOCAL-DISCOVERY-EXTERNAL-BACKEND-SELECTION-V2_2`

## Terminal status

`BACKEND_SELECTION_BLOCKED_BY_CREDENTIALS`

The credential gate (task sections 7-9) ran before any backend probing:

- `BRAVE_API_CREDENTIAL = NOT_AVAILABLE`
- `TAVILY_API_CREDENTIAL = NOT_AVAILABLE`

Checks covered environment variables and project-local ignored secret/config
paths only. No secret values were printed, logged, or stored. No accounts
were created and no paid plans were activated (task sections 8 and 26).

Because no structured external candidate (Brave Search API, Tavily Search
API) had an authorized credential, the comparative benchmark (sections
17-34) was never started. Per section 9 this is not a backend failure.

## What was still verified

- Historical integrity: Protocol V1 SHA `fb533d99...f99ca`, provider config
  V2 SHA `d6890b5f...cbc3`, candidate V2 manifest SHA `74329662...a678`,
  and all seven V2.1 implementation-snapshot SHAs re-verified unchanged.
- Brave HTML remains the documented negative control; not re-evaluated.
- V1/V2/V2.1 regression suites re-run green after the task lock (see
  final-report.md and test evidence therein).

## Restart condition

A user-supplied authorized credential (env var `BRAVE_API_KEY` or
`TAVILY_API_KEY`, or an approved project secret path) is required before a
new bounded task can run the frozen benchmark design in
backend-selection-contract-restart.md. No credential request was made on
the user's behalf.
