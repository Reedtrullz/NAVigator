# 53. Kildedokumentasjon okonomi (barnebidrag-etappen)

**Sist verifisert**: 29.08.2026 (barnebidrag); 30.08.2026 (skatt på mottatt barnebidrag, kjerne)
**Formal**: Sporbarhet for alle satser, grenser og prosesskritt introdusert i fil 48-52. Se ogsa data/legal-index.json (lovstoff) og data/familieokonomi-regler.json (rutingregler med kilde-ID).

---

## Primarkilder hentet og verifisert

| Kilde | URL | Hentet | Brukt til |
| --- | --- | --- | --- |
| nav.no Barnebidrag | https://www.nav.no/barnebidrag | 29.08.2026 (siden oppdatert 25.08.2026) | Beregningsmodell, gebyr 1 345, fritak 367 400, behandlingstid 9/8 mnd, 12-prosentterskel, maksgrenser 5/6 og 25 prosent, barnets inntekt 62 400/208 000, aldersjustering, inkreving (purring 10., 14 dagers frister, utleggstrekk), delt fast bosted-eksempel |
| nav.no Bidragsforskudd | https://www.nav.no/bidragsforskudd | 29.08.2026 | Satser 2 080/2 600/1 560/1 040, inntektsgrenser 388 200-686 400, vilkar, delt fast bosted-unntak, 3 maneder tilbake, 5/4 uker behandlingstid, klage 6 uker |
| nav.no Saerbidrag | https://www.nav.no/saerbidrag (tidligere bidrag til saerlige utgifter) | 29.08.2026 | Minstebelop 2 080 (fra 1.7.2025), barnets inntekt 60 300/201 000, ettarsfrist, fordeling etter inntekt |
| nav.no bidragsgjeld | https://www.nav.no/bidragsgjeld (via sok) | 29.08.2026 | Sletting: inntekt < 75x forhoyet forskuddssats, delsletting, formue, 18+-ettergivelse |
| Lovdata rundskriv v1-55-02 | https://lovdata.no/nav/rundskriv/v1-55-02 | 29.08.2026, fulltekst via r.jina.ai-proxy (57 KB) | Alle sjablonger 1.7.2026: forbruk, boutgifter, tilsyn, samvarsfradrag, barnetrygd 2 012, utvidet 30 864, smabarnstillegg 8 544, skattesatser |
| Lovdata barnelova | https://lovdata.no/loi/1981-04-08-7 (bnl_full.txt) | 29.08.2026 | Kap. 8 par. 66-80 (fostringstilskot), par. 36 delt bosted, par. 51 mekling |
| Lovdata inkrevingloven | LOV-2005-04-29-20 | 29.08.2026 | Par. 5, 7, 8, 26-29; sist endret LOV-2025-04-25-12 i kraft 01.01.2026 |
| nav.no bidragskalkulator (veiledende) | https://www.nav.no/barnebidrag/tjenester | 29.08.2026 | Veiledende privat-avtale-kalkulator LIVE; NAVs fastsettingskalkulator midlertidig borte |
| nav.no samvaersalkulator | nav.no | 29.08.2026 | Live; fastsetter samvaersklasse |
| skatteetaten.no Barnebidrag og skatt | skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/familie-og-helse/barn/barnebidrag/ | 30.08.2026 | Mottatt barnebidrag ikke skattepliktig; ingen fradrag for betaler (sktl §§ 5-42/5-43) |

## Verifiseringsmetode

