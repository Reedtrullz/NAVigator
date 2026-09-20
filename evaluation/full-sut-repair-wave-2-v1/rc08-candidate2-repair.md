# Candidate-2 Repair: Cross-Track Evidence-ID Collision

## Failure observed (candidate 1, official replay)

Candidate-1 structural replay (runs/structural-120-replay-v1/) finished with
99/120 SUCCESS and 21/120 EXECUTION_FAILED, all 21 with the same fail-closed
mechanism: "output consistency failed: verified claim value missing from
answer". The runner's harness-level error count was 0; the failures are
prediction-level status failures, correctly surfaced fail-closed.

## Root cause (single cause, all 21)

Per-domain retrieval in runtime/sut/phase2/knowledge.py restarts evidence
numbering (E-D001...) inside each track. Multi-track queries therefore
produced duplicate evidence_ids across tracks (e.g. a ROUT case retrieving
both mental_health and education tracks yielded E-D003/E-D004/E-D005 twice).
phase3/planner.py deduplicates INFO blocks by evidence_id, so the second
track's records never rendered into the answer. The s11 claim verification in
phase3/finalize.py then correctly refused to emit verified claims whose
values were absent from the rendered answer and failed closed.

This is a genuine id-uniqueness defect inside the RC-08 track-scoping scope:
track scoping introduced per-track record collections without a global
identity guarantee.

## Bounded fix (candidate 2)

runtime/sut/phase2/pipeline.py, end of s4_knowledge_retrieval: after the
combined record list is assembled across tracks, record_id and evidence_id
are renumbered globally over that list. Source-type prefixes are preserved
(K-R... retained for route-candidate records, K-D... for knowledge-doc
records), so downstream consumers see stable, collision-free identities.
No other stage, schema, scoring, or behavior was touched.

New regression test: runtime/sut/phase2/test_pipeline_ids.py
(two-track retrieval asserts 10 records with unique rids and unique eids).

## Verification

- Full suite: python3 -m pytest runtime/sut/ -q -> 216/216 passed
  (was 215 before the new id-uniqueness test).
- Manifest regenerated: candidate_version v2, frozen_candidate_attempts 2,
  pipeline.py sha256 73cd0350625a0424d3e20723d915270b0b72f8cacd8e655303ebce598e027429.
- Official replay: runs/structural-120-replay-v2/ -> 120/120 SUCCESS,
  0 crashes, 0 input hard failures, 120 schema-valid outputs.
- Determinism: independent full rerun into runs/determinism-check-v2/;
  120/120 prediction files byte-identical by SHA-256.

## Candidate policy

Candidate 2 was the final allowed attempt (max 2, TASK-LOCK). No further
runtime changes are permitted in this task after this repair.
