# RC1 Blind Recertification - Phase 2 (Scoring After Freeze)

Phase 2 of the RC1 blind recertification: decrypt answer key after the Phase-1 prediction freeze, score the 120 frozen core predictions, produce the certification verdict.

## Contents

- TASK-LOCK.json - phase task lock (status COMPLETED after close)
- scoring-policy.json - pre-hashed scoring policy (RC1-PHASE2-SCORING-POLICY-V1)
- certification-results.json - full gate/threshold results per policy
- official-score.json - official score artifact (frozen; scorer correction note embedded)
- official-score-freeze.json - official-score SHA + freeze-before-error-audit attestation
- semantic-confusion.json / proof-safe-confusion.json / product-confusion.json - 5x5 confusion matrices (rows = predicted, cols = key)
- subgroup-results.json - subgroup accuracies (safety, legal, numeric, temporal, locality, modality, actor, condition/exception, compound, multi-span, genuine-insufficiency)
- proof-audit.json - per-case proof re-derivation audit (84/84 valid)
- rc1b-0112-impact.json - runtime-failure counterfactual
- error-analysis.md - 82-error severity table, root causes, RC2 bug candidates
- label-audit.md - potential blind-label errors and impact
- certification-report.md - numbered items 1-66 per spec
- final-report.md - executive summary

## Verdict

RC1_NOT_CERTIFIED (all three accuracy thresholds, critical-product, unsafe-contra hard gate, and auto precision fail; proof-quality and reserve gates pass).

## Provenance

- Predictions frozen in Phase 1 (see ../prediction-freeze.json, ../RC1-predictions.json, SHA-verified, mode 444).
- Answer key decrypted in memory only; no plaintext key persisted; temp artifacts deleted.
- No RC1 patching, no reruns, no reserve use, no KB or label changes.
