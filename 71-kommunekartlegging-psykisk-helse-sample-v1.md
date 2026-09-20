# Kommunekartlegging psykisk helse: representativt utvalg V1

**Task ID**: NAV-EXPLORE-MUNICIPAL-MENTAL-HEALTH-SAMPLE-V1
**Dato**: 08.09.2026 (hentedato for alle live-verifiserte kilder)
**Status**: MUNICIPAL_SAMPLE_V1_COMPLETE
**Maskinlesbart grunnlag**: [data/municipal-mental-health-sample-v1.json](data/municipal-mental-health-sample-v1.json) (24 kommuner, 75 tjenester)
**Schema**: [data/municipal-mental-health-sample-v1.schema.json](data/municipal-mental-health-sample-v1.schema.json)

---

## 1. Metode

Utvalget ble frosset FØR tjenestekartleggingen startet (se [data/municipality-sample.json](data/municipality-sample.json)). Kommuneutvalget bygger på SSBs sentralitetsklassifikasjon (KLASS 128 / korrespondansetabell 131, dato 2024-01-01, hentet live fra data.ssb.no 08.09.2026). Fire kommuner per sentralitetsklasse (1–6), med geografisk spredning og minst 18 av 24 kommuner som ikke var kartlagt tidligere. Trondheim inngår som kjent ankerkommune.

Kartleggingen registrerte per tjeneste: målgruppe og alder (eksakt offentlig formulering bevart), tilgangsmåte (selvhenvisning), kostnad, tilbudstype, diagnostikk, akutthåndtering, kontaktmetode og kilde med URL. Ventetid ble kun registrert dersom kommunen selv publiserer den. Ingen kommuner ble kontaktet. Ingen ventetider ble estimert.

Datainnsamlingen ble gjort av to subagenter (GPT-5.6-Luna) med 12 kommuner hver, mot det frosne samplet. Funnene ble deretter slått sammen og QA-verifisert mot schema ([data/merge-qa.py](data/merge-qa.py)) og med URL-sjekk ([data/url_check.py](data/url_check.py)).

## 2. Utvalg

| Sentralitetsklasse | Kommuner |
|---|---|
| 1 (mest sentrale) | Oslo, Bærum, Lillestrøm, Lørenskog |
| 2 | Bergen, Trondheim, Stavanger, Hamar |
| 3 | Arendal, Haugesund, Gjøvik, Bodø |
| 4 | Alta, Steinkjer, Farsund, Ulstein |
| 5 | Sør-Varanger, Ørland, Sauda, Tynset |
| 6 (minst sentrale) | Hasvik, Osen, Askvoll, Bykle |

Geografisk spredning: Østlandet (6), Vestlandet (6), Midt-Norge (5), Nord-Norge (5), Sørlandet (2). Previously researched: 2 (Oslo som delvis dekket, Trondheim som anker). Newly researched: 22.

## 3. Hovedfunn

1. **75 verifiserte lokale tjenester** fordelt på 24 kommuner (3–3,5 per kommune). Ingen kommune manglet helt verifisert lokal inngang (service-source coverage 24/24).
2. **Selvhenvisning er hovedinngangen der tilgangsmåten er dokumentert**: 42/75 tjenester kan kontaktes direkte, 5 via skjema, 28 er uklare. De 28 uklare er fordelt over hele landet, men konsentrert i små kommuner.
3. **Kostnad er gratis der det opplyses** (45/75), men 30/75 har ukjent kostnad i offentlig materiale.
4. **Ingen av de 75 tjenestene publiserer ventetid** i offentlig materiale (0/75). Dette er et systematisk public-data gap, ikke et tegn på fravær av kø.
5. **Aldersgrensene varierer sterkt** mellom nabokommuner — HFU spenner fra «13–20 år» (Sauda, Steinkjer) via «13–24» (Bodø) til «til og med 25» (Hamar, Bykle, Alta). RPH-aldersgrenser varierer også (16+, 18+ eller ukjent).
6. **RPH er funnet i 10/24 kommuner** (8 OWN, 1 INTERMUNICIPAL, 1 UNCLEAR med tilbud), mens 14 kommuner har ingen funnet RPH-side. De fleste NO_RPH_FOUND-kommunene er i klasse 4–6.
7. **Kommunepsykolog er sjelden en direkte innbyggertjeneste**: 2/24 kommuner dokumenterer psykolog direkte til innbyggere (Sør-Varanger, Sauda), 11 kun via team, 4 embedded intern, 1 interkommunalt, 6 har ingen offentlig dokumentasjon.
8. **Routing for 19–22 år er svakest**: scenario C og D klarer seg dårligere enn A og B, spesielt i klasse 4–6.

