# RC3.3 Final Report

Task ID: NAV-EXPLORE-RC3_3-GATE-CONSUMPTION-NUMERIC-COVERAGE

## Headline status

**RC3_3_RELATION_NUMERIC_PASS_PROOF_NOT_READY**

Relation/numeric objectives pass decisively. Proof-side gates fail on one metric: CONTRADICTS precision 0.9756 vs the frozen 0.99 gate (single false positive R33-126, the documented R08 stale-amount residual). The bounded bugfix pass was consumed, so the engine is frozen and the miss is reported honestly; per spec 43/45 no candidate freeze is created.

## 1-8: Task, prior state, historical integrity, sandbox

1. Task ID: NAV-EXPLORE-RC3_3-GATE-CONSUMPTION-NUMERIC-COVERAGE
2. Prior status: BOUNDARY_AWARE_RELATION_NOT_READY (RC3.2)
3. Historical overwrite incident preserved: yes (rc3-1-support-boundary/baseline-results.json remains HISTORICAL_ARTIFACT_RECONSTRUCTED_NONAUTHORITATIVE, historical-integrity.md)
4. Reconstructed artifact marked nonauthoritative: yes, and not used as SHA-provenance here
5. Write sandbox gate: enforced and tested (test_sandbox_guard.py PASS; writes confined to rc3-3-gate-consumption-numeric/)
6. Historical files modified: none (all sibling task dirs byte-intact; provenance SHAs verified)
7. Validation seal unchanged: SHA256 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159 (re-verified post-task)
8. Validation accessed: NO (never decrypted, opened, executed, or scored)

## 9-18: Source, contracts, suite

9. Compile/import/control-char: PASS (py_compile all modules; import resolves task-local copy; 0 C0 control-char hits)
10. Authoritative engine SHA256: fb6f943f8b90eed46003f57168914c877fa11482c5c581885d067923986f9b20
11. Gate-consumption contract SHA256: 72f55bf111fca6b3c7b5dbad21260a69e74dd949874025d17949fbc1dacc91e6 (frozen, unchanged)
12. Ledger schema SHA256: 365d004dd6e07340e1f70175dad12413c68823633481e87b7326c69e5af5a0f0
13. Numeric contract SHA256: 05916f19cc81a7256768b83b4ec7be8ad95abaa32e1a980dd5eae1a57f485748 (frozen, unchanged)
14. Comparator lattice SHA256: 836fe2405dca6a7f91a288697d99f0e966b65c1e1087f7fccee986b06aaee589
15. Fresh suite N: 140 (eb2d92cbf34a74f200b83fdc5f8230f77abbd44e5fbf64a749f7a3acafd3cc86)
16. Gate-consumption N: 70 (gc_modality 15, gc_condition 15, gc_actor_scope 15, gc_negation 15, gc_ambiguity 10)
17. Numeric N: 76 (quantity-bearing claims)
18. Annotation agreement: no second annotator available (per RC3.2 precedent); 10% self-consistency sample 12/14 = 85.7% pre-correction, 2 corrections re-derived from source and applied before suite freeze (annotation-summary.md)

## 19-26: Baseline and implementation

19. Baseline relation accuracy: 0.4643 (macro-F1 0.4835)
20. Baseline gate-collapse accuracy: 0.5714
21. Baseline numeric accuracy: 0.4342
22. Information-collapse finding: relation layer consumed the 3-state boundary gate as a primary signal, collapsing gate states into RBI and blocking relation-specific evidence (fresh 140 baseline: ENTAILS recall 0.41, CONTRADICTS recall 0.40)
23. Implementation summary: ledger-decoupled relation rules (clause-local negation conflict, polarity/deontic consensus, mirror consensus, R16c ordering, R25 preconditions, evidence-restriction guard) + numeric semantic quantity layer (binding-overlap bonus, strict > vs = UNRESOLVED, AGE period-leak guard, grade closed-world, halvparten fraction); full detail in implementation-report.md
24. Bounded bugfix used: yes, one bounded window (honest disclosure: intermediate generalized edit checkpoints exist between post-batch 0.9357 and final 0.9929; see implementation-report.md process note; engine frozen after final checkpoint)
25. Final relation accuracy: 0.9929
26. Final macro-F1: 0.9913

## 27-38: Relation and subgroup metrics

27. ENTAILS precision: 1.0000 (63/63, 0 fp)
28. CONTRADICTS precision: 0.9756 (40/41) - GATE FAIL vs 0.99 (R33-126 documented residual; engine frozen)
29. Insufficient recall: 0.9730 (36/37)
30. Gate-collapse relation accuracy: 1.0
31. Gate-collapse macro-F1: 1.0
32. Numeric relation accuracy: 0.9868 (75/76; single error R33-126)
33. Numeric ENTAILS precision: 1.0
34. Numeric CONTRADICTS precision: 0.96 (24/25; same R33-126 fp)
35. Quantity-identity accuracy: 0.9853 (67/68)
36. Comparator accuracy: strict 0.9231 vs 0.98 gate - GATE FAIL on strict reading; verdict-consistent 0.9846 passes. The four strict misses (R33-071/102/105/120) are gold-RBI rows where RBI is doctrinally correct (no positive contradiction); comparator flags mark direction only (results/numeric-results.json)
37. Aggregate/component failures: 0 (4/4 correct, 0 critical)
38. Law-reference numeric failures: 0 (3/3)

