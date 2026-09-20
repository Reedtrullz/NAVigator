# Semantic Judge v0.4.1 - Sluttrapport (stability repair)

Dato: 2026-09-01. Kjoring: gpt-5.6-luna (judge C), serial, proxy 127.0.0.1:10100.
Alle LLM-baserte resultater i denne rapporten er ferske kjoringer under sluttkode
(relation prompt SHA256 2206dd->b6890edc, decompose prompt uendret 072a24b1).
Resultater fra Iteration A er arkivert under results/iterationA-archive/ og *.bak.

## Pre-flight og laas

1. **TASK-LOCK**: SEMANTIC-JUDGE-V0.4.1-STABILITY-REPAIR, ACTIVE, allowed_area respektert. Pre-flight A/B/C/D: YES/YES/NO/YES.
2. **Kommunepsykolog-goal 42b50c52**: lest og ignorert som stale historikk (forbidden_goal_id i TASK-LOCK). Ingen kommunal research utfoert (files 25-27 ikke aapnet, ikke re-verifisert, ingen nye kommuneeksempler).
3. **HV2-049 audit**: utfoert tidligere i oppgaven (se hv2-049-audit.md); fant ingen testcase-spesifikke patches.
4. **Root cause 5 stability-wobbles** (Iteration A): fragmenterte verdict-adaptere uten vedvarande primitiver; se stability-wobble-rootcause.md.
5. **Root cause 12 minimal-pair misses** (Iteration A): negasjonspolaritet, autoritetsreferent, datarolle, eksklusivitet; se minimal-pair-misses-rootcause.md.

## Arkitektur

6. **v0.4.1 arkitektur**: LLM dekomponerer -> LLM trekker ut praimitiver (ingen verdict) -> deterministisk adjudikator -> deterministisk aggregasjon. Ingen claim-id-logikk.
7. **Praimitiv skjema**: 30+ felt (polaritet, modalitetstriggere, numerisk, temporal, scope/locality, aktor/enum, struktur). relation_type er derivat, ikke LLM-output.
8. **Relasjonsnormalisering**: polarity flags atom-scoped; negation-agreement = SUPPORT; eksklusjonsvakter; evidence-krav paa konflikt.
9. **Modality normalizer**: verbatim trigger -> MAY/MAY_OMIT/MUST/ENTITLED/MAY_BE_ENTITLED/USUALLY/SHOULD/NEVER/NOT_REQUIRED/ALWAYS/UNKNOWN.
10. **Modality matrix**: SAME/CLAIM_WEAKER/CLAIM_STRONGER/CONFLICT; Iteration B laa til MAY_OMIT-vs-plikt = CONFLICT og universal-vs-saerlige-tilfeller = CONFLICT.
11. **Scope/locality**: BROADER hefter for hedge-clause; NAMED->NATIONAL generalisering blokkeres; eksistens/variasjon-utsagn ikke refuterbart av enkeltkilde.
12. **Aktor/enumeration**: EXHAUSTIVE kun naar kilden selv markerer uttommende liste; outside-enum + EXHAUSTIVE = CONFLICT med evidence-krav.

## Iterasjoner

13. **Iteration A**: negasjon, autoritetsarv, dato-roller, eksklusivitet, scope-gates, NON_EXHAUSTIVE-vern, locality eksistensvern. (Basis for 90.38% pairs / 83.33%->70% stoettestuktur.)
14. **Iteration A metrikk** (arkivert): pairs 47/52, modality 26/30, CI 56/69, actor 25/30, locality 19/20.
15. **Iteration B noedvendig?** JA: modality 86.67% < 90% maal (par 21).
16. **Iteration B** (utfoert): (a) deterministisk: MAY_OMIT-normalisering (kan velge aa droppe/fravaelge/...) + universal-vs-saerlige-tilfeller-konflikt i modality.py; (b) prompt: full modalkonstruksjon som trigger + konfliktobserasjon krever verbatim contradiction_evidence. Ett samlet arkitekturbeltove, ingen nye per-case-regler.
17. **Iteration B metrikk** (fersk, alle bencher re-kjoert): se punkt 22-27. Modality 29/30 (96.67%).

## Ferske resultater (sluttkode, Luna)

18. **Dekomponering**: 43/44 (DEC-008 flakrer run-to-run, historisk 6/7 pass paa identisk prompt; dokumentert variasjon).
19. **Compound**: deterministisk aggregasjon selftest 8/8; PARTIALLY kun for blandede compound.
20. **Kontradiksjonspresisjon**: 25/26 = 96.15% (maal >=95 PASS).
21. **Insufficiency recall**: 31/32 = 96.88% (maal >=95 PASS).
22. **Modality**: 29/30 = 96.67% (maal >=90 PASS; MOD-10 eneste miss, ekstraksjonsflakring).
23. **Actor**: 24/30 = 80.00% (6x no_explicit_affirmation - prosess-impliserer-aktor er fortsatt ekstraksjonssvaakhet).
24. **Locality**: 17/20 = 85.00% (LOC-04 span-tap, LOC-09/13 + D20-L5 locality-opplaasing).
25. **Minimal pairs overall**: 48/52 = 92.31% (maal >=90 PASS; main 45/48, supplement 3/4).
26. **Minimal pairs per dimensjon**: actor 13/13, negation 6/6, temporal 8/9, scope 11/12, modality 7/8, numeric 3/4.
27. **Diagnostic-20**: 16/20 = 80.00% (DEVELOPMENT_ONLY_NEVER_CERTIFICATION; 2 konflikt-obserasjoner uten span D20-M1/A4, 1 locality-opplaasing D20-L5, 1 graatone D20-M4 boer-vs-skal).

