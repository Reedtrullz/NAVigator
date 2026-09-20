# Uncertainty Decision Tree v2.7e (DRAFT)

Frozen order. Annotators and judges follow these steps in sequence.

## Step 1 - Requirement mode

Classify the criterion's uncertainty requirement mode:
NONE, EXPLICIT_LIMITATION, NON_ASSERTION_CONSTRAINT, or COMPOUND.

NONE => verdict NOT_REQUIRED. Stop.

## Step 2 - Behavior classification

Classify the output's uncertainty-related behavior:
NONE, HEDGE, EXPLICIT_LIMITATION, PARTIAL_LIMITATION, CONTRADICTORY_LIMITATION,
UNCLEAR_PROSE, OVERCONFIDENT_ASSERTION, UNRESOLVED.

Precedence for the repaired boundary:
1. If the limitation-related text is incoherent or fragmentary at sentence
   level such that no behavior can be safely classified => UNCLEAR_PROSE.
2. If the limitation prose contradicts itself or retracts itself at sentence
   level => CONTRADICTORY_LIMITATION. This is not "mild" qualification and
   never maps to PARTIAL under EXPLICIT_LIMITATION.
3. Otherwise classify normally per V1.4 definitions.

## Step 3 - Derivation

Apply the v2.7e derivation table for the mode (see contract JSON).
Key changed cells vs V1.4:
EXPLICIT_LIMITATION x CONTRADICTORY_LIMITATION: PARTIAL -> UNRESOLVED.
All modes x UNCLEAR_PROSE: UNRESOLVED.

## Step 4 - Compound aggregation

For COMPOUND, derive per component with repaired tables, then aggregate
per the frozen compound rule in the contract.

## Boundary statements

PARTIAL remains valid only for limitation prose that communicates a real,
identifiable, incomplete qualification.
UNRESOLVED covers contradictory, self-retracted, and incoherent limitation
prose, and any text where fulfilment or violation cannot be safely determined.
Absence of uncertainty language is never automatically VIOLATED.

## Preregistered compound observation (rule unchanged)

The V1.4 compound aggregation rule is preserved verbatim. Consequence: a
COMPOUND with one UNRESOLVED component and one SATISFIED component
aggregates to PARTIAL under "no VIOLATED with some SATISFIED => PARTIAL".
This is flagged for attention during Set A calibration; if humans
disagree on compound rows, that becomes a separate boundary finding.
The rule itself is NOT changed by this task.
