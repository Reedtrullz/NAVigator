# NAVigator – korrekthet, UI og UX

Dato: 08.10.2026. Analyse av lokal kildekode, styringsdokumenter, registermetadata og to konkrete private pilotbygg. Nettleserprøvene bruker bare syntetiske svar.

## Konklusjon

NAVigator har mye nyttig grunnarbeid: kilde- og byggregistre, eksplisitte usikkerhetstilstander, lokale brukerdata, korte behovsspørsmål og støtte til å forberede en kontakt. Den viktigste neste leveransen er en **avgrenset, etterprøvbar referanseutgave og én sammenhengende privat pilotflyt**. Brukeren skal kunne forstå hva som er relevant, velge en første kontakt og ta med et kort notat.

Det som hindrer dette nå er først og fremst motstridende planstatus, skjulte forutsetninger for å komme videre, for lange resultater, manglende tidsdimensjon for enkelte hastende behov og kilde-/verifikasjonsmodeller som kan uttrykke større sikkerhet enn grunnlaget støtter. Den eksperimentelle runtime-motoren har dessuten reproduserbare feil som må sperre eventuell senere tilkobling.

Bevar husholdningsvariantens bedre behovsspørsmål og semantikk, og bruk den roligere variantens presentasjon som utgangspunkt. Ingen av variantene er dokumentert som entydig valgt neste hovedversjon. Samlingen må skje i kildene, med et nytt identifisert bygg, før den kan vurderes som én kandidat.

## Hva som faktisk er undersøkt

| Del | Kontroll | Hva resultatet betyr |
|---|---|---|
| Prosjektets retning | CURRENT_STATE, PILOT_LINEAGE, mål og avgrensning, låser og tidligere porteføljer | Roten er et kunnskapsarkiv med flere eksperimenter og private piloter. Mål C er fortsatt dokumentert første referanseutgave. |
| Referansegrunnlag | Register-/profilmetadata og kontrollstatus for rev2 | Generell publiseringsprofil er BLOCKED. Rev2 har et arbeidsutkast med 26 påstander klart for faglig kontroll. Dette er ikke godkjenning. |
| To pilotbygg | Manifestkontroll: 44 innganger og én HTML-utgang i hvert bygg | Filene samsvarer med hvert sitt manifest. Dette bekrefter byggidentitet, ikke at rådene er riktige. |
| Brukerflyt | Start, spørsmål, bekreftelse, sikkerhet, plan, kontakt, eksportforhåndsvisning, smal skjerm og et tastaturutvalg | 14 skjermbilder og tekstlige observasjoner er lagret fra denne gjennomgangen. |
| Eksperimentell runtime | Kodelesing og 11 isolerte mekanismekontroller | Alvorlige feil er reprodusert uten private dokumenter, modellkall eller live discovery. |
| Pilotlogikk | Åtte kontroller, fire per variant | Bekrefter konkrete forskjeller mellom variantene og to felles forhold. |
| GitHub | Alle 65 forslagssaker og sammenligning med siste main | #1–65 er åpne. Åpen sak er ikke i seg selv bevis for manglende implementasjon. |
| Autoritative stikkprøver | NAV, VO-linjen og W3C | Avgrenset kontroll av kontaktbetegnelser, bolig-/matbehov og tilgjengelighetsprinsipper. Ingen full juridisk eller klinisk vurdering. |

Lokal rot står på `f778090a7a1f151aebcdad1cdd2af7dc51453b41`. GitHub main var `55eac73a54fbb05dac6e5ac9b1a70363fe9811ac` ved kontroll. Den eneste mellomliggende endringen er `AGENT_WORKFLOW.md`; runtime-koden i denne analysen er derfor ikke forbigått av en senere kodeendring på main. Pilotene ligger i separate, delvis ignorerte kataloger og har sin egen identitet.

