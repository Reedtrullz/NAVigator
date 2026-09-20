# Fresh Holdout Readiness

## Status

**NOT_READY_FOR_FRESH_HOLDOUT**

## Basis

The frozen Wave-1 measurement shows the dominant residual mechanisms are structural, not marginal:

1. Route correctness: 0/108 evaluable route criteria PASS; 96/108 produce no usable structured route (PW1-R1).
2. Retrieval contamination: 104/120 answers, 75/120 claims, 2/120 routes polluted by unscoped national KB material (PW1-R4); all 6 residual forbidden failures are contamination-shaped.
3. Critical-condition: 69 PREMATURE_ABSENCE FAILs, largely downstream of route/retrieval emptiness (PW1-R2).
4. Evidence: 38/38 evidence criteria at 0.0 split into an attachment defect (23) and missing provenance (15) (PW1-R5, PW1-R6).

Running a fresh holdout against the current product candidate would measure these known structural defects again on new data without any diagnostic value added over the frozen 120-case measurement, and would burn holdout material.

## Preconditions to revisit

- Wave-2 repairs (RC-08 + RC-10 + RC-11, then RC-07) implemented and regression-clean.
- Frozen re-measurement on the existing 120 cases shows the route funnel and contamination counts materially moved.
- Owner-authorized holdout design with fresh sampling, freeze-then-blind scoring, and the same measurement semantics.

## Non-claims

This is an engineering readiness judgment for holdout timing, not a product-quality or certification statement. No fresh data was accessed in this task.
