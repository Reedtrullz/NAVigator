# LOKAL TILGANGSMODELL OG DISCOVERY-PROTOKOLL V1

**Task ID:** NAV-EXPLORE-LOCAL-ACCESS-DISCOVERY-PROTOCOL-V1
**Dato:** 09.09.2026
**Foreldretasker:** [71-kommunekartlegging-psykisk-helse-sample-v1](71-kommunekartlegging-psykisk-helse-sample-v1.md) / [72-18-23-aar-lokal-routing-klasse-4-6](72-18-23-aar-lokal-routing-klasse-4-6.md)
**Artifacts:** `data/access-unclear-targets-v1.json`, `data/local-access-verification-v1.json`, `data/local-service-discovery-protocol-v1.json`

## 1. HVORFOR DENNE OPPGAVEN

Dybdikartleggingen i fil 72 benyttet en trinnvis discovery-strategi som gjenopprettet 18/20 uklare rutingceller (90 %) i 12-kommuneutvalget. Etter den kartleggingen sto 9 konkrete tjenester igjen med `access_clear = no` eller partial: tjenestene var dokumentert som relevante, men den offentlige informasjonen viste ikke tydelig hvordan en innbygger faktisk kommer inn i tjenesten.

Denne oppgaven var en avgrenset oppfølging: gjenopprett tilgangen i disse 9 cellene med samme protokoll, og formaliser protokollen som en reproduserbar discovery-kontrakt for fremtidig bruk.

Task lock (`TASK-LOCK-LOCAL-ACCESS-DISCOVERY-V1.json`) frøs scope-et: ingen nye kommuner, ingen produktlogikk, ingen nasjonal juss, ingen kontakt med kommunene. All research er level 0-2 mot offentlige kommunale nettsider, hentet 09.09.2026.

## 2. FRØSTE TARGETS (T1-T9)

| ID | Kommune | Tjeneste | Sentralitet | Utfordring |
|----|---------|----------|-------------|------------|
| T1 | Alta | Psykisk helse og rus (voksentilbud, fire tjenester) | 4 | Inntaksløp per tjeneste ikke detaljert; Tjenestekontor dokumentert som veiledningsinngang |
| T2 | Alta | Lavterskelteam | 4 | Tilgangsfelt manglet i grunnkartleggingen |
| T3 | Steinkjer | Kommunepsykologen | 4 | Uklar om tjenesten tar imot pasienter i det hele tatt |
| T4 | Ulstein | Teneste for psykisk helse og rus | 4 | Søknadsvei ikke kartlagt |
| T5 | Ulstein | Kommunepsykolog (interkommunal Ulstein/Sande) | 4 | Uklar målgruppe og inngang |
| T6 | Ørland | Ambulant ungdomsteam | 4 | Inngangsvilkår ikke dokumentert |
| T7 | Ørland | Helsestasjon for ungdom | 4 | Drop-in-tider ikke kartlagt |
| T8 | Askvoll | Psykisk helse- og rusteneste for vaksne | 4 | Tilgangsfelt manglet i grunnkartleggingen |
| T9 | Hasvik | Helsesykepleier (helsestasjon/skolehelsetjeneste) | 4 | Bokvei for ikke-skolegående unge uklar |

Target-listen ble frøst i `data/access-unclear-targets-v1.json` før research startet, generert programmatisk fra fil 72 sitt datasett via `data/build_access_targets.py`.

## 3. RESULTAT PER TARGET

| ID | Utfall | Kanonisk tilgang | Self-referral | Route confidence | Avgjørende bevis (sitat) |
|----|--------|------------------|---------------|------------------|--------------------------|
| T1 | RESOLVED | DIRECT_PHONE, DIRECT_EMAIL (Tjenestekontoret) | CONDITIONAL | ROUTE_FULLY_VERIFIED | «For veiledning - ta kontakt med Tjenestekontoret vårt» |
| T2 | RESOLVED | DIRECT_PHONE, DIRECT_EMAIL | YES | ROUTE_FULLY_VERIFIED | «Du trenger ingen henvisning, og en digital kartlegging danner grunnlaget for en avklaringssamtale» |
| T3 | RESOLVED | OTHER_PROFESSIONAL_REFERRAL, DIRECT_EMAIL | NO | ROUTE_EXISTENCE_ONLY | «Det er for tiden ikke kapasitet til å tilby avklaringssamtaler og/eller behandling av pasienter» |
| T4 | RESOLVED | APPLICATION_FORM (skjema ULS097), DIRECT_PHONE, GP_REFERRAL, OTHER_PROFESSIONAL_REFERRAL | YES | ROUTE_FULLY_VERIFIED | «Bruk skjema for helse- og omsorgstenester. Du kan også ringe» |
| T5 | RESOLVED | OTHER_PROFESSIONAL_REFERRAL | NO | ROUTE_EXISTENCE_ONLY | «Hovudoppgåva ... er førebygging og helsefremmande arbeid» (systemrettet, ingen pasientinntak) |
| T6 | RESOLVED | DIRECT_PHONE, DIRECT_EMAIL, OTHER_PROFESSIONAL_REFERRAL | CONDITIONAL | ROUTE_FULLY_VERIFIED | «Hvis disse tjenestene allerede er forsøkt ... kan Ambulant ungdomsteam kontaktes» (steg 2-tjeneste) |
| T7 | RESOLVED | DIRECT_DROPIN, DIRECT_PHONE | YES | ROUTE_FULLY_VERIFIED | Publiserte drop-in-åpningstider (fast datoformat, to ukers rytme) + tjenestekoblet telefon |
| T8 | RESOLVED | DIRECT_PHONE (navngitte ansatte) | YES | ROUTE_FULLY_VERIFIED | «Du treng ikkje tilvising for å få hjelp» |
| T9 | PARTIALLY_RESOLVED | DIRECT_DROPIN, DIRECT_PHONE | CONDITIONAL | ROUTE_ACCESS_PARTIAL | Skoleelever: kontortid på skolene. Ikke-skolegående 19-åring: eksplisitt bokningsvei ikke publisert |

