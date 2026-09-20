# dev-corpus-semantic-judge-v1-1

Evaluator-contract-lineage for NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_1-ROUTE-CONTRACT-REPAIR.

## Formaal

Kollapse score-irrelevante route-labels CANONICAL_ACCEPTABLE og
EQUIVALENT_ACCEPTABLE til ACCEPTABLE i en ny lineage, uten a endre V1,
corpus, scorer V1 eller kritiske/forbudte/usikkerhetskontrakter.

## Terminalstatus

SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY

Preregistrert agreement gate feilet (93.75 % overall < 95 %; uncertainty
85 % < 90 %). Official modellvalidering ble aldri startet. Ingen gold er
frosset. Combined scorer V1.1 er ikke bygget.

## Hovedleveranser

- Frosset V1.1-kontrakt med ny route-enum og diagnostisk route_match_detail
- BURNED kontrafaktisk projeksjon: overall 92.42 -> 98.48 %, route
  76.47 -> 100 % (BURNED_COUNTERFACTUAL_NOT_VALIDATION)
- 20-fixture kalibrering (burned, 3 kjoeringer/iterasjoner)
- 80 ferske valideringsfixtures (20 per dimensjon, 6 injection-outputs)
- Dobbelt blindt annoteringspass: 93.75 % overall enighet
- 0 av 5 uenigheter pa den kollapsete CANONICAL/EQUIVALENT-grensen
- Schema-failure tester: PASS

## Integritet

Alle V1-baselines re-verifisert identisk ved oppstart og lukking
(se baseline-integrity.json). Historiske filer endret: 0.
V1 forblir DEV_CORPUS_SEMANTIC_JUDGE_V1_NOT_READY.

## Inngang for lesere

- final-report.md: full sluttrapport med gate-utfall og anbefalt neste etappe
- semantic-judge-manifest-v1-1.json: maskinlesbar status og SHA-er
- route-contract-rationale.md: hypotese og endringsomfang

Ikke bruk artifacts i denne mappen som valideringsgold eller
readiness-bevis. Neste bounded stage er beskrevet i final-report.md.
