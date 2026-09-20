# RC3.3.1 Implementation Report

## Phase: main implementation pass

- New task-local module: engine_local/temporal.py (TEMPORAL_APPLICABILITY_V1).
  - applicability_mismatch(claim, evidence) -> False | FRAME_ONLY | VALUE_STALE | PERIOD_MISMATCH.
  - Sentence-level temporal markers with unit-suffix guards; year-phantom stripping for non-DATE quantities; law-stamp year-identity conflicts.
  - CURRENT_YEAR = 2026. All mark regexes raw strings (a concatenated-string backspace bug was caught and fixed during development).
- engine_local/numeric.py: temporal gating before final aggregation (FRAME_ONLY -> all UNRESOLVED; VALUE_STALE -> ENTAILS becomes UNRESOLVED, CONTRADICTS survives); open-boundary entailment; gratis carve-out; maneder spelling; claim-side year-phantom strip; law-stamp year identity.
- engine_local/engine.py: app_mismatch guards on R05/R07/R08/R09/R10; R01 quantity-aware fallback (RBI instead of UNRELATED when both sides carry quantities); R02 year-escape following the numeric layer.
- run_eval.py: task metrics - temporal_applicability, quantity_identity, comparator_state_on_applicable, law_reference_numeric_errors, unsound_eligible_proofs.

## Bounded bugfix pass (single, generalized)

Residual class (provenance-only anchor R33-126): claim value is derived from an
explicit in-claim fraction premise ("halvparten av X") whose operand is absent
from the evidence; the hard table rules auto-CONTRADICT on the value mismatch.

Fix: frac_premise_unverified(claim, evidence) in numeric.py returns True when an
explicit fraction operand is unverified; wired into (1) the numeric contradiction
path (aggregate conflict suppressed -> UNRESOLVED) and (2) the R07/R08 hard-rule
producers (CONTRADICTS -> RBI, rule R07/R08-derived-premise-unresolved).
Generalized across all fraction claims; no case IDs, no source filenames, no
amounts, no literal verdict maps. Verified non-regression: T90-041/R33-134
(verified bases) unaffected; T90-003/063 were already gated by temporal logic;
R33-140 (no numeric operand) unaffected.

## Post-fix state

- Development-60: relation 1.0, macro-F1 1.0, C-prec 1.0, false-stale 0,
  temporal 1.0 (58), quantity 1.0 (56), comparator 1.0 (11), law-ref 0, unsound 0.
- Global-140: relation 1.0, macro-F1 1.0, E-prec 1.0, C-prec 1.0 (40/40),
  RBI recall 1.0, false-stale 0, quantity 1.0 (68), law-ref 0, unsound 0.
