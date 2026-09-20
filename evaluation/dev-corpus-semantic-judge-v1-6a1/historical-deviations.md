# Historical Process Deviations (preserved from V1.6A)

## Annotation provenance

The two V1.6A annotation passes were performed by the same annotator.

- Correct metric name: `INTRA_ANNOTATOR_REPEATABILITY = 1.0`
- This must NOT be reported as `independent inter-annotator agreement = 1.0`.
- The V1.6A.1 targeted gold (60 fixtures) uses the same honest label:
  `INTRA_ANNOTATOR_REPEATABILITY` (dual-pass, single curator).

## Execution-order deviation

The V1.6A official deterministic run occurred before the agreement/gold
artifacts were completely materialized.

- The incident is preserved permanently.
- It is not erased or retroactively repaired: no engine edits occurred
  afterward, and V1.6A remains `V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY`.

## TDD sequence note for V1.6A.1

V1.6A.1 follows RED-first: the regression fixture runs against the
unmodified frozen V1.6A engine copy (behavioral RED: actual
`VAGUE_NONCOMMITTAL`, expected `ABSTAIN`) before any production change.
This is recorded in `tdd-red-result.json`.
