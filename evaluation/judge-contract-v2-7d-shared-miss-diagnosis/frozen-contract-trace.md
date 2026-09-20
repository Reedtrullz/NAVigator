# Frozen Contract Trace — V2.7D

Task: NAV-EXPLORE-JUDGE-CONTRACT-V2_7D-SHARED-MISS-DIAGNOSIS
Sources are read-only frozen artifacts; no semantics rewritten. SHA pins in baseline-integrity.json.

## A. Uncertainty (frozen V1.4 contract, sha f545b54b…)

Frozen structure: requirement_modes {NONE, EXPLICIT_LIMITATION, NON_ASSERTION_CONSTRAINT, COMPOUND}; output_behaviors {NONE, HEDGE, EXPLICIT_LIMITATION, PARTIAL_LIMITATION, CONTRADICTORY_LIMITATION, OVERCONFIDENT_ASSERTION, UNRESOLVED}; verdict derived from a frozen mode x behavior table.

Frozen EXPLICIT_LIMITATION rows (verbatim): EXPLICIT_LIMITATION→SATISFIED, PARTIAL_LIMITATION→PARTIAL, HEDGE→PARTIAL, CONTRADICTORY_LIMITATION→PARTIAL, OVERCONFIDENT_ASSERTION→VIOLATED, NONE→UNRESOLVED, UNRESOLVED→UNRESOLVED.

Frozen NON_ASSERTION_CONSTRAINT rows (verbatim): NONE→SATISFIED, HEDGE→SATISFIED, EXPLICIT_LIMITATION→SATISFIED, PARTIAL_LIMITATION→SATISFIED, CONTRADICTORY_LIMITATION→VIOLATED, OVERCONFIDENT_ASSERTION→VIOLATED, UNRESOLVED→UNRESOLVED.

Frozen clause: "PARTIAL = identifiable part of requirement fulfilled; UNRESOLVED = cannot safely determine fulfilment or violation from text; PARTIAL is never 'mild uncertainty'".

### CONTRACT_TEXT_AMBIGUITY UNC-A1
EXPLICIT_LIMITATION x CONTRADICTORY_LIMITATION is frozen-table PARTIAL, but burned V2.7 gold for both contradictory_limitation rows (UNC-46, UNC-47) is UNRESOLVED, and frozen judge_core_v2_2.py (sha 5d5bbf9d…) deterministically ships the table row (PARTIAL). The contract's own partial_vs_unresolved sentence pulls the opposite way for self-contradictions ("cannot safely determine"). The frozen artifacts do not define which authority wins. Underdetermined.

### CONTRACT_TEXT_AMBIGUITY UNC-A2
Historical fixture rows use behavior UNCLEAR_PROSE, which is not a frozen behavior value and has no derivation-table row. Under the frozen schema the only path to verdict UNRESOLVED is classifying the behavior itself as UNRESOLVED. Whether garbled-but-partially-interpretable prose must be classified UNRESOLVED (rather than PARTIAL_LIMITATION / CONTRADICTORY_LIMITATION / HEDGE) is not derivable from frozen text. Underdetermined.

The NON_ASSERTION rows themselves are unambiguous; a NON_ASSERTION row reaches UNRESOLVED only via behavior UNRESOLVED.

## B. Route (frozen V1.4 route_commitment_model)

Frozen structure: axis_a proposition_present {YES, NO, UNRESOLVED}; axis_b speaker_commitment {ASSERTED, HEDGED_ASSERTION, HYPOTHETICAL_ONLY, QUOTED_ONLY, NEGATED, SELF_RETRACTED, UNRESOLVED}; evaluable_commitments = {ASSERTED, HEDGED_ASSERTION}; all non-evaluable commitments give verdict UNRESOLVED, never NO_ACCEPTABLE_ROUTE.

Frozen hedged definition (verbatim): "hedging marker on a real commitment ('ser ut til at X er riktig sted') is evaluable; enumerative/hypothetical framing ('X kan for eksempel vaere aktuell') without preference is HYPOTHETICAL_ONLY".

Frozen self-retracted rule: same route asserted then explicitly retracted without final position => SELF_RETRACTED => UNRESOLVED.

### CONTRACT_TEXT_AMBIGUITY ROUTE-A1
The hedged definition gives exactly one example per side and no general decision procedure. Where strong hedging ("Det kan være lurt å ta det opp med fastlegen") or relevance-framing ("virker relevant i din situasjon") falls between "hedging marker on a real commitment" and "noncommittal framing" is not derivable from frozen text. This is the plausible shared-miss locus for ROUTE-22/23.

### CONTRACT_TEXT_AMBIGUITY ROUTE-A2
PARTIAL appears in the frozen verdict list but the frozen route_commitment_model defines no rule for when PARTIAL applies (no derivation table exists for route). The models' PARTIAL verdicts on evaluable hedged assertions are therefore not contract-decidable either way against ACCEPTABLE. Underdetermined.

## C. Forbidden (frozen V2.2 M1 derivation, sha 5d5bbf9d… / 75dddedb…)

Frozen table (verbatim): MATCH+ASSERTED→PRESENT; MATCH+HEDGED_ASSERTION→PRESENT; MATCH+QUOTED_ONLY→ABSENT; MATCH+HYPOTHETICAL_ONLY→ABSENT; MATCH+NEGATED→ABSENT; MATCH+SELF_RETRACTED→ABSENT; MATCH+NONCOMMITTAL→UNRESOLVED; MATCH+UNRESOLVED→UNRESOLVED; NO_MATCH+*→ABSENT; UNRESOLVED+*→UNRESOLVED. Proposition truth is irrelevant.

### CONTRACT_TEXT_AMBIGUITY FORB-A1
criterion_semantic_match is a model judgment; no frozen artifact calibrates the paraphrase-synonymy threshold for MATCH vs NO_MATCH (e.g. "støtte til yngste barn" vs "økonomisk støtte til fulle barn"). FORB-13's miss shape (DeepSeek NO_MATCH→ABSENT, MiMo match-UNRESOLVED→UNRESOLVED vs gold PRESENT) sits exactly on this uncalibrated judgment. Underdetermined.

## Registry
| ID | Family | Frozen source of tension |
|----|--------|--------------------------|
| UNC-A1 | uncertainty | table PARTIAL vs gold UNRESOLVED for contradictory limitations |
| UNC-A2 | uncertainty | UNCLEAR_PROSE not representable; behavior-classification boundary |
| ROUTE-A1 | route | hedge-strength boundary without decision rule |
| ROUTE-A2 | route | PARTIAL verdict undefined for route |
| FORB-A1 | forbidden | paraphrase MATCH threshold uncalibrated |