Alle sitater er verbatim fra hver URL med hentedato 09.09.2026, jf. ACCESS-E5.

## 4. HOVEDTALL

- **Access-recovery: 8/9 = 89 %** (8 RESOLVED, 1 PARTIALLY_RESOLVED, 0 PUBLIC_DATA_EXHAUSTED)
- **Route confidence:** 6 ROUTE_FULLY_VERIFIED (T1, T2, T4, T6, T7, T8), 1 ROUTE_ACCESS_PARTIAL (T9), 2 ROUTE_EXISTENCE_ONLY (T3, T5)
- **Self-referral:** 3 YES (T2, T4, T8), 3 CONDITIONAL (T1, T6, T9), 2 NO (T3, T5), 1 uavklart del (T9 for ikke-skolegående)
- T3 og T5 ble negativt lukket: systemrettede tjenester uten pasientinntak. Dette er verifiserte funn, ikke funnfeil.
- Discovery-dybde: L0-L1 lukket 5 (T2, T3, T5, T6, T7), L2 lukket 3 (T1 via Tjenestekontor-lenken, T4 via skjema-URL ULS097, T8 via foreldresiden «Du treng ikkje tilvising»)
- Teknikk: KNOWN_PAGE_CONTENT 5, NAVIGATION_LINK 3

## 5. DISCOVERY-LADDEREN

| Level | Navn | Når den brukes | Teknikker |
|-------|------|-----------------|-----------|
| 0 | KNOWN_SERVICE_URL | Hent allerede kartlagt tjenesteside, skann fulltekst for tilgangsmarkører | KNOWN_PAGE_CONTENT |
| 1 | MUNICIPALITY_SERVICE_CATALOG | Kommunens tjenestekatalog under psykisk helse/ungdom/voksen | KNOWN_PAGE_CONTENT |
| 2 | SERVICE_DESCENDANTS | Følg underlenker: slik søker du, kontakt oss, team-sider, skjema | NAVIGATION_LINK |
| 3 | STRUCTURED_MUNICIPALITY_SEARCH | Sitemap, intern søkemotor, dokumentindeks | SITE_SEARCH, SITEMAP |
| 4 | INTERMUNICIPAL_DISCOVERY | Vertskommune, IKS, samarbeid, partnerkommune | INTERMUNICIPAL_CHAIN |
| 5 | OFFICIAL_EXTERNAL_ENTRY | Helsenorge-lokalinfo, offisielle interkommunale porter | OFFICIAL_EXTERNAL_PORTAL |

Fulltekster fra alle hentede sider er cachet i `/tmp/access_l0/T1..T9.txt` (sesjonsspesifikt, ikke i repo).

## 6. PROTOKOLLKONTRAKTEN

Protokollen er formalisert i `data/local-service-discovery-protocol-v1.json`. Hovedelementene:

**Tilgangsbevisregler (ACCESS-E1 til E5):**
- **ACCESS-E1:** `access_clear = yes` krever eksplisitt offentlig bevis for minst ett av: ta kontakt, kontaktskjema, telefon koblet til inntak, digital selvhenvendelse, drop-in, eksplisitt henvisningskrav, eksplisitt intern inngang.
- **ACCESS-E2:** Generell switchboard/telefon eller kontaktblokk på bunnen er ikke automatisk bevis. Den teller bare når siden knytter den til tjenesten (navngitte ansatte, inntakslinje, booking).
- **ACCESS-E3:** Self-referral er eget felt (YES/NO/CONDITIONAL/UNCLEAR) og skal aldri utledes av at et telefonnummer finnes. Direkte kontakt med senere faglig vurdering = CONDITIONAL, ikke ubetinget selvhenvendelse.
- **ACCESS-E4:** Skill «kan kontakte tjenesten» fra «kan få behandling uten videre vurdering».
- **ACCESS-E5:** Alle sitater verbatim fra beholdt URL, med hentedato og eventuell publisert faglig endringsdato.

