# Lokal discovery-generalisering V1

**Task ID:** `NAV-EXPLORE-LOCAL-DISCOVERY-GENERALIZATION-V1`
**Dato:** 2026-09-09
**Status:** `LOCAL_DISCOVERY_GENERALIZATION_PASS`
**Maskinartefakt:** `data/local-discovery-generalization-v1.json` (SHA-256 `b7fb2c6d5c134a77d6b7c5c9f605aa1355ec65de69e63bffb380a20cd4bc7e88`)

## Hensikt

Frosne discovery-protokoll V1 (`data/local-service-discovery-protocol-v1.json`) ble testet på helt nye kommuner for å avklare om den generaliserer, før eventuell crawler/runtime-implementering. Dette er en holdout-lignende generaliseringstest, ikke ny protokollutvikling. Ingen protokolldeler ble endret underveis (`PROTOCOL_MODIFICATIONS = 0`).

## Utvalg

11 ferske kommuner, fordelt 1 x klasse 1 og 2 x klasse 2-6:

| Klasse | Kommuner |
|---|---|
| 1 | Rælingen |
| 2 | Drammen, Fredrikstad |
| 3 | Askøy, Bamble |
| 4 | Birkenes, Bjerkreim |
| 5 | Alstahaug, Etnedal |
| 6 | Aure, Balsfjord |

**Dokumentert avvik fra spesifikasjonen (12 kommuner):** Nasjonalt finnes bare fem kommuner i sentralitetsklasse 1, og fire av dem var brukt i Municipal Sample V1. Kun Rælingen var tilgjengelig som fersk klasse 1-kommune. Avviket (`SAMPLE_DEVIATION_KLASSE1_POOL_EXHAUSTED`) er forfrosset i samplefilen før research og er ikke et seleksjonsvalg.

Freshness: 10 x `UNSEEN`, 1 x `INCIDENTAL_MENTION_ONLY` (Drammen). Ingen kommune var tidligere grundig kartlagt.

## Freeze-kjede

1. Protokoll + schema + sample frosset før første søk: `evaluation/local-discovery-generalization-v1/protocol-freeze.json` (protokoll-SHA `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca`, sample-SHA `295f3a168648bf72c2cfeee52296b2b53824a22b3e59bf334398087ad1e2fd5f`).
2. Phase A (frozen-protocol execution) fullført for alle 22 scenario-celler (2 scenarier x 11 kommuner).
3. Phase A frosset før audit: `evaluation/local-discovery-generalization-v1/protocol-predictions.json` (SHA `ff8b0322552db2c815d8f9eee3e77f6360cc3641ee882b26b3c1f32e7bf2f759`, status `PROTOCOL_PREDICTIONS_FROZEN_BEFORE_AUDIT`).
4. Phase B (uavhengig audit) kjørt etter freeze.

## Scenarier

Per kommune ble to celler testet:

- **Scenario C:** 19 år, moderate psykiske plager, ikke akutt.
- **Scenario D:** 22 år, ønsker rask/lavterskel psykisk helsehjelp, ikke akutt.

## Phase A - frosne protokollprediksjoner

Fordeling: **17 x `ROUTE_FULLY_VERIFIED`**, **3 x `ROUTE_ACCESS_PARTIAL`** (Askøy D, Bjerkreim C og D), **2 x `ROUTE_EXISTENCE_ONLY`** (Rælingen C og D), **0 x `ROUTE_UNVERIFIED`**.

Discovery-dybde: 16 celler løst på nivå 0-1 (direkte søketreff), 4 celler krevde nivå 2 (kategorinavigasjon), 0 celler krevde nivå 3-5 for ruteutfall. Rælingen ble blokkert av JS-SPA-rendering og endte ærlig på `EXISTENCE_ONLY` i stedet for falsk full-verifisering.

## Phase B - uavhengig audit

To uavhengige auditorer (modell `gpt-5.6-luna`, 2 subagenter, delt inn i diskjunkte kommunesett på 6 + 5) kjørte bred offentlig websøk etter prediction freeze:

- **Auditor-blindhet:** Auditorne mottok kun kommunenavn og scenario-beskrivelse. De fikk ikke se Phase A-verdicts, tjenester, URL-er eller metrics, og leste ingen prosjektfiler.
- **Resultat:** 22/22 celler dokumentert med URL + verbatim-sitater + hentedato. Ingen `NOT_DOCUMENTED`-celler.
- **Provenansspot-sjekk:** 3/3 nøkkel-URL-er live-verifisert HTTP 200. Bamble drop-in-bookingskravet verbatim-bekreftet mot live side (endret 02.03.2026).

## Generaliseringsmetrics

| metrikk | resultat | target | vurdering |
|---|---|---|---|
| Scenario route recovery | 22/22 = **100 %** | >= 90 % | PASS |
| False no-route (kritisk) | **0** (0 `ROUTE_UNVERIFIED` totalt) | 0 | PASS |
| `FULLY_VERIFIED`-presisjon | 17/17 = **100 %** | >= 95 % | PASS |
| Tilgangsmodell-presisjon | 20/20 rute-relevant = **100 %** (19/20 = 95,0 % streng) | >= 95 % | PASS |
| Audit fullført | 11/11 kommuner, 22/22 celler | alle | PASS |
| Historiske artefakter endret | 0 | 0 | PASS |

## Mismatch-taksonomi (6 treff, 0 kritiske)

