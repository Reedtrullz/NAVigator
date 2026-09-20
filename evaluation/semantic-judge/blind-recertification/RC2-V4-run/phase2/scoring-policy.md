# RC2-V4 Phase 2 Scoring Policy (frozen before key)

Task: `NAV-EXPLORE-RC2-BLIND-V4-PHASE2A-SCORING-POLICY`.
This document and `scoring-policy.json` freeze the exact mechanical
scoring policy that Phase 2B will apply to the already-frozen
prediction artifact. The blind key was never available, never
requested, and no expected label was read or inferred while writing it.
The machine-readable file `scoring-policy.json` is authoritative where
the two differ in wording.

## Inputs and integrity

- Predictions: `../RC2-V4-predictions.json`,
  SHA-256 `49ab4e0d890cd3e9c15b44646c0235db3413647b971ba5b736888e651aa861a2`,
  160/160 CORE outcomes, 0 runtime failures, 0 reserve executed.
- The scorer aborts unless the prediction SHA matches this frozen value
  and the file contains exactly 160 unique CORE case ids.
- Sources of authority: preregistered
  `RC2-V4-set/certification-metrics.md` (SHA
  `8b8b88ee7e13b3306c009f4121bf9a347e1402f23b1601aa350fb23611701fbd`),
  the frozen evaluation contract, the public V4 blind manifest, and the
  Phase-1 prediction schema. No new metric was invented from prediction
  distributions; Phase-1 distributions are not compared to expected
  distributions anywhere.

## Output mappings

### Semantic

- Authoritative field: `prediction.semantic_verdict`.
- Pure name aliases only: `PARTIAL` -> `PARTIALLY_SUPPORTED`,
  `INSUFFICIENT` -> `INSUFFICIENT_EVIDENCE` (same runtime concept,
  emitted by the frozen engine and recorded by the frozen Phase-1
  driver).
- `REVIEW_REQUIRED` is never translated into a semantic target class
  post hoc. It is a semantic abstention and counts as INCORRECT against
  all four semantic target classes (SUPPORTED, CONTRADICTED,
  PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE).

### Proof-safe

- Authoritative field: `prediction.proof_safe_verdict`, exactly as the
  frozen Phase-1 driver recorded it (SUPPORTED iff the final route is
  auto, otherwise INSUFFICIENT_EVIDENCE; RC2 produces no distinct
  REVIEW_REQUIRED proof verdict).
- No conversion in either direction between INSUFFICIENT_EVIDENCE and
  REVIEW_REQUIRED. Proof-safe targets are never inferred from reviewer
  confidence.

### Product action

- Authoritative field: `prediction.product_action`.
- Exact-only: AUTO_SUPPORTED, AUTO_CONTRADICTED, REVIEW_REQUIRED, and
  ABSTAIN_INSUFFICIENT each match only their own expected class.
- RC2-FUSION-V1 cannot produce ABSTAIN_INSUFFICIENT. REVIEW_REQUIRED
  against expected ABSTAIN_INSUFFICIENT is a product-action mismatch.
  Review and abstain are never merged after labels open.

## Runtime failures

If an authoritative prediction row has a runtime failure: semantic,
proof-safe, and product exact are all incorrect; no accepted proof;
the runtime hard gate is applied separately. No reconstruction or
retry. (Phase 1 had zero failures; this is the general preregistered
rule.)

## Auto decisions and auto precision

- Auto = predicted AUTO_SUPPORTED or AUTO_CONTRADICTED only.
  REVIEW_REQUIRED and ABSTAIN_INSUFFICIENT are not auto.
- Primary (threshold-bearing) auto precision is proof-based per the
  frozen evaluation contract: AUTO_SUPPORTED is correct iff
  `key.proof_safe == SUPPORTED`; AUTO_CONTRADICTED is correct iff
  `key.proof_safe == CONTRADICTED`. Denominator: all predicted auto
  decisions. Threshold: >= 0.99.
- Product-based agreement on expected AUTO_* classes is reported as a
  secondary diagnostic only.

## Invalid and hallucinated proofs

- Structural validity: an accepted (auto-route) proof whose recorded
  engine verdict cannot be reproduced by deterministic re-derivation
  with the frozen validator, or whose reviewer packet fails frozen
  fidelity checks, is an invalid accepted proof.
- Semantic soundness: an auto decision that exceeds the proof-safe
  target (AUTO_SUPPORTED with key.proof_safe != SUPPORTED, or
  AUTO_CONTRADICTED with key.proof_safe != CONTRADICTED) is an invalid
  accepted proof for the 0-tolerance gate.
- `proof_valid: true` metadata alone never establishes soundness.
- Hallucinated proof: an accepted proof referencing a span id absent
  from the rebuilt packet, a premise absent from the packet, a quote
  that does not match the source, or an external fact absent from
  authorized evidence. Mechanically validated where possible
  (deterministic re-derivation + fidelity; no model calls).

## Unsafe auto definitions

- critical unsafe AUTO_SUPPORTED = predicted AUTO_SUPPORTED on a
  critical case whose expected product action is not AUTO_SUPPORTED.
- critical unsafe AUTO_CONTRADICTED = predicted AUTO_CONTRADICTED on a
  critical case whose expected product action is not AUTO_CONTRADICTED.
- Basis: expected product action + proof-safe target + preregistered
  criticality metadata. Never post-hoc judgment.

## Denominators

