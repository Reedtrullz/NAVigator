# Relation Contract v2 (FROZEN)

Task: NAV-EXPLORE-RC3_1-GENERALIZED-RELATION-CLASS-REPAIR. Frozen before any runtime change. Metric definitions in relation-metrics-v2.json are immutable for this task.

## 1. Core separation

Three outputs are independent and none may substitute for another:

1. SEMANTIC RELATION (atom level): what the source proposition establishes relative to the claim atom.
2. SUPPORT BOUNDARY (frozen, candidate-boundary/): whether auto-support is safe on scope/modality dimensions.
3. PROOF ELIGIBILITY / PRODUCT ACTION: AUTO_SUPPORT_ELIGIBLE iff semantic_relation == ENTAILS AND boundary == BOUNDARY_COMPATIBLE; product labels (AUTO_SUPPORTED, AUTO_CONTRADICTED, REVIEW_REQUIRED, ABSTAIN_INSUFFICIENT) are routing, not relation.

A blocked boundary does NOT force the relation to insufficient. An ENTAILS relation does NOT bypass the boundary. The engine must emit relation and boundary as separate fields per atom.

## 2. Relation vocabulary (canonical, atom level)

- ENTAILS: the source proposition establishes the claim atom under its relevant qualifiers, following the directional modality lattice (section 5).
- CONTRADICTS: the source proposition gives POSITIVE incompatibility with the claim atom (section 6). Insufficient support alone never yields CONTRADICTS.
- PARTIAL: the source establishes only an explicit semantic part of the single atom, where the atom contract permits partiality (section 8). PARTIAL is never a synonym for uncertain.
- RELATED_BUT_INSUFFICIENT: the source addresses the right theme/entity but establishes neither the claim nor its negation within proof doctrine.
- AMBIGUOUS: two or more plausible proposition interpretations block a safe classification (section 9).

Legacy UNRELATED (no lexical-topical overlap) remains an engine pre-relation state; fresh suite cases all have relevant evidence by construction, so UNRELATED does not appear in relation scoring there.

## 3. Atom-level metric

ATOM_RELATION_ACCURACY = exact correct semantic relation / all expected claim atoms (single-atom cases count one atom; compound cases count each expected atom separately). This is not product accuracy, auto eligibility accuracy, proof-safe accuracy, or top-level compound verdict. product_aggregation_accuracy, support_boundary_precision, and proof_eligibility_accuracy are separate counters (relation-metrics-v2.json) and none may be redefined mid-task.

## 4. Proposition dimensions used by the relation classifier

actor, predicate, object/value, polarity, modality, condition, exception, temporal scope, locality/organizational scope, numeric semantic identity. The relation classifier compares these dimensions semantically; the frozen boundary computes its own dimension states for eligibility. Same inputs, different output semantics.

## 5. Directional modality lattice (relation entailment)

Licensed entailment directions (source establishes weaker claim):
- REQUIRED -> PERMITTED, POSSIBLE
- ENTITLED -> POSSIBLE
- CONDITIONAL_ENTITLEMENT -> ENTITLED only when the condition is inherited/bound by the claim context; otherwise the claim is not established unconditionally
- DEFAULT_RULE -> REQUIRED/PERMITTED only when the default is explicitly binding

Not entailment (reverse or lateral):
- PERMITTED -> REQUIRED, ENTITLED
- POSSIBLE -> ENTITLED, REQUIRED
- CONDITIONAL_ENTITLEMENT -> unconditional ENTITLED
- DISCRETIONARY -> any deontic upgrade

Modality weakness alone (source weaker than claim, no positive conflict) is not contradiction: the claim is simply not established (RELATED_BUT_INSUFFICIENT, or PARTIAL where section 8 applies).

## 6. Contradiction obligation

CONTRADICTS requires positive incompatibility, limited to:
- explicit negation governing the same predicate/clause (claim X vs source ikke-X, or reverse)
- incompatible same semantic numeric quantity (amounts, ranges, deadlines, counts)
- PROHIBITED vs REQUIRED/PERMITTED, or NOT_REQUIRED vs REQUIRED, on the same proposition and scope (doctrine-listed deontic opposition)
- mutually exclusive temporal or scope facts (e.g., payment in advance vs in arrears for the same period)
- exhaustive exclusion (claim situation falls inside a stated exception that excludes it)

"Not enough support" is never CONTRADICTS. A boundary MISMATCH on actor, condition, temporal, locality, or weak-modality dimensions without positive incompatibility is NOT contradiction.

## 7. Negation binding

Negation binds to the predicate/clause it governs (same model as boundary-contract-v1 section 5). A polarity flip on the aligned predicate is positive incompatibility and may yield CONTRADICTS; a negation elsewhere in the source text does not.

## 8. PARTIAL rule (explicit justification required)

PARTIAL is permitted at atom level only for these shapes, each with a recorded justification:
- conditional establishment: source establishes the proposition only under a condition the claim does not carry
- sub-part unresolved: claim asserts X "uten Y" / with an unresolved sub-object; the main predicate is established, the sub-part is not
- universal vs alternative subset: claim asserts a universal; evidence establishes an alternative/subset covering part of the extension
- partially matched compound rows: some product/row quantities match, others unresolved

If the claim atom is canonical atomic with no sub-part structure, PARTIAL is forbidden; use ENTAILS, CONTRADICTS, RELATED_BUT_INSUFFICIENT, or AMBIGUOUS.

## 9. AMBIGUOUS rule

AMBIGUOUS only when the source (or claim) supports two or more plausible propositions with different relation outcomes and the engine cannot resolve them: explicit alternative constructions ("eller X" ambiguity), unresolved discretionary scopes on the aligned predicate, or intrinsically ambiguous reference. An unresolvable boundary dimension alone is not ambiguity; absent a second plausible reading it maps to RELATED_BUT_INSUFFICIENT.

## 10. Compound handling

1. canonical decomposition (existing frozen decomposition), 2. classify each atom independently through this contract, 3. deterministic top-level aggregation per the existing frozen aggregation law. The parent claim is never classified first and atoms repaired afterwards.

## 11. Safety invariants (must hold after repair)

- No new ENTAILS classification bypasses support boundary: eligibility remains relation==ENTAILS AND boundary==BOUNDARY_COMPATIBLE.
- CONTRADICTS classification does not by itself authorize AUTO_CONTRADICTED; existing contradiction-proof requirements remain.
- The frozen boundary layer, reviewer, fusion, product routing, abstain routing, and confidence thresholds are untouched.

## 12. Failure taxonomy (fixed labels)

RELATION_BOUNDARY_COLLAPSE, WRONG_MODAL_LATTICE, NEGATION_RELATION, CONDITION_RELATION, EXCEPTION_RELATION, ACTOR_RELATION, SCOPE_RELATION, NUMERIC_RELATION, TEMPORAL_RELATION, PARTIAL_MISUSE, INSUFFICIENT_MISUSE, COMPOUND_AGGREGATION, OTHER.
