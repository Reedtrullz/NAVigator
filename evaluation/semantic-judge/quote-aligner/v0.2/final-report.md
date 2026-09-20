# SLUTTRAPPORT - Semantic Judge Lexical Coverage Repair (v0.2)

Generated: 2026-09-02. Engine: `polarity_engine_v02.py` + `domain-lexicon.json` (deterministic, zero model calls). All artifacts under `evaluation/semantic-judge/quote-aligner/v0.2/`; frozen v0.1 root untouched.

## 1. Task-lock

`task_id == SEMANTIC-JUDGE-LEXICAL-COVERAGE-REPAIR`. Confirmed: no holdout-v3, no blind recertification run, no live-dialog, no kommune-research, no NAV-research, no LLM-runtime in the loop, max two general implementation iterations (both spent; engine converged). See `TASK-LOCK.json`.

## 2. Baseline

v0.1 (qa05, frozen): minimal-pairs acc 0.7083 / contraP 0.6667 / insufR 0.8462 / fpSup 0; contra-insuff acc 0.7681 / contraP 0.9583 / insufR 0.9375 / fpSup 1; modality acc 0.7667; actor-scope acc 0.6333; locality acc 0.9; diagnostic-20 acc 0.65 / fpSup 2; ENT 3/4; review rate 50.7% (110/217 over the 6 main sets). 59 misses total.

## 3. Full error taxonomy

59 misses classified in `error-taxonomy.md` (this directory, copied from root): ACTOR_ALIAS 9, ANTONYM_GAP 7, EXHAUSTIVENESS 6, PREDICATE_PARAPHRASE 5, MORPHOLOGY 5, NEGATION_SCOPE 4, TEMPORAL_BINDING 4, NUMERIC_BINDING 3, LEGAL_PHRASEOLOGY 3, TOO_BROAD_MATCH 3, MODALITY_STRENGTH 3, SYNONYM_GAP 3, plus one each of COMPOUND_PREDICATE, EXCEPTION_SCOPE, CONDITIONAL_SCOPE, PRONOUN_REFERENCE.

## 4. Pareto-funn

Top-5 categories = ACTOR_ALIAS + ANTONYM_GAP + EXHAUSTIVENESS + PREDICATE_PARAPHRASE + MORPHOLOGY = 54.2% of all misses (top-3 = 37.3%). Five general mechanisms (exhaustive-list membership, negation-scope/criteria negation, scalar free/pay binding, staff-membership actor grounding, morphology/compound stems) drive the bulk of the repair.

## 5. ENT-D root cause

Claim "ADHD-diagnose kan stilles av helsesykepleier på skolen" vs source "Skolehelsetjenesten ... stiller ikke diagnoser". The negated predicate `stiller ikke diagnoser` does not lexically reach the paraphrased claim actor/predicate path with enough exact overlap to construct a contradiction proof; exact-lexical rules correctly refuse to guess, and the fallback is INSUFFICIENT_EVIDENCE. Deterministic ceiling: needs paraphrase-level entailment, i.e. the hybrid review layer.

## 6. Lexicon architecture

Single JSON (`domain-lexicon.json`) with typed groups: concepts (polarity axes with rationale), synonym_groups, antonym_pairs, actor_aliases (subset/superset/staff_of), disjoint_actors (with rationale), function_families (via predicate-map), length_check guard metadata. Every entry is generic domain language; no benchmark-specific strings (see point 45).

## 7. Predicate canonicalization

Concept axes (free_of_charge, referral, diagnose_competence, treatment, signature, benefit-condition) reduce surface predicates to polarity-compatible axes; `utrede`/`kartlegge` intentionally NOT merged with `stille diagnose` (competence vs assessment distinction).

## 8. Polarity model

Concept-level: same concept + same polarity = support-compatible; opposite polarity on shared axis = contradiction; unresolved = insufficient. Modality relation (`må/bare` > `kan` > `kan ikke`) gates support rescue: a source that is modally weaker than the claim can never rescue it (CLAIM_STRONGER veto).

## 9. Morphology

4-char stem matching for tokens, 5-char for synonym groups, plus explicit ASCII-Norwegian variants (aa->å, maa, faar, boer) for modal normalization. Actor matching now requires standalone tokens (see point 19), not compound-prefix matches.

## 10. Synonym model

Synonym groups with rationale (gratis/kostnadsfri, råd/veiledning, utreder/undersøker, henvisning/henvise). Applied only after stem-normalization, never across negation boundaries.

