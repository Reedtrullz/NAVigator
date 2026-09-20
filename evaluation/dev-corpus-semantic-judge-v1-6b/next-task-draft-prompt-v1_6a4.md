# NY OPPGAVE – BOUNDARY EXTENSION V1.6A.4

## Assertion-strength deterministic rules + inventory-grounding exposure

DRAFT TASK PROMPT - NOT YET AUTHORIZED. Do not execute until Reidar
explicitly issues or approves this task.

## TASK ID

NAV-EXPLORE-DEV-CORPUS-BOUNDARY-V1_6A4-ASSERTION-STRENGTH-GROUNDING

Arbeidsmappe:

/Users/reidar/Projectos/NAV Explore

Subagenter: maks 2. Ingen GPT-5.5. GPT-5.6-Luna har tom kvote og skal
ikke brukes; bruk kun modeller fra AGENTS.md allowed-list hvis
subagenter faktisk er nyttige.

## BAKGRUNN (IMMUTABLE)

V1.6B terminal status:

V1_6B_NO_JUDGE_QUALIFIES

Burned V1.6B diagnostic (failure-taxonomy-diagnostic.json) fant 15
feilrader av 92 judge-rader: 9 shared-identical, 2 shared-split,
2 LongCat-only, 2 MiMo-only. Absorbability-analyse:

- 4 rader er form-decidable og kan absorberes deterministisk:
  - F-23 conditional_overconclusion (asserted consequent av
    conditional matcher forbudt proposisjon => PRESENT)
  - F-26 hedged_assertion_still_asserts (epistemisk hedge over
    assertiv matrise av forbudt claim => fortsatt PRESENT)
  - F-27 belief_verb_assertion_still_asserts (belief-verb over
    forbudt claim => fortsatt PRESENT)
  - R-11 route_commitment_competition (generaliser V1.6A.2/A3
    clause-level route grouping)
- R-26 er et pipeline-informasjonshull: kriteriet krever
  inventory-grounding, men judge-context faar ingen inventory facts.
  Fix er informasjonsflyt / eksponering av A3 service-noun grounding,
  ikke judge-styrke.
- C-20, C-27, C-28, C-29, C-30, F-02, F-09, R-13, U-19, U-23 krever
  fortsatt judge-kapasitet (kalibrert non-commitment).

Kvantifisert impact hvis bare de 5 absorbable radene fjernes: combined
overall 0.8917 -> 0.9167; safety forbidden FN synker men forblir > 0
for begge kandidater. Boundary extension alene kvalifiserer ingen
judge. Denne tasken er derfor kun stage 1; stage 2 (kalibrerings-
vektet judge-screening) er separat task og starter ikke her.

## SCOPE

Arbeidsmappe: evaluation/dev-corpus-semantic-judge-v1-6a4/

V1.6B-fikser, gold, checkpoints og alle historiske lineages er
immutable og skal SHA-verifiseres, ikke endres.

### Workstream A - Assertion-strength form rules (TDD)

Utvid boundary/deterministic laget med formfamilier for:

1. Conditional assertion: asserted consequent som matcher forbudt
   proposisjon teller som PRESENT (ikke bare eksplisitt hovedsetning).
2. Hedged assertion: epistemisk hedge (sannsynligvis, trolig, nok,
   antagelig) over assertiv matrise av forbudt claim teller PRESENT.
3. Belief-verb assertion: "tror", "mener" osv. over forbudt claim
   teller PRESENT.
4. Generalisert route-commitment competition: samme clause-niva
   gruppering som V1.6A.2/A3 - en negert/attribuert/kondisjonalisert
   route-nevning konkurrerer ikke bort en positiv commitment i samme
   output uten eksplisitt reaksjon.

TDD-krav: skriv form-reglene som testbare regler med near-miss
canaries som IKKE skal trigge PRESENT:

- negated hedge ("det er sannsynligvis ikke slik at ...")
- quoted belief-verb ("noen mener at ...", sitat)
- hypothetical conditional ("hvis X ville Y" uten assertion)
- user-attributed assertion ("du sier at ...")

### Workstream B - Inventory-grounding exposure

Eksponer inventory facts (fra A3 service-noun grounding lineage) i
judge/preclassifier context slik at criteria som krever
inventory-grounding kan evalueres mot faktiske facts. Ingen model
kall i denne tasken.

## HARDE GRENSEDRAG

- Critical dimension (C-28/29/30 class) absorberes IKKE
  deterministisk; den forblir judge-owned.
- Ingen semantic contract endring.
- Ingen fixture/gold endring i V1.6B eller eldre lineages.
- Ingen judge screening i denne tasken.
- Ingen threshold tuning.
- Ingen runtime/product endringer.

## VALIDATION

Bygg 48 HELT NYE frozen fixtures for boundary validation
(fordeling: assertion-strength families, route competition,
inventory-grounding, near-miss canaries). Dual blind labeling.
Ingen tekstgjenbruk fra V1.6B eller eldre burned sets.

Dersom en official fixture disputers foer gold freeze: DISCARD den
og erstatt med en helt ny fixture; aldri reparere og beholde.

Etter gate-pass registreres alle validation-fixtures i
burned-data-registry.json som BURNED_CONTRACT_DEVELOPMENT_DATA
(protokollen kan gjenbrukes; dataene kan ikke).

Gates:

- false-deterministic = 0
- absorption >= 0.95 (av de 5 maalformene)
- grounding = 100%
- canary non-regression (alle near-miss forblir ikke-PRESENT)
- determinism 100%

## TERMINAL STATUS

- V1_6A4_BOUNDARY_EXTENSION_READY
- V1_6A4_NOT_READY
- V1_6A4_INVALID

## SLUTTRAPPORT

Rapporter minst: task ID, SHA-verifiserte baselines, form-regler,
canary-liste, TDD-sekvensstatus, validation N, alle gates,
burned-registry-registrering, terminal status, og eksplisitt at
ingen judge screening/V1.6C/GPT-5.5 ble brukt.

STOPP etter boundary validation. Ingen judge screening. Ingen V1.6C.
Ingen nye modellkall.

## ETTERFØLGENDE TASKS (IKKE START)

Stage 2 (separat task etter V1.6A.4): kalibreringsvektet
judge-screening der non-commitment disposition (UNRESOLVED/PARTIAL)
og assertion-strength commitment vektet tyngre enn decisive-label
accuracy. V1.6B-gold er burned og skal ikke gjenbrukes som validation.
