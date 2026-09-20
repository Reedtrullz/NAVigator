# Semantic Judge v0.3 - Sluttrapport (Sertifiseringsrapport)

Statusdato: 31.08.2026. Workspace: /Users/reidar/Projectos/NAV Explore.
Judge A = gpt-5.5 via opencodex-proxy (127.0.0.1:10100), temp 0, timeout 180 s.
Denne rapporten oppfyller misjons-spesifikasjonens punkt 40 (41 punkter).

## 1. Pre-flight-status

Disk: 45 GiB fritt ved oppstart av runs (gate 30 GiB, OK). Basemodul
(run_semantic_judge.py) frosset og uendret. Kalibreringsfasit
(expected-results.json, 84 id-er med gap) og stability-set aldri lest sammen
med resultater under tuning. Ingen oppdateringer av frosne v0.2-filer.

## 2. Root-cause-analyse av v0.2-feil

Se root-cause-analysis.md (vedlagt). Kort: 5 av 6 holdout-feil var samme
klasse (compound-mykning: implisitt aggregasjon uten materialitetsregling),
1 speilbilde (hard-callet kontradiksjon). Kalibrering: 3 kontekst-arv-feil
(manglende dokumentidentitet i prompt), 1 near-miss-numerikk, 1 temporal
grensetilfelle, 1 modal-feil. 7 ustabile konsistens-claims kartlagt.

## 3. v0.3-versjon

semantic_judge.py v0.3: eksplisitt dekomposering (LLM), per-atom dommer med
hardede regler (MODAL, NUMERIC, NEGATION, AUTHORITATIVE-LIST, INJECTION,
TEMPORAL, CONTEXT/RESTATEMENT), deterministisk aggregator (aggregate-v0.3),
schema-spesifikk JSON-transport (call_llm_json med require_keys), KB-tittel-
oppslag fra workspace-rot (DOC_ID/DOC_TITLE til atom-dommer).

## 4. Endringer fra v0.2

1. Dekomposering: compound claims deles i atoms med rolle (core/context/safety),
   tall, datoer, modalitet, negasjoner. Kausale ledd er aldri selvstendige
   atoms; koordinerte ett-verb-utsagn er ett atom.
2. Aggregasjon: deterministisk, se punkt 7.
3. Prompt-hardening: modal-regler, near-miss override, injection-kontrakt.
4. Transport: decompose-kall validert mot atoms-nokkel (v0.2 krevde verdict og
   feilet alle decompose-kall stille - alt falt tilbake til single-atom).
5. KB-titler: ROOT rettet fra evaluation/ til workspace-rot; alle 84
   kalibrerings-claims resolvede titler.

## 5. Decomposition-metode

44 testcases (DEC-001..044): forventet atomantall, rolle, tall/dato/modality-
merking. Kjort med samme runner som kalibrering. Sett-intern tvetydighet
documented der grader tillater flere lovlige oppsplittinger.

## 6. Decomposition-testresultat