## 11. Antonym model

Explicit antonym pairs (full/halv, permanent/midlertidig, gratis/koster, med/uten) plus axis-driven antonymy (free vs pay). Negation-parity gate prevents opposite-polarity matches across differing negation states.

## 12. Legal phraseology parser

Legal-phrase coverage is axis-based (rights, consent, taushetsplikt via generic lexicon) rather than a dedicated parser. Novel-40 shows this is the weakest area (2/6 first exposure, point 35) - a real parser would be hybrid-layer work.

## 13. Condition handling

Condition markers (hvis, dersom, ved, for, date/soknad guards) prevent unconditioned support rescue; condition-bearing claims with unconditioned sources stay INSUFFICIENT.

## 14. Exception handling

Exception markers (unntak, bortsett fra, med unntak) gate universal claims; exception-vs-source mismatches block support rescue.

## 15. Actor aliases

Subset/superset alias map (fastlege subset of lege, helsesykepleier subset of skolehelsetjenesten, foreldre subset of familier, kommunepsykolog = psychologist family, PPT/BUP/NAV/Husbanken/barnevern) plus staff_of relations (har lege som gir X grounds lege i Tjeneste kan X).

## 16. Service aliases

Service-level alias families (skolehelsetjeneste/helsestasjon; BUP vs PPT; NAV vs Husbanken kept disjoint) with disjoint-pair guards for recipient/payer substitution.

## 17. Pronoun handling

Not implemented (1 baseline miss, PRONOUN_REFERENCE, documented residual). Exact-lexical design cannot resolve anaphora safely; left to hybrid layer.

## 18. Compound predicate handling

Compound predicates matched via synonym-group part-matching (foreta helseundersøkelse = perform + helseundersøkelse group) and compound actor names are no longer confused with actor tokens (foreldresamtale is not foreldre).

## 19. Sentence/span matching

Quote aligner returns ranked candidate sentences; gates operate on the aligned span only. New in v0.2: actor-token hits for disjoint guards must be standalone tokens (punctuation stripped, length <= actor+2 chars), and complementary mentions (claim actor also present in sentence, e.g. administreres av Husbanken og krever soknad gjennom NAV) do not fire actor-substitution guards.

## 20. Hard blockers

ENT-D paraphrase entailment; direction-aware old/new-rules regime logic (MP-015A); kun-presence condition on source-side exhaustive lists (CI-046); date-phrase enum scope (MP-009A); compound-aggregate support (MP-008A). All documented, none bypassed with claim-specific rules.

## 21. Support proof

Support = aligned span with matching polarity across all claim atoms + gate survival (scope, modality, negation, exhaustiveness, condition, actor). Every SUPPORT is quote-grounded; rescue paths are veto-gated.

## 22. Contradiction proof

