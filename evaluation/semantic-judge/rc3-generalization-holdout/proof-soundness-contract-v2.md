# Proof-Soundness Contract v2

Task: NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION
Status: FROZEN before holdout case authoring. Authoritative for the RC3 generalization holdout scoring policy.
Machine-readable twin: proof-soundness-contract-v2.json (same directory; both hashed).
Historical artifacts remain immutable. This contract changes evaluation TERMINOLOGY AND INSTRUMENTATION ONLY (METRIC_CONTRACT_REPAIR_ONLY); no runtime component is modified.

## Motivation (reconciliation result)

The burned V4 shadow reported simultaneously:

- invalid accepted proofs = 0
- auto precision = 16/34 = 47.06%

Recomputation under the separated metrics below (BURNED_V4_METRIC_RECONCILIATION_ONLY, n=160, 0 runtime failures, 66 accepted proofs, 34 autos) shows these are different metric layers, not a contradiction:

- STRUCTURAL_PROOF_VALIDITY failures: 0
- EVIDENCE_GROUNDEDNESS failures: 0
- SEMANTIC_PROOF_SOUNDNESS failures (atom level): 37
- PROOF_SAFE_AUTO_CORRECTNESS failures (case level): 18
- PRODUCT_ACTION_CORRECTNESS failures (autos): 18

Root cause: the historical "invalid proof" counter only measured structural validator failures (missing proof object or span absent from source). Auto precision measured correctness of the final auto polarity against the sealed proof-safe target. A proof can be structurally valid and grounded while its CONCLUSION is semantically unsound. Structural validity must never be allowed to hide semantic unsoundness (hard invariant, section 6).

## M1. STRUCTURAL_PROOF_VALIDITY

The proof object is technically/formally valid. For an accepted auto path this requires, per atom:

- a proof object exists (non-null)
- proof_type is one of SUPPORT, CONTRADICTION, DETERMINISTIC_COMPARATOR
- for SUPPORT/CONTRADICTION: source_span is a non-empty string
- for DETERMINISTIC_COMPARATOR: comparator rule id is registered in the frozen engine rule set

Failure class: STRUCTURAL_INVALID. Count: structural_invalid_accepted_proofs.

## M2. EVIDENCE_GROUNDEDNESS

Every span/premise referenced by the proof exists verbatim in the authorized evidence packet for the case. For an accepted auto path this requires, per atom:

- proof.source_span is a literal substring of the case evidence text (exact byte match after the frozen engine's own normalization, which is byte-preserving)
- no span id outside the case's evidence packet ids
- no premise text not traceable to packet spans

Failure class: UNGROUNDED (fabricated or out-of-packet premise). Count: ungrounded_accepted_proofs.

## M3. SEMANTIC_PROOF_SOUNDNESS

The proof conclusion actually follows from the evidence under the evaluation contract, at atom granularity. An accepted auto atom (AUTO_SUPPORTED or AUTO_CONTRADICTED) is SEMANTICALLY_UNSOUND when the sealed proof-safe target for the case does not allow exactly that auto polarity (i.e. the target forbids auto for that polarity or allows only the opposite polarity auto). This holds regardless of M1/M2 passing.

Polarity-only check (soundness of kind, not of degree): a correct-polarity auto over a compound that also requires the other polarity is not penalized here at atom granularity; it is penalized at M4/M5 case granularity and in the compound gates.

Failure class: SEMANTICALLY_UNSOUND. Count: semantically_unsound_accepted_proofs.

## M4. PROOF_SAFE_AUTO_CORRECTNESS

Case-level check. When the system predicts AUTO_SUPPORTED or AUTO_CONTRADICTED and the sealed proof-safe verdict does not allow that auto (proof-safe target is REVIEW_REQUIRED, INSUFFICIENT_EVIDENCE, or the opposite auto polarity), the auto is PROOF_SAFE_UNSOUND, regardless of structural_valid = true.

Failure class: PROOF_SAFE_UNSOUND. Count: proof_safe_unsound_autos.

## M5. PRODUCT_ACTION_CORRECTNESS

The final product action equals the sealed product_action target. Counted for autos as wrong_product_autos and for the full set as the product gate metric in evaluation-metrics.md.

## Hard soundness invariant (normative)

If the system predicts AUTO_SUPPORTED but the expected proof-safe verdict does not allow SUPPORTED-auto, the auto proof is PROOF_SAFE_UNSOUND regardless of structural_valid = true. Likewise AUTO_CONTRADICTED. Structural validity must never hide semantic/proof-safe unsoundness. Every preregistered soundness gate counts M1-M4 separately; no gate may substitute structural validity for soundness.

## Metric independence

M1-M5 are computed and reported separately. No composite may collapse them. In particular:

- invalid_proof counts (M1) say nothing about soundness (M3/M4)
- groundedness (M2) says nothing about conclusion validity (M3)
- auto precision is M4-based (case level), never M1-based

## Application

These definitions are authoritative for the RC3 generalization holdout (future G1/G2 scoring) and for any RC3-era diagnostic re-scoring. Historical RC2 official artifacts are not re-scored and remain immutable under their frozen policy.

