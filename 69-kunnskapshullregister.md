# 69. Kunnskapshullregister

**Datostempel**: 30.08.2026
**Status**: Sentralt register over kunnskapshull i overgangsstønads-delen, oppdatert etter GAP-closure 30.08.2026 mot FOR-2026-06-25-1361 og primærkilder (Lovdata, NAV, Husbanken, Skatteetaten). Registeret overstyrer de gamle hull-listene i fil 63-66 for punktene som er lukket. Ingen del er tilpasset konkrete vedtak.
**Kryssreferanser**: [68-overgangsforskriften-i-dybden](68-overgangsforskriften-i-dybden.md), [63-overgangsstonad-endringsloven-og-kapittel-15](63-overgangsstonad-endringsloven-og-kapittel-15.md), [64-overgangsstonad-nye-regler-i-dybden](64-overgangsstonad-nye-regler-i-dybden.md), [65-saerlig-tilsyn-dokumentasjon-aktorer](65-saerlig-tilsyn-dokumentasjon-aktorer.md), [66-barnetilsyn-og-samspill-andre-ytelser](66-barnetilsyn-og-samspill-andre-ytelser.md), [67-mari-overgangsstonad-vurdering](67-mari-overgangsstonad-vurdering.md), [53-kildedokumentasjon-okonomi](53-kildedokumentasjon-okonomi.md).

## 1. Statuskoder

| Kode | Betydning |
|---|---|
| LUKKET | Primærkilde funnet og verifisert; funnet dokumentert i ett eller flere dokumenter. |
| DELVIS LUKKET | Kjernen er verifisert; et avgrenset delspørsmål står igjen og rutes ikke. |
| ÅPENT | Ikke verifisert; ikke rut og ikke anta. |
| IKKE LENGER RELEVANT | Spørsmålet bygger på et premiss som er borte, eller er erstattet av et konkret verifisert svar. |

## 2. Registeret (status per 30.08.2026)

### 2.1 Overgangsforskriften — LUKKET

| | |
|---|---|
| Spørsmål | Hva inneholder overgangsforskriften; hvem omfattes; hvilke betingelser gjelder for gamle saker? |
| Svar | Forskrift 25.06.2026 nr. 1361 (FOR-2026-06-25-1361) er hentet i fulltekst fra Lovdata 30.08.2026. § 1 omfatter enslig mor/far som før 1.7.2026 (a) har vedtak om overgangsstønad eller barnetilsyn med periode ut over 1.7.2026, (b) har søkt og fyller vilkårene, (c) har fått avslag som omgjøres etter 1.7.2026 med virkningsdato før 1.7.2026, eller (d) har vedtak om overgangsstønad og kan få perioden utvidet/forlenget etter gamle § 15-8 andre, fjerde og femte ledd. § 13: stønadsperioder etter forskriften løper ikke ut over 30.06.2031. § 14: ikraft 1.07.2026, forskriften opphører å gjelde 01.07.2031. Endret ved FOR-2026-08-17-1633 (§ 5 endret, ny § 12 om midlertidig bortfall inntil én måned, gamle § 12/13 flyttet til § 13/14). |
| Funn lagret i | [68-overgangsforskriften-i-dybden](68-overgangsforskriften-i-dybden.md) (full paragrafvis gjennomgang og scenario-motor A-I); fil 63-67 og 00-BESLUTNINGSTRE oppdatert samtidig. |
| Kilde | lovdata.no/dokument/SF/forskrift/2026-06-25-1361 |

### 2.2 Stortingets barnetilsynssatser — IKKE LENGER RELEVANT

| | |
|---|---|
| Spørsmål | Maksbeløp for barnetilsyn fastsatt av Stortinget (tidligere hull). |
| Løsning | Premisset er borte: satsene er verifisert fra NAVs oppdaterte side. Fra 01.01.2026: 1 barn 4 895 kr/mnd (58 740/år), 2 barn 6 385 (76 620), 3+ 7 237 (86 844); 64 prosent dekning av dokumenterte utgifter; inntektsgrense 6 G = 819 294 kr; AAP, dagpenger, sykepenger m.m. teller i 6 G-vurderingen. Overført til fil 66 og r22 i data/familieokonomi-regler.json. |
| Kilde | nav.no/barnetilsyn-enslig (lest 30.08.2026) |

