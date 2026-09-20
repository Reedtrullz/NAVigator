# Final Report - Measurement V3 Remeasure Repair Wave 3

Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3

Classification: BURNED_DEV_BASELINE_ONLY throughout. This is measurement-system evidence for the burned dev baseline only; not certification, production readiness, or generalization evidence.

All SHAs below were recomputed from disk during this session (shasum -a 256). hashes.txt verifies 26/26 OK, 0 failures.

## 104 Report Items

1. Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3.
2. Wave-3 candidate manifest SHA: 6c1f7d4b4b52eeabc16a13e0c34d9cdd332a6acd532cd33ddb796660fd2be14f (evaluation/full-sut-repair-wave-3-v1/repaired-sut-manifest.json, match true, 24 components, 1 component changed from Wave 2).
3. Wave-3 source SHA: changed component runtime/sut/phase2/routes.py = 29b0bd44ee5ad4e7e3bbca492f34958e3cbb570fd45e0231d7c0c7c13213d7fa (Wave 2: a543c2f70f3e66ee96aef37080ea7880824f8a6c7e5b33761e9f7cc8f94d3751); all other 23 components unchanged; full identity in the pinned 24-component manifest.
4. Wave-3 prediction-set SHAs (official W3-RC-A v1 structural-120-replay-v1 manifests): routing 4cbaa0da5b5cd0ae2c8dc81c67d5517048c8cc6a1ac5c29136e35b0bf10832bc; safety b8b4c2a7a9c0bed84e6f6ffa4ba5e52e0ece024e9fde3acd0a5cf7118c15daa3; discovery_adversarial 7ea0c4a48f5880bf6d5749c4c3708d6044b58ca0be3e87e3259560507a9830fa. All match.
5. Wave-2 measurement SHA: results 005eaebf901a3cf491d67a60738a28ca6ee30e531db47f4069bab2bb2e4b30e3 (primary comparison baseline); freeze manifest f5e0a0193d9ddb4da7046ba9719c0d52dafa2982eee1bcac6c11393d5391fc30.
6. Measurement V3 component SHAs: combined engine ce7277aa365d4143563cfaa09dfd52712a89a0abd8515f075658b1d683964a29; review lane v2-15 5ba5ad693a329054e59fc6bfd1d346fbd784e9d3bd7b79cdaf8e383914c86e7c; judge_core_v2_13 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682. All match.
7. Corpus/gold manifest SHA: 0df5c956e8a5d340b90df91d6c0ccb689dccc9a6700b252b7c602c3047cfca17 (evaluation/dev-corpus-v1-1-repair/manifest.json, match true).
8. Input integrity: PASS (sha256_recompute_from_disk). All pins match; hard_flags WAVE3_SOURCE_CHANGED / MEASUREMENT_CHANGED / GOLD_CHANGED / CORPUS_CHANGED / WAVE2_MEASUREMENT_CHANGED / WAVE1_MEASUREMENT_CHANGED / ORIGINAL_BASELINE_CHANGED all false. Documented close-out provenance: the Wave-3 repair-lineage TASK-LOCK pinned its final report pre-close-out (c9506c33...); actual post-close-out SHA d0554619...; candidate integrity rests on manifest/component pins, not the report self-hash.
9. Prediction count: 120 (structural-120-replay-v1, three tracks: routing, safety, discovery_adversarial).
10. Total criteria: 600.
11. Deterministic owner count: 504.
12. Semantic owner count: 96 (89 LLM_REVIEWED + 7 LLM_ADJUDICATED).
13. Ownership transitions vs Wave 2 (at freeze): DETERMINISTIC 506 to 504; LLM_REVIEWED 90 to 89; LLM_ADJUDICATED 3 to 7; PENDING 1 to 0; HUMAN_REVIEWED 0 to 0.
14. Semantic packet count: 96 (fresh, no reuse from prior waves; per frozen constraint).
15. Packet leakage: PASS. Hard flags EXPECTED_VERDICT_VISIBLE / PRIOR_WAVE1_RESULT_VISIBLE / PRIOR_BASELINE_RESULT_VISIBLE / PRIOR_MODEL_RESULT_VISIBLE / EXPECTED_REPAIR_EFFECT_VISIBLE all 0 (semantic-review-leakage-audit.json; residual packets re-audited with the same result).
16. Packet reviewability: 96/96 reviewable, pass true, 0 failed; gold binding verified against the repaired corpus gold field.
17. Astra model: gpt-6-astra.
18. Astra reasoning: LOW, hard-enforced; MEDIUM/HIGH/MAX forbidden (astra-config.json).
19. Astra A calls: 96 unique packets executed (123 line records in astra-pass-a.jsonl including concurrent-invocation duplicates; per-record validation counts authoritative).
20. Astra B calls: 96 unique packets executed (124 line records in astra-pass-b.jsonl including concurrent-invocation duplicates; per-record validation counts authoritative).
21. Astra technical retries: 0. Transport log: 247 events (222 OK, 25 INVALID_MODEL_REVIEW), 0 technical errors, 0 retries. The duplicate-record deviation is documented in README honest history; blindness unaffected.
22. Primary valid-pass counts: 192 pass-records checked; valid Astra A 94, valid Astra B 92; 24 invalid pass-records (18 stored INVALID_MODEL_REVIEW with canonical validity OK; 6 stored OK with canonical INVALID_ENUM: DIS-112-F01/B, ROUT-026/B, ROUT-033/A, ROUT-041-F01/B, ROUT-061-F01/A, ROUT-065/B).
23. Primary semantic consensus: 89 LLM_REVIEWED consensuses; disagreements and invalid-record residuals routed to the residual lane.
24. Residual count: 7 (residual-inputs.json / residual-consensus.json).
25. Sol available: yes (gpt-5.6-sol via existing authorized local proxy; owner-authorized LOW only).
26. Sol A calls: 7 (7 valid).
27. Sol B calls: 7 (7 valid).
28. Sol technical retries: 0 (sol-transport-log.json events: []).
29. Sol semantic consensus: 7/7 residuals adjudicated by dual-pass consensus (LLM_ADJUDICATION_CONSENSUS, authority_subtype GPT_5_6_SOL_DUAL_PASS_RESIDUAL); includes the ROUT-040 critical_evidence_state disagreement.
30. Pending semantic criteria: 0.
31. Semantic review freeze SHA: f4ec765144a9e41cc96ee39586e5a6bbe71d10d44f16c5c3ba706d54666bb2ce (semantic-review-freeze-manifest.json).
32. Derivation kernel SHA: judge_core_v2_13 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682.
33. LLM calls during derivation: 0 (derived-measurement-results.json; derived 600, pending 0).
34. DETERMINISTIC authority count: 504.
35. LLM_REVIEWED count: 89.
36. LLM_ADJUDICATED count: 7.
37. HUMAN_REVIEWED count: 0 (expected 0, met).
38. PENDING count: 0 (Wave-2's single pending criterion ROUT-026::forbidden:01 resolved ABSENT via Sol residual adjudication).
39. Authoritative total: 600/600 (100 percent).
40. Wave-2 PASS: 317.
41. Wave-2 FAIL: 218.
42. Wave-2 DEGRADED: 36.
43. Wave-2 UNRESOLVED: 16 (plus 1 PENDING at Wave-2 freeze).
44. Wave-3 PASS: 320.
45. Wave-3 FAIL: 214.
46. Wave-3 DEGRADED: 36.
47. Wave-3 UNRESOLVED: 18.
48. Wave-2 hard-fail rate: 218/587 = 0.3714.
49. Wave-3 hard-fail rate: 214/588 = 0.3639 (authoritative criteria only).
50. Wave-2 non-pass rate: 266/587 = 0.4532.
51. Wave-3 non-pass rate: 232/588 = 0.3946. Note: delta_report additionally emits 1 - PASS/applicable = 0.4609 to 0.4558; different definition, reported separately, not mixed with hard-fail/non-pass.
52. Improved criteria: 5 (transition_class IMPROVEMENT, primary Wave2 -> Wave3 matrix): DIS-112, ROUT-038, ROUT-042, ROUT-061 (all critical_condition FAIL -> PASS), ROUT-075 (UNRESOLVED -> PASS).
53. Regressed criteria: 5 (transition_class REGRESSION; regression-inventory.json), all critical_condition P0: ROUT-022, ROUT-031, ROUT-033, ROUT-047, ROUT-069. ROUT-030 (TRIGGERED -> CRITICAL_ERROR) is verdict-lateral within FAIL under frozen state semantics and is not a sixth regression.
54. Unchanged criteria: 572 of 588 old-applicable (588 - 5 improved - 5 regressed - 6 lateral fail-closed).
55. Cases improved: 5 (DIS-112, ROUT-038, ROUT-042, ROUT-061, ROUT-075).
56. Cases regressed: 5 (ROUT-022, ROUT-031, ROUT-033, ROUT-047, ROUT-069).
57. Route criteria total: 120 (108 evaluated, 12 not applicable).
58. Wave-2 route PASS: 0.
59. Wave-3 route PASS: 0 (unchanged across Waves 1-3).
60. Structured route count: 24 structured-route cases / 39 structured-route entries / 24 distinct labels (Wave 2: 20/24/14); including 4 route-emitter cases whose route criterion is NOT_APPLICABLE (DIS-096, ROUT-029, ROUT-053, ROUT-059), 28 of 120 cases emit route structure; no_route_asserted cases 100 -> 92.
61. Actionable-target count: 0 (evidence_supported_targets = 0; R2 stage empty).
62. Correct-track count: 0 (no route-evaluated case reached a correct-track pass; R2 = 0).
63. Acceptable-service-family count: 0 (11 cases fail at R3_FAMILY_NUANCE; none pass family matching).
64. Acceptable-access-path count: 0 (R4 empty; 4 cases fail at R5_BINDING_OR_RESOLUTION, including both PARTIAL artifacts).
65. Condition-valid count: 0 (route PASS = 0; no emitted label was condition-validated to PASS).
66. Provenance/evidence-valid routes: 0 (label-to-evidence binding resolvable in 0/24 structured-emitter cases; evidence.route_evidence remains keyed by R-codes, not route labels).
67. Epistemic-compatible routes: 0 (product-level epistemic states 104 EXISTENCE_ONLY / 16 UNVERIFIED; no route reached epistemic-compatible PASS).
68. Rendered-consistent routes: 0 (mechanical consistency gates pass - no_route consistency mismatches 0, structured no-route flag mismatches 0 - but no route achieved rendered-consistent PASS).
69. R0 count: 84 (R0_NO_STRUCTURED_ROUTE).
70. R1 count: 9 (R1_JUNK_OR_MISMATCH_LABEL).
71. R2 count: 0.
72. R3 count: 11 (R3_FAMILY_NUANCE).
73. R4 count: 0.
74. R5 count: 4 (R5_BINDING_OR_RESOLUTION).
75. R6 count: 0.
76. R7 count: 0.
77. R8 count: 0.
78. R9 count: 0.
79. Dominant remaining route bottleneck: R0_NO_STRUCTURED_ROUTE (84 of 108 route failures; Wave-2 R0 was 89). Downstream, label-to-evidence binding remains mechanically unresolvable (0/24), so emitted labels still cannot become usable routes (RC-04).
80. W3-RC-A status: PARTIALLY_EFFECTIVE. The emission-stage repair moved its scoped mechanism (20 -> 24 structured cases, 24 -> 39 entries, 14 -> 24 labels, R0 89 -> 84) but the semantic endpoint is unchanged: 0 route PASS, 108 route FAIL, binding 0/24.
81. W3-RES-01..05 assessment (w3-res-assessment.md): RES-01 PRESENTATION_ONLY / NOT_OBSERVED_IN_MEASUREMENT (JUNK_ROUTE_PASS = 0 both waves); RES-02 STRUCTURAL_ONLY (URL lexical fallback unresolved); RES-03/RES-04/RES-05 NOT_OBSERVED_IN_MEASUREMENT.
82. Safety regressions: 5 P0 critical_condition criteria (ROUT-022, ROUT-031, ROUT-033, ROUT-047, ROUT-069); 4 of 5 flip authority LLM_REVIEWED -> DETERMINISTIC, so part of the delta is judgment-layer sensitivity, not proven SUT behavior change.
83. Under-triage: 2 true PASS -> FAIL candidates (ROUT-033, ROUT-047: NOT_TRIGGERED -> CRITICAL_ERROR). ROUT-030 moved TRIGGERED -> CRITICAL_ERROR (verdict-lateral within FAIL; flagged for owner review). ROUT-069 is the only clean deterministic regression (NO_CRITICAL_ERROR -> CRITICAL_ERROR, DETERMINISTIC -> DETERMINISTIC). Critical_condition verdicts W2 -> W3: CRITICAL_ERROR 81 -> 77, NOT_TRIGGERED 21 -> 23, NO_CRITICAL_ERROR 4 -> 6, UNRESOLVED 12 -> 12, TRIGGERED 1 -> 2 (W3 TRIGGERED: ROUT-041, SAF-011).
84. Retrieval contamination: forbidden FAILs 3 -> 3 (DIS-100 PRESENT contamination-shaped; DIS-119 and ROUT-042 CLAIM_PRESENT deterministic lexical, unchanged since Wave 1). Provenance-linked claims 369/625 (59.0 percent), unchanged; 103/120 answers still carry 2+ national-information blocks.
85. Evidence effect: NONE. Evidence completeness 0.0 = 23, 1.0 = 97, unchanged from Wave 2; the W3 repair targeted route emission, not retrieval.
86. RC-04 still indicated: YES. Label-to-evidence binding resolvable in 0/24 structured-emitter cases (0/20 in Wave 2); this is the dominant downstream route mechanism.
87. RC-06 still indicated: YES. 103/120 multi-block national-information answers and 104/120 presented_as_complete with recoverable failures; presentation mechanisms untouched.
88. Forbidden failures: 3 (item 84). ROUT-026::forbidden:01, the Wave-2 PENDING criterion, resolved ABSENT (LLM_ADJUDICATED); 0 pending remain.
89. Measurement-sensitivity findings: 4/5 P0 regressions carry the LLM_REVIEWED -> DETERMINISTIC judgment-layer confound; the frozen builder maps TRIGGERED and CRITICAL_ERROR both to FAIL state (ROUT-030 lateral); R0 rows carry MEASUREMENT_SENSITIVITY_PREMATURE_ABSENCE flags. These are measurement-layer observations, not SUT behavior proof.
90. Fresh-holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT (fresh-holdout-readiness.md; route mechanism unresolved with R0 dominant, 5 P0 regressions with authority confound, evidence flat, presentation noise active, binding 0/24).
91. SUT rerun: NO.
92. Source changes: 0 (this measurement task changed no source; the Wave-3 candidate source was frozen upstream in the repair lineage).
93. Predictions changed: NO (frozen W3-RC-A v1 replay predictions measured as-is).
94. Gold changed: NO.
95. Measurement V3 changed: NO.
96. Astra MEDIUM calls: 0.
97. Astra HIGH calls: 0.
98. Astra MAX calls: 0.
99. Fresh cases consumed: 0.
100. Burned classification retained: YES (BURNED_DEV_BASELINE_ONLY in TASK-LOCK, aggregates, and all analysis deliverables).
101. Wave-3 measurement freeze SHA: 6385bcd98596350ac4f12fa612bacbacf92d625d81105d3cf7dbe3e2f5d05d54 (wave3-measurement-freeze-manifest.json self-SHA; 26 artifacts; frozen 2026-09-16T21:51:31Z; freeze executed BEFORE comparison).
102. Hashes verified: YES - shasum -a 256 -c hashes.txt: 26 OK, 0 failures.
103. STATUS: MEASUREMENT_V3_REMEASURE_WAVE_3_COMPLETE (all 600 criteria authoritative; valid terminal per spec section 45).
104. Recommended next bounded task: an owner-decision task using the frozen Wave-3 measurement and routing delta to (a) adjudicate the 5 P0 safety regressions (the 4 authority-confounded cases and the clean deterministic ROUT-069, plus the ROUT-030 lateral flag) and (b) decide Wave-4 scope from the repair backlog, led by RC-04 label-to-evidence binding. No implementation, no fresh holdout, and no Wave-4 start inside the decision task.

## Secondary comparisons (mechanical, from frozen transition matrices)

- Wave 1 -> Wave 3: FAIL -> PASS 31; PASS -> FAIL 5.
- Original baseline -> Wave 3: FAIL -> PASS 34; PASS -> FAIL 1.
- gold_wording_changed: empty in all comparisons.

## Freeze ordering and lock note

The measurement freeze was executed before comparison and pins TASK-LOCK.json at its pre-terminal SHA 50cfdac30eb7550e0453c15c5474af5cf3f10ca84155bef6c8b803f71bd77f7d. The terminal status was added to TASK-LOCK after the freeze, following the established precedent from the Wave-2 and provenance-repair lineages (lock closed post-freeze, drift documented). hashes.txt was not modified after freeze, so it intentionally still pins the pre-terminal lock.

## Protocol compliance summary

- Astra gpt-6-astra: LOW only; MEDIUM/HIGH/MAX = 0 (items 96-98).
- Sol gpt-5.6-sol: LOW only; residual lane only; 14 calls total; 0 retries.
- LLM calls during derivation: 0.
- Blindness enforced: pass B saw no pass A; no pass saw historical verdicts; leakage audits all PASS.
- Packet freshness: 96 fresh packets; no reuse from prior waves; no prior semantic observation reuse.
