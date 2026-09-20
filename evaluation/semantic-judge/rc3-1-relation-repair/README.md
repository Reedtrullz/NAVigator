# RC3.1 Generalized Relation-Class Repair

Task: NAV-EXPLORE-RC3_1-GENERALIZED-RELATION-CLASS-REPAIR

Final status: RELATION_REPAIR_NOT_READY

The frozen support boundary candidate remains untouched and byte-identical
(engine SHA 4bd2845fac3535fba22ab3e242b51e80f0d2abbbb5d57a3123b7207b2383ea7d).
The single bounded bugfix pass (SEMANTIC_RELATION_LAYER_V2 rule battery
extension) was implemented, measured, and reverted: it improved atom
relation accuracy only to 0.6862 and degraded boundary safety, which
spec section 32 forbids. The sealed 60-case validation remains sealed
and unopened (SHA 15b13bb7006e... verified before and after).

Key files:

- relation-results.json - final restored-state relation metrics
- bounded-bugfix-pass-results.json - measured pass results (superseded)
- boundary-regression.json - restored-state boundary run
- train-diagnostics.json - burned TRAIN diagnostics
- regression-report.md - full suite table and bugfix-pass verdict
- final-report.md - SLUTTRAPPORT (77 items)
- relation-contract-v2.md / relation-metrics-v2.json / modality-relation-lattice.json - frozen contracts
- fresh-relation-cases.json - 120-case development suite
