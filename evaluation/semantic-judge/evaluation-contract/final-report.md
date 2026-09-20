# SLUTTRAPPORT - SEMANTIC-JUDGE-EVALUATION-CONTRACT-REDESIGN

Dato: 2026-09-02. Data/schema/audit-stage; no evaluator, aligner, reviewer, or adjudicator code changed. No holdout-v3, no blind recertification, no live dialog, no NAV/kommune research, no bounded-operator implementation. Original labels preserved everywhere.

1. **Task-lock**: TASK-LOCK.json, task_id SEMANTIC-JUDGE-EVALUATION-CONTRACT-REDESIGN, ACTIVE through build, COMPLETED at close. All 9 forbidden_tasks respected.
2. **Oracle-probe utgangspunkt**: 46 cases audited (A=6, B=17, C=12, D=3, E=6, F=2); 33/46 = 71.7% benchmark-vs-doctrine divergence. Probe: frozen reviewer v1.1 benchmark accuracy 5/24 = 20.8% vs doctrine accuracy 22/24 = 91.7% (2 true errors: N-L4, N-C5).
3. **Single-target utilstrekkelig**: one benchmark label cannot simultaneously be semantic ground truth and production-safety gate; it forced reviewer v1.1 to look 20.8%-bad while being 91.7% doctrine-consistent, and rewarded an invalid auto-contradiction on ENT-C.
4. **Semantic truth defined**: bounded-inference reading (explicit synonymy, identity definitions, rule+condition, marked exhaustive exclusion, simple conjunction, small transitive paraphrase chains); no closed world, no external/legal knowledge without source. Four classic labels.
5. **Proof-safe defined**: verdict derivable with an explicitly validatable proof under current doctrine; labels SUPPORTED / CONTRADICTED / INSUFFICIENT / REVIEW_REQUIRED (PARTIAL documented as aggregation result only). Always equal to or more cautious than semantic truth.
6. **Product decision defined**: fusion choice auto/review/abstain judged against proof-safe target; auto right iff verdict matches proof-safe; review right iff semantic and proof-safe diverge; unnecessary review = efficiency cost.
7. **Oracle-46 reannotated**: 46/46 with dual labels, two-pass (curated + mechanical), schema evaluation-contract-dual-labels-v1, full justification + evidence spans + operator class.
8. **Original-vs-semantic disagreements: 18** of 46 (39.1%).
9. **Original-vs-proof disagreements: 33** of 46 (71.7%).
10. **Semantic-vs-proof disagreements: 20** of 46 (43.5%).
11. **Annotation disputes: 2** (CI-046, CAL089) - status ANNOTATION_DISPUTE, not forced.
12. **Novel-40 reannotated**: 40 cases (8 oracle-overlap ids imported with two-pass provenance, 32 curated first-hand). Original-vs-semantic disagreements: 3 (N-S9, N-A3, N-O5 - all EXPECTED_LABEL_OVERREACH).
13. **Novel-40 original accuracy**: hybrid engine 27/35 decided = 77.1%; quote-aligner v0.2 27/40. Both LEGACY_SINGLE_TARGET_GATE.
14. **Novel-40 semantic accuracy**: engine 29/35 = 82.9%; the three overreach flips count as hits under bounded reading.
15. **Novel-40 proof/product**: auto path 11 claims; review path 5 RR. Product-correct auto requires verdict == proof-safe target; N-O5 benchmark CONTRADICTED is semantically INSUFFICIENT (varierer mellom kommunene vs i alle kommuner is marked-exhaustive only in the claim) - proof-safe INSUFFICIENT.
16. **ENT-A**: orig SUPPORTED -> semantic INSUFFICIENT (foreldresamtale premise absent, verified in KB 26 line 32), proof-safe INSUFFICIENT. Taxonomy EVIDENCE_MISSING. Old ENT-A FAIL was partially semantic truth, partially benchmark overreach.
17. **ENT-B**: orig INSUFFICIENT -> semantic INSUFFICIENT (source about school health service, claim about fastlege), proof-safe INSUFFICIENT. Consistent.
18. **ENT-C**: orig CONTRADICTED -> semantic INSUFFICIENT (no explicit PPT-diagnosis exclusion; CONTRA needs closed-world), proof-safe INSUFFICIENT. Taxonomy EXPECTED_LABEL_OVERREACH. Engine auto-CONTRADICTED was an invalid proof the old gate scored as PASS.
19. **ENT-D**: orig CONTRADICTED -> semantic CONTRADICTED, proof-safe CONTRADICTED (explicit negation). The v0.1 lexical failure was a genuine lexical gap, not a label problem.
20. **Hybrid Iteration-B reinterpretation**: 389 rows, 362 decided, 317 old-correct = 87.57% selective (recomputed from raw rows, matches report). Semantic accuracy all-decided: 333/362 = 91.99% (307 defaulted rows keep original labels); reannotated-78 subset: 47/76 = 61.8% (error/probe-enriched by design).
21. **87.6% decomposed**: auto path 121 claims = 120/121 semantic-correct, 119/121 proof-valid, 0 critical false auto-SUPPORTED. All 45 verdict errors are review-path; reclassified: 17 SEMANTIC_HIT_BENCHMARK_OVERREACH, 16 PROOF_SAFE_ABSTENTION, 12 VERDICT_EXCEEDS_PROOF_BOUNDS. 21 of 27 reviews unnecessary (safe but inefficient). 2 invalid auto-proofs: MP-014A (auto-SUPPORTED over proof-safe INSUFFICIENT) and ENT-C (auto-CONTRADICTED over INSUFFICIENT).
22. **Quote-aligner v0.2 reinterpretation**: 27/35 = 77.1% original vs 29/35 = 82.9% semantic; 3 of 8 misses were label overreach (N-S9, N-A3, N-O5), 5 genuine (N-S4, N-L4, N-C4, N-C5, N-R3). The 90% novel-40 gate was measuring the wrong target for 3 of its misses.
23. **Reviewer v1.1 reinterpretation**: 20.8% benchmark accuracy is a label-alignment artifact, not capability collapse; 91.7% doctrine accuracy with 2 true errors. Proof-safe strong; semantic capability was never actually measured by the probe benchmark.
24. **Semantic accuracy metric**: decided-row verdicts vs semantic_truth on CONFIRMED dual-label cases, per set, dispute-weighted; abstention where semantically decidable = semantic miss. Written in metrics-spec.md.
25. **Proof-safety metric**: invalid-proof rate (auto verdict exceeding proof-safe target) at 0 tolerance; includes unsupported auto-accept, auto-contradiction, hallucinated premise.
26. **Product-decision metric**: expected action per case (auto iff semantic==proof-safe and operator not REVIEW_ONLY); critical false auto = 0 tolerance; unnecessary-review rate tracked as efficiency.
27. **Error-cost model**: critical false auto-SUPPORTED; very severe false auto-CONTRADICTED; moderate unnecessary REVIEW_REQUIRED; low semantic miss without auto-decision.
28. **Label-quality metrics**: label_disagreement_rate = 39.1% (oracle-46), 7.5% (novel-40), 50% (ENT-B/C candidates); annotation_dispute_rate = 2/46 oracle two-pass cases = 4.3%. High disagreement invalidates single-target gates, not the model.
29. **Operator count**: 15 classified (from frozen inference-operators.json v1) + NO_OPERATOR semantics documented. Nothing implemented.
30. **SAFE_FOR_AUTO_PROOF: 5** (DIRECT_ASSERTION, EXPLICIT_NEGATION, NUMERIC_CONFLICT, TEMPORAL_CONFLICT, SIMPLE_ARITHMETIC).
31. **SAFE_WITH_PRECONDITIONS: 9** (MODALITY_CONFLICT, SAME_PREDICATE_OPPOSITE_POLARITY, RULE_PLUS_CONDITION, RULE_PLUS_EXCEPTION, DEFINITION_PLUS_INSTANCE, EXHAUSTIVE_SET_EXCLUSION, ACTOR_MEMBERSHIP, MULTI_SPAN_CONJUNCTION, TRANSITIVE_EQUIVALENCE).
32. **REVIEW_ONLY: 1** (LOCAL_RULE_OVERRIDES_GENERAL - legal hierarchy rarely explicit in evidence).
33. **FORBIDDEN: 0** as standing classes; unmarked exhaustiveness inside EXHAUSTIVE_SET_EXCLUSION and any hidden-world premise are forbidden instances, not operator classes.
34. **Tier-1 backlog**: the 5 SAFE_FOR_AUTO_PROOF operators - high value, low risk, implementation-ready.
35. **Tier-2 backlog**: the 9 preconditions operators - DEFINITION_PLUS_INSTANCE may graduate to auto-proof for explicit identity definitions; EXHAUSTIVE_SET_EXCLUSION only with explicit markers (kun/bare/eneste/alle) + same scope/time/role.
36. **Tier-3**: LOCAL_RULE_OVERRIDES_GENERAL stays review-only; do not automate on locality-term presence alone.
37. **Future holdout schema**: every blind case carries semantic_truth + proof_safe + required operator + expected product action before exposure; four-annotation pre-exposure contract in future-holdout-spec.md. Holdout-v3 NOT built.
38. **Holdout firewall**: tuning agent/model never sees semantic or proof-safe answer keys before freeze; keys in access-controlled files.
39. **Annotation review policy**: legal/safety/bounded-inference/implicit-contradiction cases require two independent passes; disagreement -> ANNOTATION_DISPUTE, excluded from scoring until resolved.
40. **Legacy gates misaligned**: novel-40 <90% FAIL (unqualified target); oracle benchmark accuracy as capability; single-number mixed-set accuracy; ENT-C PASS as contradiction precision. Marked LEGACY_SINGLE_TARGET_GATE.
41. **New readiness metrics**: semantic reviewer target on CONFIRMED dual labels; proof engine invalid-proof = 0; product fusion critical false auto = 0 + selective quality threshold; unnecessary-review reported separately.
42. **Original-label preservation**: verified programmatically - 0 mismatches across oracle-46 (vs frozen ledger), novel-40 (vs source file), ENT-A..D (vs expected file).
43. **ID guard**: check_id_guard.py exit 0 (rationale notes only, no benchmark ids/literal claims in runtime code). No case-id patterns introduced in this task; deliverables are data/docs only.
44. **KB regression**: score_baseline.py re-run live - 48/48 unique S-cases BESTATT, 0 failures.
45. **Evaluator regression**: run_evaluator_regression.py re-run live - TP=24 TN=96 FP=0 FN=0, acc=1.00, safety_FP=0.
46. **qa_check.sh**: re-run live - PASS, no known error strings.
47. **HOVEDKONKLUSJON benchmark quality**: the old benchmark set is not one ground truth. 39-72% of labels diverge from semantic truth depending on subset; the legacy 87.57% understates auto-path quality (near-ceiling, 0 critical FP) while hiding 2 invalid proofs and an efficiency problem (78% unnecessary reviews). ENT-C shows the old gate actively rewarding an unsafe behavior.
48. **Bounded-operator implementation defensibility**: yes for Tier 1 (5 operators) - the auto path already proves the doctrine sound; conditional for Tier 2 with explicit structural preconditions; LOCAL_RULE_OVERRIDES_GENERAL should remain review-only. Decision belongs to the next stage.
49. **Remaining uncertainties**: (a) 2 ANNOTATION_DISPUTE cases unresolved; (b) 307 of 389 hybrid rows rely on the default original-label mapping for semantic scoring - targeted reannotation of calibration/holdout error clusters would sharpen the 91.99% figure; (c) novel-40 proof-safe targets derive from engine behavior, adding mild circularity - independent doctrine proof needed for production claims; (d) the 32 curated novel labels had one curated pass, not the formal two-pass - flagged in provenance.
50. **Anbefalt neste steg**: resolve CI-046 and CAL089 disputes, then run a formal second pass over the 32 curated novel labels; then take the Tier-1 operator backlog into a bounded implementation stage with invalid-proof=0 and critical-FP=0 gates. Do not resume deterministic lexical R&D.
