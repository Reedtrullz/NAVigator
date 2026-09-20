# RC2 Partial-Band Analysis (BURNED_BLIND_V1_DEVELOPMENT_ONLY)

Data: 103 reviewer-routed rows from frozen RC1 predictions, scored
against the in-memory-decrypted sealed answer key. Two views:

1. **Final** — the verdict RC1 actually shipped per row.
2. **Counterfactual** — what would have happened if the reviewer's own
   verdict were auto-accepted at its confidence (the fusion question).

## Band table (counterfactual unless noted)

| Band | n | final sem | final prod | cf sem | cf prod | engine agree | agree-OK | cf false sup | cf false con |
|---|---|---|---|---|---|---|---|---|---|
| <0.70 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 0.70-0.77 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0.78-0.84 | 12 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| 0.85-0.89 | 2 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 |
| >=0.90 | 82 | 67 | 67 | 62 | 69 | 25 | 24 | 0 | 0 |

## Findings

1. **The 0.78-0.84 hypothesis is dead.** 0/12 counterfactual-correct.
   Lowering the global threshold into this band would inject 12
   unsound autos. Rejected.
2. **Direction asymmetry at >=0.90.** Accepting reviewer SUPPORT:
   32/32 semantic and product correct, zero false supports, including
   21 CRITICAL + 11 HIGH rows. Accepting reviewer CONTRA: 30/31 - the
   miss is RC1B-0169 (HIGH, truth PARTIALLY_SUPPORTED; both engine and
   reviewer overcalled CONTRA on a SUPPORT+INSUFFICIENT atom mix).
3. **Engine agreement is not the discriminator.** It halves accept
   volume (16 of 32) with zero accuracy gain (16/16 correct without
   conditioning; the 16 non-agreeing rows are also all correct - five
   are engine false-contras the reviewer overrode). Conditioning adds
   review load, not soundness. Rejected.
4. **Gate-reason classes do discriminate.** Among the 32 accept-SUPPORT
   rows, 13 carry only generic thinness flags (not_a_proof:*,
   engine_review_flag) and 19 carry specific defect evidence
   (compound_claim, numeric_support_binding, weak-support/coverage).
   Vetoing specific evidence and bypassing generic flags is the only
   cut that keeps 0 false supports while recovering autos.
5. **Threshold stays 0.90.** The 0.85-0.89 band has n=1 (1 correct) -
   insufficient evidence to lower it.

## Consequence

Fusion policy (fusion.py): auto-accept reviewer SUPPORT at conf >=0.90
only when no specific-defect gate reason exists; all CONTRA, all
PARTIAL/INSUFFICIENT, all sub-0.90, and all specific-flag rows stay
review. See fusion-calibration.json for metrics and provenance.
