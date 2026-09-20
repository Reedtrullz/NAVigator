# CERTIFICATION REPORT - NAV-EXPLORE-RC1-BLIND-RECERT-PHASE2

Blind recertification of evaluator RC1 (semantic-judge v0.4.1 stack: quote-aligner v0.2 deterministic engine, tier1 operators, reviewer v1.1 gpt-5.6-luna, fusion + auto_gate v0.1) on blind set NAV-EXPLORE-RC1-BLIND-V1 core (N = 120). Predictions were frozen in Phase 1 before key decryption; scoring used the pre-hashed policy RC1-PHASE2-SCORING-POLICY-V1.

1. Task lock: evaluation/semantic-judge/blind-recertification/RC1-run/phase2/TASK-LOCK.json (ACTIVE during run; status set COMPLETED at close). No runtime/prediction/label changes allowed.
2. Phase-1 prediction SHA verified: 0178f086b1e376c9a6f7f9bfaa67befd59507607fd12b1b4bbe502ade207f7b1 (re-verified at Phase-2 open and close).
3. RC1 hashes before: 17/17 OK (sha256sum -c release-candidate/hashes.txt, re-run in Phase 2: 17 OK).
4. Blind-set hashes before: blind-cases.json a3a4dd60bc8662dd77581696809be6f68e93aeddf136ebad6f828cd4b52e7a39; answer-key.sealed f5e453950649a3b934f52f6d2d84cf2e7e93cbdd9edcbabc0c501006905406ff; blind-manifest 466ab575b3e286bd946d12483bc10949505ab3b09d2d8fc2fa4c6a61694e26fa.
5. Key authentication/decryption: AES-256-GCM, associated data = SHA-256 of exact blind-cases.json bytes; authenticated decrypt OK; 187 entries (120 core + 67 reserve), all annotation_status CONFIRMED.
6. Key persisted? NO. Decrypted in memory only; scoring done in-process; no plaintext key file exists under evaluation/ (scan: 0 matches for key material; raw-key helper temp file deleted at cleanup).
7. Answer-key CORE count: 120.
8. ID equality: prediction IDs == blind-core IDs == key-core IDs (120 unique; 0 missing, 0 extra, 0 duplicates). Six retired candidate IDs absent by construction.
9. Runtime-failure policy: conservative default. RC1B-0112 (AttributeError, quote-aligner polarity_engine.py:474) scored incorrect on all three targets, not an accepted proof, recorded RUNTIME_FAILURE; no reconstruction, no retry.
10. Scoring-policy SHA-256: 06be45636aed2b22d62e8c5595bad572c320f64a6485bf6f882ab4f4db02a44f (hashed before any label comparison).
11. Semantic correct/N: 79/120.
12. Semantic accuracy: 65.83% (Wilson 95% CI 56.97-73.71%).
13. Semantic threshold >= 0.90: FAIL.
14. Proof-safe correct/N: 44/120.
15. Proof-safe accuracy: 36.67% (Wilson 95% CI 28.58-45.58%).
16. Proof-safe threshold >= 0.95: FAIL.
17. Product correct/N: 79/120.
18. Product accuracy: 65.83% (Wilson 95% CI 56.97-73.71%).
19. Product threshold >= 0.95: FAIL.
20. AUTO_SUPPORTED precision (proof-based): 29/29 = 100%.
21. AUTO_CONTRADICTED precision (proof-based): 41/46 = 89.13%.
22. Combined auto precision (proof-based): 70/75 = 93.33% vs threshold >= 0.99: FAIL.
23. Accepted proofs: 84 (all re-derived exactly equal under JSON-normalized comparison; scorer correction documented in official-score.json).
24. Invalid accepted proofs: 0 (PASS).
25. Hallucinated proofs: 0 (PASS).
26. Critical unsafe AUTO_SUPPORTED: 0 (PASS).
27. Critical unsafe AUTO_CONTRADICTED: 2 (RC1B-0122, RC1B-0131) - HARD-GATE FAIL.
28. REVIEW_REQUIRED metrics: predicted 9 / expected 12; TP 5, unnecessary 4, missed 7; precision 0.556, recall 0.417.
29. ABSTAIN metrics: predicted 35 / expected 5; correct 4, over-abstention 31, under-abstention 1.
30. Safety subgroup (n=3, exploratory): semantic 1/3, proof-safe 0/3, product 1/3.
31. Legal subgroup (n=31): semantic 16/31 (51.6%), proof-safe 12/31 (38.7%), product 16/31 (51.6%).
32. Numeric subgroup (n=79): semantic 49/79 (62.0%), proof-safe 28/79 (35.4%), product 49/79 (62.0%).
33. Temporal subgroup (n=47): semantic 29/47 (61.7%), proof-safe 18/47 (38.3%), product 29/47 (61.7%).
34. Locality subgroup (n=27): semantic 19/27 (70.4%), proof-safe 7/27 (25.9%), product 19/27 (70.4%).
35. Modality subgroup (n=74): semantic 46/74 (62.2%), proof-safe 28/74 (37.8%), product 46/74 (62.2%).
36. Actor subgroup (n=40): semantic 30/40 (75.0%), proof-safe 12/40 (30.0%), product 30/40 (75.0%).
37. Condition/exception subgroup (n=22, keyword-heuristic, exploratory): semantic 16/22 (72.7%), proof-safe 9/22 (40.9%), product 16/22 (72.7%).
38. Compound subgroup (n=80): semantic 50/80 (62.5%), proof-safe 27/80 (33.8%), product 49/80 (61.25%); atom-level 22/45 = 48.9% on 21 alignable compound cases.
39. Multi-span subgroup (n=58): semantic 31/58 (53.4%), proof-safe 17/58 (29.3%), product 31/58 (53.4%). Genuine-insufficiency subgroup (n=7, exploratory): semantic 4/7, proof-safe 6/7, product 4/7.
40. Runtime failure RC1B-0112 impact: if excluded, semantic 66.39%, proof-safe 36.97%, product 66.39%, critical product wrong 22; all thresholds still fail (rc1b-0112-impact.json).
41. Official-score SHA-256: fff9b539b97d414389fbc6198d1ecbc92f546556bbc7374fdbbfa29d5ef93d72.
42. Official score frozen before error audit? YES (official-score-freeze.json).
43. Critical error count: 3 critical-tier (2 critical unsafe AUTO_CONTRADICTED + 1 runtime failure).
44. High errors: 20 (remaining critical-subset product misses).
45. Medium errors: 12 (10 over-abstention, 2 unnecessary review) plus 6 other product errors classified separately; low 41 (40 proof-safe-only, 1 semantic-only). Full 82-row table: error-analysis.md.
46. Potential blind-label issues: 2 strong candidates (RC1B-0116, RC1B-0165), 1 borderline (RC1B-0143); 2 audited cases attributed to evaluator, not labels (label-audit.md).
47. Audited alternate score: NOT computed. Even if both strong candidates flipped to PARTIALLY_SUPPORTED, semantic/product = 81/120 (67.5%), critical product 39/60; all thresholds still fail; verdict unchanged.
48. Deterministic-only count: 17.
49. Reviewer calls: 103 (gpt-5.6-luna, temperature 0; 0 retries).
50. LLM calls per 100 cases: 85.8.
51. Review/auto coverage: product auto 75/120 (62.5%), review 9/120 (7.5%), abstain 35/120 (29.17%), runtime-none 1.
52. Reserve used: 0 (MUST 0 - PASS). 67 reserve cases untouched.
53. Prediction SHA after: 0178f086b1e376c9a6f7f9bfaa67befd59507607fd12b1b4bbe502ade207f7b1 (unchanged; file mode 444).
54. RC1 hashes after: 17/17 OK.
55. Blind-set hashes after: unchanged (blind-cases, answer-key.sealed, blind-manifest).
56. Plaintext leakage: key material 0 matches under evaluation/; phase2 deliverables contain no per-case key labels; only rc1b-0112-impact.json discloses RC1B-0112 expected labels (required by spec item 40); decrypted key temp file deleted; no unresolved disputes (PASS1_CONFIRMED / PASS2_CONFIRMED / RESOLVED_NEW only).
57. QA: ID equality re-verified; predictions/freeze permissions 444 verified; scorer-correction audit (tuple-vs-list JSON artifact) re-derived all 84 accepted proofs exactly equal; QA scans clean; /tmp scorer artifacts deleted.
58. CERTIFICATION VERDICT: RC1_NOT_CERTIFIED.
59. Gates passed: invalid_accepted_proofs_zero; critical_unsafe_auto_supported_zero; hallucinated_proofs_zero; valid_accepted_proofs_100 (proof-audit 84/84); reserve_unused_zero.
60. Gates failed: semantic_ge_090 (65.83%); proof_safe_ge_095 (36.67%); product_ge_095 (65.83%); critical_product_100 (61.67%); critical_unsafe_auto_contradicted_zero (2 cases); critical_unsafe_auto_rate_zero; auto_proof_precision_ge_099 (93.33%).
61. Viktigste generaliseringsfunn: (a) deterministiske falske CONTRADICTED er hard-gate-lasende - to regex-defekter (aldersparser tolker "§ 4-3" og FOR-id som alder; tallsammenligning kolliderer fulle/halverte satser i samme rad) produserer usikre AUTO_CONTRADICTED som anmelderen ikke kan overstyre; (b) proof-safe er systematisk for lav (36.7%) fordi reviewer/PARTIAL-bandet 0.78-0.84 ligger under fusionsterskelen 0.90 for numeriske claims, med over-cautious INSUFFICIENT og support_span_not_entailing i tillegg; (c) over-abstention (31/35) dominerer produktfeilene; (d) atom-segmentering (48.9% atom-treff) begrenser kompositt-noyaktighet.
62. Low-N insufficiency caveat: safety n=3, genuine-insufficiency n=7, standard-tier n=4 - exploratory only, not generalizable.
63. Condition/exception quota caveat: subgroup uses keyword heuristic and deviates from construction quota (N=19 documented in scoring policy); treated as exploratory.
64. RC2 bug candidates: B1 age-parser citation false positives; B2 numeric cross-amount conflicts; B3 fusion threshold vs PARTIAL band; B4 support_span_not_entailing too strict for paraphrase; B5 proof-present abstention floor; B6 reviewer INSUFFICIENT over-confidence (0.93-0.98 on provable claims); B7 polarity_engine.py:474 crash guard; B8 atom segmentation. Details and fix suggestions: error-analysis.md.
65. Evaluator R&D boer gjenapnes: YES. RC1 fails 7 of 10 gates; failure modes are concentrated in two deterministic engine defects plus fusion calibration - addressable without protocol changes.
66. Anbefalt neste steg: fix B1+B2 in quote-aligner v0.3 with targeted regression tests (RC1B-0122/0131/0005/0086 patterns), recalibrate B3/B6 thresholds on the calibration set (not blind set), add B7 crash guard, then owner decides RC2 on a fresh blind run. No RC2 was started; RC1 is not patched.

Prohibited actions honored: no RC1 patching, no blind reruns, no reserve use, no KB changes, no label edits, no alternate score substitution.
