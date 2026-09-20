# Measurement V3 Remeasure Repair Wave 1

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1

Read-only remeasurement of the frozen Wave-1 v2 candidate (RC-01/02/03 repairs) with the frozen Measurement V3 stack, followed by a frozen before/after comparison against the old burned baseline.

## Terminal status

MEASUREMENT_V3_REMEASURE_WAVE_1_RESIDUAL_ADJUDICATION_REQUIRED

596/600 criteria have authoritative outcomes. 4 residual forbidden-claim criteria are frozen PENDING and require human adjudication in a separate owner-authorized lineage. Residuals must not be rerun; this partial terminal is valid per spec section 37.

## Artifact map

### Inputs and integrity

- TASK-LOCK.json - task scope, hard constraints, upstream pins
- input-integrity.json - SHA-256 recompute of all upstream pins (PASS)

### Deterministic measurement

- measurement-routing.json / measurement-routing-results.json - deterministic scoring routing
- deterministic-results.json / deterministic-scores.json - 508 deterministic criterion results
- measurement-determinism.json - 2-run determinism check (semantic identical, PASS)
- partial-aggregate-metrics.json - pre-review coverage snapshot
- product-diagnostics.json - read-only diagnostics on frozen predictions (routes, claims, provenance, repeated blocks)

### Semantic review (blind, dual-pass, Astra LOW)

- semantic-review-packets.jsonl / semantic-review-packet-manifest.json - 92 frozen packets
- semantic-review-leakage-audit.json / semantic-reviewability-audit.json - leakage and reviewability gates (both PASS)
- astra-config.json - frozen model/reasoning/transport policy (gpt-6-astra, LOW only)
- astra-pass-a.jsonl / astra-pass-b.jsonl - 92+92 blind passes
- primary-review-validation.json / primary-consensus.json - 88 consensus, 4 residual
- residual-inputs.json / residual-leakage-audit.json - blind residual inputs (leakage PASS)
- adjudication-pass-a.jsonl / adjudication-pass-b.jsonl - 4+4 LOW adjudication passes
- adjudication-validation.json / residual-consensus.json - 0 consensus, 4 HUMAN_ADJUDICATION_REQUIRED

### Freeze and derivation

- primary-review-freeze-manifest.json - frozen before residual adjudication
- semantic-review-freeze-manifest.json - observations frozen before gold derivation
- derived-measurement-results.json - mechanical derivation via frozen judge_core_v2_13
- wave1-combined-measurement-results.json - authoritative 600-row result
- wave1-aggregate-metrics.json - authority mix and coverage
- wave1-measurement-freeze-manifest.json - terminal measurement freeze
- hashes.txt - 23 pins, all verified

### Comparison (created after the measurement freeze, by design)

- baseline-transition-matrix.json - 600-row transition matrix
- wave1-effect-analysis.json - effect summary (8 improvements, 0 regressions, 13 fail-closed lateral moves)
- regression-inventory.json - regression inventory (0) with mechanism notes
- safety-comparison.md - RC-01/RC-02/uncertainty/critical-condition comparison
- routing-comparison.md - RC-03 route emission vs verdict comparison
- remaining-rc04-06-assessment.md - RC-04 descoped; RC-05/RC-06 still indicated
- post-freeze-analysis-hashes.txt - SHA-256 pins for the 6 post-freeze analysis artifacts

### Closure

- final-report.md - 66-item spec report

## Ordering note

The measurement freeze (wave1-measurement-freeze-manifest.json, hashes.txt) was completed before the old-baseline comparison. The comparison and analysis artifacts were then written read-only against frozen data and pinned in post-freeze-analysis-hashes.txt. This ordering is intentional: analysis could not influence scoring.

## Interpretation boundary

BURNED_DEV_BASELINE_ONLY. Everything in this directory is measurement-system evidence for the burned dev baseline only. It is not certification, production readiness, or generalization evidence. No fresh holdout was run and no tuning was performed.
