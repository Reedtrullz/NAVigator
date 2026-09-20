# ERROR ANALYSIS - RC1 BLIND RECERTIFICATION PHASE 2

Basis: official-score.json (SHA-256 fff9b539b97d414389fbc6198d1ecbc92f546556bbc7374fdbbfa29d5ef93d72, frozen before this analysis), per-case comparisons re-derived from the frozen prediction artifact and the decrypted answer key. No runtime, prediction, key, or label artifact was modified.

## Error population

82 of 120 cases have at least one wrong target (semantic, proof-safe, or product). Severity classification assigns one priority per case:

RUNTIME > CRITICAL-UNSAFE-CONTRA > CRITICAL-PRODUCT-MISS > product-level > proof-safe-only > semantic-only.

| Severity | n | Cases / definition |
|---|---|---|
| CRITICAL unsafe AUTO_CONTRADICTED | 2 | RC1B-0122, RC1B-0131 (hard-gate failure) |
| RUNTIME | 1 | RC1B-0112 (AttributeError, conservative default) |
| HIGH critical product miss | 20 | remaining critical product errors (23 - 2 - 1) |
| MED over-abstention | 10 | non-critical ABSTAIN where key expects AUTO_SUPPORTED/AUTO_CONTRADICTED (0001, 0004, 0009, 0017, 0028, 0101, 0134, 0144, 0145, 0151) |
| MED unnecessary review | 2 | RC1B-0005, RC1B-0143 (non-critical REVIEW where key expects AUTO_SUPPORTED) |
| OTHER product error | 6 | 0010, 0014, 0102, 0169, 0176, 0178 (system auto-decided where key expects REVIEW_REQUIRED/ABSTAIN_INSUFFICIENT) |
| LOW proof-safe-only | 40 | product correct, proof-safe target wrong |
| LOW semantic-only | 1 | RC1B-0192 |

Sum: 82. The 17-cell product-overlap (e.g. ABSTAIN where key AUTO_SUPPORTED) appears in both the confusion matrix and this table; the priority rule prevents double counting.

## Root cause 1 - deterministic false CONTRADICTED verdicts

The frozen quote-aligner v0.2 emits hard CONTRADICTED on two defective patterns. Per fusion spec the reviewer cannot override a hard engine CONTRA, so these lock the product action.

- Age-range parser treats law references as ages. extract_ages (quote-aligner/quote_aligner.py:148) matches digit ranges with an optional year suffix, so "PRL § 4-3" parses as the interval [4, 3]; age_relation (quote_aligner.py:192) then reports "disjoint" against a real "fra 16 år" span, and polarity_engine.py:485 escalates to hard CONTRA. Verified on RC1B-0122 ("§ 4-3" vs "fra 16 år"); RC1B-0131 fails via the same age_disjoint rule on a forskrift citation (FOR-2026-06-25-1361). Key: SUPPORTED; system: AUTO_CONTRADICTED.
- Numeric cross-amount conflict. _numeric_contra (polarity_engine.py:238) fires when the claim's number and any same-unit number in the aligned source row have disjoint bounds. RC1B-0005: claim "full sats 2 572 kroner" collides with "1 286 kroner per forelder" from the halving rule in the same row. RC1B-0086: same pattern on a 3-months deadline row. Verdict: CONTRADICTED (engine) where key: SUPPORTED.

Both rules produce semantic + proof-safe + product errors simultaneously.

## Root cause 2 - over-cautious reviewer/fusion (27 rows)

27 rows have a key-supported claim (proof exists, key proof-safe SUPPORTED) but the system returns REVIEW_REQUIRED or INSUFFICIENT_EVIDENCE:

| Fusion route | n | Notes |
|---|---|---|
| accepted (proof override, engine PARTIAL/INSUFFICIENT) | 10 | 0005, 0088, 0111, 0120, 0136, 0138, 0140, 0143, 0147, 0189 |
| below_threshold_or_flagged | 9 | reviewer PARTIAL 0.78-0.84 vs numeric threshold 0.90; two cases (0139) reviewer SUPPORTED 0.88 still below 0.90; 0132 also needs_human_review flag |
| reviewer_insufficient | 5 | 0079, 0086, 0117, 0152, 0162 (reviewer INSUFFICIENT where key proves the claim) |
| support_span_not_entailing | 3 | 0004, 0009, 0126 |