### 2.3 Skatt på mottatt barnebidrag — DELVIS LUKKET

| | |
|---|---|
| Spørsmål | Er mottatt barnebidrag skattepliktig inntekt? Får betaler skattefradrag? |
| Verifisert | Nei til begge: mottatt barnebidrag er ikke skattepliktig for mottaker, og betaler får ikke fradrag (skatteloven §§ 5-42/5-43; Skatteetatens side). |
| Igjen | Etterbetaling, særbidrag, barnebidrag til barn over 18 år og bidragsforskudd er ikke separat verifisert mot Skatteetaten; ingen av disse rutes. |
| Kilde | skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/familie-og-helse/barn/barnebidrag/ (lest 30.08.2026) |

### 2.4 AAP + overgangsstønad — LUKKET

| | |
|---|---|
| Spørsmål | Kan en person motta AAP og overgangsstønad samtidig etter reglene som gjelder fra 1.7.2026? |
| Svar | Ja som hovedregel, men overgangsstønaden avkortes. Folketrygdloven § 15-13 utelukker bare omstillingsstønad som gjenlevende, uføretrygd og tilsvarende utenlandske ytelser; AAP er ikke oppført. Ftrl § 11-27: valget om å kombinere ytelser gjelder bare ytelser for samme inntektstap, og overgangsstønad dekker ikke inntektstap. NAVs avkortingsliste inkluderer arbeidsavklaringspenger. Ved sykdom uten sykemelding, AAP eller uføretrygd krever NAV legeerklæring på egen sykdom. |
| Funn lagret i | Fil 66 (samspillsmatrise), fil 68. |
| Kilder | lovdata.no/lov/1997-02-28-19 (§ 15-13, § 11-27); nav.no/overgangsstonad-enslig (lest 30.08.2026) |

### 2.5 Bostøtte: inntektsbehandling av familieytelser — LUKKET

| | |
|---|---|
| Spørsmål | Hvilke ytelser teller i bostøtteinntekten (tidligere hull). |
| Svar | Skattepliktig inntekt før skatt for husstanden over 20 år teller; overgangsstønad er trygd og er med. Eksplisitt unntatt på Husbankens side: barnetrygd, barnebidrag, kontantstøtte, stønad til barnetilsyn, grunn- og hjelpestønad, økonomisk sosialhjelp, tiltakspenger, engangsstønad og skattepenger. AAP og dagpenger: 2/3-regelen i måneder med tre 14-dagersutbetalinger. Formuefribeløp: 333 557 kr (leid bolig) / 700 468 kr (formuesverdi primærbolig); kapitalfribeløp 6 672 kr. |
| Funn lagret i | [55-bostotte-i-dybden](55-bostotte-i-dybden.md), fil 66. |
| Kilde | husbanken.no/person/bostotte/inntektsgrunnlaget/ (sist oppdatert 19.06.2026, lest 30.08.2026) |

### 2.6 Lov 20.06.2025 nr. 40 (endring av § 15-4) — DELVIS LUKKET

| | |
|---|---|
| Spørsmål | Har lovendringen i § 15-4 trådt i kraft? |
| Verifisert | Loven endrer folketrygdloven § 15-4 andre ledd (viser til barnelova § 6-2). Status per 30.08.2026: VEDTATT IKKE I KRAFT; § 15-4 inneholder fortsatt ordlyden «fra den tid Kongen bestemmer», og kongelig ikraftresolusjon er ikke funnet. |
| Igjen | Overvåk Lovdatas ikrafttredjelsesvisning for kongelig resolusjon. |
| Kilder | lovdata.no/lov/2025-06-20-40; lovdata.no/lov/1997-02-28-19/§15-4 |

### 2.7 60 prosent, «andre kan ta vare» og «forhindret fra å arbeide» — LUKKET

| | |
|---|---|
| Spørsmål | Forholdet mellom lovordlyd og NAVs brukerformuleringer (kildekonflikt). |
| Svar | Lovtekst (§ 15-4) bruker «varig klart mer av den daglige omsorgen»; «minst 60 prosent» er NAVs brukerrettete formulering, ikke lovordlyd. «Du har ikke rett til stønaden dersom andre kan ta vare på barnet ditt» står på NAVs brukerside, men finnes ikke i gjeldende lov eller forskrift; forskrift 20.06.2026 nr. 1341 §§ 4-7 er opphevet ved FOR-2026-08-17-1633. Lovordlyden er «forhindret fra å arbeide», ikke «forhindret fra eget arbeid». |
| Funn lagret i | Fil 68; data/qa-log.md. |
| Kilder | lovdata.no/lov/1997-02-28-19 (§ 15-4, § 15-5); nav.no/overgangsstonad-enslig; lovdata.no/dokument/SF/forskrift/2026-06-25-1363 (endringsnotiser) |

