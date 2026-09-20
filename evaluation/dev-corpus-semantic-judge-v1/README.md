# dev-corpus-semantic-judge-v1

Semantisk dommerlag for frozen Scorer V1. Maaleinstrument, ikke runtime.

## Status

DEV_CORPUS_SEMANTIC_JUDGE_V1_NOT_READY. Sikkerhetsgater passerte (0 critical
FN, 0 forbidden FN, 0 injection-brudd), men strict-label accuracy (92.4% < 95%),
route-equivalence accuracy (76.5% < 90%) og modal stability (87.5% < 95%)
feilet. Se final-report.md for alle 57 sluttrapport-punkter.

## Filguide

- TASK-LOCK.json: oppgavelaas og terminalstatus
- baseline-integrity.json: SHA-verifikasjon av corpus og scorer foer start
- semantic-judge-design.md: arkitektur og valideringsprotokoll
- semantic-judge-contract-v1.json: frosset kontrakt (modell, prompt-SHA, retry-policy)
- semantic_judge.py: dommerimplementasjon (transport, validering, fail-closed)
- run_calibration.py + calibration-*.json: kalibrering (burned)
- dual_label.py: dobbelt blindt annoteringspass
- judge-validation-fixtures.json / judge-validation-gold.json: valideringssett og frosset gold
- validation-protocol.json: forhandsregistrerte gater
- run_official_validation.py + official-validation-results.json: official one-shot
- run_stability.py + stability-results.json: stabilitet (24 fixtures x 5)
- test_schema_failures.py + schema-failure-tests.json: deterministisk valideringsfeil-testing
- injection-tests.json: SUT-injection-motstand
- coverage-report.json: criteria coverage dry-run
- ../dev-corpus-scorer-v1-semantic/: adapter, integration_test.py, manifest
- semantic-judge-manifest.json / scorer-v1-semantic-manifest.json: frosne instrument-hasher
- final-report.md: full sluttrapport (57 punkter)

## Gjenbruk

Ikke gjenbruk validation-fixtures eller gold i senere tasks uten eksplisitt
beslutning; de er da burn. Kalibreringssettet er burn. Prompten er frosset;
endring krever ny kontraktsha og full revalidering.
