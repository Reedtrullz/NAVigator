# NAV-EXPLORE-JUDGE-CONTRACT-V2_7D-SHARED-MISS-DIAGNOSIS

Diagnosis-only lineage after V2_7_NO_NON_M2_JUDGE_QUALIFIES. No model calls, no contract repair, no historical writes.

Terminal status: V2_7D_CONTRACT_REPAIR_REQUIRED

Key findings:
- Uncertainty family human-unstable (0.75): the frozen contract and judge-core table conflict on CONTRADICTORY_LIMITATION (UNC-A1) and UNCLEAR_PROSE is undefined (UNC-A2).
- Route and forbidden families human-stable (1.00): the shared V2.7 misses were model bias, not contract failure.
- Historical retrospective: UNC-46/47 gold questionable, UNC-48/49 genuinely ambiguous, ROUTE-22/23 and FORB-13 model errors.

Files:
- TASK-LOCK.json - task lock and terminal status
- baseline-integrity.json - 13 verified SHA pins
- burned-data-registry.json - V2.7 set remains burned
- preregistered-hypotheses.json - H1-H4 frozen before fresh data
- frozen-contract-trace.md - UNC-A1, UNC-A2, ROUTE-A1, ROUTE-A2, FORB-A1
- shared-miss-mechanism-analysis.md - mechanism trace per burned row
- gen_fixtures_v2_7d.py - fresh fixture generator
- diagnostic-fixtures.json, collision-audit.json, diagnostic-fixture-hashes.json - 90 fresh fixtures, 0 collisions
- annotation-pass1.json, annotation-pass2.json - two blind intra-annotator passes
- raw-agreement.json - frozen pre-adjudication numbers
- fixture-defect-registry.json - 0 defects, 9 genuine contract disagreements
- adjudication-results.json - UNRESOLVED stance on 9 boundary rows
- uncertainty-boundary-report.json, route-boundary-report.json, forbidden-boundary-report.json - family diagnoses
- historical-retrospective.json - burned retrospective
- final-report.md - full 36-item report
