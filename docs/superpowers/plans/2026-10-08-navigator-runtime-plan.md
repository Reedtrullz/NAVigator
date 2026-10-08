# NAVigator – separat runtime-plan

> **For agentic workers:** Bruk `superpowers:executing-plans`, sekvensielt og med syntetiske fixtures. Ingen live provider, privat retrieval, evaluatoråpning eller pilotintegrasjon er implisitt i denne planen.

**Goal:** Reparere påviste korrekthetsgrenser i motoren før en eventuell senere tilkobling til et brukerprodukt.

**Architecture:** Bevar phase-3 som SUT-inngang, phase-2 som delte trinn og V2.5 som separat discovery-eksperiment. Forbedre kontrakter og feilforplantning i egne revisjoner; historiske schemas/låser og replayresultater forblir uendret.

**Tech Stack:** Python unittest, JSON-kontrakter, fake leverandører og syntetiske kilde-/ruteobjekter. Ingen nye modeller eller leverandørkontoer kreves.

**Spec:** [Korrekthetsanalysen](/Users/reidar/Projectos/NAVigator/PRODUCT_REVIEW_2026-10-08.md), [hovedplanen](/Users/reidar/Projectos/NAVigator/docs/superpowers/plans/2026-10-08-navigator-product-plan.md), `runtime/AGENTS.md` og nivåspesifikke guider.

**Status:** Senere separat løp. Planen er ikke en åpning av frosne schemas, historisk evaluator eller live runtime.

## Global Constraints

- Phase 1 forblir en dokumentert skeleton; V2.5 erstatter ikke phase-3/V1 replay i historiske målinger.
- Avvisningsstatus, stage execution, kildeevidens, epistemisk tilstand og faktisk tjenestetilgang skal forbli forskjellige begreper.
- Privat tilgang bestemmes før filåpning. Hashgyldighet og kildeklasse alene er ingen tillatelse.
- Eksisterende frosne input/output-schemaer omskrives ikke. Nødvendige interfaceendringer utvikles som ny eksplisitt revisjon med adapter eller forblir et blokkert forslag.
- Ikke kjør hele eksisterende testsuiten før kildetilgang/providerbruk er inventert. Flere gamle tester åpner den virkelige kunnskapsindeksen.
- Ingen hemmeligheter, private saksdata eller binære medier sendes til modeller. Ingen modellbruk er nødvendig for disse reparasjonene.

## Review Focus

1. Privat/ukjent klasse, sti utenfor rot eller symlink åpnes ikke før tillatelse. R1.
2. Norsk Unicode og negasjon i annen setning bevarer betydningen. R2.
3. Manglende eller avvist kilde blir ikke «ingen tjeneste» eller VERIFIED. R3.
4. Evidens fra én tjeneste/målgruppe beviser ikke en annen. R4.
5. Avvist rendering, mislykket fetch og feil vertsgrense stopper riktig output. R5–R6.

## R1 – Tilgang før filåpning

**Files:** `runtime/sut/phase2/knowledge.py`, `pipeline.py`, eventuelt config-hjelper; ny `runtime/sut/phase2/test_privacy_scope.py`. Nytt kuratert indeks-/profilgrunnlag peker bare til godkjente generelle kilder; frosset indeks omskrives ikke.

**Interfaces:** Foreslå `load_knowledge(index_path, repo_root, *, access_profile)` med default avvisning når eksplisitt godkjent profil mangler. Profil angir tillatte dokument-ID-er/stier og permission-beslutning. Det må ikke finnes en fallback til hele privat indeks. `retrieve` og S4 sender samme profil videre.

- [ ] Skriv tester som fanger filåpninger med fake filesystem: privat, avledet, ukjent, symlink og traversal avvises før open; tillatt offentlig fil åpnes først etter profil-/stikontroll.
- [ ] Kjør `PYTHONPATH=runtime python3 -m unittest sut.phase2.test_privacy_scope` og registrer relevant feil.
- [ ] Implementer den eksplisitte profilen og feilstatus uten å vise rå private filnavn/tekst i brukeroutput.
- [ ] Kjør positiv/offentlig og negativ/privat suite; kontroller at også keyword/domain-løse eller feilklassifiserte forespørsler ikke kan åpne private filer.

