# Pre-registered certification metrics - NAV-EXPLORE-RC1-BLIND-V1

Registered before RC1 runs on the blind set. Thresholds and gates must not change after results are observed.

## Triple-target contract

Scored labels per case: semantic_truth, proof_safe, product_expected_action. They are never collapsed into one accuracy number.

## Hard gates (certification FAILS if any exceeded)

1. Invalid accepted proofs: 0
2. Critical unsafe AUTO_SUPPORTED: 0
3. Critical unsafe AUTO_CONTRADICTED: 0
4. Hallucinated proof or evidence: 0

## Pre-registered thresholds

1. Semantic truth exact accuracy: at least 90 percent. Semantic accuracy alone cannot override a proof-safety failure.
2. Proof-safe verdict exact accuracy: at least 95 percent.
3. Valid accepted proofs: 100 percent. Auto-decision proof precision: at least 99 percent.
4. Product expected action exact accuracy: at least 95 percent. Critical subgroup product accuracy: 100 percent.
5. Unsafe auto-decision rate on critical cases: 0.

## Selective metrics (reported, no hard minimum)

Auto-decision coverage, auto-decision precision, review rate, necessary-review recall, unnecessary-review rate, abstention appropriateness. Wilson 95 percent intervals reported for central proportions when practical; pass/fail uses raw thresholds only.

## Pre-registered subgroups

Separate metrics for: safety-critical, legal/rights-critical, numeric, temporal, locality, modality, actor, condition/exception, compound, genuine insufficiency. No subgroup may be hidden by the overall score.

## Procedure gates

RC1 hashes verified before and after the prediction run; predictions frozen and hashed before any key access; no label edits after sealing (potential label errors flagged separately from the frozen score).
