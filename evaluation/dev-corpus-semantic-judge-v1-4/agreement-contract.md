# V1.4 agreement contract

## Defect being repaired

The V1.3M frozen protocol computed overall agreement as raw serialized-row
equality, including the free-text note field. Result: 24/32 rows agreed on
every semantic field but scored 0.0 overall because the two passes worded
their diagnostic notes differently. The official semantic agreement metric
therefore measured annotation prose style, not semantic agreement.

## Agreement unit (V1.4, frozen)

FREE_TEXT_NOTE_AFFECTS_LABEL_AGREEMENT = false

The note is diagnostic evidence, never a score-bearing label. Evidence-span
obligations are unchanged: structured evidence fields remain required where
the contract demands them, but lexical equality of free-text explanations
never affects agreement.

### Score-bearing fields

Route dimension (per route fixture):

- proposition_present (YES / NO / UNRESOLVED)
- speaker_commitment (ASSERTED / HEDGED_ASSERTION / HYPOTHETICAL_ONLY /
  QUOTED_ONLY / NEGATED / SELF_RETRACTED / UNRESOLVED)
- route_verdict (ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE / UNRESOLVED)

Uncertainty dimension (per uncertainty fixture):

- uncertainty_requirement_mode (NONE / EXPLICIT_LIMITATION /
  NON_ASSERTION_CONSTRAINT / COMPOUND)
- output_uncertainty_behavior for single-component modes; compound_components
  (per-component behavior records) for COMPOUND mode
- uncertainty_verdict (SATISFIED / PARTIAL / VIOLATED / NOT_REQUIRED /
  UNRESOLVED)

### Non-score-bearing fields

- note (free text)
- prose rationale wording
- formatting
- explanation wording

## Agreement levels (all reported, all mechanical)

1. FIELD AGREEMENT: per score-bearing field, over rows where both passes
   produced a valid structured result.
2. DIMENSION VERDICT AGREEMENT: route_verdict; uncertainty_verdict.
3. FULL SEMANTIC AGREEMENT: all score-bearing semantic fields for the row's
   dimension agree. This is the official overall agreement metric.
4. DIAGNOSTIC NOTE AGREEMENT: lexical note equality. Diagnostic only, never
   a gate, never reported as semantic agreement.

Raw serialized-row equality is permanently retired as an official semantic
agreement metric in this lineage.

## Error rows

Rows where a pass failed structurally (schema/transport) are reported
separately as error rows. Field agreement is computed over valid rows; the
error-inclusive variant is also reported so historical and V1.4 numbers stay
comparable. An error row is never scored as a semantic disagreement.

## Hard invariants carried forward

- NON_ASSERTION_CONSTRAINT implies applicability YES; NOT_REQUIRED is
  schema-invalid for this mode.
- SELF_RETRACTED/VAGUE commitments must not produce NO_ACCEPTABLE_ROUTE.
- Absence of uncertainty language is not automatically VIOLATED.
