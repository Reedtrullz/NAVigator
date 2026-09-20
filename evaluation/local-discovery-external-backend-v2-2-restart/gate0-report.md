# GATE 0 REPORT - V2.2 RESTART

Task: `NAV-EXPLORE-LOCAL-DISCOVERY-EXTERNAL-BACKEND-SELECTION-V2_2-RESTART`
Date: 2026-09-09. Authoritative design (not redesigned):
`evaluation/local-discovery-external-backend-v2-2/backend-selection-contract-restart.md`.

## Gate 0 results

| Check | Result |
|---|---|
| `TAVILY_API_KEY` presence (env `TAVILY_API_KEY`/`TAVILY_API_TOKEN`) | NOT_AVAILABLE |
| `BRAVE_API_KEY` presence (env `BRAVE_API_KEY`/`BRAVE_SEARCH_API_KEY`) | NOT_AVAILABLE |
| Project-local secret/config paths | 0 files exist; nothing to contain keys |
| Secret values printed | 0 |
| Secret values stored in artifacts/logs | 0 |
| Protocol V1 SHA `fb533d99...f99ca` | MATCH (re-verified) |
| Candidate V2 manifest `74329662...a678` | MATCH (re-verified) |
| Provider config V2 `d6890b5f...cbc3` | MATCH (re-verified) |
| V2.1 snapshot (7 files) | 7/7 MATCH |
| Fresh municipalities used | 0 |
| Historical files modified | 0 |

## Stop decision

Per the restart task instruction: a missing expected credential requires an
immediate STOP and a missing-credential report. Both expected credentials
are missing, so:

- No account was created, no key generated, no plan activated.
- The frozen V2.2 benchmark contract was NOT executed and NOT redesigned.
- Adapters, configs, comparison artifacts, and candidate freezes were NOT
  fabricated.

## Missing credentials (exactly as required)

- `TAVILY_API_KEY` - MISSING
- `BRAVE_API_KEY` - MISSING

Execution of the frozen restart contract resumes only when at least one of
these is present in the environment (or an approved project secret path)
at the start of a future attempt. No other remediation was performed on
the user's behalf.