| Variant | Eksakt kilde-/byggrot | HTML SHA-256 | Status |
|---|---|---|---|
| A: rolig start | `/Users/reidar/Projectos/NAVigator-rolig-start-2026-09-23` | `9a1ce8d2144ccbcf91f9f5121fbf66c148c5af74df401202c72a3a0f2b74a4c5` | UTKAST / BLOCKED |
| B: husholdning | `/Users/reidar/Projectos/NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/work` | `203136c9c513999abdb87f35b80fe010b600181cd6cd40a4aa58e2c36dc5cadd` | UTKAST / BLOCKED |

Aktiv serverversjon, autentisert drift, fysisk telefon og faktisk tilgjengelighet hos kontaktstedene er ikke kontrollert. Den historiske deploybeskrivelsen avgjør ikke hvilken versjon som er aktiv i dag.

## Det som bør bevares

- Korte spørsmål i vanlig norsk, med «Vet ikke» og «Vil ikke oppgi» som egne svar. Manglende opplysninger skal ikke bety nei eller avslag.
- Husholdningsvariantens to første behovsspørsmål, valgfrie detaljgrupper og korrigerte forhold mellom lav inntekt og betalingsproblemer.
- Rolig starts tydelige hovedknapp og mindre teksttunge introduksjon.
- Eksplisitt brukerutvalg av hva som tas med i møtenotatet, og lagring/eksport som brukeren selv velger. Automatisk lagring av sensitive svar er ikke nødvendig for bedre UX.
- Signalbundet negasjon og norsk normalisering i pilotens eksisterende sikkerhetskode. Denne håndterte den undersøkte setningen korrekt; runtime-motoren gjorde ikke det.
- Sporbare kilder, utdatert-vern, manifest og adskilte UTKAST/BLOCKED-tilstander. Disse må bli lettere å forstå, og fortsatt være reelle sperrer.

## Korrekthet: hva som må gjøres

### 1. Gjør offentlig og privat kunnskap til teknisk adskilte innganger

Den generelle publiseringsprofilen har en dokumentert personvernblokkering. Et offentlig korpus må ferdigstilles som en separat, kontrollert avledning med eget manifest, uten private opplysninger, avledede saksfakta eller lenker til ekskludert materiale. Bevar det private originalarkivet.

Runtime-leseren åpner alle indekserte dokumenter før domenefiltrering, og retrieval har ingen tilsvarende tilgangsbeslutning. En syntetisk post merket PRIVATE ble returnert. Dette er en påvist mekanismefeil, ikke en påstand om at en faktisk personopplysning ble sendt ut i denne gjennomgangen.

Akseptanse: Allmenn profil velges eksplisitt; avviste/private poster åpnes ikke; ukjent klassifisering avvises; kryssreferanser går bare til tillatte filer; separate syntetiske tester viser at private markører aldri når resultat eller logg. Det må kontrolleres på den faktiske avledede kandidaten, ikke bare på et generelt skjema.

