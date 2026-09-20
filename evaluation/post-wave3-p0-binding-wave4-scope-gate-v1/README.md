# Post-Wave-3 P0 + RC04/Binding Wave-4 Scope Gate V1

Task ID: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY
Starting state: MEASUREMENT_V3_REMEASURE_WAVE_3_COMPLETE (input integrity PASS, all pins verified from disk).
Type: READ-ONLY DIAGNOSIS. No SUT/measurement/gold/prediction changes, no semantic LLM calls, no fresh holdout, no Wave-4 implementation.

## Purpose
1. Audit the 5 Wave2->Wave3 P0 regressions independently (are any real product safety regressions?).
2. Diagnose why label-to-evidence binding is 0/24 and recompute why route PASS remains 0/108.
3. Reconcile RC-04 terminology and assign the binding defect its own repair ID.
4. Recommend exactly one minimal Wave-4 scope for explicit owner authorization.

## Headline results
- 0 REAL_PRODUCT_SAFETY_REGRESSION: 4x AUTHORITY_TRANSITION_CONFOUND (ROUT-022/031/033/047), 1x PRODUCT_REPRESENTATION_CHANGE (ROUT-069), ROUT-030 = NOT_A_REGRESSION (lateral FAIL->FAIL).
- Binding EXISTS at route-object level (39/39 entries with evidence_refs + provenance_refs); the defect is serialization join shape: routes serialize labels-only, evidence.route_evidence is keyed by R-codes, scorer sees no join key. B5 = 23, B4 = 16 (non-service labels), all other B-classes = 0.
- A perfect binding join flips no verdicts: labels vs proposition-shaped gold = 0 exact matches; scorer has no structured route-evaluation path. Route PASS 0/108 is dominated by R0_NO_STRUCTURED_ROUTE (84/108).
- RC-04 terminology: historical RC-04 = uncertainty-depth grading (intact); binding defect = NEW ID W4-RC-A.
- Recommended Wave-4 scope: WAVE4_ROUTE_TARGET_PLUS_BINDING (W4-RC-A only). Fresh holdout: NOT_READY_FOR_FRESH_HOLDOUT.

## Deliverables
- TASK-LOCK.json - task scope, invariants, terminal status
- input-integrity.json - SHA-verified frozen inputs
- p0-regression-diagnosis.json - independent P0 audit and classifications
- authority-transition-confounds.json - W2 Astra lane vs W3 deterministic reconstruction
- rout-069-analysis.md / rout-030-analysis.md - single-case audits
- route-evidence-binding-dataflow.md - stage-by-stage binding trace + gold-shape finding
- route-binding-classification.json - B-class taxonomy, 39 entries
- route-binding-support-matrix.json - PROVENANCE_PRESENT vs EVIDENCE_SUPPORTS_ROUTE_PROPOSITION
- route-failure-stage-classification.json - frozen 120-row base + binding recompute
- rc04-terminology-reconciliation.md - option B/C resolution, W4-RC-A assigned
- epistemic-binding-consequences.md - binding causes 0 epistemic failures; historical RC-04 independent
- w3-res-binding-assessment.md - W3-RES-01..05 classified
- measurement-sensitivity-findings.json - MS-01..06, 0 product changes justified
- wave4-repair-candidates.json - W4-RC-A/B/C/D
- wave4-dependency-graph.md - A -> B; C independent; D folded into A
- wave4-scope-recommendation.md - exactly one scope
- fresh-holdout-readiness.md - NOT_READY verdict
- hashes.txt - SHA-256 of all deliverables
- final-report.md - all 57 required report items
