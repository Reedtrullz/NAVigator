# M2 Current-State Analysis (Spec Section 8)

No-model analysis of whether the frozen five-value `critical_evidence_state`
field conflates multiple decisions in one value.

## The five values encode two orthogonal questions

Reading the frozen definitions (frozen-semantics-trace.md):

1. **Trigger polarity**: does the answer put the condition forward (CLEAR_TRIGGER_SUPPORT) or exclude it (CLEAR_NON_TRIGGER_SUPPORT)?
2. **Decidability**: is the textual evidence safe to classify at all?

Values AMBIGUOUS_OR_CONFLICTING, INSUFFICIENT_TO_DECIDE, and UNRESOLVED all
map to the same final verdict (UNRESOLVED) but answer "decidability" with
three different reasons: competing readings, missing information, and
unclassifiable state itself. The five-value field therefore forces one label
to carry both polarity AND decidability AND reason-for-undecidability. That is
the conflation.

## Evidence from burned V2.4 iterations (diagnostic only)

Source: `judge-deepseek-v2-4-m2-validation/calibration-comparison.json` (frozen SHA 9054efbd...1b68), 40 burned fixtures, DeepSeek v4.1 flash, frozen prompt iterations 0-2:

| Gate | iter0 | iter1 | iter2 | Gate |
|---|---|---|---|---|
| m2_ambiguous_unresolved | 7/18 (0.389) | 11/18 (0.611) | 8/18 (0.444) | >= 0.90 |
| m2_insufficient_unresolved | 0/6 | 5/6 (0.833) | 6/6 (1.000) | >= 0.90 |
| m2_clear_correct | 12/12 | 11/12 | 12/12 | >= 0.95 |
| overall | 0.70 | 0.8333 | 0.8167 | (diagnostic) |

Observations:

- CLEAR cases are near-ceiling in every iteration (35/36 across iters). The model has no polarity problem.
- The persistent failure is concentrated: gold-UNRESOLVED cases forced into CLEAR states. Persistent failure mode quote from the frozen comparison: "Forced-binary collapse on gold-UNRESOLVED critical_condition cases; prompt-level mechanism clarification improved but never met the 0.90 gates in two iterations."
- Prompt iteration 0 vs 1 moved INSUFFICIENT 0/6 -> 5/6, showing the failure is addressable by mechanism, not model capability. But ambiguous stayed 0.389-0.611 across all three attempts - prompt-level clarification of a conflated field plateaued.
- The handoff-recorded dominant error signature: gold-UNRESOLVED forced to CLEAR_NON_TRIGGER_SUPPORT; at iter0 INSUFFICIENT_TO_DECIDE went to 0/6 UNRESOLVED with absence-of-assertion misread as contrary evidence. Absence of an assertion is NOT contrary evidence; the frozen contract itself says so for uncertainty (V2.2 L114), yet M2's single field gives the model nowhere to record "I see no trigger support AND nothing contradicting it" except a state that maps to NOT_TRIGGERED.

## Conflation analysis

The single field must answer, implicitly, four sub-questions:

a. Is trigger-supporting evidence present?
b. Is non-trigger-supporting (excluding) evidence present?
c. Do (a) and (b) conflict, or is the assertion itself ambiguous?
d. Is there enough information to decide?

The frozen enum lets the model answer with one of five values, but the model
must compute a-d jointly and compress the result. V2.4 evidence shows the
compression fails exactly where (a)=(absent) and (d)=(insufficient): the
model resolves "no evidence of X" into "evidence of not-X". A field that
asks (a) and (b) separately, plus explicit conflict and sufficiency fields,
removes the compression step.

## Conclusion

The conflation is real, structural, and evidenced. Decomposition into
independent sub-fields with deterministic derivation is the correct repair
direction under the frozen task lock. This satisfies spec section 8's
analysis gate.
