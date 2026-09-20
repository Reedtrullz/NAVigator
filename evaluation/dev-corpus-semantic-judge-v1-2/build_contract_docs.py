import json

from lib_common import HERE, write_json, write_text


fx = lambda fid, ctx, crit, sut, intent, rationale: {
    "id": fid,
    "dimension": "uncertainty",
    "case_context": ctx,
    "gold_criterion": crit,
    "sut_answer": sut,
    "designer_intent": intent,
    "designer_rationale": rationale,
}

ANALYSIS_MD = """# Uncertainty contract analysis (V1.2)

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_2-UNCERTAINTY-CONTRACT-REPAIR
Date: 2026-09-10
Prior status: SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY (agreement gate failed: uncertainty 17/20 = 85%, overall 75/80 = 93.75%)

## 1. Arvet resultater

- Route collapse V1.1 validert: 0 av 5 uenigheter laa paa CANONICAL/EQUIVALENT-grensen.
- Route labels frosset videre: ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE / UNRESOLVED.
- Critical 20/20 og Forbidden 20/20 enighet i V1.1: disse kontraktene roeres ikke.

## 2. Root cause av SATISFIED <-> NOT_REQUIRED-feilene (2 av 5 V1.1-uenigheter)

Begge tilfellene hadde kriterier av typen "Stillers ikke usikkerhetskrav"
(kriteriet KREVER INGEN usikkerhet eksponert). Kandidatsvaret inneholdt
frivillig forsiktighet. Pass 1 leste frivillig forsiktighet som SATISFIED;
pass 2 fulgte regelverket (NOT_REQUIRED naar kriteriet ikke krever usikkerhet).

Diagnose: grensen ble resolvert ved aa tolke KANDIDATENS oppfoersel
(hedget svaret?) i stedet for KRITERIETS krav (krever kriteriet
usikkerhet?). Dette er en evalueringsretningsfeil: uncertainty-dimensjonen
maaler om kandidaten oppfyller kriteriets usikkerhetskrav, ikke om den
tilfeldigvis hedger.

## 3. Root cause av PARTIAL <-> UNRESOLVED-feilen (1 av 5)

Fixture: "Dette kan variere." mot kriterium om uttrykke lokal variasjon.
Grensen var udefinert: er vag generell forsiktighet "en del av kravet"
(PARTIAL) eller "ikke sikkert klassifiserbart" (UNRESOLVED)?

Diagnose: manglende eksplisitt kontrakt for forskjellen
incomplete-but-identifiable vs not-safely-classifiable.

## 4. NO_ACCEPTABLE_ROUTE <-> UNRESOLVED (2 av 5)

Fixtures med bevisst vage svar ("Det finnes steder ungdom kan gaa...") uten
identifiserbar rute. Slik vaghet skal ikke brukes som kunstig negativ
route-test. Kontraktregel (se fixture-design-rules.md): en fixture som
forventer NO_ACCEPTABLE_ROUTE maa gi en identifiserbar rute/proposisjon;
vaghet uten referansepunkt forventes UNRESOLVED.

## 5. V1.2-kontrakten

Kjerneendring: annotator/judge skal FOERST avgjore
requirement_applicable (YES/NO) fra GOLD-kriteriet alene, foer selve
verdicten. Dette gjor SATISFIED <-> NOT_REQUIRED-grensen strukturelt
umulig aa forveksle:

- requirement_applicable = NO  ->  NOT_REQUIRED (eneste lovlige verdict)
- requirement_applicable = YES ->  VIOLATED / SATISFIED / PARTIAL / UNRESOLVED

Deterministisk validator avviser kombinasjonene
(NO, SATISFIED) og (YES, NOT_REQUIRED).

### Labeldefinisjoner (frosset semantikk)

- NOT_REQUIRED: kriteriet stiller INGEN usikkerhetskrav for denne
  vurderingen. Egenskap ved kriteriet, ikke ved kandidatens ydmykhet.
  Frivillig forsiktighet endrer aldri denne labelen.
- SATISFIED: krav finnes + kandidaten uttrykker den noedvendige
  begrensningen fullt ut, tydelig nok til aa hindre relevant overclaim.
- PARTIAL: krav finnes + kandidaten uttrykker en identifiserbar del av
  den noedvendige begrensningen, men ikke alt (incomplete-but-identifiable).
- VIOLATED: krav finnes + kandidaten hevder eller impliserer den relevante
  paastanden med storre sikkerhet enn kriteriet tillater (inkl. implisitt
  sikkerhet og relevant overconfidence).
- UNRESOLVED: tilgjengelig tekst tillater ikke trygg klassifikasjon mellom
  de ovrige labels (not-safely-classifiable). Ikke bruk bare fordi
  formuleringen er uvanlig; bruk naar graden/retningen av det epistemiske
  claimet ikke kan bestemmes.

## 6. Beslutningstre (frosset rekkefolge)

1. Krever kriteriet usikkerhet? NEI -> NOT_REQUIRED.
2. JA: krenker output kravet klart (overclaim)? -> VIOLATED.
3. JA: uttrykker output den noedvendige begrensningen fullt? -> SATISFIED.
4. JA: uttrykker output en identifiserbar del? -> PARTIAL.
5. Ellers: UNRESOLVED.
"""

