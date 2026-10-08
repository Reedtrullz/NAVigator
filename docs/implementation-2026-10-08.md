# NAVigator – gjennomføring 08.10.2026

Plan: docs/superpowers/plans/2026-10-08-navigator-product-plan.md
Arbeidsgren: codex/navigator-contact-pilot. Original checkout og pakker bevares.

## Avgjørelser

- Ruling: Ny generator bruker kun egne tillatte innganger; historiske register-, kommune- og korpusavhengigheter kopieres ikke. De er ikke faglig godkjent for ny kandidat. Kostnad: den nye piloten tilbyr begrenset kontaktinformasjon, ikke alle gamle ordninger.
- Ruling: Kvalifisert kildekontroll og faktiske menneskelige brukerprøver kan forberedes, men ikke attesteres av agenten. Disse kvitteringene blir NOT_RUN og distribusjon forblir BLOCKED. Kostnad: kandidaten trenger ekstern kontroll før utgivelse.
- Ruling: Runtime er planens separate senere løp, frakoblet fra denne pilotleveransen. Kostnad: dokumenterte motorfeil består frem til R-løpet utføres.
- Ruling: Brukerens «Start arbeidet» autoriserer lokal implementasjon av den konkrete planen uavhengig av GitHub Ready-felt; eksisterende issues får en lokal dispositionstabell. Ingen push, PR eller endret sakstilstand i denne leveransen.

## Fremdrift

- G1: kildeidentiteter kontrollert; 9 kode-/schema-/policyfiler positivt tillatt og kopiert byteidentisk. 41 GiB ledig før bygg. Remote AGENT_WORKFLOW.md lest via GitHub API; lokal base beholdes eksplisitt.

- U2: 7 nye tilstandskontrakter feilet på gammel kode (DOM-avhengighet/manglende API); 8/8 består etter ren modell. Eksisterende korrekt pilot-negasjonstest bevart.
- U3/U4: nye spørsmåls-/hjelpeinnganger observert RED → GREEN; 18 kontraktprøver består. Nettleserprøving gjenstår etter nytt bygg.
- G3: nye autoritative kildeoppslag hentet utenfor frosne registre. Kontaktinformasjon holdes LIMIT i utviklingskandidat; kvalifisert kontroll av kandidat er PENDING.

- U1: egen positiv byggallowlist, lokal AJV og fast tidspunkt. Uavhengig bygg feilet på den gamle registeravhengigheten før ny generator. 3 byggprøver består, inkludert avvisning av utdata utenfor outputs og symlink i utdata.
- U5/U6: kontakt før kildeapparat, én kort live-region, native radioer uten defaults. Nettleser: hovedvei uten fritekst, 320 px uten overflow og fokus etter «Neste» kontrollert. Notatcheckbox mistet fokus i første nettleserprøve; rettet og ny prøve beholder fokus. VoiceOver og faktisk 400 % zoom gjenstår.
- U7: felles personvernprojeksjon for tekst/kopi/utskrift. Seks negative kontrakter observert RED → GREEN. Faktisk kopiert tekst kontrollert; PDF generert med nettleserens printmotor. Nedlastingshendelsen i IAB har timeout; faktisk lokal fil kontrolleres separat.
- U8: v1/v2/v3-import med validering og eksplisitt anvendelse; tre bekreftelser arves ikke. Rå sikkerhetstekst utelates også fra arbeidsfil. Originalt v1-betalingssvar bevares som migrasjonshistorikk, uten ny betydning. Akutt-sperre består ved tømt tekst, import og nullstilling.
- G2: positivt tillatt, nytt kontaktgrunnlag avledet; 5 syntetiske personvern-/avledningstester består. Full referansebase og faktisk personvernkontroll er ikke ferdig. Testenes første positive output ble avvist på macOS /var-symlink; fixtures flyttet til avgrenset worktree-output fremfor å svekke kontrollen.
- G3: matrise med 26 historiske påstander PENDING/ikke tatt inn, pluss 4 begrensede kontaktkilder. Ingen faglig godkjenning arvet. Kvalifisert kontroll gjenstår.
- Ruling: Sikkerhetsgrunnlaget får ingen agentbesluttet overgang fra tidligere akutt-sperre til ordinære råd; eksplisitt reset og import beholder sperren i samme side. Kostnad: brukeren kan bli stående i hjelpeskjermen frem til et separat, kvalifisert vurdert overgangsdesign finnes.
- Ruling: Rå situasjonstekst lagres heller ikke i privat arbeidsfil. Dette begrenser privat datamengde, og forklares ved tekstfelt og filkontroll. Kostnad: teksten må skrives inn igjen ved gjenåpning.

- Final review: én fersk lesende GPT-6 Luna på 43b4c04. Ingen kritiske funn; 4 viktige funn rettet i én RED → GREEN-runde. V2-svarvokabular omgradert til viktig og rettet. Resultat og gjenstående minor: docs/code-review-2026-10-08.md.
- Final: fixed fremdriftsbasis-tekst, gammel bekreftelse, historikktap og autolenker — navngitte negativ-/regresjonsprøver RED → GREEN; samlet 43 Node + 3 bygg + 6 referanseprøver består, samt generert schema-kontrakt.
- Final: minor (deferred): referanseprofil med filnavnet manifest.json kan kollidere med kontrollmetadata og gi delvis output ved feil. Nåværende positiv profil bruker kontaktgrunnlag.md.
- Final: Ruling: kontrollørens avståelse fra kilde-/klinisk/personvern-/menneskelig vurdering opprettholdes — kandidatens nye tekst er nøytral kontaktinformasjon, men teknikk erstatter ingen slik kontroll — kostnad: distribusjon forblir BLOCKED.
- Final: Ruling: v2-importvokabular ble viktig fremfor minor — eldre filversjon må ikke endre betydning på svar — kostnad: filer med verdier som aldri tilhørte den versjonen avvises uten å endre state.
- G4: faktiske browserprøver, kopiert/nedlastet tekst og arbeidsfil samt én-sides print-PDF kontrollert med fiktive svar. Delvise tilgjengelighetsresultater er ført; VoiceOver, faktisk zoom og menneskelige brukerprøver er NOT_RUN.
- G5: identifisert lokal reviewleveranse forberedes med egne hashes og vedlikeholds-/prøveprotokoll. Primær HEAD fortsatt f778090; 172 valgte originalfiler er byteidentiske. Ingen deploy, motoraktivering eller GitHub-mutasjon.