### 2.8 Trygderettens praksis om særlig tilsyn — ÅPENT

| | |
|---|---|
| Spørsmål | Hvordan vurderer Trygderetten kravet om særlig tilsyn (§ 15-5 fjerde ledd), inkludert barn under utredning uten diagnose? |
| Hvorfor viktig | Avgjør hvor streng praksisen er rundt legedokumentasjon og arbeidsforhindring; direkte betydning for Mari-caset og fila 65/67. |
| Kilder forsøkt | Lovdata (lover/forskrifter), NAV-brukerstoff; praksisdatabaser ikke hentet i denne etappen. |
| Siste forsøk | 30.08.2026 |
| Anbefalt neste metode | Trygderettens egne avgjørelser (trygderetten.no/domstol.no), NAVs praksisnotater og rundskriv; begrens søket til overgangsstønad og særlig tilsyn. |

### 2.9 Nytt barn for gammel mottaker (scenario G) — ÅPENT

| | |
|---|---|
| Spørsmål | Hvilket regelverk og hvilke betingelser gjelder når en mottaker i overgangsgruppen får nytt barn (her: 2027) og søker på nytt? |
| Hvorfor viktig | Forskriften gir overgangsstatus, men tolkningen av ny vurdering/nytt barn i praksis er ikke verifisert; dette er det eneste scenarioet i fil 68s scenario-motor som ikke kan rutes helt. |
| Kilder forsøk | FOR-2026-06-25-1361 (fulltekst); NAVs brukerside gir ikke svaret. |
| Siste forsøk | 30.08.2026 |
| Anbefalt neste metode | NAV-rundskriv og samarbeidspartnersider om overgangsregler; eventuell skriftlig avklaring med NAV. |

## 3. Gamle NAV-sider: klassifisering (sammendrag)

| Side | Status | Kommentar |
|---|---|---|
| nav.no/overgangsstonad-enslig | BLANDET / MÅ LESES MED FORBEHOLD | Dekker både nye saker og overgangssaker. «Minst 60 prosent» og «andre kan ta vare på barnet» er brukerstoff uten støtte i gjeldende lov/forskrift; avkortingslisten (inkl. AAP) og dokumentasjonskravene er verifiserte. |
| NAVs side om tidligere regelverk | OVERGANGSSAKER / GAMMELT REGELVERK | Korrekt for mottakere per 30.6.2026; skal ikke brukes for nye søkere. |
| nav.no/barnetilsyn-enslig | NYTT REGELVERK | Oppdaterte satser fra 1.1.2026; AAP teller i 6 G-vurderingen. |

Full kontroll ligger i fil 68 (kildetabell og kildekonfliktgjennomgang).

## 4. Kilder

| Kilde | URL | Lest |
|---|---|---|
| FOR-2026-06-25-1361 (fulltekst) | lovdata.no/dokument/SF/forskrift/2026-06-25-1361 | 30.08.2026 |
| Endringsforskrift FOR-2026-08-17-1633 | lovdata.no (endringsnotiser) | 30.08.2026 |
| Folketrygdloven §§ 15-4, 15-5, 15-9, 15-10, 15-13, 11-27 | lovdata.no/lov/1997-02-28-19 | 30.08.2026 |
| Lov 2025-06-20-40 | lovdata.no/lov/2025-06-20-40 | 30.08.2026 |
| NAV overgangsstønad | nav.no/overgangsstonad-enslig | 30.08.2026 |
| NAV barnetilsyn enslig | nav.no/barnetilsyn-enslig | 30.08.2026 |
| Husbanken inntektsgrunnlag | husbanken.no/person/bostotte/inntektsgrunnlaget/ | 30.08.2026 |
| Skatteetaten barnebidrag | skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/familie-og-helse/barn/barnebidrag/ | 30.08.2026 |
