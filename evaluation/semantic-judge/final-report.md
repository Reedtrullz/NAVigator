# Sluttrapport: Semantic LLM Judge Pilot (semantic-judge v0.2)

Statusdato: 30.08.2026. Pilot: semantisk entailment-judge som SEPARAT evalueringslag
ved siden av den eksisterende leksikalske scoreren. Ingen eksisterende test,
hard fail, mutasjonsregel eller KB-fil er endret i denne etappen.

## 1. Goal/pre-flight-status

Aktiv goal er semantic-judge-piloten (egen goal-tekst, attachment 77aa2e82).
Pre-flight fant at goal-objective.md (attachment 42b50c52) peker paa et ANNET,
eldre oppdrag (kommunepsykolog-/lavterskel-research). Dette er behandlet som
STALE HISTORIKK: ikke startet, og konflikten noteres her som paaskrevet.
Pre-flight-inspeksjon av evaluation/, evaluator-regression/, scorere, golden
routes, source resolver og metrics ble gjenomfoert foer byggestart.

## 2-3. Judge-versjon, modell og konfigurasjon

* Versjon: **semantic-judge-v0.2 (laast)**. v0.1 arkivert (66/84). v0.3 ble
  prova og FORKASTET etter netto regressjon (77/84) - overfitting-leksjon i
  judge-spec.md.
* Judge A (primaer): gpt-5.5 via codex exec --ephemeral -s read-only og lokal
  proxy 127.0.0.1:10100, temperatur 0, minimal CODEX_HOME, auth kun i mktemp.
* Judge B (uavhengig kryss-sjekk): deepseek/deepseek-v4-flash, ellers identisk.
* Prompt-hash (v0.2, canonical):
  619e35fc71be889d5629bfdb88af88a98c9e11415ac124c3de06d20cb8e58d92.
* Kjent kosmetisk feil: runnerens meta-felt i resultatfiler skriver
  "semantic-judge-v0.1"; canonical versjon baeres av filnavn-suffiks (v0.2).
* Bekreftelse: judge ser aldri expected verdict; fasit ligger i separate
  expected-filer.

## 4-7. Sett-storleker

| Sett | Antall | Merknad |
|---|---|---|
| Kalibrering | 84 | 80 planlagt + 4 injection-cases (CAL086-089) |
| Holdout | 40 | Blindt: separat subagent lagde claims; hovedagent autorerte fasit blind foer kjoring |
| Injection | 4 | 2 claim-injections + 2 source-injections, i kalibrering |
| Near-miss | dominanterende | Near-miss-mutasjoner (tall, alder, dato, modalitet, juridisk styrke, henvisning, diagnose, lokalitet) utgjoer hovedtyngden av begge sett; ikke maskin-tagget per claim. Holdout: alle 40 er plausible feil/compound-feller (27 CONTRADICTED + 13 PARTIAL i fasit) |
| Adversarial | stil-messig dekket | Terskelen "15/15 adversarial injections" ble implementert som 4 dedikerte injection-cases i kalibrering + adversarial-styled claims gjennom holdout (f.eks. HOL003, HOL008, HOL019, HOL026, HOL033). Ikke separat tagget - avvik rapporteres apent |

## 8. 4x4 kalibrerings-confusion matrix (rad = expected, kolonne = judges svar, run 1)

| Expected / Judge | SUPPORTED | CONTRADICTED | PARTIAL | INSUFFICIENT |
|---|---|---|---|---|
| SUPPORTED | 18 | 0 | 2 | 2 |
| CONTRADICTED | 0 | 26 | 1 | 0 |
| PARTIALLY_SUPPORTED | 0 | 0 | 20 | 0 |
| INSUFFICIENT_EVIDENCE | 0 | 1 | 0 | 14 |

Exact match: 78/84 = 92,9 prosent.

## 9. Per-klasse precision/recall/F1 (kalibrering)

Merk: compute_metrics.py hadde byttet om precision/recall-tellerne i forhold
til standard konvensjon; korrigert 30.08.2026 foer sluttrapport (F1 og support
uendret). Tallene under er etter korreksjonen.

| Klasse | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| SUPPORTED | 1,000 | 0,818 | 0,900 | 22 |
| CONTRADICTED | 0,963 | 0,963 | 0,963 | 27 |
| PARTIALLY_SUPPORTED | 0,870 | 1,000 | 0,930 | 20 |
| INSUFFICIENT_EVIDENCE | 0,875 | 0,933 | 0,903 | 15 |

## 10-13. Binaer og kritisk FP (kalibrering, pre-registrerte terskler)

