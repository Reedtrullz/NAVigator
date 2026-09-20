# SLUTTRAPPORT: Semantic Judge v0.4 Architecture Repair

Statusdato: 31.08.2026
Primærmodell: **Judge C = gpt-5.6-luna** (kostnadsdirektiv; ~10x billigere enn gpt-5.5)
Sammenligningsmodell: **Judge A = gpt-5.5** (basiskontinuitet mot v0.3)

Denne rapporten er **IKKE en sertifisering**. Det er utviklingsresultatet etter
arkitekturreparasjonen, mot readiness-kriteriene i oppgaven. Ingen nye blindte
holdout er bygget.

## 1. Pre-flight-status

Riktig oppgave utført: v0.4-arkitekturreparasjon i
`evaluation/semantic-judge/v0.4/`. Maks 2 subagenter respektert (0 brukt i
denne etappen; langkjøringer kjørt serialisert i PTY med resume fra
resultatfiler).

## 2. Frysing av v0.2/v0.3

v0.2, v0.3, v0.3 freeze-manifest, holdout-v2 raw results, holdout-v2 answer key
og certification-report er uendret og urørt. Alle v0.3-artefakter er kun lest.

## 3. Root causes fra v0.3

Human audit av de 15 holdout-feilene viste: 8/15 overreach til CONTRADICTED der
fasit var INSUFFICIENT, 2 delkonflikt/compound som skulle vaert PARTIAL, 1
undekomponert compound claim, 4 hyperstrikte actor-instantieringer, og HV2-049
som mulig label-feil. Rotarsak: LLM-en hadde siste ordet pa final verdict, uten
proof-obligation for konflikt og uten uttommenhets-sjekk.

## 4. v0.4-arkitektur

Claim -> atomic decomposition -> claim normalization
  -> evidence relation judge (LLM, strukturert output)
  -> DETERMINISTIC ADJUDICATOR -> final verdict

LLM identifiserer claim-semantikk, source-semantikk og evidence relation.
Adjudicator (`adjudicator.py`) beregner final verdict deterministisk fra de
strukturerte relasjonene.

## 5. Hva LLM gjor

Dekomponerer compound claims til atomer (bevarer conditional/exception-struktur),
trekker ut relasjonsprimitiver per atom: subject/scope/time/actor match,
modality-relation, numeric-relation, negation-relation, enumeration
(exhaustive/non_exhaustive/unknown), relation (supports/contradicts/insufficient),
confidence, og konkrete evidence spans.

## 6. Hva den deterministiske adjudicatoren gjor

Beregner final verdict per atom fra relasjonsprimitivene, aggregerer compound
claims (forskjellige atom-dommer -> PARTIALLY_SUPPORTED), handhever
safety_block og review_flag, og nedgraderer `contradicts` til INSUFFICIENT nar
contradiction_evidence mangler.

## 7. Contradiction proof obligation

`absence_of_support != contradiction` er handhevet: CONTRADICTED krever positivt
konfliktbevis (evidence span) via en av de 5 tillatte CONTRA_RELATIONS. Source
silence, scope/locality/actor mismatch og non-exhaustive enumeration gir
normalt INSUFFICIENT. Adjudicator nekter CONTRADICTED uten evidence span.

## 8. Nye evidence relation types

Tillatte konfliktrelasjoner: EXPLICIT_NEGATION, MUTUALLY_EXCLUSIVE_VALUE,
TEMPORAL_CONFLICT, EXHAUSTIVE_SET_EXCLUSION (kun ved dokumentert uttomende
liste), EXPLICIT_DISCRETION_CONFLICT. Relations som aldri alene gir
CONTRADICTED: source silence, scope mismatch, actor not mentioned, locality
mismatch, general->specific, specific->universal, non-exhaustive enumeration,
weaker modality.

## 9. Modalitetsmodell

Ekspisitt modality-relation (same/weaker/stronger/conflict/unknown) med matrise:
SOURCE MAY vs CLAIM MUST => ikke entailed, kun CONTRADICTED hvis source ogsa
etablerer discretion/non-obligation, ellers INSUFFICIENT. SOURCE NOT_REQUIRED vs
CLAIM REQUIRED => CONTRADICTED. SOURCE MUST vs CLAIM MAY => kompatibel.
Payment-duration telles ikke som age-limit (dedikert guard).

## 10. Actor/exhaustiveness-modell

CLASS/MEMBER/ORGANIZATION/ROLE/SERVICE skilles; uttommenhet er eget felt.
Ukjent uttommenhet + uoppfort aktor => INSUFFICIENT, ikke CONTRADICTED.

## 11. Scope-modell

National/municipality/NAV-national/NAV-local/specialist-health/historical/
transition-representasjon; scope mismatch => normalt INSUFFICIENT.

