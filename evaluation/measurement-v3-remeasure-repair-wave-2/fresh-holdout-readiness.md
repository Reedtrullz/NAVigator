# Fresh-Holdout Readiness - Decision Support Only

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY. This document is decision support; it is not certification, generalization evidence, or authorization to run any holdout.

## READINESS: NOT_READY_FOR_FRESH_HOLDOUT

## Basis (route correctness, safety, evidence, retrieval, regressions - not overall score)

1. Route correctness: 0 PASS on 108 route-evaluated criteria, unchanged from Wave 1. The funnel bottleneck moved but is unresolved: 15/24 route entries are junk-like, 2 fragment-like labels, and label-to-evidence binding is mechanically unresolvable in 20/20 structured-route cases. A dominant known mechanism is still fully active.
2. Safety: 2 new P0 under-triage candidates (ROUT-026, ROUT-088) plus 6 UNRESOLVED -> FAIL critical conversions with scorer-layer sensitivity (PREMATURE_ABSENCE / SEMANTIC_JUDGE_STUB markers). The safety mechanism is not controlled enough to spend fresh evidence on.
3. Evidence quality: materially improved (0.0 criteria 38 -> 23; provenance-linked claims 47.8 % -> 59.0 %), but 100 % provenance coverage coexists with 0 route PASS, so evidence attachment alone does not make routes usable.
4. Retrieval cleanliness: improved (forbidden FAILs 5 -> 3; 2 contamination failures resolved) but not clean: DIS-100 contamination-shaped failure persists and 103/120 answers still carry 2+ national-information blocks.
5. Regressions: 9 (8 critical_condition P0, 1 required_uncertainty P2), with an unresolved scorer-judgment-layer sensitivity mechanism between W1 LLM-reviewed and W2 deterministic observations.

## Interpretation

Under the frozen spec's three-state taxonomy, the controlling factors are the unresolved route-target mechanism and the unadjudicated safety under-triage candidates. Neither LIMITED_FRESH_PROBE_JUSTIFIABLE nor READY_FOR_FRESH_HOLDOUT is defensible from the frozen artifacts. The next owner decision should address the route funnel mechanism and adjudicate the safety candidates before any fresh evidence is consumed.

Hard: this task runs no holdout, consumes no fresh cases, and changes no runtime.
