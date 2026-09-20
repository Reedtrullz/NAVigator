# FINAL REPORT - NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1

Terminal status: NO_LOW_COST_MODEL_QUALIFIES (screening-stage elimination; valid experimental outcome per spec section 28).

## 1. Stage chronology

1. Reference corpus built from frozen Wave-4 quota-safe lineage (387 unique canonical inputs; Tier-A 375, Tier-B 12; 25 excluded; 0 reference conflicts; forbidden 250 / critical 137).
2. Benchmark frozen (md5 stratified bucket rule): forbidden SCREEN 53 / EDGE 31 / CORE 116 / STABILITY 27 / TRANSPORT 13; critical SCREEN 37 / EDGE 42 / CORE 38 / STABILITY 12 / TRANSPORT 6.
3. Transport calibration run for 5 candidates; inkling permanently excluded (HTTP 403 route-restricted to agentic harnesses, 19/19 rows, not recoverable by policy).
4. Candidate config frozen (5 entries; inkling marked TRANSPORT_NOT_VERIFIED_ROUTE_RESTRICTED; 4 active candidates).
5. Stage-1 blind screening executed, one pass per candidate, 90 rows each (53 forbidden + 37 critical).
6. Bounded single recovery pass for transient transport errors only (timeout/502/429), executed per frozen policy; 402/503 not in frozen transient enumeration and not retried; INVALID_JSON / INVALID_MODEL_REVIEW never retried ("invalid remains invalid").
7. Screening outputs frozen, then scored with score_screening.py against frozen gates.
8. No candidate passed the frozen screening gates. Stage 2 (dual pass) and Stage 3 (stability) were NOT started because spec section 24 restricts them to surviving candidates. Terminal status issued.

## 2. Report (56-point list)

