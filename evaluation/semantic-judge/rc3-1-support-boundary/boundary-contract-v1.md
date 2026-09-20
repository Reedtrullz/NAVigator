# Boundary Contract v1 (FROZEN)

Task: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR. This contract is frozen before implementation. Metric definitions in boundary-metrics-v1.json are immutable for this task.

## 1. Propositions

Both the claim atom and each candidate source match are normalized to a proposition with dimensions: actor, predicate, object_value, polarity, modality, temporal_scope, locality_scope, conditions, exceptions, numeric_quantity_identity, clause_span. Any dimension may be UNKNOWN. UNKNOWN never counts as a MATCH.

## 2. Boundary dimensions and allowed values

Per-dimension results: MATCH, LICENSED_ENTAILMENT, MISMATCH, UNKNOWN, NOT_APPLICABLE.

overall = BOUNDARY_COMPATIBLE iff every relevant dimension is MATCH, LICENSED_ENTAILMENT, or NOT_APPLICABLE. Any MISMATCH or UNKNOWN on a relevant dimension yields overall != BOUNDARY_COMPATIBLE, and AUTO_SUPPORTED is forbidden for that proof. The engine then returns SEMANTIC_PROOF_UNRESOLVED (or another explicit non-auto proof state), failing closed.

## 3. AUTO_SUPPORTED eligibility

A support proof is eligible only if: (1) the source proposition entails the claim proposition; (2) polarity is compatible; (3) the modality relation is allowed per the frozen modality-boundary-table.json; (4) actor binding is compatible; (5) locality/organizational scope is compatible; (6) temporal constraints are compatible; (7) the claim does not drop a required source condition; (8) no applicable source exception is ignored; (9) numeric identity is compatible where numeric proof is used; (10) the governing clause of the matched source proposition is sufficiently covered. All ten must hold.

## 4. Modality relation table (directional, source -> claim)

Frozen in modality-boundary-table.json. Highlights: REQUIRED -> PERMITTED is LICENSED_ENTAILMENT; PERMITTED -> REQUIRED is NOT entailment; CONDITIONAL_ENTITLEMENT -> ENTITLED is not entailment without condition binding; NOT_REQUIRED -> REQUIRED on the same proposition and scope is a contradiction; PROHIBITED -> REQUIRED and PROHIBITED -> PERMITTED are MISMATCH; DEFAULT_RULE -> REQUIRED is UNKNOWN unless the default is explicitly binding. Lexical similarity alone never establishes a modality relation.

## 5. Negation binding

Negation binds to the predicate/clause it governs, not to the whole sentence. Covered shapes: ikke X; ikke krav om X; X er ikke noedvendig; X kan ikke; ikke bare X; X, men ikke Y; X gjelder, med mindre Y; fravaer av X hindrer ikke Y. A support match whose aligned span ignores a negation governing the same predicate is MISMATCH on polarity.

## 6. Clause coverage

A lexical hit inside a clause is insufficient when a later qualifier, negation, condition, or exception inside the same governing structure changes modality, polarity, or applicability. The boundary comparison must include the necessary local clause context of the aligned span. If the engine cannot resolve the governing structure, the dimension is UNKNOWN and auto-support fails closed.

## 7. Condition and exception binding

If the source proposition carries a condition required for the claim to hold, the claim must also carry (or be licensed to inherit) that condition; dropping it is MISMATCH. If the source has an applicable exception and the claim's situation falls inside it, the proof is blocked (MISMATCH on the exception dimension). Irrelevant conditions/exceptions are NOT_APPLICABLE.

## 8. Actor, scope, temporal, numeric

Actor: exact actor or a documented compatible relation (e.g., same role expressed differently). Otherwise MISMATCH or UNKNOWN. Locality/scope: national vs local vs service-specific must agree or be licensed. Temporal: same applicable period or valid entailment. Numeric: same semantic quantity and compatible value where numeric proof is used.

## 9. Permitted implementation scope

Only: semantic proposition extraction, boundary comparison, support proof eligibility, clause coverage logic. Contradiction path behavior must not be redesigned but must be regression-tested. Reviewer, fusion, product routing, abstain routing, and confidence thresholds are out of scope.
