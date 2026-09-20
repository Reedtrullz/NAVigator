# RC2 blind recertification set V2 - NAV-EXPLORE-RC2-BLIND-V2

Sealed double-annotated blind set for RC2 evaluator certification. RC2 has never been executed against these cases.

## Artifact map

| File | Purpose |
|---|---|
| blind-cases.json | Public, label-free CORE cases (160). SHA-256 0c62f093a71f1b0f719284f8b2d3d47f4155f2fbb700356a9b7865b4e8e0afbf |
| blind-cases.schema.json | Draft-07 schema for the public case shape |
| answer-key.sealed | AES-256-GCM sealed answer key covering all 160 CORE cases (labels, atoms, required_inference, criticality, source_spans, rationale, adjudication metadata). Associated data binds the blind-cases SHA |
| blind-manifest.json | Machine-readable construction manifest incl. distributions, pool aggregates, agreement, deviations |
| selection.json | Case-ID selection (core/reserve) plus counts. No per-case labels |
| annotation-input-pass2.json | Label-free annotation input bundle (276 cases; RC2B-0277 was annotated single-pass post-wave) |
| candidates-a1/a2/b1/c/d/e.json | Candidate waves, 277 total, label-free post-scrub (spec 44) |
| novelty-checker.py, validation/ | Deterministic construction tooling and per-wave novelty/fidelity outputs |
| novelty-report.md | Novelty gate results (277/277 retained, max similarity 0.5385) |
| source-fidelity-report.md | Verbatim-excerpt fidelity results (277/277, 0 failures; 303/303 span re-check) |
| annotation-summary.md | Two-pass agreement aggregates and adjudication outcomes |
| quota-report.md | Pool quota verification (ALL_QUOTAS_PASS) and CORE-level deviation notes |
| certification-metrics.md | Pre-registered gates and thresholds, fixed before any RC2 run |
| future-certification-protocol.md | Two-phase prediction-freeze firewall incl. key-handling rules |
| final-report.md | SLUTTRAPPORT (aggregates 1-62) |
| rc2-hashes-before.txt / rc2-hashes-after.txt | RC2 engine hashes verified before and after construction (ALL_OK) |
| TASK-LOCK.json | Task lock, status COMPLETED |
| .pre-scrub-backup/ | Byte-exact pre-scrub snapshot of candidate files kept for provenance; contains no recovered plaintext label files (candidates were scrubbed in place pre-backup) |

Plaintext label artifacts (annotation pass-2 output, adjudication files, label-bearing authoring specs and recovery extracts, label-era tooling quota_check.py and backfill_flags.py) were deleted after the seal per spec 44. Aggregate counts in reports and the manifest are permitted.

## Certification firewall

Phase 1 (agent without the key): verify RC2 hashes (rc2-hashes-before.txt from evaluation/semantic-judge/), run RC2 on blind-cases.json CORE only, freeze and hash predictions, stop.

Phase 2 (only after prediction freeze): the user supplies BLIND_RC2_V2_KEY in a separate message. The key must never appear in any prompt, log, report, or file. No copy of the key exists on disk or in any log from the construction task.

## Key handling rules for the user

The key was returned once in the construction task's final message as BLIND_RC2_V2_KEY. Store it outside this project. Never paste it into the certification prompt itself; provide it only as a separate message after predictions are frozen.