Contradiction = axis polarity opposition, negation-scope exclusion, scalar bound conflict, exhaustive-list exclusion, or division-of-function (function family marker on claim actor's sentence + other-actor sentence carrying the reserved function, e.g. BUP utreder psykiske lidelser vs PPT claim). The `_guard_fd` guard no longer demotes division-of-function CONTRAs when a different-actor sentence carries the function's `other_markers`.

## 23. Iteration A

Twelve general changes: modality gate in support rescue; ASCII modal normalization (boer->bør etc.); negation-parity in same-object negation; SUPPORTED-branch contradiction check; free_of_charge payer-axis guard; `_PASS_VETO` narrowed to PREDICATE_GROUNDING_UNVERIFIED; uncovered-content gates in rescue; PLACE_CONFLICT never veto-explained; Oslo/Trondheim place guard; kun/bare rescue gate; son-empty veto-aware gate; lexicon perform += foreta helseundersøkelse.

## 24. A-resultater

Probe misses fixed 39->51/58; regressions 30->0. Full suite: mp 0.9583, ci 0.9855, modality 0.9667, actor 0.9667, locality 1.0, d20 0.95, fpSup 0 (d20: 1). ENT temporarily regressed to 1/4 (ENT-A + ENT-C) - handled in Iteration B.

## 25. Iteration B nødvendig?

Ja: ENT-A og ENT-C var i feil tilstand etter Iteration A (1/4 vs baseline 3/4), så en målrettet B-iterasjon var påkrevd og tillatt.

## 26. Iteration B

Three changes: (1) standalone-token actor matching in `_dest_adjacent_disjoint` (compound words like foreldresamtale no longer stem-match foreldre; punctuation stripped before length check; complementary mentions exempt). (2) `_guard_fd`: division-of-function guard suppressed when a different-actor sentence carries the family's other_markers (ENT-C keeps CONTRADICTED). (3) no lexicon additions - pure logic fixes.

## 27. B-resultater

Probe 52/58 (ACT-08 fixed as side effect of the compound fix); 0 regressions, 6 residuals; ENT 3/4 restored (A SUPPORTED, B INSUFF, C CONTRADICTED, D INSUFF); suite: mp 0.9583, supplement 0.75, ci 0.9855, modality 0.9667, actor 1.0, locality 1.0, d20 0.95, fpSup only d20=1.

## 28. Minimal pairs total

45/48 = 93.75% raw; harness accuracy 0.9583 over graded rows (3 residuals: MP-008A, MP-009A, plus MP-015A in the supplement set). Target >=95%: met at 0.9583 on minimal-pairs alone; supplement set 3/4 (0.75, n=4).

## 29. Minimal pairs per dimension

modality 7/8, negation 4/4, scope 12/12, actor 13/13, numeric 4/4, temporal 6/7. High-confidence errors: none.

## 30. Contra precision

minimal-pairs 1.0, contra-insuff 0.9737, modality 1.0, actor-scope 1.0, locality 1.0, diagnostic-20 1.0. Target >=97%: met on every set.

## 31. Insuff recall

minimal-pairs 1.0, contra-insuff 0.9688 (target 0.97: 1 below), modality 1.0, actor-scope 1.0, locality 1.0, diagnostic-20 0.8 (below). Honest miss: gate target not fully met.

## 32. Source entailment A-D

ENT-A SUPPORTED (fixed in B), ENT-B INSUFFICIENT_EVIDENCE, ENT-C CONTRADICTED (fixed in B), ENT-D INSUFFICIENT_EVIDENCE (expected CONTRADICTED - known deterministic ceiling). Result 3/4.

## 33. ENT-C

Root cause of the v0.2 regression was `_guard_fd` firing unconditionally when the claim's function family appears nowhere as a claim marker; the BUP sentence (utreder psykiske lidelser) is positive evidence of the division of function, so the guard must not demote the CONTRA. Fix generalized: different-actor sentences with other_markers suppress the guard. MP-004B/ACT-05 (same-actor, no other-actor evidence) keep guard firing - verified.

## 34. ENT-D

See point 5. Not fixed; documented as the deterministic ceiling case motivating the hybrid architecture.

## 35. Novel development-40

`novel-development-set.json` marked `DEVELOPMENT_ONLY_NEVER_BLIND_CERTIFICATION`, 40 cases across 6 categories, run once on first exposure, then NOT tuned (stop rule; tuning would be a third iteration and overfitting): 27/40 = 67.5%. Per category: actor 6/6, synonym 8/10, condition 4/6, locality 4/6, antonymy 3/6, legal 2/6. Results in `results/qa06-novel-dev.json`; rerun via `check_novel_dev.py`.

## 36. Safety result

Safety false-support: 0 across all sets.

## 37. Numeric result

Numeric false-support: 0; minimal-pairs numeric dimension 4/4.

## 38. Temporal result

Temporal false-support: 0; minimal-pairs temporal dimension 6/7 (MP-009A date-scope enum residual is documented separately).

## 39. Actor/locality

actor-scope 30/30 (1.0), locality 20/20 (1.0), both with contraP 1.0 and fpSup 0.

## 40. Review/no-evidence rate

v0.2 review rate 35.0% (76/217) vs v0.1 50.7% (110/217) on the 6 main sets: -31% relative. INSUFFICIENT verdicts 38.9% vs ~52% v0.1. Still high - the deterministic engine is conservative by design.

## 41. v0.1 vs v0.2

| Set | Metric | v0.1 | v0.2 |
|---|---|---|---|
| minimal-pairs (48) | acc / contraP / insufR / fpSup | 0.7083 / 0.6667 / 0.8462 / 0 | 0.9583 / 1.0 / 1.0 / 0 |
| supplement (4) | acc | 0.5 | 0.75 |
| contra-insuff (69) | acc / contraP / insufR / fpSup | 0.7681 / 0.9583 / 0.9375 / 1 | 0.9855 / 0.9737 / 0.9688 / 0 |
| modality (30) | acc / contraP | 0.7667 / 0.8 | 0.9667 / 1.0 |
| actor-scope (30) | acc / contraP / fpSup | 0.6333 / 0.0 / 1 | 1.0 / 1.0 / 0 |
| locality (20) | acc | 0.9 | 1.0 |
| diagnostic-20 (20) | acc / fpSup | 0.65 / 2 | 0.95 / 1 |
| ENT (4) | pass | 3/4 | 3/4 |
| Review rate (6 sets) | share | 50.7% | 35.0% |
| Determinism (5 runs) | identical | yes | yes (225 cases) |
| Probe misses fixed | /58 | 5/58 | 52/58 |

## 42. Burned holdout-v2 development result

Holdout-v2 was consumed during v0.1 development (prior task); qa05 numbers above are its development-burned state. No holdout-v3 was built or run (spec 44); the novel-40 set (point 35) is the only new evaluation surface and is marked development-only.

## 43. Deterministic reproducibility

5x full determinism over all 7 benchmark sets + ENT: 225 cases, verdicts identical across every run (100%). Artifact: `results/qa06-determinism.json`; rerun via `check_determinism.py`.

## 44. Runtime model-call count

0. The engine and all QA runs are pure Python + JSON; no LLM calls anywhere in the pipeline.

## 45. ID guard

0 violations (`check_id_guard.py`): no claim IDs, no testcase IDs, no literal benchmark claims in runtime code or lexicon. Length check: 13 strings >60 chars, all documentation/rationale fields, none matchable phrases. Spec 35 met.

## 46. KB regression

48/48 BESTATT, 0 FEILET (`evaluation/score_baseline.py`, re-run live this session).

## 47. Evaluator regression

acc 1.00 (TP=24 TN=96 FP=0 FN=0), safety_FP=0, subtle_FP=0, mean_score=5.00 (`evaluation/evaluator-regression/run_evaluator_regression.py`).

## 48. qa_check.sh + tests

`scripts/qa_check.sh`: OK (no known error strings). Quote-aligner test suite `tests/test_polarity_engine.py`: ALL PASS (incl. determinism check). All benchmark JSON outputs written and valid under `v0.2/results/qa06-*`.

## 49. Critical/high-confidence errors

None. Every graded set reports empty `high_confidence_errors` (confidence >=0.95 errors). All residuals are conservative (INSUFF/PARTIAL) except the single documented D20-C4 false SUPPORT.

## 50. READINESS

**NOT_READY_FOR_BLIND_RECERTIFICATION.** Failing gates: source-entailment 3/4 (<4/4), insufficiency recall 0.9688 contra-insuff and 0.8 diagnostic-20 (<0.97), 1 diagnostic-20 fpSup. Passing: minimal-pairs >=95%, contraP >=97%, safety/numeric/temporal FP 0, determinism 100%, evaluator clean, KB 48/48, id_guard 0.

## 51. Eksakte gjenværende svakheter

1. ENT-D paraphrase entailment ceiling. 2. MP-008A compound-aggregate support (PARTIAL vs SUPPORT). 3. MP-009A gjelder-fra date-phrase enum misfire. 4. MP-015A direction-aware old/new-rules regime. 5. CI-046 source-side kun-presence for exhaustive lists. 6. MOD-14 lexical gap (delta i undersøkelsen ~ deltakelsen). 7. D20-C4 reiseutgifter til lege vs utgifter til behandling (demotion verified to break 4 gold atoms). 8. Novel-40 generalization gaps: legal phraseology (2/6), antonymy (3/6), condition (4/6) on first exposure.

## 52. STOPP eller fortsett?

**Deterministic lexical R&D STOPPER her** (two iterations spent, converged). Further lexical additions would be blind test-tuning: the novel-40 first-exposure score of 67.5% shows the exact-lexical approach generalizes only partially, and the remaining misses (legal phraseology, paraphrase entailment, regime logic) are not fixable by more synonyms without overfitting risk.

## 53. Anbefalt neste steg

Implement the hybrid architecture: deterministic exact rules -> quote aligner -> high-confidence proof -> else REVIEW_REQUIRED, with a semantic review layer for REVIEW cases only. Then, as a separate later task, run blind re-certification on a fresh holdout (not holdout-v3). Suggested first scope for the review layer: legal-phraseology and paraphrase-entailment cases (ENT-D family), where the deterministic ceiling is structural.
