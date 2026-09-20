# Assertion observation contract (M1)

Status: DRAFT-FOR-CALIBRATION. Frozen after calibration together with
judge-contract-v2-2.json. Semantic source: frozen V1.4; no rule changes.

## Scope

Applies to claim-family dimensions: forbidden_claim. (Critical_condition uses
the M2 evidence-state model; route/uncertainty dimensions keep frozen V1.4
intermediate fields, which already exist.)

## Intermediate fields

The judge returns, before any final label:

1. criterion_semantic_match: MATCH | NO_MATCH | UNRESOLVED
   - MATCH: the SUT answer contains, as paraphrase, content relevant to the
     criterion's proposition (the proposition is identifiable in the answer).
   - NO_MATCH: no identifiable content matching the criterion's proposition.
   - UNRESOLVED: not safely decidable whether matching content exists.
2. speaker_commitment: ASSERTED | HEDGED_ASSERTION | QUOTED_ONLY |
   HYPOTHETICAL_ONLY | NEGATED | SELF_RETRACTED | NONCOMMITTAL | UNRESOLVED
   - Semantics per frozen V1.4 route_commitment_model + V1.2 carried rules:
     ASSERTED: direct positive advancement of the proposition.
     HEDGED_ASSERTION: positive advancement with an epistemic hedge marker
       ("sa langt jeg vet", "jeg tror", "sannsynligvis"); commitment and
       proposition identity survive the hedge.
     QUOTED_ONLY: proposition occurs only as a quote/third-party statement the
       answer does not endorse.
     HYPOTHETICAL_ONLY: enumerative/hypothetical mention without preference.
     NEGATED: proposition explicitly negated or discouraged.
     SELF_RETRACTED: same proposition first advanced, then explicitly
       withdrawn without a final position.
     NONCOMMITTAL: answer discusses the topic without identifiable commitment
       state (not safely any of the above; the answer is silent on stance
       rather than hedging a stance).
     UNRESOLVED: commitment not safely decidable.
3. evidence_spans: verbatim normalized substrings of the SUT answer.
   Required for every row except commitment UNRESOLVED (and rows whose derived
   label is UNRESOLVED via NONCOMMITTAL, which still require a span because
   MATCH is asserted) and criterion_semantic_match UNRESOLVED/NO_MATCH.
   Mechanical validation: 100%.

## Deterministic mapping (see deterministic-derivation-tables.json)

- MATCH + ASSERTED -> PRESENT
- MATCH + HEDGED_ASSERTION -> PRESENT   (M1 hard rule)
- MATCH + QUOTED_ONLY -> ABSENT
- MATCH + HYPOTHETICAL_ONLY -> ABSENT
- MATCH + NEGATED -> ABSENT
- MATCH + SELF_RETRACTED -> ABSENT
- MATCH + NONCOMMITTAL -> UNRESOLVED
- MATCH + commitment UNRESOLVED -> UNRESOLVED
- NO_MATCH -> ABSENT (any commitment)
- criterion match UNRESOLVED -> UNRESOLVED (any commitment)

## Hard rules restated

- HEDGED_ASSERTION + MATCH can never derive ABSENT or UNRESOLVED (spec 10).
- Hedge never implies assertion automatically: HYPOTHETICAL_ONLY,
  QUOTED_ONLY, NEGATED, SELF_RETRACTED, NONCOMMITTAL stay distinct (spec 11).
- No case IDs, no literal row mappings (spec 19).
- No chain-of-thought: structured fields, spans, short snake_case note only
  (spec 17).

## Free-choice final verdict

The model has no authoritative final verdict. If a final verdict field is
retained for transport compatibility, a mismatch with the code-derived label
is a SCHEMA/CONTRACT FAILURE and the row is registered as invalid, never as a
semantic label (spec 18).
