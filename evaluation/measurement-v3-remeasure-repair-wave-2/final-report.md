# Final Report - Measurement V3 Remeasure Repair Wave 2

Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2

Classification: BURNED_DEV_BASELINE_ONLY throughout. This is measurement-system evidence for the burned dev baseline only; not certification, production readiness, or generalization evidence.

All SHAs below were recomputed from disk during this session (shasum -a 256). hashes.txt verifies 26/26 OK, 0 failures.

## 99 Report Items

1. Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2.
2. Wave-2 candidate manifest SHA: 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e (evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json, match true, 24 components, 0 drift).
3. Wave-2 prediction SHAs (official Candidate-2 structural-120-replay-v2 manifests): routing 35be9666f47ff6ae1f85875185945957ec95401c8ffb4427a53f31eefd51cfd0; safety 71d65c5973aeda50530d8c256118ea6cb71d75b238eea393bbd842145052569d; discovery_adversarial 099c4aa9da36d04c101cb7b0c44097a7d46c9c3526679db36aa6460605e6dc2e. All match.
4. Candidate attempts: 2 of 2.
5. Candidate-1 superseded incident: status SUPERSEDED_HISTORICAL_NOT_MEASURED; 99/120 SUCCESS, 21 EXECUTION_FAILED fail-closed (verified claim value missing from answer); proven root cause: per-track evidence IDs restarted, producing duplicate evidence IDs across tracks; planner INFO dedup then removed second-track blocks; finalizer correctly failed closed. Engineering evidence only; enters scoring: false.
6. Measurement V3 component SHAs: combined engine ce7277aa365d4143563cfaa09dfd52712a89a0abd8515f075658b1d683964a29; review lane v2-15 5ba5ad693a329054e59fc6bfd1d346fbd784e9d3bd7b79cdaf8e383914c86e7c; judge_core_v2_13 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682. All match.
7. Corpus/gold manifest SHA: 0df5c956e8a5d340b90df91d6c0ccb689dccc9a6700b252b7c602c3047cfca17 (evaluation/dev-corpus-v1-1-repair/manifest.json, match true).
8. Wave-1 measurement freeze SHA: e6d91a813dbf69fa647b15e683638a69a14bb9870e8ffbf7da801fd0615e2abb; Wave-1 results SHA 4f407672bd6c63c545d67547ff99f07c2ce143d1a56fbf8ce9af085e8888fbb7 (verified against Wave-1 freeze manifest pin). Discrepancy note: the prior handoff and this TASK-LOCK upstream_pins cited 1f4aac89...e7c1, which does not exist on disk; the verified artifacts above are the only basis used.
9. Original baseline freeze SHA: 34d78dae25acb5c21a8b1e42be8a90be478be76f196b3271661718ff486e65c1; original baseline results SHA e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf. Match true.
10. Input integrity: PASS (sha256_recompute_from_disk). All pins match; hard_flags WAVE2_SOURCE_CHANGED / WAVE2_PREDICTIONS_CHANGED / MEASUREMENT_CHANGED / GOLD_CHANGED / CORPUS_CHANGED / WAVE1_MEASUREMENT_CHANGED / ORIGINAL_BASELINE_CHANGED all false.
11. Prediction count: 120 (structural-120-replay-v2, three tracks: routing, safety, discovery_adversarial).
12. Total criteria: 600.
13. Deterministic owner count: 506.
14. Semantic owner count: 93 (90 LLM_REVIEWED + 3 LLM_ADJUDICATED).
15. Ownership transitions vs Wave 1 (at freeze): DETERMINISTIC 508 to 506; LLM_REVIEWED 88 to 90; LLM_ADJUDICATED 0 to 3; PENDING 4 to 1; HUMAN_REVIEWED 0 to 0.
16. Semantic packet count: 94.
17. Packet leakage: PASS. Hard flags EXPECTED_VERDICT_VISIBLE / PRIOR_WAVE1_RESULT_VISIBLE / PRIOR_BASELINE_RESULT_VISIBLE / PRIOR_MODEL_RESULT_VISIBLE / EXPECTED_REPAIR_EFFECT_VISIBLE all 0 (semantic-review-leakage-audit.json). Residual packets re-audited before Sol adjudication with the same result.
18. Packet reviewability: 94/94 reviewable, pass true, 0 failed; gold binding verified by verbatim comparison against the repaired corpus gold field.
19. Astra model: gpt-6-astra.
20. Astra reasoning: LOW, hard-enforced; MEDIUM/HIGH/MAX forbidden (astra-config.json).
21. Astra A calls: 94 (astra-pass-a.jsonl lines).
22. Astra B calls: 94 (astra-pass-b.jsonl lines).
23. Astra technical retries: 0 (astra-transport-log.jsonl contains 0 events).
24. Primary valid-pass counts: 188 pass-records checked; valid Astra A 92, valid Astra B 93; 3 invalid pass-records (PKT-ESC-DIS-109 pass A; PKT-ESC-ROUT-022 passes A and B, stored INVALID_MODEL_REVIEW).
25. Primary semantic consensus: 90 LLM_REVIEWED consensuses; 1 disagreement routed to residual; 3 invalid-pass packets resolved via residual lane.
26. Residual count: 4 (residual-inputs.json / residual-consensus.json).
27. Sol available: yes (gpt-5.6-sol via existing authorized local proxy; owner-authorized LOW only).
28. Sol A calls: 4.
29. Sol B calls: 4.
30. Sol technical retries: 0 (sol-transport-log.json events: []).
31. Sol semantic consensus: 3 of 4 residuals adjudicated by dual-pass consensus (LLM_ADJUDICATION_CONSENSUS, authority_subtype GPT_5_6_SOL_DUAL_PASS_RESIDUAL).
32. Pending semantic criteria: 1 - ROUT-026::forbidden:01 (PENDING_LLM_ADJUDICATION; pending_reason: semantic disagreement; observation model gpt-5.6-sol LOW). Frozen spec forbids resampling.
33. Semantic review freeze SHA: ca0b710653b4f73c38e6a90cb90b4775d1aaf6e054986a678be3866218ef8ab2 (semantic-review-freeze-manifest.json).
34. Derivation kernel SHA: judge_core_v2_13 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682.
35. LLM calls during derivation: 0 (derived-measurement-results.json llm_calls_during_derivation = 0; derived 93, pending 1).
36. DETERMINISTIC authority count: 506.
37. LLM_REVIEWED count: 90.
38. LLM_ADJUDICATED count: 3.
39. HUMAN_REVIEWED count: 0 (expected 0, met).
40. PENDING count: 1.
41. Authoritative total: 599/600 (99.83 percent).
42. Wave-1 PASS: 287.
43. Wave-1 FAIL: 243.
44. Wave-1 UNRESOLVED: 18.
45. Wave-1 DEGRADED: 36 (plus 4 PENDING at Wave-1 freeze).
46. Wave-2 PASS: 317.
47. Wave-2 FAIL: 218.
48. Wave-2 UNRESOLVED: 16.
49. Wave-2 DEGRADED: 36 (plus 1 PENDING).
50. Wave-1 hard-fail rate: 243/588 = 0.4133.
51. Wave-2 hard-fail rate: 218/587 = 0.3714 (authoritative criteria only; pending excluded).
52. Wave-1 non-pass rate: 297/588 = 0.5051.
53. Wave-2 non-pass rate: 266/587 = 0.4532. Note: delta_report additionally emits old/new failure rate as 1 - PASS/applicable = 0.5119 to 0.46; different definition, reported separately, not mixed with hard-fail/non-pass.
54. Improved criteria: 31 (transition_class IMPROVEMENT), across 24 cases.
55. Regressed criteria: 9 (transition_class REGRESSION; regression-inventory.json): DIS-106, ROUT-026, ROUT-049, ROUT-057, ROUT-063, ROUT-065, ROUT-070, ROUT-088 (all critical_condition, P0), ROUT-091 (required_uncertainty, P2).
56. Unchanged criteria: 540 of 588 old-applicable (588 - 31 improved - 9 regressed - 8 lateral).
57. Cases improved: 24 (DIS-105, DIS-116, ROUT-033, ROUT-039, ROUT-050, ROUT-059, ROUT-079, ROUT-085, SAF-001 through SAF-020 subset; full list in transition matrix).
58. Cases regressed: 9 (DIS-106, ROUT-026, ROUT-049, ROUT-057, ROUT-063, ROUT-065, ROUT-070, ROUT-088, ROUT-091).
59. RC-08 mechanical effect: PARTIAL (MECHANICAL_CONTAMINATION_REDUCTION). Claims with contamination markers 645 to 625; provenance-linked claims 308/645 (47.8 percent) to 369/625 (59.0 percent); mechanical gates PASS; 103/120 answers still carry 2+ national-information blocks.
60. RC-08 semantic effect: concentrated in the forbidden lane - forbidden FAILs 5 to 3 with DIS-105 and DIS-116 resolved; verdict transitions include CLAIM_ABSENT_TAKEN to ABSENT 6 and ABSENT to CLAIM_ABSENT_TAKEN 14; 3 forbidden FAILs remain. Overall state movement PASS 287 to 317, FAIL 243 to 218.
61. Route criteria total: 120 (108 evaluated, 12 not applicable).
62. Route PASS: 0 (unchanged from Wave 1).
63. Route FAIL: 108.
64. Structured-route count: 20 structured-route cases / 24 structured-route entries.
65. Actionable-target count: 0 (evidence_supported_targets = 0; target_relevant_to_active_track_resolvable = 0).
66. Junk-route count: 15 junk-like route entries (of 24).
67. Fragment-like route count: 2 fragment-like route labels.
68. Acceptable-route-family matches: 0.
69. RC-07 semantic effect: the funnel bottleneck moved but is unresolved. Wave 1: 120 to 108 evaluated to 20 structured to 12 plausibly usable to 0 PASS. Wave 2: 20/20 cases have structurally valid provenance (gate PASS), but label-to-evidence mapping is unresolvable in 20/20 because route_evidence is keyed by R-codes, not route labels. Route PASS unchanged at 0.
70. Claim provenance: 369/625 = 59.0 percent provenance-linked (Wave 1: 308/645 = 47.8 percent).
71. Route provenance: provenance_valid_cases 20/20; cases_with_routes_but_no_provenance 0; however provenance validity does not make targets actionable (items 65 and 69).
72. Evidence measurement effect: evidence_completeness 0.0 count 38 to 23; 1.0 count 82 to 97; the only strictly non-negative dimension. Provenance is not correctness.
73. RC-10 status: positive effect, retained (evidence attachment improved); does not by itself resolve route correctness.
74. Safety-level result: CRITICAL_ERROR 91 to 81; NOT_TRIGGERED 10 to 21; NO_CRITICAL_ERROR 6 to 4; UNRESOLVED 12 to 12; TRIGGERED 1 to 2 (Wave-2 TRIGGERED: ROUT-030 and SAF-011, both LLM_REVIEWED; Wave-1 TRIGGERED: ROUT-050).
75. Safety-category result: critical_condition PASS 11 to 23, FAIL 91 to 81; frozen safety-priority distribution 19 acute/safety tracks vs 101 NON_ACUTE_ROUTINE; both TRIGGERED verdicts occur in safety-relevant tracks.
76. Over-triage: none recorded; the two Wave-2 TRIGGERED verdicts are positive critical-handling outcomes, not false alarms.
77. Under-triage: 2 P0 candidates from true PASS to FAIL in critical_condition: ROUT-026 (NOT_TRIGGERED W1 LLM_REVIEWED to CRITICAL_ERROR W2 DETERMINISTIC) and ROUT-088 (same pattern). Additionally 6 UNRESOLVED to FAIL conversions (DIS-106, ROUT-049, ROUT-057, ROUT-063, ROUT-065, ROUT-070) where W2 deterministic evidence rows carry PREMATURE_ABSENCE / SEMANTIC_JUDGE_STUB markers where W1 carried LLM_REVIEWED observations. The W1-vs-W2 delta is therefore partly scorer-judgment-layer sensitivity, not proven SUT behavior change; not decidable from frozen artifacts; requires owner review. ROUT-026::forbidden:01 is the single pending criterion and must not be resampled.
78. RC-11 status: positive aggregate effect (CRITICAL_ERROR down 10, NOT_TRIGGERED up 11, TRIGGERED up 1) but not proven safe to build on until the 2 P0 under-triage candidates are owner-adjudicated.
79. Forbidden FAIL count: 3 - DIS-100 (PRESENT), DIS-119 (CLAIM_PRESENT), ROUT-042 (CLAIM_PRESENT); deterministic lexical for the latter two, unchanged.
80. Contamination-shaped forbidden count: 1 (DIS-100, PRESENT, LLM_REVIEWED, contamination-shaped).
81. Uncertainty result: NOT_REQUIRED 83, PARTIAL 36, VIOLATED 1. Wave 1: NOT_REQUIRED 83, PARTIAL 36, SATISFIED 1.
82. RC-04 still indicated: YES. The uncertainty distribution is unchanged except ROUT-091 SATISFIED to VIOLATED (PASS to FAIL, severity P2, evidence CERTAINTY_MARKER_WITH_REQUIRED_UNCERTAINTY); retrieval/evidence improvements did not indirectly resolve uncertainty semantics, and the judgment-layer boundary persists.
83. Renderer diagnostics (mechanical, kept separate from semantic criteria): 103/120 answers with 2+ national-information blocks; presented_as_complete_with_failures 104/120; no_route_asserted 100/120 (Wave 1: 97); epistemic state EXISTENCE_ONLY 104 / UNVERIFIED 16.
84. RC-06 still indicated: YES. RC-08 changed retrieval scoping, not rendering; presentation noise still dominates the answer surface.
85. Fresh-holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT (fresh-holdout-readiness.md; 5-point basis: route mechanism unresolved, unadjudicated P0 safety candidates, evidence attachment alone insufficient, retrieval not clean, 9 regressions with scorer-layer sensitivity).
86. SUT rerun: NO.
87. Source changed: NO.
88. Predictions changed: NO.
89. Gold changed: NO.
90. Measurement V3 changed: NO.
91. Astra MEDIUM calls: 0.
92. Astra HIGH calls: 0.
93. Astra MAX calls: 0.
94. Fresh cases consumed: 0.
95. Burned classification retained: YES (BURNED_DEV_BASELINE_ONLY in TASK-LOCK, aggregates, and all analysis deliverables).
96. Wave-2 measurement freeze SHA: f5e0a0193d9ddb4da7046ba9719c0d52dafa2982eee1bcac6c11393d5391fc30 (wave2-measurement-freeze-manifest.json self-SHA; 26 artifacts; frozen 2026-09-16T15:50:42Z; freeze executed BEFORE comparison).
97. Hashes verified: YES - shasum -a 256 -c hashes.txt: 26 OK, 0 failures, re-run this session after all writes to scored/frozen artifacts.
98. STATUS: MEASUREMENT_V3_REMEASURE_WAVE_2_RESIDUAL_ADJUDICATION_REQUIRED (valid terminal per spec section 42: ROUT-026::forbidden:01 remains pending after the allowed dual-pass Astra + bounded Sol adjudication; no additional model sampling permitted).
99. Recommended next bounded task: a dedicated owner-decision task to (a) adjudicate the frozen pending criterion ROUT-026::forbidden:01 together with the 2 P0 under-triage candidates (ROUT-026 critical_condition, ROUT-088 critical_condition) and the scorer-layer sensitivity question, and (b) decide Wave-3 scope from the repair backlog (route label-to-evidence binding mechanism, RC-04, RC-06). No implementation, no resampling, no fresh holdout in that decision task.

## Freeze ordering and lock note

The measurement freeze was executed before comparison and pins TASK-LOCK.json at its pre-terminal SHA 3000631d156fb9abfe6684d0ddeb6a190ec82507acd558951326d738ef91007f. The terminal status was added to TASK-LOCK after the freeze, following the established precedent from the measurement-v3-final-authority-provenance-repair-v1 lineage (lock closed post-freeze, drift documented). The post-terminal TASK-LOCK SHA is recorded below; hashes.txt was not modified after freeze, so it intentionally still pins the pre-terminal lock.

## Protocol compliance summary

- Astra gpt-6-astra: LOW only; MEDIUM/HIGH/MAX = 0 (items 91-93).
- Sol gpt-5.6-sol: LOW only; residual lane only; 8 calls total; 0 retries.
- LLM calls during derivation: 0.
- Blindness enforced: pass B saw no pass A; no pass saw historical verdicts; leakage audits all PASS.
- No fresh cases, no SUT rerun, no source/prediction/gold/corpus/measurement changes.
- One pending criterion remains by design; terminal state is RESIDUAL_ADJUDICATION_REQUIRED, not COMPLETE.
