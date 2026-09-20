# Proof validator spec (oracle-reasoning-probe)

Purpose: deterministic post-validation of the structured-proof reviewer
output (probe spec 15-17). The validator is model-free.

## Validation pipeline

1. Output must be a JSON object with verdict, premises_used,
   inference_operator, derived_fact.
2. verdict in {SUPPORTED, CONTRADICTED, PARTIAL, INSUFFICIENT,
   REVIEW_REQUIRED}.
3. Every id in premises_used must exist in candidate_spans.
4. inference_operator must be in the allowed enum
   (see inference-operators.json) or NO_OPERATOR.
5. INSUFFICIENT requires NO_OPERATOR/absent operator.
   Any other verdict requires a real operator.
6. Operator preconditions are checked mechanically (regex/token checks
   in validate_proof.py). Examples:
   - EXHAUSTIVE_SET_EXCLUSION: premise must contain an explicit
     exhaustiveness marker (kun, bare, eneste, alle, ingen andre...).
     Without a marker the operator is invalid (spec 7-8).
   - NUMERIC_CONFLICT: premise must contain a number that differs from
     the claim numbers on the same axis.
   - SAME_PREDICATE_OPPOSITE_POLARITY: shared predicate plus negation
     marker on exactly one side.
7. derived_fact is checked for hallucinated content: every content
   term must appear in the claim or the cited premises (prefix-4 match
   allows Norwegian inflection).
8. Any validation failure means the output is not accepted; the runner
   records REVIEW_REQUIRED for that case.

## Deliberate ceilings

- ponytail: token-overlap preconditions are coarse (prefix-4 inflection
  fallback); a real deployment would embed this in the polarity engine.
  Upgrade path: share the aligner normalization and relation tags.
- Derivation soundness beyond preconditions is the model job; the
  validator blocks invented premises and forbidden operator use, not
  every wrong-but-well-formed proof.
