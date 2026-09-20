# Construction QA Report - RC2 Blind V3

Date: 2026-09-04. Tooling: construction_qa.py (fail-closed, CORE-only enforcement) and qa-tests/test_construction_qa.py (spec 43 regression).

## Gate run (current session evidence)

python3 construction_qa.py construction.json, run from the set directory:

- exit code 0, ALL_HARD_GATES_PASS (CORE-only enforcement)
- INFO CORE n=160, reserve n=122, pool n=282
- INFO pre-adjudication CORE agreement: semantic_truth=0.9500, proof_safe=0.9375, product_action=0.9375
- INFO adjudication rate: 10/160 = 0.0625
- INFO pool semantic distribution (informational, not gate-satisfying): SUPPORTED 127, CONTRADICTED 67, PARTIALLY_SUPPORTED 48, INSUFFICIENT_EVIDENCE 40

## Hard gates evaluated on CORE only

| Gate | Value | Status |
|---|---|---|
| CORE n >= 140 | 160 | PASS |
| Semantic class floors | 40/40/40/40 | PASS |
| Genuine insufficiency >= 30 | 40 | PASS |
| Product class minima | 40/40/54/26 | PASS |
| All 11 flag minima | lowest margin: safety 20/20, age_legal 20/20, multi_span 31/30 | PASS |
| Agreement >= 0.90 (3 slots) | 0.95 / 0.9375 / 0.9375 | PASS |
| Full double annotation | 282/282 | PASS |
| Adjudication rate <= 35% | 6.25% | PASS |
| Unresolved disputes = 0 | 0 | PASS |
| Fidelity failures = 0 | 0 | PASS |
| Novelty pass | 282/282 retained | PASS |
| Plaintext leaks in public artifacts | 0 (token + row scan) | PASS |
| RC2 hashes before / after seal | 11/11 OK both | PASS |

## Regression tests (spec 43)

python3 qa-tests/test_construction_qa.py: all seven scenarios PASS - pool-quota-cannot-satisfy-CORE, zero-insufficiency, zero-ABSTAIN, multi-span 18/30, agreement 0.78, single-pass candidate, adjudication over 35% - plus cli-nonzero-on-failure and cli-zero-when-clean.

These tests permanently encode the V2 failure modes: every scenario builds a pool that passes pool-wide but must fail on a CORE-only gate, and the runner asserts construction_qa returns failures and exits non-zero.
