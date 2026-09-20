# V1.6A Pre-Classifier Integration Design

## Pipeline position

    scorer -> boundary pre-classifier (this task) -> semantic judge (only if needed)

The pre-classifier sits after the deterministic scorer and before any judge
model call. For each of the three boundary dimensions (route commitment,
uncertainty behavior, assertion scope) the classifier returns either a
deterministic boundary label with a mechanically validated evidence span, or
an ABSTAIN with a reason.

## Routing contract

- Deterministic non-ABSTAIN label: the boundary sub-verdict is passed to the
  scorer/judge pipeline as fixed metadata. The judge is NOT called for that
  dimension's boundary question.
- ABSTAIN: the judge is called; the abstain reason is passed as context.

Hard invariant: **LLM_OVERRIDE_OF_BOUNDARY_PRECLASSIFIER = 0**. A deterministic
non-ABSTAIN boundary label cannot be overwritten by the judge. The judge sees
it as fixed input, like the deterministic scorer output, not as a proposal.

## What the pre-classifier does NOT decide

It never emits a final semantic verdict (ACCEPTABLE, PARTIAL, VIOLATED, ...),
never a critical or forbidden outcome, and never a route correctness verdict.
It resolves only observable commitment/scope states:
ASSERTED, HEDGED_ASSERTION, NEGATED, SELF_RETRACTED, QUOTED_ONLY,
HYPOTHETICAL_ONLY, VAGUE_NONCOMMITTAL, EXPLICIT_LIMITATION, PARTIAL_LIMITATION,
CONTRADICTORY_LIMITATION, HEDGE, OVERCONFIDENT_ASSERTION, NONE, RETRACTED,
USER_REPORTED, THIRD_PARTY_QUOTED, HYPOTHETICAL, SYSTEM_ENDORSED.

The judge maps these states plus the criterion to final labels.

## Judge-call reduction

Measured on the burned V1.4 diagnostic replay
(burned-v1-4-diagnostic-replay.json): 70% of boundary-dimension fixtures
(35/50) were resolved with no judge call; with structured criteria in
production the uncertainty-family share is conservative (text-only NONE
classifications become OVERCONFIDENT_ASSERTION, still deterministic).
Route-family abstains (15/25) are judge-required by design.

## Known limitations

- Marker-inventory ceiling: finite regex sets, not parsers; unrecognized
  phrasing fails closed to ABSTAIN (precision-first), never to a silent label.
- OVERCONFIDENT_ASSERTION requires a structured criterion with
  required_limitations; prose criteria get abstain-style behavior instead.
- Interrogative outputs abstain in all three dimensions by frozen rule.
- The single false deterministic on the official 120-fixture run
  (VR-H-08, route family) is the known open defect; it is why the task
  terminates NOT_READY and must be fixed in a NEW task before V1.6B.
