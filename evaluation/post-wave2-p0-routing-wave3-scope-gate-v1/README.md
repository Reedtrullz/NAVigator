# Post-Wave-2 P0 + Routing Diagnosis / Wave-3 Scope Gate V1

Task: NAV-EXPLORE-POST-WAVE2-P0-ROUTING-WAVE3-SCOPE-GATE-V1
Type: READ_ONLY diagnosis (no SUT/Measurement/gold/prediction changes; no LLM adjudication; ROUT-026::forbidden:01 carried as PENDING_LLM_ADJUDICATION)
Upstream: Wave-2 measurement lineage (MEASUREMENT_V3_REMEASURE_WAVE_2_RESIDUAL_ADJUDICATION_REQUIRED) and Wave-2 SUT (FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT), pinned in input-integrity.json (7/7 OK).

## Headline findings
- 8 P0 Wave1->Wave2 critical regressions: 0 real product safety regressions; 8/8 SCORER_LAG_OR_CONTRACT_SENSITIVITY. First-party counterfactual replay with the frozen scorer reproduces all 8 measured verdicts; trigger is the unconditional R3 PREMATURE_ABSENCE rule on no_route_asserted, while prose route guidance and safety fields are preserved.
- ROUT-026 and ROUT-088 deep dives: both SCORER_SENSITIVITY; no under-triage proven.
- ROUT-091 (P2): lexical certainty-marker sensitivity on legitimate new content.
- Route PASS 0/108: funnel R0=89 (no structured routes), R1=19 (junk fragment labels), R2-R10=0 reached. Dominant bottleneck: route-proposition construction in the SUT planner.
- RC-08 PARTIALLY_EFFECTIVE; RC-10 PARTIALLY_EFFECTIVE; RC-04 STILL_REQUIRED (sequenced); RC-06 STILL_REQUIRED.
- Wave-3 recommendation: WAVE3_ROUTE_SEMANTICS_FIRST (primary: structured route-proposition construction with evidence binding; secondary: renderer dedup). Fresh holdout: NOT_READY_FOR_FRESH_HOLDOUT.
- Measurement-sensitivity findings (R3 rule, certainty markers, paraphrase matching) documented for separate owner authorization; Measurement V3 untouched.

## File map
See final-report.md for the 48-item closure report. Machine-readable artifacts: input-integrity.json, p0-regression-inventory.json, safety-regression-diagnosis.json, routing-failure-stage-classification.json, routing-funnel-v2.json, measurement-sensitivity-findings.json, wave3-repair-candidates.json.
