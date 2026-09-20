# SLUTTRAPPORT - RC3.1 Generalized Relation-Class Repair

## Status

**RELATION_REPAIR_NOT_READY**

Overall proof-dev readiness gates (spec 34) failed on fresh relation
accuracy. The frozen support boundary remains intact and byte-identical.
The sealed 60-case validation was not accessed, decrypted, or scored.

## Historical integrity (items 1-5)

1. Task ID: NAV-EXPLORE-RC3_1-GENERALIZED-RELATION-CLASS-REPAIR
2. Prior status: BOUNDARY_REPAIR_PASS_PROOF_NOT_READY
3. Historical artifacts unchanged: RC2 official artifacts, RC3G
   generalization artifacts, proof-semantics corpus, boundary candidate
   manifest and component hashes all unmodified (read-only verification).
4. Validation seal unchanged: corpus/validation-answer-key.sealed
   SHA-256 15b13bb7006e... rehash-verified, matches recorded history.
5. Validation accessed: **NO**

## Gate 0 - source integrity (items 6-12)

6. Compile gate: py_compile OK on final engine
7. Import gate: actual module import verified, path logged in
   relation-results.json provenance
8. Control-char gate: 0 unexpected C0 control characters
9. Imported engine path: evaluation/semantic-judge/rc3-1-proof-semantics/rc3_1_engine/engine.py
10. Imported engine SHA-256: 4bd2845fac3535fba22ab3e242b51e80f0d2abbbb5d57a3123b7207b2383ea7d
11. Relation contract SHA-256: 6c092eec3d99b81f1279c363dfad6aa06579e7216d906a0b8a4999c341bb53f2
12. Relation metrics SHA-256: 18f4c8b93e217f53313fd53cdc89ce3c2e0292cc13db535a5136c3680c72a352

## Relation architecture (items 13-20)

13. Vocabulary: ENTAILS / CONTRADICTS / PARTIAL /
    RELATED_BUT_INSUFFICIENT / AMBIGUOUS (relation-contract-v2)
14. Atom metric: ATOM_RELATION_ACCURACY = exact correct semantic
    relation / all expected claim atoms (188 atoms over 157 cases)
15. Product/relation separation: relation layer returns relation only;
    product routing (AUTO_*/REVIEW/ABSTAIN) is out of scope here
16. Boundary/relation separation: R27/R28 gate unchanged; boundary
    result never overwritten by relation verdict
17. Modality lattice: frozen modality-relation-lattice.json
    (SHA a5af67a1...), directional REQUIRED/ENTITLED/PERMITTED/
    POSSIBLE/PROHIBITED/NOT_REQUIRED
18. Contradiction obligation: positive incompatibility only; absence is
    not contradiction
19. Insufficiency rule: RELATED_BUT_INSUFFICIENT absorbs relevant-but-
    non-establishing evidence
20. Partial rule: PARTIAL only with explicit semantic partial ground

## Fresh suite and baseline (items 21-34)

21. Fresh relation N: 157 cases (188 atoms)
22. Class distribution: ENTAILS 51, CONTRADICTS 35,
    RELATED_BUT_INSUFFICIENT 42, PARTIAL 28, AMBIGUOUS 1
23. Annotation agreement: no separate annotation-summary recorded in
    this tree from the earlier phase; agreement evidence not available
24. Negation N: 25 cases
25. Modality N: 25 cases
26. Condition/exception N: 20 cases
27. Actor/scope N: 30 cases
28. Numeric/temporal N: 27 cases
29. Compound N: 30 cases (plus cross-group compound atoms)
30. Baseline relation accuracy: 0.6596 (atom)
31. Baseline macro-F1: 0.7157
32. Baseline ENTAILS precision: 0.9180
33. Baseline CONTRADICTS precision: 0.6341
34. Root-cause taxonomy (baseline, 88 errors):
    RELATION_BOUNDARY_COLLAPSE 51, NEGATION_RELATION 10,
    WRONG_MODAL_LATTICE 8, INSUFFICIENT_MISUSE 7, ACTOR_RELATION 3,
    OTHER 5, NUMERIC_RELATION 2, CONDITION_RELATION 2

## Implementation and bounded pass (items 35-36)

35. Implementation summary: SEMANTIC_RELATION_LAYER_V2 rule battery
    (R01-R31) was planned and the bounded-pass implementation was
    applied: negation-scope helpers (_neg_scoped_tokens,
    _neg_predicates_unaddressed, META_NEG_OBJECTS), boundary
    passthrough (_passthrough_ok) for modality/condition/actor blocks
    on high-coverage claims, R05b/R05c deadline units, R09b/R09c/R11b
    amount/direction frames, R16c/R16d/R16e actor/consent/requirement
    rules, R26b absence-frame rework, R27/R28 gate rework, and
    R29/R30/R31 scope guards.
