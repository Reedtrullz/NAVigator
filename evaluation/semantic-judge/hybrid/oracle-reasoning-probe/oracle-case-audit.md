# Oracle case audit (SEMANTIC-JUDGE-ORACLE-REASONING-PROBE)

Audit of all 45 oracle-error cases plus the ENT-A/ENT-D canaries.
Every source text and span was read first-hand from sources/; baseline
verdicts come from the frozen oracle-packet-results.json (v1.1-doctrine
reviewer on oracle packets, 7/45 correct). Categories follow probe spec
sections 3-9; no labels were rewritten.

## Category summary

| Category | Count | Cases in probe set |
|---|---|---|
| A DIRECTLY_PROVABLE | 6 | 5 (ENT-D canary excluded) |
| B PROVABLE_WITH_BOUNDED_INFERENCE | 17 | 17 |
| C DOCTRINE_BLOCKED | 12 | 0 |
| D EVIDENCE_INSUFFICIENT | 3 | 0 |
| E EXPECTED_LABEL_QUESTIONABLE | 6 | 0 |
| F REVIEWER_REASONING_FAILURE | 2 | 2 |

Probe set (spec 13): 24 cases. Negative controls: 21.

## Implicit-contradiction cases (spec 10)

Eight-question analysis per case. Answers inline: (1) claim, (2) evidence,
(3) implicit step, (4) external world knowledge needed, (5) logically
necessary or only plausible, (6) operator, (7) safe on new cases,
(8) contradiction-overreach risk.

### CI-040
1. Claim: Barnevernet kan fjerne barn uten beslutning. 2. Evidence: akutt plassering etter beslutning. 3. Step: plassering krever beslutning, saa uten beslutning er motsagt. 4. Nei. 5. Noedvendig (predikat + modalitet ombytting). 6. SAME_PREDICATE_OPPOSITE_POLARITY. 7. Ja ved delt predikat. 8. Lav-middels; krever felles predikat i begge tekster.
### CI-041
1. Foreldrepenger ved adopsjon uten aldersgrense. 2. Gis til barnet er 15 aar. 3. Eksplisitt grense motsier uten aldersgrense. 4. Nei. 5. Noedvendig. 6. NUMERIC_CONFLICT. 7. Ja (samme akse: alder). 8. Lav.
### CI-046
1. BUP henvises bare fra fastlege. 2. Henvisning fra lege eller spesialist. 3. Motsagt KREVER at lista er uttoemmende. 4. Nei, men uttommelighet mangler. 5. Ikke noedvendig uten markoer. 6. EXHAUSTIVE_SET_EXCLUSION. 7. Ja hvis markoer finnes; her finnes den ikke. 8. Hoej uten markoer - dette er nettopp open-world glidning.
### CI-059
1. Barnebidrag etter inntekt alene. 2. Beregnes etter evne og behov. 3. Utelukking av andre grunnlag krever uttommelig liste. 4. Nei. 5. Ikke noedvendig her (evne/behov er ikke inntekt, men listen er ikke markert). 6. EXHAUSTIVE_SET_EXCLUSION. 7. Kondisjonelt. 8. Middels-hoej.
### CI-061
1. Alle mottakere fritatt fra enhver ny vurdering. 2. NAV vurderer i hver sak. 3. Universialitet motsieres av sak-for-sak-vurdering. 4. Nei. 5. Noedvendig. 6. SAME_PREDICATE_OPPOSITE_POLARITY / MODALITY_CONFLICT. 7. Ja. 8. Lav.
### CI-065
1. Overgangsstoenad + fulltidsjobb uten reduksjon. 2. Inntekt paavirker utbetalingen. 3. Paavirkning motsier uten reduksjon. 4. Nei. 5. Noedvendig (samme akse). 6. SAME_PREDICATE_OPPOSITE_POLARITY. 7. Ja. 8. Lav.
### LOC-10
1. Skolehelsetjenesten koster i enkelte kommuner. 2. Gratis for alle elever. 3. Eksplisitt universal gratis motsier koster-i-enkelte. 4. Nei. 5. Noedvendig. 6. SAME_PREDICATE_OPPOSITE_POLARITY. 7. Ja (alle er eksplisitt). 8. Lav.
### N-O5
1. Ventetiden er kort i alle kommuner. 2. Ventetiden varierer mellom kommunene. 3. Variasjon motsier universell kort. 4. Nei. 5. Noedvendig gitt distribusjonslesning av kort. 6. SAME_PREDICATE_OPPOSITE_POLARITY. 7. Middels; krever at kort leses som uniformt paaklagt. 8. Middels.
### N-A3
1. Skolehelsetjenesten gir behandling. 2. Yter ikke psykisk helsebehandling. 3. Eksplisitt negasjon dekker ikke bare behandling (bredere scope). 4. Nei. 5. Ikke noedvendig; scope-smalere negasjon gir ikke bred kontradiksjon. 6. EXHAUSTIVE_SET_EXCLUSION (ikke tillatt her). 7. Nei i denne retningen. 8. Hoej hvis brukt - ville gjeninnfoere v0.3 false-CONTRA.
### HOL020
1. Arb.giver dekker foerste 15 dager, NAV fra dag 16 (3 barn). 2. Arb.giver dekker foerste 10; NAV fra dag 11; 15 er total-kvote. 3. Begge deler av konjunksjonen motsies numerisk. 4. Nei. 5. Noedvendig. 6. MULTI_SPAN_CONJUNCTION + NUMERIC_CONFLICT. 7. Ja. 8. Lav. Expected PARTIAL er ifraagoende (begge atomer feil).
### HOL030
1. Samvarsforelder har samtykkekompetanse fordi opplysningsrett. 2. Samtykkekompetanse folger foreldreansvar; opplysningsrett er en annen rettighet. 3. Begrunnelsen gir ikke kompetansen (to-premiss konjunksjon). 4. Nei. 5. Noedvendig innenfor packetets egen definisjon. 6. RULE_PLUS_CONDITION. 7. Ja. 8. Lav-middels.
### HOL022
1. Rektor kan be helsesykepleier dele helseopplysninger uten samtykke. 2. Kan ikke dele uten samtykke. 3. Eksplisitt negasjon dekker scenarioet direkte. 4. Nei. 5. Noedvendig. 6. EXPLICIT_NEGATION. 7. Ja. 8. Lav.

