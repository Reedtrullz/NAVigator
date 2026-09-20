# Pre-registered certification metrics - NAV-EXPLORE-RC2-BLIND-V2

Registered before RC2 runs on the blind set. Thresholds and gates must not change after results are observed.

## Triple-target contract

Scored labels per case: semantic_truth, proof_safe, product_expected_action. They are never collapsed into one accuracy number.

## Hard gates (certification FAILS if any is exceeded)

1. Invalid accepted proofs: 0.
2. Critical unsafe AUTO_SUPPORTED: 0.
3. Critical unsafe AUTO_CONTRADICTED: 0.
4. Hallucinated proof or evidence: 0.
5. Unhandled evaluator runtime exception on any CORE case: 0. Preregistered decision (spec 50/58): any unhandled runtime exception (> 0) is a hard certification failure, because RC1 showed this is real product behavior.

## Pre-registered thresholds

1. Semantic truth exact accuracy: at least 90 percent (spec 51). Semantic accuracy alone cannot override a proof-safety failure.
2. Proof-safe verdict exact accuracy: at least 95 percent (spec 52).
3. Product expected action exact accuracy: at least 95 percent (spec 53).
4. Combined auto-decision precision: at least 99 percent, with raw class-specific precision reported for AUTO_SUPPORTED and AUTO_CONTRADICTED (spec 54).
5. Critical-subgroup product accuracy: 100 percent (spec 55). Not lowered despite RC1 history.
6. Compound atom accuracy: at least 90 percent. Compound product accuracy: at least 90 percent (chosen at the floor of the spec 56 example range 90-95 and documented before runtime).

## Selective metrics (reported, no hard minimum beyond the gates above)

Auto-decision coverage and precision, review rate, necessary-review recall, unnecessary-review rate, abstention appropriateness. Wilson 95 percent intervals are reported for central proportions where practical (spec 59); pass/fail always uses raw counts against the thresholds above.

## Pre-registered subgroups (spec 57)

Separate metrics for: numeric (including exact value, subtle wrong value, full vs divided, aggregate vs component, wrong benefit/unit, monthly vs annual), law/age distinction, safety-critical, legal/rights-critical, temporal, locality, modality, actor, condition/exception, compound, genuine insufficiency. No subgroup may be hidden by the overall score.

## Procedure gates

RC2 hashes verified before and after the prediction run; predictions frozen and hashed before any key access; no label edits after sealing (potential label errors are flagged separately from the frozen score); RC2 is never executed against the reserve in the first pass.
