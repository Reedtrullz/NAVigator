# RC2 SLUTTRAPPORT - NAV-EXPLORE-RC2-ROOT-CAUSE-REPAIR

Maks claim: **RC2_READY_FOR_NEW_BLIND_SET**. Denne rapporten er
IKKE en sertifisering. Alt bruk av Blind V1 er merket
BURNED_BLIND_V1_DEVELOPMENT_ONLY.

1. **Task lock**: TASK-LOCK.json ACTIVE -> COMPLETED; task_id
   NAV-EXPLORE-RC2-ROOT-CAUSE-REPAIR; alle forbidden_tasks respektert.
2. **RC1 official preserved**: RC1-predictions, freeze, sealed key,
   official-score.json uendret. SHA fff9b539...93d72 (full:
   fff9b539b97d414389fbc6198d1ecbc92f546556bbc7374fdbbfa29d5ef93d72).
3. **Burned V1**: 120 core cases brukt til postmortem, regressions,
   band-analyse og shadow; hver artifact bærer burned-marker.
4. **Critical blind failures**: 2 kritiske unsafe AUTO_CONTRADICTED
   (0122, 0131, age-disjoint); 1 runtime (0112); 60 CRITICAL cases;
   RC1 critical product 37/60.
5. **Age-parser root cause**: ranges regex fikk valgfri år-suffiks ->
   "§ 4-3" = [4,3], "FOR-2026-06-25-1361" = [6,25] -> age_disjoint ->
   hard CONTRA (age-parser-audit.md).
6. **Age-parser fix**: år-ord påkrevd i range-regex; nye mønstre
   (mellom/fra-til/N-åringer); enhets-lookaheads; span-dedup.
7. **Age regression results**: law_age_negative + age_positive
   passer; 37/37 total; law_as_age_fp gate = 0.
8. **Numeric-binding root cause**: any-pair same-unit bound
   sammenligning ignorerte qualifier-sett og attestasjon (0005, 0086;
   0003 oppdaget under RC2 via regressionspin).
9. **Numeric-binding model**: qualifier-sett-likhet (full/hel/halv/
   delt/total) + same-subject value-attestation skip + newline som
   phrase-grense; diff-krev-attestasjon fail-closed.
10. **Numeric regression results**: numeric_conjunction /
    agg_component / full_divided alle pass, inkl. ny
    cross-subject-citation pin.
11. **Runtime root cause 0112**: set(...).values() på en mengde
    (set har ikke .values()) -> AttributeError
    (runtime-bug-audit.md).
12. **Runtime fix**: iterer settet direkte; + 4 robustness-cases.
13. **Runtime robustness**: runtime_robust-group pass; 0 uncaught
    exceptions i 120-raders rerun; outcome coverage 100%.
14. **Structural proof validity**: proof-objekt oppfyller sin types
    krav (spans, regel-id, koordinater, ingen injeksjon).
15. **Soundness**: gyldig OG spans Entailer påstanden under regelen
    (ingen misbinding/misquote/universal-snarvei).
16. **Soundness result**: 0 invalid accepted proofs; 0 unsound
    accepted; 0 hallucinated (utviklingskjøringer).
17. **Iteration A result**: 3 rotårsaks-familier fikset; engine
    semantic på burned set 42 -> 52; 10 fixed, 0 regressed.
18. **Iteration A gates**: RC2_PHASE_A_PASS (36/36 da; 37/37 nå).
19. **PARTIAL band distribution**: 0.78-0.84: 9; >=0.90: 9 (18
    reviewer-PARTIAL totalt).
20. **PARTIAL correctness by band**: 0.78-0.84: 1/9; >=0.90: 5/9
    (label PARTIALLY_SUPPORTED) - ingen autogodkjenning av PARTIAL.
21. **Current fusion result**: 13 autos 13/13 korrekte; 0 false
    autos; 0 critical false autos; 107 review.
22. **Candidate fusion strategies**: (a) behold 0.90 global;
    (b) senk global terskel; (c) predicate/subgroup-tilpasset;
    (d) proof-conditioned; (e) retningssymmetrisk vs asymmetrisk -
    vurdert i partial-band-analysis.md.
23. **Selected fusion strategy**: reviewer SUPPORT >=0.90 uten
    spesifikke defekt-flagg autogodkjennes; CONTA/PARTIAL/INSUFF/
    sub-0.90/spesifikt-flagg -> review; samme asimetri på
    deterministisk sti (CONTRA autoer aldri).
24. **Why threshold change is safe/unsafe**: senking er UTRYGG:
    0/12 korrekte i 0.78-0.84; beholde 0.90 er trygt: 32/32
    SUPPORT-autos korrekte; 0.85-0.89 har n=1 - utilstrekkelig
    grunnlag.
25. **Fusion calibration SHA**: fusion.py
    21d5ffabc5a2d6d3dd88b5f6a9595b81dbea91804d6e94808a83c2e35c452747;
    fusion-calibration.json c263f284ded25d99bd4c5340faad08da6219f46e3ce5fd376d6e22b9b737eea2.
26. **Compound taxonomy**: BAD_DECOMPOSITION 24;
    WRONG_ATOM_BOUNDARY 12; ATOM_VERDICT_ERROR 4;
    AGGREGATION_OR_FUSION 1 (compound-audit.json).
