# 18-23-årsrouting i kommuner med lavere sentralitet (klasse 4-6)

**Task ID**: NAV-EXPLORE-18-23-LOCAL-ROUTING-GAP-V1
**Dato**: 08.09.2026
**Status**: 18_23_LOCAL_ROUTING_GAP_V1_COMPLETE
**Forelder**: [71-kommunekartlegging-psykisk-helse-sample-v1](71-kommunekartlegging-psykisk-helse-sample-v1.md) (NAV-EXPLORE-MUNICIPAL-MENTAL-HEALTH-SAMPLE-V1)

## 1. Formål og avgrensning

V1-kartleggingen viste at beslutningsstøtten sviktet mest for unge voksne i sentralitetsklasse 4-6. Denne etappen forklarer hvorfor: For en 18-23-åring i en mindre sentral kommune - finnes det faktisk en lokal inngang til psykisk helsehjelp, og kan en vanlig innbygger forstå hvordan den brukes ut fra offentlig informasjon?

Dette er et **målrettet problemsample**, ikke et representativt nasjonalt utvalg. Resultatene kan ikke generaliseres. Ingen nasjonal juss ble åpnet, ingen kommuner ble kontaktet, ingen V1-artefakter ble endret, ingen produktlogikk ble rørt.

## 2. Metode

- Utvalget (12 kommuner) ble fryst i «data/18-23-routing-target-sample.json» før dyp research. Ingen kommune ble byttet underveis.
- Kildeletting gikk dypere enn landingssiden: kommunal tjenestekatalog, psykisk helse/rus-sider, HFU/ungdomshelsetjeneste, RPH, kommunepsykolog/team, voksen psykisk helse, interkommunale samarbeid, vertskommunesider, sitemap-søk. Hver kommune har komplet søkelogg med seks obligatoriske innganger (search_log: alle seks true for 12/12).
- Verifisering skjedde med direkte sidehenting og kontekstsøk (page_grep.py, links_grep.py, sitemap-grep); r.jina.ai ble brukt som fallback der Cloudflare blokkerte curl (Fosen Helse). Alle 12 kommuners sentrale URL-er var live ved henting 08.09.2026.
- Klassifisering skjer per scenario (C: 19 år, moderate plager; D: 22 år, rask lavterskelhjelp) etter protokollen i oppgavespesifikasjonen. Alderpåstander er kildebaserte (covers_age_19 / covers_age_22 per tjeneste).
- Maskinlesbar konsolidering: merge-deep-qa.py → «data/18-23-local-routing-gap-v1.json», QA: 0 problems.

## 3. Frossent utvalg

| Klasse | Kommune | V1 scenario C | V1 scenario D |
|---|---|---|---|
| 4 | Alta | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 4 | Steinkjer | LOCAL_ROUTING_UNCLEAR | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 4 | Farsund | LOCAL_ROUTING_UNCLEAR | LOCAL_ROUTING_UNCLEAR |
| 4 | Ulstein | LOCAL_ROUTING_UNCLEAR | LOCAL_ROUTING_UNCLEAR |
| 5 | Sør-Varanger | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 5 | Sauda | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 5 | Tynset | LOCAL_ROUTING_UNCLEAR | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 5 | Ørland | CLEAR_LOCAL_ROUTE | CLEAR_LOCAL_ROUTE |
| 6 | Osen | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 6 | Askvoll | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 6 | Bykle | NO_MATCHING_LOCAL_SERVICE_FOUND | NO_MATCHING_LOCAL_SERVICE_FOUND |
| 6 | Hasvik | CLEAR_LOCAL_ROUTE | CLEAR_LOCAL_ROUTE |

Ørland og Hasvik fungerer som kontroller (V1 CLEAR). De 10 øvrige C/D-scenariene per behovsnivå var problemscenarier: 10 for C, 10 for D, 20 totalt (4 av 24 V1-celler i utvalget var kontroller).

## 4. Hovedfunn

**Routing recovery rate: 18/20 = 90 %.** Av de 20 V1-problemscenariene ble 18 reklassifisert til VERIFIED_LOCAL_ROUTE etter dyp leting. Ni av ti V1-svikt var altså informasjons-/oppdagelseshull, ikke verifiserte tjenestehull.