## 4. Sentralitetsforskjeller (eksplorativt, ikke kausalt)

| Klasse | Tjenester totalt | Snitt per kommune | Direkte-tilgang | RPH tilgjengelig | psy direkte | Klare/multiple ruter (av 16 scenario-celler) | Public-data completeness |
|---|---|---|---|---|---|---|---|
| 1 | 12 | 3,0 | 10 | 2 | 1 | 10 | 0,83 |
| 2 | 14 | 3,5 | 12 | 4 | 1 | 16 | 0,79 |
| 3 | 12 | 3,0 | 9 | 1 | 0 | 10 | 0,75 |
| 4 | 12 | 3,0 | 5 | 1 | 0 | 3 | 0,33 |
| 5 | 13 | 3,25 | 8 | 1 | 0 | 10 | 0,54 |
| 6 | 12 | 3,0 | 3 | 0 | 0 | 6 | 0,08 |

Mønstre i dette utvalget (ikke konklusjoner om årsak):

- **Antall tjenester per kommune er nærmest konstant** (3–3,5) på tvers av sentralitet. Forskjellen ligger ikke i om kommunen har psykisk helsetjenester, men i **hvor godt de er dokumentert** og i **hvem som kan kontaktes direkte**.
- **Direkte-tilgang og public-data completeness faller med sentralitet** — klasse 1–3 ligger på 75–83 % completenes, klasse 4 på 33 % og klasse 6 på 8 %.
- **RPH forsvinner i små kommuner**: 0 RPH-funn i klasse 6. Disse kommunene er trolig avhengige av interkommunale eller helseforetaksdrevne tilbud som ikke er lett synlige fra kommunens egen side.
- Klasse 4 bryter mønsteret på routability (kun 3/16 klare/multiple) på grunn av Alta og Ulstein, hvor offentlig informasjon er tynt dokumentert.

## 5. Aldersvariasjon (faktiske formuleringer)

HFU (helsestasjon for ungdom) som eksempel på variasjon:

| Kommune | Offisiell formulering |
|---|---|
| Oslo | «12–24 år» |
| Bærum | «13–23 år» |
| Bergen | «13–23 år; til og med 25 år i Bergenhus/Årstad» |
| Trondheim | «13 år til og med 21 år» |
| Stavanger | «ungdom fra 16 til og med 20 år, og alle elever i videregående skole» |
| Hamar | «fra 13 til og med 25 år» |
| Arendal | «ungdom ut året du fyller 24 år» |
| Gjøvik | «ungdom og studenter opp til 25 år» |
| Bodø | «ungdom fra 13 til 24 år» |
| Alta | «13–25 år» |
| Steinkjer | «13–20 år; høgskolestudenter opp til 25 år» |
| Sør-Varanger | «13–25 år» |
| Sauda | «ungdom mellom 13–20 år» |
| Tynset | «ungdom mellom 13–25 år» |
| Bykle | «13–25 år» |
| Osen | eksakt aldersgrense ikke offentlig oppgitt |

9 av 75 tjenester mangler eksplisitt aldersinformasjon. Rask psykisk helsehjelp varierer også: «over 16 år (18 år i noen bydeler)» i Oslo, «over 18» i Bærum, «16–23» i Bergen, «18+» i Trondheim/Bodø/Hamar, «voksne» i Stavanger.

