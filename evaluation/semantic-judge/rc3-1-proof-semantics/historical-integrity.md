# Historical Integrity Record

Task: `NAV-EXPLORE-RC3_1-PROOF_SEMANTICS-REPAIR` (RC3.1 proof-semantics repair)

## Verified at task start (2026-09-04)

All four historical artifacts under `evaluation/semantic-judge/rc3-generalization-holdout/` verified with SHA-256 at task start and re-verified at task end (see bottom).

| Artifact | SHA-256 |
|---|---|
| `run/RC3G-predictions.json` | `6923c66c8abafde0bd0e3e58a282e2b40a3da4adefd3a364b25cddcd3a88a361` |
| `run/scoring/official-generalization-score.json` | `384e1a21798001041d961ab06b0f5111f3b3077d6e3b519f56fff7aa739a61bb` |
| `generalization-cases.json` | `3f22c19b9f48e748ed5b5aadd0f715430e914225fc2923edd0e953cf09e720d4` |
| `answer-key.sealed` | `e25b3ab813274662e354d4502192c2639df765bb3e5c5e67e616cba1fa32498a` |

## Burned status

`RC3G-HOLDOUT-V1` = **BURNED_GENERALIZATION_DEVELOPMENT_ONLY**.

Permitted uses in this task: aggregate failure counts, root-cause taxonomy, a limited number of forensic cases, generalized failure shapes. Prohibited: threshold sweeps, variant selection, prompt optimization, readiness scoring, model selection, re-running, and any `RC3G-*` case ID in runtime code.

## Frozen failure baseline (diagnosis only, from official score)

| Metric | Value |
|---|---|
| semantic | 26/159 = 16.35% |
| proof-safe | 44/159 = 27.67% |
| product | 60/159 = 37.74% |
| auto precision | 10/24 = 41.67% |
| auto coverage | 24/159 = 15.09% |
| structurally invalid accepted proofs | 0 |
| ungrounded accepted proofs | 0 |
| semantically unsound accepted proofs | 53/64 atom proofs |
| proof-safe unsound autos | 14/24 |
| necessary-review recall | 77.27% |
| unnecessary-review | 70.69% |
| abstain recall | 45.71% |
| review/abstain macro F1 | 0.520 |
| compound atom-count exact | 67.31% |
| atom semantic | 44.54% |
| compound product | 55.77% |
| runtime failures | 0 |

## Immutable artifacts (untouched in this task)

- RC2 official score, RC2/V4 artifacts
- RC3G predictions, G1 prediction freeze
- G1.5 scoring-policy freeze
- G2 official-generalization-score and official score freeze
- holdout answer key and annotations

Official `GENERALIZATION_FAIL` is permanent and shall never be rewritten. The corrected proof-gate audit (`corrected-proof-gate-audit.json`) is an analytics-only companion artifact; it does not modify the official score and does not change the verdict.

## 2026-09-05 session 4 addendum (engine execution + stop)

- Corpus SHAs re-verified: train fb467faefb7a..., validation-cases
  3e336d68fc17..., validation-answer-key.sealed 15b13bb7006e... (seal unopened).
- RC3G protected artifacts re-verified, all match the table above.
- engine.py had never compiled (backslash corruption in its write step); it was
  rewritten once with identical rule intent in a backslash-free regex style.
- First train run: 77.42 percent relation accuracy, 61 unsound auto atoms.
  After the single bounded bugfix pass: 84.68 percent, 40 unsound auto atoms,
  stability 100 percent, compound count exact 42/43.
- Hard train gates not met. Per the one-bounded-pass rule, tuning stopped.
  Validation seal not opened, no validation run, no release candidate.
  Status: RC3_1_PROOF_NOT_READY. See final-report.md and train-results.txt.

## Scorer gate bug (fixed first, per spec section 4)

Root cause: `gate_results()` in the frozen scorer divided numerator by a hardcoded denominator of 0 for zero-tolerance gates, short-circuiting to 0.0 and always PASS. Fix: new `score_generalization_v2.py` evaluates zero-tolerance gates as raw count comparisons. Official G2 artifact untouched. See `corrected-proof-gate-audit.json` and `scorer-v2-report.md`.