27. **Bad decomposition count**: 24.
28. **Atom verdict error count**: 4.
29. **Aggregation error count**: 1 (0 rene AGGREGATION_ERROR; 1
    atom-korrekt sak feiler i fusion/aggregering).
30. **Compound oracle result**: oracle-dekomponert kjøring fikser
    bare 6/30 atom-merkede feil - støtte-recall på smale atomer er
    binding begrensning, ikke segmentering.
31. **Compound fix**: ingen utsatt (Iterasjon B brukt på fusion;
    dokumentert i compound-audit.md med målt yield-sammenligning:
    fusion 32 vs dekomponering 6).
32. **Compound atom accuracy after**: uendret fra RC1-nivå
    (~49%) - ikke mål for denne oppgaven.
33. **Iteration B result**: fusion.py frosset; shadow-verifisert
    13/13 auto-presisjon; ingen endring etter freeze.
34. **Critical deterministic FP**: 0 (canaries + law_as_age_fp=[]).
35. **Critical reviewer FP**: 0 i autogodkjent masse; 1 kjent
    reviewer-COTA-feil (0169) forblir i review (blokkert fra auto).
36. **Critical fusion FP**: 0 (13/13 + 0 det-sti autos).
37. **Invalid proofs**: 0.
38. **Unsound accepted proofs**: 0.
39. **Hallucinated proofs**: 0.
40. **Runtime failures**: 0 i RC2 engine-rerun (RC1: 1 - 0112).
41. **Auto precision development**: 13/13 = 100% (>=99% gate PASS).
42. **Proof-safe/product dev metrics**: streng scorer: RC1 44/79 ->
    RC2 shadow 28/24 (konservativ policy; auto-kanalen er ren;
    se #52-54 og tradeoff-notat i fusion-calibration.json).
43. **Review rate**: 107/120 = 89,2% (RC1: 85,8%).
44. **Necessary vs unnecessary review**: kritisk-forventet-auto
    (n=56) går til review pga: reviewer-CONTRA 11,
    compound_claim 9, INSUFF 8, det-sti 8, PARTIAL 7,
    numeric_support_binding 2, øvrige flagg 4, under-0.90 1,
    utover det 5 ikke-kritiske saker; konservativt design,
    reduksjon krever ny blind-evaluering.
45. **KB regression**: 48/48 BESTATT (score_baseline.py).
46. **Evaluator regression**: tier1 43/43 = 1.00.
47. **Operator regression**: 23/23 PASS.
48. **Quote-aligner regression**: 37/37 (rc2 suite; kanaries sjekker
    i Phase A-gates).
49. **id_guard**: 0 treff (engine/ og fusion.py skannet).
50. **qa_check**: PASS ("OK: ingen kjente feilmnstre funnet").
51. **Deterministic reproducibility**: to fullstendige kjøringer av
    regressions + shadow; identiske resultater og SHA-verdier.
52. **Burned V1 shadow semantic**: 63/120 (streng scorer; RC1 79).
53. **Burned V1 shadow proof-safe**: 28/120 (RC1 44).
54. **Burned V1 shadow product**: 24/120 (RC1 79).
55. **Burned V1 critical errors**: 0 kritiske falske autoer
    (RC1: 5); kritisk produkt 37 -> 11 under konservativ policy
    (byttet mot 0 usikre autoer).
56. **Burned V1 runtime failures**: 0.
57. **Potential-label sensitivity**: 0116/0165 sterke kandidater;
    begge forblir offisielt merket; under reviderte PARTIAL-labels
    ville fused REVIEW_REQUIRED vaere korrekt produkthandling;
    ingen tuning mot alternative labels (label-audit i RC1 phase2).
58. **RC1 vs RC2 burned-shadow**: engine-lag 42 -> 52 semantisk;
    auto-presisjon 70/75 -> 13/13; falske autoer 5 -> 0; kritiske
    falske autoer 2 (offisiell) / 5 (streng) -> 0.
59. **RC2 candidate frozen**: JA - release-candidate/RC2/
    FROZEN_DEVELOPMENT_CANDIDATE.
60. **Manifest/hash status**: RC2-manifest.json + hashes.txt med
    komponent-SHAer; calibration SHA c263f284...7eea2 (full i
    manifest).
61. **READINESS**: RC2_READY_FOR_NEW_BLIND_SET.
62. **Exact failed development gates**: ingen (alle ni
    gategrupper pass; detaljer i readiness-report.md).
63. **Remaining architecture weaknesses**: atom-support-recall på
    smale compound-atomer; reviewer-CONTRA-overcall på blandede
    atomer (0169-klassen); reviewer-PARTIAL-presisjon lav i alle
    bånd; deterministisk sti kan ikke alene bære produktvolum.
64. **Fusion/reviewer R&D videre**: JA, men kun mot NYE utviklings-
    data; burned V1 er uttømt for tuningformål.
65. **New blind V2**: JA - anbefalt som egen oppgave etter freeze
    (ikke påbegynt her).
66. **Recommended next step**: Bygg Blind V2 (samme sealed-key
    prosess), kjør RC2 mot den; databoom: prioriter compound-atomer
    med atom-labels slik at støtte-recall kan måles direkte.

## Verdict

RC2_READY_FOR_NEW_BLIND_SET - med eksplisitt forbehold: ingen
certification, ingen live dialog, ingen KB-tuning, ingen case-ID
runtime-kode (id_guard 0), RC1 historikk urørt.

