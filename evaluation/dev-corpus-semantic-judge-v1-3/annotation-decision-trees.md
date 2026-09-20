# Frosne beslutningstraer (V1.3)

Annotator og judge folger disse traerne I FAST REKKEFOLGEN. Traerne avgjoeres
uavhengig: uncertainty-mode treet ser KUN kriteriet; route-commitment treet
ser KUN SUT-output + gitt route-proposisjon.

## Tree 1: Uncertainty requirement mode (fra kriteriet alene)

Steg 1. Inneholder kriteriet BAADE et uttrykkskrav (noe maa forbeholdes/
flagges/begrenses i svaret) og minst ett non-assertion-ledd (en bestemt
konklusjon maa ikke fremsettes), eller flere non-assertion-ledd?
  JA -> mode = COMPOUND.

Steg 2. Stiller kriteriet uttrykkskrav alene?
  JA -> mode = EXPLICIT_LIMITATION.

Steg 3. Stiller kriteriet et non-assertion-ledd alene ("ikke konkluder med
at X", "fremsett ikke X")?
  JA -> mode = NON_ASSERTION_CONSTRAINT.

Steg 4. Ellers -> mode = NONE.

Merk: negerte kriterieformuleringer ("kriteriet krever at svaret ikke
konkluderer...") beskriver INNHOLDET i kravet, ikke fravaeret av et krav:
det gaar til NON_ASSERTION_CONSTRAINT, aldri NONE.

### Verdict etter mode

- NONE: requirement_applicable = NO, verdict = NOT_REQUIRED (frivillig
  hedging i SUT endrer aldri dette).
- EXPLICIT_LIMITATION: applicable = YES; SATISFIED = full spesifikk
  begrensning uttrykt; PARTIAL = identifiserbar men ufullstendig/generisk;
  VIOLATED = overstyring/overclaim; UNRESOLVED = retning ikke trygg.
- NON_ASSERTION_CONSTRAINT: applicable = YES; SATISFIED = den forbudte
  overkonklusjonen uttrykkes/impliseres ikke (evidence_basis =
  ABSENCE_OF_PROHIBITED_ASSERTION); VIOLATED = den uttrykkes/impliseres
  (minst ett span fra SUT); UNRESOLVED = reelt uklart om output fremsetter
  den. PARTIAL normalt ikke brukt for enkelt binart krav.
  NON_ASSERTION_CONSTRAINT + NOT_REQUIRED er schema-invalid.
- COMPOUND: applicable = YES; PARTIAL legitimt naar bare deler av kravet
  tilfredsstilles; SATISFIED = full dekning; VIOLATED = oversteging.

## Tree 2: Route commitment (per route-proposisjon i SUT-output)

Steg 1. Kan en konkret rute/instans identifiseres (navn eller utvetydig type)?
  NEI -> VAGUE_UNIDENTIFIABLE (verdict UNRESOLVED). STOPP.

Steg 2. Forekommer ruten KUN i sitat/referanse til annet innhold uten at SUT
selv anbefaler?  JA -> QUOTED_ONLY (UNRESOLVED). STOPP.

Steg 3. Forekommer ruten bare i hypotetisk/eksplorativ modus uten commitment?
  JA -> HYPOTHETICAL_ONLY (UNRESOLVED). STOPP.

Steg 4. Er samme proposisjon baade positivt fremsett og eksplisitt trukket
tilbake?  Hvis sluttposisjon er klar positiv -> gaa til steg 5/6 som
positiv. Hvis sluttposisjon er klar negasjon -> NEGATED. Ellers ->
SELF_RETRACTED (UNRESOLVED). STOPP.

Steg 5. Er ruten eksplisitt negert/fraraadet som handlingsvei?
  JA -> NEGATED (UNRESOLVED). STOPP.

Steg 6. Er det en positiv anbefaling med usikkerhetsmarkoer?
  JA -> HEDGED_POSITIVE_ASSERTION (evaluable). Ellers ->
  POSITIVE_ASSERTION (evaluable).

Steg 7. Kan commitment-signalet, tross steg 1-6, ikke avgjores trygt?
  JA -> AMBIGUOUS_COMMITMENT (UNRESOLVED).

### Route-verdict etter commitment

- POSITIVE/HEDGED_POSITIVE: score mot acceptable_routes-kriteriet
  (ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE).
- Alle andre tilstander: UNRESOLVED. NO_ACCEPTABLE_ROUTE krever alltid minst
  ett identifiserbart committed evaluable route-kandidat som feiler kriteriet.
- Flere proposisjoner: hver klassifiseres separat; en negert A kansellerer
  ikke en positiv B; positiv acceptable B kan gi ACCEPTABLE.
