# G2 LABEL AUDIT (post-freeze, spec 35-36)

Status: POTENTIAL_GENERALIZATION_LABEL_ERROR registered count = 0. No relabel. Official score preserved byte-for-byte.

## Method

Four deterministic internal-consistency detectors ran over every sealed label (g2_error_analysis.py):

1. SUPPORT_TRUTH_BUT_ABSTAIN_PRODUCT: semantic and proof-safe truth in {SUPPORTED, PARTIALLY_SUPPORTED} while product truth is ABSTAIN_INSUFFICIENT.
2. INSUFFICIENT_TRUTH_BUT_AUTO_PRODUCT: semantic truth INSUFFICIENT_EVIDENCE while product truth is AUTO_SUPPORTED or AUTO_CONTRADICTED.
3. GENUINE_INSUFFICIENCY_NOT_ABSTAIN: genuine_insufficiency flag true while product truth is not ABSTAIN_INSUFFICIENT.
4. PRODUCT_PROOF_SAFE_POLARITY_MISMATCH: product truth polarity contradicts proof-safe truth polarity.

Result: no case triggered any detector.

## Annotation provenance

Adjudication status distribution in the sealed key: 140 PASS1_PASS2_AGREE, 9 ADJUDICATED_P2, 6 ADJUDICATED_P1, 4 ADJUDICATED_ATOM. All 159 labels carry an annotation rationale; atoms carry required_inference tags.

Construction audit access (spec 37): the sealed construction-audit.sealed was decrypted once during scoring, before official freeze, solely to derive preregistered critical-case membership (25 critical cases; the public audit material strips criticality by design). No annotation content was modified and no score rewrite occurred. No post-freeze audit access was needed because no label-error candidates emerged.

## Alternate sensitivity (spec 36)

With zero registered candidates, sensitivity scores equal the official scores:

- Product exact: 60/159 (37.74 percent), unchanged.
- Auto precision excluding candidate cases: 10/24 (41.67 percent), unchanged.

## Limitation

The detectors test internal consistency of the label set, not the correctness of each label against the underlying KB sources. External re-verification of all 159 sealed labels was not performed in this task and remains possible for a future audit without touching this run.
