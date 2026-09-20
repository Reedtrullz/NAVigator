# Annotation second pass - 32 curated novel labels

Task: SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS, DEL A spec 3-4. Pass 2: independent model thread (gpt-5.6-luna), claims + sources only, no access to pass-1 verdicts or justifications. Pass 1: curated first-hand reading (previous stage). Adjudication: source + frozen contract + operator definitions only; reviewer output never used as key.

## Inter-pass agreement (n=32)

| Measure | Agreement |
|---|---|
| Exact (all four fields equal) | 21/32 = 65.6% |
| Semantic truth | 31/32 = 96.9% |
| Required operator | 21/32 = 65.6% |
| Proof-safe | 23/32 = 71.9% |
| Product action | 23/32 = 71.9% |

Note: pass 1 recorded no explicit proof-safe label for novel cases; it is derived under the frozen doctrine (Tier-1 operator -> proof = semantic; otherwise INSUFFICIENT), applied identically to both passes.

## Disagreements (11)

1 semantic disagreement (N-R1, adjudicated RESOLVED_NEW_LABEL); 10 operator-attribution disagreements with identical verdicts (adjudicated PASS1_CONFIRMED unless noted). Zero cases entered ANNOTATION_DISPUTE.

| id | class | pass1 sem/op | pass2 sem/op | adjudication |
|---|---|---|---|---|
| N-S3 | OPERATOR_ONLY | SUPPORTED/DIRECT_ASSERTION | SUPPORTED/TRANSITIVE_EQUIVALENCE | **PASS1_CONFIRMED**: DIRECT_ASSERTION; Kostnadsfrie -> gratis is a single synonym substitution (paraphrase-level overlap), not a multi-step chain. |
| N-S6 | OPERATOR_ONLY | SUPPORTED/DIRECT_ASSERTION | SUPPORTED/TRANSITIVE_EQUIVALENCE | **PASS1_CONFIRMED**: TRANSITIVE_EQUIVALENCE; Foresatte/foreldre is synonymy, not class instantiation. |
| N-S7 | OPERATOR_ONLY | SUPPORTED/DIRECT_ASSERTION | SUPPORTED/TRANSITIVE_EQUIVALENCE | **PASS1_CONFIRMED**: TRANSITIVE_EQUIVALENCE; "har lavterskel psykisk helsehjelp" -> "driver lavterskeltilbud" is a paraphrase chain, not definition. |
| N-A5 | OPERATOR_ONLY | CONTRADICTED/EXHAUSTIVE_SET_EXCLUSION | CONTRADICTED/RULE_PLUS_EXCEPTION | **PASS1_CONFIRMED**: EXHAUSTIVE_SET_EXCLUSION; "ogsaa med frivillig hjelp" establishes non-exclusivity of tvangssaker via a marked partial-set statement; conservative attribution kept. |
| N-L2 | OPERATOR_ONLY | SUPPORTED/RULE_PLUS_CONDITION | SUPPORTED/DIRECT_ASSERTION | **PASS1_CONFIRMED**: RULE_PLUS_CONDITION; Age-conditioned consent rule; explicit condition structure, not flat assertion. |
| N-L6 | OPERATOR_ONLY | SUPPORTED/RULE_PLUS_CONDITION | SUPPORTED/DIRECT_ASSERTION | **PASS1_CONFIRMED**: RULE_PLUS_CONDITION; Source is a conditional rule ("ved akutt hjelp ... ikke noedvendig"); keeping the condition explicit is the conservative attribution. |
| N-C2 | OPERATOR_ONLY | INSUFFICIENT/NO_OPERATOR | INSUFFICIENT_EVIDENCE/MODALITY_CONFLICT | **PASS1_CONFIRMED**: NO_OPERATOR; Source never addresses ADHD-diagnosis; absence of support, no modality tokens exist to conflict. |
| N-C3 | OPERATOR_ONLY | INSUFFICIENT/NO_OPERATOR | INSUFFICIENT_EVIDENCE/ACTOR_MEMBERSHIP | **PASS1_CONFIRMED**: NO_OPERATOR; Verdict is absence of support ("akutt" unaddressed); helsesykepleier/helsestasjon share no actor term, so ACTOR_MEMBERSHIP precondition is unmet. |
| N-R1 | SEMANTIC | CONTRADICTED/EXPLICIT_NEGATION | INSUFFICIENT_EVIDENCE/ACTOR_MEMBERSHIP | **RESOLVED_NEW_LABEL**: ACTOR_MEMBERSHIP; Pass 2 correct: source negates diagnosis by skolehelsetjenesten; claim actor helsesykepleier is not established as member. ACTOR_MEMBERSHIP precondition (shared actor term) unmet -> verdict cannot be established -> INSUFFICIENT. Exposes engine auto-CONTRADICTED on N-R1 as an over-fire under the hardened contract. |
| N-R2 | OPERATOR_ONLY | INSUFFICIENT/NO_OPERATOR | INSUFFICIENT_EVIDENCE/ACTOR_MEMBERSHIP | **PASS1_CONFIRMED**: NO_OPERATOR; BUP/PPT share no actor term; ACTOR_MEMBERSHIP precondition unmet, hence absence of support. |
| N-O3 | OPERATOR_ONLY | CONTRADICTED/SAME_PREDICATE_OPPOSITE_POLARITY | CONTRADICTED/EXHAUSTIVE_SET_EXCLUSION | **PASS1_CONFIRMED**: SAME_PREDICATE_OPPOSITE_POLARITY; Direct scope-polarity opposition on shared predicate (gjelder: hele fylket vs bare i Trondheim); contradiction rides on the scope conflict, not set exclusion. |

