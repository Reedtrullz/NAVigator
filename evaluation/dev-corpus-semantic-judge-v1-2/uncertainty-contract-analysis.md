# Uncertainty contract analysis (V1.2)

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
