# RC1 blind recertification - Phase 1 (prediction run)

Task NAV-EXPLORE-RC1-BLIND-RECERT-PHASE1. RC1 (NAV-EXPLORE-EVALUATOR-RC1,
frozen) was executed exactly as frozen against the 120 CORE cases of
NAV-EXPLORE-RC1-BLIND-V1. Predictions are frozen before any answer-key access.

## Files

| File | Purpose |
|---|---|
| TASK-LOCK.json | Phase lock: PREDICTION_BEFORE_KEY, answer_key_access=false |
| run_blind_phase1.py | Deterministic driver; calls the frozen RC1 pipeline functions (polarity engine v0.2, auto_gate, reviewer) in the same import configuration as hybrid/run_hybrid_eval.py. Multi-source cases are joined into one source string (documented adapter, no runtime change) |
| RC1-predictions.json | Authoritative prediction artifact (read-only): 120 outcomes incl. full raw intermediates (engine atoms, gate reason, reviewer packet output, fusion route) |
| prediction-freeze.json | SHA-256 freeze manifest (read-only) |
| phase1-run-report.md | Run log and integrity verification |
| phase1-final-report.md | 39-point SLUTTRAPPORT (prediction/integrity only) |

## Firewall

No answer-key decryption, no key search, no scoring, no tuning, no runtime
changes in this phase. The answer key was never accessed and the blind key was
never available. Reserve cases (67) were not executed.

Phase 2 requires the user to send BLIND_RC1_KEY in a separate message after
this freeze; the key must never be pasted into a certification prompt.
