# Historical reinterpretation under the dual-target contract

Task: SEMANTIC-JUDGE-EVALUATION-CONTRACT-REDESIGN. Raw artifacts only; no re-runs (spec 22). Legacy single-target numbers are marked LEGACY_SINGLE_TARGET_GATE where reused.

## Hybrid Iteration B (hybrid/results/hybrid-eval.json, 389 rows)

Recomputed from raw rows (not from report): 362 decided, 317 old-target correct = 87.57% selective (LEGACY_SINGLE_TARGET_GATE). 45 verdict errors, all review-path. Directions (benchmark -> engine): SUPP->INSUF 17, CONTRA->INSUF 11, INSUF->CONTRA 9, PARTIAL->CONTRA 5, CONTRA->PARTIAL 2, PARTIAL->INSUF 1.

### New-target metrics

| Metric | Value | Reading |
|---|---|---|
| Old selective accuracy (legacy) | 317/362 = 87.57% | mixes semantic and proof targets |
| Semantic accuracy, all decided rows (defaulted sets keep original label) | 333/362 = 91.99% | engine verdicts match semantic truth more often than the legacy score suggests |
| Semantic accuracy on the 78 reannotated cases (76 decided) | 47/76 = 61.8% | low by design: oracle-46 and the novel overlaps are error/probe-enriched |
| Auto path (121 claims) | semantic 120/121; proof-valid 119/121 | 1 over-proof (MP-014A auto-SUPPORTED, proof-safe INSUFFICIENT), 1 invalid auto-contradiction (ENT-C) |
| Review path (27 REVIEW_REQUIRED) | 6 necessary, 21 unnecessary-but-safe | moderate cost only (spec 21) |
| Critical false auto-SUPPORTED | 0 | preserved from B-run |
| Fidelity | 100% | unchanged |

### ENT-C finding (important)

Old benchmark scored ENT-C auto-CONTRADICTED as CORRECT (expected CONTRADICTED). Under the dual contract the source never states that PPT cannot diagnose; semantic_truth = INSUFFICIENT_EVIDENCE and proof_safe = INSUFFICIENT. The engine verdict is therefore an invalid auto-contradiction (very severe class, spec 21) that the legacy benchmark rewarded. The old "ENT-C PASS" gate was rewarding the failure mode the lexical-coverage stage later had to repair.

### Reinterpretation of the 87.57% headline

The 87.57% blended two different questions. Under the dual contract:
1. The auto path is near-ceiling: 120/121 semantically correct, 119/121 proof-valid, 0 critical FP. Product decisions on the auto path are sound except the two invalid proofs above.
2. All 45 verdict errors live on the review path. Reclassified against dual labels below.
3. 21 of 27 reviews were unnecessary (semantic truth equals proof-safe target and no doctrine review was required) - an efficiency cost, not a safety cost.
4. Several old "errors" are benchmark-label overreach: the engine was semantically right (see SEMANTIC_HIT rows below).

### 45-error reclassification

Columns: id | set | old expected | engine final | semantic truth | proof-safe | class.