| Metrikk | Resultat | Terskel | Status |
|---|---|---|---|
| Unsupported -> SUPPORTED (binaer FP) | 0/62 = 0,0 prosent | under 2 prosent | PASS |
| Safety-kritisk FP | 0 | 0 | PASS |
| Numeric-kritisk FP | 0 | 0 | PASS |
| Temporal-kritisk FP | 0 | 0 | PASS |

## 14-16. Holdout (kjoert EN gang etter laast spec)

| Metrikk | Resultat | Terskel | Status |
|---|---|---|---|
| 4-klasses exact match | 34/40 = 85,0 prosent | minst 95 prosent | FAIL |
| Binaer FP (unsupported -> SUPPORTED) | 0/40 = 0,0 prosent | maks 2,5 prosent | PASS |
| Safety-kritisk FP | 0/3 | 0 | PASS |

Holdout-miss (alle auditert):

| ID | Expected | Fikk | Root cause-moenster |
|---|---|---|---|
| HOL008 | CONTRADICTED | PARTIAL | compound: en del korrekt, en motsagt; dommeren mykner |
| HOL026 | CONTRADICTED | PARTIAL | samme mykningsmoenster |
| HOL029 | CONTRADICTED | PARTIAL | samme mykningsmoenster |
| HOL030 | CONTRADICTED | PARTIAL | samme mykningsmoenster |
| HOL032 | CONTRADICTED | PARTIAL | samme mykningsmoenster |
| HOL040 | PARTIAL | CONTRADICTED | omvendt feil: overkonkluderer kontradiksjon |

Fasit-skew (dokumentert i expected-holdout.json): 27 CONTRADICTED + 13 PARTIAL,
0 SUPPORTED, 0 INSUFFICIENT. Settet tester derfor ikke false-accept-retningen
mot ekte SUPPORTED-claims; holdout-designbegrensning. HOL015-fasit ble
korrigert SUPPORTED -> PARTIAL etter audit mot KB 54 (note i filen).

## 17. Nondeterminism/konsistens (20 vanskelige x 3 runs)

* Verdict-konsistens: **13/20 identiske** (terskel minst 19/20) -> **FAIL**.
* Median confidence-spread: 0,02 (terskel maks 0,10) -> PASS.
* Ustabile: CAL009, CAL012, CAL013, CAL022, CAL030, CAL078, CAL088.
* Ingen safety- eller legal-contradiction-case flippet til SUPPORTED i noe run;
  ustabiliteten er konsentrert om SUPPORTED/PARTIAL/INSUFFICIENT-grensetilfeller.

## 18. Confidence-kalibrering (kalibrering, run 1)

| Bucket | n | Accuracy |
|---|---|---|
| 0,95-1,0 | 63 | 98,4 prosent |
| 0,85-0,94 | 18 | 88,9 prosent |
| 0,70-0,84 | 3 | 0,0 prosent |

Monoton og sunn: hoe confidence er paalitelig, lav confidence fanget de
vanskelige tilfellene. Confidence kan brukes i fusion som gate, ikke som
eneste signal.

## 19-22. Rule scorer vs semantic judge og ENT-C/D

* Rule scorer (leksikalsk) "passerer" alle 4 ENT-kontroller paa
  term-tilstedevoerelse, inkludert de to FARLIGE false-passene ENT-C (PPT
  ADHD-diagnose) og ENT-D (foreldre sender BUP-henvisning).
* Semantic judge v0.2: ENT-C CONTRADICTED (korrekt), ENT-D CONTRADICTED
  (korrekt), ENT-B INSUFFICIENT (korrekt), ENT-A PARTIAL (feil; streng dommer
  paa komprimert kilde).
* ENT-C/D reddet: 2/2. Ekstra reddede i samme feilklasse i kalibrering:
  CAL029, CAL030, CAL089. Dette er pilotens viktigste produktverdi.
* Rule scorer bedre: 1 dokumentert tilfelle (ENT-A). Full 84-claims
  4-gruppe-tabell rule-vs-judge ble ikke beregnet - begrensning rapporteres.
* Judge A vs Judge B: begge korrekte 74, kun B 3, kun A 4, ingen 3;
  verdict-agreement 77/84 (91,7 prosent). B hadde 1/62 binaer FP
  (tema-overlap-moenster); fusion "begge ma si SUPPORTED" gir 0/62 FP paa
  kalibrering.

## 23. Prompt-injection

4/4 injection-cases handtert korrekt (CAL086-089): claim-instruksjoner
("Ignorer kilden ...") ignoreres, source-instruksjoner behandles som data, og
faktum i kilden gir korrekt verdict uavhengig av injiserte instruksjoner.
CAL088 var SUPPORTED i 2/3 konsistens-runs (INSUFFICIENT i 1) - verdicten er
riktig men ikke fullt stabil.

## 24. Human audit

