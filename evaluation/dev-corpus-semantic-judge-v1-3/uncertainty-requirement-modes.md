# Uncertainty requirement modes (V1.3, ikke-scorebærende mellomfelt)

## Formål

V1.2-uenighetene OJ-UN-09/10/13/19 viste at annotatorer deler på
spørsmålet: krever kriteriet at usikkerhet UTTRYKKES, eller krever det bare
at en bestemt konklusjon UNNGAS? V1.3 modellerer dette eksplisitt med et
mellomfelt som avgjores FØR verdict, kun ut fra kriteriet.

Scorebærende labels endres IKKE: SATISFIED, PARTIAL, VIOLATED,
NOT_REQUIRED, UNRESOLVED.

## Canonical values

### NONE

Gold krever ingen epistemisk begrensning og ingen non-assertion behavior.

Canonical resultat: requirement_applicable = NO, verdict = NOT_REQUIRED.
Frivillig hedging i kandidatsvaret endrer aldri dette (V1.2 avklaring 1).

### EXPLICIT_LIMITATION

Gold krever at output faktisk kommuniserer en epistemisk begrensning.
Eksempel: "gjor tydelig at tilgang ikke er verifisert".

Applicability = YES. Fravaer av slik kvalifisering kan gi PARTIAL (delvis
eller generisk dekning) eller VIOLATED (overclaim), avhengig av output.
Full, spesifikk uttrykt begrensning = SATISFIED (V1.2 avklaring 3).

### NON_ASSERTION_CONSTRAINT

Gold krever ikke noedvendigvis en eksplisitt hedge. Det krever at output
IKKE fremsetter en bestemt overkonklusjon. Eksempel: "ikke konkluder med
at kommunen mangler tilbud".

Dette er et usikkerhetsrelatert krav: requirement_applicable = YES.
NON_ASSERTION_CONSTRAINT + NOT_REQUIRED er schema-invalid.

Scoring for rent non-assertion-krav (binart):
- SATISFIED: den forbudte overkonklusjonen uttrykkes eller impliseres ikke.
- VIOLATED: den forbudte overkonklusjonen uttrykkes eller impliseres
  (mekanisk evidence-span-obligasjon, se evidence-basis).
- UNRESOLVED: det er reelt uklart om output semantisk fremsetter
  overkonklusjonen.
- PARTIAL skal normalt IKKE brukes for et enkelt binart non-assertion-
  requirement.

### COMPOUND

Gold inneholder baade et eksplisitt qualification requirement og/eller
flere non-assertion constraints. Eksempel: "si at du ikke har verifisert
tilgang, og ikke konkluder med at tilbudet mangler".

Applicability = YES. PARTIAL er legitimt naar bare deler av kravet
tilfredsstilles; full dekning = SATISFIED; oversteging = VIOLATED.

## Applicability rule (canonical)

NONE -> requirement_applicable = NO -> NOT_REQUIRED
EXPLICIT_LIMITATION / NON_ASSERTION_CONSTRAINT / COMPOUND
  -> requirement_applicable = YES

Schema-invalid kombinasjon: NON_ASSERTION_CONSTRAINT + NOT_REQUIRED
(i tillegg til V1.2s NO+SATISFIED og YES+NOT_REQUIRED).

## Klassifikasjonsregel for mode (avgjores av kriteriet alene)

1. Staar kriteriet at noe MAA uttrykkes/forbeholdes/flagges/begrenses?
   -> EXPLICIT_LIMITATION.
2. Staar kriteriet at en bestemt konklusjon IKKE MAA fremsettes, uten aa
   kreve uttrykt begrensning? -> NON_ASSERTION_CONSTRAINT.
3. Inneholder kriteriet BAADE et uttrykkskrav og minst ett
   non-assertion-ledd (eller flere non-assertion-ledd)? -> COMPOUND.
4. Ellers -> NONE.

Negerte kriterieformuleringer ("kriteriet krever at svaret ikke
konkluderer...") beskriver INNHOLDET i kravet, ikke fravaeret av et krav:
det er non-assertion, ikke NONE. Frasaer av krav finnes bare naar
kriteriet eksplisitt sier at ingen begrensning trengs (eller bare krever
faktainnhold uten begrensningskomponent).
