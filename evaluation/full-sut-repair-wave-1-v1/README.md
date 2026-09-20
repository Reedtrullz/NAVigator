# Full SUT Repair Wave 1 - RC-01 + RC-02 + RC-03

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1
Status: FULL_SUT_REPAIR_WAVE_1_READY_FOR_REMEASUREMENT (terminal)
Candidate: v2 (attempt 2 of 2), frozen; runtime wave1-rc01+rc02+rc03-v2

This lineage repairs the three highest-priority root causes from the
burned-baseline failure analysis: RC-01 input/schema compatibility,
RC-02 safety/triage granularity, and RC-03 structured routes and
provenance. It is product-mechanism work only: no Measurement V3
scoring, no gold changes, no fresh holdout, no deployment.

## Key facts

- Candidate v1 replay failed the RC-01 mechanism gate: 2 of 120 cases
  (SAF-007, SAF-011) hard-failed on scalar string profile.context.
- Candidate v2 adds a generalized scalar-context wrap in
  normalize_input(); official v2 replay: 120/120 SUCCESS, 0 crashes,
  0 input hard failures, 0 terminal failures.
- Mechanism gates: RC-01 0 known failures remain; RC-02 no blanket
  collapse (16/3/101 priority distribution, 12 distinct classes);
  RC-03 rendered-vs-structured 0 violations, provenance 0 missing.
- Determinism: independent rerun byte-identical 120/120 (SHA-256).
- Full test suite: 170 passed, 0 failed.
- RC-04/05/06 remain open (see remaining-rc04-06-findings.json).

## Documents

- TASK-LOCK.json - frozen task contract
- input-integrity.json - upstream frozen-input verification
- gate0-report.json - build/import/control-character gate
- rc01-root-cause.md / rc01-tests.json
- rc02-root-cause.md / rc02-tests.json
- rc03-root-cause.md / rc03-tests.json / route-dataflow-before.md
- source-change-summary.md - per-RC source deltas
- regression-results.json - full-suite result
- repaired-sut-manifest.json / hashes.txt - frozen candidate manifest
- structural-replay-results.json - both attempts, v2 official
- structural-replay-diagnostics.json - gold-blind diagnostics + gates
- remaining-rc04-06-findings.json - explicitly not implemented here
- final-report.md - 48-point close-out

Replay runs are preserved as evidence: runs/structural-120-replay/ (v1,
superseded) and runs/structural-120-replay-v2/ (official). The
determinism rerun lives in runs/determinism-check-v2/.

Hard stop after this task: re-measurement (Measurement V3) of the
frozen v2 candidate requires a separate owner authorization.
