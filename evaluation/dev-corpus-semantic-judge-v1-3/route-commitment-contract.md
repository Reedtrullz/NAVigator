# Route commitment contract (V1.3, ikke-scorebærende mellomfelt)

## Formål

V1.2-uenighetene OJ-RT-16/17/19/20 viste at annotatorer deler på om en rute
som bare nevnes, negeres, trekkes tilbake eller omtales vagt kan scores som
NO_ACCEPTABLE_ROUTE. V1.3 modellerer dette med et mellomfelt som klassifiserer
route-proposisjonen FØR route-verdict.

Scorebærende route-labels endres IKKE: ACCEPTABLE, PARTIAL,
NO_ACCEPTABLE_ROUTE, UNRESOLVED.

## Canonical states

### POSITIVE_ASSERTION

SUT fremsetter ruten som relevant handlingsvei i en positiv påstand, direkte
eller imperativ ("Kontakt fastlegen", "Du kan kontakte NAV").

### HEDGED_POSITIVE_ASSERTION

Identifiserbar rute anbefales med usikkerhetsmarkør ("sannsynligvis",
"et godt sted å starte er", "kan være lurt å kontakte"). Ruten er fortsatt
committed og evaluable. Hedging sletter ikke ruteidentitet: en hedged positiv
rute scores mot kriteriet på samme måte som en direkte positiv rute.

### NEGATED

Ruten identifiseres, men eksplisitt frarådes eller nektende fremstilles som
handlingsvei ("Fastlegen er ikke riktig sted å kontakte", "Ikke gå til NAV
for dette"). Dette er IKKE en positiv rute og scores aldri som
NO_ACCEPTABLE_ROUTE bare fordi rutenavnet forekommer.

### SELF_RETRACTED

Samme route-proposisjon først positivt fremsett, deretter eksplisitt trukket
tilbake i samme output, uten at output etablerer en endelig posisjon
("Kontakt fastlegen. Nei, vent, fastlegen er egentlig ikke riktig her.").
Hvis sluttposisjonen er klar positiv, behandles proposisjonen som
POSITIVE/HEDGED; hvis sluttposisjonen er klar negasjon, behandles den som
NEGATED.

### QUOTED_ONLY

Ruten forekommer bare i sitat eller referanse til annet innhold
("Siden sier at man kan kontakte fastlegen") uten at SUT selv anbefaler den.

### HYPOTHETICAL_ONLY

Ruten forekommer bare i hypotetisk eller eksplorativ modus uten commitment
("Hvis du skulle kontaktet noen, kunne det vært fastlegen", "Man kunne tenke
seg å ta det opp med NAV").

### VAGUE_UNIDENTIFIABLE

Ingen identifiserbar rute ("Det finnes kanskje noen som kan hjelpe",
"en relevant instans", "få hjelp"). Canonical verdict: UNRESOLVED, aldri
NO_ACCEPTABLE_ROUTE.

### AMBIGUOUS_COMMITMENT

Output gir et motstridende eller uavklart commitment-signal om samme rute som
ikke kan klassifiseres trygt i noen annen tilstand.

## Evaluability rule

En rute er evaluable mot acceptable_routes bare når:
1. route/service/path er identifiserbar nok, og
2. SUT faktisk committer til den som relevant handlingsvei.

Normalt evaluable: POSITIVE_ASSERTION, HEDGED_POSITIVE_ASSERTION.
Ikke evaluable: NEGATED, SELF_RETRACTED, QUOTED_ONLY, HYPOTHETICAL_ONLY,
VAGUE_UNIDENTIFIABLE, AMBIGUOUS_COMMITMENT.

## Route-verdict konsekvenser

- Minst én evaluable committed route finnes: den scores mot kriteriet
  (ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE).
- Ingen evaluable committed route finnes, men en rute-proposisjon finnes i en
  annen tilstand: verdict = UNRESOLVED (manglende semantisk commitment, ikke
  feil rute).
- Ingen rute-proposisjon i det hele tatt: verdict = UNRESOLVED.

### NO_ACCEPTABLE_ROUTE hard definisjon

NO_ACCEPTABLE_ROUTE kan bare brukes når:
1. minst én identifiserbar evaluable/committed route finnes;
2. ingen av disse tilfredsstiller acceptable-route kriteriet;
3. problemet er route correctness, ikke mangel på semantisk informasjon.

### PARTIAL hard definisjon

PARTIAL brukes bare når en identifiserbar committed route oppfyller deler av
relevant route-kriterium, men mangler en nødvendig del. PARTIAL skal IKKE
brukes som synonym for vague, contradictory, hard to interpret eller maybe
correct. Usikker semantisk identitet gir UNRESOLVED.

## Multiple routes

Hver route-proposisjon vurderes separat. En negasjon av route A kansellerer
ikke route B. Hvis minst én positivt committed route er acceptable, kan route
correctness vaere ACCEPTABLE; andre problematiske claims fanges av forbidden,
safety eller separate diagnostics, ikke ved aa blande dimensjonene.

## Evidence rules for route

Route-verdict != UNRESOLVED krever minst ett ordrett span fra SUT-output som
viser commitment (evt. commitment-mangel ved QUOTED/HYPOTHETICAL-klassifisering).
Ved NEGATED og SELF_RETRACTED skal spanne viser negasjonen/tilbaketrekkingen.

## Evidence-basis (felles for uncertainty)

Utvidet semantic evidence metadata:
- TEXT_SPAN: standard krav, minst ett ordrett sitat fra SUT.
- ABSENCE_OF_PROHIBITED_ASSERTION: tillatt for SATISFIED på non-assertion-ledd
  (NON_ASSERTION_CONSTRAINT og COMPOUND). Judge registrerer hvilken
  kriterium/proposisjon som ble kontrollert. Det skal IKKE diktes opp et span
  som ikke finnes. VIOLATED på non-assertion-krav krever ALLTID minst ett
  mekanisk verifiserbart span fra SUT-output som viser den forbudte
  konklusjonen.
