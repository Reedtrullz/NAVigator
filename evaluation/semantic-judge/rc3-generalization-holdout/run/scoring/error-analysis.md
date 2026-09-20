# G2 ERROR ANALYSIS (post-freeze, spec 32-36)

Stage: run only after official-generalization-score.json was frozen (SHA 384e1a21...1bb). Aggregate-only artifacts; no plaintext labels written; no score rewrite; no rerun; no tuning.

## Headline

159 cases analyzed. 133 semantic misses, 115 proof-safe misses, 99 product misses. The dominant failure is not wrong polarity but **routing collapse**: 118 of 133 semantic misses predicted REVIEW_REQUIRED, and 82 of 116 review predictions were unnecessary. The engine's non-auto default did not generalize to an untuned corpus.

## Failure-mode counts (spec 33)

| Failure mode | Count | Basis |
|---|---|---|
| SEMANTICALLY_UNSOUND_PROOF | 53 accepted atoms | official proof_gates (atom-level AUTO route) |
| PROOF_SAFE_UNSOUND_AUTO | 14 cases | case-level auto rows |
| WRONG_DECOMPOSITION | 17 cases | missing or extra atoms vs expected |
| CORRECT_ATOMS_WRONG_AGGREGATION | 3 cases | all atoms correct, product wrong |
| CORRECT_PROOF_WRONG_ROUTING | 0 cases | semantic and proof-safe correct but product wrong |
| SOUND_AUTO_WRONG_PRODUCT | 0 cases | all accepted atoms sound and auto, but product wrong |
| STRUCTURALLY_INVALID_PROOF | 0 | official proof_gates |
| UNGROUNDED_PROOF | 0 | official proof_gates |

Denominator note: official proof_gates counts accepted-proof atoms routed AUTO at atom level across all rows (64 accepted atoms, 53 unsound). Within the 24 case-level AUTO rows there are 32 accepted atoms, 19 unsound, and 14 cases with at least one unsound atom or wrong polarity. Both views are reported; the case-level unsound-auto count (14) is identical in both.

## Severity (spec 34)

| Severity | Count | Rule applied |
|---|---|---|
| CRITICAL | 14 | wrong product on an auto-routed case (unsafe auto) |
| HIGH | 85 | wrong product on non-auto case |
| MEDIUM | 34 | semantic and proof-safe both wrong, product right |
| LOW | 0 | single-layer mismatch with product correct (none survived: all 34 both-layer mismatches had product correct) |
| OK | 26 | fully correct case |

Severity is descriptive; the readiness verdict is unchanged by construction.

## Deterministic taxonomy (spec 32)

| Tag | Cases | Note |
|---|---|---|
| NEGATION | 47 | truth rationale or atom inference involves negation scope |
| EVIDENCE_SUFFICIENCY | 35 | truth is INSUFFICIENT_EVIDENCE or genuine_insufficiency |
| NUMERIC | 16 | numeric comparison/aggregate involved |
| TEMPORAL | 12 | temporal comparison involved |
| ACTOR_SCOPE | 5 | actor/role scope involved |
| DEONTIC_MODAL | 4 | modality/deontic qualifier involved |
| ENGINE_POLARITY | 8 | predicted polarity flipped vs truth polarity |
| REVIEW_VS_ABSTAIN | 18 | review predicted where abstain expected or vice versa |
| WRONG_DECOMPOSITION | 17 | 15 cases missing atoms, 2 cases extra atoms |
| TOP_LEVEL_AGGREGATION | 3 | atoms all correct, aggregation wrong |
| ARBITRATION | 0 | reviewer never engaged (reviewer_used = 0) |
| OTHER | 58 | semantic miss with no specific marker |

Tags are not exclusive; a case can carry several.

## Truth-to-prediction flow (semantic)

The scorer confusion matrix (semantic-confusion.json) shows the collapse pattern:

- 29 SUPPORTED, 35 CONTRADICTED, 36 PARTIALLY_SUPPORTED, 18 INSUFFICIENT_EVIDENCE truths all predicted REVIEW_REQUIRED.
- Only 8 CONTRADICTED, 6 SUPPORTED, 5 PARTIAL, 1 INSUFFICIENT predictions were committed at all, and most of those were wrong (auto precision 41.67 percent).

Reading: Phase A proof machinery (structural validity, grounding) held; the Phase A/B/C semantic judgment, decomposition, and routing layers did not transfer to the untuned corpus.

## Arbitration observations

reviewer_used = 0 on all 159 outcomes: the keyless snapshot ran engine-only, so RC3's reviewer/arbitration layer was never exercised on this holdout. No reviewer flips occurred and none could be evaluated. The RC2-era failure class (reviewer overriding correct engine proofs) therefore remains untested on novel data, not disproven.

## Scorer defect discovered during analysis (registered, not patched)

The frozen scorer's zero-tolerance proof gates cannot fail: gate_results receives denominator 0 and short-circuits actual to 0.0. Recomputed from proof_gates counts, semantically_unsound_accepted_proofs = 53 and proof_safe_unsound_autos = 14 would both FAIL a correct zero-tolerance gate. Structural-invalid and ungrounded counts are genuinely 0 and pass either way. The official score artifact is preserved byte-for-byte; this defect is mandatory input for the next scorer version and does not change the verdict, which already fails on 11 other gates.
