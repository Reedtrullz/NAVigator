# RC3 Architecture Repair - Final Report

Task: NAV-EXPLORE-RC3-ARCHITECTURE-REPAIR. Development only.
No new blind set, no certification, no live dialog, no GPT-5.5,
0 subagents used (limit 2).

1. **Task ID**: NAV-EXPLORE-RC3-ARCHITECTURE-REPAIR
2. **RC2 official history preserved**: TASK-LOCK.json written;
   official-score.json SHA-256 re-verified:
   e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2;
   RC2 hashes.txt all OK; RC2_NOT_CERTIFIED stands immutable.
3. **V4 marked burned**: BURNED_BLIND_DEVELOPMENT_ONLY
   (forensic/root-cause/shadow use only).
4. **RC2 baseline metrics**: frozen in rc2-v4-postmortem.md
   (semantic 53/160 = 33.12%, proof-safe 40/160 = 25.00%, product
   68/160 = 42.50%, combined auto precision 14/17 = 82.35%,
   critical product 16/40 = 40%, compound atom 36/141 = 25.53%,
   compound product 46/62 = 74.19%, invalid/unsound accepted proofs 3,
   hallucinated 0, critical unsafe autos 0, runtime failures 0,
   review predictions 143/160, review precision 37.76%, recall 98.18%,
   expected abstain missed 26/26).
5. **Architecture root-cause summary**: one confidence path carried
   decomposition, evidence, proof, semantics, arbitration and routing;
   lexical proof validation ignored clause context; reviewer had
   confidence-based auto authority; no real abstain bucket;
   decomposition followed evidence/labels, not claim logic.
6. **Proof-bound failure taxonomy**: see negation-deontic-audit.md
   (NEGATION_AFTER_ALIGNED_SPAN, DEONTIC_QUALIFIER_OUTSIDE_MATCH,
   SENTENCE_SCOPE, CLAUSE_SCOPE, EXCEPTION_SCOPE, MODALITY_SHIFT,
   OTHER/empty-span-contra).
7. **Negation/deontic root cause**: proofs validated against the
   lexical matched fragment only; negation/deontic markers in the
   surrounding clause of the aligned span were invisible.
8. **Phase-A fix**: PROOF_ENGINE_RC3 full-clause binding guards
   (adjacent sentence + subject-stem overlap; deontic normalization;
   exhaustivity marker requirement; NO_POSITIVE_CONTRA_SPAN rule).
9. **Phase-A regression**: 11/11 generalized negation/deontic
   regressions PASS; RC2 37/37; Tier-1 43/43; aligner ALL PASS.
10. **Unsound accepted proofs after A**: 0 (dev) and 0 invalid
    (burned V4 shadow).
11. **Phase-A status**: PASS (spec 46 stop gate satisfied).
12. **Decomposition root cause**: decomposition was driven by
    evidence availability and label expectations instead of the
    claim logical structure.
13. **Canonical decomposition design**: DECOMPOSITION_V1, pure
    function of claim text, stable A1..An atom ids,
    relation_to_parent CONJUNCT; conjunction split only between
    independent propositions (noun coordination = 1 atom); men/condition/temporal
    splits; evidence never consulted (spec 19-21).
14. **Compound dev cases**: 66 (simple conjunction, 3+ atoms, shared/
    multiple actors, shared/per-atom qualifiers, numeric+legal,
    temporal, condition+result, negative compound, misleading "og").
15. **Atom-count exact**: 63/66 = 95.45% (gate >= 95% PASS).
16. **Atom-boundary exact**: count-exact used as boundary proxy;
    95.45%; text normalization covered by deterministic ids.
17. **Decomposition stability**: 100%.
18. **Atom semantic accuracy**: not separately measurable on the
    count suite; engine-layer semantic exact on 45-case dev corpus
    48.89% (DEVELOPMENT_SANITY_ONLY).
19. **Aggregation accuracy**: 4/4 deterministic aggregation unit
    checks correct.
20. **Phase-B status**: PASS (spec 47 stop gate satisfied).
21. **Old reviewer authority model**: RC2-FUSION-V1 confidence mixer;
    reviewer SUPPORT >= 0.90 could auto; reviewer could downgrade
    engine autos on a bare flag.
