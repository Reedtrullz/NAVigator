# Measurement V2.6 — M2 Human-Review Lane

Terminal status: V2_6_M2_HUMAN_REVIEW_LANE_READY

Automated M2 critical-condition verdicts are removed from the measurement system.
M2 judgments route to a human-review lane; the final label is derived mechanically
from human intermediate observations via the frozen V2.5 81-row derivation table.
No model calls anywhere in this lineage.

Entry points:

- final-report.md — 50-item closure report
- m2-human-review-lane-v2-6-manifest.json — frozen manifest (28 files, SHA-256)
- ADR-M2-HUMAN-REVIEW.md and architecture-decision.md — why the lane exists
- review_lane_v2_6.py — the lane runtime (stdlib-only)

Verification artifacts:

- workflow-test-results.json — 40/40 workflow fixtures (spec sections 22-23)
- burned-v2-5-replay.json — 60/60 V2.5 replay (spec section 24)
- fresh-workflow-results.json — 60 fresh fixtures, all hard gates PASS (spec sections 26-27)
- leakage-audit.json — 0 leakage findings; runtime guard verified
- provenance-audit.json — provenance complete on all resolved cases

Contract layer: V2.5 semantics frozen and pinned in m2-contract-pins.json;
lane schemas in human-review-*.schema.json and adjudication.schema.json;
status machine in workflow-status-contract.json.

Historical lineages (V2.4 draft, V2.5) are preserved unchanged. Next stage
(V2.7 non-M2 judge screening) requires separate owner authorization.
