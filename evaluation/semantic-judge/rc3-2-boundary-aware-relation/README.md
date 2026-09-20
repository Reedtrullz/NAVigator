# RC3.2 Boundary-Aware Relation Recovery

Task ID: NAV-EXPLORE-RC3_2-BOUNDARY-AWARE-RELATION-RECOVERY
Status: COMPLETED - READINESS: BOUNDARY_AWARE_RELATION_NOT_READY

Enrich semantic dimension evidence without weakening the frozen
auto-support safety gate, then let the relation layer consume the rich
evidence instead of the collapsed 3-state gate.

## Outcome in one paragraph

The DIMENSION_EVIDENCE_LAYER_V1 implementation pass plus one bounded
bugfix pass left all safety gates intact (false auto 0, unsound proofs
0, critical false-CONTRADICTS 0) and fixed the targeted over-firing
classes (exception-bounded conflicts, direction-unknown modality), but
the primary relation gate reached only 0.514 accuracy against the 0.95
target, concentrated in 3-state gate-collapse and numeric-coverage
cases this task was not authorized to change. The sealed 60-case
validation remains sealed. See final-report.md.

## Key files

- final-report.md - full SLUTTRAPPORT and readiness rationale
- implementation-report.md - what changed and why, within budget
- regression-report.md - legacy battery results and the documented
  baseline-results.json overwrite incident (restored, headline-only)
- dimension-evidence-contract-v1.md - frozen contract (section 6 is
  the relation-consumption authority)
- architecture-results.json / dimension-results.json /
  boundary-regression-post.json - post-implementation evidence
- baseline-results.json - pre-implementation baseline (152-case
  provenance, refreshed this task)
- proof-safety-audit.json - entailment grounding/gate audit

## Constraints honored

Frozen 3-state gate unchanged (0/677 differential diffs); sealed
validation never opened; no new blind set; no case-ID rules in runtime
(id_guard 0); 0 subagents (GPT-5.6-Luna default policy, GPT-5.5
forbidden); one implementation pass + one bounded bugfix pass, then
stopped.