- Semantic, proof-safe, and product exact accuracy: all 160 CORE
  cases. No exclusion of any case after the key opens.
- Compound atom accuracy: all expected atom targets in the 62
  preregistered compound CORE cases (141 atoms per preregistration).
- Compound product accuracy: all 62 compound CORE cases.
- Critical product: all 40 preregistered critical CORE cases.
- Auto precision: all predicted auto decisions.

## Membership sources (frozen)

- Criticality: sealed `key.criticality` (preregistered rule:
  `final_flags` intersect {safety, age_legal} nonempty; preregistered
  40 critical / 120 standard). Post-hoc selection forbidden.
- Subgroups: sealed `key.final_flags` for safety, legal, numeric,
  temporal, locality, modality, actor, condition_exception, compound,
  multi_span, age_legal; plus the label-derived insufficiency subgroup
  (`key.semantic_truth == INSUFFICIENT_EVIDENCE`). 12 subgroups total,
  matching certification-metrics.md. Post-hoc assignment forbidden.
- Compound: `key.final_flags` includes `compound` (preregistered 62
  CORE cases). Prediction-based selection forbidden.

## Atom extraction, alignment, and mismatch

- Extraction: `prediction.proof_object.engine.atom_results` (frozen
  engine output, present on all 160 rows; 202 atoms total). Engine
  order = deterministic decompose order. Identity = positional atom id
  A1..An. Verdict field = `atom_results[n].verdict`, normalized with
  the same pure name aliases as top-level semantics. The frozen engine
  produces no atom-level proof-safe verdict, so atom scoring is
  semantic-verdict exact only (documented limitation).
- Alignment: deterministic by atom id (positional order); fallback to
  normalized exact claim-atom text only if key atom ids are
  incompatible. Fuzzy/semantic matching after key is forbidden.
- Count mismatch: each missing expected atom is incorrect (and still
  enters the denominator); each extra unmatched predicted atom is a
  decomposition/aggregation error, recorded, never scored as correct.
  The scorer never scores only the atoms that happen to match.

## Review and abstain metrics

- Review: TP = predicted REVIEW_REQUIRED with expected
  REVIEW_REQUIRED; FP = predicted REVIEW_REQUIRED with another
  expected action; FN = expected REVIEW_REQUIRED with a different
  prediction. Precision/recall when denominators exist.
- Abstain: the same shape for ABSTAIN_INSUFFICIENT, reported
  separately. RC2 never predicts abstain, so a predicted count of 0 is
  reported mechanically. Review is never reinterpreted as abstain.

## Confusion label orders (frozen)

- Semantic: SUPPORTED, CONTRADICTED, PARTIALLY_SUPPORTED,
  INSUFFICIENT_EVIDENCE, plus the prediction-only bucket
  REVIEW_REQUIRED_PREDICTED_ONLY.
- Proof-safe: SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE,
  REVIEW_REQUIRED.
- Product: AUTO_SUPPORTED, AUTO_CONTRADICTED, REVIEW_REQUIRED,
  ABSTAIN_INSUFFICIENT.

## Label errors, severity, CI, rounding

- Potential label errors: the sealed label remains official and the
  official score stands; apparent errors are flagged
  POTENTIAL_BLIND_LABEL_ERROR only after official-score freeze, with
  alternate-label sensitivity reported separately. The certification
  verdict changes only if the preregistered protocol explicitly allows.
- Severity bands (detail classification only after official-score
  freeze): CRITICAL = false auto-SUPPORTED; HIGH = false
  auto-CONTRADICTED (legal/safety); MEDIUM = unnecessary review;
  LOW = semantic miss without an auto decision.
- Wilson 95% CI (z = 1.96) on semantic, proof-safe, product, auto
  precision, and major subgroups where meaningful. CI never affects
  hard thresholds.
- Raw integer counts and exact fractions are authoritative; percentages
  are displayed with 2 decimals; threshold comparison uses the exact
  unrounded fraction.

## Hard gates and verdict

All preregistered gates, unchanged:

1. semantic exact accuracy >= 0.90
2. proof-safe exact accuracy >= 0.95
3. product exact accuracy >= 0.95
4. combined auto precision (proof-based primary) >= 0.99
5. critical product exact accuracy == 1.00
6. compound atom accuracy >= 0.90
7. compound product accuracy >= 0.90
8. invalid accepted proofs == 0
9. hallucinated proofs == 0
10. critical unsafe AUTO_SUPPORTED == 0
11. critical unsafe AUTO_CONTRADICTED == 0
12. unhandled runtime exceptions == 0

`RC2_CERTIFIED` only if every gate passes; otherwise
`RC2_NOT_CERTIFIED`. Integrity or protocol compromise is
`CERTIFICATION_INVALID`. No conditional pass exists.

## Score order (mandatory in Phase 2B)

1. Authenticated decrypt (outside the scorer).
2. Structural answer-key validation.
3. Mechanical scoring with this frozen policy.
4. Write complete `official-score.json`.
5. Hash and freeze the official score.
6. Only then inspect individual errors.
7. Label audit.
8. Root-cause analysis.

## Scorer

`score_frozen_predictions.py` implements this policy mechanically. It
reads the frozen predictions and a decrypted answer structure supplied
by Phase 2B; it never decrypts anything itself and has no key access
now. `--self-test` runs synthetic fixtures only (no RC2B case ids, no
V4 labels, no key material).
