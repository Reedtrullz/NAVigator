# dev-corpus-v1

Maskinlesbart dev-/regresjonssett med 120 syntetiske caser, levert av bruker 2026-09-10 og kategorisert i tre korpus:

- `cases/safety_cases.json`: SAF-001 til SAF-020 (kildekalder 1-20): akutt/safety og eskaleringsnivaa.
- `cases/routing_cases.json`: ROUT-021 til ROUT-095 (kildekalder 21-95): barn/unge, BUP/HABU/PPT/skole, kommunepsykisk helse og 18-23-routing, familie/barnevern, NAV/oekonomi/bolig.
- `cases/discovery_adversarial_cases.json`: DIS-096 til DIS-120 (kildekalder 96-120): lokal discovery, provenance og adversarial.

Alle case er **BURNED_DEVELOPMENT_ONLY**: de skal ikke brukes som fresh holdout, sertifisering eller threshold-mal.

Scoring bruker gold-modellen i `gold-model.md`: `safety_priority`, `acceptable_routes[]`, `forbidden_claims[]`, `required_uncertainty`, `required_evidence_fields`, `critical_error_if`. Reduser aldri et hele til en enkelt "riktig/feil"-label.

Ingen runtime- eller forskningsfiler er endret av dette datasett-bygget. Manifest med sha256: `manifest.json`.