Threshold mechanics: classify_threshold (hybrid/reviewer.py:177) requires 0.95 (safety) or 0.90 (numeric/legal); reviewer PARTIAL outputs cluster at 0.78-0.84, so numeric claims systematically fall below the fusion threshold. Only 8 of the 27 are semantically correct (all in the accepted route), i.e. the semantic layer compounds the product error in 19/27.

The remaining proof-safe-only errors are dominated by REVIEW_REQUIRED->CONTRADICTED (21) and INSUFFICIENT_EVIDENCE->SUPPORTED (17) confusion cells; the first overlaps root cause 1 (engine hard CONTRA), the second root cause 2 and 3.

## Root cause 3 - over-abstention

- ABSTAIN predicted on 35 cases, key expects ABSTAIN on only 5; correct 4, over-abstention 31, under-abstention 1.
- Product confusion: ABSTAIN->AUTO_SUPPORTED 17, ABSTAIN->AUTO_CONTRADICTED 9, ABSTAIN->REVIEW_REQUIRED 5, ABSTAIN->ABSTAIN 4 (correct), ABSTAIN->AUTO_SUPPORTED after accepted review 2.
- Dominant gate reasons on the ABSTAIN errors: not_a_proof:INSUFFICIENT_EVIDENCE (no reviewer engaged) and compound_claim gates. The auto gate abstains where the key expects a proof-backed auto decision.

## Root cause 4 - atom segmentation quality

On the 21 compound cases with alignable atoms: 22/45 atoms correct = 48.9% atom accuracy. Compound product accuracy overall: 49/80 = 61.25%. Segmentation and atom-level signals, not the reviewer, are the limiting factor for compound claims.

## Root cause 5 - genuine-insufficiency handling

Genuine-insufficiency subgroup (n = 7, exploratory): proof-safe 6/7 correct but semantic only 4/7. Failure mode: engine emits hard CONTRADICTED on claims the key labels INSUFFICIENT_EVIDENCE (underdetermined), i.e. over-confident contra where abstention is correct.

## Efficiency

- Deterministic-only: 17; reviewer used: 103/119 OK cases (85.8 LLM calls per 100 cases); 0 retries; 1 runtime failure; 510.8 s wall clock. Token usage not emitted by the frozen components.
- Review/auto coverage: product auto decision rate 62.5% (75/120), review rate 7.5%, abstain rate 29.17%.

## RC2 bug candidates (priority order)

- B1 age parser: require explicit age context (aar/gamle/alder) after a digit range and reject ranges preceded by a section sign or inside citation tokens (FOR-YYYY-MM-DD-NNNN). Fixes RC1B-0122/0131 class.
- B2 numeric conflict: pair the claim number to its nearest bound match before declaring conflict; require same bound kind and semantic role (full rate vs halved rate), not merely same unit within one row. Fixes RC1B-0005/0086 class.
- B3 fusion threshold vs reviewer PARTIAL band: recalibrate numeric threshold (0.90) against the observed PARTIAL band 0.78-0.84, or route PARTIAL-with-accepted-proof to REVIEW_REQUIRED instead of silent threshold failure.
- B4 support_span_not_entailing is too strict for paraphrase supports (3 cases).
- B5 over-abstention: auto gate abstains on not_a_proof:INSUFFICIENT_EVIDENCE without engaging the reviewer even when a proof exists; consider proof-present -> REVIEW floor.
- B6 reviewer over-conservatism: INSUFFICIENT at 0.93-0.98 confidence on claims the key proves; reviewer prompt needs contradiction/sufficiency calibration examples.
- B7 runtime crash guard: polarity_engine.py:474 AttributeError (set object has no attribute values) on RC1B-0112; add regression test + defensive conversion.
- B8 atom segmentation: 48.9% atom accuracy caps compound accuracy; revisit segmentation before adding rules.

## Caveats

- Safety subgroup n = 3 and genuine-insufficiency n = 7 are too small for generalization.
- Condition/exception subgroup uses a keyword heuristic and deviates from the construction quota (N = 19 documented); exploratory only.
- No tuning, reruns, reserve use, or KB changes were performed; this analysis reads frozen artifacts only.