- Scenario C: V1 hadde 10 problemscenarier; 9 recovered til VERIFIED_LOCAL_ROUTE, 1 forblir VERIFIED_LOCAL_SERVICE_ACCESS_UNCLEAR (Ulstein).
- Scenario D: V1 hadde 10 problemscenarier; 9 recovered til VERIFIED_LOCAL_ROUTE, 1 forblir SPECIALIST_GATEWAY (Ulstein).
- Etter full søkeprotokoll finnes det **0** kommuner i utvalget med NO_LOCAL_MATCH_FOUND og **0** med INSUFFICIENT_PUBLIC_DATA. Kontrollkommunene beholdt sine clear-ruter.
- Det betyr at «no match» i V1 nesten alltid betydde «ikke funnet på landingssiden», ikke «finnes ikke». Konkret: tjenester ligger i voksen-PHR-tilbud (18+), interkommunale samarbeid, eller på underordnede sider som landingssøket ikke fanget opp.

Endelig klassifisering (12 kommuner):

| Klassifisering | C (19 år) | D (22 år) |
|---|---|---|
| VERIFIED_LOCAL_ROUTE | 11 | 11 |
| VERIFIED_LOCAL_SERVICE_ACCESS_UNCLEAR | 1 (Ulstein) | 0 |
| SPECIALIST_GATEWAY | 0 | 1 (Ulstein) |
| GP_GATEWAY_ONLY / NO_LOCAL_MATCH_FOUND / INSUFFICIENT_PUBLIC_DATA | 0 | 0 |

## 5. Funn per sentralitetsklasse

**Klasse 4 (4 kommuner).** Alta: voksen-PHR-tilbud «Psykisk helse og rus» (over 18 år, fire tjenester, Tjenestekontoret som veiledningsinngang) pluss lavterskelteam dekker begge scenarioene. Steinkjer: HFU 13-20 år (høgskolestudenter til 25) pluss voksen-tilbud for 22-åringen. Farsund: HFU til 25 år og kommunale tilbud gir route for begge. Ulstein er det eneste unntaket: fastlege → Volda DPS er den dokumenterte ruten for 22-åringen (SPECIALIST_GATEWAY), og tilgangsmåten til kommunepsykolog-tilbudet er uklar for 19-åringen.

**Klasse 5 (4 kommuner).** Alle fire recovered. Sør-Varanger: HFU drop-in 13-25. Sauda: HFU 13-20 pluss voksen-tilbud for 22. Tynset: HFU 13-25 og voksen-PHR-sider; FARTT-kommunepsykologen er systemrettet (tar ikke imot henvisninger til utredning/behandling) og teller derfor ikke som direkte rute. Ørland (kontroll): ambulant ungdomsteam 10-20 år, HFU fra 13 uten publisert øvre grense, RPH via Fosen Helse IKS.

**Klasse 6 (4 kommuner).** Alle fire recovered. Osen: skolehelsetjeneste/voksen-tilbud dokumentert; ingen egen HFU-side funnet. Askvoll: HFU 13-20 pluss voksen-tilbud. Bykle: felles HFU med Valle (13-25) partnermodell. Hasvik (kontroll): helsesykepleier 0-20 år og FFR lavterskeltilbud med direkte telefon (78 45 25 59).

## 6. 18-20 år vs 21-23 år

HFU-grensene varierer mye i utvalget: Alta 13-25, Steinkjer 13-20 (studenter til 25), Farsund til 25, Ulstein 0-25, Sør-Varanger 13-25 drop-in, Sauda 13-20, Tynset 13-25, Ørland fra 13 (ingen øvre grense publisert), Askvoll 13-20, Bykle 13-25 (delt med Valle), Hasvik 0-20 (helsesykepleier), Osen ingen HFU-side funnet.

For 19-åringer: 25 av 29 tjenester dekker 19 (covers_age_19 true; 4 unknown). For 22-åringer: 20 av 29 dekker 22, 4 eksplisitt ikke (HFU-er med grense 20: Sauda, Ørland ungdomsteam, Askvoll, Hasvik), 5 unknown (inkludert kommunepsykolog-tilbud der alder ikke er publisert). Døde vinkler gjelder altså ungdomstjenester, ikke voksen-tilbudene.

**Routing cliff 19→22: 0 tilfeller** i utvalget. Ingen kommune har «19 har lokal rute men 22 ikke»: der ungdomstjenesten stopper ved 20, starter voksen-PHR-tilbudet (18+). Cliffet vi så i V1 var ikke et alders-cliff i tjenestene, men et oppdagelses-cliff: voksen-tilbud og interkommunale ruter var ikke synlige i første letting.

