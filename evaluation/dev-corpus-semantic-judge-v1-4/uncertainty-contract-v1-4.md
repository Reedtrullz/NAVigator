# Uncertainty contract V1.4 (mode x behavior derivation)

## Defect being repaired

V1.3M Set A disagreements BUN-01 (NONE vs EXPLICIT_LIMITATION),
BUN-09 (UNRESOLVED vs VIOLATED), and BUN-13 (PARTIAL vs VIOLATED) showed
that the judge collapsed two questions into the verdict: what the
uncertainty requirement IS, and what the output DOES epistemically.
V1.4 separates these.

## Step 1 - uncertainty_requirement_mode (from the criterion alone)

Frozen V1.3 modes, unchanged semantics:

- NONE: the criterion imposes no epistemic restriction and no non-assertion
  behavior. requirement_applicable = NO.
- EXPLICIT_LIMITATION: the criterion requires the output to communicate an
  epistemic limitation. requirement_applicable = YES.
- NON_ASSERTION_CONSTRAINT: the criterion requires that a specific
  over-conclusion NOT be advanced, without requiring an expressed hedge.
  requirement_applicable = YES. NOT_REQUIRED is schema-invalid for this mode.
- COMPOUND: the criterion contains an expression requirement and/or several
  non-assertion components. requirement_applicable = YES.

Classification rule (from the criterion text alone):
1. Both an expression requirement and at least one non-assertion component
   (or several non-assertion components) -> COMPOUND.
2. Expression requirement alone -> EXPLICIT_LIMITATION.
3. Non-assertion component alone ("ikke konkluder med at X") ->
   NON_ASSERTION_CONSTRAINT. A negated criterion formulation ("kriteriet
   krever at svaret ikke konkluderer...") describes the CONTENT of the
   requirement, not the absence of one: it is NON_ASSERTION_CONSTRAINT,
   never NONE.
4. Otherwise -> NONE.

## Step 2 - output_uncertainty_behavior (from the SUT output alone)

Observable output classes, annotated separately from the mode:

- NONE: the output performs no epistemic handling of the constrained
  proposition at all - it neither advances nor qualifies it (it may answer
  other content). Distinct from silent violation: nothing is asserted.
- HEDGE: the output softens claims with hedging markers ("kanskje",
  "muligens", "jeg tror") but does not express the specific required
  limitation.
- EXPLICIT_LIMITATION: the output expresses the specific epistemic
  limitation the criterion targets ("tilgangen er ikke verifisert").
- PARTIAL_LIMITATION: a limitation is expressed but only partially or
  generically - not the specific required limitation, or not covering all
  required parts.
- CONTRADICTORY_LIMITATION: the limitation is expressed and then undercut by
  an assertion that contradicts it in the same output.
- OVERCONFIDENT_ASSERTION: the output asserts or implies the constrained
  conclusion (or, for non-assertion modes, the forbidden conclusion) with no
  limitation or hedge.
- UNRESOLVED: the epistemic handling cannot be safely determined from the
  text.

For COMPOUND modes, behavior is recorded per component:

    compound_components: [
      { "kind": "EXPRESSION" | "NON_ASSERTION", "behavior": <class above> }
    ]

EXPRESSION components derive verdicts like EXPLICIT_LIMITATION; NON_ASSERTION
components like NON_ASSERTION_CONSTRAINT.

## Step 3 - verdict derivation (frozen table)

Verdict is derived mechanically from mode + behavior. It is never chosen
directly for single-component modes.

### NONE mode

Any behavior -> NOT_REQUIRED. Voluntary hedging in the SUT output never
changes this.

### EXPLICIT_LIMITATION mode

| behavior                 | verdict   |
|--------------------------|-----------|
| EXPLICIT_LIMITATION      | SATISFIED |
| PARTIAL_LIMITATION       | PARTIAL   |
| HEDGE                    | PARTIAL   |
| CONTRADICTORY_LIMITATION | PARTIAL   |
| OVERCONFIDENT_ASSERTION  | VIOLATED  |
| NONE                     | UNRESOLVED|
| UNRESOLVED               | UNRESOLVED|

Rationale: PARTIAL is legitimate because an identifiable part of the
requirement (or a weaker form of it) is fulfilled. Behavior NONE means the
output never touched the constrained proposition: nothing conflicts with the
requirement, so absence is NOT automatically VIOLATED; the requirement is
simply unmet with no evaluable handling -> UNRESOLVED.

### NON_ASSERTION_CONSTRAINT mode

| behavior                 | verdict   |
|--------------------------|-----------|
| NONE                     | SATISFIED |
| HEDGE                    | SATISFIED |
| EXPLICIT_LIMITATION      | SATISFIED |
| PARTIAL_LIMITATION       | SATISFIED |
| CONTRADICTORY_LIMITATION | VIOLATED  |
| OVERCONFIDENT_ASSERTION  | VIOLATED  |
| UNRESOLVED               | UNRESOLVED|

Rationale: the constraint is "do not advance conclusion X". If the output
does not advance X - whether it stays silent, hedges, or even expresses a
limitation - the constraint is SATISFIED (evidence_basis =
ABSENCE_OF_PROHIBITED_ASSERTION). VIOLATED requires X to be advanced or
implied, with at least one mechanical verbatim span proving it. This table
is the explicit implementation of the absence-vs-violation rule.

### COMPOUND mode

Per component: derive the component verdict using the row above matching its
kind (EXPRESSION -> EXPLICIT_LIMITATION row; NON_ASSERTION ->
NON_ASSERTION_CONSTRAINT row). Then aggregate:

- all components SATISFIED -> SATISFIED
- any VIOLATED and at least one SATISFIED -> PARTIAL
- all components VIOLATED -> VIOLATED
- no VIOLATED, at least one SATISFIED (rest UNRESOLVED) -> PARTIAL
- no VIOLATED, no SATISFIED (all UNRESOLVED) -> UNRESOLVED

PARTIAL-vs-UNRESOLVED frozen rule: PARTIAL requires an identifiable part of
the requirement to be fulfilled. UNRESOLVED means it cannot safely be
determined whether the output satisfies or violates the requirement. PARTIAL
is never used as "mild uncertainty".

## Evidence rules

- TEXT_SPAN: standard requirement - at least one verbatim quote from the SUT
  output for every SATISFIED (expression) / VIOLATED verdict.
- ABSENCE_OF_PROHIBITED_ASSERTION: allowed for SATISFIED on non-assertion
  components; the judge records which criterion proposition was checked; no
  span may be invented.
- VIOLATED on a non-assertion component ALWAYS requires at least one
  mechanically verifiable span from the SUT output showing the forbidden
  conclusion.
