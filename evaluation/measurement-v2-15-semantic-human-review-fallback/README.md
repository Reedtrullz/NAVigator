# V2.15 — Generic Semantic Human-Review Fallback

Task: NAV-EXPLORE-MEASUREMENT-V2_15-SEMANTIC-HUMAN-REVIEW-FALLBACK
(AFK campaign Stage 2F, entered after terminal V2_13_NO_FORBIDDEN_ROUTE_JUDGE_QUALIFIES).

Generic human-review lane for all four semantic dimensions
(critical_condition, forbidden_claim, route_correctness, required_uncertainty).
Reuses frozen contracts only: v1-4 (critical/forbidden/route) and v2-7e (uncertainty).
Mechanical final derivation via frozen judge_core_v2_13.derive_final.
Zero model calls. No new semantic meaning. No product runtime changes.

## Components

- review_lane_semantic_v2_15.py — the generic lane (packet creation, routing,
  dual-blind ingestion, adjudication, fail-closed states, provenance stream).
- gen_workflow_fixtures_v2_15.py / workflow-test-fixtures.json — 60 dev fixtures.
- run_workflow_tests_v2_15.py / workflow-test-results.json — 60/60 PASS.
- gen_fresh_workflow_fixtures_v2_15.py / fresh-workflow-fixtures.json — 120 fresh
  fixtures (30 per dimension) + 8 fail-closed probes.
- run_fresh_workflow_v2_15.py / fresh-workflow-results.json — all gates PASS,
  deterministic rerun stable.
- run_audits_v2_15.py — leakage, provenance, and process audits (all PASS).
- v2-15-manifest.json + hashes.txt — frozen artifact hashes.

## Terminal status

SEMANTIC_HUMAN_REVIEW_FALLBACK_READY
