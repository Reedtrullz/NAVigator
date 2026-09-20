# FINAL REPORT — NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V2

Terminal status: **NO_LOW_COST_MODEL_QUALIFIES_V2**

## 1-7. Identity, lineage, candidates

1. Task ID: NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V2
2. V1 lineage: hashes.txt sha256 7446dd00392ace38345d18f29bc154332e71da9db3fed60e3400580ae2465c2a; benchmark-freeze-manifest sha256 b22856abcaa5fd77d9fa6dc474ebbb613dbf4d36391b99e5a01a7bca99dcc9a3
3. V1 qualification contract SHA: a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f
4. Reference corpus unchanged: YES (9/9 pins re-verified MATCH after screening)
5. Qualification gates unchanged: YES (V1 contract used in place; no threshold mutation)
6. Reserve candidates tested: 5 logical (R1-R5)
7. Actual provider routes:
   - R1 nemotron-3-super: NO ROUTE (absent from proxy catalog; HTTP_400 both forms) — not substitutable with nemotron-3-ultra without silent escalation
   - R2 laguna-s-2.1: command-code/poolside/laguna-s-2.1-free
   - R3 ling-3.0-flash-sante: command-code/inclusionai/ling-3.0-flash-sante:free
   - R4 gemma-4-26b-a4b-it: openrouter/google/gemma-4-26b-a4b-it:free
   - R5 inkling-small: openrouter/thinkingmachines/inkling-small:free

## 8-12. Nex, viability, screening

8. Nex recheck authorized/executed: NO (NEX_RECHECK_NOT_AUTHORIZED; spec section 5 semantic-dominance rule)
9. Nex V1 invalid root cause: 30 SEMANTIC_CONTRACT_VIOLATION_NULL_ENUM (speaker_commitment=null) + 8 EVIDENCE_RULE_VIOLATION; 0 transport/serialization. Semantic/evidence violations dominate 38/38.
10. Transport-valid candidates: R2 (10/19 + recovery; 3 residual TERR), R3 (7/19 + 13 recaptured fenced JSON; 0 residual transport errors)
11. Operationally viable candidates: R2 PROVISIONAL (intermittent 502s, recovered on single retry), R3 transport-sound in calibration BUT 48 HTTP_429 events during screening (24 rows unresolved in critical lane). R1 not testable (no route), R4 chronic 429 (38 events/19 rows), R5 hard 403 (19/19).
12. Screening survivors: **NONE**

## 13-17. Qualification results

13. Full qualification candidates: NONE (Stage 2 dual pass not started; spec restricts Stage 2+ to survivors)
14. Forbidden lane qualification: NONE (gate: schema_valid_rate_min 1.0; R2 0.8302, R3 0.9623)
15. Critical lane qualification: NONE (R2 0.8919, R3 0.3514)
16. Stability result: NOT RUN (no Stage-2 qualifiers)
17. Dangerous critical errors: R2 4 catastrophic escapes (ref CLEAR_NON_TRIGGER_SUPPORT -> candidate CLEAR_TRIGGER_SUPPORT, over-escalation direction) within the max-7 gate but alongside failing schema gate; R3 0 escapes. Neither reaches semantic qualification regardless.

## 18-20. Failure families, quota, cost

18. Systematic semantic failure families (screening-scored-v2.json + disagreement-analysis.json):
    - R2: low reference agreement among valid rows (forbidden 0.5333, critical 0.4000), 14+8 INVALID_MODEL_REVIEW (evidence/schema/enum), 2+4 INVALID_JSON, 7 forbidden-lane transport errors, 6 critical-lane INVALID_JSON.
    - R3: forbidden lane close on transport (0.9623 schema rate) but 20 INVALID_MODEL_REVIEW (enum/evidence) and agreement only 0.4839; critical lane collapsed operationally (24/37 HTTP_429) with valid-row agreement 0.8333 (n=6, small n).
19. Quota/rate-limit findings: R2 0 x 429/402 but 27 x 5xx events; R3 48 x 429 events during screening; R4 chronic 429; R5 permanent 403; R1 route absent. No candidate demonstrates sustainable Tier-1 capacity.
20. Cost/token findings (screening only): R2 355,409 tokens (329,369 prompt / 26,040 completion), mean latency 5.74s, p50 4.5s, p95 10.5s; R3 373,203 tokens (250,774 prompt / 122,429 completion), mean 8.12s, p50 6.1s, p95 19.4s. Quota status UNKNOWN; command-code free routes, no priced billing observed. No cost figures invented.

## 21-30. Selection and router

21. Qualified models: NONE
22. Near-misses: NONE within gates. R3 forbidden lane (0.9623 schema rate, 0 escapes) is the closest lane result but still fails the hard schema_valid_rate_min = 1.0 gate and has agreement 0.4839 among valid rows. No best-of-bad selection performed.
23. No-best-of-bad preserved: YES
24. Projected Tier-1 resolution: NOT ISSUED (no qualified model)
25. Projected Astra escalation: NOT ISSUED
26. Projected Astra calls / 100: NOT ISSUED
27. Projected Sol residuals / 100: NOT ISSUED
28. Strong-model calls avoided / 100: NOT ISSUED
29. Proposed forbidden router: NOT ISSUED (section 18: only qualified models may appear as Tier-1)
30. Proposed critical router: NOT ISSUED

## 31-38. Compliance

31. New Astra calls: 0 (MUST 0) - PASS
32. New Sol calls: 0 (MUST 0) - PASS
33. V1 artifacts mutated: NO
34. Historical measurements mutated: NO
35. SUT changed: NO
36. Gold changed: NO
37. Fresh cases consumed: 0 (frozen V1 partitions reused exactly; SCREEN 53+37 rows)
38. STATUS: **NO_LOW_COST_MODEL_QUALIFIES_V2**

## 39. Recommended next owner task

No automatic continuation. Options for owner:

- (a) Keep GPT-6 Astra LOW as the standing semantic-review authority (status quo) and stop low-cost replacement attempts;
- (b) Cost strategy per spec section 19: deterministic ownership where contractually valid, exact-review reuse when reviewer input is identical, batching/caching;
- (c) Future requalification ONLY as a new explicitly authorized lineage when new models/routes with demonstrated quota stability become available. R2's 5xx instability and R3's 429 rate make both unsuitable targets for prompt-level rescue under unchanged gates.

## Intentionally absent artifacts

full-qualification-results.json, stability-results.json, lane-qualification-results.json, cascade-simulation.json, proposed-review-router.json and shadow-replay-results.json were NOT created because zero candidates survived screening and spec sections 13/15/17/18 restrict those stages to qualifiers. Fabricating placeholder artifacts would violate the protocol (same treatment as V1 terminal report).

## Artifact integrity

All V2 artifacts are hashed in hashes.txt (28 files incl. this report). Transport-stage pins remain in transport-freeze-manifest.json. Screening outputs frozen in semantic-screen-results.json before scoring; scoring frozen in screening-scored-v2.json.