## Stabilitet (30 claims x 5 runs = 150 rader, 0 run-errors)

28. **Full stability verdict consistency**: 70.00% (modal) - v0.4-baseline 83.33%. MAAL >=95 FAIL.
29. **Praimitiv stabilitet**: subject/scope/time/actor match 100%; relation 60%; relation_type 70%; modality_relation 83.3%; numeric_relation 83.3%; negation_relation 70%.
30. **Final verdict stability**: 21/30 ids heelt konsistente; 9 wobble-ids (CAL007 S<->P, CAL012/013 I<->S, CAL035/039/067/079 I<->C, CAL048/054 P<->I/C).
31. **Safety flips**: 2 (CAL039, CAL067, I<->C). Maal = 0 FAIL.
32. **Numeric flips**: 1 (CAL007, S<->P via near-miss; ingen S<->C). Maal S<->C = 0 PASS teknisk, men tellekravet i par 26 er ikke oppfylt for sikker rapportering.
33. **Temporal flips**: 0 PASS.
34. **REVIEW_REQUIRED-rate**: 76.5% (345/451 rader; flagget er bredt i aggregasjonsdesignet - ikke feilrate, men behov for menneskelig gjennomgang av compound/near-miss).
35. **Targeted gpt-5.5 eskalering**: IKKE kjoert. Begrunnelse: stoppregelen (par 31) traff foer eskalering kunne endre utfallet; roet er ekstraksjons-side (dokumentert over), og par 31 forbyr videre tuning/iterasjoner.
36. **Burned holdout-v2 (development check)**: 71/80 = 88.75% (v0.3: 81.25, v0.4 Luna: 91.25, v0.4.1 Luna: 88.75). Aldri blind sertifisering.

## Anti-regresjon og QA

37. **ENT-C/D**: ENT-D (hard safety) CONTRADICTED = PASS. ENT-C INSUFFICIENT (tidligere CONTRADICTED) = regresjon under strengere polaritetsprompt, klassifisert under par 47.
38. **Injections**: CAL088 (source-injection) = SUPPORTED i 5/5 stability-runs PASS; injection-kontrakt (loud CONTRADICTED) uendret.
39. **Evaluator regression**: acc 1.00, 0 FP/FN, safety_FP=0 PASS.
40. **KB 48-regresjon**: 48/48 BESTATT PASS.
41. **id_guard**: 0 treff (ingen testcase-id-logikk) PASS.
42. **qa_check.sh**: OK - ingen kjente feilmnstre PASS.
43. **High-confidence errors**: ingen rader >=0.95 confidence blant feil i minimal-pairs/locality/actor; diagnostic-20 feil ligger 0.7-0.9.
44. **Trade-offs**: Strengere polaritet/evidence-prompt fikset modality (+10pp) og ga best pairs (92.31%), men gjorde ekstraktoren mer konservativ: faerre affirm-flagger ga stability 70% (ned fra 83.33%) og ENT-C-regresjon. Deterministisk kjerne er heelt stabil; all roelse sitter i LLM-polaritet/span-ekstraksjon.
45. **Luna-kall (fersk kjoring)**: ca. 986 (451 rader + 526 relasjonskall + ENT-controls 4 + retry-buffer).

## Lesestatus og videre arbeid

46. **READINESS: NOT_READY_FOR_BLIND_RECERTIFICATION** (par 26-krav: verdict-konsistens 70% < 95%, safety flips 2 > 0, negation/relation-primitiver < 90%).
47. **Gjenvaerende svaakheter**: (a) LLM polaritet/span-ekstraksjon flakrer run-to-run (rot aarsak til all verdict-roelse); (b) prosess-impliserer-aktor og locality-opplaasing under-ekstraheres; (c) ENT-C neytralitet-regresjon; (d) DIAG-settet viser konflikt-uten-span-hull i 2/20.
48. **Anbefalt neste steg (par 33-valg: C - mer deterministisk semantisk ekstraksjon)**: flytt polaritetsbeslutning fra LLM til deterministisk lag ved aa la ekstraktoren levere verbatim sitater (claim-span + source-span) og la en deterministic aligner avgjore affirm/negate/silent fra sitatene. Det fjerner den eneste gjenvaerende roelekilden uten ny prompt-tuning. Ikke start dette naa (stopperegel); ikke lag v0.4.2/v0.5, ikke holdout-v3, ikke blind re-sertifisering, ikke live-dialog.

## Leveranser

- Kode: semantic_judge_v041.py, adjudicator_v041.py, modality.py, run_benchmarks.py (final: git-diff mot Iteration A arkiv).
- Resultater (fersk, sluttkode): results/v041-results-{minimal-pairs,minimal-pairs-supplement,contra-insuff,modality,actor-scope,locality,diagnostic-20}-C-judge-c-gpt-5.6-luna.json + grade-filer.
- Stabilitet: results/v041-results-stability-C-judge-c-gpt-5.6-luna.json (150 rader), results/metrics-stability-v041.json.
- Holdout-v2 dev: results/v041-results-holdout-v2-C-judge-c-gpt-5.6-luna.json, results/metrics-holdout-v2-v041.json.
- ENT-controls: results/v041-results-ent-controls-C-judge-c-gpt-5.6-luna.json.
- Diagnostic-20: benchmarks/diagnostic-20.json (DEVELOPMENT_ONLY_NEVER_CERTIFICATION).
- Arkiver: results/iterationA-archive/, *.iterationA.bak, *.pre-repair.bak, prerepair-*.
- Logger: results/suite-v041-C.log, results/stability-v041-C.log, results/holdout-v2-v041-C.log.