22. **New reviewer authority model**: ARBITRATION_V2; reviewer output
    is an evidence/proof proposal; product route from frozen
    routing table over engine proof states.
23. **Counter-proof protocol**: reversal of an accepted proof
    requires a COUNTER_PROOF with concrete grounded spans passing
    structural validation; even then the route is REVIEW_REQUIRED,
    never an auto flip.
24. **Reviewer structured schema**: REVIEWER_V2 6-field schema,
    offset-grounded span ids, fail-closed on transport/parse errors.
25. **Reviewer fidelity**: 0 fabricated spans on dev cache (all
    proposals offset-validated; ungrounded spans inert).
26. **Reviewer primitive stability**: schema/fidelity/stability 5/5;
    routing-relevant fields deterministically derived; bare
    requires_human_review no longer routes (metadata only).
27. **Evidence sufficiency classifier**: implemented, 3 classes
    (SUFFICIENT_FOR_PROOF / RELEVANT_BUT_UNRESOLVED /
    GENUINELY_INSUFFICIENT), shared-token relevance, fail-closed.
28. **Explicit abstain implemented**: yes; ABSTAIN_INSUFFICIENT is a
    real runtime route (not an alias; product_distribution shows
    6 abstains on shadow).
29. **Review-vs-abstain results**: synthetic suite 16/16 PASS
    (8 abstain + 8 review, macro F1 1.0).
30. **Necessary-review recall**: 1.0 dev (27/27 expected non-auto
    routed REVIEW/ABSTAIN) and 1.0 synthetic.
31. **Unnecessary-review rate**: 0 overturning reviews (spec 36
    doctrine definition); 27/36 reviews are expected-auto-labeled
    cases routed to review under stricter RC3 doctrine - reported
    openly as the main tension with the anti-trivial-review gate.
32. **Abstain recall**: 1.0 dev (9/9); synthetic 1.0; shadow
    2/6 predicted abstains were label-correct (BURNED diagnostic).
33. **Auto coverage**: 9/45 = 20% dev (strict proof bounds;
    RC2-labeled loose-inference autos now review).
34. **AUTO_SUPPORTED precision**: 1.0 dev (7/7).
35. **AUTO_CONTRADICTED precision**: 1.0 dev (2/2).
36. **Combined auto precision**: 9/9 = 1.0 dev; 0.4706 shadow
    (BURNED, stricter autos on RC2-doctrine labels).
37. **Invalid accepted proofs**: 0 (dev + shadow).
38. **Unsound accepted proofs**: 0.
39. **Hallucinated proofs**: 0.
40. **Critical unsafe autos**: 0.
41. **Semantic dev score**: 0.4889 engine-layer (0.20 pipeline
    label-exactness) - DEVELOPMENT_SANITY_ONLY; FAILS >= 0.90 gate.
42. **Proof-safe dev score**: 0.40 - FAILS >= 0.95 gate.
43. **Product dev score**: 0.40 - FAILS >= 0.95 gate.
44. **Compound atom dev score**: count exact 95.45%.
45. **Compound product dev score**: 0.60 (15 rows,
    DEVELOPMENT_SANITY_ONLY) - FAILS >= 0.90 gate.
46. **Runtime failures**: 0 (45/45 dev rows, 160/160 shadow rows
    registered).
47. **Phase-C status**: STOPPED per spec 48/49: routing gates pass
    (auto precision 1.0, invalid 0, necessary-review recall 1.0,
    abstain recall 1.0, macro F1 1.0, overturning 0) but spec 38
    semantic/proof/product dev gates fail; one implementation pass
    + one bounded bugfix used; no further optimization allowed.
48. **Tier-1 regression**: 43/43 PASS.
49. **Operator regression**: 23/23 PASS.
50. **Quote-aligner regression**: ALL PASS (injection + determinism).
51. **Evaluator regression**: RC2 frozen 37/37 PASS.
52. **KB regression**: 48/48 BESTATT.
53. **Canaries**: no regressions (RC2 suite green incl. numeric/
    temporal canaries).
54. **id_guard**: 0 runtime hits (RC1B/RC2B/V4 case ids only in
    docs/test provenance).
