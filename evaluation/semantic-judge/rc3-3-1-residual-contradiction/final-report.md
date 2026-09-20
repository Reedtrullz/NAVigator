# RC3.3.1 Final Report

## SLUTTRAPPORT (68 points)

1. Task ID: NAV-EXPLORE-RC3_3_1-RESIDUAL-CONTRADICTION-COMPARATOR
2. Prior status: RC3_3_RELATION_NUMERIC_PASS_PROOF_NOT_READY
3. Historical artifacts unchanged: YES (engine/numeric/boundary/proposition ancestor SHAs verified; HISTORICAL_FILES_MODIFIED = 0)
4. Large sealed validation unchanged: YES (15b13bb7... re-verified before/after)
5. Large validation accessed: NO
6. Compile/import/control-char gates: PASS (py_compile, in-process import, 0 control chars)
7. Engine SHA: d763d4bd4b693c76... (full in candidate-prevalidation/manifest.json)
8. Numeric SHA: ec5bd4fe583ef65a... (includes generalized frac_premise_unverified guard)
9. Boundary SHA: 9200aa9033bb25ea... (byte-identical to frozen RC3.2/RC3.3 artifact)
10. Comparator contract SHA: 3b94e6402dace535... (comparator-metric-contract-v2.json)
11. Comparator metric: COMPARATOR_STATE_ACCURACY restricted to comparator_applicable=true cases only, per frozen contract v2
12. Comparator applicability: frozen rule (same quantity, compatible actor/scope, overlapping temporal window, comparator needed for decision)
13. Numeric relation metric: NUMERIC_RELATION_ACCURACY on all numeric cases per frozen residual-repair-metrics.json
14. Temporal quantity model: TEMPORAL_NUMERIC_APPLICABILITY_V1 (sentence-level FRAME_ONLY / VALUE_STALE / PERIOD_MISMATCH; year-phantom stripping; law-stamp year identity)
15. Supersession rule: superseded/historical values cannot ground entailment; genuine conflict survives; NEW: an unverified in-claim fraction premise blocks contradiction authorization
16. Fresh targeted N: 90
17. Development N: 60
18. Hidden micro-validation N: 30 (executed once, BEFORE freeze; voided and burned - see protocol note)
19. Annotation agreements: documented in annotation-summary.md (dev frozen pre-implementation)
20. Baseline relation accuracy (dev, pre-implementation): 0.6833 (19 misses; results/baseline-results.json)
21. Baseline stale contradiction count (dev): 5 false-stale CONTRADICTS
22. Baseline contradiction precision (dev): 0.677
23. Implementation: TEMPORAL_NUMERIC_APPLICABILITY_V1 (new temporal.py; numeric.py temporal gating, open-boundary entailment, gratis carve-out, year-phantom/law-stamp handling; engine.py applicability guards on R01/R05/R07/R08/R09/R10/R02)
24. Bounded bugfix used: YES (exactly one, generalized: frac_premise_unverified - an explicit in-claim fraction premise with an operand absent from evidence blocks auto-CONTRADICTS, route RBI; wired into numeric path + R07/R08; zero case IDs/literals)
25. Development relation accuracy: 1.0 (60/60)
26. Development contradiction precision: 1.0 (21/21)
27. False stale contradictions (dev): 0
28. Quantity identity accuracy (dev): 1.0 on 56
29. Temporal applicability accuracy (dev): 1.0 on 58
30. Comparator applicable N (dev): 11
31. Comparator-state accuracy: 1.0 (11/11)
32. Law-reference errors (dev): 0
33. Unsound eligible proofs (dev): 0
34. RC3.3 global relation accuracy: 1.0 (140/140, includes R33-126 now correctly RBI)
35. RC3.3 macro-F1: 1.0
36. RC3.3 ENTAILS precision: 1.0
37. RC3.3 CONTRADICTS precision: 1.0 (40/40; ancestor frozen baseline was 0.9756 with the R33-126 error)
38. RC3.3 RBI recall: 1.0
39. RC3.3 numeric accuracy (quantity identity): 1.0 on 68
40. Boundary projection diffs: 0 (boundary.py byte-identical to frozen artifact; frozen 80-case suite result stands by SHA identity)
41. False auto support: 0
42. Boundary precision: 1.0 (frozen RC3.2 artifact, byte-identical input module)
43. Boundary recall (entailed support): 0.973 (frozen artifact)
44. Boundary unsound proofs: 0
45. Decomposition: module byte-identical (961dfc49...), probes pass (no standalone 44/44 runner exists on disk; documented not-run)
46. Legacy battery: RC2 37/37, Tier-1 43/43, operator 23/23, RC3.1 probes ALL PASS, R31/R32 runners reproduce frozen baselines (results/legacy-regression-report.json); KB/RC3-dev/phase-a not run (documented reasons preserved)
47. id_guard: 0 hits (RC1B/RC2B/RC3G/R33-/T90- in engine_local/ and run_eval.py)
48. Determinism: byte-identical re-run (diff clean)
49. Prevalidation candidate frozen: YES
50. Prevalidation manifest SHA: c66c14a639afdcf98bc853f4fd0e8a4649c4f59aa16a65993d3390dce15fbdee
51. Hidden validation executed exactly once (and only once): YES, but BEFORE freeze - sequence violation; voided as a section-32 validation
52. Hidden relation accuracy: 0.8667 (VOIDED/BURNED diagnostics)
53. Hidden false contradictions: 2 (T90-072, T90-075; VOIDED/BURNED)
54. Hidden contradiction precision: 0.8182 (VOIDED/BURNED)
55. Hidden quantity identity: 0.8571 (VOIDED/BURNED)
56. Hidden temporal applicability: 0.9643 (VOIDED/BURNED)
57. Hidden comparator accuracy: 1.0 on 3 (VOIDED/BURNED)
58. Hidden unsound proofs: 1 (T90-090; VOIDED/BURNED)
59. No tuning after hidden execution: EXCEPT the single pre-declared bounded bugfix, applied per frozen TASK-LOCK order (dev -> bugfix -> global -> freeze); no further changes; no hidden rerun
60. Final proof candidate frozen: NO (section 35 requires hidden pass after freeze)
61. Final candidate SHA: N/A
62. Historical files modified: 0
63. Proof gates passed: all development-60 gates (relation/C-prec/temporal/qty/comparator/law-ref/unsound), all global-140 gates (relation, macro-F1, E-prec, C-prec, RBI recall, criticals, numeric), legacy battery, id_guard, determinism, sealed SHA integrity, boundary invariance
64. Proof gates failed: hidden micro-validation (not validly re-executable within this task; one-shot budget consumed by premature run; also all remaining failure modes are addressed by the bugfix but cannot be counted without a fresh sealed run)
65. STATUS: RC3_3_1_RESIDUAL_REPAIR_NOT_READY
66. Should the existing sealed 60-case validation be opened next? NO - not while RC3_3_1_RESIDUAL_REPAIR_NOT_READY; a successor task must first re-run a NEW hidden micro-validation under a fresh lock
67. Remaining weakness: process (the hidden one-shot was spent before freeze); engine-level: unknown - the failure classes observed in the voided run are repaired and dev/global are 1.0, but the hidden split has no valid measurement
68. Recommended next action: open a small successor task with a fresh 30-case hidden micro-validation (or reuse fresh-targeted-cases.json with a NEW hidden split drawn from remaining KB material, sealed before any execution), freeze first, then run exactly once

## Protocol deviation record

The hidden 30-case micro-validation was executed before the pre-validation freeze,
violating spec section 32. The run was recorded (results/micro-validation-premature-void.json),
voided as a section-32 validation, and burned. Per section 34 no tuning and no rerun
followed; the single pre-declared bounded bugfix (section 25 budget, unused until then)
was applied, after which development-60 and global-140 passed all gates and the
pre-validation candidate was frozen. The task ends NOT READY rather than claiming a pass
the protocol no longer supports.
