# RC-01 Root Cause: input/schema compatibility

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1

## Symptom

9 of 120 frozen Phase 3 predictions end in EXECUTION_FAILED with S1
validation errors (input_normalization TERMINAL). Failure-analysis
classified the mechanism as input/schema related.

## Diagnosis (source-verified)

- `make_context()` (`runtime/sut/context.py`) calls `validate_input()`
  strictly; `run_with_trace()` (`runtime/sut/phase2/pipeline.py`) maps
  the resulting SchemaError to a terminal failed output.
- The runner loader (`evaluation/full-sut-implementation-phase3/sut_runner/loader.py:strip_gold`)
  passes `case["profile"]` verbatim; it also always emits top-level
  `context: {}` and `location_context: {}`.
- `sut-input.schema.json` declares `profile` with
  `additionalProperties: false` and only `age` (integer 0-120) and
  `role`. It has no optional `context` inside profile and no
  `household_children`.

## Classification per corpus profile shape (mechanism-level, no case IDs)

| Shape | Class | Reason |
|---|---|---|
| `age: null` with role present | A - valid input representation not accepted | Unknown age is a legitimate caller state; the schema forbids null |
| `context` inside profile | A | The top-level `context` field exists, but a nested caller context is legitimate and rejected only by `additionalProperties: false` |
| `household_children: int` and `household_children: true` | A | Household structure is legitimate caller context; int-or-boolean is the corpus representation of "N children" / "children present" |
| `profile: {}` (empty) | not a failure | Already schema-valid |

No case is class B (invalid corpus input), C (loader bug) or
D (normalization bug): the loader faithfully passes caller data, and the
data is semantically well-formed. Therefore no STOP condition applies.

## Repair design

Canonical normalization at the SUT input boundary plus a strict
post-normalization schema:

1. `normalize_input()` in `runtime/sut/context.py` (single normalization
   point, used by `make_context`):
   - `profile.age`: `null` -> key dropped (optional in schema); non-int
     numeric strings are NOT coerced (keep fail-closed for malformed).
   - `profile.context`: moved to top-level `context` (merge, caller
     top-level wins); never contains gold (loader guard still runs).
   - `profile.household_children`: `true` -> 1, `false` -> 0, int stays;
     malformed values are kept in place so the strict post-normalization
     schema rejects them (fail closed, not guessed).
2. Schema extension (`sut-input.schema.json`): `profile.age` becomes
   nullable (type ["integer","null"], 0-120), optional
   `profile.household_children` (["integer","boolean"], min 0), and
   normalization removes the nested `context` alias before validation.
   Strictness preserved: unknown profile keys still rejected.
3. No downstream alternate-type branches: after normalization the rest
   of the pipeline sees the same canonical shapes as before
   (`profile.get("age")` returns None when age absent/null).

Invariant: VALID_SUPPORTED_INPUTS_REJECTED = 0 while malformed inputs
(bad types, unknown fields, out-of-range age) still fail closed.