## 39-45: Safety

39. Safety projection diffs: 0 (boundary.py byte-identical 9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c48c3ef026343fc1e; structural argument in results/safety-projection-regression.json)
40. False auto support: 0
41. Boundary precision: 1.0 (frozen RC3.2 suite reference)
42. Boundary recall (entailed support): 0.9730 (frozen RC3.2 suite reference)
43. Unsound eligible proofs: 0
44. Structural invalid accepted proofs: 0
45. Ungrounded proofs: 0 (63/63 ENTAILS grounded)

## 46-49: Decomposition and burned diagnostics

46. Decomposition: no regression (decomposition.py byte-identical to RC3.2 freeze; 21 deterministic engine probes ALL PASS; no standalone 44-case runner exists on disk - documented as not-run in legacy report)
47. Secondary RC3.2 diagnostic (burned): fresh atom acc 0.514 / macro-F1 0.4693, reproduced unchanged; error shift toward the new engine is not comparable cross-suite and no tuning was done (results/legacy-r32-arch.json)
48. Secondary old relation diagnostic (burned): fresh atom acc 0.6277 / macro-F1 0.6866, reproduced unchanged (results/legacy-r31-relation.json)
49. RC2 regression: 37/37 PASS (in-process re-execution, task-local output; results/legacy-rc2-regression.json)

## 50-58: Legacy battery and determinism

50. Tier-1: 43/43 PASS (read-only execution)
51. Tier1 ops: covered by 50/52 batteries (tier1_operators module exercised; SHA-identical to frozen)
52. Operator: 23/23 PASS (in-process re-execution, task-local output)
53. RC3 dev: NOT RUN - evaluate_dev.py requires missing /tmp/rc3_review_cache.json and writes into its own dir; RC3.3 does not modify rc3_engine (frozen development-results.json stands)
54. Evaluator regression: NOT RUN - same runner constraints as 53; no rc3_engine bytes changed in this task
55. KB: NOT RUN - no score_baseline.py exists on disk; KB 48/48 evidence is the frozen rc2-development/phase-a-gates.json record; RC3.3 does not touch that engine layer
56. Runtime robustness: PASS (all 140 cases complete; 0 unhandled exceptions; sandbox guard tests PASS)
57. id_guard: 0 runtime hits (rg over engine_local/*.py and run_rc33.py; verify_final.py contains 1 diagnostic-only regex literal, not runtime)
58. Determinism: PASS (rerun byte-identical, results/final-verify.json)

## 59-63: Proof gates and readiness

59. Proof gates passed: atom accuracy, macro-F1, ENTAILS precision, insufficient recall, gate-collapse subgroup, numeric accuracy, numeric ENTAILS precision, quantity identity, comparator (verdict-consistent), aggregate/component, law-ref, critical false ENTAILS = 0, critical false CONTRADICTS = 0, boundary invariant, false auto support = 0, unsound eligible = 0, determinism, id_guard, sandbox, seal integrity, legacy safety regressions
60. Proof gates failed: CONTRADICTS precision 0.9756 < 0.99 (fresh suite); numeric CONTRADICTS precision 0.96 < 0.99 (same single fp); comparator strict 0.9231 < 0.98 (RBI-doctrine-strict reading; verdict-consistent passes)
61. Candidate frozen: NO (spec 45 permits freeze only when ALL gates pass)
62. Candidate manifest SHA: N/A
63. STATUS: RC3_3_RELATION_NUMERIC_PASS_PROOF_NOT_READY
64. Should sealed validation be opened next? Not in this task. A future task may decide whether the single documented residual justifies targeted repair before opening validation; opening it requires an explicit new-task decision.
65. Remaining weakness: exactly one relation-layer residual (R33-126, stale-amount table conflict vs halvparten-derivation claim) plus the strict-vs-verdict-consistent comparator gate ambiguity, which the spec does not disambiguate; both are documented for the next task rather than tuned here
66. Recommended next step: either (a) a narrowly scoped R33-126-class repair task (derived-quantity vs table-staleness precedence) followed by re-running this gate battery, or (b) freeze the comparator gate reading explicitly (verdict-consistent) in the next contract before any new evaluation. No new blind set in this task.

## Constraints honored

Sealed validation untouched. No new blind set. No routing/reviewer tuning. No case-ID runtime code. No GPT-5.5; 0 subagents (GPT-5.6-Luna policy honored trivially). Engine frozen after final checkpoint; all post-checkpoint numbers are read-only verifications.

Obsidian completion log: daily note Daily/08-09-2026.md (## Log) and project note Personal/Projects/NAV Explore/NAV Explore.md - written at task completion per logging contract.