**Done:** Ingen syntetisk privat markør er lest/returnert/logget; ukjent tillatelse stopper. Eksisterende #1–2, #10 og #21.

## R2 – Norsk normalisering og signalbundet negasjon

**Files:** `runtime/sut/phase2/safety.py`, `decompose.py`, `knowledge.py`; ny `runtime/sut/phase2/text_normalization.py`; ny `test_semantic_normalization.py`.

**Interfaces:** `normalize_match_text(text: str) -> str` med eksplisitt Unicode-/æøå-behandling og dokumentert mapping til matchtekst. Negasjon knyttes til samme signaluttrykk; et rent antall tegn før signalet er utilstrekkelig.

- [ ] Skriv parvise tester for norsk/ASCII, tegnsetting, annen-setning-negasjon og ekte benektelse; inkluder det reproduserte «blør/blor» og «Det er ikke akutt. Jeg blor mye».
- [ ] Kjør `PYTHONPATH=runtime python3 -m unittest sut.phase2.test_semantic_normalization` og bekreft feilene før endring.
- [ ] Implementer samme avtalte matchnormalisering i sikkerhet, domenedeling og søkeord, uten å endre originale kildeutdrag.
- [ ] Samstem med pilotens kontroller som tillegg, men bruk uavhengig vurderte setningspar som fasit. Klinisk ordlyd/klassifikasjonssemantikk følger G3; ukjent skal ikke fremstilles som positiv trygghetsvurdering.

**Done:** Skrivemåte gir ikke utilsiktet ulik betydning, og uvedkommende negasjon undertrykker ikke separat signal. #8–9.

## R3 – Kildeavvisning, kunnskapshull og faktisk dato

**Files:** `knowledge.py`, `aggregate.py`, `pipeline.py`; ny `test_source_admission.py`. Nye kontraktforslag holdes utenfor frosset schema.

**Interfaces:** Foreslå intern `RetrievalResult` med `records`, `failures` og `coverage`. `coverage` skiller komplett behandling av avgrenset kildeutvalg fra kildehull. Et GAP-record er en opplysning om et hull, aldri et positivt verifisert tjenestefaktum.

- [ ] Skriv tester `sha_rejection_propagates`, `missing_differs_from_no_match`, `gap_not_verified_fact`, `historical_not_current` og `verified_date_is_source_specific` med bare syntetiske poster.
- [ ] Kjør `PYTHONPATH=runtime python3 -m unittest sut.phase2.test_source_admission`; implementer resultatformen gjennom S4/S7/emission i ny kontraktrevisjon eller kompatibel intern adapter.
- [ ] Fjern fast dato som verifikasjonsbevis. Manglende kontrollert_dato blir ukjent; runtime henting blir ikke faglig kontroll.
- [ ] Vis begrensningen på berørt spor/påstand. Kontroller at kilder som avvises ikke kan brukes som bakgrunn for et verifisert råd.

**Done:** Kildehull og avvisningsgrunner overlever alle relevante trinn. #4–5, #11, #45 og #58.

## R4 – Evidens per tjeneste, dimensjon og målgruppe

**Files:** `runtime/sut/phase2/routes.py`, `pipeline.py`, `aggregate.py`; ny `test_evidence_integrity.py`; berørte V2.5-parser/ruteevalueringsmoduler etter avgrenset kildeinspeksjon.

**Interfaces:** Behold `build_route_candidates(discovery, track_domain, age=None)` der mulig. Hver VERIFIED/PARTIAL-dimensjon trenger en matchende evidence-/provenance-binding med tjenesteidentitet, kilde og hva som faktisk er bevist. Ingen «matched or all refs»-fallback. Manglende alder-/målgruppekriterium gir UNRESOLVED.

- [ ] Skriv tester `other_service_evidence_rejected`, `run_access_not_inherited`, `age_presence_not_eligibility`, `independent_track_uncertainty` og `evidence_ids_unique_across_tracks`.
- [ ] Kjør `PYTHONPATH=runtime python3 -m unittest sut.phase2.test_evidence_integrity`; fjern generell evidensfallback og run-level tilgangsarv.
- [ ] Sammenlign eksplisitte målgruppe-/alderskriterier med faktisk input når grunnlaget finnes. Uavklart kriterium/brukerinput får ingen positiv egnethetskonklusjon.
- [ ] Kontroller hver påstand for faktisk kildeutdrag/locator, ikke bare eksisterende ID. Schema-/måleendringer foreslås separat.

