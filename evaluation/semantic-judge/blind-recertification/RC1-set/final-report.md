# SLUTTRAPPORT - NAV-EXPLORE-RC1-BLIND-SET-CONSTRUCTION

1. Task lock: NAV-EXPLORE-RC1-BLIND-SET-CONSTRUCTION, active throughout, flipped to COMPLETED at end of task.
2. RC1 manifest verification: sha256sum -c release-candidate/hashes.txt, all OK.
3. RC1 manifest SHA-256 before and after: 5cb6c5a5ec80bfe719bc67ae00b884e90f85293cb8e9fc3a1559322e2578fe86 (unchanged).
4. Blind-set version: NAV-EXPLORE-RC1-BLIND-V1 (created 2026-09-03).
5. Candidates generated: 193 (waves 1-3: 167; wave 4: 26).
6. Exact duplicates rejected: 0.
7. Near duplicates rejected: 2 (RC1B-0076, RC1B-0146).
8. Source-skeleton duplicates rejected: 4 (RC1B-0091, RC1B-0095, RC1B-0100, RC1B-0123).
9. Source-fidelity rejects: 0 (193 checks, all verbatim excerpts pass).
10. Annotation disputes: 7.
11. Candidates excluded for other reasons: 0.
12. CORE count: 120.
13. Reserve count: 67.
14. Semantic class distribution (core): SUPPORTED 51, CONTRADICTED 52, PARTIAL 10, INSUFFICIENT 7.
15. Product-action class distribution (core): AUTO_SUPPORTED 51, AUTO_CONTRADICTED 52, REVIEW_REQUIRED 12, ABSTAIN_INSUFFICIENT 5.
16. Domain distribution (core, multi-counted per case): familieokonomi 29, familie_barnevern 23, juridisk_prosess 18, bolig_okonomi 16, lokalt_trondheim 14, skole 11, voksen_akutt 6, barn_psykisk_helse 4.
17. Safety-critical count (core): 18.
18. Legal-critical count (core): 31.
19. Numeric/temporal count (core): numeric 67, temporal 104.
20. Locality count (core): 22.
21. Atomic count (core): 38.
22. Compound count (core): 82 (pool-wide compound ratio exceeded the 40-50 target; actual reported per spec).
23. Pass-1/pass-2 semantic agreement: 182/187 = 0.9733 (kappa 0.9531).
24. Proof-safe agreement: 183/187 = 0.9786 (kappa 0.9622).
25. Product-action agreement: 180/187 = 0.9626 (kappa 0.9343).
26. Operator agreement (all three targets equal per case): 180/187 = 0.9626.
27. Adjudication count: 7 (3 pass-1 confirmed, 2 pass-2 confirmed, 2 resolved with new labels).
28. Remaining disputes in CORE: 0.
29. Source fidelity result: all pass; whitespace-only canon-normalization; deliberate ASCII orthography and the literal file-49 typo preserved.
30. Novelty result: all retained cases pass pre-registered gates.
31. Maximum similarity retained: 0.5385 (waves 1-3); wave 4 max 0.2941.
32. blind-cases SHA-256: a3a4dd60bc8662dd77581696809be6f68e93aeddf136ebad6f828cd4b52e7a39.
33. Answer-key ciphertext SHA-256: f5e453950649a3b934f52f6d2d84cf2e7e93cbdd9edcbabc0c501006905406ff.
34. Encryption algorithm: AES-256-GCM (Python cryptography, 32-byte key from secrets.token_bytes, 12-byte nonce).
35. Associated-data hash: SHA-256 of exact blind-cases.json bytes (a3a4dd60...e7a39).
36. Encryption round-trip verified in memory: YES (decrypt with same key + associated data reproduced the plaintext key bytes exactly).
37. Plaintext leakage scan: label-field scan over blind-recertification tree returns only aggregate-count keys and schema/metric documentation; per-case labels exist only inside the sealed envelope. Annotation pass files, the selector's adjudication overrides, and compiled bytecode were deleted.
38. Key written to disk: NO.
39. Key written to Obsidian: NO.
40. RC1 executed on blind set: NO.
41. RC1 unchanged: YES.
42. Pre-registered hard gates: invalid accepted proofs 0; critical unsafe AUTO_SUPPORTED 0; critical unsafe AUTO_CONTRADICTED 0; hallucinated proof/evidence 0.
43. Semantic threshold: at least 90 percent exact accuracy (cannot override proof-safety failure).
44. Proof-safe threshold: at least 95 percent exact accuracy.
45. Product-action threshold: at least 95 percent exact accuracy; critical subgroup 100 percent.
46. Pre-registered subgroups: safety-critical, legal/rights-critical, numeric, temporal, locality, modality, actor, condition/exception, compound, genuine insufficiency.
47. Prediction-freeze protocol: two-phase firewall in future-certification-protocol.md; predictions frozen and hashed before any key access.
48. Answer-key release protocol: key returned once in the construction task's final message as BLIND_RC1_KEY; user supplies it only as a separate message after predictions are frozen.
49. QA: manual schema checks PASS (187 cases, 120 core, 67 reserve, exact case structure, selection consistency); scripts/qa_check.sh does not exist in this tree, structural checks were run directly instead. RC1 hash check re-run after construction: all OK.
50. BLIND SET STATUS: SEALED_AND_READY.
51. Blocker: none.
52. Recommended next step: Phase 1 certification (RC1 prediction run on blind-cases.json, hash RC1 first, freeze predictions, request the key as a separate message).

## Addendum: section 11 difficulty coverage (actual counts, CORE)

| Dimension | Count |
|---|---|
| modality / legal force | 63 |
| actor / role | 57 |
| locality / scope | 24 |
| numeric / amounts | 67 |
| temporal / dates | 102 |
| negation / polarity | 41 |
| condition / exception | 19 (keyword heuristic; borderline to the 20 floor) |
| multi-span entailment | 82 (compound cases) |
| compound claims | 82 |
| genuine insufficiency | 7 (pool ceiling: only 7 INSUFFICIENT_EVIDENCE cases in the full 187-case pool) |

Two dimensions fall below the section 11 minimum of 20: genuine insufficiency
(7) is limited by the annotated pool itself; condition / exception is borderline
at 19. Per section 8 and 43, the sealed set is not edited; actual distributions
are documented here. Section 16 compound target (40-50) is exceeded (82) and
reported as actual per spec.