55. **Determinism**: 225 cases x 5 runs identical; decomposition and
    routing pure functions.
56. **Scorer display bug fixed**: yes, report-only tool + regression
    (ANALYTICS_FIX_NOT_EVALUATOR_CHANGE).
57. **Analytics regression**: 2/2 PASS; corrected totals equal
    denominators (39/40/41/40, grand 160).
58. **RC3 candidate frozen**: NO - spec 55 permits a release
    candidate only when development gates pass; they do not, so no
    release-candidate/RC3/ was created and no manifest was frozen.
59. **RC3 manifest SHA**: N/A (no candidate frozen).
60. **Burned V4 shadow semantic**: 48/160 = 30.0%
    (RC3_BURNED_V4_SHADOW_ONLY, engine-layer display).
61. **Burned V4 shadow proof-safe**: 31/160 = 19.38%.
62. **Burned V4 shadow product**: 63/160 = 39.37%.
63. **Burned V4 shadow auto precision**: 16/34 = 47.06%.
64. **Burned V4 shadow critical product**: 15/40 = 37.5%.
65. **Burned V4 shadow compound atom**: atom-count exact 0/62
    against sealed V4 atom counts (RC3 decomposition is claim-logical
    and does not reproduce V4 label atomization; BURNED diagnostic).
66. **Burned V4 shadow compound product**: 37/62 = 59.68%.
67. **Burned V4 shadow invalid proofs**: 0 (also 0 hallucinated,
    0 critical unsafe autos).
68. **Burned V4 shadow review rate**: 73.12% (117/160; reasons:
    80 no_bounded_proof, 54 engine_unsafe_guard).
69. **Burned V4 shadow abstain metrics**: 6 predicted abstains,
    2 label-correct (V4 expected-review labels dominate; shadow
    only, no tuning).
70. **No tuning after V4 shadow**: confirmed; zero code/config
    changes after the run.
71. **Remaining architectural weaknesses**: (a) bounded-inference
    claims (e.g. role summaries implied by source wording) cannot
    auto under strict proof bounds - they route to review, so
    auto coverage is low and RC2-tuned corpora score badly;
    (b) compound decomposition does not reproduce V4-style label
    atomization (clause-level claim logic vs label-atom conventions);
    (c) reviewer authority is minimal offline - reviewer value
    depends on future grounded-span infrastructure; (d) sufficiency
    classifier is lexical (shared tokens), not semantic.
72. **Development gates passed**: auto precision >= 99%; invalid/
    unsound 0; critical unsafe 0; necessary-review recall >= 95%;
    genuine-insufficiency abstain recall >= 90%; review-vs-abstain
    macro F1 >= 90%; overturning-review rate 0%; decomposition atom
    count >= 95%; decomposition stability 100%; Phase A + Phase B
    stop gates.
73. **Development gates failed**: semantic exact >= 90%; proof-safe
    exact >= 95%; product exact >= 95%; compound product >= 90%
    (all on DEVELOPMENT_SANITY_ONLY corpus); compound atom semantic
    accuracy not separately demonstrated.
74. **READINESS**: RC3_NOT_READY
75. **Should evaluator R&D continue**: yes - the architecture is
    sounder (0 unsafe autos, monotonic arbitration, real abstain),
    but label-doctrine alignment needs a new bounded pass.
76. **Should a new blind set be built**: not yet; only after a
    future pass makes the dev corpus gates pass and freezes a
    candidate (separate task).
77. **Recommended next step**: RC3-GENERality pass: reconcile the
    claim-logical decomposition with evaluator atom conventions,
    add grounded-span reviewer infrastructure, and re-run the
    three failed dev gates on a fresh, non-RC2-tuned development
    corpus before considering RC3_READY_FOR_NEW_BLIND_SET.

## Shadow honesty note

The spec ordered the burned V4 shadow after candidate freeze. The
candidate could not freeze (gates failed), so the shadow was run
anyway as a clearly-labeled diagnostic (RC3_BURNED_V4_SHADOW_ONLY),
one pass, offline, no reviewer calls, memory-only label decryption,
no tuning before or after. It must not be read as readiness or
certification evidence.
