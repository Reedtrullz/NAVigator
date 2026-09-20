# Scorer V2 Report

Classification: **ANALYTICS_FIX_ONLY**. No evaluator runtime change.

## Root cause

`score_generalization_frozen.py :: gate_results()` evaluated every gate as
`actual = numerator / denominator`. Zero-tolerance proof gates were declared
with a hardcoded `denominator = 0`, so the expression short-circuited to
`0.0` and the `==` comparison against threshold 0 always evaluated PASS,
regardless of the recorded violation count. In the official G2 score the
`metrics.proof_gates` block recorded 53 semantically unsound accepted proofs
and 14 proof-safe unsound autos while the gate block displayed all five
zero-tolerance gates as PASS with `actual: 0.0`.

## Fix

New file: `score_generalization_v2.py` (SHA-256
`ebc6390e7e44bdee278ae74bbbca29e0190d57388a4e7da94af3350aaa08c04b`).

V2 imports the frozen scorer and reuses all metric computation unchanged.
Only `gate_results` is replaced (`gate_results_v2`): for `==` gates the raw
count is compared directly against the threshold; no division occurs. Ratio
gates keep frozen semantics. `score_predictions_v2()` wraps the frozen
`score_predictions()` and swaps in the corrected gate engine
(`SCORER_V2_ZERO_TOLERANCE_COUNT_DIRECT`).

## Tests (all pass)

Synthetic 159-case documents mirroring the frozen self-test pattern:

1. count = 0 for all five zero-tolerance gates -> PASS, actual 0
2. semantically unsound count = 1 -> FAIL, actual 1
3. semantically unsound count = 53 -> FAIL, actual 53
4. proof-safe unsound autos 53-case doc -> FAIL (counts derived)
5. structural-invalid count = 1 -> FAIL, actual 1
6. ungrounded count = 1 -> FAIL
7. runtime exceptions count = 1 -> FAIL
8. frozen scorer demonstrably wrong on identical input (actual 0.0, PASS with 53 violations) - regression guard
9. confusion totals = 159 for semantic, proof_safe, product matrices

Run: `python3 score_generalization_v2.py --self-test` ->
`SCORER_V2 SELF_TEST PASS: 12 checks incl. frozen-bug demonstration`

## Impact on official results

None. `official-generalization-score.json` is untouched (SHA verified before
and after this task). The official verdict `GENERALIZATION_FAIL` already
stands on 11 failing ratio gates; the corrected zero-tolerance gates only add
failures, so the corrected mechanical result does not change the verdict.
See `corrected-proof-gate-audit.json`.

## Scope guard

V2 exists for future scoring runs and audits. The frozen scorer itself is not
modified. The RC3.1 corpus/validation scoring in this task uses its own
proof-gate logic and does not depend on the frozen scorer's gate table.
