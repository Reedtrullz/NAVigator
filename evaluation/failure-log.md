# Failure log - baseline evaluering

Datasett: 48 scenarioer (S01-S48). Scorer: evaluation/score_baseline.py.
Baseline-resultat: evaluation/baseline-results.json.

## Kjorehistorikk

| Run | Bestatt | Delvis | Feilet | Kommentar |
|-----|---------|--------|--------|-----------|
| run5 (pre-patch) | 33 | 8 | 7 | Flere scenarioer feilet pga uopploste kildereferanser i scoreren (tom haystack) |
| run6 (etter resolver-patch) | 44 | 0 | 4 | S19, S36, S41, S43 feilet paa aktor-heuristikk |
| run7 (etter heuristikk-fix) | 48 | 0 | 0 | Alle 9 dimensjoner 5/5; 0 safety-critical feil |

## Feilklasser funnet

### 1. Scorer-infrastruktur (ikke KB-feil)

Disse ble fikset i scoreren, ikke i kunnskapsbasen. De teller derfor som
verktoyfeil, ikke som faglige feil i NAV Explore.

- S19/S36/S41/S43 (run6): aktor-heuristikken plukket de lengste ordene i
  expected-routing-teksten ("psykiatrisk", "hovedregelen", "utlosering")
  i stedet for aktorene. 3-bokstavs akronymer (BUP, RPH, DPS) ble filtrert
  bort av min lengdekrav paa 4 tegn.
- Fiks: heuristikken tar na de forste substantivierte tokens + akronymer
  (3+ tegn), og stoppordlisten ble utvidet.
- Run5-massen (S01, S03, S09, S11, S12, S16, S19, S35, S36, S37, S38, S40,
  S41, S42, S43): kildereferanser som "16-livssituasjoner/05" og
  "familieokonomi-regler.json r23" ga tom haystack. Fikset med utvidet
  resolve_source (mappeprefiks, numerisk suffix, json-suffix).

### 2. Reelt KB-hull (verifisert)

#### S43 - barnesikkerhet ved akutt voksenkrise

- Claim i golden route: "barnesikkerhet: ikke la barnet alene med
  forsvarsloshet; var person".
- Verifisert med rg: teksten finnes IKKE i fil 42 (vold/trusler),
  fil 57 (nodhjelp) eller fil 16-05 (voksnes psykiske helse).
- Sokt hele korpuset: ingen fil inneholder "barnesikkerhet",
  "forsvarslos" eller "ikke la barnet alene".
- Scenarioet passerer likevel i run7 fordi ordet "alene" treffes svakt i
  kilden 42. Dette er en svak pass og logges her som aapent hull.
- Feilklasse: ASSUMED_FACT / dokumentasjonsjobb - testdata antar en
  veiledning som aldri ble skrevet inn i KB.
- Root cause (per oppdrag paragraf 28): beslutningstreet har en gren
  (barnesikkerhet ved akutt voksenkrise), men KB mangler selve
  innholdet i lovet. Fil 57 dekker okonomi/bolig/medisin i nod, ikke
  barns sikkerhet; fil 42 dekker vold/trusler, men ikke generell
  barnesikkerhetsvurdering.

### 3. Ikke-klassifiserte observasjoner

- Scoreren maaler evidence-coverage: kan golden routes dokumenteres fra
  eksisterende KB-innhold? Den maaler IKKE full faglig kvalitet,
  kildekvalitet eller ruting i en live dialog. Detta begrenser hva
  48/48 BESTATT kan brukes til.
- Web-sok var utilgjengelig i denne sesjonen (metodefeil, ikke nettfail).
  Barnesikkerhets-hullet faar dermed 0 av 2 oppslagssjanser brukt
  effektivt; hullet noteres i stedet for aa fylles med uverifisert
  innhold.

## Konklusjon

Ingen sikkerhetskritisk KB-feil ble funnet. Ett reelt kunnskapshull er
avdekket (S43 barnesikkerhet). Alle andre feil underveis var scorer-bugs.
Retting av hullet krever enten en autoritativ kilde (Helsenorge/Legevakt/
Barnevernvett) eller en eksplisitt "hull"-note i kunnskapshullregisteret.
