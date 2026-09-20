# RC1 blind recertification set - NAV-EXPLORE-RC1-BLIND-V1

Sealed double-annotated blind set for RC1 evaluator certification. RC1 has never been executed against these cases.

## Artifact map

| File | Purpose |
|---|---|
| blind-cases.json | Public, label-free cases: 120 CORE + 67 reserve. SHA-256 a3a4dd60bc8662dd77581696809be6f68e93aeddf136ebad6f828cd4b52e7a39 |
| answer-key.sealed | AES-256-GCM sealed answer key covering all 187 cases. Associated data: SHA-256 of exact blind-cases.json bytes |
| selection.json | Case-ID selection (core/reserve) plus aggregate class counts for the core. No per-case labels |
| annotation-input.json / annotation-input-w4.json | Label-free annotation input bundles (187 cases) |
| candidates/ | Candidate waves (193 generated, 187 retained) |
| validation/ | Novelty checker outputs (w1-w4) and source-fidelity outputs (w1-w4), plus checker scripts |
| author_wave3.py / author_wave4.py / novelty-checker.py / validation/source_fidelity.py | Deterministic construction tooling. No label data |
| novelty-report.md | Novelty gate results incl. wave 4 |
| source-fidelity-report.md | Verbatim-excerpt fidelity results (0 failures across 193 checks) |
| annotation-summary.md | Double-annotation agreement aggregates and dispute count |
| certification-metrics.md | Pre-registered gates and thresholds (fixed before RC1 runs) |
| future-certification-protocol.md | Two-phase prediction-freeze firewall |
| blind-manifest.json | Machine-readable construction manifest |

Plaintext label artifacts (annotation pass files, selector with adjudication overrides, compiled bytecode) were deleted after the seal.

## Certification firewall

Phase 1 (agent without the key): verify RC1 hashes, run RC1 on blind-cases.json, freeze and hash predictions, stop.

Phase 2 (only after prediction freeze): the user supplies the key in a separate message. The agent must ask for the key as a separate message and must NOT include the key in any prompt, log, report, or file.

## Key handling rules for the user

The key was returned once in the construction task's final message as BLIND_RC1_KEY. Store it outside this project. Never paste BLIND_RC1_KEY into the certification prompt itself; provide it only as a separate message after predictions are frozen. No copy of the key exists on disk or in any log from this task.
