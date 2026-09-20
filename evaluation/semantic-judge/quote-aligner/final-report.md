# Sluttrapport: Deterministic Quote-Aligner / Polarity Engine (v0.5-prototype)

Statusdato: 01.09.2026. Deterministisk prototype i
evaluation/semantic-judge/quote-aligner/. Null modellkall i motor eller
harness. Frosne v0.2/v0.3/v0.4/v0.4.1 er uendret (read-only). Denne
rapporten erstatter ikke semantic-judge/final-report.md (v0.2 pilot),
den dekker quote-aligner-tasken.

1. **Task-lock/pre-flight.** TASK-LOCK.json: task_id
   SEMANTIC-JUDGE-DETERMINISTIC-POLARITY-ALIGNER, status ACTIVE,
   forbidden: municipal-research, holdout-v3, blind-recertification,
   live-dialog, semantic-prompt-tuning. Goal-objekt 42b50c52 (kommunal
   research) er underlagt forbidden og ikke kjort.
2. **v0.4.1 wobble-audit.** polarity-wobble-audit.md: 9/30 stabilitets-ID-er
   wobblet (Luna ekstraksjonsflagg affirm/negate); 7/9 losbare
   deterministisk fra span-signaler, 2/9 fusionsavvik. Motordesignet er
   utledet herfra (sekt 5-24 i spec).
3. **Root cause polarity.** Eneste rullekilde i v0.4.1 var LLM-ekstraksjonens
   aff/neg-flagg. Quote-aligner eliminerer kilden: polarity utledes av
   tekstsignaler i span-alignment, ikke av flagg.
4. **Quote-aligner architecture.** Se architecture.md: atom-splitting ->
   harde contra-regler -> myke signaler -> polaritet -> numerisk ->
   support-gate med claim-strength-vetoer -> aggregering.
5. **Claim representation.** Claim splittes i atomer (konjunksjon uten
   eksklusiv eller; eller med disjoint aktorer = egen contra-regel).
   Hvert atom bedommes separat; aggregering folger v0.3 regel 1-5.
6. **Source-span representation.** Source beholdes som normalisert heltekst;
   alignment skjer mot hele teksten (kandidatvinduer i quote_aligner).
7. **Norsk normalisering.** aa/Ar -> breveformer, verb (gjeld/gjelder),
   canon-synonymer (helsesykepl* -> skolehelsetjeneste).
8. **Negation engine.** Negasjons-scope med claim_effective_neg,
   NOT_REQUIRED-former; unntaksformer (uten X) hoppes over i
   polaritetskonflikt.
9. **Negation-scope tests.** Enhetstester 11/11 PASS
   (tests/test_polarity_engine.py, inline tekster).
10. **Numeric alignment.** Verbatim-tallpareitet, sjekk av
    beregningsgrunnlag, akser (kostnad/revers), APPROX-markorer.
11. **Temporal alignment.** Tidspunkt/frister alignes mot source;
    temporal-subgruppen 7/8 i contra-insuff.
12. **Modality alignment.** Gjenbruker frosne v0.4.1 modality.py +
    modality-map.json; skal/bor (OBLIGATION_WEAKENED), may/must/kan.
13. **Predicate map.** predicate-map.json: medisinsk <-> pedagogisk ->
    INSUFF (predicate swap), ikke falsk SUPPORT.
14. **Predicate opposition.** Antonym-par (full/halv, permanent/midlertidig,
    gammel/nye) gir modifier-antonym-signal; kjent false-CONTRA-tak pa
    unicode-tekst (MP-015A).
15. **Exhaustiveness handling.** Eksklusive eller-lister: medlem + disjoint
    aktor = CONTRA; ukjent eksklusivitet = INSUFF, ikke falsk SUPPORT.
16. **Proof-object format.** Se architecture.md: verdict, confidence,
    injection_detected, review_required, atom_results, atoms.
17. **Support-proof logic.** SUPPORTED krever hard evidence: verbatim span,
    numerisk likhet eller full predikat-alignment; alle claim-styrke-vetoer
    maa passeres.
18. **Contradiction-proof logic.** CONTRA krever eksplisitt spenn: negasjon,
    alder-disjunksjon, universal mot eksistens-negasjon/unntak, eller
    eksklusiv liste-konflikt.
