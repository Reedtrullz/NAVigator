# V2.5 Engineering Sluttrapport

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_5-ENGINEERING
Dato: 2026-09-10
Status: LOCAL_DISCOVERY_RUNTIME_V2_5_CANDIDATE_FROZEN
Candidate SHA-256 (manifest.json): 2ccdcb5de92404bbdd4af4ac5fcec6e57b9f58033fc9775c6aba70fdfdae2470

## Historikk bevart

- V2.4-kandidat uendret: manifest-SHA re-verifisert etter alt arbeid = 6f7e7ab3fe5f1576a5ca03f9509aa5fd06928b607cebc462702ca1e3ec393a2d.
- Protocol V1 SHA verifisert i benchmark-artefakt: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca.
- Alle frosne base-filer (protocol, roots_v24, cli_v23, providers, render, orchestrator, sitemap_fetch, security) SHA-identiske med V2.4-manifestet.
- V2.4 holdout-status forblir FAIL_FROZEN; ingen frosne filer ble patchet.

## Rotarsaker og generaliserte reparasjoner

1. Sitemapindex follow: WordPress-sitemapindex med kun barne-sitemaps ga 0 kandidater. Fix: SiteDirectProviderV25 folger inntil 4 validerte barne-sitemaps (SITEMAP_INDEX_FOLLOW). Fail-closed beholdt.
2. Render-on-empty: SPA-meny-root ga 0 kandidater uten at renderer ble trigget. Fix: ett begrenset root-render nar nav+sitemap gir 0 (RENDERED_NAVIGATION_LINK). Fail-closed beholdt.
3. FV-provenance: seksjonssider kunne claim-e FULLY_VERIFIED. Fix: is_service_specific_url-gate + RouteEvaluatorV25 cap FV -> ACCESS_PARTIAL. orchestrator_v25 er ordrett kopi av frossen orchestrator med tre dokumenterte deltas.
4. Wording: runtime-usikkerhetstekst verifisert forsiktig nok; certain_access_wording er et blind-audit-flagg per celle (scorer-policy), ikke en runtime-feil. Ingen runtime-endring.

## Budget-reparasjon under validering (dokumentert avvik)

Under Raelingen-gaten feilet forste kjoring med RATE_LIMITED: de fire dode raelingen-rotvariantene (DNS borte, verifisert mot autoritative navneservere) exhauste det frosne base-budsjettet (8) for den levende roten. SiteDirectProviderV23/V24 hadde samme heving (16) i sine subclasses; V2.5 arvet 8 fra frossen base. Fix: budsjett 8 -> 16 i providers_v25.__init__ (ny lineage). tests_v25 7/7 og alle frosne suiter re-kjort gronne etter endringen.

## Prosess-hendelser (ikke runtime-feil)

- Forste ralingen-kjoring (fra forrige sessjon) ble hang-diagnostisert; zombie-Chrome ble drept (OPERATOR_PROCESS_CLEANUP).
- Forgrunns-kjoring med timeout 400 ble drept av timeout for alle 9 queries.
- nohup-bakgrunnskjoring ble drept av exec-prosessgruppen; Chrome overlevde som foreldrelse. Konklusjon: bakgrunn ukompatibelt med dette miljoet; PTY-session brukt.
- Driveren var taus fordi den printet forst etter hver query; instrumentert med per-call progress (driver-artefakt).
- Dette er kjorevarianter, ikke evaluator-feil; siste kjoring er det offisielle artefaktet.

## Valideringsresultater (burned, en kjoring hver)

- Raelingen gate: 9/9 SUCCESS, metode NAVIGATION_LINK, riktig rot (ralingen.bedreinnsats.no), latens 203.0-204.1s (V2.4-referanse 203.1s), 0 eksterne sok, 0 runtime-feil.
- Full benchmark: 117/117 SUCCESS (query execution rate 1.0), gold-domain recall 1.0, official domain precision mean 0.9692, 0 bot blocks, 0 provider errors, 0 render-fallback events.
- Replay: 22/22 MATCH (frosne V1-fiksturer).
- Live 13 kommuner: 13/13 COMPLETE, runtime_failures=0, external_search_calls=0, critical_false_no_route=0, unsupported_fully_verified=0; Bamble korrekt cap-et til ACCESS_PARTIAL (V2.4: feilaktig FV) og ingen EXISTENCE_ONLY-celle ble FV.
- Access regression: 7/9 med de to dokumenterte V2.3 source-drift parene (Alta T2 FV->EXISTENCE_ONLY nedgradering; Hasvik T9 EXISTENCE_ONLY->FV oppgradering; begge live-drift, ikke runtime-feil), 0 existence-safety regressions.
- Network audit: external_search_calls=0.
- Tester: tests_v25 7/7; tests 27, tests_v21 19, tests_v22 20, tests_v23 15, tests_v24 4 - alle pass.

## Freeze

- candidate-runtime-v2-5/ med manifest.json (22 komponent-SHA-er), hashes.txt, README.md.
- Status: LOCAL_DISCOVERY_RUNTIME_V2_5_CANDIDATE_FROZEN.
- TASK-LOCK.json: CLOSED_TERMINAL.

## Grenser og neste steg

Dette er en development-kandidat, ikke en generaliseringspåstand. Ingen ferske kommuner, ingen fresh eval, ingen nytt blindsett, ingen Protocol V1-endring, ingen eksterne sokkemotorer. Anbefalt neste steg (separat task): begrenset fresh holdout mot nytt frys-design.
