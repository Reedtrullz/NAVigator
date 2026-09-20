# Route-contract rationale V1.1

## Preregistrert hypotese

Distinksjonen mellom CANONICAL_ACCEPTABLE og EQUIVALENT_ACCEPTABLE er ikke
noedvendig for correctness-scoring naar begge representerer en rute som
tilfredsstiller acceptable_routes-kontrakten.

## Produktsemantisk regel

Correctness-spoersmaalet er: fant systemet en rute som tilfredsstiller minst
een godkjent acceptable-route-semantikk? Ikke: brukte systemet samme ordlyd
eller canonical rute-ID som gold? Derfor fjernes CANONICAL_ACCEPTABLE og
EQUIVALENT_ACCEPTABLE som score-baerende labels og erstattes av ACCEPTABLE.

## V1.0 bevisgrunnlag

I V1 official validation var alle 4 route-feil og all observert
route-ustabilitet begrenset til CANONICAL_ACCEPTABLE <->
EQUIVALENT_ACCEPTABLE. Scoreren behandler allerede begge som aksept-positive
(route_equivalent returnerer True for begge). Grensen er dermed score-benign,
men skapte kunstig lav route-accuracy (76.47 %) og modal ustabilitet (87.5 %).

## Hva som endres og ikke endres

- Endres: route_equivalence labels blir ACCEPTABLE, PARTIAL,
  NO_ACCEPTABLE_ROUTE, UNRESOLVED.
- Ikke endres: critical_condition, forbidden_claim og uncertainty. Grensen
  SATISFIED <-> PARTIAL beholdes og testes separat som diagnostikk.
- Diagnostikk: route_match_detail (CANONICAL, ALIAS, SEMANTIC_EQUIVALENT,
  NONE, UNRESOLVED) kan bevares som metadata. Den inngaar ikke i correctness,
  PASS-gates eller accuracy.
- Deterministic-first videreføres: judge kalles bare naar deterministisk lag
  er UNRESOLVED, og deterministic resultat kan aldri overstyres
  (LLM_OVERRIDE_OF_DETERMINISTIC_RESULT = 0 testes mekanisk).
- ACCEPTABLE vs PARTIAL beholdes som produktrelevant grense: PARTIAL betyr
  fortsatt at ruten bare tilfredsstiller deler av kriteriet.
- Ingen absens-evidens: manglende stotte er ikke ACCEPTABLE uten positiv
  rute-evidens; separation av claim, evidence og verdict videreføres fra
  V1-systemprompten.

## Generaliserte feilklasser (designinngang, ingen case-ID-mapping)

- POSITIVE_CLAUSE_WITH_NEGATED_EXCEPTION: akseptabel hovedsetning fulgt av
  negerende unntak ("ikke krav om", "bare dersom").
- SUPPORT_PHRASE_FOLLOWED_BY_NEGATION.
- DEONTIC_QUALIFIER_OUTSIDE_MATCH: modalitet (kan/skal/maa) endres i
  tilleggssetning etter alignet fragment.
- HYPOTHETICAL_OR_QUOTED_ROUTE: rute nevnt i sitat eller hypotetisk form er
  ikke tilbudt.
- CONDITIONAL_ENDORSEMENT: betinget tilbud tilfredsstiller ikke ubetinget
  kriterium naar betingelsen ikke er gitt i casen.
- MENTION_WITHOUT_OFFER: tjeneste nevnt som eksempel er ikke tilbud.
- HYPHENATED_SEGMENT_MASKING: ordbegrenset samsvar kan feilaktig laate
  "Rask psykisk helsehjelp" dekke "psykisk helsehjelp"; ikke deterministisk
  auto-aksept, legges til judge-kriteriet.
