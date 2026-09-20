# Measurement V2.12 - Uncertainty Human-Review Lane

Terminal status: UNCERTAINTY_HUMAN_REVIEW_LANE_READY

Automated semantic-uncertainty verdicts are removed from the measurement system.
Uncertainty judgments route to a human-review lane; the final verdict is derived
mechanically from human intermediate observations via the frozen V2.7E
derivation module (uncertainty_derivation_v2_7e.py, imported unmodified,
including the UNC-A1 and UNC-A2 repairs). No model calls anywhere in this
lineage.

Entry points:

- final-report.md - stage closure report
- v2-12-contract-pins.json - frozen contract pins (SHA-256)
- TASK-LOCK.json - frozen task lock with terminal evidence
- review_lane_uncertainty_v2_12.py - the lane runtime (stdlib-only)

Verification artifacts:

- workflow-test-results.json - 40/40 workflow fixtures
- burned-replay-results.json - 92/92 burned replay (V2.7E Set A 32/32,
  V2.8 uncertainty subset 60/60; pre-registered normalized span rule for V2.8
  historical gold spans, documented in the replay script docstring)
- fresh-workflow-results.json - 60 fresh fixtures, all hard gates PASS
  (routing, packet validity, ingestion, derivation, provenance completeness,
  determinism, fail-closed probes)
- leakage-audit.json - 0 leakage findings; runtime guard rejects all forbidden keys
- provenance-audit.json - provenance complete on all 179 resolved cases
- process-audit.json - frozen inputs unchanged; fresh rerun idempotent

State machine: HUMAN_REVIEW_REQUIRED -> HUMAN_REVIEW_PENDING ->
(HUMAN_REVIEW_RESOLVED | HUMAN_REVIEW_INVALID | HUMAN_REVIEW_DISAGREEMENT ->
adjudication with model outputs hidden -> RESOLVED). Fail-closed: no final
verdict without valid human review; duplicate reviews rejected; adjudicator
must have model_outputs_visible_to_adjudicator = false.

Historical lineages (V2.6, V2.7E, V2.8, V2.10, V2.11) are preserved unchanged.
Campaign continuation (Stage 2D forbidden/route specialist screening) is
pre-authorized by the AFK campaign contract and does not require new owner
authorization.

