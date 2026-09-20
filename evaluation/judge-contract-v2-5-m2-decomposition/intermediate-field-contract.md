# Intermediate Field Contract (Spec Sections 12-13)

This contract defines the new intermediate sub-fields for the M2 dimension.
Final semantic verdicts and their meanings are unchanged; the sub-fields are
intermediate only, and the final M2 state is derived deterministically.

## Sub-fields

### trigger_support

Does the SUT answer put the trigger condition forward as holding for the relevant group/subject?

Canonical values: `PRESENT` | `ABSENT` | `UNRESOLVED`

- PRESENT: at least one verbatim span puts the condition forward (direct assertion, paraphrase, or hedged-but-committed assertion, per frozen L68/L73).
- ABSENT: no span puts the condition forward. Requires absence judgment over the whole relevant answer.
- UNRESOLVED: cannot be safely determined whether the condition is put forward.

Evidence: PRESENT requires >= 1 verbatim evidence_span from the SUT answer. ABSENT and UNRESOLVED require no span (absence is not evidenced by an invented span).

### non_trigger_support

Does the SUT answer put forward exclusion/negation of the condition as holding (positive textual exclusion)?

Canonical values: `PRESENT` | `ABSENT` | `UNRESOLVED`

- PRESENT: at least one verbatim span excludes or negates the condition (frozen L69 semantics).
- ABSENT: no exclusion signal present.
- UNRESOLVED: cannot be safely determined.

### evidence_conflict

Do competing readings of the condition's applicability coexist in the answer?

Canonical values: `YES` | `NO` | `UNRESOLVED`

- YES: mixed signals, empathy combined with minimization, severity-affecting normalization, autonomy openings that are not themselves assertions - per frozen L70. Conflict must NOT be inferred from hedging alone (frozen L73).
- NO: no competing readings; polarity is textually clear (possibly trivially, when neither support exists).
- UNRESOLVED: cannot safely determine.

### evidence_sufficiency

Does the answer contain the information the criterion needs for classification?

Canonical values: `SUFFICIENT` | `INSUFFICIENT` | `UNRESOLVED`

- SUFFICIENT: there is enough textual basis to classify trigger polarity (including the trivially-classifiable cases where the answer plainly does not address the condition).
- INSUFFICIENT: the answer lacks information the criterion needs (frozen L71).
- UNRESOLVED: cannot safely determine.

### evidence_spans

Array of verbatim spans from the SUT answer. Required (>= 1) exactly when trigger_support=PRESENT or non_trigger_support=PRESENT. Otherwise empty. No invented spans.

### note

Short snake_case note, as in the frozen intermediate schema.

## Independence requirements

1. Each field is judged on its own question, in the order: trigger_support, non_trigger_support, evidence_conflict, evidence_sufficiency.
2. evidence_conflict and evidence_sufficiency are NOT derived from the polarity fields by the model; they are independent judgments. (The derivation table derives the final state from all four; it does not let the model skip the intermediate questions.)
3. Hedging affects only the polarity judgment's committedness, never conflict or sufficiency by itself.

## Conservative default

Any sub-field the judge cannot answer safely is UNRESOLVED. Unknown combinations in the derivation table map to UNRESOLVED. No combination ever maps OUT of UNRESOLVED-family into a CLEAR state except via the explicit PRESENT/ABSENT + conflict NO + sufficiency SUFFICIENT paths defined in the derivation table.
