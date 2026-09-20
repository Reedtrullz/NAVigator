# Post-Wave-1 Residual Failure Analysis V1

Task: NAV-EXPLORE-FULL-SUT-POST-WAVE1-RESIDUAL-FAILURE-ANALYSIS-V1

Read-only diagnosis over the frozen Wave-1 measurement (`MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE`). No SUT, gold, measurement, or prediction changes. No reruns. No LLM semantic calls. All conclusions recomputed from disk by `build_analysis.py`.

## Key findings

- Frozen Wave-1 state: 600 criteria = 290 PASS / 244 FAIL / 18 UNRESOLVED / 36 DEGRADED / 12 N/A (denominator 588; hard-fail 0.4150, non-pass 0.5068). Authority: 508 DETERMINISTIC + 88 LLM_REVIEWED + 4 LLM_ADJUDICATED. Delta vs old baseline: 8 improved, 0 regressed.
- Residuals: 298 criteria across all 120 cases, re-clustered into 7 fresh families (PW1-R1..R7); old F1-F8 labels not reused.
- Dominant mechanism: route-target selection absent (PW1-R1, 108 criteria, 0/108 route PASS; 88 empty + 8 junk + 12 KB-fragment routes).
- Retrieval contamination (PW1-R4): 104/120 answers carry 2+ unscoped national blocks (645 total), 75/120 claims and 2/120 routes polluted; all 6 residual forbidden-claim failures are contamination-shaped.
- Safety: under-triage 0; level correct 19/20; residual is category-vocabulary collapse (19 mismatches, over-triage dominant).
- Critical FAILs: 69 PREMATURE_ABSENCE (downstream shadow of route/retrieval emptiness), 19 safety mismatches, 3 RC-01 provenance rows (attachment defect), 1 other.
- Repair candidates RC-07..RC-12 proposed (proposals only). Priority: RC-08 retrieval scoping, RC-10 evidence attachment, RC-11 safety vocabulary, then RC-07 route-target selection; RC-09 and RC-12 deferred as downstream shadows.
- Fresh holdout: NOT_READY_FOR_FRESH_HOLDOUT.

## Deliverables

| File | Content |
|---|---|
| TASK-LOCK.json | Task lock and hard constraints |
| build_analysis.py | Recomputation script (inventory, funnel, contamination, families) |
| input-integrity.json | Pin verification, authority mix, state counts, delta |
| wave1-residual-inventory.json | Per-criterion residual inventory (298 rows) |
| residual-failure-families.json | PW1-R1..R7 families with observed-vs-hypothesis split |
| routing-failure-classification.json | A/B classification of 108 route criteria |
| routing-funnel.json | 120 -> 108 -> 20 -> 12 -> 0 route funnel |
| rc01-postmortem.md | RC-01 CLOSED (3 residual rows are evidence-attachment defect) |
| rc02-postmortem.md | RC-02 PARTIALLY_EFFECTIVE (under-triage 0; 19 category mismatches) |
| rc03-postmortem.md | RC-03A PARTIALLY_EFFECTIVE; RC-03B STILL_REQUIRED |
| rc04-assessment.md | Do not recommend yet; downstream of routing/retrieval |
| rc05-assessment.md | ~60% standalone attachment defect (-> RC-10), 40% downstream |
| rc06-assessment.md | Renderer mostly PRESENTATION_ONLY; retrieval scoping first |
| forbidden-claim-analysis.md | 6/6 contamination; ROUT-042 LABEL_SENSITIVITY_KNOWN |
| retrieval-contamination-analysis.md | Cross-layer contamination counts and mechanism |
| next-repair-candidates.json | RC-07..RC-12 with tests, risks, dependencies |
| repair-dependency-graph.md | RC-08 -> RC-07 -> (RC-09, RC-12 re-assessment) |
| repair-priority.md | Ranked Wave-2 triage |
| fresh-holdout-readiness.md | NOT_READY_FOR_FRESH_HOLDOUT |
| hashes.txt | SHA-256 of deliverables |
| final-report.md | 48-point terminal report |

## Terminal status

FULL_SUT_POST_WAVE1_RESIDUAL_FAILURE_ANALYSIS_COMPLETE