## 6. Selvhenvisning

Fordeling på 75 tjenester: **direkte 42**, **skjema 5**, **unclear 28**.

Hovedmønster: helsestasjoner, skolehelsetjeneste og lavterskeltilbud i de største kommunene dokumenterer direkte tilgang. Kommunale psykisk helseteam for barn/unge er hyppigst «via fastlege, skole, helsestasjon eller barnevern». De 28 uklare tilfellene er konsentrert der kommunen beskriver tilbudet uten å oppgi kontaktrute — dette er et public-data gap, ikke nødvendigvis en tjenestegrense.

## 7. RPH (rask psykisk helsehjelp)

| Klassifisering | Antall kommuner |
|---|---|
| OWN_RPH | 8 |
| INTERMUNICIPAL_RPH | 1 |
| NO_RPH_FOUND | 14 |
| UNCLEAR | 1 |

RPH finnes som kommunalt tilbud i de største kommunene i utvalget (Oslo, Bærum, Bergen, Trondheim, Stavanger, Hamar, Bodø, Gjøvik), men aldri i klasse 5–6 i dette samplet. Aldersgrensene varierer (se seksjon 5). Dette samvarer med nasjonal dokumentasjon om at RPH primært er et voksen- og ungdomstilbud med lokal variasjon — ingen POTENTIAL_LOCAL_NATIONAL_CONFLICT ble registrert.

## 8. Kommunepsykolog

| Leveringsmodell | Antall kommuner |
|---|---|
| direkte til innbyggere | 2 |
| via team | 11 |
| embedded intern | 4 |
| interkommunalt | 1 |
| ingen offentlig dokumentasjon | 6 |

Begrepet «kommunepsykolog» er **ikke en standardisert tjeneste**. I Sør-Varanger og Sauda er psykologen eksplisitt tilgjengelig for innbyggere (barn/unge). De fleste andre kommunene leverer psykolog som en del av et team (psykisk helse og rus, familieteam, ungdomsteam). Dette bekrefter fil 25s hovedfunn og generaliserer det til et representativt utvalg.

## 9. Scenario-basert routability

Klassifisering per kommune (24 kommuner per scenario):

| Scenario | CLEAR | MULTIPLE | UNCLEAR | NO_MATCH |
|---|---|---|---|---|
| A: 14-åring, milde angstplager | 6 | 13 | 5 | 0 |
| B: 17-åring, hjelp uten foreldre/fastlege | 12 | 6 | 5 | 1 |
| C: 19-åring, moderate plager | 5 | 4 | 11 | 4 |
| D: 22-åring, rask lavterskelhjelp | 7 | 2 | 3 | 12 |

Mønster: barn og yngre ungdom (A, B) har best ruting — skolehelsetjeneste/HFU finnes over hele landet og har ofte direkte tilgang. Voksne 19–22 (C, D) får stadig LOCAL_ROUTING_UNCLEAR eller NO_MATCHING_LOCAL_SERVICE_FOUND, spesielt i klasse 5–6, hvor verken RPH, psykolog eller lavterskeltilbud er dokumentert for denne aldersgruppen. Scenario D har 12/24 NO_MATCH — drevet av små kommuner uten dokumentert voksen-lavterskeltilbud.

## 10. Kunnskapshull (gap-klassifisering)

### PUBLIC-DATA GAP (dominerende)

- Ventetid publisert av 0/75 tjenester — systematisk, ikke tilfeldig.
- 28/75 tjenester med uklar tilgangsmåte; 30/75 med ukjent kostnad.
- 9/75 tjenester uten aldersgrense.
- RPH i klasse 4–6: usikkert om tilbudet finnes interkommunalt eller via helseforetak, men det er ikke synlig fra kommunens side.
- 6/24 kommuner uten offentlig dokumentasjon av psykologlevering.

### KNOWLEDGE GAP

