# RC-A Effect Analysis - Route Emission Repair

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-3 measurement, frozen Wave-2 measurement, frozen Wave-3 structural replay diagnostics, frozen W3-RC-A v1 candidate manifest (routes.py, 1 component changed from Wave 2).

## Emission funnel movement (observed)

- Structured route cases: 20 (W2) -> 24 (W3); including 4 route-emitter cases that are route-criteria NOT_APPLICABLE (DIS-096, ROUT-029, ROUT-053, ROUT-059), 28 of 120 cases now emit route structure.
- Structured route entries: 24 -> 39. Distinct route labels: 14 -> 24.
- no_route_asserted cases: 100 -> 92.
- Funnel stages (W3): R0 = 84, R1 = 9, R3 = 11, R5 = 4; R2/R4/R6+ = 0. W2 reference: R0 = 89, R1 = 19.

The repair moved the emission funnel exactly where it was scoped: fewer silent no-route answers, more structured entries, more distinct labels.

## Semantic endpoint (unchanged)

- Route PASS: 0 / 108 evaluated, W2 and W3. Route FAIL: 108 (106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL).
- Label-to-evidence binding remains mechanically unresolvable: 0 / 24 structured-emitter cases in W3 (0 / 20 in W2). evidence.route_evidence is keyed by R-codes, not route labels, so no emitted label can be bound to supporting evidence.
- The 2 PARTIAL verdicts are lexical token artifacts (ROUT-040 "NAV" inside a NEGATED gold clause; ROUT-061 "Familievernkontoret" token match without first-line commitment), not partial semantic passes.

## Verdict

RC-A (W3-RC-A v1): PARTIALLY_EFFECTIVE. The emission-stage mechanism it targeted moved as designed; the semantic endpoint did not. Route correctness is gated one stage downstream on label-to-evidence binding, which remains unimplemented (RC-04 still indicated). More emission structure without binding produces more labels to adjudicate, not usable routes.

