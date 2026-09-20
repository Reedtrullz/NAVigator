# RC-02 Root Cause: safety/triage granularity collapse

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1

## Symptom

19/20 frozen safety predictions mismatch gold safety_priority; 17
collapse to ACUTE_RISK_NOW. No observed under-escalation on genuinely
acute dev cases.

## Diagnosis (source-verified)

The internal S2 taxonomy is a 12-value `safety_class` vocabulary
(`data/safety-triage-rules-v2.json:class_collapse`, verified: 12 classes
with per-class `priority` + `suppressed_routing`). The loss is
architectural and two-stage:

1. `runtime/sut/phase2/safety.py` collapses each class to the canonical
   3-value `priority` (ACUTE_RISK_NOW / URGENT_NOT_ACUTE / NOT_ACUTE) in
   `_result()`; 8 of 12 classes map to ACUTE_RISK_NOW in the rules file.
2. `ctx["safety"]["priority"]` (3-value) is the ONLY state that reaches
   S11. `finalize.py` additionally coerces anything unknown to
   ACUTE_RISK_NOW. The fine-grained `safety_class` and `signals` never
   reach the output.
3. `sut-output.schema.json` hard-codes the 3-value enum for
   `safety.priority` and the `safety_priority` mirror. The frozen scorer
   (`evaluation/dev-corpus-scorer-v1/scorer.py`, R1 rule) compares
   `safety_priority` EXACTLY against the 12-value gold taxonomy. The
   3-value enum is therefore a proven measurement-interface loss point.

## Repair design (deterministic authority preserved)

- Emit the deterministic 12-value `safety_class` as `safety_priority`
  when classification succeeded (same rules file, same signal matching,
  same negation guard - no classification logic change).
- Unknown/failed states stay fail-closed: `TRIAGE_FAILED` and any
  unknown value map to ACUTE_RISK_NOW exactly as before (FC: never
  downgrade an unverifiable safety state).
- Schema change: `safety.priority` and `safety_priority` accept the
  12 canonical class values (superset that includes the old 3). This is
  an explicit, documented schema expansion, not a silent one; recorded
  here and in source-change-summary.md.
- No LLM authority introduced; S2 remains a frozen-rules deterministic
  classifier. Planner/render safety-lane logic keys off
  `suppressed_routing` and `priority != "NOT_ACUTE"`, which remains
  correct for all 12 classes (11 map to non-NOT_ACUTE priorities and
  suppressed classes set the flag).

Acute invariant: every class whose frozen collapse priority was
ACUTE_RISK_NOW still maps to an ACUTE_RISK_NOW-class output value, so
known explicit acute triggers cannot be downgraded by this repair.
