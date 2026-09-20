# Fresh Holdout Readiness (Wave 2 candidate)

## Verdict: NOT_READY_FOR_FRESH_HOLDOUT

## Reasons
1. Route PASS 0/108 with dominant bottleneck R0 (89 criteria, no structured routes): fresh holdout would measure an absent capability, not a repaired one.
2. The primary Wave-3 repair (route-proposition construction) is not implemented; fresh cases cannot confirm a repair that does not exist.
3. Unresolved measurement-sensitivity findings (R3 unconditional fire; certainty-marker breadth; paraphrase matching) would inject known scorer noise into a fresh holdout.
4. One criterion (ROUT-026::forbidden:01) remains PENDING_LLM_ADJUDICATION in the Wave-2 measurement (carried per task lock; does not block engineering diagnosis, but the lineage is not adjudication-complete).

## Re-assessment condition
A fresh holdout becomes justifiable only after: Wave-3 RC-A implemented and re-baselined under the frozen scorer, deliberate owner decision on measurement-sensitivity repairs, and adjudication path for the pending criterion. Limited probes are not recommended either: the R0 failure is structural and already proven on 89/108 criteria.
