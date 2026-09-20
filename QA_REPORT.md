# QA-sluttrapport: juridisk integritetskontroll av NAV Explore

Datostempel: 29.08.2026
Oppdrag: juridisk integritetskontroll, faktasjekk og integrasjons-QA av hele kunnskapssenteret, med konkrete mistanker (foreldreloven, forliksrad, fylkesnemnda, akuttvedtak, undersokelsesfrist, internatopphold/eksamenshjem), revisjon av juridiske pastander, lovendringer per 29.08.2026, konsistens, Mari-regresjon og scenariostresstest.
Metode: kontroll mot Lovdata-tekster lastet lokalt i sesjonen (barnevernsloven 2026, barnelova, ekteskapslova, opploringslova 2023, folketrygdlova, pasient- og brukerrettighetslova, helsepersonellova, sosialtjenestelova, arbeidsmiljolova, rettshjelpslova, plan- og bygningslova), Helsedirektoratets rundskriv og nasjonale retningslinjer via nettsok. Programmatisk henting fra Lovdata er blokkert (curl gir generisk side), sadan er forskriftstekster verifisert via rundskriv i stedet.
Hovedstatus: 15 vesentlige feil registrert og korrigert. Automatisk kontroll (scripts/qa_check.sh) gronn. Ingen kjente feilmnstre gjenstår.

## 1. Antall filer kontrollert

- 57 markdown-filer totalt: rotfagfiler 00 og 17-47, omraderedene 01-15, 5 livssituasjonsfiler i 16-livssituasjoner, README.md, INNHOLD.md, bug-rapport og data/qa-log.
- Alle fagfiler ble kontrollert i batcher: 01-15-omradene og 16-livssituasjoner med systematisk feilmnstre-sjekk, 17-29 med paragrafspot, 30-47 med full revisjon og verbatim-lovkontroll.
- Lokale lovtekster brukt som kontrollgrunnlag er lastet i /tmp i sesjonen; funnene er innarbeidet i filene, ikke bare notert.

## 2. Antall vesentlige feil funnet

15 vesentlige feil, registrert i data/qa-log.md. Tellingen dekker feil lovhenvisninger, feil lovnavn, manglende kapitteldekning, vilkars- og fristfeil, statusfeil (vedtatt vs. gjeldende), diagnostiseringspåstand i oppsummering og misvisende "plikt"-formulering. Trivielle skrivefeil er ikke talt som egne feil når de inngikk i samme korreksjon.

## 3. Antall feil korrigert

15 av 15 korrigert. Rettet filer: 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 43, README.md, INNHOLD.md. Filene 17-29, 40 og 44-47 samt 16-livssituasjoner ble kontrollert uten funn av samme typer feil.

## 4. De 10 viktigste feilene

