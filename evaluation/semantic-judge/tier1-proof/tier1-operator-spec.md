# Tier-1 operator specifications (SAFE_FOR_AUTO_PROOF only)

Task: SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS, DEL B spec 11-20. These five operators are the complete Tier-1 set from the frozen operator classification. Implementation must follow these specs exactly; preconditions are conjunctive (ALL must hold or the operator abstains), per spec 12. No chaining beyond a documented bounded proof (spec 20).

## Common preconditions (all operators)

1. **Same subject axis**: claim and premise share the established subject/actor term (or a documented alias pair); actor class flattening is forbidden.
2. **Compatible scope**: locality/scope markers must not conflict (known-locale vs other-locale, bare-i-Trondheim vs hele-fylket).
3. **Compatible time**: temporal anchors, when present on both sides, must not conflict.
4. **Unknown = abstain**: if any required relation cannot be established from evidence, the operator does not fire (spec 12: no best effort).
5. **Fail closed**: crash, missing data, or ambiguity -> REVIEW_REQUIRED (spec 15).

## 1. DIRECT_ASSERTION

- **Semantic definition**: The premise directly asserts the claim content at paraphrase level (synonym substitution or small agent-verb paraphrase; at most one non-trivial substitution).
- **Required premises**: claim and premise share subject; predicate paraphrase is small and standard; polarity equal; scope/time compatible
- **Allowed evidence forms**: the premise span itself
- **Proof object**: JSON object with fields operator ("DIRECT_ASSERTION"), premises (span ids), derived_fact, claim_atom, result (SUPPORTED or CONTRADICTED).
- **Invalidating conditions**: any common precondition unmet; any listed failure mode detected; validator rejects the proof object.
- **Scope requirements**: compatible scope (common preconditions).
- **Temporal requirements**: none beyond common preconditions.
- **Actor requirements**: shared actor term or documented alias; no flattening.
- **Safety/legal failure modes**: synonym drift stacking across >1 substitution; negation token missed inside span; subject flattening (helsesykepleier read as skolehelsetjenesten).

## 2. EXPLICIT_NEGATION

- **Semantic definition**: The premise contains an explicit negation of the same predicate the claim asserts (or vice versa), with matched scope.
- **Required premises**: same canonical predicate; negation token present and in scope of the predicate; no intervening exception applies to the negated instance; claim asserts the positive (or the negation) with same subject and scope
- **Allowed evidence forms**: the negated premise span
- **Proof object**: JSON object with fields operator ("EXPLICIT_NEGATION"), premises (span ids), derived_fact, claim_atom, result (SUPPORTED or CONTRADICTED).
- **Invalidating conditions**: any common precondition unmet; any listed failure mode detected; validator rejects the proof object.
- **Scope requirements**: compatible scope (common preconditions).
- **Temporal requirements**: temporal anchors must not conflict.
- **Actor requirements**: shared actor term or documented alias; no flattening.
- **Safety/legal failure modes**: partial negation read as full (negation scoping to a different verb); negation of a different actor/predicate counted as conflict.

## 3. NUMERIC_CONFLICT

- **Semantic definition**: The premise states a number on the same value axis as the claim, and the values differ.
- **Required premises**: same value axis (unit, basis, population); both values explicit in evidence; no aggregation ambiguity (single value vs distribution)
- **Allowed evidence forms**: the numeric premise span plus the claim value
- **Proof object**: JSON object with fields operator ("NUMERIC_CONFLICT"), premises (span ids), derived_fact, claim_atom, result (SUPPORTED or CONTRADICTED).
- **Invalidating conditions**: any common precondition unmet; any listed failure mode detected; validator rejects the proof object.
- **Scope requirements**: compatible scope (common preconditions).
- **Temporal requirements**: same axis and population required.
- **Actor requirements**: shared actor term or documented alias; no flattening.
- **Safety/legal failure modes**: unit or basis mismatch read as value conflict; claim aggregates (alle/kort) where premise gives a distribution.

## 4. TEMPORAL_CONFLICT

- **Semantic definition**: The premise states a date/duration anchor on the same time axis as the claim, and the anchors conflict.
- **Required premises**: same time axis (validity period, age, duration); anchors explicit on both sides; granularity compatible
- **Allowed evidence forms**: the temporal premise span
- **Proof object**: JSON object with fields operator ("TEMPORAL_CONFLICT"), premises (span ids), derived_fact, claim_atom, result (SUPPORTED or CONTRADICTED).
- **Invalidating conditions**: any common precondition unmet; any listed failure mode detected; validator rejects the proof object.
- **Scope requirements**: compatible scope (common preconditions).
- **Temporal requirements**: explicit anchors required on both sides.
- **Actor requirements**: shared actor term or documented alias; no flattening.
- **Safety/legal failure modes**: granularity mismatch read as conflict; date-of-event vs validity-period confusion.

## 5. SIMPLE_ARITHMETIC

- **Semantic definition**: A derived fact follows from premise numbers by one documented arithmetic relation (sum or difference) stated in the operator spec.
- **Required premises**: numbers in a single premise or two premises of one document; the arithmetic relation is sum or difference only (no multiplication of amounts, no percentages); derived_fact is checked by recomputation; same scope and time as claim
- **Allowed evidence forms**: the numeric spans plus the relation plus the recomputed value
- **Proof object**: JSON object with fields operator ("SIMPLE_ARITHMETIC"), premises (span ids), derived_fact, claim_atom, result (SUPPORTED or CONTRADICTED).
- **Invalidating conditions**: any common precondition unmet; any listed failure mode detected; validator rejects the proof object.
- **Scope requirements**: compatible scope (common preconditions).
- **Temporal requirements**: relation must be explicit in the proof object and recomputed by the validator.
- **Actor requirements**: shared actor term or documented alias; no flattening.
- **Safety/legal failure modes**: applying an arithmetic relation to unrelated numbers; unit mixing (kr vs prosent).

## Cross-operator conflict policy (spec 19)

If two operators produce proof objects with different results (e.g. SUPPORTED from DIRECT_ASSERTION and CONTRADICTED from NUMERIC_CONFLICT), the fused outcome is REVIEW_REQUIRED. No priority guessing.

## Chaining policy (spec 20)

Each operator uses only its documented premises in one bounded proof. No A->B->C chains.

## Implementation boundary (spec 16)

Reviewer v1.1 and the hybrid review path stay frozen. Tier-1 operators may only move REVIEW_REQUIRED/INSUFFICIENT cases to valid deterministic proofs; they may never override an existing auto verdict with a less cautious one, and every fired auto verdict must carry a validator-passed proof object.
