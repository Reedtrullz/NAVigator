# tier1-proof - Tier-1 SAFE_FOR_AUTO_PROOF operators

Task: SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS (DEL B). Status: COMPLETED. DEL A (annotation hardening + contract freeze) is frozen; this directory holds the operator implementation, independent proof validation, the 389-row gate, and the reports.

## Layout

| Path | Content |
|---|---|
| tier1_operators.py | 5 deterministic Tier-1 operators over the frozen polarity engine; conjunctive preconditions, fail-closed run_operators() |
| proof_validator.py | Independent re-derivation of every operator proof (spec 23) |
| test_tier1_operators.py | Unit suite, 34 cases |
| run_gate.py | Gate over the 389 frozen hybrid rows (spec 16/26) |
| operator-regression/ | 16-case operator regression corpus + runner |
| results/ | gate-results.json, operator-impact.json, evaluation-contract-results.json, freeze-verify.json |
| operator-impact-summary.json | Gate summary incl. Tier-2 candidate list |
| product-metrics.json | Baseline vs after product metrics |
| annotation-resolution.json, annotation-second-pass.md | DEL A artifacts referenced by the reports |
| tier1-operator-spec.md | Operator contract summary |
| review-analysis.md | Review-path analysis (spec 21/31) |
| implementation-report.md | Deliverables, session-end fixes, verification battery |
| final-report.md | 60-point SLUTTRAPPORT |
| TASK-LOCK.json | Task state (COMPLETED) |

## Quick rerun

- Unit tests: python3 test_tier1_operators.py
- Operator regression: cd ../operator-regression && python3 run_regression.py
- Gate: python3 run_gate.py
