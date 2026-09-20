# LOCAL DISCOVERY PROVIDER V2.1 - ADAPTER CORRECTNESS

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-V2_1-ADAPTER-CORRECTNESS (2026-09-09).

**Terminal status: LOCAL_DISCOVERY_PROVIDER_V2_1_ADAPTER_FIXED_BACKEND_NOT_READY**

Adapter-bugen (curl exit kode brukt som HTTP-status + challenge-scan kun foerste 5000 tegn) er fikset og bevist. Brave-backend er fortsatt bot-blokert (0/5 BOT_BLOCKED, korrekt klassifisert) - derfor ingen fresh-eval candidate.

## Filer

- TASK-LOCK.json - task lock med terminal status
- adapter-correctness-contract-v2-1.md - frosset bug-kontrakt (R1-R10)
- adapter-correctness-tests-v2-1.json - frosset testplan (cases A-H, T1-T5, INV1-2)
- fixtures/ - ekte arkivert 429-challenge + meta (SHA-verifisert)
- e1_rerun.py - E1 readiness re-run harness (burned data)
- provider-readiness-v2-1.json - E1 resultater + begge verdome (adapter PASS / backend FAIL)
- security-regression.json, archived-challenge-regression.json - sikkerhets- og fixture-regresjon
- implementation-report.md, test-report.md, historical-integrity.md - rapporter
- implementation-snapshot/ - SHA-provenance for endrede + uendrede filer
- final-report.md - 50-punkts sluttrapport

## Nøkkelresultater

- V2.1 tests 19/19, V2 27/27, V1 49/49 - alle groen
- Site-direct 5/5 PASS paa brente kommuner (identisk med V2-baseline)
- Brave 0/5 - alle 5 korrekt BOT_BLOCKED (HTTP 200 + challenge innhold; challenge_detected=true)
- 0 fresh kommuner brukt; 0 historiske filer endret