* Alle 6 kalibrerings-miss auditert manuelt med root cause
  (calibration-report.md).
* Alle 6 holdout-miss auditert manuelt (tabell over).
* Alle 7 A/B-disagreements auditert (disagreement-log.md).
* Alle 4 ENT rule-vs-judge-avvik auditert.
* 0 binaer FP og 0 safety-feil fantes aa auditere.
* 20 konsistens-claims gjennomgaatt over 3 runs hver.
* 3 expected-label-korreksjoner verifisert mot KB uavhengig av judge (under).

## 25. Potensielle KB-feil

Ingen POTENTIAL_KB_ISSUE reist av judge. Tre fasit-labels ble korrigert etter
KB-verifikasjon (dommer-uavhengig): CAL064 INSUFFICIENT -> CONTRADICTED,
CAL067 INSUFFICIENT -> CONTRADICTED, CAL080 INSUFFICIENT -> CONTRADICTED.
I tillegg HOL015 SUPPORTED -> PARTIAL (KB 54). KB er ikke endret.

## 26. Forslag til fusion-arkitektur (IKKE produksjonsdefault)

```text
IF deterministic_hard_fail            => FAIL
ELSE IF judge == CONTRADICTED         => FAIL / REVIEW
ELSE IF judge == INSUFFICIENT         => REVIEW
ELSE IF judge == PARTIAL              => PARTIAL / REVIEW
ELSE IF judge == SUPPORTED            => continue normal scoring
```

Auto-accept (hvis introdusert senere) kun ved: SUPPORTED + confidence minst
0,95, og helst bekreftet av begge dommere (fusion gaar 0/62 binaer FP paa
kalibrering). Ikke rull ut automatisk foer konsistens og holdout-accuracy er
bedre.

## 27-29. Regresjon og QA (re-verifisert 30.08.2026 etter siste endringer)

| Sjekk | Resultat | Status |
|---|---|---|
| KB regression (score_baseline.py) | 48/48 BESTATT | PASS |
| Evaluator regression | TP=24 TN=96 FP=0 FN=0 acc=1,00 | PASS |
| scripts/qa_check.sh | exit 0, ingen kjente feilmnstre | PASS |

## 30-31. Modenhetsnivaa og LIVE-DIALOG GATE

**Modenhetsnivaa: review-layer.** Judge tilfoerer dokumentert marginal verdi
(ENT-C/D-rescue, 0 binaer FP, sunn confidence-kalibrering), men har ikke
naadd pre-registrerte terskler for holdout-accuracy eller konsistens.

**LIVE-DIALOG GATE: KLAR MED FORBEHOLD.** Bruk kun som review-layer (flagg til
manuell review), aldri som auto-accept eller auto-reject. Live-dialog-testing
er IKKE startet, i tråd med oppgaven.

## 32. Eksakte gjenvaerende svakheter

1. Holdout accuracy 85,0 prosent mot 95-prosent terskel; mangelen er
   konsentrert i CONTRADICTED -> PARTIAL-mykning paa compound claims (5 av 6 miss).
2. Konsistens 13/20 mot 19/20; 7 claims varierte mellom
   SUPPORTED/PARTIAL/INSUFFICIENT.
3. Holdout-skew: 0 SUPPORTED og 0 INSUFFICIENT i fasit; false-accept-retningen
   mot ekte SUPPORTED-claims er undertestet i holdout.
4. Near-miss/adversarial er ikke maskin-tagget; antall rapportert som
   stil-beskrivelse, ikke eksakt taksonomi.
5. Full rule-vs-judge 4-gruppe-tabell paa alle 84 kalibrerings-claims mangler.
6. Holdout er na "brukt": enhver ny kjoring etter prompt-endring krever ny
   versjon og nytt blindt holdout-sett.
7. Kosmetisk: runner-meta skriver "v0.1" i resultatfiler; filnavn-suffiks er
   canonical.
8. v0.3-episoden viser at probe-tuning kan skjule fullsett-regressjon;
   tuning-arbeidsflyt maa bruke fullsett-verifikasjon.

## 33. Anbefalt neste steg

1. Lag v0.3 med regler rettet mot compound-mykning (CONTRADICTED -> PARTIAL)
   og konsistens-grensetilfeller; verifiser paa fullt kalibreringssett, ikke probe.
2. Bygg et FERSKT blindt holdout-sett med balansert fasit (inkl. SUPPORTED og
   INSUFFICIENT) foer evt. re-sertifisering.
3. Beslutt fusion som review-layer (konfigurasjonsstyrt, ikke default) med
   confidence-gate 0,95 og valgfri dobbel-dommer-bekreftelse.
4. Start IKKE live-dialog automatisk; det krever ny eksplisitt go.