**Done:** Ingen tjeneste eller spor blir mer verifisert av en annens evidens. #12, #42–44, #58 og #62.

## R5 – Avvist svar fjernes fra brukerutgangen

**Files:** `runtime/sut/phase3/finalize.py`; ny `runtime/sut/phase3/test_rejected_output.py`; eventuell adapter for ny feilkontrakt.

- [ ] Skriv tester `rejected_answer_not_in_output`, `render_exception_safe_output` og `failure_cannot_be_overridden_by_answer_field`.
- [ ] Kjør `PYTHONPATH=runtime python3 -m unittest sut.phase3.test_rejected_output`; endre `_failed_render_output(message, answer_text='')` slik at avvist tekst aldri havner i kanonisk brukerfelt.
- [ ] Bevar årsak/feiltype uten rå avvist anbefaling i vanlig output. Eventuell teknisk diagnostikk må ha separat, eksplisitt innholdspolicy.
- [ ] Test output som en enkel downstream-klient som bare leser `answer`, i tillegg til klient som leser hele statusobjektet.

**Done:** Et avvist svar kan ikke vises ved å overse statusfeltet. #7 og #63.

## R6 – Korrekt fetch-regnskap og nettverksgrense

**Files:** `runtime/discovery_v2/orchestrator_v25.py`, `runtime/discovery/security.py`; relevante HTTP-/renderprovider-filer etter inspeksjon; nye `runtime/discovery_v2/test_fetch_accounting.py` og `runtime/discovery/test_host_policy.py`.

**Interfaces:** Regnskap har særskilt attempted_fetches, successful_fetches, protocol_completed og services_found i ny revisjon. COMPLETE forutsetter avtalt protokollgjennomføring; vellykket henting uten tjenester kan være et ærlig tomt resultat. Fetch-feil er ikke det samme som tom dekning.

- [ ] Skriv fake-provider-kontroller for timeout, feilstatus, tom vellykket side, delvis protokoll og komplett protokoll. Ingen nettverk.
- [ ] Skriv host-/redirect-/adressekontroller for eksakt offisiell vert, spoofet suffiks, subdomenegrenser, private IP-er, redirect til privat adresse og endret DNS-resultat før tilkobling.
- [ ] Kjør `python3 -m unittest runtime.discovery_v2.test_fetch_accounting runtime.discovery.test_host_policy` før implementasjon.
- [ ] Reparer tellere og statuspropagering. Gjør `is_official_domain` til korrekt vertsgrensekontroll; behold URL-tillit og nettverkstillatelse som separate beslutninger.
- [ ] Kontroller samme policy ved alle redirect-hopp og HTTP-/renderinnganger med fake resolver/transport. Ingen uspesifisert browser-renderfallback får omgå nettverksgrensen.

**Done:** Ingen mislykket fetch blir vellykket henting; ingen spoofet vert får offisiell kildeautoritet; private nettverksmål stoppes før tilkobling. #13–15 og #63.

## R7 – Samlet, avgrenset runtime-receipt før senere integrasjon

**Files:** Ny runtime-kandidatkvittering og kontraktendringsoversikt. Historiske evalueringer og task locks uendret.

- [ ] Kjør bare de nye navngitte syntetiske modulene samlet etter R1–R6. Eksisterende tester får klassifikasjon: syntetisk, tillatt offentlig fixture, privat indeks eller live provider før eventuell kjøring.
- [ ] Lag en fake-provider end-to-end-prøve via den avtalte fase-3-inngangen: private scope, kildeavvisning, ukjent egnethet, renderingfeil og teknisk discovery-feil forblir ærlige i siste output.
- [ ] Dokumenter gamle og nye interne grensesnitt, eventuelle schema-revisjoner og hva som ikke er målt. Ingen historisk score gjenberegnes automatisk.
- [ ] Lever separat beslutningsgrunnlag for en senere begrenset integrasjon. Teknisk PASS alene aktiverer verken motor, nettverk eller distribusjon.

**Done:** Hver reparert feil har et falsifiserbart kontrollresultat, og alle uavklarte aktiveringsgrenser er synlige. Runtime kan fortsatt være frakoblet etter en teknisk vellykket reparasjon.