1. Task ID: NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1.
2. Wave-4 semantic reference freeze SHA: 30abe921d5d79a49e2827aa6da8c80cb1d5214646062434d376928d279a54fab (TASK-LOCK upstream_freeze).
3. Historical semantic-review freezes used: W3, W2, B1, W4, W1 (see reference-provenance.json; preferred order documented).
4. Unique reference input count: 387.
5. Tier-A count: 375.
6. Tier-B count: 12.
7. Excluded count: 25 (4 KNOWN_MEASUREMENT_SENSITIVITY, 14 CRITERION_DEFECT_REPAIRED, 7 NO_FROZEN_OBSERVATION).
8. Reference conflict count: 0.
9. Forbidden reference count: 250.
10. Critical reference count: 137.
11. Split sizes: forbidden SCREEN 53 / EDGE 31 / CORE 116 / STABILITY 27 / TRANSPORT 13; critical SCREEN 37 / EDGE 42 / CORE 38 / STABILITY 12 / TRANSPORT 6.
12. Qualification gates frozen before calls: YES (qualification-contract.json frozen before screening calls; gates_allowed_error_counts never modified after outputs were observed).
13. Approved model inventory loaded: YES (candidate-inventory.json).
14. Primary candidates: nemotron-3-ultra, nex-n2.5-pro, gemma-4-31b-it, mimo-v2.5-pro, inkling.
15. Reserve candidates used: NONE (no reserve pool was defined or consumed).
16. Actual provider routes selected: see candidate-configs.json (frozen wire_ids; RouteOpen/nemotron-3-ultra-550b-a55b, openrouter/nex-agi/nex-n2.5-pro:free, openrouter/google/gemma-4-31b-it:free, command-code/xiaomi/mimo-v2.5-pro; inkling openrouter/thinkingmachines/inkling:free failed transport permanently).
17. Candidates tested: 5 (4 semantic screening, inkling transport-only).
18. Candidates reaching full qualification: 0 (Stage 2 not started; no screening survivors).
19. New Astra calls: 0.
20. New Sol calls: 0.
21. Per-candidate transport validity: nemotron 5/90 OK after recovery (54 recovery attempts recovered 0); nex 48/90 OK after recovery (9/13 recovered); gemma 16/90 OK after recovery (3/75 recovered); mimo 32/90 OK (0 transport errors; 21 unparseable JSON); inkling 0/19 transport rows, permanent 403.
22. Per-candidate operational viability: nemotron NOT VIABLE (chronic 429 + 30x HTTP 402 credit exhaustion); nex PARTIALLY VIABLE (episodic timeouts); gemma NOT VIABLE (chronic 429); mimo NOT VIABLE at screening due to invalid-output dominance (0 transport errors); inkling NOT VIABLE (route restricted).
23. Quota status per candidate: UNKNOWN_NOT_EXPOSED_BY_PROVIDER for all (no provider quota metadata exposed; 402 on nemotron documents credit exhaustion on RouteOpen).
24. Per-candidate schema validity (frozen gate schema_valid_rate_min = 1.0): nemotron 0.1132 forbidden / 0.0 critical; nex 0.9811 / 0.9189; gemma 0.2075 / 0.1622; mimo 0.6981 / 0.8649. ALL FAIL.
25. Forbidden agreement (among valid reviews): nemotron 1.0 (n=5); nex 0.7222 (n=18); gemma 1.0 (n=10); mimo 1.0 (n=14). Small-n; not qualification evidence.
26. Critical agreement (among valid reviews): nemotron n=0; nex 0.7333 (n=30); gemma 0.5 (n=6); mimo 0.6111 (n=18). Small-n; not qualification evidence.
27. Edge-set agreement: NOT_RUN_STAGE_STOPPED_AT_SCREENING.
28. Dual-pass consistency: NOT_RUN_STAGE_STOPPED_AT_SCREENING.
29. Evidence validity: enforced per row during screening (INVALID_MODEL_REVIEW includes evidence failures; see disagreement-analysis.json for per-reason counts).
30. Stability: NOT_RUN_STAGE_STOPPED_AT_SCREENING.
31. Systematic disagreement families (among valid reviews, field-level): nex forbidden NO_MATCH->MATCH over-claims (5) and commitment over-reading UNRESOLVED->NEGATED/ASSERTED (5); nex critical AMBIGUOUS_OR_CONFLICTING over-resolution (6) and CLEAR_NON_TRIGGER_SUPPORT->INSUFFICIENT_TO_DECIDE (2); mimo critical critical_evidence_state instability in both directions (7 field disagreements among 18 valid); gemma critical over-hedging INSUFFICIENT_TO_DECIDE (2) and one AMBIGUOUS->CLEAR_TRIGGER over-resolution.
32. High-severity disagreements: mimo critical CLEAR_TRIGGER_SUPPORT->CLEAR_NON_TRIGGER_SUPPORT (under-escalation direction) 1 row; mimo CLEAR_TRIGGER_SUPPORT->INSUFFICIENT_TO_DECIDE 1 row. Counted as semantic observations among valid rows only; candidate already eliminated by screening gates.
33. Forbidden lane qualification: NONE.
34. Critical lane qualification: NONE.
35. Qualified candidates: NONE.
36. Unqualified near-misses: nex-n2.5-pro (semantically strongest; eliminated by invalid-model-review rate 34+4 and residual timeouts, not by gate reinterpretation).
37. No-best-of-bad invariant preserved: YES (spec section 28 applied literally; near-miss not advanced).
38. Calls per candidate (attempts incl. screening + recovery + transport calibration rows where recorded): nemotron 5 + 84 screening failures + 108 recovery attempts + 15 transport OK/1 err; nex 90 screening rows (13 timeouts) + 26 recovery attempts + 12 transport OK/2 err; gemma 90 rows (73 failures) + 150 recovery attempts + 9 transport OK/10 err; mimo 90 rows all attempted (no transport retries); inkling 19 transport probes. All frozen in result JSONL/JSON artifacts.
39. Input/output tokens (observed OK rows only): nemotron 18214/3365; nex 175312/52491; gemma 49513/1415; mimo 123069/68063; inkling 0/0.
40. Latency (median OK row): nemotron 29.1s; nex 22.8s (p90 59.4s); gemma 11.9s (p90 15.9s); mimo 46.0s (p90 70.8s).
41. Authoritative pricing available: NO for all routes.
42. Observed cost: UNKNOWN_NO_PRICING_DATA for all.
43. Tier-1 resolution percent: NOT_COMPUTED (router activation outside this task).
44. Astra escalation percent: NOT_COMPUTED.
45. Projected Astra calls / 100: NOT_COMPUTED.
46. Projected Sol residuals / 100: NOT_COMPUTED.
47. Strong-model calls avoided / 100: NOT_COMPUTED.
48. Proposed forbidden router: NOT ISSUED (no qualified candidate).
49. Proposed critical router: NOT ISSUED (no qualified candidate).
50. Historical measurements mutated: NO.
51. Semantic standards changed: NO (screening scorer fixed twice to honor frozen artifacts/spec: diagnostic-row guard and authoritative-fields-only comparison; both are harness corrections, not gate/threshold changes).
52. SUT changed: NO.
53. Gold changed: NO.
54. Fresh cases consumed: 0.
55. STATUS: NO_LOW_COST_MODEL_QUALIFIES.
56. Exact next activation task: NONE authorized. Options for owner: (a) new explicitly authorized screening attempt with different routes/quota windows for the strongest near-miss (nex-n2.5-pro) under unchanged gates and a NEW frozen benchmark lineage if inputs would be burned; or (b) stay on the Astra review lane until a route with sustainable quota is owner-approved. This task consumed no fresh cases and remains reusable evidence.

