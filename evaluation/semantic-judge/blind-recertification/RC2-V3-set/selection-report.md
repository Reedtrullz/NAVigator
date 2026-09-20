# Selection Report - RC2 Blind V3

Date: 2026-09-04. Spec sections 18-27. Tooling: construction/select_core.py.

## Method

Constraint-based deterministic greedy selection with rescoring after each pick (spec 22; ILP not needed - zero failures on first solve). Hard constraints are enforced DURING selection, not measured afterwards; this is the structural fix for the V2 bug where all INSUFFICIENT cases were routed to reserve and pool-wide QA never noticed.

Selection objective after hard constraints (spec 23, in priority order): annotation agreement, novelty, source fidelity, domain diversity (primary_kb dispersion penalty), inference diversity. RC2 performance was never an input - RC2 has not executed.

## Result

| Item | Value |
|---|---|
| CORE | 160 (spec 18 minimum 140) |
| Reserve | 122 |
| Constraint failures | 0 |
| Adjudicated cases in CORE | 10/160 = 6.25% (hard max 35%, spec 25) |
| All cases double-annotated | yes, 282/282, no single-pass exceptions (spec 26) |

All 23 label disputes were adjudicated before selection ran; selection consumed final labels only, so disputes could not enter CORE unadjudicated (spec 24).

## CORE semantic balance

Exact 40/40/40/40 across SUPPORTED / CONTRADICTED / PARTIALLY_SUPPORTED / INSUFFICIENT_EVIDENCE (spec 19 targets met exactly; floors were target-5 with INSUFFICIENT at least 30).

## Full-eligible-pool agreement vs proposed CORE agreement

| Slot | Full pool (277 scored) | Proposed CORE (160) | Gate |
|---|---|---|---|
| semantic_truth | 0.9314 | 0.9500 | >= 0.90 PASS |
| proof_safe | 0.9242 | 0.9375 | >= 0.90 PASS |
| product_action | 0.9242 | 0.9375 | >= 0.90 PASS |

(spec 27: both scopes reported; the hard gate is CORE.)

## Reserve

122 cases retained as scored reserve (final labels exist; reserve is not sealed into the answer key). Reserve includes the 13 non-CORE adjudicated disputes and the pool's remaining class mass (pool-wide semantic distribution: SUPPORTED 127, CONTRADICTED 67, PARTIALLY_SUPPORTED 48, INSUFFICIENT_EVIDENCE 40).
