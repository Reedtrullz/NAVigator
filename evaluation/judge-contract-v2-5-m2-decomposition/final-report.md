# V2.5 M2 Evidence-State Decomposition - Final Report

## Terminal status

`V2_5_REFERENCE_MODEL_CANNOT_USE_DECOMPOSITION`

Human decomposition contract is annotatable (60/60, all agreement gates at 1.0), but the
reference model failed calibration within the allowed two prompt iterations. Per spec
sections 23 and 43 this is a hard stop: no official 120-fixture phase, no stability run,
no further DeepSeek prompt tuning in this lineage.

## What was tested

- Hypothesis (spec section 9): M2 might be hard because one model call must emit an abstract
  evidence state directly; expressing it as four orthogonal intermediate observations
  (trigger_support / non_trigger_support / evidence_conflict / evidence_sufficiency) with
  deterministic derivation might make it tractable.
- Reference model: `opencode-go/deepseek-v4.1-flash` via the frozen local proxy (the only
  authorized wire ID). LongCat calls: 0. No other models.
- Calibration set: 36 burned M2 rows of the V2.4 calibration fixtures
  (6 clear_trigger, 6 clear_non_trigger, 18 ambiguous_conflicting, 6 insufficient_to_decide).
  One model call per fixture per iteration. No CoT. Final verdict derived in code.

## Results

| Metric (spec section 23 gate) | Iteration 0 | Iteration 1 | Gate |
|---|---|---|---|
| Valid structured rate | 36/36 = 1.00 | 35/36 = 0.972 | (official gate 0.99) |
| Derived final accuracy (>= 0.95) | 18/36 = 0.500 | 30/36 = 0.833 | FAIL both |
| trigger_support (>= 0.90) | 0.833 | 1.000 | FAIL / PASS |
| non_trigger_support (>= 0.90) | 0.833 | 0.833 | FAIL both |
| evidence_conflict (>= 0.90) | 0.389 | 0.765 | FAIL both |
| evidence_sufficiency (>= 0.90) | 0.000 | 1.000 | FAIL / PASS |
| Critical FN (0) | 1 | 1 | FAIL both |

Iteration 0 to iteration 1 moved derived-final accuracy from 0.50 to 0.833, but the
two-iteration budget was exhausted before reaching the 0.95 gate.

## Iteration 1 prompt delta (schema-comprehension only)

Three bounded clarifications, no semantic-definition change (spec section 22):

1. Mixed-signal conflict operationalization: normalization/bagatellization alongside
   acknowledgment of severity counts as competing readings (evidence_conflict YES), even
   when neither part is a direct assertion.
2. On-topic-but-stanceless answers are evidence_sufficiency INSUFFICIENT, not the trivially
   classifiable absence case.
3. Requirement/condition statements are not condition assertions (trigger_support), and an
   explicit rejection formulation is textual exclusion (non_trigger_support).

Effect: sufficiency field 0/6 -> 6/6; conflict field 7/18 -> 13/17. The three clarifications
measurably worked but not far enough.

## Error attribution (spec section 35)

Iteration 0 (18 misses): 11x evidence_conflict under-reporting on competing-reading texts;
6x evidence_sufficiency over-reporting on on-topic-stanceless texts; 1x negation-scope
over-read (M2N-01: requirement statement read as condition assertion; explicit exclusion
missed).

Iteration 1 (5 label misses + 1 schema-invalid): 4x evidence_conflict under-reporting
(model still reads mixed-signal texts as clear exclusions); 1x overcorrection of M2N-01
(now INSUFFICIENT, still missing the explicit negation) - the only critical FN; 1x schema
invalid (M2A-02: non-verbatim evidence span; HTTP 200, no label produced, transport
observation only).

Zero misses originate from the derivation table itself: every misclassification traces to a
model misreported intermediate field. The decomposition contract is sound; the model
cannot fill it reliably.

## Accounting

- DeepSeek calls in V2.5: 74 total = 1 pre-fix burn (V24-CAL-M2A-01, validator error, no
  label) + 36 iteration-0 + 37 iteration-1 (36 + the documented M2A-01 re-run, matching the
  failed-transport precedent).
- Runner defect found and fixed: the summary step crashed with KeyError because valid entries
  lacked gold_state; first summaries were computed offline from checkpoint files and frozen
  gold (see compute-calibration-summaries.py). The runner's critical_fn silently undercounted;
  corrected value is 1 for both iterations.

## Artifact SHAs (frozen at terminal)

- Contract: 173d123b5d49d2ef1149427d3be647d8bd4bff666333e6b81b066b935d0c01ed
- Prompt file (ITER0 + ITER1): 5678aba7798fd58e1aeccb273003b28f8aeb9036b066e3bd1d32ea72ba94a89c
- Validator: 55e84086670d3afedf9bc24b8747d83d705d309cede521187020aaf0536c2d24
- Derivation table: 0349f2bde30045b808c39beef8a8a3bb0693783ddac3669d4b667f8f70565435
- Full list: calibration-artifact-shas.json

## Gates passed

- Human annotatability (60 fixtures, dual pass): overall 1.0, per-field 1.0, derived 1.0.
- Schema/derivation offline checks: PASS.
- Contract freeze, collision audit, burned-data registry: intact, unchanged.

## Gates failed (calibration, spec section 23)

- Derived final accuracy >= 0.95: 0.833 at iteration 1.
- non_trigger_support >= 0.90: 0.833.
- evidence_conflict >= 0.90: 0.765.
- Critical FN = 0: 1.

## Not run (blocked by calibration stop)

- Official 120-fresh-fixture validation, gold freeze, one-shot DeepSeek validation,
  stability suite, burned retrospective, evaluator freeze. None of these artifacts exist.

## Spec section 38 decision

`NO_M2_MODEL_LIMIT`: the human contract is clearly annotatable, but the reference model
cannot populate the intermediate fields reliably enough within two prompt iterations.

## Recommended next architecture stage (per spec section 40)

1. Human-review lane for M2 ambiguous/conflicting cases (the model's residual failures are
   concentrated exactly there; clear cases are now 11/12 and were 12/12 on trigger side).
2. Ensemble/adjudication over the intermediate fields, or a specialized evaluator for the
   conflict field.
3. NOT: further DeepSeek prompt tuning (exhausted), NOT: automatic 12-model screening
   (remains unauthorized), NOT: any product/runtime work.

## Protocol integrity

- LongCat calls: 0. GPT-5.5: not used. No subagents used.
- No historical artifacts modified; no product runtime changes; no full SUT; no holdout.
- Historical terminal statuses preserved unchanged.
