# Metrics specification

Three separate targets; never blended into one accuracy (spec 17).

## 1. Semantic accuracy

Fraction of decided (non-review) verdicts matching semantic_truth on CONFIRMED dual-label cases. A reviewer that abstains where semantic truth is decidable is a semantic miss even if the abstention was proof-safe. Report per set; never average across sets with different composition without weighting disclosure.

## 2. Proof safety

Primary: invalid-proof rate = auto verdicts that exceed the proof_safe target, counted 0-tolerance. Includes unsupported auto-accept, unsupported auto-contradiction, and hallucinated premises. A REVIEW_REQUIRED where semantic truth is provable and proof-safe says otherwise is NOT a proof-safety failure (spec 19).

## 3. Product-decision quality

On each case with a known expected action: auto expected iff semantic_truth == proof_safe and the operator class is not REVIEW_ONLY; otherwise REVIEW_REQUIRED. Metrics: critical false auto-decisions (must be 0), wrong-auto rate, unnecessary-review rate (efficiency), abstention rate.

## Error-cost classes

| Class | Definition | Weight |
|---|---|---|
| Critical | false auto-SUPPORTED | blocking |
| Very severe | false auto-CONTRADICTED (legal/safety) | blocking |
| Moderate | unnecessary REVIEW_REQUIRED | efficiency |
| Low | semantic miss with no auto-decision | informational |

## Label-quality metrics

label_disagreement_rate = cases where original_benchmark_label != semantic_truth, over annotated cases. annotation_dispute_rate = ANNOTATION_DISPUTE cases over cases that entered two-pass review. High disagreement invalidates single-target gates (LEGACY_SINGLE_TARGET_GATE) rather than the model.

## Legacy gates superseded

novel-40 <90% FAIL; oracle benchmark accuracy; single-number mixed-set accuracy; ENT-C PASS as contradiction precision. Future reports must name the target (semantic / proof-safe / product) for every threshold.
