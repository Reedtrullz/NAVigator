# Fresh Holdout Readiness

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY

**Verdict: NOT_READY_FOR_FRESH_HOLDOUT**

## Basis
- Route PASS = 0/108 in Wave-3, unchanged from Wave-2; the dominant failure stage R0_NO_STRUCTURED_ROUTE (84/108) is unresolved.
- The only measurement movement since Wave-2 (2 PARTIAL verdicts, ROUT-040/061) is MEASUREMENT_SENSITIVITY (token-substring artifacts), not semantic route progress.
- The binding join and structured route evaluation (W4-RC-A) are not implemented; a fresh holdout would re-measure the same lexical dead end on new data and produce no new information about the mechanism.

## Gate to revisit
A fresh holdout becomes justifiable only after a Wave-4 candidate implementing WAVE4_ROUTE_TARGET_PLUS_BINDING is frozen and its regression suites pass. This task consumes no fresh evidence.