- Detaljerte åpningstider og besøksadresser for flere småkommunetjenester.
- Kontaktinformasjon for interkommunale RPH-tilbud (hvilket helseforetak, hvilken inngang).
- Presise aldersgrenser for 9 tjenester der formuleringene er «barn og unge» uten tall.

### SERVICE GAP (mulig, ikke konkludert)

- Voksen-lavterskeltilbud (scenario D) ser ut til å mangle i flere klasse 5–6-kommuner, men fravær av dokumentasjon er ikke bevis for fravær av tjeneste.
- RPH ser ut til å mangle i klasse 6, men interkommunale ordninger kan eksistere uten synlighet på kommunens egen side.

## 11. Implikasjoner for beslutningsstøtte

1. **Routing kan ikke anta at «lavterskel» betyr direkte tilgang** — 28/75 tjenester har uklar tilgangsmåte selv om navnet antyder lavterskel.
2. **HFU er den mest pålitelige inngangen for 13–24-åringer** — dokumentert direkte tilgang i nesten alle kommuner med HFU, men aldersgrensen må slås opp lokalt.
3. **Scenario C/D krever lokal spørring eller nasjonal fallback** — NAV Explore må ha en trygg generisk rute (fastlege, 116 123, helsenorge) når lokal ruting er uklar.
4. **Kommunepsykolog må modelleres som team-tilgang**, ikke som individuell psykologtime, i de fleste kommuner.
5. **Ventetid må hentes fra helseforetak eller via brukerrapportering** — kommunale sider publiserer det ikke.

## 12. QA

- 24/24 kommuner komplett (municipal coverage).
- Sentralitetsfordeling 4/4/4/4/4/4 verifisert.
- Unike kommunenummer verifisert.
- Schema-validering via manuell walk + [data/merge-qa.py](data/merge-qa.py): 0 problemer.
- URL-sjekk: 66 unike URL-er, alle levende etter QA-erstatning. 5 døde URL-er (Bykle organisasjonskart-PDF, Alta parenthood-nyhet, Alta HFU-detaljside, Lørenskog psykisk helse-oversikt, Osen stillingsannonse) ble erstattet med nærmeste levende offisielle side som fortsatt støtter påstanden; dette er notert per tjeneste i JSON-filene.
- Referral-felt konsistent (49/75 komplette, resten bevisst unclear — ikke blank).
- Aldersfelt konsistent: maskinlesbare felt supplerer aldri originalteksten.
- Ventetid: 0/75 publisert; ingen inference registrert (alle NOT_PUBLISHED eller null).
- Ingen endringer i filer 25/26/28b.
- Crossreference JSON ↔ markdown: dekker samme 24 kommuner og 75 tjenester.

## 13. Kryssreferanser

- Nasjonal oversikt kommunale tjenester: [25-kommunale-psykiske-tjenester-barn-unge](25-kommunale-psykiske-tjenester-barn-unge.md)
- Beslutningsmatrise: [26-beslutningsstotte-hvor-henvende-seg](26-beslutningsstotte-hvor-henvende-seg.md)
- Routing 18–20 år: [28b-18-20-aar-routing](28b-18-20-aar-routing.md)
- Kunnskapshull i beslutningsstøtten: [28c-beslutningsstotte-gaps](28c-beslutningsstotte-gaps.md)
- Trondheim-pilot: [70-lokalt/trondheim/README](70-lokalt/trondheim/README.md)

## 14. Avgrensninger

Utvalget på 24 kommuner er eksplorativt, ikke statistisk representativt for landet. Å konkludere at «lav sentralitet forårsaker dårligere tilbud» er ikke tillatt ut fra dette materialet — mønsterne beskriver dette utvalget. Kartleggingen er et øyeblikksbilde per 08.09.2026 og dekker kun hva kommunene selv publiserer på offisielle sider. Interkommunale tilbud, helseforetaksdrift og uformelle ordninger kan eksistere uten synlighet her.
