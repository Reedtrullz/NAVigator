# Decomposition Hypothesis (Spec Sections 9-10)

## Hypothesis

If the single conflated five-value `critical_evidence_state` judgment is
decomposed into independent sub-fields - trigger-support presence,
non-trigger-support presence, evidence conflict, and evidence sufficiency -
and the final five-state semantic state is derived deterministically from
those sub-fields, then:

1. A reference model can meet the same per-state accuracy gates that the
   conflated single field failed (ambiguous-unresolved >= 0.90,
   insufficient-unresolved >= 0.90, clear-correct >= 0.95) within two prompt
   iterations, because each sub-question is independently decidable and the
   forced-binary compression error is structurally removed.
2. Human annotators will agree on the sub-fields at >= 0.95 per field, which
   the conflated field's UNRESOLVED-family could not guarantee.
3. The derivation table can be proven equivalent to the frozen V2.2 mapping
   for every reachable old-state input.

## Falsifiability

The hypothesis is falsified if any of:

- the human gate fails on any sub-field (status
  `V2_5_M2_DECOMPOSITION_NOT_ANNOTATABLE`), or
- after two calibration iterations the reference model still fails the
  sub-field gates (status
  `V2_5_REFERENCE_MODEL_CANNOT_USE_DECOMPOSITION`), or
- no equivalent derivation table exists that reproduces the frozen semantics
  for all old-reachable states.

In the first two cases the decomposition concept itself is invalidated as a
repair for M2, and the result is terminal for this task - no third mechanism,
no boundary expansion, no gate reduction.

## Absence vs contrary evidence (spec section 10)

The core failure signature in V2.4 was absence-of-assertion misread as
contrary evidence. The decomposed schema encodes the distinction explicitly:

- trigger_support = ABSENT: the answer does not put the condition forward.
- non_trigger_support = PRESENT: the answer puts forward exclusion or negation of the condition (positive textual exclusion).

These are independent: ABSENT + PRESENT is possible (the answer says "the
condition is not met"), ABSENT + ABSENT is possible (the answer says nothing
bearing on the condition), PRESENT + ABSENT is the classic trigger case.

ABSENT + ABSENT is not automatically UNRESOLVED: frozen L69 disjunct 1
("the answer clearly does not put forward the condition") makes trivial
absence a CNTS case when evidence_sufficiency = SUFFICIENT, deriving to
NOT_TRIGGERED. When evidence_sufficiency = INSUFFICIENT, the same combination
derives to ITD -> UNRESOLVED. That sufficiency split - not the polarity
fields alone - is what separates the two UNRESOLVED-family states the old
single field collapsed.

## Hedge vs ambiguity (spec section 11)

The frozen M2 doctrine: hedged-but-committed assertion is CLEAR_TRIGGER_SUPPORT (a hedge does not erase commitment); AMBIGUOUS_OR_CONFLICTING is reserved for cases where the assertion itself is uncertain, not merely weakened. The decomposed fields preserve this: a hedge lowers commitment strength but not trigger polarity; only genuinely competing readings produce conflict=YES. Hedges never move a case out of the CLEAR family by themselves.