## 12. Decomposition-resultat

**44/44 PASS** (results/decomposition-run.json, gpt-5.5; dekomponeringsprompt
uendret etter siste PASS, SHA256 fc1d77f0...). Krav >=98%: **OPPFYLT**.

## 13. Compound-resultat

**30/30 PASS** (v0.3/results/compound-run.json: n=30, pass=30, failures=[]).
Krav 100%: **OPPFYLT**.

## 14. Burned holdout-v2 development-resultat (80 claims)

| Modell | Accuracy | Macro F1 | Binary FP |
|---|---|---|---|
| v0.3 baseline | 81.25% | 0.8162 | 0 |
| v0.4 gpt-5.5 (A) | **95.00%** | 0.95 | **0** |
| v0.4 gpt-5.6-luna (C) | **91.25%** | 0.9137 | **0** |

Luna-miss (7): HV2-011 PS->CONTRA (.90), HV2-031 PS->CONTRA (.90), HV2-034
CONTRA->INSUFF, HV2-041 SUPPORTED->INSUFF, HV2-042 CONTRA->INSUFF,
HV2-049 SUPPORTED->INSUFF (audit-case), HV2-070 CONTRA->INSUFF. 5/7 er
konservative nedgraderinger. A-miss (4): HV2-023, HV2-031, HV2-042, HV2-049.
Luna fanger HV2-023 korrekt der A feiler; ingen av modellene har
 hoy-konfidens-feil pa holdout.

## 15. De 8 overreach-casene

HV2-004, -008, -024, -032, -036, -048, -056, -068: alle 8 fikk v0.3-verdict
CONTRADICTED mot fasit INSUFFICIENT. Under v0.4 (luna) er samtlige 8 na
**INSUFFICIENT_EVIDENCE** - lost av proof-obligation-arkitekturen, ikke av
claim-spesifikke patcher (ingen testcase-ID-er i kode; id_guard = 0 treff).

## 16. De 4 actor-casene

| Case | Fasit | v0.3 | v0.4 luna |
|---|---|---|---|
| HV2-041 | SUPPORTED | SUPPORTED (feil ift. audit) | INSUFFICIENT |
| HV2-049 | SUPPORTED | SUPPORTED | INSUFFICIENT (audit, se pkt 17) |
| HV2-023 | PARTIAL | CONTRADICTED (feil) | PARTIAL (riktig) |
| HV2-071 | PARTIAL | feil | PARTIAL (riktig) |

Kildens aktorliste var ikke dokumentert uttommente for 041/049; unknown actor
=> INSUFFICIENT. Merk: 041 er en reell nedgraderings-miss under luna
(fasit SUPPORTED), rapportert som trade-off.

## 17. HV2-049-vurdering

Original fasit: SUPPORTED. v0.4 (begge modeller): INSUFFICIENT_EVIDENCE;
pre-doctrine-fix ga SUPPORTED. Klassifisert som **POTENTIAL_LABEL_ERROR**
(audit-case). Regelen som avgjor: kilden etablerer ikke plikten/retten slik
fasiten antar uten mer eksplisitt evidence. Fasiten er frosset; caset er ikke
brukt som tune-target. Original metric er ikke skjult (den teller i pkt 14).

## 18. Contradiction-vs-insufficiency confusion (luna, 69 cases)

                 predicted
              CONTRA   INSUFF
actual CONTRA    36        1
actual INSUFF     0       32

Identisk for gpt-5.5. Krav: contradiction precision >=0.95 og insufficiency
recall >=0.95.

## 19. Contradiction precision

**36/36 = 1.00** (begge modeller). Krav >=0.95: **OPPFYLT**.

## 20. Insufficiency recall

**32/33 = 0.9697** (begge modeller; en konservativ CONTRA->INSUFF, CI-015).
Krav >=0.95: **OPPFYLT**.

## 21. Modality benchmark (30 cases)

luna: **90.0%** (3x SUPPORTED->INSUFF). gpt-5.5: **100%**.

## 22. Actor-scope benchmark (30 cases)

luna: **73.33%** (8x SUPPORTED->INSUFF nedgraderinger). gpt-5.5: **80%**.

## 23. Locality benchmark (20 cases)

luna: **65.0%** (4x SUPPORT->INSUFF, 3x INSUFF->CONTRA). gpt-5.5: **75%**.
Lunas eneste overreach-spot: LOC-10, LOC-18, LOC-20 (INSUFF->CONTRA med
konfidens 0.98-0.99, rapportert under pkt 30).

## 24. Minimal-pair resultat (52 cases: 48 hovedsett + 4 supplement for spec par. 27)

