# Phase 1 run report - NAV-EXPLORE-RC1-BLIND-RECERT-PHASE1

## Pre-run verification

| Check | Result |
|---|---|
| RC1 manifest name | NAV-EXPLORE-EVALUATOR-RC1 |
| RC1 status | FROZEN |
| RC1 hashes | 17/17 OK |
| RC1 manifest SHA-256 | 5cb6c5a5ec80bfe719bc67ae00b884e90f85293cb8e9fc3a1559322e2578fe86 |
| blind-cases.json SHA-256 | a3a4dd60bc8662dd77581696809be6f68e93aeddf136ebad6f828cd4b52e7a39 (matches sealed manifest) |
| answer-key.sealed SHA-256 | f5e453950649a3b934f52f6d2d84cf2e7e93cbdd9edcbabc0c501006905406ff (matches sealed manifest) |
| blind-manifest.json | SEALED, core 120, reserve 67, RC1 status NOT_RUN |
| Reviewer proxy | OpenCodex 2.38.0 healthy at 127.0.0.1:10100 |

## Run

Command: python3 run_blind_phase1.py (frozen RC1 pipeline: E.judge_claim ->
auto_gate -> reviewer.review_claim; reviewer model openai/gpt-5.6-luna,
temperature 0 via local OpenCodex proxy).

- Started: 2026-09-03T07:18:52+0200, completed: 2026-09-03T07:27:22+0200 (510.8 s)
- Outcomes recorded: 120/120 CORE
- Runtime failures: 1 (RC1B-0112, AttributeError inside frozen quote-aligner
  polarity_engine.py _function_division, line 474: 'set' object has no
  attribute 'values'. Recorded per spec 9; not reconstructed, not retried, no
  runtime fix. It is a genuine RC1 bug surfaced by this case's input shape.)
- Deterministic-only decisions: 17; semantic reviewer calls: 103; retries: 0
- Token/cost accounting is not emitted by RC1's frozen components; reported as
  unavailable (103 calls listed per spec 25 aggregation options)

## Prediction distributions (prediction-only, no scoring)

| Field | Distribution |
|---|---|
| semantic_verdict | SUPPORTED 29, CONTRADICTED 46, PARTIALLY_SUPPORTED 9, INSUFFICIENT_EVIDENCE 12, REVIEW_REQUIRED 23, none 1 (runtime failure) |
| proof_safe_verdict | SUPPORTED 19, CONTRADICTED 30, INSUFFICIENT_EVIDENCE 35, REVIEW_REQUIRED 35, none 1 |
| product_action | AUTO_SUPPORTED 29, AUTO_CONTRADICTED 46, REVIEW_REQUIRED 9, ABSTAIN_INSUFFICIENT 35, none 1 |
| auto_or_review | AUTO 16, REVIEW 103 (gate-routed), failure 1 |

## Post-run verification

| Check | Result |
|---|---|
| RC1 hashes after run | 17/17 OK |
| RC1 manifest SHA | unchanged |
| blind-cases / answer-key.sealed / blind-manifest | unchanged |
| RC1-predictions.json SHA-256 | 0178f086b1e376c9a6f7f9bfaa67befd59507607fd12b1b4bbe502ade207f7b1 |
| PREDICTION_HASH_STABLE | TRUE |
| KB regression (no blind cases) | 48/48 BESTATT, fails=[] |
| Evaluator regression (no blind cases) | acc 1.00, FP=0, safety_FP=0 |
| Key-access scan over phase artifacts | NONE |
| RC1 key env vars | NONE |
| Score-artifact scan | CLEAN (no accuracy/confusion fields) |
| Reserve executed | 0 |
| Truth fields in predictions | NONE |

Prediction file and freeze manifest are read-only (chmod 444); SHA-256 is the
primary integrity mechanism.