Grunnlag: [publiseringsprofil](/Users/reidar/Projectos/NAVigator/data/publiseringsprofil-v1.json), [load_knowledge](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/knowledge.py:67), [retrieve](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/knowledge.py:153). Viderefør eksisterende [#1](https://github.com/Reedtrullz/NAVigator/issues/1) og [#2](https://github.com/Reedtrullz/NAVigator/issues/2).

### 2. Knytt verifikasjon til den konkrete påstanden og handlingen

Et korrekt hash viser hvilke bytes som ble lest. Det viser ikke at et telefonnummer virker, at tjenesten tar imot den aktuelle alderen, at en rettighetsregel gjelder i dag eller at et råd passer personen. Registerets dato og kontrollør må følge akkurat den påstanden som vises.

Runtime mister kildeavvisninger i retrieval, setter registrerte kunnskapshull til VERIFIED i aggregeringen og bruker en fast verifikasjonsdato. Ruteleggingen kan dessuten arve evidens fra en annen kilde og tilgangsstatus fra hele discovery-kjøringen. Dette kan gi et tilsynelatende verifisert svar uten tilsvarende bevis for den konkrete tjenesten.

Akseptanse: Bevar hver kildes avvisningsårsak; skill «ikke funnet», «ikke hentet», «gammel kilde» og «kilden motsier rådet»; bind evidens til tjeneste, påstand, dimensjon og kildeutdrag; sammenlign faktisk alder/behov med kriteriene; ikke løft en annen tjenestes tilgangsbevis til denne tjenesten. Kjent tjeneste, relevant inngang og innvilget rettighet skal ha forskjellige betydninger.

Grunnlag: [knowledge](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/knowledge.py:170), [aggregate](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/aggregate.py:20), [routes](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/routes.py:66), [evidensbinding](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/routes.py:251), [verifikasjonsdato](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/pipeline.py:46). Eksisterende #4–6, #11–12, #42–45, #57–58 og #64 dekker store deler av dette.

Rev2-kandidaten skal vurderes som sitt eget arbeidsutkast. Det er ikke grunnlag for å gjenåpne frosne evalueringer, oppdatere gamle hashpinner for å få grønt lys eller promotere rettede formuleringer til faglig godkjenning.

### 3. Reparer runtime-sikkerhet før motoren kobles til en brukerflyt

Den eksperimentelle Python-koden ga NOT_ACUTE for «Jeg blør mye», men ACUTE_RISK_NOW for ASCII-varianten «Jeg blor mye». «Det er ikke akutt. Jeg blor mye.» ble også nedgradert fordi en negasjon fra en annen setning fikk undertrykke faresignalet. Normal norsk skrivemåte påvirker også domenedekomponeringen.

Pilotens JavaScript håndterte norsk skrivemåte og den undersøkte negasjonen korrekt i begge bygg. Dette er et godt, eksisterende grunnlag for å samstemme kontrakten. En ordlistekontroll alene kan likevel ikke etablere klinisk trygghet; fravær av ordlistetreff skal ikke presenteres som en bekreftelse på at situasjonen er trygg.

Akseptanse: Samme eksplisitte normalisering og signalbundne negasjon i de relevante komponentene; positive og negative setningspar med norske tegn; profesjonelt vurdert tekst og eskaleringsmåte; uavklart skal forbli uavklart. Testene må kontrollere betydningen, ikke bare sammenligne komponentene med hverandre.

Grunnlag: [safety](/Users/reidar/Projectos/NAVigator/runtime/sut/phase2/safety.py:67), [mekanismekontroller](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/runtime-probe-results.json). Eksisterende #8–9 og #59.

### 4. La avvist output og mislykket kildehenting stoppe på riktig sted

Finalizerens feilutgang kan beholde svarteksten som kontrollen nettopp avviste. En nedstrøms visning som bare leser `answer`, kan dermed vise en avvist anbefaling. V2.5 teller et fetch-forsøk som hentet side før resultatet kontrolleres; ett mislykket forsøk med null tjenester kunne gi COMPLETE.

Det er også mulig å få klassifisert `helsenorge.no.untrusted.example` som en offisiell Helsenorge-kilde. Vertskontrollen bruker delstreng i stedet for korrekt vertsgrense. Nettverks-/redirectgrensen må vurderes samlet før live bruk; denne analysen viser ingen utført utnyttelse.

Akseptanse: Brukerutgang ved avvist rendering inneholder ingen avvist anbefaling; forsøk, vellykket henting, protokollgjennomføring og funn telles separat; offisiell vert valideres med eksakte grenser; DNS, redirect og eventuelt rendering følger samme nettverkspolicy. Feilstatus skal overleve alle overganger til UI og måling.

Grunnlag: [finalize](/Users/reidar/Projectos/NAVigator/runtime/sut/phase3/finalize.py:174), [V2.5](/Users/reidar/Projectos/NAVigator/runtime/discovery_v2/orchestrator_v25.py:138), [security](/Users/reidar/Projectos/NAVigator/runtime/discovery/security.py:76). Eksisterende #7, #13–15 og #63. Dette er sperrer for senere runtime-aktivering; pilotgrensesnittet bruker ikke denne motoren.

### 5. Gjør behov, hast og kontaktbetegnelse mer presise i piloten

Begge varianter kan prioritere en inngang til sosialhjelp som ORDINAER når brukeren mangler penger til nødvendige utgifter. Svaret sier ikke om dette gjelder neste måned eller mat i dag. Legg til et kort spørsmål bare når svaret krever det: eksempelvis «Gjelder dette mat i dag eller noe som må løses straks?» Skill tidskritisk økonomisk behov fra medisinsk akuttfare. NAV omtaler blant annet mat og fare for strømstenging som forhold som kan høre til nødhjelp. [NAV – økonomisk sosialhjelp](https://www.nav.no/okonomisk-sosialhjelp).

Boligspørsmålet trenger mer enn en binær vurdering av tak over hodet. Et midlertidig, usikkert opphold hos venner/familie må ikke automatisk bli «ikke relevant». NAV beskriver også denne situasjonen som en mulig inngang til hjelp med midlertidig botilbud. Første kontakt må passe oppholdsstedet, og en eventuell vei utenfor åpningstid må være konkret kildebelagt. [NAV – midlertidig botilbud](https://www.nav.no/midlertidig-botilbud).

116 006 bør navngis som Vold- og overgrepslinjen og beskrives som en hjelpelinje som blant annet kan veilede videre til krisesenter. Betegnelsen «krisesenterlinjen» kan skape feil forventning om direkte kontakt med et bestemt krisesenter. [VO-linjen](https://www.volinjen.no/vo-linjen/).

Akseptanse: Hvert hastende kort har ett forståelig første steg, rett tjenestenavn, dokumentert kontaktmåte, relevante åpningstider, kontrollert alternativ når stengt og tydelig opplysning om det som ikke er bekreftet. Ingen automatisk innvilgelses-/avslagskonklusjon. Fagperson kontrollerer de handlingsbærende formuleringene på den eksakte kandidaten.

## Brukerflyten – sju kontrollerte steg

Helsevurderingene nedenfor gjelder den observerte oppgaven, ikke en generell tilgjengelighetssertifisering. Bildene er tatt i denne gjennomgangen. A og B har ulike forbedringer; funn for A skal ikke leses som ubetingede funn for B.

### 1. Åpne produktet og forstå hva det hjelper med — delvis god

A har en rolig start, tydelig knapp og mindre konkurrerende tekst. B har bedre behovslogikk, men starter med tekniske statuser og en tyngre sikkerhetsintroduksjon. Brukeren trenger et tydelig løfte: «Svar på noen korte spørsmål. Du får hjelp til å velge første kontakt og lage et notat.» Forklar at svarene er valgfrie og hva som skjer ved lukking. UTKAST-statusen skal fortsatt være synlig med et forståelig innhold; hash, register-ID og bygginformasjon kan ligge under «Om denne utgaven».

![Steg 1 – A: rolig start](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/01-start.jpg)

![Steg 1 – B: flere tekniske begreper på startsiden](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/10-household-start.jpg)

### 2. Fortelle om behov uten å kjenne ordningsnavn — best i B, fortsatt ufullstendig

B prioriterer et sted å sove og penger til nødvendige utgifter, med detaljer i valgfrie grupper. Dette er mer hjelpsomt enn As seks spørsmål på samme nivå. Bevar B-strukturen. Følg bare opp med opplysninger som faktisk kan endre første steg, hast eller relevans. Vis kjente svar samlet, og skill ubesvart fra «Vet ikke» og «Vil ikke oppgi».

A holdt en gammel oppsummering synlig under gjennomgangen, selv om et spørsmål var besvart. Brukeren må kunne stole på at oppsummeringen viser de nåværende svarene. B har også rettet en semantisk forskjell: Lav inntekt uten betalingsproblemer ga ikke vurdert for bostøtte/sosialhjelp i A, men aktuelle innganger i B. B-resultatet er en screening av mulige kontakter, ikke bevis for rett til ytelsen.

![Steg 2 – A: seks spørsmål](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/02-questions.jpg)

![Steg 2 – B: to behov først, flere detaljer ved behov](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/11-household-questions.jpg)

### 3. Bekrefte svar og forstå sikkerhetskontrollen — dårlig

Den forespeilede, valgfrie friteksten passer ikke dagens videreføringsregler. A blokkerer plan med tom tekst selv etter vurdering. B tillater vurdert tom tekst, men «Gå til spørsmålene» utfører ingen sikkerhetsvurdering. En bruker som følger hovedveien, svarer og bekrefter, blir dermed møtt av en blokkering og store hjelpetekster.

Lag én sammenhengende overgang fra svar til resultat. Eventuell nødvendig sikkerhetsavklaring må være forståelig og synlig på denne veien. Tom eller tilbakeholdt tekst kan gi en begrenset kontakt-/forberedelsesflyt, men skal ikke bli en påstand om bekreftet sikkerhet. Revider de tre avkrysningene: Informasjon om produktets grenser bør gis når den hjelper beslutningen; en avkrysning kan ikke erstatte faglig eller teknisk validering.

![Steg 3 – A: bekreftelse med gammel oppsummering](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/03-review.jpg)

![Steg 3 – A: blokkert etter hovedflyten](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/04-blocked-plan.jpg)

![Steg 3 – B: hovedveien ender fortsatt i sikkerhetsblokkering](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/12-household-plan.jpg)

### 4. Finne planen og forstå om den gjelder — dårlig

I A stod «Utdatert» og «Gjeldende plan» samtidig. I begge varianter kunne steg 3 si at planen var klar samtidig som «Se gjeldende plan» var deaktivert. Knappen krever et eldre temavalg i stedet for å følge den faktiske plantilstanden. Selve kortene ligger i steg 2; steg 3 er i praksis en status-/navigasjonsflate til dem.

Bruk én eksplisitt modell for plantilstand og ett sted for resultatet. Vis hva som endret seg: «Du endret svaret om bolig. Oppdater planen for å bruke det nye svaret.» Navigasjonslenke til en eksisterende plan skal virke uavhengig av et skjult, eldre felt. Brukerens fremdriftsmarkeringer kan bevares som egen historikk når grunnlaget endres, med tydelig forklaring.

![Steg 4 – A: motstridende status](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/05-plan.jpg)

![Steg 4 – A: plan klar, men deaktivert inngang](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/07-plan-navigation.jpg)

![Steg 4 – B: samme navigasjonsproblem etter gyldig vurdering av tom tekst](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/13-household-plan-navigation.jpg)

Grunnlag: [A – gate](/Users/reidar/Projectos/NAVigator-rolig-start-2026-09-23/src/state-plan.js:341), [B – gate](/Users/reidar/Projectos/NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/work/src/state-plan.js:407), [B – knapp](/Users/reidar/Projectos/NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/work/src/ui.js:709), [B – start](/Users/reidar/Projectos/NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/work/src/ui.js:733). Eksisterende #30, #35 og #60.

### 5. Velge første kontakt og vite hva man skal gjøre — dårlig

Kortene bruker stor plass på begrunnelse, kontrollstatus, kilder og tekniske referanser før den praktiske handlingen. Det gjør et ellers nyttig resultat tungt å bruke. B-scenariet hadde to aktuelle innganger og fire avklaringer; de lange åpne tekstene konkurrerte om oppmerksomheten.

Presenter først ett tydelig anbefalt neste steg, deretter eventuelle alternativer. Et kort bør vise kontaktmåte, når kontakten kan brukes, hva man kan si og to–tre nyttige forberedelser. «Hvorfor dette kan være relevant» og «Kilder og begrensninger» kan foldes ut. Still bare en ny avklaring hvis svaret faktisk endrer neste handling; uklarheter uten slik virkning kan vente.

Vis tydelig når en tjeneste finnes, men lokal adgang ikke er kontrollert. Et dokumentert nasjonalt kontaktpunkt kan stå som en orienteringsinngang; det må ikke samtidig gi inntrykk av verifisert lokal mottaksvei eller sikker tilgang etter stengetid.

![Steg 5 – A: kontaktkort med handling langt nede](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/06-contact-card.jpg)

Eksisterende #32, #57–59, #61 og #65. Prioritering må bygge på behov og dokumentert hast; brukerens preferanse kan styre mellom forsvarlige alternativer.

### 6. Ta med en nyttig oppsummering og komme tilbake — delvis god

Utvalget av opplysninger og handlinger er en god personvernmekanisme. Forhåndsvisningen er imidlertid lang og teknisk. Lag et kort møtenotat med «Dette trenger jeg hjelp med», «Dette har jeg oppgitt», «Dette ønsker jeg å spørre om» og «Første kontakt». Hold produktets vurdering adskilt fra brukerens egne opplysninger.

Bruk samme eksplisitte personvernutvalg i tekst, utskrift og lokal lagringsfil. Gjør det klart hva som er lagret, og gi angremulighet ved nullstilling. Bevar valgfri lagring; tilby en tydelig beskjed om ulagrede endringer uten å innføre automatisk lagring av sensitive svar.

Forhåndsvisning er undersøkt. Faktisk filnedlasting ble ikke fanget av nettlesermiljøet, og import→eksport, utskrift og gjenåpning er ikke verifisert i denne runden. Dette er en verifikasjonsgrense, ikke en påvist eksportfeil.

![Steg 6 – A: brukervalg og lang forhåndsvisning](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/08-export.jpg)

Eksisterende #28–29 og #33–34.

### 7. Bruke flyten på mobil og med tastatur — delvis god

De kontrollerte breddene på 390 px i A og 320 px i B hadde ingen horisontal sideoverflyt. B holder de to viktigste spørsmålene høyt. Lang svarttekst blir imidlertid avkortet i en smal select, og resultatflyten blir svært lang når kort og avklaringer står åpne. Full syntetisk B-side var omtrent 27 000 px høy; dette er en observasjon av denne tilstanden, ikke en universell sidelengde.

Startknappen flytter fokus til spørsmål, og et tastaturutvalg fungerte. Det finnes samtidig ni høflige live-regioner i B; en av dem inneholdt over 11 000 tegn og eksportforhåndsvisningen over 4 000. Det bør være en kort statusmelding som varsles, mens hele resultatet kan leses ved normal navigasjon. Dette er en kode-/DOM-basert risiko; faktisk opplesing i VoiceOver er ikke testet. W3C beskriver hvordan statusmeldinger skal være tilgjengelige uten unødvendig fokusflytting. [W3C – status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html).

Bruk WCAG 2.2 AA som testmål, med eksplisitt manuell vurdering av tastatur, fokus, kontrast, zoom, leserekkefølge, skjermleser og feilhjelp. Ikke kall denne gjennomgangen samsvarssertifisering eller norsk juridisk godkjenning. Noen steglenker målte 24 px i høyde; dette er ikke alene bevis for brudd på minimumskravet. Større trykkflater vil likevel gjøre flyten enklere for mange. Legg også inn en nyttig statisk fallback uten JavaScript og respekt for redusert bevegelse. [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

![Steg 7 – A på 390 px](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/09-mobile-questions.jpg)

![Steg 7 – B på 320 px](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/14-household-mobile.jpg)

## Anbefalt gjennomføring

P0 betyr en sperre for det berørte bruksområdet. Runtime-P0 betyr ikke at referanseutgaven må vente på all motorutvikling; motoren kan holdes frakoblet. Følg de eksisterende sakene og revider akseptansekriteriene med disse funnene før nye duplikater opprettes.

| Rekkefølge | Avgrenset arbeidspakke | Ferdig når | Eksisterende saker |
|---|---|---|---|
| 1 | Velg én aktiv pilotkandidat og dokumenter forholdet til mål C | Ett navngitt kildegrunnlag, reproducerbart bygg/manifest, bevarte tidligere bygg og entydig neste kontrollmål. A-presentasjon og B-logikk vurderes som separate endringer. | #3, #23–24 |
| 2 — P0 for generell utgivelse | Ferdigstill offentlig avledet korpus og rev2-kontroll | Ingen private/avledede opplysninger eller private kryssreferanser; riktig kandidatbinding; kvalifisert beslutningsjournal for de handlingsbærende påstandene. | #2, #6, #36 |
| 3 — P0 for handlingsråd | Samstem hast, målgruppe og første kontakt | Mat straks, utrygt midlertidig opphold, riktig tjenestenavn og stengt kontaktsted har forståelige, kildebelagte forløp. Uavklart betyr fortsatt uavklart. | #12, #32, #57–59 |
| 4 | Reparer hovedflyt, sikkerhetsovergang og plantilstand | Hovedknappen leder sammenhengende til en begrenset/gyldig plan; planlenken virker; ingen samtidig «utdatert»/«gjeldende»; endringer forklares. | #30, #35, #60 |
| 5 | Gjør første steg kort og nyttig | Brukeren finner hvem, hvordan, når og hva man kan si uten å åpne tekniske detaljer; bare handlingsrelevante avklaringer kommer først. | #32, #57–58, #61, #65 |
| 6 | Fullfør mobil, tastatur og ta-med-flyt | Lesbare svar, korte statusvarsler, riktig fokus, no-JS-fallback, eksplisitt lagring, trygg nullstilling og verifisert eksport/import/utskrift. | #28–31, #33–35 |
| 7 — P0 før runtime-aktivering | Reparer og kvalifiser motorens grenser | Personvern før filåpning, norsk normalisering, avvist output fjernet, korrekt evidensbinding/tilgang, presise feiltellere og avgrenset nettverk. Ingen integrasjon før dette er bevist. | #1, #4, #7–15, #42–45, #62–64 |
| 8 | Gjennomfør avgrensede brukerprøver på identifisert kandidat | Faktiske observasjoner av oppgaveforståelse, første kontakt, avklaringer og møtenotat; feil og gjenstående begrensninger føres separat fra tekniske kontroller. | #21, #30, #32–36 |

Pakke 2 og 4 kan utvikles uavhengig etter at kandidatidentiteten er avklart. Pakke 3 må ligge til grunn for utforming av kontaktkortene. Pakke 7 er et eget senere motorløp; mer live discovery, flere modeller, større kommuneutvalg og en ny chatflate bør ikke utvide den første leveransen nå.

## Konkret akseptanse for neste pilot

Bruk en liten ny syntetisk suite ved siden av de frosne evalueringene. Den skal minst vise følgende:

1. Kun to behovssvar er nok til å nå en forståelig, begrenset kontaktflyt uten skjult krav om ordningsnavn eller fritekst.
2. «Vet ikke», ubesvart og «Vil ikke oppgi» forblir forskjellige; ingen blir til nei/avslag.
3. En aktuell bolig-/økonomiinngang blir ikke borte fordi et sekundært spørsmål er ubesvart.
4. Mat i dag eller annen tidskritisk nødvendig utgift gir et tydelig, faglig kontrollert neste steg uten å bli medisinsk akuttfare.
5. Midlertidig usikkert opphold og manglende bolig neste døgn kan uttrykkes presist.
6. Norske tegn, flere setninger og negasjon endrer ikke betydningen i sikkerhetskontrollen på en utilsiktet måte. Uavklarte formuleringer får forsvarlig begrenset output.
7. En plan har én status; endring av et relevant svar gjør bare berørte råd ugyldige og forklarer hva som må oppdateres.
8. Planlenken virker når planen finnes, uten et eldre skjult temavalg.
9. Manglende, utdatert eller avvist kilde reduserer akkurat den berørte påstanden; andre tjenesters bevis brukes ikke som erstatning.
10. Første kontakt er lett å finne og har dokumentert alternativ når relevant kontaktpunkt er stengt, eller en ærlig opplysning om at dette ikke er kontrollert.
11. Tekst, utskrift og lagringsfil følger samme valgte innhold; syntetisk import og gjenåpning bevarer svar, utvalg og fremdrift uten automatisk lagring av sensitive opplysninger.
12. Smal skjerm, 200/400 % zoom, bare tastatur, VoiceOver og manglende JavaScript er prøvd på det eksakte bygget. Alle påståtte kontroller har observerte resultater.

For brukerprøving: Begynn med 5–8 personer i en avgrenset, moderert runde med fiktive scenarioer. Ta med personer som trenger enkelt språk eller bruker hjelpemidler. Se om de uten veiledning kan forklare neste steg, finne kontaktmåten, skille egen opplysning fra produktets forslag og lage et nyttig møtenotat. Registrer hvor de stopper og hvorfor. Mål oppgaveutførelse og forståelse; antall klikk alene er ikke et mål på hjelpsomhet.

Kildegjennomgang, teknisk funksjon og menneskelig oppgaveforståelse må få separate resultater. En teknisk grønn suite er ikke grunnlag for å oppheve BLOCKED eller hevde juridisk/klinisk godkjenning.

## Evidens, bevaring og grenser

- [Runtime-prober](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/runtime-probes.py) og [11 observerte mekanismer](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/runtime-probe-results.json).
- [Pilotprober](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/pilot-probes.js) og [åtte observerte mekanismer](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/pilot-probe-results.json).
- [Mobil-/DOM-observasjoner](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/browser-layout-observations.json) og [syntetisk eksportforhåndsvisning](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/synthetic-meeting-preview.txt).
- [GitHub-sakssnapshot](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/github-issues-snapshot.json) og [main-sammenligning](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/github-main-comparison.json).
- [Manifestkontroll av begge pilotene](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/pilot-manifest-results.json): 44 innganger og én utgang per variant, uten avvik.
- [Bevaringskontroll](/Users/reidar/Projectos/NAVigator/audits/2026-10-08/preservation-results.json): utvalgte 172 runtime-, register-, manifest- og pilotfiler sammenlignes før/etter. Dette er ikke en bytekontroll av hele arkivet.

De 19 mekanismekontrollene fullførte sine assert-betingelser. Flere betingelser er laget for å bekrefte en feil; resultatet skal derfor ikke beskrives som «produktet består 19 tester». Pilotene ble åpnet fra en lokal server som bare eksponerte de to aktuelle HTML-filene.

Det er ikke gjort produktkodeendringer, regenerering, opplåsing, ny blindmåling, privat retrieval, modellkall, GitHub-mutasjoner, commit, publisering eller deploy. Eksisterende arbeidskopi og arkiver skal bevares. Nye filer er denne rapporten og gjennomgangens evidens; Obsidian får en separat kort logg.

Gjennomgangen er omfattende på arkitektur, viktige korrekthetsgrenser og den primære observerte pilotflyten. Den er ikke en linje-for-linje kontroll av hele kunnskapskorpuset, alle eldre pilotpakker, hver kommunerute eller en faglig vurdering av personlige saker.
