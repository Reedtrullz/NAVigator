# FINAL REPORT - RC1 BLIND RECERTIFICATION PHASE 2

## Verdict

RC1_NOT_CERTIFIED.

Evaluator RC1 (semantic-judge v0.4.1 stack) scored 79/120 semantic (65.83%), 44/120 proof-safe (36.67%), 79/120 product (65.83%) against thresholds 90/95/95. Combined auto precision 93.33% (threshold 99%). Critical subgroup product 37/60 (61.67%, requires 100%). Hard gate failed on 2 critical unsafe AUTO_CONTRADICTED (RC1B-0122, RC1B-0131). Proof quality gates passed: 84/84 accepted proofs valid, 0 invalid, 0 hallucinated, 0 critical unsafe AUTO_SUPPORTED.

Official score frozen at SHA-256 fff9b539b97d414389fbc6198d1ecbc92f546556bbc7374fdbbfa29d5ef93d72 before error analysis. Full numbered results: certification-report.md.

## Root causes

1. Deterministic false CONTRADICTED: the age parser reads law citations ("§ 4-3", FOR-ids) as age ranges and the numeric rule conflicts full-rate vs halved-rate amounts in the same table row; hard engine CONTRA cannot be overridden by the reviewer, locking unsafe AUTO_CONTRADICTED (2 critical cases) and adding false contradictions elsewhere.
2. Over-cautious fusion: reviewer PARTIAL outputs (0.78-0.84) sit below the 0.90 numeric fusion threshold, so provable claims end in REVIEW/INSUFFICIENT (27 cases where the key proves the claim).
3. Over-abstention: 35 ABSTAIN vs 5 expected (31 over).
4. Atom segmentation: 48.9% atom accuracy on alignable compound cases caps compound accuracy.
5. One runtime failure (RC1B-0112, polarity_engine.py:474 AttributeError), scored conservatively incorrect; all thresholds fail with or without it.

## Label audit

2 strong potential blind-label errors flagged (RC1B-0116, RC1B-0165 - compound CONTRADICTED where the contract's one-atom-supported/one-contradicted partial rule fits better), 1 borderline (RC1B-0143). Flipping both would move semantic/product to 81/120 (67.5%) - verdict unchanged. No alternate score computed; official key untouched (label-audit.md).

## Recommendation

Reopen evaluator R&D. For RC2: fix the two engine regex defects (B1/B2) with regression tests, recalibrate fusion thresholds (B3) and reviewer INSUFFICIENT calibration (B6) on the calibration set, add the crash guard (B7), then a fresh blind run. RC1 remains unpatched; no reruns, no reserve use.
