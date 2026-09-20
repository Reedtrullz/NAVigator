# Source Integrity Report (Gate 0)

Task: NAV-EXPLORE-RC3_2-BOUNDARY-AWARE-RELATION-RECOVERY
Date: 2026-09-07

## Restored authoritative engine

- Path: evaluation/semantic-judge/rc3-1-proof-semantics/rc3_1_engine/engine.py
- SHA-256: 4bd2845fac3535fba22ab3e242b51e80f0d2abbbb5d57a3123b7207b2383ea7d
- Matches TASK-LOCK authoritative_engine_sha256: YES
- Failed bounded-pass implementation excluded: YES (historical artifact only)

## Sealed validation

- Path: evaluation/semantic-judge/rc3-1-proof-semantics/corpus/validation-answer-key.sealed
- SHA-256: 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159
- Accessed/decrypted/executed: NO

## Compile / import / scan gates

- python3 -m py_compile engine.py: PASS
- Import smoke test (rc3_1_engine.engine + boundary): PASS (Python 3.14.6)
- C0 control-character scan over engine.py, boundary.py, proposition.py,
  decomposition.py: 0 hits
- Functional smoke: evaluate_atom ENTAILS/R25-coverage on aligned pair

## Environment

- Python: 3.14.6
- Disk free: 76 Gi (above 30 Gi guard)

All harnesses import the engine via
sys.path -> evaluation/semantic-judge/rc3-1-proof-semantics + rc3_1_engine
package import (same pattern as the RC3.1 harness); provenance hashes are
recomputed at run time, not copied.