| ACT-10 | actor-scope | SUPPORTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| ACT-19 | actor-scope | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| ACT-23 | actor-scope | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| ACT-25 | actor-scope | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| CAL029 | calibration | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CAL030 | calibration | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CAL048 | calibration | PARTIAL | CONTRADICTED | PARTIAL | PARTIAL | VERDICT_EXCEEDS_PROOF_BOUNDS |
| CAL050 | calibration | PARTIAL | CONTRADICTED | PARTIAL | PARTIAL | VERDICT_EXCEEDS_PROOF_BOUNDS |
| CAL064 | calibration | CONTRADICTED | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| CAL086 | calibration | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CAL089 | calibration | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | REVIEW_REQUIRED | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CI-040 | contra-insuff | INSUFFICIENT | CONTRADICTED | CONTRADICTED | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CI-041 | contra-insuff | INSUFFICIENT | CONTRADICTED | CONTRADICTED | CONTRADICTED | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CI-046 | contra-insuff | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| CI-059 | contra-insuff | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| CI-061 | contra-insuff | INSUFFICIENT | CONTRADICTED | CONTRADICTED | CONTRADICTED | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| CI-065 | contra-insuff | INSUFFICIENT | CONTRADICTED | CONTRADICTED | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| D20-L5 | diagnostic-20 | SUPPORTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| ENT-A | ent | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| HOL005 | holdout-v2-burned | PARTIAL | INSUFFICIENT | PARTIAL | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| HOL007 | holdout-v2-burned | PARTIAL | CONTRADICTED | PARTIAL | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| HOL020 | holdout-v2-burned | PARTIAL | CONTRADICTED | CONTRADICTED | CONTRADICTED | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| HOL022 | holdout-v2-burned | CONTRADICTED | INSUFFICIENT | CONTRADICTED | CONTRADICTED | VERDICT_EXCEEDS_PROOF_BOUNDS |
| HOL026 | holdout-v2-burned | CONTRADICTED | PARTIAL | CONTRADICTED | CONTRADICTED | VERDICT_EXCEEDS_PROOF_BOUNDS |
| HOL030 | holdout-v2-burned | CONTRADICTED | PARTIAL | CONTRADICTED | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| HOL034 | holdout-v2-burned | CONTRADICTED | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| HOL037 | holdout-v2-burned | CONTRADICTED | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| HOL040 | holdout-v2-burned | PARTIAL | CONTRADICTED | PARTIAL | PARTIAL | VERDICT_EXCEEDS_PROOF_BOUNDS |
| LOC-10 | locality | INSUFFICIENT | CONTRADICTED | CONTRADICTED | CONTRADICTED | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| LOC-20 | locality | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| MOD-13 | modality | SUPPORTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| MP-007A | minimal-pairs | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| MP-009A | minimal-pairs | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| MP-013B | minimal-pairs | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| MP-014A | minimal-pairs | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| MP-015A | minimal-pairs-supplement | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| MP-016A | minimal-pairs | SUPPORTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| N-A3 | novel-40 | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |
| N-C4 | novel-40 | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| N-C5 | novel-40 | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| N-L4 | novel-40 | SUPPORTED | INSUFFICIENT | SUPPORTED | SUPPORTED | VERDICT_EXCEEDS_PROOF_BOUNDS |
| N-O5 | novel-40 | CONTRADICTED | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| N-R3 | novel-40 | INSUFFICIENT | CONTRADICTED | INSUFFICIENT | INSUFFICIENT | VERDICT_EXCEEDS_PROOF_BOUNDS |
| N-S4 | novel-40 | SUPPORTED | INSUFFICIENT | SUPPORTED | INSUFFICIENT | PROOF_SAFE_ABSTENTION (semantic miss, product-safe) |
| N-S9 | novel-40 | SUPPORTED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SEMANTIC_HIT_BENCHMARK_OVERREACH |

Counts: {"PROOF_SAFE_ABSTENTION (semantic miss, product-safe)": 16, "SEMANTIC_HIT_BENCHMARK_OVERREACH": 17, "VERDICT_EXCEEDS_PROOF_BOUNDS": 12}

Per-set old vs semantic hits (decided rows):

| Set | n | old hit | semantic hit |
|---|---|---|---|
| actor-scope | 30 | 26 | 27 |
| calibration | 84 | 64 | 68 |
| contra-insuff | 69 | 62 | 66 |
| diagnostic-20 | 20 | 18 | 19 |
| ent | 4 | 3 | 2 |
| holdout-v2-burned | 40 | 28 | 29 |
| locality | 20 | 16 | 17 |
| minimal-pairs | 48 | 42 | 44 |
| minimal-pairs-supplement | 4 | 3 | 3 |
| modality | 30 | 28 | 29 |
| novel-40 | 40 | 27 | 29 |

## Quote-aligner v0.2 (novel-40)

Original gate: 27/35 decided = 77.1% -> FAIL vs 90% (LEGACY_SINGLE_TARGET_GATE). Under semantic truth the engine hits 29/35 = 82.9%: N-S9, N-A3, N-O5 flip from miss to hit because their benchmark labels demanded more than bounded reading licenses; N-S4, N-L4, N-C4, N-C5, N-R3 remain genuine misses. The 90% novel-40 gate measured the wrong target for at least 3 of its 8 misses.

## Reviewer v1.1 (oracle probe 24-case subset)

Benchmark accuracy 5/24 = 20.8% vs doctrine accuracy 22/24 = 91.7% (existing probe numbers, not re-run). The 20.8% is a label-alignment artifact, not a reasoning collapse: only N-L4 and N-C5 are true doctrine errors. Under the dual contract reviewer v1.1 is proof-safe-strong and the 20.8% must not be quoted as semantic capability. Structured-proof variant stays frozen (probe conclusion).

## Legacy gates now misaligned

- novel-40 <90% -> FAIL (target not stated: original vs semantic)
- oracle probe benchmark accuracy as a capability measure
- any single-number accuracy over mixed sets (calibration + holdout + probe)
- ENT-C PASS as a contradiction-precision signal (rewarded invalid contradiction)

## New readiness metrics (spec 33)

- Semantic reviewer: semantic accuracy on CONFIRMED dual-label cases; dispute-weighted.
- Proof engine: invalid-proof rate = 0 (auto verdict must equal or be more cautious than proof-safe target).
- Product fusion: critical false auto-decisions = 0; unnecessary-review rate reported separately as efficiency.
