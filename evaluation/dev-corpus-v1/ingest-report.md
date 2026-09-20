# ingest-report

**Hentet**: 2026-09-10, kilde: brukerpaste (120 nummererte caser).
**Ingen case er omformulert innholdsmessig**: citater forkortes der lenger tekst gaar paa kontekst, men alle gold-felt koples til den opprinnelige kalderens intensjon.

## Kategorisering

- Kalder 1-20 (20 caser): safety/akutt. Alle beholder en egen `safety_priority` i gold.
- Kalder 21-40 (20 caser): barn/unge, BUP/HABU/PPT/skole. Kapet i routing_cases.
- Kalder 41-60 (20 caser): kommunepsykisk helse og 18-23-routing. Kapet i routing_cases.
- Kalder 61-75 (15 caser): familie/barnevern. Kapet i routing_cases.
- Kalder 76-95 (20 caser): NAV/oekonomi/bolig. Kapet i routing_cases.
- Kalder 96-110 (15 caser): lokal discovery/provenance. Kapet i discovery_adversarial_cases.
- Kalder 111-120 (10 caser): adversarial/metatester. Kapet i discovery_adversarial_cases.

## ID-konvensjon

- SAF-nnn: kalder 1-20.
- ROUT-nnn: kalder nnn (21-95).
- DIS-nnn: kalder nnn (96-120).

Id = kildekalder-nummer for alle korpus. En utkastregel (kalder 21 = ROUT-041) ble forkastet foer publisering fordi den lagde et unodvendig offset.

Alle case beholder `source_line` for sporing tilbake til originalpaste.

## Gold-modell

Se `gold-model.md`. Ingen case har kun ett "riktig svar": alle har minst ett av feltene `acceptable_routes`, `forbidden_claims`, `required_uncertainty`, `required_evidence_fields` eller `critical_error_if`.

## Avvik fra opprinnelig anbefaling

Opprinnelig forslag var korpusnavnet `discovery/adversarial_cases`. Implementert som ett filobjekt `discovery_adversarial_cases.json` for aa holde filantall lavt; kapet inneholder baade kalder 96-110 (discovery) og 111-120 (adversarial).