1. Fil 37: "Foreldreloven §§ 54-65" som samlet foreldretvisprosess. Korrigert til barnelova med paragrafvis dekning: § 54 tvangskraft, § 55 vilkar, §§ 56-63 mekling/attest/vilkarsproving, § 61 nr. 1-5 og 7 saksforberedelse, § 64 begjaring, § 65 tvangsfullforelse.
2. Fil 37: ordinare foreldretvister via forliksrad. Korrigert: foreldretvist gar via obligatorisk mekling hos familievernkontoret og videre saksforberedende prosess i tingrett (BNL § 64); forliksrad gjelder ikke.
3. Fil 38: akuttrad manglet §§ 4-3, 4-5 og 4-6, og omsorgsovertakelse manglet kapittelhenvisning. Korrigert til fullt kapittel 4-løp (§§ 4-1 til 4-6 inkl. flytteforbud, menneskehandel, utreiseforbud) med omsorgsovertakelse henviset til kapittel 5, § 5-1. Topptekst bekreftet: LOV-2026-06-12-22 er i kraft 01.07.2026; LOV-2026-06-19-35 er "endres ved" og ikke i kraft.
4. Fil 30: permisjon og trussamfunnsfravar oppgitt som opploringslova 2023 §§ 2-12/2-13 (finnes ikke der). Korrigert til § 2-2 fjerde og femte ledd.
5. Fil 31: skolehelsetjeneste hjemlet i "HOTL § 3-1 tredje ledd og § 3-2 andre ledd". Korrigert: § 3-2 forste ledd nr. 1 er hjemmelen; andre ledd er kompetansebestemmelse.
6. Fil 31: HPL § 33 "fjerde ledd" oppgitt som BVL-kobling. Korrigert: i gjeldende 2026-tekst er det tredje ledd som omhandler palegg i samsvar med BVL § 13-4. Endringen av HPL § 21 (snoking) fra 01.07.2026 er notert i fila.
7. Fil 39: § 3-4 beskrevet med feil tiltaksliste og feil tidsfrister (barnehage uten tidsbegrensning, senter for 0-6 ar inntil 3 maneder, forovrig 1 ar); endringslov 2025 nr. 40 fremstilt som gjeldende. Korrigert mot lovtekst og merket IKKE I KRAFT.
8. Fil 41: BNL § 37/§ 42-blanding og PRL § 4-4 fremstilt for bredt. Korrigert: § 37 gir vesentlige omsorgssider til den barnet bor fast hos (også uten foreldreansvar), § 42 annet ledd for resten; PRL § 4-4 er unntaksbestemmelse med forsokt varsling av begge foreldre.
9. Fil 42/43: feil EKL-henvisning (rettet til §§ 23 og 26; tredje ledd unntar § 23/§ 24-saker fra mekling) og § 61-referanser uten nummerering/kostnadssvar (korrigert til nr. 1-5 og 7 med statsfinansiering).
10. Fil 32: "skriftlig plan" ved bekymringsfullt fravar fremstilt som Udir-plikt. Korrigert til Udir-anbefaling. I samme korreksjonsrunde fikk fil 37 korrekt 2026-modell for fri rettshjelp (behovsprovning, egenandel 1-99 prosent, ingen egenandel under 1G, forskrift FOR-2025-12-03-2411 i kraft fra 01.01.2026; ny navnelov IKKE i kraft).

## 5. Gamle eller utdaterte lover/begreper

- "Foreldreloven" som lovnavn: ikke lenger i bruk i kunnskapssenteret; alle forekomster er rettet til barnelova.
- "Fylkesnemnda": ingen treff i gjeldende-rett-tekst; dagens organ beskrives som Barneverns- og helsenemnda der relevant.
- "Forliksrad" i foreldretvister: fjernet.
- "Internatopphold" og "eksamenshjem": ingen treff i fagfilene; den tidligere feilaktige tiltakslisten er erstattet av korrekt § 3-1/§ 3-4-liste (besokshjem, avlastning, stottekontakt, fosterhjem, institusjon osv.).
- "Barnefordeling" finnes bare i fil 22 i konteksten "fri rettshjelp for prioriterte sakstyper", som er korrekt bruk av dagens terminologi.
- Statusmarkering bevart: ny barnelov (vedtatt 2025) og endringslov LOV-2026-06-19-35 er VEDTATT, IKKE I KRAFT, og er ikke innarbeidet som gjeldende rett.

## 6. Motsigelser mellom dokumenter

Ingen aktive motsigelser funnet i finale kjoringer. Konsistenspunkter som ble sjekket: BUP-henvisning (fastlege, psykolog, skolehelse; PPT henviser ikke), HABU-henvisning (fastlege/habiliteringsspor), diagnosekompetanse (BUP/HABU, ikke PPT), meklingsregler (BNL §§ 51-54, ett mote, attest gyldig 6 maneder), undersokelsesfrister (1 uke gennomgangsvurdering, 3 maneder ordinart) og akuttkapittel 4.

## 7. Kunnskapshull

