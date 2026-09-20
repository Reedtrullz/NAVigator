# Full SUT Repair Wave 2 V1

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1

Terminal status: FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT

## What this lineage did

Repaired four generalized product defects identified by the post-Wave-1
residual failure analysis, within a strict 2-candidate attempt policy:

- RC-08: track-scoped retrieval + globally unique evidence ids across tracks
  (data/knowledge-index-v1.json, phase2/knowledge.py, phase2/pipeline.py,
  phase3/planner.py)
- RC-07: route-target semantic selection (CURRENT-first retrieval slot
  ordering, numeric-fragment rejection, consistent track binding)
- RC-10: per-route and per-claim evidence attachment
  (evidence.route_evidence / evidence.claim_evidence)
- RC-11: fine 12-class safety vocabulary at top level (collapsed 3-level
  value retained in nested safety.priority per frozen scorer contract)

## Key results

- Official gold-blind structural replay: 120/120 SUCCESS, 0 crashes,
  120/120 schema-valid (runs/structural-120-replay-v2/)
- Determinism: independent rerun 120/120 byte-identical
  (runs/determinism-check-v2/)
- Full test suite: 216/216 passed
- Route provenance: 20/20 route-bearing cases fully provenanced; 0 junk
  routes; 2 documented fragment-like labels (lexical ceiling)
- Claim provenance: 673/673 claims carry provenance
- Emergency trigger logic unchanged; no safety.py changes; no under-triage

## Candidate history

- Candidate v1: replay 99/120 SUCCESS; 21 fail-closed executions from a
  cross-track evidence_id collision (see rc08-candidate2-repair.md);
  superseded, replay preserved.
- Candidate v2 (FINAL): bounded global id-renumbering fix + regression test;
  official 120/120. Frozen at
  repaired-sut-manifest.json SHA-256
  8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e.

## Not done (out of scope, per TASK-LOCK)

No Measurement V3 run, no gold changes, no RC-09/RC-12, no broad RC-04 or
RC-06, no fresh holdout, no deployment. Historical predictions and
measurements untouched.

## Next bounded task (requires owner authorization)

NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2 against the frozen v2
candidate manifest above.

Start with final-report.md (57 spec items), then structural-replay-results.json
and structural-replay-diagnostics.json.