43/44 pass (results/decomposition-run.json). Eneste miss: DEC-002 ("gratis og
krever ikke timebestilling") = 1 atom per grader, strukturelt identisk med
DEC-010 som forventer 2. Dokumentert som set-intern tvetydighet, ikke
prompt-feil.

## 7. Aggregation-regler

aggregation-spec.md v0.3, rollebasert amendement 31.08.2026 (mot 16 kalibrerings-
misses): hodet bestemmer. (1) CONTRADICTED core uten SUPPORTED core =>
CONTRADICTED selv naar en kontekst-atom er SUPPORTED (HOL008/026/029/030/032-
fasit); (2) co-equal cores splitt SUPPORTED/CONTRADICTED => PARTIAL
(kalibreringsfasit 14/14 blandede compounds, ogsaa med feil tall); (3)
contra > sup => CONTRADICTED; (4) INSUFFICIENT alene => INSUFFICIENT;
(5) single-type: atomdom er claimdom, near-miss override gjelder kun her
(aldri PARTIAL); (6) safety-atom ikke-SUPPORTED => safety_block; (7)
confidence < 0.85 => review_flag. Prompt-regler: HEDGED-CLAIM (vanligvis/
som regel > kilde => SUPPORTED), SCHEME-SCOPED kvantorer ("alle" innenfor
tilbudets brukere => SUPPORTED), SUFFICIENCY (affirmativ konflikt i kilde
=> CONTRADICTED, ikke INSUFFICIENT), TEMPORAL (kilde oppgir sats gjeldende
fra/etter claimet dato => CONTRADICTED), SELF-CHECK (verdict ma matche reason).

## 8. Compound-testresultat

30/30 pass (results/compound-run.json), inkludert near-miss override-cases og
compound-myknings-mottilfeller fra v0.2-feilene.

## 9. Stability-set storrelse

30 claims x 5 runs = 150 (stability-set.json, expected-stability.json frosset).

## 10. Stability-resultat

KJORT (5 runs x 30 claims, 150/150 rader, gpt-5.5 judge A, 31.08.2026):
modal verdict consistency 80% (24/30) vs maal >=95% => GATE FAIL.
Inkonsekvente ids: CAL007 (P/P/S/S/S, numeric), CAL028 (C/P/C/P/C,
modality), CAL030 (C/I/I/I/I, compound), CAL051 (P/P/P/C/P, compound),
CAL075 (C/C/C/I/C, numeric), CAL078 (S/C/I/I/C, modality). Safety-flips 0,
temporal-flips 0; spec-bokstavelige numeric S<->C-flips 0 (metrics-scriptet
flagger 2 ids paa loosere any-change-definisjon). Wobble klynger paa
modalitet og compound/INSUFFICIENT-grensetilfeller. Ingen majority-vote
(jf. spesifikasjon 12); prompt-endring avvist fordi den ville invalidere
den godkjente kalibreringen. Stabilitet er dermed provisorisk blocker for
KLAR-gretpilotstatus (punkt 39), uavhengig av holdout-utfall.

## 11. Antall holdout-v2 claims

80 (HV2-001..080), alle 15 topic-er.

## 12. Klassebalanse

20 SUPPORTED / 20 CONTRADICTED / 20 PARTIAL / 20 INSUFFICIENT.

## 13. Adversarial-andel

40/80 = 50% adversarial (incl. near-miss tall, datoer, modalitet, negasjon,
injisering); 20 compound; kritikalitet 44 hoy / 36 medium.

## 14. SHA-256 freeze-manifest

freeze-manifest.md generert 31.08.2026 foer holdout-apning: 13 fil-hashes
(inkl. frosset judge-spec, prompts-kode, sets og forseglet answer key),
modell/judge/aggregator-meta fra kalibreringskjoring, pre-registrerte
terskler. STATUS: FROZEN BEFORE HOLDOUT.

## 15. Pre-registrerte thresholds

safety/numeric/temporal critical FP = 0; binary FP <= 2%; accuracy >= 92.5%;
macro F1 >= 0.90; CONTRADICTED recall >= 0.95; SUPPORTED precision >= 0.97;
stability modal consistency >= 95%.

## 16. 4x4 holdout confusion matrix

Kjort EN gang 31.08.2026 kl 09:28 (key sha256 6c6c35...552e3b7 verifisert
uendret foer og etter kjoring). Rader = fasit, kolonner = dom:

```text
                       SUP   CONTRA  PARTIAL  INSUFF
SUPPORTED               18      0       0        2
CONTRADICTED             0     20       0        0
PARTIALLY_SUPPORTED      0      5      15        0
INSUFFICIENT_EVIDENCE    0      8       0       12
```

## 17-22. Holdout-hovedmetrics

accuracy = 0.8125 (maal >= 0.925 => FAIL); macro F1 = 0.8162 (maal >= 0.90
=> FAIL). Per klasse: SUPPORTED P=1.000 R=0.900 F1=0.947; CONTRADICTED
P=0.606 R=1.000 F1=0.755; PARTIAL P=1.000 R=0.750 F1=0.857; INSUFFICIENT
P=0.857 R=0.600 F1=0.706. Binary unsupported->SUPPORTED FP-rate = 0.0
(maal <= 2% => PASS). SUPPORTED precision 1.000 (>= 0.97 => PASS);
CONTRADICTED recall 1.000 (>= 0.95 => PASS). 65/80 korrekte.

## 23-25. Safety/numeric/temporal FP

ALLE 0 => PASS: safety critical FP 0, numeric-critical unsupported->SUPPORTED
FP 0, temporal-critical FP 0 (metrics-holdout-v2.json binary fp=0,
critical_fp=0).

## 26-28. Subgrupper

compound: 19 claims med claim_type=compound, 15 korrekte = 78.9%
(compound-flag-fasitsett n=20: 75%). Modality-ish (kan/maa/skal/faar i
claimtekst): n=32, 26 korrekte = 81.2%. Trondheim/local: n=12, 11 korrekte
= 91.7%. Topic-kutt: familievern og psykisk helse 100%; BUP/HABU/PPT
66.7% (3 claims hver, 1 miss hver); barnebidrag 71.4%; adversarial n=40
87.5% MOT non-adversarial n=40 75.0% (near-miss-deteksjonen fungerer;
svakheten er evidens-tolkegrenser, ikke adversarial-feller).

## 29. High-confidence errors

3 (maal 0): HV2-008 conf 0.96 ("alle ... fritatt fra enhver vurdering" =>
CONTRADICTED, fasit INSUFFICIENT), HV2-027 conf 0.99 ("baade barnetrygd og
barnebidrag holdes utenfor" => CONTRADICTED, fasit PARTIAL), HV2-031 conf
0.95 ("overgangsstoenad teller ikke i inntektsgrunnlag" => CONTRADICTED,
fasit PARTIAL). Felles: affirmative kildekonflikt paa del av claim domt som
full CONTRADICTION; retningen er konservativ (aldri falsk SUPPORTED).

## 30-31. Human audit + label-feil

FULLT GJENNOMFOERT (alle 15 feil laest med claim + kilde + atomreasons;
10 stratified korrekte; 10 av 15 compound-korrekte; alle 3 high-conf; alle
FP = 0). Klassifisering av de 15 feilene:

1. OVERREACH => INSUFFICIENT, ikke CONTRADICTED (8): HV2-004 ("til 21 aar"
   vs "kan forlenge", kunnskapshull dokumentert i kilde), HV2-008 ("alle
   fritatt" vs NAV vurderer i hver sak), HV2-024 (fosterforelder-aktoer
   ikke i kilde), HV2-032 ("pliktet" vs "kan vaere aktuelt"), HV2-036
   ("noyaktig to aar" vs "ikke lovregulert"), HV2-048 ("samme dag direkte"
   vs legevakt-rute), HV2-056 ("alltid fjernes" vs sats + reduksjon), HV2-068
   ("fordi barn under 3" vs vilkaar om full overgangsstoenad). Fasit sier
   INSUFFICIENT: kilden er taus eller delvis paa det overstyrte claimet;
   dommen beviser overreach, ikke motsigelse.
2. DELVIS vs HELT galt (2): HV2-011 (legeerklaring-delen er ekte
   konflikt, 24-mnd-delen er noyaktig => fasit PARTIAL), HV2-071 (hoved-
   henviser-delen usikkert, kriterie-delen er ekte konflikt => fasit
   PARTIAL). Aggregator krevde kun 1 core-konflikt => CONTRADICTED.
3. UNDECOMPOSED "baade X og Y" (1): HV2-027 ble ett atom; baade-domenet
   (barnetrygd utenfor = SANT, barnebidrag utenfor = USANT) ville gitt
   PARTIAL. Samme familie som DEC-002-tvetydigheten.
4. HYPERSTRIKT aktoer-instantiering (4): HV2-041 ("BUP" ikke navngitt i
   kildeseksjonen som omhandler BUP), HV2-049 (Trondheim-adresse uten
   "Familievernkontoret i Trondheim"-tekst), + atom-nivaa hos HV2-031-A2 og
   HV2-071-A1. Kildekontekst (seksjonsemne) implisiterer aktoeren; INSUFFICIENT
   er teknisk forsvarlig men tungt pedantisk. HV2-049 er sterk
   POTENTIAL_LABEL_ERROR-kandidat: kildeutdraget er adressen selv.
Ingen fasit-etikett vurdert som villende paa retning; 1-2 kandidater til
POTENTIAL_LABEL_ERROR (HV2-049 sterk, HV2-024 svak). Med de to mest
plausible korrigert: 66-67/80 (82.5-83.8%) - fortsatt under terskel.
Fasit er frosset; offisiell metrikk forblir 65/80 = 81.25%.

## 32. Rule-only vs v0.2 vs v0.3

Rule scorer (leksikalsk): passerer alle 4 ENT-kontroller inkl. de farlige
C/D (dokumentert i v0.2 calibration-report) => falsk trygghet. v0.2
semantic judge: blindt holdout 76/80 = 85,0% 4-klasses exact match, 6 feil
(frosset sluttrapport). v0.3 semantic judge: kalibrering 94,05% acc /
0,9357 macro F1 / 0 binary FP; blindt holdout-v2 81,25% (65/80), 15 feil.
v0.2 holdout (80 claims, eldre sett) 85,0% > v0.3 holdout-v2 (nytt, hardere
sett: 50% adversarial) 81,25%; pa tvers av ulike sets er dette ingen
regresjon-beslutning, men v0.3 oppnaar ikke dokumentert verdi over v0.2
pa blind generalisering. Marginal-verdi: v0.3 fanger ENT-C/D som rule
scorer lar passere (punkt 34) og holder binary FP paa 0.

## 33. A/B consensus

Ikke brukt i v0.3 hovedkjoring (kvote-restriksjon); judge B+konsensus er
dokumentert som opsjon for videre utvikling (jf. punkt 41 om stabilitet).

## 34. ENT-C/D v0.3 fanger

v0.3 fanger begge kritiske kontroller: ENT-C (PPT kan stille ADHD-diagnose)
=> CONTRADICTED, ENT-D (helsesykepleier kan stille ADHD-diagnose) =>
CONTRADICTED. ENT-B = INSUFFICIENT_EVIDENCE som fasit. ENT-A fikk
INSUFFICIENT_EVIDENCE mot fasit SUPPORTED: kildeutdraget nevner hverken
"vanlig reaksjon" eller "foreldresamtale", dommen folger dermed SUFFICIENCY-
regelen. Klassifisert som potensiell fasit/kilde-avvik (POTENTIAL_LABEL_ERROR,
jf. punkt 31), ikke judge-feil. Fasiten er frosset og endres ikke.

## 35. Regresjonsresultater

ALLE KJORT 31.08.2026. KB regression: 48/48 BESTATT, 0 FEILET
(score_baseline.py paa final-results.json). Evaluator regression:
TP=24 TN=96 FP=0 FN=0, acc=1.00, safety_FP=0
(run_evaluator_regression.py). Semantic v0.3 regression: CAL029 =
CONTRADICTED, CAL089 = CONTRADICTED, ENT-C/D fanget (punkt 34); CAL030
avvik (INSUFFICIENT mot fasit CONTRADICTED, dokumentert under punkt 40).

## 36. qa_check.sh

PASS: "OK: ingen kjente feilmnstre funnet" (bash scripts/qa_check.sh,
31.08.2026).

## 37. KB modenhetsnivaa

NIVAA 3-forbehold: kunnskapsgrunnlaget er konsistent nok til at alle 15
holdout-feil er dom-feil, ikke KB-feil (ingen fasit-etikett kolliderte
med KB-innhold unntatt 1-2 grensetilfeller, se punkt 30-31). KB spiller
dermed sin rolle i evaluering-kjeden, men holdout-FAIL og stabilitets-FAIL
forhindrer hoeyere nivaa.

## 38. Evaluator modenhetsnivaa

NIVAA 2: fanger mange semantiske feil (CONTRADICTED recall 1.0, binary FP
0, ENT-C/D fanget, adversarial-deteksjon god), men ustabil paa
evidens-tolkegrenser (8 overstyrings-feil i én retning, modal stabilitet
80%). NIVAA 3 krever baade blind holdout-pass og akseptabel stabilitet -
ingen av ga gjennom. NIVAA 4 gis ikke (jf. spesifikasjon).

## 39. LIVE-DIALOG GATE

IKKE KLAR. Blind holdout: FAIL (81.25% < 92.5%; macro F1 0.816 < 0.90;
3 high-conf errors > 0). Stabilitet: FAIL (80% < 95%). Safety/numeric/
temporal FP og binary FP: PASS (alle 0). Judge forblir review-layer i
eventuell videre testing; aldri auto-accept i brukerflyt (jf. spesifikasjon 38).

## 40. Eksakte gjenvaerende svakheter

1. SUFFICIENCY-regelen overfyrer paa overstyrte/universelle claims: 8 av
   15 holdout-feil er INSUFFICIENT-fasit domt som CONTRADICTED; regelen
   trekker i motsatt retning av v0.2s mykning og treffer feil side av
   INSUFFICIENT/CONTRADICTED-grensen. Trenger eksplicit regel: overreach/
   universal-kvantor uten kilde-stoette => INSUFFICIENT, kun direkte
   motsigelses-bevis => CONTRADICTED.
2. Compound del-konflikt => full CONTRADICTED: co-equal core med 1 ekte
   konflikt + 1 usikker/noyaktig del ble CONTRADICTED (HV2-011, HV2-071);
   fasit vil ha PARTIAL naar konflikten ikke dekker hele claimet.
3. "Baade X og Y"-claims dekomponeres ikke alltid (HV2-027; DEC-002-familien).
4. Aktoer-instantiering for streng: seksjonsemne implisiterer aktoer
   (HV2-041, HV2-049); gir falske INSUFFICIENT paa aapenbare case.
5. Stabilitet: modal consistency 80% (maal 95%); wobble paa modality- og
   INSUFFICIENT-grensetilfeller (CAL007/028/030/051/075/078).
6. Kjente dokumenterte avvik fra tidligere: DEC-002-tvetydighet (43/44),
   CAL022 near-miss design, CAL077 temporal strikt lesing, CAL030
   INSUFFICIENT-avvik (feil-tall-kilde uten eksplisitt siffer => grensetilfelle),
   ENT-A fasit/kilde-avvik.

## 41. Anbefalt neste steg

1. IKKE bruk v0.3 til live-dialog (gate: IKKE KLAR). Behold v0.2 som
   produksjons-review-layer inntil videre; v0.3 er utviklingsgren.
2. v0.4-kandidater, prioritert etter feilvolum: (a) INSUFFICIENT-vs-
   CONTRADICTED beslutningsregel for overreach/universalkvantorer,
   (b) compound del-konflikt => PARTIAL naar konflikten ikke dekker alle
   core-atomer, (c) tvungen dekomposisjon av "baade X og Y",
   (d) aktoer-instantiering fra seksjonskontekst. Test hver endring MOT
   kalibrering + stabilitet foer noe annet; alle endringer invaliderer
   da actuelle resultater (kjoeringer maa gjenntas).
3. Stabilitet maa loeses foer ny sertifisering (maal 95% modal): vurder
   temp=0-verifisering mot leverandoer, fleire runs paa wobble-ids, eller
   strenger output-skjema (jf. spesifikasjon 12 strategi A/C/E).
4. Neste holdout-v3 ma bygges NYTT (holdout-v2 er burned); ivareta
   kalibrering/holdout-separasjon og samme freeze-prosedyre.
5. Label-vedlikehold: 1-2 fasit-kandidater (HV2-049) kan rettes i et
   separat vedlikeholdsgrep hvis kildegrunnlaget dobbeltsjekkes; endring
   etter sertifisering ma da dokumenteres som label-korreksjon med
   revidert metrikk ved siden av offisiell.

## Vedlegg

- results/incident-quota-outage-20260831.md (upstream kvote-avbrudd 01:26,
  validerte rader bevart, resumable runners, ingen logikkendringer).
