# FINAL REPORT - V1.6A.3 BOUNDARY PRE-CLASSIFIER

## 1-4. Identity and integrity

1. **Task ID**: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A3-AMBIGUITY-ABSTENTION-HARDENING
2. **Prior V1.6A.2 status**: PRESERVED. V1.6A.2 official 80-stratum precision 0.7027 (fail); registered failure families: quote scope, parenthetical scope, mixed polarity, hedge competition, multiple candidates, cross-clause grounding.
3. **Baselines verified**: baseline-integrity.json verified at checkpoint 3; frozen engine SHA 21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b re-verified this session against candidate-freeze-before-fresh.json before any fixture run.
4. **Historical writes**: 0. All prior lineages untouched.

## 5-10. Failure analysis

5. **V1.6A.2 official 80 marked burned**: YES (burned-data-registry.json).
6. **Gold-boundary disputes preserved**: 4 registered disputes from V1.6A.2 preserved unchanged.
7. **Failure families identified**: quote scope, parenthetical, mixed polarity, hedge competition, multiple candidates, cross-clause, out-of-inventory nouns.
8. **Deterministically resolvable**: clear assertion, hedge, negation, retraction, inventory routes, resolvable quote reports.
9. **Structurally ambiguous**: out-of-quote signals after quote end, all-parenthetical commitments, mixed polarity on one candidate, hedge competition across men/eller, multi-candidate same-clause competition.
10. **Contract/gold-boundary**: OFF-SCOPE-05/17 retraction polarity, OFF-SCOPE-09 trailing qualifier, OFF-SCOPE-08 attributed bare quote, OFF-SCOPE-16 bare quote output.

## 11-20. Implementation

11. **Case-specific rules**: NO. Engine contains no fixture IDs, no literal sentence matches; text-reuse audit confirms no case-mapping reuse.
12. **Generic ambiguity gate implemented**: YES - five generic Norwegian-linguistic gates (ambiguity-gate-design.md), frozen before implementation.
13. **Quote guard**: G1 BC_ROUTE_QUOTE_SCOPE_04 - ABSTAIN on quote span plus out-of-quote commitment signal after quote end; pre-quote assertions do not contaminate (burned-gold pattern preserved).
14. **Parenthetical guard**: G2 BC_ROUTE_PAREN_SCOPE_05 - ABSTAIN when all candidates and all operators sit inside parentheses.
15. **Mixed-polarity guard**: G3 BC_ROUTE_MIXED_POLARITY_04 - single candidate collecting 2+ distinct polarity frames ABSTAINs; retraction binding keeps SELF_RETRACTED.
16. **Hedge-competition guard**: G4 BC_ROUTE_HEDGE_COMPETITION_06 - hedge-licensed clauses on different candidates separated by eller/men ABSTAIN; parallel hedges without disjunction stay deterministic.
17. **Multi-candidate guard**: BC_ROUTE_AMBIGUOUS_02 - 2+ candidates sharing one non-hypothetical clause ABSTAIN (preserved from V1.6A.2, exercised on fresh batch).
18. **Retraction guard**: conservative retraction retained (contract section 18); ambiguous corrections route through clause-locality/unknown-noun abstain paths.
19. **Out-of-inventory guard preserved**: BC_ROUTE_UNKNOWN_SERVICE_01 - 0 regressions in burned cascade.
20. **Clause-locality guard preserved**: BC_ROUTE_CLAUSE_LOCALITY_01 - 0 regressions in burned cascade.

## 21-29. Development

21. **New dev fixtures**: 30 TDD (10 clean / 12 required-abstain / 8 counterexample).
22. **Generalized RED observed**: YES - 10/30 TDD failed on V1.6A.2 engine before fix; all family-representative.
23. **Existing tests**: 67 unit (v1-6a) + 72 checkpoint-3 regression assertions.
24. **New tests**: 30 TDD + 17 burned-regression assertions.
25. **Total GREEN**: TDD 30/30, unit 67/67, burned cascade all green (see 26-29).
26. **Burned-120 precision**: 1.0.
27. **Burned-60 precision**: 1.0.
28. **Burned-V1.6A2-80 precision**: 0.871 strict / 1.0 dispute-aware (the 4 registered gold disputes are the only strict-mismatches; zero engine regressions).
29. **Burned false deterministics**: 0.

## 30-36. Fresh set

30. **Engine frozen before fresh authoring**: YES (candidate-freeze-before-fresh.json dfc7e837...; ENGINE_CHANGES_ALLOWED=false thereafter).
31. **Fresh fixtures**: 120 (40 CLEAN_DETERMINISTIC / 40 REQUIRED_ABSTAIN / 40 ADVERSARIAL_MIXED).
32. **Engine queries during authoring**: 0.
33. **Disputed fixtures removed**: 0 (pass-1/pass-2 full agreement).
34. **Disputed fixtures retained**: 0.
35. **Gold provenance**: INTRA_ANNOTATOR_REPEATABILITY - same annotator, two passes (pass-2 traced frozen rule semantics per fixture before engine execution); no model calls.
36. **Gold SHA**: 133993c2511e22e77bb35d3bf55c3a7ab4a9ce7eef27109111ef4cc00513929c.

