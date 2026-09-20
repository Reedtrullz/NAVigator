# RC2 blind recertification - Phase 1 (V4 prediction run)

Task NAV-EXPLORE-RC2-BLIND-V4-PHASE1. NAV-EXPLORE-EVALUATOR-RC2 (frozen)
was executed exactly as frozen against the 160 CORE cases of
NAV-EXPLORE-RC2-BLIND-V4. Predictions are frozen before any answer-key
access; the blind key was never available in this session.

## Files

| File | Purpose |
|---|---|
| TASK-LOCK.json | Phase lock: PREDICTION_BEFORE_KEY, answer_key_access=false |
| run_blind_phase1_v4.py | Deterministic driver; calls the frozen RC2 pipeline (rc2 engine -> hybrid auto_gate -> frozen reviewer v1.1 on gated cases -> RC2-FUSION-V1 fuse). Multi-source cases are joined into one source string (documented adapter, no runtime change) |
| RC2-V4-predictions.json | Authoritative prediction artifact (read-only): 160 outcomes incl. full raw intermediates (engine atoms, gate reason, reviewer packet output, fusion route) |
| prediction-freeze.json | SHA-256 freeze manifest (read-only) |
| phase1-run-report.md | Run log and integrity verification |
| phase1-final-report.md | SLUTTRAPPORT (prediction/integrity only) |
| validation/ | pre-run-hashes.json (19-file immutable snapshot), run-console.log |

## Firewall

No answer-key decryption, no construction-audit decryption, no key
search, no scoring, no tuning, no runtime changes in this phase. The
answer key was never accessed and the blind key was never available.
blind-cases.json is CORE-only (160 entries); RESERVE_EXECUTED = 0.

Phase 2 requires the user to send BLIND_RC2_V4_KEY in a separate
continuation after this freeze; the key must never be pasted into a
certification prompt.
