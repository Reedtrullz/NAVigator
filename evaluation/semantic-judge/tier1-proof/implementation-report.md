# Implementation report - SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS

Task lock: SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS. Status: COMPLETED. Date: 2026-09-02.

## Deliverables

| File | Content |
|---|---|
| tier1_operators.py | 5 Tier-1 SAFE_FOR_AUTO_PROOF operators (DIRECT_ASSERTION, EXPLICIT_NEGATION, NUMERIC_CONFLICT, TEMPORAL_CONFLICT, SIMPLE_ARITHMETIC), conjunctive preconditions, directional actor binding (N-R1 doctrine), fail-closed run_operators() |
| proof_validator.py | Independent re-derivation of every proof (premises re-read, concepts re-matched, arithmetic recomputed); multi-premise DA/EN + detail.concepts list shape |
| test_tier1_operators.py | Unit suite: 34/34 PASS |
| run_gate.py + results/gate-results.json | Gate over 389 frozen rows; results embedded |
| results/operator-impact.json, operator-impact-summary.json | Per-operator impact and summary incl. Tier-2 candidates |
| results/evaluation-contract-results.json | Oracle-46 / novel-40 / ent before-after under dual contract |
| product-metrics.json | Baseline vs after product metrics (corrected review finals = 30) |
| operator-regression/ (README, cases.json, expected-results.json, run_regression.py, results.json) | 16-case regression corpus; 16/16 PASS |
| review-analysis.md | Spec 21/31 review-path analysis |
| final-report.md | 60-point SLUTTRAPPORT |

## Session-end code fixes (post-gate, all verified)

1. _DATE_VALUE_RE gate in TEMPORAL_CONFLICT: bare dated statements (date-as-value, not deadline anchor) never fire. Fixes DA-TIME drift.
2. _QUALIFIER_RE guard in DA/EN candidate loops: negated relative qualifier clause (ikke ... omfattes/gjelder/dekkes/inkludert/regnes) scopes the whole sentence; unqualified claim cannot inherit its assertion. Fixes EN-SCOPE.
3. Aggregate guard in NUMERIC_CONFLICT: _ARITH_RE claims (til sammen/totalt/sum) recompute across premises and are not comparable to single component bounds; abstain. Fixes ARI-POS/ARI-AMBIG cross-operator firing.
4. Earlier session fixes retained: aggregation framing guard in SIMPLE_ARITHMETIC (_ARITH_RE claim requirement), exactly-one-relation ambiguity gate, strict _time_compatible (dated vs undated abstains), full-fold/stem-6 actor equality (4-char stem collisions), N-R1 directional contra binding.

## Verification battery (all exit 0)

- Unit tests: 34/34 PASS (test_tier1_operators.py)
- Operator regression: 16/16 PASS (operator-regression/run_regression.py)
- check_regress.py: exit 0
- check_id_guard.py: 0 violations
- KB regression: 48/48 exit 0
- Evaluator regression: acc 1.00
- qa_check.sh: PASS
- run_gate.py rerun post-fixes: moved 1, retracted 3, conflicts 0, invalid accepted 0, critical after 0, semantic 45/80, auto 121->119, review finals 27->30, Tier-2 candidates (review-path, post-gate) 28
- Freeze manifest: 9/9 verified, NOT stale (results/freeze-verify.json)
