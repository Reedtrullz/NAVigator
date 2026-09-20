# SLUTTRAPPORT - PHASE 1, NAV-EXPLORE-RC1-BLIND-RECERT-PHASE1

1. Task lock: NAV-EXPLORE-RC1-BLIND-RECERT-PHASE1 (COMPLETED, phase PREDICTION_BEFORE_KEY).
2. RC1 before-run hashes: 17/17 OK (sha256sum -c release-candidate/hashes.txt).
3. RC1 manifest SHA-256: 5cb6c5a5ec80bfe719bc67ae00b884e90f85293cb8e9fc3a1559322e2578fe86.
4. Blind-set SHA-256 (blind-cases.json): a3a4dd60bc8662dd77581696809be6f68e93aeddf136ebad6f828cd4b52e7a39.
5. Sealed-answer SHA-256 (answer-key.sealed): f5e453950649a3b934f52f6d2d84cf2e7e93cbdd9edcbabc0c501006905406ff.
6. CORE count expected: 120.
7. CORE outcomes recorded: 120.
8. Missing: 0.
9. Extra: 0.
10. Duplicates: 0.
11. Runtime successes: 119.
12. Runtime failures: 1 (RC1B-0112: AttributeError inside frozen quote-aligner polarity_engine.py line 474, 'set' object has no attribute 'values'; recorded per spec 9, never reconstructed or retried, runtime untouched).
13. Deterministic-only count: 17.
14. Reviewer-used count: 103 (openai/gpt-5.6-luna, temperature 0, local OpenCodex proxy).
15. Total model calls: 103.
16. Retry count: 0.
17. Token usage: not emitted by RC1's frozen components; unavailable (reported honestly per spec 25).
18. Runtime: 510.8 s wall clock.
19. Product prediction distribution: AUTO_SUPPORTED 29, AUTO_CONTRADICTED 46, REVIEW_REQUIRED 9, ABSTAIN_INSUFFICIENT 35, none 1 (runtime failure).
20. Semantic prediction distribution: SUPPORTED 29, CONTRADICTED 46, PARTIALLY_SUPPORTED 9, INSUFFICIENT_EVIDENCE 12, REVIEW_REQUIRED 23, none 1.
21. Proof-safe prediction distribution: SUPPORTED 19, CONTRADICTED 30, INSUFFICIENT_EVIDENCE 35, REVIEW_REQUIRED 35, none 1.
22. Proof-valid count (internal): 16 auto gate passes; per-case proof_valid recorded in the artifact.
23. Invalid internal proof count: not emitted by RC1; fidelity failures surface as review routes in the artifact.
24. REVIEW_REQUIRED count: 9 (product_action) plus 35 proof-safe review holds and 23 semantic review outcomes; full per-case detail in the artifact.
25. Reserve cases executed: RESERVE_EXECUTED = 0.
26. Prediction file path: evaluation/semantic-judge/blind-recertification/RC1-run/RC1-predictions.json (read-only).
27. Prediction SHA-256: 0178f086b1e376c9a6f7f9bfaa67befd59507607fd12b1b4bbe502ade207f7b1.
28. Raw-results SHA: not applicable (raw intermediates embedded in the prediction artifact; the prediction SHA is authoritative).
29. Prediction hash stable? PREDICTION_HASH_STABLE = TRUE (re-verified after all QA).
30. RC1 hashes after run: 17/17 OK.
31. Blind-set hashes after run: unchanged (blind-cases, answer-key.sealed, blind-manifest).
32. Answer key accessed? NO.
33. Blind key available? NO.
34. Scoring performed? NO (prediction-only distributions; no comparison to any expected distribution).
35. Tuning performed? NO.
36. Runtime modified? NO (driver is an external adapter; one import-path fix occurred before any prediction ran and is documented).
37. QA: prediction schema + 120-ID completeness + duplicate check PASS; post-run hashes PASS; KB regression 48/48; evaluator regression acc 1.00, FP=0, safety_FP=0 (no blind cases used); key-access scan NONE; score-artifact scan CLEAN.
38. PHASE1 STATUS: PREDICTIONS_FROZEN_BEFORE_KEY.
39. Next action: user sends BLIND_RC1_KEY in a new, separate message to start Phase 2 (key must never be pasted into a certification prompt).
