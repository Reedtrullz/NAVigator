# Regression Report - RC3.1 Generalized Relation-Class Repair

Spec: NAV-EXPLORE-RC3_1-GENERALIZED-RELATION-CLASS-REPAIR (section 42/45).
All suites re-run on the final (restored) engine,
SHA 4bd2845fac3535fba22ab3e242b51e80f0d2abbbb5d57a3123b7207b2383ea7d.

| Suite | Result | Status |
|---|---|---|
| Gate 0 compile | py_compile OK | PASS |
| Gate 0 import | actual engine import, path logged | PASS |
| Gate 0 control chars | 0 | PASS |
| Engine probes | ALL PASS | PASS |
| Boundary suite (fresh 80) | false auto = 0, precision = 1.0, recall = 0.9730, unsound = 0 | PASS (hard gates) |
| Boundary per-dimension | see note below | PRE-EXISTING DRIFT |
| Fresh relation (188 atoms) | accuracy 0.6596, macro-F1 0.7157 | FAIL (gates >= 0.95 / >= 0.93) |
| ENTAILS precision | 0.918 | FAIL (gate >= 0.99) |
| CONTRADICTS precision | 0.6341 | FAIL (gate >= 0.99) |
| Critical false ENTAILS | 3 | FAIL (gate = 0) |
| Critical false CONTRADICTS | 4 | FAIL (gate = 0) |
| Insufficient recall | 0.6667 | FAIL (gate >= 0.90) |
| Burned TRAIN | atom relation accuracy 0.3614, unsound eligible 0 | diagnostic only |
| Decomposition | 44/44 | PASS |
| RC2 frozen regressions | 37/37 | PASS |
| Tier-1 gate | no invalid proofs, no critical auto errors | PASS |
| Tier-1 operators | 43/43 | PASS |
| RC3 dev pytest | 24/24 | PASS |
| Evaluator regression | 120/120 | PASS |
| KB baseline | 48/48 BESTATT | PASS |
| Quote-aligner | 2 date-window drifts (MP-015A, CI-021) + 4 pre-existing mismatches identical to recorded QA06 | PRE-EXISTING |
| Determinism | two full relation runs identical | PASS |
| Validation seal | SHA 15b13bb7006e... match, unopened | PASS |
| qa_check.sh | not present in this tree | N/A |

## Bounded bugfix pass (spec 29)

The single allowed bounded bugfix pass was implemented (negation scope
helpers, modality/actor/condition passthrough, R05b/R05c/R09b/R09c/R11b/
R16c/R16d/R16e, R26b rework, R27/R28 gate rework, R29/R30/R31 guards),
then fully reverted: it moved atom accuracy 0.6596 -> 0.6862 but
degraded frozen boundary safety (entailed-support recall 0.9730 ->
0.8649, train unsound-eligible 0 -> 1, critical false ENTAILS 3 -> 4).
Spec 32 forbids trading boundary safety for relation gains. The pre-pass
engine was restored byte-identically (SHA-verified) and the verdict is
recorded in bounded-bugfix-pass-results.json.

## Boundary per-dimension note

On the restored engine the four hard safety gates pass, but fresh
per-dimension boundary accuracies (negation 0.95, modality 0.70,
condition/exception 0.67, actor/scope 0.80, temporal/numeric 0.60)
do not reproduce the boundary task's recorded frozen per-dimension
values (1.0 / 0.95 / 1.0 / 1.0 / 0.9). The recorded run used engine SHA
c4bc7186...; the current runtime engine SHA differs. This drift
predates this task and is reported as a pre-existing observation.

## Runtime stability

run_relation.py completed all registered outcome rows with 0 unhandled
exceptions in every run (baseline, pass, restored).
