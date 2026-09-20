# V1.2 boundary analysis -> V1.3 contract

## Utgangspunkt

V1.2 official annotation: 70/80 agreement (87.5%), 10 disagreements.
Terminalstatus: SEMANTIC_JUDGE_V1_2_ANNOTATION_CONTRACT_NOT_READY.
V1.2 contract (5747d8d1...815b) og prompt (08c57c44...a785) er frozen.
Set B human calibration var 20/20 etter uncertainty-reparasjonen, sa
residualgrensene er smalere enn V1.2-reparasjonen dekket.

## Disagreement-mapping

### Route (4 av 10): OJ-RT-16, OJ-RT-17, OJ-RT-19, OJ-RT-20

Pass 1 scoret definite NO_ACCEPTABLE_ROUTE/PARTIAL; pass 2 scoret UNRESOLVED
pa T vag/noytrale eller selv-motsigende tilbud (alle 5 intent-UNRESOLVED
route-fiksturer delte). Klasser: vague/unidentifiable offers, negerte rute-
referanser, self-retraction. OJ-RT-18 ble enig NO_ACCEPTABLE_ROUTE av begge
passes, men tilhoerer samme klasse og noteres.

Reparasjon: route_commitment-mellomfelt. Bare POSITIVE_ASSERTION og
HEDGED_POSITIVE_ASSERTION er evaluable; NEGATED, SELF_RETRACTED,
QUOTED_ONLY, HYPOTHETICAL_ONLY, VAGUE_UNIDENTIFIABLE og
AMBIGUOUS_COMMITMENT gir UNRESOLVED, aldri NO_ACCEPTABLE_ROUTE.

### Uncertainty (4 av 10): OJ-UN-09, OJ-UN-10, OJ-UN-13, OJ-UN-19

Applicability-splits. OJ-UN-19 er kanonisk eksempel: "kriteriet krever at
svaret ikke konkluderer med at tilbudet mangler". V1.2-treeet behandlet
negative kravformuleringer som requirement_applicable = NO, men kravet er
epistemisk reelt: det forbyr en overkonklusjon.

Reparasjon: uncertainty_requirement_mode-mellomfelt. Negativ kravformulering
beskriver INNHOLDET i kravet => NON_ASSERTION_CONSTRAINT, applicability YES,
NOT_REQUIRED er schema-invalid. NONE forbeholdes kriterier uten begrensnings-
komponent.

### Forbidden (2 av 10): OJ-FB-09, OJ-FB-17 (lav prioritet, utenfor scope)

Implicitte universelle paastandar (PRESENT vs ABSENT/UNRESOLVED). Forbidden-
contract endres IKKE i V1.3. Noteres som residual begrensning.

## Burn

Hele V1.2 official 80-settet er BURNED_CONTRACT_DEVELOPMENT_DATA
(burned-data-registry.json): kontrakten utledes direkte fra dets
disagreement-patterns, sa verken fiksturene eller tekstnaere varianter kan
brukes i V1.3 official validation. Protokollen kan gjenbrukes, dataene kan ikke.
