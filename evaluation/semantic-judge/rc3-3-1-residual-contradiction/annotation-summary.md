# Annotation Summary - RC3.3.1 Targeted Suite

Corpus: fresh-targeted-cases.json (frozen 2026-09-08, 90 cases: 60 development T90-001..060, 30 hidden T90-061..090).

## Double-pass method

Pass 1: full 90-case authoring pass (relation, quantity identity, temporal applicability, quantity status, comparator applicability/relation, criticality).

Pass 2: independent adjudication of all 31 pass-1 CONTRADICTS labels against comparator-metric-contract-v2 and temporal-numeric-contract D1-D6, plus a full doctrine-consistency sweep of all 90 cases (reverse-direction review of non-conflict labels against D5 positive-conflict doctrine).

## Pass-2 outcome

Four pass-1 labels failed independent adjudication and were relabeled:

- T90-036 (development): claim states payment happens on the 10th; evidence states the payment deadline is the 20th. A deadline does not contradict an earlier execution date; different predicate. CONTRADICTS -> RELATED_BUT_INSUFFICIENT; temporal_applicability PERIOD_MISMATCH -> UNKNOWN; comparator_applicable true -> false (different-predicate comparison).
- T90-072 (hidden): claim states a regulation entered into force 19.10.2019; evidence is the regulation identifier FOR-2018-10-19-1584. The FOR-number date is the issue date, not an in-force date; the evidence asserts no in-force date. Accepting this as contradiction would reward exactly the unsound date-inference D4 exempts. CONTRADICTS -> RELATED_BUT_INSUFFICIENT; temporal_applicability PERIOD_MISMATCH -> UNKNOWN.
- T90-019 (development): claim "na 120000" vs evidence carrying an explicit current value 114 540 (fra 2026). Same-quantity current-vs-current value conflict: positive conflict under D5, not RBI. RELATED_BUT_INSUFFICIENT -> CONTRADICTS; temporal_applicability HISTORICAL_VS_CURRENT -> CURRENT_MATCH.
- T90-027 (development): claim "sist endret i 2023" vs evidence FOR-2024-04-26. Same explicit last-changed date quantity, positive conflict; same pattern as T90-022. RELATED_BUT_INSUFFICIENT -> CONTRADICTS; temporal_applicability PERIOD_MISMATCH -> NOT_APPLICABLE (law-reference date identity).

All 31 remaining conflict labels are same-quantity identity failures (role/qualifier/binding: delt vs full, aggregate vs component), same-window value/date conflicts, arithmetic identity conflicts, or deadline-vs-deadline conflicts; each satisfies D1/D4/D5 positive-conflict doctrine.

## Final distribution (frozen)

- relation: ENTAILS 39, CONTRADICTS 31, RELATED_BUT_INSUFFICIENT 20
- split: 60 development / 30 hidden
- groups: curhist 15, superseded 15, periods 14, sameqty 13, effdate 12, aggcomp 12, comparator 7, lawtrap 2
- quantity_identity populated: 84/90 (6 date-only deadline cases legitimately null)
- temporal_applicability populated: 90/90
- comparator_applicable: 14 (comparator_relation populated on all 14)
- critical: 32; compound: 0 (atom-level suite by design)

## Spec-22 target check

The spec targets are double-annotation agreement rates. With a single annotator, the practical reproduction is the independent second pass: 4 of 90 labels corrected (31 conflict labels re-adjudicated: 2 corrected; 59 non-conflict labels re-adjudicated against D5: 2 corrected). This is reported as single-annotator double-pass evidence, not independent inter-annotator agreement. The contract and corpus are frozen now (SHA 7228cffa3efbddea9ba30b34185052dff0327834ff831f9fde91b7974290f841); if the hidden micro-validation or global regression later shows label noise, that is recorded as corpus limitation, not repaired post-hoc.