- Lovdata blokkerer programmatisk henting, sadan er forskriftsteksten FOR-2018-10-19-1584 §§ 2, 3, 6 og 8 verifisert via Helsedirektoratets rundskriv og nettsok i stedet for Lovdata-original.
- Lokale variasjoner i kommunale tilbud (kommunepsykolog, lavterskeltilbud, Rask psykisk helsehjelp for voksne, tilsvarende tilbud for barn/unge) er dokumentert som organisasjonsmote og praksisvariasjon, men ikke som fullstendig kommune-for-kommune-oversikt.
- Ventetider er dekket av nasjonale prioriteringsfrister (65 virkedager under 23 ar ved lidelse/rus, prioriteringsforskriften § 4a); lokale ventetall er ikke samlet.
- Kildesjekk av kommunale sider er ikke dato-koordinert; kilder med dato ligger i kildedokumentasjonsfilene 24, 27 og 46.

## 8. Mari-regresjonstesten

Bestått. Fil 44 er konsistent med fil 22 (50 prosent stilling, datter 7 ar, utredning startet, ingen formell diagnose) og fil 34 (obligatorisk mekling, ett mote, attest gyldig 6 maneder, BNL §§ 51-54). Ingen dokumenter omtaler datteren som diagnostisert. Under rapportfasen ble oppsummeringene i README og INNHOLD rettet fra "barn med ADHD" til "under utredning (ingen diagnose)" og logget i data/qa-log.md. Barnevern er plassert som frivillig hjelpeinstans ved reelt behov (§ 3-1) og ikke som automatisk løp; BNL §§ 31, 52 og 54 er verifisert verbatim.

## 9. Scenariostresstesten

Bestått. 25 scenarioer i fil 47 (øvre grense av kravet 15-25) lapt mot 00-BESLUTNINGSTRE, fil 26 (matrise) og fil 45 (beslutningstre): alle 25 konsistente etter korreksjonene. Differensieringen av akutt, lavterskel, pedagogisk utredning, psykisk helseutredning, diagnostisk utredning, habilitering og foreldrestotte er sjekket mot fil 26. Testen avdekket konkrete svakheter i fil 30-32 og 37-43, som ble rettet.

## 10. Nye QA- og indeksfiler

- 00-BESLUTNINGSTRE.md: menneske- og AI-lesbar inngang "Jeg har dette problemet. Hvor begynner jeg?" med noder til fagfiler.
- 47-scenarioregresjon.md: 25 situasjoner med konsistensstatus.
- data/legal-index.json: maskinlesbar lovindeks (metadata + lover), validerer som JSON.
- data/services-index.json: tjenesteindeks for beslutningsstotte, validerer som JSON.
- data/qa-log.md: feilregister med fil, gammel formulering, korrigering, kilde og dato.
- scripts/qa_check.sh: lokal sjekk for gamle lovnavn, kjente feilmnstre og JSON-validering.
- QA_REPORT.md: denne rapporten.
- README.md og INNHOLD.md: oppdatert med QA-seksjoner og pekere til alle nye filer.

## 11. Statusvurdering

BRUKBAR MED FORBEHOLD. Alle identifiserte vesentlige feil er korrigert mot gjeldende lovtekst per 29.08.2026, den automatiske kontrollen er gronn og alle 25 scenarioer er konsistente. Forbeholdene er kunnskapshullene i punkt 7: ikke-fullstendig kommuneoversikt, programmatisk Lovdata-blokkering og manglende lokale ventetall. Full GODT VERIFISERT-status kommer forst nar lokale tilbud og ventetider er kildesjekket og vedtatt lovendringer (ny barnelov, LOV-2026-06-19-35) innarbeides nar de trer i kraft.

## 12. Neste avgrensede research-etappe

Kommunale variasjoner i psykisk helsehjelp til barn og unge: hent og verifiser faktasider fra et utvalg kommuner (storby, mellomstor, rural) om kommunepsykolog/psikologstillinger, lavterskeltilbud, barn-/ungdomstilbud og eventuelle lokale navn der Rask psykisk helsehjelp ikke finnes for barn/unge. Dette lukker det storste gjenvarende kunnskapshullet og hjelper beslutningstreet til a svare "hvor begynner jeg?" utover nasjonale hovedregler. Ikke startet automatisk.