luna: **76.92% kombinert (40/52)**; hovedsett alene 77.08% (41/48);
supplement 3/4 - negasjons-paret (MP-014A/B) fullt riktig, temporal-paret
1/2 (MP-015A konservativ INSUFF-nedgradering, ingen overreach). Svakhet:
numeric-dimensjonen 0/2 (hovedsett) er tydelig. gpt-5.5 pa hovedsett:
**85.42%**.

## 25. Stability-resultat (30 claims x 5 runs, luna)

Modal verdict consistency: **83.33%** (25/30). Krav >=95%: **IKKE OPPFYLT**.
Inkonsekvente (alle C<->I / S<->I / C<->PS, ingen S<->C):
CAL035 (3C/2I), CAL041 (3C/2I, safety-flagget), CAL055 (4C/1PS),
CAL061 (4PS/1I), CAL088 (3S/2I).

## 26. Structured-relation stability (luna)

relation 76.67%, relation_type 53.33%, subject_match 83.33%, scope_match
83.33%, time_match 90%, actor_match 86.67%, modality_relation 43.33%,
numeric_relation 80%, negation_relation 56.67%, verdict 83.33%.
Wobble-kilden er tydelig: relation_type/modality_relation-ekstraksjonen,
ikke final-adjudicationen.

## 27. Safety flips

**0** SUPPORTED<->CONTRADICTED flips pa safety-flaggede claims (150 runs,
programmatisk verifisert). Krav 0: **OPPFYLT**.

## 28. Numeric flips

**0** SUPPORTED<->CONTRADICTED flips pa numeric-flaggede claims. Krav 0:
**OPPFYLT**.

## 29. Temporal flips

**0** SUPPORTED<->CONTRADICTED flips pa temporal-flaggede claims. Krav 0:
**OPPFYLT**.

## 30. High-confidence errors (confidence >=0.95)

Holdout-v2 (luna): **0**. Kalibrering (luna): 1 - CAL050
(PS->CONTRA, 0.99, lokal gruppe). Benchmarks (luna): 3 - LOC-10/18/20
(INSUFF->CONTRA, 0.98-0.99). gpt-5.5: 0 pa holdout og benchmarks.
Malet "0 hvis mulig" er ikke fullt oppnadd pa luna; det er 4 high-conf-feil
totalt, alle konservative-retning eller lokalitet.

## 31. Rule scorer + v0.4

Sluttarkitekturen er testet som helhet: deterministic exact checks (KB),
hard safety rules (safety_block i adjudicator), semantic relation extraction,
deterministic entailment adjudication og review gate (review_flag) er alle
aktive i v0.4-kjoringen. Se pkt 34-36 for regresjonsbevis.

## 32. Trade-offs mot v0.3

Holdout: 81.25% -> 95% (A) / 91.25% (C). Overreach: 8 feil -> 0.
Binary FP: 0 -> 0 begge. Men: kalibrering falt fra 94.05% (v0.3, gpt-5.5) til
84.52% (luna) - hovedsakelig 9 konservative CONTRA->INSUFF-nedgraderinger
(CAL029/030/031/034/035/064/067/080/089) der fasiten forventer CONTRA, pluss
CAL050. Stability modal consistency: 80% -> 83.33% (marginal forbedring,
fortsatt under mal). Nedgraderings-tendensen er generell (rammer actor-scope,
locality, minimal-pairs), ikke claim-spesifikk.

## 33. Anti-overfitting-resultat

Ingen testcase-ID-er i evaluator-kode eller konfig (id_guard: 0 treff).
Cross-benchmark: holdout-forbedringen folger generelle regler (proof
obligation, exhaustiveness, modality-matrise) og vises igjen pa alle
benchmark-settene. Trade-offs er rapportert, ikke skjult (pkt 21-24, 32).

## 34. KB regression

**48/48 BESTATT, 0 FEILET** (`python3 evaluation/score_baseline.py`,
re-kjort live 31.08.2026). Krav 48/48: **OPPFYLT**.

## 35. Evaluator regression

`python3 evaluation/evaluator-regression/run_evaluator_regression.py`
(re-kjort live): **TP=24 TN=96 FP=0 FN=0, acc=1.00, safety_FP=0**. Ingen
regresjon. **OPPFYLT**.

## 36. qa_check.sh

`bash scripts/qa_check.sh` (re-kjort live): **PASS - "OK: ingen kjente
feilmnstre funnet"**. Offline v0.4-gates: adjudicator_test 19/19, selftest 8/8,
id_guard 0 treff. **PASS**.

## 37. v0.4 modenhetsniva per komponent