## 37-54. Official one-shot results

37. **Overall precision**: 1.0 (59/59 non-ABSTAIN correct).
38. **Route precision**: 1.0 (gate >=0.99 PASS).
39. **Overall coverage**: 49.2% correct non-ABSTAIN of 120; 50.8% abstain rate - conservative by design, utility gated by the CLEAN stratum.
40. **REQUIRED_ABSTAIN N**: 40.
41. **Unsafe non-abstain**: 0 (hard zero-gate PASS).
42. **CLEAN_DETERMINISTIC N**: 40.
43. **Clean correct coverage**: 1.0 (gate >=0.80 PASS).
44. **Clean precision**: 1.0 (gate >=0.99 PASS).
45. **Adversarial precision**: 1.0 (19/19; gate >=0.98 PASS).
46. **Quote subgroup**: n=13, prec 1.0, coverage 0.46.
47. **Parenthetical subgroup**: n=6, all ABSTAIN correct.
48. **Mixed-polarity subgroup**: n=7, all ABSTAIN correct.
49. **Hedge-competition subgroup**: n=6, all ABSTAIN correct.
50. **Multi-candidate subgroup**: n=6, all ABSTAIN correct.
51. **Retraction subgroup**: n=12, prec 1.0, coverage 0.50.
52. **Cross-clause subgroup**: n=2, all ABSTAIN correct. (Inventory subgroup: n=8, prec 1.0, coverage 1.0.)
53. **Safety false deterministic**: 0.
54. **Evidence-span validity**: 1.0.

## 55-61. Freeze and diagnostic replay

55. **Candidate frozen**: YES - boundary-preclassifier-v1-6a3, manifest SHA 0fedd38b5aa680a891dd9e16307e5de200cd3e06464789b8393580d4d71bcd00.
56. **Manifest SHA**: 0fedd38b5aa680a891dd9e16307e5de200cd3e06464789b8393580d4d71bcd00.
57. **V1.4 diagnostic replay**: run once over burned 100-row benchmark; 0 full three-dimension deterministic resolutions; 100% judge-required under conservative definition; all 19 historical model misses flagged by >=1 abstain dimension.
58. **Historical misses boundary-resolved**: 19/19 captured by abstain; 3 rows (R-12, R-16, R-18) had route-deterministic pre-classifier labels - registered as unresolved diagnostic risk (gold re-adjudication forbidden), not adjudicated errors.
59. **Remaining semantic judge workload**: all safety dimensions (critical/forbidden) plus every row with >=1 abstain dimension; effectively full adjudication remains, reduced only in sub-adjudication where all dimensions resolve.
60. **Estimated judge-call reduction**: 0% full-call reduction; reducible sub-adjudication share 0% on V1.4 (route dim resolved on only 6/100 rows). Honest estimate - the pre-classifier is a boundary gate, not a judge replacement.
61. **Semantic judge calls**: 0 (hard gate; entire task was model-free).

## 62-68. Terminal

62. **V1.6B run**: NO.
63. **Product runtime changed**: NO.
64. **Gates passed**: 8/8 official hard gates; all burned cascade gates; TDD RED->GREEN; unit suite.
65. **Gates failed**: none.
66. **STATUS**: V1_6A3_BOUNDARY_PRECLASSIFIER_READY (TASK-LOCK).
67. **Is V1.6B justified?**: Not by this task's data alone. The five ambiguity families are now deterministically gated; V1.6B rescreen should be justified by the V1.6A.2-known model weaknesses plus the 3 route-deterministic-on-miss rows (R-12/R-16/R-18) as future model-side R&D input - not as contract work.
68. **Recommended next bounded stage**: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6B-RESCREEN (separate task, per contract section 46), with the pre-classifier integrated as a deterministic first-stage gate; model-side analysis of R-12/R-16/R-18 as preregistered diagnostic targets.

## Deviations (permanent disclosure)

- **A1**: TDD RED was reconstructed after the patch existed (TDD_SEQUENCE_DEVIATION=TRUE, checkpoint 3). Disclosed permanently; did not alter frozen candidate, scoring basis, or holdout data.
- **A2**: Disclosed template-frame overlaps with historical corpora (273 generic 4-grams; 0 exact/normalized reuse) - disputed-fixture-registry.json.
- **A3**: burned-v1-4-diagnostic-replay.json amended after first write (false_deterministics definition): the preregistered narrow definition was non-falsifiable by construction; operationally meaningful route_deterministic_on_model_miss (3 rows) added with full note. No gold re-adjudication; engine and fixtures unchanged; file SHA before amendment recorded in official-validation run inputs.

## Stop condition

STOPP. No semantic judge calls, no V1.6B, no model rescreen, no product runtime changes, no fresh product holdout, no further fixtures. Next stage is a separate task.
