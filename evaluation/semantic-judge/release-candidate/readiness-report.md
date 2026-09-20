# Readiness report - blind recertification set creation

Release candidate: NAV-EXPLORE-EVALUATOR-RC1 (frozen 2026-09-03).
Verdict per spec 27.

## Verdict

**READY_TO_BUILD_BLIND_RECERTIFICATION_SET**

## Gate evidence

| Gate (spec 27) | Requirement | Observed | Status |
|---|---|---|---|
| Invalid accepted proofs | 0 | 0 (tier1 gate re-run: new_invalid_proofs=[]; baseline's 3 invalid auto rows N-A4/N-R1/ENT-C retracted to review) | PASS |
| Critical auto errors | 0 | critical_auto_errors_after=[] | PASS |
| Current-contract regressions | pass | gate over 389 rows: 0 conflicts, 0 false auto decisions, dual-row semantic accuracy unchanged 45/80, canaries intact | PASS |
| Operator regression | pass | 23/23 (16 existing + 7 new near-miss cases) | PASS |
| KB regression | 48/48 | Total 48, BESTATT 48, DELVIS 0, FEILET 0, exit 0 | PASS |
| Evaluator regression | clean | acc 1.00, prec 1.00, rec 1.00, safety_FP 0 | PASS |
| id_guard | 0 | 0 violations | PASS |
| qa_check.sh | PASS | OK, exit 0 | PASS |
| Runtime freeze manifest | complete | RC1-manifest.json: 17 files hashed, component versions + contract reference recorded | PASS |

Additional determinism evidence (not a spec-27 gate but required by the
component's own contract): 5 runs x 225 cases, identical_across_runs =
true, after the final engine edits.

## Not required by spec 27

All seven bug-cases becoming auto-decided is explicitly not required.
Outcome: 3 FIXED_SAFE_AUTO, 4 REMAINS_REVIEW_BY_DESIGN, 0
IMPLEMENTATION_BUG_NOT_FIXED, 0 FALSE_SHOULD_AUTO_CLASSIFICATION.

## Conditions going forward

1. The blind recertification set, when built, must test the exact RC1
   hashes (spec 31). Any modification invalidates RC1 and requires RC2.
2. No tuning before recertification results exist (spec 26).
3. The blind set is built in a separate task (spec 29) with a separate
   annotation agent/process, annotating: semantic truth, proof-safe
   verdict, product expected action, required inference/operator, and
   annotation status (spec 30). No cases are created in this task.
