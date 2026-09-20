# Final Report - Phase 2B

Task: NAV-EXPLORE-RC2-BLIND-V4-PHASE2B-SCORING

## Verdict

RC2_NOT_CERTIFIED - 8 of 12 preregistered hard gates failed; 4 passed.
No integrity, blindness, or protocol compromise: CERTIFICATION_INVALID
does not apply. No conditional pass.

## What was done

1. All frozen artifacts rehashed and verified before decryption
   (predictions, policy, scorer, certification metrics, RC2 10/10,
   V4 blind-cases/answer-key/construction-audit).
2. Authenticated in-memory decryption of the sealed answer key with the
   V4 AES-256-GCM convention; structural validation passed (160 rows,
   exact ID equality, 62/62 compound with 141 atoms, 40 critical).
3. Frozen scorer applied the frozen policy mechanically; official
   score written and hash-frozen (e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2)
   before any error inspection.
4. Post-freeze error analysis, confusion matrices, subgroup/compound
   deliverables, label audit, audited sensitivity.
5. Post-analysis rehash: every frozen artifact byte-identical.

## Results

* Semantic exact: 53/160 = 33.12% (gate >= 90%)
* Proof-safe exact: 40/160 = 25.00% (gate >= 95%)
* Product exact: 68/160 = 42.50% (gate >= 95%)
* Combined auto precision: 14/17 = 82.35% (gate >= 99%)
* Critical product: 16/40 = 40.00% (gate 100%)
* Compound atom: 36/141 = 25.53%; compound product 46/62 = 74.19%
* Review: TP 54 / FP 89 / FN 1 (precision 37.76%, recall 98.18%)
* Abstain: 0 predicted / 26 FN (no abstain bucket in RC2)
* Invalid accepted proofs: 3 (all exceeds-proof-safe on false SUPPORTED)
* Hallucinated proofs: 0. Critical unsafe autos: 0/0. Runtime failures: 0.
* Severity: CRITICAL 3, HIGH 0, MEDIUM 63, LOW 80.

## Generalization finding

RC2's calibration collapsed off-distribution: on V4 the pipeline
defaulted to REVIEW_REQUIRED on 143/160 cases and its reviewer+fusion
layers inverted or discarded engine verdicts that were already correct,
while the few auto decisions it did take were 82.35% precise with all
three errors being proof-bound violations (auto-SUPPORTED where the
sealed proof-safe target was CONTRADICTED). The failure is systemic
(routing/calibration), not a long tail of hard cases.

## Main remaining weakness

Proof-bounded auto-gating: the engine's quote-alignment supports text
that contradicts the claim when negation/deontic markers trail the
aligned span, and neither reviewer nor fusion catches it - so the
auto path is simultaneously too eager (3 false SUPPORTED) and too shy
(63 unnecessary reviews). Compound decomposition coverage (missing
expected atoms on 35/62 cases) is the second structural weakness.

## R&D recommendation

Yes - reopen evaluator R&D for RC3, but as calibration/routing work,
not re-annotation: (1) fix negation/deontic span handling in the
engine, (2) re-gate reviewer/fusion so they cannot flip a correct
engine auto verdict without proof-bound evidence, (3) add the ABSTAIN
bucket for insufficiency, (4) fix compound atom emission to match
canonical decomposition, and (5) fix the scorer's confusion-matrix
view key (RC3_BUG_CANDIDATE). Do not rerun V4 predictions; do not
tune on blind labels.

## QA

* All pre/post hashes verified (see certification-report.md).
* Official score frozen before error analysis: yes.
* Reserve used 0. Reruns 0. Tuning none. Runtime modified: no.
* KEY_ACCEPTED = TRUE; key not persisted; plaintext answer key never
  written to disk; temp scripts removed; key session terminated.
* v4_qa.py live plaintext-label gate reports expected hits on scoring
  artifacts (that gate is a pre-score firewall; per spec 40 post-score
  artifacts legitimately contain prediction-vs-expected analysis).
  6/6 fixture regression tests pass; no full plaintext key on disk
  (structure-field scan clean).
* qa_check.sh is V2-set-specific and was not compatible with V4; V4
  equivalent (v4_qa.py + qa-tests) run instead.
