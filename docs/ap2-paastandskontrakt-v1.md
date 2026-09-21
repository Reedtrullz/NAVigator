# AP2: paastandskontrakt for eksportkandidat v1 revisjon1 (UTKAST)

Status: UTKAST, ikke commitet, pa grenen codex/ap2-paastandskontrakt-694d080
(baseline 694d080). distribution_gate er BLOCKED. Dokumentet registrerer
bevisstatus og foreslaatt disponering per paastand; det er ikke faglig
godkjenning. Full raddata ligger i data/verifikasjonsregister-v2.json med
skjema i data/verifikasjonsregister-v2.schema.json.

## Grenser

- Ingen faglig kontrollor er attestert; agentkrysskontroll erstatter ikke
  fagkontroll (se non_claims i registeret).
- Manglende felt er UKJENT; ingen kontrolldato eller rolle er generert.
- Kontrolldatoer arvet fra etappekontroller og kildefiler er uendret.
- Ingen publikasjonsprofil, runtime-peker eller eksportpakke er endret.

## Validering (20.09)

- AJV draft-07: PASS pa hovedfil.
- Semantiske sjekker: PASS (unike ID-er, parent/v_refs-ankre mot register-v1,
  P1-P15 dekket via klasser-arrayet, BEHOLD krever niva ikke UKJENT/
  IKKE_GJENNOMFORT, foreslaatt ordlyd skiller seg fra observed_text,
  P11-dobbelttellingsnotat, non_claims om manglende faglig kontrollor).
- Negativtester pa kopier: duplisert ID og ukjent v_ref feiler semantikk;
  ugyldig disponering og godkjenning uten grunnlag feiler skjema.
- Filhashes i occurrences er beregnet ferskt fra eksportpakken 20.09 og
  samsvarer med pakkehashene fra AP1-kontrollen.

## Behandlingsoversikt

26 paastander: 14 BEHOLD_SOM_KANDIDAT, 9 BEGRENS, 2 KREVER_AP3,
1 UTELAT_FRA_HANDLINGSSTOTTE. Alle 15 D-klasser er dekket. P11 folger
dobbelttellingsnotat: APEN+P11-radene i talloppsummeringen er dobbelttelling
av P11, ikke en 16. klasse. P14-utelatelsen (PC-025) betyr at detaljpstanden
ikke er handlingsstoette; sporsmaalet er dermed ikke loset.

## Prioritert AP3-liste

Prioriteten folger handlingskonsekvens: rettigheter og frister med lovanker
forst, deretter dokumenterte motsigelser, skatt, satser og lokal info.

### 1. PC-020 (P11, BEGRENS): husleieloven SS 9-7/9-8/9-11

- Sporsmaal: Er formkravene til oppsigelse, protestretten (1 maned) og
  varselsadgangen (2 ukers regelen) korrekt gjengitt og fortsatt gjeldende?
- Bevis: dokumentert Lovdata-lesing 30.08.2026 registrert i fil 57:41 og
  legal-index (hul); ikke registerfort i V-registeret.
- Mangel: ingen registerfort kontroll; ingen faglig kontrollor.
- Kildetype/fagkompetanse: STATUTE; krever juridisk kompetanse.
- Tidsperiode: Lovdata lest 30.08.2026.
- Betydning: handlingsbaerende frister for leietakere i okonomisk krise.
- Fallback: behold som KILDEHENVISNING_I_FIL med BEGRENS til registrert.

### 2. PC-019 (P11, BEGRENS): sosialtjenesteloven SS 17-19

- Sporsmaal: Er retten til opplysning, rad og veiledning (stl. SS 17) og
  stonadsbestemmelsene (SS 18-19) korrekt gjengitt og gjeldende?
- Bevis: tekst sitert i fil 57:23 og 57:38; ingen datert kildelesing
  registrert for linje 23.
- Mangel: ingen datert lesing, ingen registerfort kontroll.
- Kildetype/fagkompetanse: UKJENT kildestatus; krever juridisk kompetanse.
- Tidsperiode: ikke datomerket i fil 57.
- Betydning: rettighets- og fristerstoff for okonomisk sosialhjelp.
- Fallback: BEGRENS videre; verifiser mot Lovdata forut for bruk.

### 3. PC-014 (P9, KREVER_AP3): smabarnstillegg aldersvilkaar

- Sporsmaal: Gjelder smabarnstillegg for barn 0-3 ar (fil 54:53) eller
  1-5 ar (fil 51:20)?
- Bevis: OBSERVERT_KONFLIKT innenfor pakken; satsen er konsistent
  (8 544/12 = 712 kr/mnd), vilkaret er ikke.
- Mangel: gjeldende nav.no-vilkaar ikke kontrollert; ingen fagkontroll.
- Kildetype/fagkompetanse: NATIONAL_GUIDANCE; NAV-fagkompetanse.
- Tidsperiode: satser fra 01.02.2026 i begge filer.
- Betydning: feil vilkaar kan gi feil soknadsrading for smabarnsforeldre.
- Fallback: KREVER_AP3; radene PC-013/PC-014 skal ikke brukes
  handlingsstoettende for vilkaret for AP3 er loset.