**Stop states:**
- ACCESS_VERIFIED - tilgangsmetode dokumentert med gyldig bevis
- REFERRAL_VERIFIED - eksplisitt henvisnings-/søknadsmodell dokumentert (inkluderer verifiserte negative lukk: systemrettet tjeneste, ingen pasientinntak)
- PUBLIC_DATA_EXHAUSTED - alle preregistrerte nivåer sjekket uten å etablere tilgang. Ingen uendelig søking.

**Route confidence-modell (ingen probabilistiske scores):**
- ROUTE_FULLY_VERIFIED - tjeneste + målgruppe + tilgang + kontakt dokumentert
- ROUTE_ACCESS_PARTIAL - tjeneste + målgruppe dokumentert, tilgang bare delvis
- ROUTE_EXISTENCE_ONLY - tjeneste finnes, men målgruppe/tilgang utilstrekkelig dokumentert
- ROUTE_UNVERIFIED - ingen verifisert rute

## 7. USIKKERHETSKONTRAKT

Når protokollen kjøres i et produksjonslager skal output bruke faste norske varianter:

1. **VERIFIED_ROUTE:** «Jeg fant et kommunalt/interkommunalt tilbud som ser relevant ut. Du kan ...»
2. **SERVICE_FOUND_ACCESS_UNCLEAR:** «Jeg finner et relevant tilbud, men den offentlige informasjonen gjør det ikke klart hvordan du kommer inn i tjenesten.»
3. **NO_VERIFIED_ROUTE_AFTER_PROTOCOL:** «Jeg finner ikke et verifisert lokalt tilbud i de offentlige kildene jeg har kontrollert. Det betyr ikke nødvendigvis at tilbudet ikke finnes.»

**False-NO-MATCH-regel:** NAV Explore må aldri uttale «kommunen har ikke tilbud» fordi et første søk ga 0 treff. NO_LOCAL_MATCH er kun gyldig etter at discovery-protokollen er kjørt til en terminal state. Empirisk grunnlag: 18/20 problemceller ble gjenopprettet med full protokoll i foreldretasken, og 0 tilsynelatende service-gaps overlevde full protokoll i 12-kommuneutvalget.

Dokumentert fallback (f.eks. fastlege) kan kun legges til når eksisterende kunnskapsbase støtter den.

## 8. GJENVÆRENDE GAP

- **T9 Hasvik:** Bokvei for ikke-skolegående 19-åring er upublisert. Drop-in/telefon dekker skoleelever; helsesykepleiers telefon er logget, men eksplisitt booking for målgruppen mangler. Sitemap var tom (0 bytes, logget som avvist kilde).
- **T1 Alta:** Inntaksløp per undertjeneste (Lavterskeltjenesten, Samtaletjenesten, ROP, Boligtjenesten) er ikke detaljert publisert; Tjenestekontoret er verifisert veiledningsinngang, men per-tjeneste-intak krever videre paging eller kontakt.
- **T3 Steinkjer / T5 Ulstein:** Tjenestenes status er negativt lukket (systemrettet / ingen pasientkapasitet). Eliteligibility for fremtidig endring må følges opp ved kildesjekk ved behov, ikke i denne tasken.

## 9. ARTIFACTS OG QA

| Fil | Innhold | Validering |
|-----|---------|-----------|
| `data/access-unclear-targets-v1.json` | 9 frøste target-er med provenance fra fil 72 | jsonschema OK |
| `data/local-access-verification-v1.json` | before/after-lag: tilgang, self-referral, evidence, search-log per target | jsonschema OK |
| `data/local-service-discovery-protocol-v1.json` | Protokoll: nivåer, bevisregler, stop states, confidence-modell, usikkerhetskontrakt | jsonschema OK |

Bygg- og fetch-skript (`data/build_access_targets.py`, `data/access_fetch_level0.py`, `data/access_level2.py`, `data/access_level2b.py`, `data/access_askvoll.py`, `data/build_access_verification.py`) beholdes som provenance. Schema-filene ligger ved siden av JSON-ene.

## 10. PRODUKTIMPLIKASJONER (IKKE IMPLEMENTERT)

Denne tasken leverer kunnskap og kontrakt, ikke runtime-endringer:

1. Routinglaget kan fremover bruke `access_clear`, `canonical_access_methods`, `self_referral` og `route_confidence` direkte fra verifikasjonslaget for de 9 target-ene.
2. Discovery-protokollen er klar for implementering som crawler/kontrakt i runtime når det er godkjent som egen etappe.
3. Usikkerhetsvariantene (seksjon 7) er designet for brukergrensesnittet, men er ikke wiret inn i produktlogikk.
4. Ingen eksisterende filer (71, 72) er omskrevet; verifikasjonen ligger som et separat update-lag over grunnkartleggingen.