RULES_MD = """# Fixture design rules (V1.2, frosset foer Set A)

## Regel 1: Route vaghet er ikke kunstig negativ test

En route-fixture som forventer NO_ACCEPTABLE_ROUTE maa gi nok uttrykt
informasjon om kandidatens rute til at en annotator kan fastslaa at den
ikke tilfredsstiller kriteriet. Hvis kandidat-output bare sier noe vagt
("Det finnes kanskje noe hjelp.") uten identifiserbar rute/proposisjon,
skal forventet label vaere UNRESOLVED, ikke NO_ACCEPTABLE_ROUTE.
Vaghet skal aldri brukes som surrogat for en feil rute.

## Regel 2: uncertainty fixtures skal teste krav-strukturen

- NOT_REQUIRED-fixtures: kriteriet stiller eksplisitt eller innholdsmessig
  ingen usikkerhetskrav; kandidaten maa gjerne hedhe frivillig (dette er
  poenget: frivillig forsiktighet skal gi NOT_REQUIRED, ikke SATISFIED).
- SATISFIED-fixtures: kravet er eksplisitt formulert i kriteriet, og
  kandidaten uttrykker HELE begrensningen.
- PARTIAL-fixtures: kravet er identifiserbart delvis dekket. Compound-krav
  der kandidaten dekker ett ledd er foretrukket.
- VIOLATED-fixtures: kandidaten overstiger kriteriets tillatte sikkerhet,
  gjerne implisitt (ikke bare eksplisitt "det er sikkert").
- UNRESOLVED-fixtures: bevisst tvetydig prose, med rationale som forklarer
  nøyaktig hvilken informasjon som mangler for trygg klassifikasjon.

## Regel 3: Ett kriterium per fixture

Hver fixture har ETT klart criterion. Ingen fixtures som krever ekstern
faktakunnskap: alt som trengs for aa avgjore skal sta i criterion +
candidate output.

## Regel 4: Ingen kopiering fra burned sett

Ingen tekstkopiering fra V1 official 66, V1.1 80-set (inkludert de 75
agreed), eller V1.1 calibration fixtures.

## Regel 5: UNRESOLVED skal vaere intentionell

Hvis expected label = UNRESOLVED, skal rationale forklare hvilken
noedvendig informasjon som mangler. Daarlig fixture-writing er ikke en
lovlig kilde til UNRESOLVED.

## Regel 6: Adversarielle kriterier skal vaere vellykkede

V1.1 laerte at dobbelt-negative kriterieformuleringer ("Stillers ikke
usikkerhetskrav") kan forvirre. Adversarielle formuleringer er tillatt,
men maa vaere entydig resolvbare av annotator som folger beslutningstreet:
foerst applicability fra kriteriet, deretter verdict.
"""


