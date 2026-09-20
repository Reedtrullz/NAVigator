# Final Report - RC2 Blind V3 Construction (SLUTTRAPPORT)

Set: NAV-EXPLORE-RC2-BLIND-V3. Task: NAV-EXPLORE-RC2-BLIND-V3-CONSTRUCTION. Date: 2026-09-04. RC1 remains RC1_NOT_CERTIFIED (official frozen historical result); this set certifies nothing by itself - it is the sealed instrument for the future RC2 certification run.

| # | Item | Value |
|---|---|---|
| 1 | Task lock | TASK-LOCK.json, created 2026-09-04, status COMPLETED; rc2_execution_allowed=false |
| 2 | V2 immutable verification | blind-cases.json SHA 0c62f093a71f1b0f719284f8b2d3d47f4155f2fbb700356a9b7865b4e8e0afbf and answer-key.sealed SHA 0232ce94afcf516957408f7bfea44775aa3eb266dcd3843105b5139fced87406 both match V2 blind-manifest.json (re-verified this session); no V2 file modified |
| 3 | V2 eligibility status | SEALED_BUT_NOT_ELIGIBLE_FOR_CERTIFICATION - burned development data; V3 is the certification set |
| 4 | V2 quota-root-cause | qa_check.sh asserted all quotas against pool_aggregates (n=277), never CORE; selection routed all 40 INSUFFICIENT to reserve; CORE held 0 INSUFFICIENT, 0 ABSTAIN, multi-span 18. Full analysis: v2-selection-qa-root-cause.md |
| 5 | V2 annotation-root-cause | agreement gate warning-only (CORE 0.7799/0.6232/0.7645 vs 0.90 target; manifest gate_met=false but QA asserted only remaining_disputes==0); adjudication (73.6% of pool) used to force agreement instead of failing construction; single-pass RC2B-0277 passed silently |
| 6 | Construction-QA fixes | construction_qa.py fail-closed and CORE-only: semantic floors, insufficiency, product minima, 11 flag minima, agreement 3x, double-annotation, adjudication rate, unresolved disputes, fidelity, novelty, leak scan, RC2 hash gate; pool counts informational only; exit 0 only if all pass |
| 7 | QA regression tests | qa-tests/test_construction_qa.py: all 7 spec-43 scenarios + CLI failure/success checks PASS (run this session) |
| 8 | Annotation pilot N | 32 |
| 9 | Pilot semantic agreement | 0.9688 (round 3; round 1 was 0.9062) |
| 10 | Pilot proof agreement | 0.9688 (round 3; round 1 was 0.7188) |
| 11 | Pilot product agreement | 0.9688 (round 3; round 1 was 0.7188) |
| 12 | Annotation contract ready | YES - ANNOTATION_CONTRACT_READY after round 3 with four round-2 amendments incorporated |
| 13 | V3 candidates total | 282 |
| 14 | Reused unseen V2 candidates | 277 (V2_REUSED_UNSEEN_BY_RC2; spec 15; RC2 never executed on V2 - verified) |
| 15 | Newly authored candidates | 5 (V3_SPEC17_NEW gap-wave RC2B-0278..0282; authorized by spec 17 because pool had only 23 ABSTAIN < 25 CORE minimum) |
| 16 | Full double-annotated count | 282/282, zero single-pass exceptions (spec 26) |
| 17 | Eligible confirmed pool | 282 with final labels (259 pass-agreed + 23 adjudicated; 0 unresolved) |
| 18 | CORE N | 160 (minimum 140) |
| 19 | Reserve N | 122 |
| 20 | CORE semantic distribution | SUPPORTED 40 / CONTRADICTED 40 / PARTIALLY_SUPPORTED 40 / INSUFFICIENT_EVIDENCE 40 |
| 21 | CORE proof-safe distribution | SUPPORTED 40 / CONTRADICTED 40 / INSUFFICIENT_EVIDENCE 26 / REVIEW_REQUIRED 54 |
| 22 | CORE product distribution | AUTO_SUPPORTED 40 / AUTO_CONTRADICTED 40 / ABSTAIN_INSUFFICIENT 26 / REVIEW_REQUIRED 54 |
| 23 | Genuine insufficiency | 40 (minimum 30) |
| 24 | Condition/exception | 42 (minimum 30) |
| 25 | Compound | 62 (minimum 50) |
| 26 | Multi-span | 31 (minimum 30) |
| 27 | Numeric | 92 (minimum 30) |
| 28 | Age/legal adversarial | 20 (minimum 20) |
| 29 | Temporal | 82 (minimum 30) |
| 30 | Actor | 99 (minimum 30) |
| 31 | Modality | 132 (minimum 30) |
| 32 | Safety | 20 (minimum 20) |
| 33 | Legal | 89 (minimum 30) |
| 34 | Locality | 38 (minimum 20) |
| 35 | CORE semantic pre-adjudication agreement | 0.9500 |
| 36 | CORE proof pre-adjudication agreement | 0.9375 |
| 37 | CORE product pre-adjudication agreement | 0.9375 |
| 38 | Operator agreement | Not separately measured (spec 28 requires separate reporting; no hard gate, audit trigger below 0.80). Disclosed as a coverage gap in certification-metrics.md; not backfilled or inferred |
| 39 | CORE adjudication count/rate | 10/160 = 6.25% (hard maximum 35%); pool-wide 23/282 |
| 40 | Unresolved disputes | 0 (adjudicate.py is fail-closed: any unresolved label dispute aborts with exit 1) |
| 41 | Fidelity | 282/282 pass, 0 failures (verbatim excerpts) |
| 42 | Novelty | 282/282 retained, 0 rejected (exact/near/skeleton all 0) |
| 43 | Max similarity | 0.5385 (threshold 0.55) |
| 44 | Blind-cases SHA | ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d |
| 45 | Sealed-key SHA | 45323257f325cca82bc80167ff09cda4da1d93ff441445fcd604cfbb71e2aeb9 |
| 46 | AES/AAD verification | AES-256-GCM; roundtrip OK at seal; independent decrypt re-verified this session with the owner key: 160 entries, exact match to CORE selection, 10 adjudicated entries, all three label slots present. AAD bytes = UTF-8 of the blind-cases SHA-256 hex string; envelope associated_data = urlsafe-b64 of the raw 32-byte digest (manifest description corrected to match) |
| 47 | Key persisted? | NO - memory-only, delivered once in the construction final message (and once in this construction's closing user message); never written to disk, repo, Obsidian, or reports |
| 48 | Plaintext label leaks | 0 in public blind artifacts (token + row-level scan over candidates-*.json, blind-cases.json, selection.json), matching the V2 qa_check.sh precedent scope; label-bearing construction evidence retained under construction/ and disclosed in README.md |
| 49 | RC2 hash before | 11/11 OK (rc2-hashes-before.txt; verified before construction and re-verified this session) |
| 50 | RC2 hash after | 11/11 OK (re-verified after seal this session) |
| 51 | RC2 executed? | NO (rc2_executed_on_blind_set=false; no predictions produced; no scoring occurred) |
| 52 | Certification thresholds | Pre-registered UNCHANGED before seal (certification-metrics.md; spec 39 list verbatim; spec 40 no post-seal changes) |
| 53 | Construction hard gates | ALL PASS (construction_qa.py exit 0; gate table in construction-qa-report.md) |
| 54 | All hard gates pass? | YES |
| 55 | STATUS | SEALED_AND_READY |
| 56 | Exact blockers | none |
| 57 | Recommended next step | Phase 1 keyless run: verify RC2 hashes, execute CORE only, freeze predictions + SHA, stop. Phase 2 scoring only after the user supplies the V3 key (future-certification-protocol.md) |

## Deviations and honest coverage notes

1. Spec-17 gap wave (5 new cases) was required because the reused pool held 23 ABSTAIN cases against the 25 CORE minimum; documented in items 15 and 22.
2. Operator agreement (item 38) was not separately measured; disclosed, not inferred.
3. Sealed-key atom rows exist for the 10 adjudicated CORE cases; pass-agreed and single-atom cases carry the triple + flags only. Compound-atom and criticality metrics interpretation is constrained accordingly (certification-metrics.md coverage disclosure).
4. Novelty prior-art scope: V2-blind corpus applied only to V2_REUSED_UNSEEN_BY_RC2 candidates (spec 29 + spec 15 rationale; RC2 execution on V2 verified absent). Checker path bug fixed during construction; deterministic, on disk.
5. Label-bearing construction evidence is retained under construction/ (plaintext labels exist there by design as construction evidence); the public blind artifact surface is label-free and the sealed key is canonical. Any future stricter cleanup must weigh evidence loss against spec 36's public-artifact scope.