19. **NO_EVIDENCE logic.** Ingen alignbart spenn = INSUFFICIENT_EVIDENCE
    (no_deterministic_signal), aldri SUPPORT.
20. **AMBIGUOUS/REVIEW logic.** review_required settes per atom ved svake
    signaler; review-rate 37,9 % (142/375 rader) - konservativ terskel.
21. **Deterministic-only coverage.** Alle 8 bench + ent + stability kjorer
    deterministisk; ingen LLM-quote-finder i denne prototypen.
22. **Deterministic-only accuracy.** Se tabell under pkt 25-27.
23. **Luna quote-finder coverage.** 0 % (ikke implementert - deterministisk
    prototype dekker hele flyten uten modell).
24. **Luna quote fidelity.** Ikke relevant (ingen LLM-spans); verbatim-sjekk
    er implementert i support-gate for fremtidig hybrid-bruk.
25. **Contradiction precision.** minimal-pairs 0.6667; contra-insuff 0.9583;
    modality 0.80; diagnostic-20 0.6667; ent/stability 1.0.
26. **Insufficiency recall.** minimal-pairs 0.8462; contra-insuff 0.9375;
    modality 1.0; diagnostic-20 0.60; ent/stability 1.0.
27. **Minimal-pair score.** 34/48 = 0.7083 (gate-krav >= 0.95 - IKKE
    oppnadd).
28. **Negation subgroup.** minimal-pairs negation 4/4; supplement negation
    2/2; contra-insuff negation 9/10.
29. **Numeric subgroup.** minimal-pairs numeric 2/4; contra-insuff numeric
    6/10; stabil pa verbatim-paritet (CAL007/012/013-monstre loset).
30. **Temporal subgroup.** minimal-pairs temporal 4/7; contra-insuff
    temporal 7/8; supplement temporal 1/2.
31. **Modality subgroup.** modality-bench 23/30 = 0.7667; de sterkeste
    monstre (may vs must, never vs required, not required) 100 %.
32. **Actor/locality subgroup.** actor-scope 19/30 = 0.6333 (contraP 0.0 -
    ACT-02-monster); locality 18/20 = 0.90.
33. **Safety result.** fpSup: 0 i minimal-pairs, supplement, modality,
    locality, ent, stability. 4 FP-SUP totalt: D20-M1 (modality),
    D20-C4, ACT-13, CI-047 - ingen safety-kritiske (safety FP = 0).
34. **ENT-C/D.** PASS (C og D = CONTRA, korrekt).
35. **Source-entailment A-D.** A=SUP ok, B=INSUFF ok, C=CONTRA ok;
    D feiler (CONTRA -> INSUFF: synonym-canon alene utloser ikke den
    harde contra-regelen). Gate "ENT-C/D pass" er da formelt IKKE oppfylt,
    selv om C er korrekt. Dette er med i readiness-vurderingen pkt 50.
36. **Deterministic reproducibility.** 100 %: 5/5 identiske run-hasher i
    qa05-results-stability.json (etter hash-fiks: run-teller ekskludert).
37. **Hybrid 30x5 stability.** Ikke kjort (deterministisk run erstatter);
    stability 150/150 = 1.0, 0 wobble-ID-er. Mot v0.4.1: 64 % row-acc,
    9 wobble-ID-er.
38. **Review rate.** 37,9 % (142/375 rader) - hoy; terskel-tuning er
    egen oppgave, ikke gjort i denne lock.
39. **Burned holdout-v2 development score.** v0.3 (LLM-judge): acc 0.8125,
    macro F1 0.8162, binary FP 0/60. v0.4.1 (Luna): acc 0.8875,
    macro F1 0.8905, binary FP 0/60. Quote-aligner er ikke kjort mot
    holdout-v2 (forbudt a utvikle mot den).
40. **v0.4.1 vs quote-aligner comparison.**

    | Bench | v0.4.1 (Luna) | quote-aligner |
    |---|---|---|
    | minimal-pairs | 0.9375 | 0.7083 |
    | mp-supplement | 0.75 | 0.75 |
    | contra-insuff | 0.8116 | 0.7681 |
    | modality | 0.9667 | 0.7667 |
    | actor-scope | 0.80 | 0.6333 |
    | locality | 0.85 | 0.90 |
    | diagnostic-20 | 0.80 | 0.65 |
    | stability (row) | 0.64, 9 wobble | 1.0, 0 wobble |
    | holdout-v2 | 0.8875 / F1 0.8905 | ikke kjort (laast) |
    | Luna-kall pr 100 claims | 100 | 0 |

