# Quota Report - RC2 Blind V3

Date: 2026-09-04. Spec sections 19-21. Verified by construction_qa.py (CORE-only enforcement, exit 0) and re-derived directly from construction/selection.json and construction/pool-annotated.json.

All quota counts below are CORE-only (n=160). Pool counts are reported informationally and can never satisfy a gate - the exact failure mode that produced V2's false ALL_QUOTAS_PASS.

## Semantic class balance (spec 19)

| Class | Count | Floor | Gate |
|---|---|---|---|
| SUPPORTED | 40 | 35 | PASS |
| CONTRADICTED | 40 | 35 | PASS |
| PARTIALLY_SUPPORTED | 40 | 35 | PASS |
| INSUFFICIENT_EVIDENCE | 40 | 30 | PASS |

## Product class coverage (spec 20)

| Class | Count | Minimum | Gate |
|---|---|---|---|
| AUTO_SUPPORTED | 40 | 25 | PASS |
| AUTO_CONTRADICTED | 40 | 25 | PASS |
| REVIEW_REQUIRED | 54 | 25 | PASS |
| ABSTAIN_INSUFFICIENT | 26 | 25 | PASS |

## Structural flag quotas (spec 21)

| Flag | Count | Minimum | Gate |
|---|---|---|---|
| compound | 62 | 50 | PASS |
| cond_exc | 42 | 30 | PASS |
| multi_span | 31 | 30 | PASS |
| numeric | 92 | 30 | PASS |
| temporal | 82 | 30 | PASS |
| actor | 99 | 30 | PASS |
| modality | 132 | 30 | PASS |
| safety | 20 | 20 | PASS |
| legal | 89 | 30 | PASS |
| locality | 38 | 20 | PASS |
| age_legal | 20 | 20 | PASS |

## Contrast with V2

V2 routed every genuine INSUFFICIENT case to reserve and asserted quotas against pool_aggregates; QA passed while CORE held 0 INSUFFICIENT and 0 ABSTAIN. V3 satisfies every quota ON the selection (constraint-based select_core.py) and construction_qa.py fails closed if any CORE count is short. The regression suite (qa-tests/test_construction_qa.py) permanently encodes the seven V2 failure scenarios, including pool-passes/CORE-fails.