- Fulltekst-henting: Lovdata rundskriv v1-55-02 hentet komplett via r.jina.ai-proxy (curl r.jina.ai/https://lovdata.no/nav/rundskriv/v1-55-02) fordi Exa-fetch truncates. Lokalt speil: /tmp/v15502-jina.txt.
- nav.no-sider: hentet som tekst til /tmp/nav-bb.txt, /tmp/nav-forskudd.txt, /tmp/nav-utgifter.txt, /tmp/nav-bt.txt.
- Kryssjekk: navikt/bidrag-bidragskalkulator-api SjablonService.kt bekrefter samvarsfradrag = punkt 4 i rundskrivet; e2e-mocks i bidrag-bidragskalkulator-ui matcher 1.7.2024-satser eksakt (mock to ar gammel, data.ts endret 2026-06-10). Kloner: /tmp/bk-api-29, /tmp/bk-ui-29.
- Alle kroner/satser kontrollert minst to ganger mot primarkilde (grep + lesing av kildekontekst).

## Satsregister

Sentral maskinlesbar registrering: data/legal-index.json (lovstoff) og data/familieokonomi-regler.json (ruting + nokkel-satser). Hovedtabell for samvarsfradrag ogsa maskinlesbar i fil 49.

## Verifiserte 2026-satser (sammendrag, gyldige fra 01.07.2026 med mindre annet er sagt)

- Forbruksutgifter barn: 5 870 / 7 523 / 8 789 / 9 764 (0-5 / 6-10 / 11-14 / 15+)
- Boutgifter barn (fast): 3 811
- Tilsynssjablong: stonadsats 64 prosent; barnehage heltid 257/deltid 103 (dag); SFO heltid 572/deltid 469 (maned); grenser 7 648/9 977/11 308 (1/2/3+ barn); skattefradrag 15 000/10 000; netto tilsynsfradrag 22 prosent (fra 01.01.2026)
- Samvarsfradrag: tabell i fil 49 (K1 386-696; K2 1 277-2 306; K3 3 249-4 684; K4 4 078-5 880)
- Bidragsevne: eget underhold 12 330/10 442; boutgifter 12 408/7 833; eget barn 4 652/2 326
- Skatt: 22 prosent + 7,6 trygdeavgift; minstefradrag 40 prosent/maks 75 400; personfradrag 114 540; trinnskatt 2026: 0/1,7/4,0/13,7/16,8/17,8
- Barnetrygd ordinær: 2 012/mnd; utvidet: 2 572/mnd (30 864/ar) fra 01.02.2026; delt ordinær: 1 006/mnd per forelder; delt utvidet: 1 286/mnd per forelder; smabarnstillegg 8 544/ar (fra 01.02.2026)
- Bidragsforskudd: 2 080/2 600 forhoyet; 1 560 ordinaert; 1 040 redusert; grenser 388 200-686 400
- Gebyr: 1 345; fritak under 367 400; behandlingstid 9/8 mnd
- Saerbidrag: minimum 2 080; barnets inntekt 60 300/201 000
- Barnets inntekt (barnebidrag): 62 400 / 208 000

## Ny lovstatus

- Barnelova LOV-1981-04-08-7 (kap. 8) er GJELDENDE for barnebidrag per 29.08.2026.
- Den nye vedtatte barneloven (kap. 9, par. 9-x) er IKKE i kraft og er ikke brukt som gjeldende rett.
- Inkrevingloven LOV-2005-04-29-20 gjeldende; sist endret LOV-2025-04-25-12 (i kraft 01.01.2026).

## Kunnskapshull

1. Forskrift om fastsetting og endring av barnebidrag: eksakt Lovdata-ID ikke funnet. Rundskriv r55-02 + v1-55-02 brukt som autoritative mellomkilder.
2. Samvaersalkulatoren: interne klassegrenser (netter/mnd per klasse) er ikke offisielt tabellfestet av NAV.
3. Fastsatt bidrag lavere enn forskuddssats: NAVs utmaling i dette tilfellet ikke fullt verifisert.
4. Bostottekalkulator/vilkar: ikke kontrollert i denne etappen.
5. Livsoppholdssatser BFD (regjeringen.no id691824): ikke hentet.
6. Overgangsstonad 2026-satser/vilkar og omsorgspenger-dagsgrenser: ikke re-verifisert her (eksisterende filer gjelder). Overgangsforskriften FOR-2026-06-25-1361 er verifisert 30.08.2026 i fil 68; skatt på mottatt barnebidrag er kjernen verifisert 30.08.2026 (Skatteetaten), underpunkter (etterbetaling/saerbidrag/over 18/forskudd) gjenstår (fil 69).
7. Saerbidrag: eksakt klagefrist ikke verifisert separat.
8. Videregaende-opplaring: eksakt varighetstak (maks maneder/ar) ikke eksplisitt tabellfestet i hentede kilder.
9. Samvaersklassedefinisjoner (netter/dager per klasse): beskrevet som kalkulatorbestemt, ikke tallfestet.

## Kvalitetsgrenser

- Regneeksemplene i fil 48 er FORENKLET og skal ikke fremstilles som NAV-vedtak.
- Fil 52 inneholder ingen beregnede kroner.
- Alle tall ma re-verifiseres mot nav.no/satser ved nyere dato enn 29.08.2026, spesielt etter 01.07 hvert ar.