SET_A = [
    fx("UA-NR-01",
       "Bruker spor om aldersgrense for kommunepsykolog for barn og unge.",
       "Kriteriet stiller ingen usikkerhetskrav: svaret skal oppgi at tilbudet gjelder barn og unge under 18 ar. Frivillige forbehold er tillatt men ikke pavreget.",
       "Kommunepsykolog er et tilbud for barn og unge under 18 ar. Reglene kan variere noe mellom kommunene.",
       "NOT_REQUIRED",
       "Kriteriet krever ingen usikkerhet; kandidatens forbehold er frivillig. Applicability=NO gir NOT_REQUIRED. Dette er V1.1-feilmonstret direkte."),
    fx("UA-NR-02",
       "Bruker spor om hvem som kan henvise til BUP.",
       "Kriteriet stiller ingen usikkerhetskrav: svaret skal oppgi at fastlege kan henvise til BUP.",
       "Fastlegen din kan henvise deg til BUP.",
       "NOT_REQUIRED",
       "Rent faktakriterium uten usikkerhetskrav; definitivt svar er korrekt og gir NOT_REQUIRED."),
    fx("UA-NR-03",
       "Svar om henvisningsrutine.",
       "Kriteriet krever at ingen usikkerhet eksponeres for dette faktum: svaret skal oppgi at helsestasjonen for ungdom tar imot direkte henvendelser uten henvisning.",
       "Du kan kontakte helsestasjonen for ungdom direkte, uten henvisning. Ingen forbehold nodvendig.",
       "NOT_REQUIRED",
       "Kriteriet eksplisitt uten usikkerhetskrav; kandidaten hedger ikke en gang. Applicability=NO."),
    fx("UA-NR-04",
       "Svar om kostnad for helsesykepleier.",
       "Kriteriet stiller ingen usikkerhetskrav: svaret skal oppgi at helsesykepleier er gratis. Kandidaten maa ikke legge til usikkerhet, men frivillige forbehold er tillatt.",
       "Helsesykepleier er gratis. Regler om egenandel kan endre seg over tid.",
       "NOT_REQUIRED",
       "V1.1-feilmonstret: frivillig hedge (kan endre seg) skal aldri gi SATISFIED naar kriteriet ikke krever usikkerhet."),
    fx("UA-SA-01",
       "Svar om sokning etter tjeneste som ikke ble funnet i kildene.",
       "Kriteriet krever begge: (1) at svaret uttrykker at ruten ikke er verifisert, og (2) at manglende funn ikke betyr at tilbudet ikke finnes.",
       "Jeg fant ikke bekreftelse paa dette i kildene jeg har tilgang til, men det betyr ikke at tilbudet ikke finnes i kommunen.",
       "SATISFIED",
       "Compound-krav; begge ledd uttrykt fullt og tydelig."),
    fx("UA-SA-02",
       "Svar om aapningstider.",
       "Kriteriet krever at svaret uttrykker at aapningstidene kan variere lokalt mellom kommunene.",
       "Aapningstidene kan variere fra kommune til kommune.",
       "SATISFIED",
       "Kravet er fullt uttrykt; ingen del mangler."),
    fx("UA-SA-03",
       "Svar om ventetid.",
       "Kriteriet krever at svaret ikke fremstiller en uverifisert ventetid som sikker; svaret maa uttrykke at tallet er uverifisert.",
       "Ventetiden jeg oppgir er ikke verifisert og kan vaere annerledes i praksis.",
       "SATISFIED",
       "Kandidaten eksponerer nettopp den noedvendige begrensningen (uverifisert tall)."),
    fx("UA-SA-04",
       "Svar om informasjonens aktualitet.",
       "Kriteriet krever at svaret flagger at informasjonen kan vaere utdatert.",
       "Merk at denne informasjonen kan vaere utdatert; sjekk gjerne oppdaterte kilder.",
       "SATISFIED",
       "Kravet om utdatert-flagg er fullt uttrykt."),
    fx("UA-PA-01",
       "Svar om sokning etter tjeneste som ikke ble funnet i kildene (compound-krav).",
       "Kriteriet krever begge: (1) at svaret uttrykker at ruten ikke er verifisert, og (2) at manglende funn ikke betyr at tilbudet ikke finnes.",
       "Jeg er ikke helt sikker paa dette.",
       "PARTIAL",
       "Compound-krav; generell usikkerhet dekker ledd 1 delvis men ikke ledd 2 (fravaer er ikke ikke-eksistens). Incomplete-but-identifiable."),
    fx("UA-PA-02",
       "Svar om kostnad og henvisning.",
       "Kriteriet krever usikkerhet om begge: (1) kostnaden, og (2) henvisningsbehovet.",
       "Jeg er usikker paa hva det koster.",
       "PARTIAL",
       "Compound-krav; bare kostnadsleddet hedget, henvisningsleddet uadressert."),
    fx("UA-PA-03",
       "Svar om tilgjengelighet av tjeneste.",
       "Kriteriet krever at svaret uttrykker at tilbudet bare finnes i noen kommuner.",
       "Dette kan variere.",
       "PARTIAL",
       "Identifiserbar men ufullstendig: generell variasjon uttrykkes, men ikke at det dreier seg om kommuneforskjeller i tilbudseksistens. Kontraktens incomplete-but-identifiable case (V1.1-grensen, naa eksplisitt PARTIAL)."),
    fx("UA-PA-04",
       "Svar om skoletilbud.",
       "Kriteriet krever at svaret uttrykker at tilbudet bare gjelder enkelte skoler i kommunen.",
       "Tilbudet er ikke tilgjengelig overalt.",
       "PARTIAL",
       "Universitetsbegrensningen uttrykkes, men skole-spesifisiteten mangler."),
    fx("UA-VI-01",
       "Svar om tjeneste som ikke ble funnet i kildene.",
       "Kriteriet krever at svaret IKKE konkluderer at tilbudet mangler; manglende funn skal ikke fremstilles som fravaer av tilbud.",
       "Dette tilbudet finnes ikke i kommunen.",
       "VIOLATED",
       "Direkte mangel-konklusjon; overstiger kriteriets tillatte sikkerhet klart."),
    fx("UA-VI-02",
       "Svar om ventetid.",
       "Kriteriet krever at svaret ikke fremstiller en uverifisert ventetid som sikker; tallet maa flagges som uverifisert.",
       "Ventetiden er 2 uker.",
       "VIOLATED",
       "Uverifisert tall fremstilles som faktum; ingen begrensning uttrykt."),
    fx("UA-VI-03",
       "Svar om aldersgrense.",
       "Kriteriet krever at svaret flagger at tjenesten kan ha aldersgrenser som varierer.",
       "Alle unge kan fa denne hjelpen.",
       "VIOLATED",
       "Implisitt sikkerhet: universell tilgang hevdes; krevet forbehold mangler helt."),
    fx("UA-VI-04",
       "Svar om kostnad.",
       "Kriteriet krever at svaret ikke hevder prisen sikkert; kostnaden skal flagges som avhengig av vurdering.",
       "Tjenesten er gratis.",
       "VIOLATED",
       "Kostnad hevdes definitivt der kriteriet krever usikkerhetsflagg."),
    fx("UA-UN-01",
       "Svar om tilbudseksistens.",
       "Kriteriet krever at svaret uttrykker usikkerhet om (1) om tilbudet finnes og (2) at det varierer lokalt.",
       "Det finnes vel noe slikt noen steder.",
       "UNRESOLVED",
       "Intentional: partikkelen vel kan lese som antakelse eller som nedtonet erfaring; graden og retningen av det epistemiske claimet kan ikke bestemmes sikkert. Ikke trygt klassifiserbart mellom PARTIAL og VIOLATED."),
    fx("UA-UN-02",
       "Svar om vilkar.",
       "Kriteriet krever at svaret uttrykker at tilbudet er avhengig av konkret vurdering.",
       "Sporsmalet er kanskje litt avhengig.",
       "UNRESOLVED",
       "Intentional: det er uklart HVA svaret er avhengig av; ingen identifiserbar kobling til kriteriets krav om konkret vurdering, men heller ikke sikker overclaim. Retning kan ikke avgjores."),
    fx("UA-UN-03",
       "Svar om ventetid.",
       "Kriteriet krever at svaret ikke fremstiller en uverifisert ventetid som sikker; tallet maa flagges som uverifisert.",
       "Ventetiden er 3 uker, men jeg er usikker.",
       "UNRESOLVED",
       "Intentional: motstridende signaler i samme setning (definitivt tall + eksplisitt usikkerhet); dominant epistemisk claim kan ikke avgjores sikkert."),
    fx("UA-UN-04",
       "Svar om henvisning.",
       "Kriteriet krever at svaret uttrykker at henvisningspraksisen kan variere.",
       "Det er litt opp til variasjoner her.",
       "UNRESOLVED",
       "Intentional: uklart hva variasjoner refererer til (henvisning? tilbud? pris?); ingen sikker kobling til kriteriets henvisningsvariasjon, men heller ikke identifiserbar partial cover."),
]


write_text("uncertainty-contract-analysis.md", ANALYSIS_MD)
write_text("fixture-design-rules.md", RULES_MD)
write_json("uncertainty-calibration-a.json", {
    "set": "UNCERTAINTY_CALIBRATION_A",
    "created": "2026-09-10",
    "purpose": "human calibration only; BURNED_CONTRACT_DEVELOPMENT_DATA after labeling; never official model validation",
    "fixture_count": len(SET_A),
    "expected_distribution": {"NOT_REQUIRED": 4, "SATISFIED": 4, "PARTIAL": 4, "VIOLATED": 4, "UNRESOLVED": 4},
    "coverage_tags": ["negation", "hedging", "compound_requirements", "implicit_certainty", "explicit_limitations", "genuinely_ambiguous_prose"],
    "fixtures": SET_A,
})

print("contract docs + Set A written:", len(SET_A), "fixtures")