## 7. Interkommunale tjenester

Fire kommuner er avhengige av interkommunale relasjoner:

- **Ørland**: RPH leveres av Fosen Helse IKS (Indre Fosen, Åfjord, Ørland) - INTERMUNICIPAL_HOST.
- **Bykle**: felles HFU med Valle - INTERMUNICIPAL_PARTNER.
- **Ulstein**: kommunepsykolog i interkommunalt Ulstein/Sande-opplegg; SSIKT-portal for HFU.
- **Tynset**: FARTT-kommunepsykolog er systemrettet, ikke pasientrettet.

Kommunevis leveringsmodell: 11 MUNICIPAL, 1 INTERMUNICIPAL_HOST (Ørland, på kommunenivå). V1 klassifiserte blant annet Ørland som clear, men uten vertskommune-forbindelsen synlig; deep-dive dokumenterer den.

## 8. Fastlege-gateway

Kun Ulstein ender med gateway-klassifisering: kommunens side peker 22-åringen videre til fastlege og Volda DPS (SPECIALIST_GATEWAY), og ingen klar direkteinngang til det interkommunale kommunepsykolog-tilbudet er publisert (VERIFIED_LOCAL_SERVICE_ACCESS_UNCLEAR for C). De øvrige 11 kommunene har minst én dokumentert direkteinngang (telefon, drop-in eller digital skjema).

## 9. Public-data gaps

Per tjeneste (n=29) er strukturen ofte bra, men tilgangsbeskrivelsen svakest:

| Felt | yes | no |
|---|---|---|
| age_clear | 19 | 10 |
| target_group_clear | 26 | 3 |
| access_clear | 20 | 9 |
| contact_clear | 19 | 10 |
| cost_clear | 19 | 10 |
| service_content_clear | 28 | 1 |

Typiske hull: inntaksløp per tjeneste (hvem kan henvise, kan man selv ringe) er ofte upublisert; kommunepsykolog-tilbud i Steinkjer og Tynset har ikke publisert alder/tilgang; interkommunale ordninger beskrives ofte bare på vertskommunens side.

## 10. Service gaps og konflikter

- APPARENT_SERVICE_GAP etter full protokoll: 0.
- POTENTIAL_LOCAL_NATIONAL_CONFLICT: 0 registrert. Ingen lokale sider ble vurdert som juridisk misvisende.
- Tilgang for voksne (18+) med direkte inngang er dokumentert i 11 av 12 kommuner; det er dette som åpner 21-23-års-routingen.

## 11. Anbefalt uncertainty-wording (forslag, ikke implementert)

Basert på funnene foreslås denne kontrakten for beslutningsstøtten (ikke rullet ut i produktet i denne etappen):

> «Jeg finner ikke et verifisert lokalt lavterskeltilbud i de offentlige kildene jeg har kontrollert. Fastlegen er en dokumentert inngang til videre vurdering.»

Regler bak ordlyden: aldri si «kommunen har ikke tilbud» når kildene bare er ufullstendige; skill eksplisitt mellom verifisert lokal rute, lokal rute med uklar tilgang, fastlege-gateway og spesialist-gateway; og ikke behandle manglende HFU-aldersgrense over 20 som manglende tilbud for unge voksne, siden voksen-tilbudet (18+) ofte er ruten.

## 12. Artifacts og QA

- Maskinlesbart: «data/18-23-local-routing-gap-v1.json» (12 kommuner, 29 tjenester, søkelogg, evidence-sitater, gap-klassifisering) - QA 0 problems.
- Frossent utvalg: «data/18-23-routing-target-sample.json» (fryst før research, ingen substitusjon).
- Byggescript og verifisering: «data/build_deep_a.py», «data/merge-deep-qa.py», «data/page_grep.py», «data/links_grep.py».
- V1-artefakter («data/municipal-mental-health-sample-v1.json», fil 71) er uendret.

## 13. Begrensninger

Problemsample, ikke representativt utvalg. Ett-døgnsøknapp (08.09.2026) - sider endres. Severity-klassifisering er konservativ der kilden ikke spesifiserer. Ventetider er ikke kartlagt (0 tjenester publiserer dette, bekreftet i V1). Direkteinngang er dokumentert fra kilde, ikke testet i praksis.

Se «data/18-23-local-routing-gap-v1.json» for full evidenskjede per kommune og tjeneste.
