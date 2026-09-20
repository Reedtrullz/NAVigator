# Next-stage design brief (DIAGNOSTIC_ONLY - NOT A STAGE START)

Status basis: V1.6A.3 frozen (21047fda...f2563b); V1.6B terminal at
V1_6B_NO_JUDGE_QUALIFIES. This brief consolidates three diagnostic
layers (failure-taxonomy-diagnostic.json) into a concrete proposal for
the next bounded task. Nothing here is executed or authorized.

## Evidence-backed design

1. V1.6A.4 boundary extension (first, TDD):
   - Absorb form-decidable shared failures as generalized rules, NOT
     case mappings: conditional-consequent commitment (F-23), hedged
     assertive-matrix commitment (F-26), belief-verb commitment (F-27),
     competing-hedged-route-candidates -> UNRESOLVED when the criterion
     requires one clear route (R-11).
   - Expose inventory grounding to the residual judge context (R-26
     information gap): A3 already has service-noun grounding from
     V1.6A.1; the judge currently receives none.
   - Explicitly NOT absorbable deterministically: critical
     UNRESOLVED-disposition (C-28/29/30 are non-advisory epistemic
     observations, a subtle advice-act boundary) and critical
     negation-scope composition (C-20 double negation; both models
     failed). Critical stays judge-owned with calibrated abstention.
   - RED: the five burned rows above as development cases plus fresh
     near-miss canaries. GREEN: minimal rules, precision-first, ABSTAIN
     on doubt. Validation: entirely fresh frozen targeted set before
     any judge screen; no V4-style label reuse.

2. Judge selection V2 (second):
   - Screen candidates specifically on the two sub-skills accounting
     for all 9 shared wrong rows: (a) UNRESOLVED/PARTIAL disposition on
     ambiguous critical/uncertainty rows, (b) assertion-strength
     commitment on hedged/composed forbidden rows. A decisive-accuracy
     benchmark alone would select the wrong model class.
   - Fresh fixtures, one-shot, same frozen gate architecture as V1.6B;
     hard safety gates unchanged; no best-of-bad.

Quantified expectation from burned data: boundary extension alone moves
both failed candidates only to 0.9167 combined with safety forbidden FN
still nonzero; judge improvement alone leaves the form families and the
R-26 information gap unresolved. Both stages are required; neither
alone clears the frozen gates.

Out of scope until separately authorized: V1.6C official validation,
product runtime, full SUT, gate/threshold changes, new blind sets.

Concrete draft task prompt for stage 1: next-task-draft-prompt-v1_6a4.md
(DRAFT ONLY - awaiting explicit user authorization; workdir corrected
to evaluation/dev-corpus-semantic-judge-v1-6a4/ during audit).
