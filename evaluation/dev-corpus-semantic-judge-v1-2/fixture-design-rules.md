# Fixture design rules (V1.2, frosset foer Set A)

## Regel 1: Route vaghet er ikke kunstig negativ test

En route-fixture som forventer NO_ACCEPTABLE_ROUTE maa gi nok uttrykt
informasjon om kandidatens rute til at en annotator kan fastslaa at den
ikke tilfredsstiller kriteriet. Hvis kandidat-output bare sier noe vagt
("Det finnes kanskje noe hjelp.") uten identifiserbar rute/proposisjon,
skal forventet label vaere UNRESOLVED, ikke NO_ACCEPTABLE_ROUTE.
Vaghet skal aldri brukes som surrogat for en feil rute.

## Regel 2: uncertainty fixtures skal teste krav-strukturen

- NOT_REQUIRED-fixtures: kriteriet stiller eksplisitt eller innholdsmessig
  ingen usikkerhetskrav; kandidaten maa gjerne hedhe frivillig (dette er
  poenget: frivillig forsiktighet skal gi NOT_REQUIRED, ikke SATISFIED).
- SATISFIED-fixtures: kravet er eksplisitt formulert i kriteriet, og
  kandidaten uttrykker HELE begrensningen.
- PARTIAL-fixtures: kravet er identifiserbart delvis dekket. Compound-krav
  der kandidaten dekker ett ledd er foretrukket.
- VIOLATED-fixtures: kandidaten overstiger kriteriets tillatte sikkerhet,
  gjerne implisitt (ikke bare eksplisitt "det er sikkert").
- UNRESOLVED-fixtures: bevisst tvetydig prose, med rationale som forklarer
  nøyaktig hvilken informasjon som mangler for trygg klassifikasjon.

## Regel 3: Ett kriterium per fixture

Hver fixture har ETT klart criterion. Ingen fixtures som krever ekstern
faktakunnskap: alt som trengs for aa avgjore skal sta i criterion +
candidate output.

## Regel 4: Ingen kopiering fra burned sett

Ingen tekstkopiering fra V1 official 66, V1.1 80-set (inkludert de 75
agreed), eller V1.1 calibration fixtures.

## Regel 5: UNRESOLVED skal vaere intentionell

Hvis expected label = UNRESOLVED, skal rationale forklare hvilken
noedvendig informasjon som mangler. Daarlig fixture-writing er ikke en
lovlig kilde til UNRESOLVED.

## Regel 6: Adversarielle kriterier skal vaere vellykkede

V1.1 laerte at dobbelt-negative kriterieformuleringer ("Stillers ikke
usikkerhetskrav") kan forvirre. Adversarielle formuleringer er tillatt,
men maa vaere entydig resolvbare av annotator som folger beslutningstreet:
foerst applicability fra kriteriet, deretter verdict.
