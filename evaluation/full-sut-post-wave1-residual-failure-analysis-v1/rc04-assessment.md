# RC-04 Assessment: Uncertainty

RC-04 (uncertainty/epistemic repair) was deferred from Wave 1. This assessment determines whether the residual uncertainty failures are an independent bug or downstream of routing/retrieval.

## Current residual uncertainty failures

| Measure | Wave 1 |
|---|---|
| VIOLATED | 0 (old: 2; both moved to PARTIAL by RC-02 and held) |
| PARTIAL (DEGRADED) | 36 (24 ROUT, 12 SAF) |
| UNRESOLVED uncertainty criteria | 0 |
| Absence assertions as uncertainty failure | not separately scored; captured under critical PREMATURE_ABSENCE (PW1-R2) |

Epistemic states of the 36 affected cases: EXISTENCE_ONLY (28), UNVERIFIED (8).

## Independent bug or downstream?

The 36 PARTIAL cases share one shape: the product signals existence-only or unverified state, but does not emit the specific qualification wording the frozen criterion requires. In nearly all of these cases the product has no usable route to qualify: 96/108 route criteria have no usable structured route (PW1-R1), and the affected answers are dominated by unscoped national retrieval blocks instead of a track-relevant route statement.

An uncertainty-wording repair applied now would mostly decorate answers that still fail route_correctness outright. It cannot convert PARTIAL to PASS where the underlying route/retrieval content is missing, because the required qualification is about a concrete route/access statement the product never produces.

## Conclusion

Most uncertainty failures are **B: downstream consequence of wrong routing/retrieval**, not an independent epistemic bug. The 0-VIOLATED result shows the failure-path/wording defects RC-04 targeted are already partly controlled.

**Do not recommend RC-04 yet.** Re-assess after route-target selection (PW1-R1) and retrieval scoping (PW1-R4) repairs: if PARTIAL uncertainty persists once usable routes exist, a narrow wording-stage repair becomes justified with a much smaller residual set.