36. Bounded bugfix used: **YES - consumed, measured, and REVERTED.**
    Result: atom accuracy 0.6596 -> 0.6862, ENTAILS precision
    0.9180 -> 0.8657, critical false ENTAILS 3 -> 4, boundary
    entailed-support recall 0.9730 -> 0.8649, train unsound-eligible
    0 -> 1. Spec 32 (no boundary safety regression) is a hard gate,
    so the pass was reverted byte-identically (SHA-verified) rather
    than shipped. Measured evidence: bounded-bugfix-pass-results.json.

## Final metrics on restored engine (items 37-48)

37. Final relation accuracy: 0.6596 (gate >= 0.95) FAIL
38. Final macro-F1: 0.7157 (gate >= 0.93) FAIL
39. ENTAILS precision: 0.9180 (gate >= 0.99) FAIL
40. CONTRADICTS precision: 0.6341 (gate >= 0.99) FAIL
41. Critical false ENTAILS: 3 (gate = 0) FAIL
42. Critical false CONTRADICTS: 4 (gate = 0) FAIL
43. Insufficient recall: 0.6667 (gate >= 0.90) FAIL
44. Negation subgroup: 0.6400 (gate >= 0.95) FAIL
45. Modality subgroup: 0.8000 (gate >= 0.95) FAIL
46. Condition/exception subgroup: 0.2500 (gate >= 0.95) FAIL
47. Actor/scope subgroup: 0.6667 (gate >= 0.95) FAIL
48. Numeric/temporal subgroup: 0.7407 (gate >= 0.90) FAIL

## Boundary safety on final engine (items 49-52)

49. FALSE_AUTO_SUPPORT_BOUNDARY: 0 - PASS
50. Support boundary precision: 1.0 - PASS (gate >= 0.99)
51. Entailed support recall: 0.9730 - PASS (gate >= 0.85)
52. Unsound eligible support proofs: 0 - PASS

Boundary hard gates hold. Fresh per-dimension boundary accuracies
(negation 0.95, modality 0.70, condition/exception 0.67, actor/scope
0.80, temporal/numeric 0.60) do not reproduce the boundary task's
recorded frozen per-dimension values; the recorded run used engine SHA
c4bc7186..., so this drift predates the present task and is recorded as
a pre-existing observation, not a new regression.

## Burned TRAIN diagnostics (items 53-54)

53. Burned TRAIN atom relation accuracy: 0.3614 (diagnostic only,
    not freshness evidence)
54. Burned TRAIN unsound eligible count: 0

## Legacy and stability (items 55-65)

55. Decomposition: 44/44 PASS
56. Determinism: two independent full relation runs identical PASS
57. RC2 frozen regressions: 37/37 PASS
58. Tier-1 gate: PASS (0 invalid proofs, 0 critical auto errors)
59. Tier-1 operators: 43/43 PASS
60. Operator regression (23-case suite): not found in this tree;
    closest equivalents (tier1 ops 43/43, evaluator 120/120, RC3 dev
    pytest 24/24) all pass. Logged as a coverage gap, not a pass.
61. RC3 dev tests: 24/24 PASS
62. Quote-aligner: 2 mismatches new vs Sep-2 recorded QA06 (MP-015A,
    CI-021) - date-window drift in the standalone frozen aligner
    (datetime-dependent deadline logic); 4 further mismatches are
    byte-identical to recorded QA06. No import path to the RC3.1
    engine. Logged as pre-existing/not-caused-here.
63. KB baseline: 48/48 BESTATT PASS
64. Runtime robustness: 0 unhandled exceptions across all relation,
    boundary, and regression runs this task
65. id_guard: 0 runtime hits (RC1B / RC2B / RC3G / suite IDs)

## Verdict (items 66-73)

66. Overall proof-dev gates passed: NO
67. Gates failed: fresh relation accuracy, macro-F1, ENTAILS precision,
    CONTRADICTS precision, critical false ENTAILS, critical false
    CONTRADICTS, insufficient recall, all five relation subgroups
68. Candidate relation frozen: NO (spec 37 precondition unmet)
69. Candidate manifest SHA: N/A (no candidate-relation/ created)
70. STATUS: RELATION_REPAIR_NOT_READY
71. Should sealed validation be opened next: NO
72. Remaining proof weaknesses: dominant RELATION_BOUNDARY_COLLAPSE
    (51/88 baseline errors): boundaryUNKNOWN blocks on near-verbatim
    claims whose only difference is modality/condition/actor phrasing;
    negation-scope and condition-binding misclassification; PARTIAL
    under-production (recall 0.346). Bugfix attempt showed single-rule
    mitigation trades away boundary safety (passthrough weakened the
    fail-closed gate).
73. Recommended next step: a NEW task must design boundary-aware
    relation recovery at the architecture level: either (a) enrich the
    frozen boundary's dimension vocabulary so modality/condition/
    actor-phrase differences carry structured, per-dimension evidence
    instead of a single BOUNDARY_UNKNOWN, with the relation layer
    consuming those dimensions while boundary hard gates stay frozen;
    or (b) accept lower auto coverage and target the relation metric
    only on boundary-compatible subsets. No third implementation pass
    in this task. Validation remains sealed.
