# RC3.1 Auto-Support Boundary Repair - Regression Report

Task ID: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR
Dates: 2026-09-05 (implementation + suites), 2026-09-06 (same-day re-verification)
Engine SHA-256: c4bc71862febf51783e2e48550f899746f9a6d0cb00f03a84d084edcd8fdce37

## Boundary suites (final engine)

| Metric | Baseline | Final | Gate | Result |
|---|---|---|---|---|
| FALSE_AUTO_SUPPORT_BOUNDARY (fresh, n=80) | 27 | 0 | 0 | PASS |
| support_boundary_precision | 0.5345 | 1.0 | >=0.99 | PASS |
| entailed_support_recall | 0.7949 | 0.9730 | >=0.85 | PASS |
| negation_boundary_accuracy | 0.35 | 1.0 | >=0.95 | PASS |
| modality_boundary_accuracy | 0.45 | 0.95 | >=0.95 | PASS |
| condition_exception_boundary_accuracy | 0.60 | 1.0 | >=0.95 | PASS |
| actor_scope_boundary_accuracy | 0.5333 | 1.0 | >=0.95 | PASS |
| temporal_local_numeric_boundary_accuracy | 0.50 | 0.90 | (not a gate) | 2 predesignated accepted misses (RC31-BDY-0033 modality coverage, RC31-BDY-0077 temporal proper noun) |
| burned-train unsound eligible (product level, n=124) | 25 (atom level, old metric) | 0 | 0 | PASS |
| burned-train relation accuracy | 0.8468 | 0.5161 | informational (section 31) | boundary fail-closed semantics moved previously-entailed predictions to explicit non-auto states; not a proof-safety regression |

## Determinism

- 2026-09-05: two independent runs byte-identical (cmp PASS).
- 2026-09-06: two fresh runs byte-identical (cmp PASS); identical to the frozen boundary-results.json (FALSE=0, precision=1.0, unsound=0).

## Legacy regressions (all re-run against the final engine)

| Suite | Command | Result |
|---|---|---|
| RC2 regression | rc2-development/regressions/run_regression.py | 37/37 PASS |
| Tier-1 proof gate | tier1-proof/run_gate.py | conflicts=0, new_invalid_proofs=[], critical_auto_errors_after=[] PASS |
| Tier-1 operators | tier1-proof/test_tier1_operators.py | 43/43 PASS |
| Operator regression | operator-regression/run_regression.py | 23/23 PASS |
| RC3 development tests | rc3-development pytest | 24 passed |
| KB | score_baseline.py | 48/48 BESTATT, 0 DELVIS, 0 FEILET |
| Quote-aligner | quote-aligner/v0.2 check_regress.py | REGRESSIONS: 0 (7 pre-existing residuals, unchanged) |
| Quote-aligner determinism | check_determinism.py | 5 runs identical, 225 cases, unstable_cases={} |
| Quote-aligner id guard | check_id_guard.py | 0 violations |
| Engine probes | rc3-1-proof-semantics/test_engine_probes.py | ALL PROBES PASS |

## Safety and integrity

- Runtime id guard: rg for RC1B / RC2B / RC3G / RC31- case literals over rc3_1_engine/ and the task's .py files: 0 hits.
- Validation seal SHA-256 before and after: 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159 (unchanged). The sealed validation answer key was not decrypted, inspected, or executed against.
- Historical artifacts unchanged (see source-integrity-report.md).
- py_compile, actual engine import, and control-character scan: PASS (Gate 0; every run in this report re-imported the same engine file with logged SHA).

## Conclusion

No regression on any legacy or safety suite. All boundary gates pass. Overall proof-dev readiness remains NOT READY only because burned-train relation accuracy (0.5161) is below 0.95 (section 32), which requires a later relation-class repair task without opening the sealed validation.