## 3. Failure-mode summary (generalized)

- Chronic provider rate limiting (429) and credit exhaustion (402) made two candidates operationally non-viable despite acceptable semantic behavior on the few rows that completed (nemotron/gemma small-n agreement 1.0 among valid rows).
- nex-n2.5-pro was transport-tolerable and semantically the strongest, but produced 38/90 invalid model reviews (mostly enum violations in forbidden lane) and would additionally fail overall agreement gates. It is a documented near-miss, not a survivor.
- mimo-v2.5-pro had zero transport failures but dominant output-format weakness (21 unparseable JSON + 35 invalid model reviews) and critical-lane semantic instability including one under-escalation-direction error among valid rows.
- inkling is route-restricted (403) and permanently excluded.

## 4. Integrity notes

- input-integrity.json: all upstream pins verified except 4 expected TASK-LOCK status flips (documented reason EXPECTED_TASK_LOCK_STATUS_FLIP; review artifacts unaffected).
- Screening recovery pass: screening-recovery-results.json preserves per-row attempt history; original error records retained.
- Scoring only after outputs were frozen; comparator corrections were applied before interpreting results and are restricted to matching the frozen spec (section 26) and frozen reference artifact shape.

## 5. Deliverables produced vs intentionally absent

Produced: TASK-LOCK.json, README.md, input-integrity.json, reference-corpus.jsonl, reference-provenance.json, reference-exclusions.json, reference-conflicts.json, qualification-split.json, qualification-contract.json, candidate-inventory.json, candidate-configs.json, benchmark-freeze-manifest.json, transport-freeze-manifest.json, transport-screen-results.json (+ per-candidate transport progress JSONL and recovery artifacts), screening-results.json (+ per-candidate progress JSONL), screening-recovery-results.json, screening-scored.json, disagreement-analysis.json, quota-operational-analysis.json, cost-analysis.json, hashes.txt, final-report.md, plus all runner/scorer scripts.

Intentionally absent (stages never started because zero candidates survived screening; fabricating them would be a protocol violation): full-qualification-results.json, stability-results.json, lane-qualification-results.json, cascade-simulation.json, proposed-review-router.json, shadow-replay-results.json. The spec's deliverable list assumes Stage-2 survivors; the terminal outcome is documented in TASK-LOCK.json and this report instead.
