# Permanente regresjonstester - NAV Explore

Status: 30.08.2026. Alle ankere er verifisert mot KB og/eller primarkilde
seb den samme sesjonen (se data/qa-log.md for kilde- og lesetidspunkt).

## Slik skal testene brukes

1. Scoreren (score_baseline.py) er hovedregresjonen for ruting:
   kjor "python3 evaluation/score_baseline.py" og krever 48/48 BESTATT.
2. Faktatestene under er manuelle sjekkpunkter for innhold som scoreren
   ikke fanger (tall, datoer, signaturkrav, negativlogikk).
3. En endring i KB som breaker et anker skal stoppe merge/deploy.

## F1. Delt barnetrygd - satsdeling

- Delt ordinaer barnetrygd: 2 012 kr/mnd / 2 = 1 006 kr/mnd per forelder.
- Delt utvidet barnetrygd: 2 572 kr/mnd / 2 = 1 286 kr/mnd per forelder;
  1 286 gjelder KUN utvidet.
- Fil: 54-delt-barnetrygd-ordinar-og-utvidet.md;
  data/familieokonomi-regler.json.
- Feilmode hvis brutt: OLD_RULE eller satsforveksling.

## F2. Dato-motor: overgangsstonad 01.07.2026-grensen

- Soknad etter 01.07.2026 -> nye regler (kapittel 15), uavhengig av
  enslig-dato. Ensligdato etter soknad endrer ikke hovedregelvalget.
- Hovedperiode 14 maneder; +24 maneder ved forbigaende sykdom;
  saerlig tilsyn til 18 ar; oppsigelsesforbud siste 6 maneder.
- Fil: 63-overgangsstonad-endringsloven-og-kapittel-15.md,
  64-overgangsstonad-nye-regler-i-dybden.md,
  68-overgangsforskriften-i-dybden.md.
- Feilmode: OLD_RULE (overgangsregler brukt paa nye saker).

## F3. BUP-henvisning og underskrift

- Henvisning til BUP kreves: fastlege, psykolog eller barnevernsleder
  kan henvise (fil 24-kildedokumentasjon-bup-og-habu.md).
- Skole/PPT kan IKKE henvise direkte til BUP.
- HABU: 0-16 ar i samrad med foresatte; 16-18 ar kan henvises uten
  foresattes samtykke (fil 24).
- Feilmode: WRONG_SERVICE hvis skolen beskrives som BUP-henviser.

## F4. Barnevern er ikke automatisk

- Bekymringsmelding utloser undersokelse (kap. 4/7), ikke automatisk
  omsorgsovertakelse. Psykisk helse-hjelp til barn utloser ikke
  barnevern i seg selv.
- Fil: 38-barnevernet-hjelp-ikke-bare-inngrep.md,
  40-bekymringsmelding-og-undersokelse.md.
- Feilmode: OVER_ESCALATION.

## F5. Bolig/nodhjelp - frister og rettigheter

- Husleieloven: protest ved oppsigelse skriftlig innen 1 maned (9-8);
  formkrav 9-7; varselsadgang 9-11 (begjaering tidligst 2 uker etter
  varsel). HTU gir gratis veiledning/mekling.
- Nodhjelp: stonad til livsopphold 18, sarlige tilfeller 19; dekning
  av gjeld er skjonnsmessig, aldri generell rettighet.
- Fil: 57-nodhjelp-og-akutte-situasjoner.md.

## F6. RPH gjelder voksne (18+)

- Rask psykisk helsehjelp er et voksen tilbud (18+) - ikke for barn.
  Kommunale tilbud for barn/unge har andre navn (lavterskel,
  helsestasjon for ungdom, familieteam).
- Fil: 16-livssituasjoner/05-voksnes-psykiske-helse.md,
  25-kommunale-psykiske-tjenester-barn-unge.md.
- Feilmode: WRONG_SERVICE hvis RPH anbefales for barn.

## F7. Mari-canary (negativlogikk)

- Ingen dokument skal omtale Mari-journalens datter som diagnostisert
  med ADHD; utredning startet, ingen formell diagnose.
- Ingen antatt inntekt, bosted, vold eller konfliktniva i filer.
- Overgangsstonad er IKKE automatisk til rett; soknad og vilkar skal
  alltid nevnes.
- Fil 22-personlig-journal-mari.md, 44-mari-vurdering-samlivsbrudd.md;
  regresjonskrav fanget i data/qa-log.md.
- Sjekk: rg -n -i 'sterk ADHD|har ADHD|diagnostisert.*ADHD' *.md
  skal gi 0 treff.

## F8. Akuttruting (safety-critical)

- S43-S48 skal alltid beholde akuttnokler i first-aktor: 113 (livsfare),
  116 117 (legevakt), 116 123 (hjelpelinjen), legevakt, politi ved
  umiddelbar fare.
- Barnehus/akutt barnevern ved overgrep mistanke.
- Scoreren har strukturell forbidden-sjekk for disse; aldri senk
  terskelen her.
