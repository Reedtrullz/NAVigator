# FULL SUT Repair Wave 3 V1 - Route Proposition Construction

Task ID: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1
Status: FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT (closed 2026-09-16T18:57:59Z)

## Scope

Primary repair: W3-RC-A (route proposition construction).
Starting state: POST_WAVE2_P0_ROUTING_WAVE3_SCOPE_GATE_COMPLETE with Wave-2
candidate frozen as FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT.

Authorized: structured service/route proposition construction plus mechanically
necessary wiring. Forbidden: Measurement V3 changes, scoring, safety policy
changes, RC-04/RC-06 repairs, gold changes, fresh holdout, deployment,
benchmark tuning, case IDs or corpus strings in runtime, semantic review calls.

## Frozen pins

- Wave-2 manifest: evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json
  (sha256 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e; all 24
  components verified against manifest hashes at task start)
- Wave-2 official prediction manifests (routing/safety/discovery_adversarial),
  see TASK-LOCK.json frozen_pins
- Scope-gate lineage: evaluation/post-wave2-p0-routing-wave3-scope-gate-v1/ (hashes.txt)
- Repaired gold: evaluation/dev-corpus-v1-1-repair/cases/ (SHA-pinned)
- Frozen candidate spec: wave3-repair-candidates.json in the scope-gate lineage

## Plan

1. Gate 0 integrity and import smoke
2. Route proposition dataflow trace and root-cause confirmation
3. W3-RC-A implementation (routes -> planner -> render -> finalize wiring)
4. Route proposition test matrix plus full regression and evaluator separation
5. Freeze candidate (max 2 attempts), one gold-blind 120-case structural replay
6. Gold-blind diagnostics and route funnel, final report, terminal status

Terminal states: FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT |
FULL_SUT_REPAIR_WAVE_3_BLOCKED | FULL_SUT_REPAIR_WAVE_3_INVALID.

## Close-out

Candidate W3-RC-A v1 frozen (1 of max 2 attempts): manifest sha256
6c1f7d4b4b52eeabc16a13e0c34d9cdd332a6acd532cd33ddb796660fd2be14f; runtime change
limited to runtime/sut/phase2/routes.py (29b0bd44...d7fa). Full suite 242/242.
Official gold-blind structural replay 120/120 SUCCESS, gates PASS, determinism
120/120 byte-identical. Terminal report: final-report.md (sha256
c9506c33be61b4a57246ea66134e677e12a5537f49cb31c9c8a5f0f4f79e0465).
Measurement V3 remeasure is a separate owner-authorized task.