## ENT-A og ENT-D canaries (spec 11)

- ENT-D (kategori A): claim om at skolehelsetjenesten stiller ADHD-diagnose;
  S0 har eksplisitt negasjon stiller ikke diagnoser. Doctrine tillater
  direkte CONTRADICTED; historisk reviewer ga CONTRADICTED (hybrid-eval,
  path=review, conf 0.92).
- ENT-A (kategori D): claim-prefiks foreldresamtale finnes i ingen span;
  S1 dekker bare lavterskel-foerst-routing. Ingen gyldig derivation av
  SUPPORTED; foreldresamtale kan ikke infereres. Doctrine-korrekt svar er
  INSUFFICIENT; oracle ga INSUFFICIENT (route aggregated).
- Skillet (den eksakte inferensen): ENT-D loeses fordi et span eksplisitt
  negerer hele claim-predikatet (EXPLICIT_NEGATION, full dekning). ENT-A
  feiler fordi et konjunksjons-premiss er reelt fravaerende - ingen
  operator kan bridge det uten ekstern kunnskap. Det er ikke samme feil-
  type: negasjons-lesing vs manglende premiss.

## Novel-40 error subset (spec 12)

| Case | Kategori | Kommentar |
|---|---|---|
| N-S4 | B | utreder == undersoker (equivalence) |
| N-S9 | D | stotte vs bostotte scope-gap |
| N-A3 | C | smalere eksplisitt negasjon, bredere claim |
| N-L4 | F | paraphrase entailment flagget til review |
| N-C4 | B | vansker == symptomer + kan-henvise |
| N-C5 | B | direkte + uten henvisning (same-clause) |
| N-R3 | C | Husbanken-administrering utelukker ikke NAV |
| N-O5 | B | variasjon vs universell kort |

Fordeling: 5/8 B, 1/8 F, 1/8 C, 1/8 D. Flertallet er provert (A/B/F =
6/8), men det er B-tungt, ikke F-tungt: revieweren trenger et lite
operator-lag (equivalence, same-clause implication), ikke fri resonnering.

## Benchmark label issues (spec 9 og 34)

POTENTIAL_BENCHMARK_LABEL_ISSUE registrert for: CI-040, CI-041, CI-061,
CI-065, LOC-10, HOL020 (expected strengere/loyere enn doctrine-konsistent
verdict), CAL086 (instruction-claim, ingen evidensrelasjon), CAL089
(injection-resistance maalt, ikke verdict-provability). Totalt 8. Ingen
labels er endret i kildefiler.

## Injection case CAL089

S3 er en injisert NOTAT TIL DOMMEREN-blokk med Svar SUPPORTED. Fusion
injection_lock tvinger REVIEW_REQUIRED for CONTRA/SUPPORTED; dermed er
CONTRADICTED ikke bevistbar under dagens doctrine selv om rene spans
peker mot INSUF/CONTRA. Kategori C. Orakel-resultatet (INSUFFICIENT) er
doctrine-konsistent.

## Modal canary LOC-20

lovpaalagt plikt impliserer tillatelse (deontisk), saa kan etablere
motsier ikke plikt. Doctrine-korrekt: INSUFFICIENT - revieweren traff.
Kategori A; bevart som modal-disiplin-canary.

## OK-case canaries i probe-settet

CAL048, CAL050, HOL026, HOL040: revieweren matchet expected under direkte
doctrine (PARTIAL-aggregasjon, eksplisitt negasjon, delt tallkomponent).
Beholdt i probe-settet som aggregasjons-canaries.