41. **Luna calls per 100 claims.** 0 (deterministisk motor; null API-kall).
42. **Estimert kostnadsreduksjon.** Ca. 100 % av polarity-steg-kostnad
    (token + latens): polarity-kallet er fjernet, ikke redusert.
43. **Iteration A.** Mislbindings-fjerning + grunnleggende vetoer;
    fullfort og verifisert (arkiv i v0.4.1/results/iterationA-archive/).
44. **Iteration B.** _claim_strength_veto: eksklusivitet, superlativ,
    universal-vs-partitiv, scope-inflasjon, sted, kostnadsakse,
    aktor-familie, fravaerende fagroller, FUNCTION_UNVERIFIED,
    CONDITION_DROP, exemption/age/AUTOMATIC/PREDICATE_GROUNDING-vetoer,
    OBLIGATION_WEAKENED, passive konjunksjoner, predicate-swap-veto.
    Fullfort; alle metrikker over er etter B.
45. **ID guard.** 0 treff i polarity_engine.py, quote_aligner.py,
    run_benchmarks.py, tests/ (monster: CAL/CI-/MP-/ACT-/LOC-/D20-/MOD-/ENT-).
46. **KB regression.** evaluation/score_baseline.py: 48/48 BESTATT,
    exit 0.
47. **Evaluator regression.** acc 1.00, prec 1.00, rec 1.00, FPR 0.00,
    safety_FP 0, subtle_FP 0 (TP=24 TN=96).
48. **qa_check.sh.** OK: ingen kjente feilmnstre funnet. 19/19 JSON-filer
    i results/ validerer.
49. **High-confidence/critical errors.** 0 (ingen atom med confidence
    >= 0.95 paa feil verdict i noen bench).
50. **READINESS:** NOT_READY_FOR_BLIND_RECERTIFICATION.

    Mot grunnene i sec 45-gate: minimal pairs 0.7083 < 0.95,
    contraP (mp) 0.6667 < 0.97, insufR (d20) 0.60 < 0.97,
    ENT-D feiler (CONTRA -> INSUFF).
    Oppfyldte gates: safety FP 0, ENT-C/D pass, determinisme 100 %,
    evaluator/KB-regresjon rene, qa_check OK, stability 1.0.

51. **Gjenvarende svakheter.**

    - CONTRA->INSUFF: CI-004/008/009/011/019/021/023/026/030/032/048/056,
      MP-005B/008B/013B/014B/017B, MOD-23/25/27/29, ACT-02, LOC-04.
      Rot: age-relation krever delt verb; exhaustive-eller kun i
      SUPPORTED-grenen.
    - SUPPORT->INSUFF: ACT-01/04/07/08/17/25, MOD-08/20/28,
      MP-016A/017A/018A, D20-A1/A3, LOC-11: CLAIM_WEAKER + content_hit
      er forenlig med SUPPORT men blokkeres av support-gate.
    - False-CONTRA: MP-015A (modifier-antonym, unicode), D20-A5
      (exclusivity over-fire), MP-024A/B (cost-axis gratis->koster),
      CI-046 (recipient_disjoint), D20-C5 (polarity_conflict).
    - Actor-scope contraP 0.0 (ACT-02: exhaustiv eller-liste utenfor
      SUPPORTED-grenen).
    - D20-M1 FP-SUP (modality veto mangler for MAY mot MUST-kilde).
    - ENT-D: synonym-canon (helsesykepleier -> skolehelsetjeneste) gir
      funksjonsdivision-INSUFF, men utloser ikke hard contra-regel.

52. **Anbefalt neste steg.** Ikke Iterasjon C (iterasjoner brukt, task-lock).
    Forslag til egen, senere task: "targeted lexical-gap stage" -
    avgrenset oppdatering av leksikalske signal-kart (modality-map,
    predicate-map, cost-akse, exhaustiv-eller aktor-liste) uten motor-
    designendringer, etterfulgt av full bench + determinisme-rekjoring.
    Holdout-v3 og blind-re-sertifisering forblir laast til mp >= 0.95
    og contraP/insufR >= 0.97 pa alle relevante bench.