| Kategori | N | Celler |
|---|---|---|
| `AGE_ELIGIBILITY_MISS` | 2 | Bjerkreim C+D - auditor fant aldersdokumentasjon (HFU 13-20; "unge fra 16 år og voksne") protokollen ikke fanget. Ville kunne oppgradert til `FULLY_VERIFIED`; rute uendret. |
| `ACCESS_EVIDENCE_MISS` | 1 | Bamble D - Phase A skrev "drop-in for voksne"; auditor fant (live-verifisert) at drop-in-samtalen krever forhåndsbestilling. Rute og selvkontakt-modell uendret. |
| `SOURCE_DISCOVERY_MISS` | 1 | Drammen C - sekundærtilbudet Ungdomstorget (13-25, drop-in) ikke fanget; primærrute RPH korrekt. |
| `AUDIT_ONLY_WEAK_EVIDENCE` | 2 | Rælingen C+D - auditor dokumenterte marginalt sterkere tilgangsbevis (navngitt telefon, eldre veileder med egenkontakt over 18), men ikke sterkt nok til å motsi `EXISTENCE_ONLY`. Logget som fremtidig berikelse. |

Ikke-truffete kategorier: `QUERY_VOCABULARY_MISS` 0, `NAVIGATION_DEPTH_MISS` 0, `INTERMUNICIPAL_MISS` 0, `SERVICE_CLASSIFICATION_MISS` 0, `OTHER` 0.

## Query-family-ytelse

Beslutningsgivende templates i fresh sample: **1** ("psykisk helse voksne", 11/11 kommuner), **3** ("kontakt", 3), **4** ("rask psykisk helsehjelp", 3), **2** ("søknad", 1). Templates 5-9 ga ingen beslutningsgivende funn i dette utvalget. Auditor logget `MISSING_QUERY_CONCEPT`-ønsker (f.eks. RPH-statussider, digitale selvhenvisningslenker) per kommune i maskinartefaktet. Ingen template ble endret i denne tasken.

## Sentralitet (raw)

| Klasse | Celler | Fully verified | Partial | Existence only | Recovery |
|---|---|---|---|---|---|
| 1 | 2 | 0 | 0 | 2 | 2/2 |
| 2 | 4 | 4 | 0 | 0 | 4/4 |
| 3 | 4 | 3 | 1 | 0 | 4/4 |
| 4 | 4 | 2 | 2 | 0 | 4/4 |
| 5 | 4 | 4 | 0 | 0 | 4/4 |
| 6 | 4 | 4 | 0 | 0 | 4/4 |

Klasse 1-svakheten skyldes Rælingens SPA-plattform (teknisk tilgangsproblem, ikke protokoll-logikk). Ingen kausal konklusjon trekkes.

## 19 vs 22 år

- Begge routable: 11/11 kommuner.
- Routing-cliff: ingen hardt kløft i fresh sample. Ett grensetilfelle: **Askøy D** - voksenflyt er eksplisitt dokumentert "over 24", og 18-24-sporet er ikke eksplisitt dokumentert. Askøy C (barn/unge-spor) er til gjengjeld direkte dokumentert.
- Bamble D skiller produkt: voksen drop-in-samtale (18+, bestilling på forhånd) vs ungdoms-HFU 13-23.
- Bjerkreim dokumenterte i audit aldersdekning "unge fra 16 år og voksne" som også fanger 19 og 22.

## Produktimplikasjoner for fremtidig crawler/runtime

1. Dybdebehov er lavt: nivå 0-1 + 2 dekker 20/22 celler. Dyp sitemap-traversering (nivå 3-5) ga ingen tilleggsruter i dette utvalget.
2. SPA-kommuner trenger fallback-kilder (PDF/skjema-lenker, eldre veiledere) og et ærlig `EXISTENCE_ONLY`-utfall i stedet for falsk verifisering.
3. Aldersgrenser er den hyppigste dokumentasjonshulen. Runtime må aldri anta aldersdekning uten eksplisitt kildetekst.
4. Tilgangsmodell må fange produktvilkår (f.eks. forhåndsbestilling) også når navnet sier "drop-in".
5. Ikke-beslutningsgivende query families (5-9) bør evalueres i en separat fremtidig protokolltask - ikke tunet her.

## QA

- Protokoll-SHA før/etter: identisk (`fb533d99...`), `PROTOCOL_MODIFICATIONS = 0`.
- Phase A frosset før audit: ja (status + SHA registrert).
- Ingen Phase A-endringer etter freeze.
- Sample frosset før research; ingen kommuneutskifting.
- Historiske filer (71, 72, 73, sample V1, 18-23-gap V1, access-verification V1, protokoll + schema) uendret - verifisert mot SHA-er tatt ved oppstart.
- JSON-validert; konsistent med menneskerapporten.
- Auditor-uavhengighet: blindness-kontrakt overholdt (bekreftet av begge auditorer i sluttmelding).

## Grenser

- Audit-referansen er dokumentert offentlig kildegrunnlag per 2026-09-09 - ikke offline sannhet om hvilke tjenester som faktisk eksisterer.
- Klasse 1 er underrepresentert (1 kommune) pga nasjonal pool-utmattelse, dokumentert ovenfor.
- Ventetider er sjelden tallfestet i kildene; kun publiserte formuleringer er rapportert.

## Konklusjon

Den frosne protokollen generaliserer: 100 % rute-recovery, 0 kritiske false-no-route, 100 % presisjon på `FULLY_VERIFIED`, 100 % rute-relevant tilgangsmodell-presisjon. De seks mismatches er små, alle non-kritiske, og peker på berikelse (aldersdokumentasjon, sekundærtilbud, produktvilkår) - ikke protokollbrudd.

**Status: `LOCAL_DISCOVERY_GENERALIZATION_PASS`** - grønt lys for en separat crawler/runtime-prototype-task.