## Luna call accounting

1 thread (gpt-5.6-luna), one user-visible turn, 53s wall time, 0 GPT-5.5 calls. Thread 01a062fe-52ce-7e90-b897-8b1401a5ebcf kept separate from the final decision; adjudication applied the contract deterministically.

## Full pass-2 record

| id | pass2 semantic | pass2 operator | pass2 proof-safe | pass2 action |
|---|---|---|---|---|
| N-S1 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-S2 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-S3 | SUPPORTED | TRANSITIVE_EQUIVALENCE | SUPPORTED | AUTO_DECIDE |
| N-S5 | SUPPORTED | DEFINITION_PLUS_INSTANCE | SUPPORTED | AUTO_DECIDE |
| N-S6 | SUPPORTED | TRANSITIVE_EQUIVALENCE | SUPPORTED | AUTO_DECIDE |
| N-S7 | SUPPORTED | TRANSITIVE_EQUIVALENCE | SUPPORTED | AUTO_DECIDE |
| N-S8 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-S10 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-A1 | CONTRADICTED | EXPLICIT_NEGATION | CONTRADICTED | AUTO_DECIDE |
| N-A2 | CONTRADICTED | SAME_PREDICATE_OPPOSITE_POLARITY | CONTRADICTED | AUTO_DECIDE |
| N-A4 | CONTRADICTED | SAME_PREDICATE_OPPOSITE_POLARITY | CONTRADICTED | AUTO_DECIDE |
| N-A5 | CONTRADICTED | RULE_PLUS_EXCEPTION | CONTRADICTED | AUTO_DECIDE |
| N-A6 | CONTRADICTED | SAME_PREDICATE_OPPOSITE_POLARITY | CONTRADICTED | AUTO_DECIDE |
| N-L1 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-L2 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-L3 | SUPPORTED | ACTOR_MEMBERSHIP | INSUFFICIENT | REVIEW |
| N-L5 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-L6 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-C1 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-C2 | INSUFFICIENT_EVIDENCE | MODALITY_CONFLICT | INSUFFICIENT | REVIEW |
| N-C3 | INSUFFICIENT_EVIDENCE | ACTOR_MEMBERSHIP | INSUFFICIENT | REVIEW |
| N-C6 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-R1 | INSUFFICIENT_EVIDENCE | ACTOR_MEMBERSHIP | INSUFFICIENT | REVIEW |
| N-R2 | INSUFFICIENT_EVIDENCE | ACTOR_MEMBERSHIP | INSUFFICIENT | REVIEW |
| N-R4 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-R5 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-R6 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-O1 | INSUFFICIENT_EVIDENCE | NO_OPERATOR | INSUFFICIENT | REVIEW |
| N-O2 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-O3 | CONTRADICTED | EXHAUSTIVE_SET_EXCLUSION | CONTRADICTED | AUTO_DECIDE |
| N-O4 | SUPPORTED | DIRECT_ASSERTION | SUPPORTED | AUTO_DECIDE |
| N-O6 | INSUFFICIENT_EVIDENCE | NO_OPERATOR | INSUFFICIENT | REVIEW |
