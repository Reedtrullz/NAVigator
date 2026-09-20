# Gate-consumption contract v1 (RC3.3)

Frozen before implementation. No metric/schema change after this
file is hashed.

## Principle

The semantic relation layer consumes a RELATION_EVIDENCE_LEDGER built
per atom from frozen boundary dimension evidence plus the new numeric
semantic quantity layer. The 3-state support boundary projection
(COMPATIBLE / BLOCKED / UNRESOLVED) is downstream safety metadata and
is never an input to relation classification. The pattern
if-boundary-then-RBI is forbidden.

## Ledger construction (deterministic)

For each atom and its aligned evidence packet, the ledger records the
per-dimension states from boundary.compare().dimension_evidence
(frozen RC3.2 behavior), one numeric relation per claim quantity from
the numeric coverage contract, clause coverage, provenance span ids,
the deterministic rule ids, and the list of unresolved dimensions.

## Relation decision procedure (ordered, first match wins)

1. clause_coverage PARTIAL_OVERLAP -> RELATED_BUT_INSUFFICIENT
   (proposition identity broken).
2. polarity EXPLICIT_CONFLICT with rule
   DE-polarity-clause-negation-consensus and a shared predicate ->
   CONTRADICTS. Exception-bounded polarity stays RBI.
3. modality DEONTIC_OPPOSITION with rule
   DE-modality-deontic-opposition and shared content -> CONTRADICTS.
4. modality SOURCE_WEAKER_THAN_CLAIM -> RELATED_BUT_INSUFFICIENT.
5. Safety caps FIRST for positive routing: condition CONDITION_MISSING,
   actor DIFFERENT_ACTOR, or scope SCOPE_CONFLICT ->
   RELATED_BUT_INSUFFICIENT (a capped atom can never be auto-entailed
   by any later layer).
6. Numeric layer: if the claim carries a semantic quantity:
   - quantity identity matches and comparator relation is CONTRADICTS
     -> CONTRADICTS (numeric conflict outranks unresolved modality).
   - quantity identity matches and comparator relation is ENTAILS ->
     ENTAILS (numeric-grounded, provenance recorded).
   - otherwise NUMERIC_RELEVANT_BUT_UNRESOLVED -> RELATED_BUT_INSUFFICIENT.
   The numeric layer runs BEFORE modality-licensed entailment so a
   licensed modality can never launder an unresolved or conflicting
   quantity into ENTAILS.

   Pre-implementation amendment (2026-09-07, before any engine edit,
   during contract self-audit per spec section 28): caps moved to step
   5 ahead of numeric entailment. Rationale: a numeric entailment must
   not bypass condition/actor/scope safety caps; a conditional or
   differently-scoped source never licenses an unconditional claim
   even when the amount matches. Contradiction from numeric conflict
   remains stronger than unresolved modality. No other step changed.
7. modality EXACT_MATCH / CONDITIONALLY_COMPATIBLE /
   SOURCE_STRONGER_THAN_CLAIM with no earlier numeric block -> ENTAILS.
8. Directional modality lattice (evidence, claim) effect:
   DEONTIC_OPPOSITION -> CONTRADICTS; WEAK -> RBI; LICENSED -> ENTAILS.
9. Generalized PROHIBITED evidence vs REQUIRED/ENTITLED claim on
   shared object -> CONTRADICTS.
10. Hard polarity opposition (claim/evidence negation asymmetry on
    aligned clause) -> CONTRADICTS.
11. No proof -> caller default RELATED_BUT_INSUFFICIENT.

## Orthogonality requirement

Semantic relation and support boundary are separate outputs. The same
gate state can carry different relation classes; the differential
test must show relation varying within at least one frozen gate state
without any change to the projection itself.

## R25 numeric bound

The coverage rule R25 (lexical coverage >= 0.5 -> ENTAILS) must not
fire when the ledger numeric relation is CONTRADICTS or
NUMERIC_RELEVANT_BUT_UNRESOLVED for any claim quantity. R25 then
falls to RELATED_BUT_INSUFFICIENT.
