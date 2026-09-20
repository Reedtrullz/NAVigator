# Source Integrity Report - RC3.1 Auto-Support Boundary Repair

Task: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR
Date: 2026-09-05

## Historical integrity (SHA-256, first 12 chars shown)

All artifacts verified against session-4 record before any code change. No file under the protected paths was modified.

| Artifact | SHA-256 prefix | Result |
|---|---|---|
| rc3-generalization-holdout/run/RC3G-predictions.json | 6923c66c8aba | MATCH |
| rc3-generalization-holdout/run/scoring/official-generalization-score.json | 384e1a217980 | MATCH |
| rc3-generalization-holdout/generalization-cases.json | 3f22c19b9f48 | MATCH |
| rc3-generalization-holdout/answer-key.sealed | e25b3ab81327 | MATCH |
| rc3-1-proof-semantics/corpus/train-cases.json | fb467faefb7a | MATCH |
| rc3-1-proof-semantics/corpus/validation-cases.json | 3e336d68fc17 | MATCH |
| rc3-1-proof-semantics/corpus/validation-answer-key.sealed | 15b13bb7006e | MATCH |
| rc3-1-proof-semantics/corpus/corpus-manifest.json | 111d0dc132d2 | MATCH |
| release-candidate/RC2/RC2-manifest.json | 1215f0d2978d | RECORDED |
| blind-recertification/RC2-V4-run/phase2/official-score.json | e47890d0f5bd | RECORDED |
| blind-recertification/RC2-V4-run/phase2/official-score-freeze.json | 5422c220eaf4 | RECORDED |

The RC2 official artifacts were hashed for provenance; their immutable status is unchanged and they were not opened for modification.

The sealed validation answer key was rehashed only. It was not decrypted, not inspected, and not executed against. No validation labels were accessed.

## Gate 0 - runtime source integrity

Runtime files:

- rc3_1_engine/engine.py (SHA-256 prefix e7a6aafd8065)
- rc3_1_engine/proposition.py (4e3b2d007e40)
- rc3_1_engine/decomposition.py (961dfc49d905)
- run_train.py, test_engine_probes.py

Checks:

- python3 -m py_compile on all runtime files: PASS
- Actual import of rc3_1_engine.engine from the target path: PASS
  (imported file: evaluation/semantic-judge/rc3-1-proof-semantics/rc3_1_engine/engine.py)
- Control-character scan (0x08 backspace, 0x00 NUL, unexpected C0): PASS, 0 hits

Every write in this task is followed by byte read-back, py_compile, import, hash, and control-char scan per spec section 4.

## Addendum - post-implementation state (2026-09-06)

The implementation and one bounded bugfix pass modified two runtime files. Final SHA-256:

- rc3_1_engine/boundary.py: 6ebc2429dcbadb98f4b541025cbaadbdb35e7f78cc73169a4cb186c4e25d215e
- rc3_1_engine/engine.py: c4bc71862febf51783e2e48550f899746f9a6d0cb00f03a84d084edcd8fdce37

Unchanged from Gate 0: proposition.py (4e3b2d007e40...), decomposition.py (961dfc49d905...).
modality-boundary-table.json was updated during the bugfix pass (final ffd198414890...,
see candidate-boundary/hashes.txt); boundary-metrics-v1.json and boundary-contract-v1.md
remain exactly as frozen before implementation.

All protected historical artifacts listed above were re-verified unchanged after the final
run. The validation seal was rehashed again on 2026-09-06 and still hashes to
15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159. py_compile, actual
engine import, and the control-character scan were re-run clean after every source change.
