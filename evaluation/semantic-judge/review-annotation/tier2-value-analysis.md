# Tier-2 value analysis (specs 12/13/19)

Model: VALUE = eligible_review_count x confidence_of_safe_automation, adjusted down for legal risk, ambiguity, evidence availability, precondition complexity. Ranking aid, not false precision. Failure severity is weighted over raw volume.

## Operator audit (9 SAFE_WITH_PRECONDITIONS)

| Operator | Review-finals solvable | Pool-of-28 touchable | Expected review reduction | Legal/safety risk | Precondition complexity | Evidence availability | Implementation complexity | VALUE |
|---|---|---|---|---|---|---|---|---|
| RULE_PLUS_CONDITION | 1 (CAL015) | 2 (CAL015, CAL064) | 1 review final | LOW | Low (single marked span, machine-checkable) | Present, near-verbatim | Low | 0.8 |
| SAME_PREDICATE_OPPOSITE_POLARITY | 1 (CAL025) | 7 (CAL025, CI-040, CI-065, N-A2, N-A5, N-A6, N-O5) | 0 (pool contradiction rows already emit auto CONTRADICTED) | MEDIUM-HIGH (compound-atom coverage; polarity of adjacent predicates) | High (compound-atom coverage doctrine must be formalized) | Mixed | High | 0.2 |
| ACTOR_MEMBERSHIP | 1 (D20-A5) | 5 (D20-A5, ACT-19, ACT-23, N-L3, N-C3) | 0.5-1 (D20-A5 clean; pool rows mostly already auto or role-hierarchy-hazardous) | HIGH (role flattening; N-R1 adversarial family) | High (disjunction semantics, role hierarchy) | Present | Medium | 0.3 |
| MODALITY_CONFLICT | 0 | 1 weak (CAL044 discretion-vs-right) | 0 | HIGH (strength miscalibration kan/skal) | High | Weak | Medium | 0.0 |
| RULE_PLUS_EXCEPTION | 0 | 1 (CAL031 hedge shape) | 0 | HIGH (exception miss) | High | Weak | Medium | 0.0 |
| DEFINITION_PLUS_INSTANCE | 0 | 1 (N-S5) | 0 (pool row is review-path abstention, not review final) | LOW | Low | Present | Low | 0.3 (pool-only) |
| EXHAUSTIVE_SET_EXCLUSION | 0 | 0 | 0 | HIGH (closed-world) | High | Absent | Medium | 0.0 |
| MULTI_SPAN_CONJUNCTION | 0 | 1-2 (HOL007 parallel-regelverk) | 0 (pool row already auto CONTRADICTED) | MEDIUM (scope combination) | Medium | Mixed | Medium | 0.2 |
| TRANSITIVE_EQUIVALENCE | 0 | 1 (ACT-23) | 0 (pool row is review-path abstention, not review final) | MEDIUM (drift over steps) | Medium | Present | Medium | 0.2 |

Review-finals subtotal: 3 mapped, realistic safe value concentrated in RULE_PLUS_CONDITION (CAL015 only). Pool-of-28 subtotal: about 12 touchable, but 11 of 28 pool rows are direct-proof/lexer gaps (Tier-1 lexicon/lexer, not Tier-2): MP-007A, MP-009A, MP-014A, ACT-19, N-S4, N-C4, N-C5, ENT-A, CAL064, HOL005 (support-side), HOL034 (support-side).

## Pool audit (specs 16/17)

- Pool as defined: 28 deduped dual rows with semantic != INSUFFICIENT and proof = INSUFFICIENT (29 raw rows including ACT-25, already solved by Tier-1; 1 auto).
- Split: 9 review finals (this task's annotation set includes 7 of them; MP-015A and ENT-C already dual-labelled in Tier-1) + 19 review-path abstentions.
- Real Tier-2 candidates: 3 review finals (CAL015, CAL025, D20-A5) + 2 pool-only rows with clean operator fit (N-S5, ACT-23).
- Necessary reviews: 20 of 21 (plus the 9 already dual-labelled: all necessary). Annotation mismatch: 0. Evidence gap: 5 (CAL063, CAL072, CAL073, CAL077, LOC-07).
- False/obsolete Tier-2 candidates: 7 of the 21 are SHOULD_ALREADY_AUTO_DECIDE (Tier-1 bug candidates, not Tier-2 work). No pool row was found obsolete.
- Exact duplicates in pool: 0. Semantic near-duplicates: MP-007A vs HOL014 (numeric rate shape), MP-009A vs HOL007 (temporal-rule shape), ACT-19 vs ACT-23 (actor-role proof shape). Unique inference patterns: about 21-22 of 28 raw; operator value should be read on unique patterns, not case count.

## Safety weighting (spec 19)

- CAL015 is the only candidate where low failure severity and high proof confidence coincide; it is a near-verbatim restatement with the condition intact.
- The contradiction-side candidates (CAL025 and the CI/N-A family) carry the highest legal risk: auto-CONTRADICTED errors in rights/benefit cases. Their expected reduction is zero or near-zero after compound-atom and already-auto corrections.
- ACTOR_MEMBERSHIP extension (D20-A5) borders the N-R1 retraction family; without role-hierarchy preconditions it would re-import known overreach under a new name.

## Canary verdicts (specs 20/21/22)

- ENT-C: preserved as permanent negative control. No Tier-2 mapping solves it; invalid auto-CONTRADICTED remains forbidden.
- N-A4 + N-R1: preserved as adversarial controls. No proposed Tier-2 re-imports referral-inference or actor-inference overreach; CAL031 and N-C3 are flagged as same-family hazards requiring explicit role-hierarchy preconditions before any future operator touches them.
- ACT-25: documented as the legitimate +1 auto (explicit proof, correct target, zero hidden premise). CAL015 is the only new case meeting this standard.
