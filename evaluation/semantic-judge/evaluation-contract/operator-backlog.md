# Prioritized operator backlog (classification only; nothing implemented)

Sorting: impact x safety x implementation confidence (spec 31). Tiers are advisory input to a future stage, not a commitment.

## Tier 1 - high value, low risk

### DIRECT_ASSERTION -> SAFE_FOR_AUTO_PROOF

- Definition: derives verdict when paraphrase-level overlap between claim and premises (per inference-operators.json v1)
- Premises: paraphrase-level overlap between claim and premises
- Failure mode: paraphrase gap widens into unsupported generalization
- Closed-world risk: LOW
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### EXPLICIT_NEGATION -> SAFE_FOR_AUTO_PROOF

- Definition: derives verdict when premise contains explicit negation token (per inference-operators.json v1)
- Premises: premise contains explicit negation token
- Failure mode: negation-scope misses (partial negation read as full)
- Closed-world risk: LOW
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### NUMERIC_CONFLICT -> SAFE_FOR_AUTO_PROOF

- Definition: derives verdict when premise contains a number on the claim axis (per inference-operators.json v1)
- Premises: premise contains a number on the claim axis; values differ
- Failure mode: unit/basis mismatch read as value conflict
- Closed-world risk: LOW
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### TEMPORAL_CONFLICT -> SAFE_FOR_AUTO_PROOF

- Definition: derives verdict when premise contains a date/duration anchor (per inference-operators.json v1)
- Premises: premise contains a date/duration anchor; anchors conflict
- Failure mode: anchor granularity mismatch
- Closed-world risk: LOW
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### SIMPLE_ARITHMETIC -> SAFE_FOR_AUTO_PROOF

- Definition: derives verdict when numbers in premises (per inference-operators.json v1)
- Premises: numbers in premises; arithmetic relation in derived_fact
- Failure mode: wrong arithmetic relation applied to unrelated numbers
- Closed-world risk: LOW
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

## Tier 2 - useful, preconditions required

### MODALITY_CONFLICT -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when modality tokens present on both sides (per inference-operators.json v1)
- Premises: modality tokens present on both sides
- Failure mode: strength miscalibrated (kan vs skal)
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### SAME_PREDICATE_OPPOSITE_POLARITY -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when shared predicate (per inference-operators.json v1)
- Premises: shared predicate; opposite polarity
- Failure mode: polarity of adjacent-but-different predicates conflated
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### RULE_PLUS_CONDITION -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when rule and condition co-present (two premises or condition-marked span) (per inference-operators.json v1)
- Premises: rule and condition co-present (two premises or condition-marked span)
- Failure mode: consequence matched while condition dropped
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### RULE_PLUS_EXCEPTION -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when rule span plus explicit exception marker (per inference-operators.json v1)
- Premises: rule span plus explicit exception marker
- Failure mode: main rule matched while exception applies
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### DEFINITION_PLUS_INSTANCE -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when class term shared between claim and premise (per inference-operators.json v1)
- Premises: class term shared between claim and premise
- Failure mode: non-identity definitional relationship treated as identity
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection
- Note: DEFINITION_PLUS_INSTANCE may graduate to SAFE_FOR_AUTO_PROOF only for explicit identity/inclusion definitions (spec 12)

### EXHAUSTIVE_SET_EXCLUSION -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when premise marks the list exhaustive (kun/bare/eneste/alle/...) (per inference-operators.json v1)
- Premises: premise marks the list exhaustive (kun/bare/eneste/alle/...)
- Failure mode: unmarked list treated as exhaustive (closed-world)
- Closed-world risk: HIGH
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### ACTOR_MEMBERSHIP -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when actor term shared between claim and premise (per inference-operators.json v1)
- Premises: actor term shared between claim and premise
- Failure mode: role flattening (helsepersonell -> lege)
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### MULTI_SPAN_CONJUNCTION -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when at least two distinct premise spans (per inference-operators.json v1)
- Premises: at least two distinct premise spans
- Failure mode: spans combined across incompatible scopes
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

### TRANSITIVE_EQUIVALENCE -> SAFE_WITH_PRECONDITIONS

- Definition: derives verdict when each equivalence step is a small paraphrase (per inference-operators.json v1)
- Premises: each equivalence step is a small paraphrase
- Failure mode: chain accumulates drift over >2 steps
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

## Tier 3 - review-only / deferred

### LOCAL_RULE_OVERRIDES_GENERAL -> REVIEW_ONLY

- Definition: derives verdict when locality term present in the premise span (per inference-operators.json v1)
- Premises: locality term present in the premise span
- Failure mode: implicit legal hierarchy assumed
- Closed-world risk: MEDIUM
- Legal/safety risk: HIGH for LOCAL_RULE_OVERRIDES_GENERAL and unmarked exhaustiveness; LOW for bounded conflict detection

## NO_OPERATOR

- Meaning: no valid derivation; verdict must be INSUFFICIENT_EVIDENCE (or REVIEW_REQUIRED in production).

## Explicitly not implemented

All 15 operators above are classified only. No adjudicator, aligner, or reviewer code was changed in this task (spec 30, TASK-LOCK).