### 4. PC-018 (P10, KREVER_AP3): skatt pa mottatt barnebidrag

- Sporsmaal: Skattebehandling av etterbetaling, saerbidrag, bidrag til barn
  over 18 ar og bidragsforskudd.
- Bevis: fil 66:85 peker til fil 69 punkt 2.3; kjernen (ikke skattepliktig
  mottaker, ikke fradrag for betaler) er verifisert mot skatteloven
  skatteloven SS 5-42/5-43 og Skatteetaten lest 30.08.2026.
- Mangel: undersporsmalene er ikke separat verifisert.
- Kildetype/fagkompetanse: NATIONAL_GUIDANCE; skattefagkompetanse.
- Tidsperiode: kilder lest 30.08.2026.
- Betydning: skattekonsekvenser pafolger mottaker direkte.
- Fallback: vis kun til kjernen; undersporsmalene rutes ikke.

### 5-9. Satsrader (BEGRENS): PC-012, PC-013, PC-015, PC-016, PC-017

- Sporsmaal: Er satsene fortsatt gjeldende (barnetrygd 01.02.2026,
  smabarnstillegg 712 kr/mnd, barnebidrag-status 25.08.2026,
  bidragsforskuddstabellen, samvaersfradrag fra 01.07.2026)?
- Bevis: KILDEHENVISNING_I_FIL (nav.no oppgitt i fil 54/48/50/49); ingen
  registerfort kontroll i AP2.
- Mangel: ikke registerfort; ingen datert agentkontroll; PC-017 har i tillegg
  forbehold om at NAV ikke publiserer offisiell netttabell per klasse.
- Kildetype/fagkompetanse: NATIONAL_GUIDANCE; NAV-satskompetanse.
- Tidsperiode: 01.02.2026 (barnetrygd), 25.08.2026 (barnebidrag-status),
  01.07.2026 (samvaersfradrag), PC-016 ikke datomerket.
- Betydning: feil sats gir direkte feil okonomisk informasjon.
- Fallback: BEGRENS til satskontroll og registrering er gjort; PC-017 skal
  peke pa kalkulatoren, ikke per-klasse nettnoyaktighet.

### 10-11. Lokale rader (BEGRENS): PC-023, PC-024

- Sporsmaal: Er RPH 18+ (Trondheim) og BUP-poliklinikk-kontaktinfo fortsatt
  korrekt?
- Bevis: lagret etappekontroll 30.08.2026 (Trondheim-etappe); ikke frosset
  utvalg.
- Mangel: datert bakgrunn; ingen ny lokal kontroll; ingen fagkontroll.
- Kildetype/fagkompetanse: LOCAL_SERVICE_FACT; lokal helsetjenestekompetanse.
- Tidsperiode: kontroll 30.08.2026.
- Betydning: kontaktinfo og aldersgrenser styrer lokal ruting.
- Fallback: BEGRENS; ny lokal kontroll forut for lokal handlingsstoette.

### 12. PC-025 (P14, UTELAT): gjeldsdetaljer

- Eierbeslutning, ikke ren AP3: detaljpstanden (gjeldsordning via
  namsmann/tingrett) er eksplisitt ikke verifisert i fil 00:40. Uelates fra
  handlingsstoette; generell ruting (okonomiradgiving/NAV, stl. SS 17-anker)
  kan beholdes uten detaljpstanden. Utelatelsen loser ikke gjeldssporsmaalet.

## AP5-endringsliste

1. Registerkopi av V-004: eksportpakken data/verifikasjonsregister-v1.json
   har gammel ordlyd (Meklingsattest er krevet for rettslig gyldig avtale).
   Overfor korreksjonene fra 6e1f78a og 694d080 (tvangskraft-tekst i fil 34
   er korrekt) ved neste eierautoriserte pakkebygg.
2. Registerkopi av V-005: feltendring er rapportert men IKKE funnet i
   694d080-diffen. Dokumenteres som avvik; ikke fabrikkrer feltendring.
3. Protokollfil data/18-23-korrigeringsprotokoll-v1.json: overfor
   kommuneidentitet-korreksjonene fra 694d080 (kommunenumre,
   identity_corrections_summary, Steinkjer 5421 -> Lierne 5042,
   parent_selection_file vs derived_service_dataset, consumer_check).
4. Fil 00, 26 og 64: behold scrub-tilstanden; bevare 26:40
   Alarmtelefon-presisering som kildebelagt forskjell. Ikke erstatt med raa
   kildefiler.
5. Smabarnstillegg-motsigelsen (PC-014) er nytt funn fra AP2 og gaar til AP3;
   ingen eksportfil skal redigeres som del av det.

## Ikke-claims

Se non_claims i data/verifikasjonsregister-v2.json. Ingen paastand er faglig
godkjent; BEHOLD_SOM_KANDIDAT er disponeringsforslag, ikke godkjenning;
distribution_gate forblir BLOCKED.
