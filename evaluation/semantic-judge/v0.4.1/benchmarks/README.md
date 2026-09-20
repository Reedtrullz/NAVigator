# v0.4 benchmark sets

Alle expected-etiketter er utledet av v0.4-spesifikasjonens regler
( CONTRADICTION PROOF OBLIGATION, modality model, actor semantics,
scope model ), ikke kopiert fra v0.3-fasit.

* minimal-pairs.json (24 pairs = 48 cases): one semantic dimension changed per pair
* contra-insuff.json (62 cases: 31 CONTRADICTED + 31 INSUFFICIENT)
* modality.json (30 cases): may/must, can/shall, usually/always, entitlement
* actor-scope.json (30 cases): member/class, exhaustive/non-exhaustive, service/role
* locality.json (20 cases): national vs Trondheim vs municipality-unspecified

Schema per case: {id, claim, source: {text}, expected, dimension, note}
Expected: SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE
