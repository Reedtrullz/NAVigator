# V2 Construction Audit - NAV-EXPLORE-RC2-BLIND-V2

Date: 2026-09-04
Auditor: NAV-EXPLORE-RC2-BLIND-V3-CONSTRUCTION task
V2 status: **SEALED_BUT_NOT_ELIGIBLE_FOR_CERTIFICATION**

V2 is NOT COMPROMISED: RC2 never executed against the set (manifest rc2_status NOT_RUN, no prediction artifacts). V2 is NOT SEALED_AND_READY: construction gates failed. V2 must never be used as the official RC2 blind certification CORE. V2 remains immutable; this audit is an external artifact.

## 1. Immutability verification (performed 2026-09-04)

| Item | Value | Result |
|---|---|---|
| blind-cases.json SHA-256 | 0c62f093a71f1b0f719284f8b2d3d47f4155f2fbb700356a9b7865b4e8e0afbf | OK |
| answer-key.sealed SHA-256 | 0232ce94afcf516957408f7bfea44775aa3eb266dcd3843105b5139fced87406 | OK |
| blind-manifest.json SHA-256 | 1215f0d2978d80cf383f921155933f19f85f259279d04136ad00fd9f81d559cc (recorded inside manifest as RC2 manifest ref; manifest itself verified via qa_check consistency) | OK |
| RC2 hash gate (rc2-hashes-before.txt) | 11 files (engine, fusion, reviewer, auto_gate, lexicons) | ALL_OK, re-verified this session |
| RC2 executed on blind set | false (manifest) + no prediction artifacts | OK |

## 2. Concrete gate failures

### 2.1 Semantic CORE balance - FAIL

Required: approximately balanced classes, INSUFFICIENT >= 30.

| Class | CORE actual |
|---|---|
| SUPPORTED | 94 |
| CONTRADICTED | 41 |
| PARTIALLY_SUPPORTED | 25 |
| INSUFFICIENT_EVIDENCE | 0 |

All 40 genuine INSUFFICIENT cases existed in the pool but the firewall CORE selection placed every one in reserve. CORE contains 0 genuine insufficiency against a hard minimum of 30.

### 2.2 Product-action CORE coverage - FAIL

Required: >= 25 per class, no class = 0.

| Action | CORE actual |
|---|---|
| AUTO_SUPPORTED | 94 |
| AUTO_CONTRADICTED | 41 |
| REVIEW_REQUIRED | 25 |
| ABSTAIN_INSUFFICIENT | 0 |

ABSTAIN_INSUFFICIENT = 0 mirrors the semantic INSUFFICIENT failure (same cases, same selection bug).

### 2.3 Multi-span CORE - FAIL

44 multi-span cases flagged pool-wide; only 18 CORE cases expose >= 2 evidence spans in the public packets. Required >= 30.

### 2.4 Annotation agreement - FAIL

Target: >= 0.90 raw pre-adjudication on all three targets.

| Measure | Pool (n=276) | CORE (n=159) |
|---|---|---|
| semantic_raw | 0.7645 | 0.7799 |
| proof_safe_raw | 0.6232 | 0.7799 |
| product_raw | 0.7645 | 0.7799 |
| all_three_joint | 0.7572 | - |
| kappa (CORE) | - | ~0.59 all three |

Manifest records gate_met: false. 203 of 276 cases required adjudication (73.6% of pool; 47/160 = 29.4% of CORE) - far above the healthy range and a symptom of contract ambiguity, not just noise.

### 2.5 Annotation completeness - FAIL

RC2B-0277 received a single annotation pass (added after pass 2 closed). Spec required full two-pass completeness; agreement was computed on n=276.

## 3. Why QA reported ALL_QUOTAS_PASS

Full mechanism in [RC2-V3-set/v2-selection-qa-root-cause.md](RC2-V3-set/v2-selection-qa-root-cause.md). Summary:

1. qa_check.sh section 5 asserted quota flags against pool_aggregates (n=277), never against core_class_distributions (n=160). The failing numbers were published in the same manifest it read.
2. CORE selection ran before/independent of quota enforcement; quota validation was never re-run on the selected CORE.
3. The agreement gate (gate_met: false) was recorded but not enforced as a blocker; qa_check.sh only asserted remaining_disputes == 0 (a post-adjudication number).
4. Double-annotation completeness was never checked (RC2B-0277 single pass passed QA).

## 4. Annotation root cause (from recovered pass1/pass2 disagreement data)

V2's annotation-pass2.json and adjudication artifacts were plaintext-scrubbed post-seal per spec 44. The disagreement data was recovered from the construction-session thread DB and re-derived for this audit: 97 round-1 semantic disputes and 106 round-2 full-triple disputes.

### 4.1 Round-1 semantic transitions (P1 -> P2), 97 disputes

| Transition | Count |
|---|---|
| CONTRADICTED -> SUPPORTED | 29 |
| SUPPORTED -> CONTRADICTED | 27 |
| PARTIALLY_SUPPORTED -> CONTRADICTED | 13 |
| PARTIALLY_SUPPORTED -> INSUFFICIENT_EVIDENCE | 8 |
| INSUFFICIENT_EVIDENCE -> CONTRADICTED | 7 |
| PARTIALLY_SUPPORTED -> SUPPORTED | 5 |
| INSUFFICIENT_EVIDENCE -> SUPPORTED | 4 |
| all other pairs | 4 (1 each) |

### 4.2 Round-2 slot transitions, 106 disputes

proof_safe (104 disagreements, only 2 agreements among disputed rows):

| Transition | Count | Reading |
|---|---|---|
| INSUFFICIENT_EVIDENCE -> INSUFFICIENT | 33 | pure label-vocabulary mismatch - contract bug, not disagreement |
| CONTRADICTED <-> SUPPORTED | 36 (18 + 18) | contradiction-proof obligation inconsistently applied |
| REVIEW_REQUIRED -> CONTRADICTED / SUPPORTED | 21 (15 + 6) | REVIEW used as safety abstain, other pass resolved the case |
| INSUFFICIENT_EVIDENCE -> CONTRADICTED | 6 | absence-vs-contradiction boundary |
| other | 4 | - |

semantic_truth (64 disagreements): SUPPORTED <-> CONTRADICTED 35, PARTIAL -> {C,S,I} 24, INSUFFICIENT -> C 3.

product_action (65 disagreements): AUTO_SUPPORTED <-> AUTO_CONTRADICTED 34, REVIEW_REQUIRED -> {AUTO_C, AUTO_S, ABSTAIN} 26, ABSTAIN -> {AUTO_C, REVIEW} 4.

### 4.3 Root-cause classification (spec 7 taxonomy)

| Category | Evidence | Approx count |
|---|---|---|
| ANNOTATOR_INSTRUCTION_AMBIGUITY | proof_safe vocabulary split (INSUFFICIENT vs INSUFFICIENT_EVIDENCE) - two passes used different label sets | 33 |
| ABSENCE_VS_CONTRADICTION + unapplied contradiction-proof obligation | SUPPORTED <-> CONTRADICTED flips across all slots; near-symmetric, so no single-pass bias - the pass-2 instruction to document a positive conflict span was applied unevenly | 56 (r1 sem) + 36 (r2 proof) |
| PARTIAL_AGGREGATION | PARTIALLY_SUPPORTED used as catch-all uncertainty rather than compound aggregation; flips out of PARTIAL dominate its transitions | 26 (r1) + 24 (r2 sem) |
| REVIEW_VS_ABSTAIN | REVIEW_REQUIRED on proof/product treated as both "cannot prove" and "needs human"; no decision rule separated INSUFFICIENT (abstain) from REVIEW (route to human) | 21 + 5 |

### 4.4 Conclusion

The low agreement was NOT pure annotator noise. Four fixable contract defects account for the bulk of disputes: a label-vocabulary mismatch (33 cases), an unoperationalized contradiction-proof requirement (~90 SUPPORTED/CONTRADICTED flips), PARTIAL as a catch-all (~50 cases), and an undefined INSUFFICIENT-vs-REVIEW boundary (~26 cases). These map directly to the V3 contract fixes: fixed label vocabulary, explicit contradiction-proof documentation (spec 10), PARTIAL restricted to compound aggregation (spec 12), and an explicit INSUFFICIENT-vs-REVIEW decision rule (spec 11).
