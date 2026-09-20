# Candidate v2 repair record (Wave 1, RC-01)

## Trigger

Structural replay on candidate v1 (attempt 1 of 2) produced 120/120
predictions but 2 EXECUTION_FAILED cases at stage input_normalization:

- SAF-007, SAF-011

This violated the Wave-1 RC-01 mechanism gate:

    KNOWN_RC01_INPUT_FAILURE_MECHANISM_REMAINS = 0

Per Wave-1 spec section 29, the frozen candidate was not patched in
place; a new candidate version was created within the lineage
(attempt 2 of 2).

## Root cause (RC-01 residual)

The failure analysis (repair-candidates.json, RC-01) explicitly named
the extended profile fields "context, household_children, non-integer
age forms". Candidate v1 normalized household_children and dict-valued
profile.context but not scalar (string) profile.context.

In the burned corpus, profile.context appears as a scalar string in
exactly 2 cases (both in safety_cases.json):

- "unconscious adult present"
- "professional receives disclosure"

normalize_input() restored the scalar value to profile, and the strict
post-normalization schema (profile.additionalProperties=false) rejected
it: "sut-input/v1 invalid: profile: unknown field 'context'".

## Fix (generalized, no case IDs in runtime)

normalize_input() now wraps scalar (str/int/float) profile.context into
the free-form top-level context object as context.situational_context:

- dict profile.context: unchanged merge behavior (top level wins)
- scalar profile.context: wrapped into context.situational_context;
  an existing top-level context.situational_context key wins
- list/null/other values: retained in profile so strict validation
  fails closed (unchanged fail-closed semantics)
- top-level context must be an object; if it is not, the scalar value
  is kept in profile and validation fails closed

The rule is idempotent and contains no case IDs or corpus literals.

## Tests

- test_scalar_profile_context_wrapped (wrap + idempotency)
- test_scalar_profile_context_top_level_wins (precedence)
- test_unsupported_context_shapes_fail_closed (list value; non-object
  top-level context)
- test_full_sut_accepts_scalar_profile_context (end-to-end, generic
  fixture, not a burned case)

Full suite: 170 passed, 0 failed
(167 in candidate v1 minus 1 replaced malformed-context test plus 4 new).