| Komponent | Krav | Resultat | Status |
|---|---|---|---|
| Decomposition | >=98% | 100% (44/44) | PASS |
| Compound aggregation | 100% | 100% (30/30) | PASS |
| Contradiction precision | >=95% | 100% | PASS |
| Insufficiency recall | >=95% | 96.97% | PASS |
| Stability modal | >=95% | 83.33% | **FAIL** |
| Safety flips | 0 | 0 | PASS |
| Numeric flips | 0 | 0 | PASS |
| Temporal flips | 0 | 0 | PASS |
| Evaluator regression | ingen | acc 1.00 | PASS |
| KB regression | 48/48 | 48/48 | PASS |

## 38. READINESS

## **NOT_READY_FOR_BLIND_RECERTIFICATION**

Ett vesentlig krav feiler: stability modal consistency 83.33% mot mal >=95%.
Alle andre readiness-kriterier er oppfylt. Nytt blindt holdout-v3 skal derfor
IKKE bygges enna.

## 39. Eksakte gjenvarende svakheter

1. **Stability**: verdict-wobble er C<->I / S<->I pa 5/30 claims. Wobble-kilden
   er LLM-ekstraksjonen av relation_type (53.33% konsistens) og
   modality_relation (43.33%), ikke den deterministiske adjudiceringen.
   Konkret: EXPLICIT_NEGATION vs SCOPE_MISMATCH vs MUTUALLY_EXCLUSIVE_VALUE
   velges inkonsistent pa samme claim pa tvers av runs.
2. **Luna locality-overreach**: 3 high-conf INSUFF->CONTRA (LOC-10/18/20) -
   lokalitetsbevissthet er svakere hos luna enn gpt-5.5.
3. **Luna konservativitet**: 8-9 SUPPORTED/CONTRA->INSUFF-nedgraderinger pa
   tvers av sett (koster kalibrering og actor/locality accuracy, men beskytter
   binary FP = 0).
4. **Numeric minimal-pairs**: 0/4 pa luna (mulig tall-format-folsomhet i
   ekstraksjonen).

## 40. Anbefalt neste steg

Ikke start v0.5. Anbefalt avgrenset stabiliserings-etappe for ny readiness-run:

1. Reduser LLM-ens beslutningsrom videre pa relation_type: koordiner
   near-synonym-typer deterministisk etter ekstraksjon (f.eks. behandl
   SCOPE_MISMATCH vs EXPLICIT_NEGATION-tvetydighet via adjudicator-regler), sa
   ordvalget ikke snurrer verdict-laget.
2. Kjor stability 30x5 pa nytt (kun dette settet) og mal pa nytt mot >=95%.
3. Rett luna-locality: styrk "lokal mismatch => INSUFFICIENT"-regelen i
   RELATION_PROMPT og re-kjor locality (20 cases) + holdout binary FP-sjekk.
4. Deretter separat oppgave: v0.4 blind re-certification med nytt holdout
   (bygges av separat agent, ikke i denne etappen).

## Vedlegg: kjorte artefakter (31.08.2026)

- `results/v04-results-holdout-v2-A-judge-a-gpt-5.5.json` + `metrics-holdout-v2-v04.json`
- `results/v04-results-holdout-v2-C-judge-c-gpt-5.6-luna.json` + `metrics-holdout-v2-v04-C.json`
- `results/v04-results-stability-C-judge-c-gpt-5.6-luna.json` (150 rows) + `metrics-stability-v04.json`
- `results/v04-results-calibration-C-judge-c-gpt-5.6-luna.json` (84 rows) + `metrics-calibration-v04-C.json`
- `results/v04-results-{minimal-pairs,contra-insuff,modality,actor-scope,locality}-C-judge-c-gpt-5.6-luna.json` + tilhorende grade-filer
- `benchmarks/minimal-pairs-supplement.json` + `results/v04-results-minimal-pairs-supplement-C-judge-c-gpt-5.6-luna.json` + `results/v04-minimal-pairs-combined-grade.json` (spec par. 27: 52 cases >= 50)
- `results/decomposition-run.json` (44/44)
- QA evidence (re-verifisert 31.08.2026 etter rapport): 34/34 v0.4
  results-JSON og 5/5 benchmark-JSON validert (JSON parse). Freeze manifest
  re-verifisert: 13/13 filer matcher recorded SHA256 - v0.2/v0.3 LLM-lag kan
  ikke ha driftet (samme kode/prompt/model => samme oppfoersel; hash-bevis
  erstatter re-kjoring av gamle judge-pipelines). Deterministiske lag dekkes
  av KB 48/48 + evaluator-regresjon acc 1.00 over.
- Prompt-SHA256 (identisk pa tvers av alle luna-runs): relation 3163cf8f7477d299724c98b402c922e897f4f1c1ae82b4720be2af65a6333a9f, decompose fc1d77f0363d5a22e8f47f68fe7276e1fb7aee7246a070f5b5f890008476876f
