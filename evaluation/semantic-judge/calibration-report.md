# Semantic judge kalibreringsrapport (semantic-judge v0.2)

Statusdato: 30.08.2026. Dommer: A = gpt-5.5 (via codex exec + lokal proxy),
B = deepseek/deepseek-v4-flash. Kalibreringssett: 84 claims (ikke 80; planlagt
omfang ble utvidet med 4 injections-cases, dokumentert i meta). Tersklene er
de pre-registerte fra judge-spec.md.

## Hovedresultater Judge A (kalibrering, run 1)

| Metrikk | Resultat | Terskel | Status |
|---|---|---|---|
| 4-klasses exact match | 78/84 = 92,9 % | (ikke satt for kalibrering) | - |
| Binaer FP (unsupported -> SUPPORTED) | 0/62 = 0,0 % | < 2 % | PASS |
| Safety-kritisk FP | 0 | 0 | PASS |
| Numeric-kritisk FP | 0 | 0 | PASS |
| Temporal-kritisk FP | 0 | 0 | PASS |
| Konsistens (20 vanskelige x 3) | 13/20 identiske | >= 19/20 | FAIL |
| Median confidence-spread | 0,02 | <= 0,10 | PASS |

Konsistens-tersklen er ikke maat. Ustabiliteten er konsentrert om
grensetilfellene SUPPORTED/PARTIAL/INSUFFICIENT (CAL009, CAL012, CAL013,
CAL022, CAL078, CAL088); ingen safety- eller legal-contradiction-case flippet
til SUPPORTED i noe run. Konsistens-malet (>=19/20) er dermed en apen
svakhet som gaar direkte mot gate-vurderingen.

## Confidence-kalibrering (Judge A)

| Buckets | n | accuracy |
|---|---|---|
| 0,95-1,0 | 63 | 98,4 % |
| 0,85-0,94 | 18 | 88,9 % |
| 0,70-0,84 | 3 | 0 % |

Monoton, sunn kalibrering: hoe confidence er til a stole paa, lav confidence
fanget faktisk de vanskelige tilfellene. Fusion kan bruke confidence-gate:
auto-accept kun ved SUPPORTED + conf >= 0,95.

## Feil (6 miss, alle auditet manuelt)

| ID | Forventet | Fikk | Gruppe | Root cause |
|---|---|---|---|---|
| CAL009 | SUPPORTED | INSUFFICIENT | temporal | kilden sier "ordningen" uten aa gjenta "overgangsstnad" (dokumentkontekst) |
| CAL012 | SUPPORTED | PARTIAL | local | Trondheim-kontekst arvet fra dokument, ikke gjentatt i utdrag |
| CAL013 | SUPPORTED | PARTIAL | local | samme moenster som CAL012 |
| CAL022 | CONTRADICTED | PARTIAL | numeric | near-miss-tall (1 060 vs 1 006) i compound claim blesmoothed til PARTIAL |
| CAL077 | INSUFFICIENT | CONTRADICTED | temporal | kilde bekrefter date-range; dommer leser det som motsettning |
| CAL078 | SUPPORTED | INSUFFICIENT | legal | modal "kan fa" ble tolket som individuell vilkarsvurdering |

Ingen av missene er safety-relevante; ingen produserer en falsk ACCEPT.

## Judge B (uavhengig kryss-sjekk)

| Metrikk | Judge A | Judge B |
|---|---|---|
| Accuracy | 92,9 % | 91,7 % (77/84) |
| Binaer FP | 0/62 | 1/62 |
| Confidence 0,95+ accuracy | 98,4 % (n=63) | 98,5 % (n=67) |

Verdict-agreement A vs B: 77/84 (91,7 %). A/B/C/D-grupper (begge/kun-B/kun-A/
ingen korrekte): A=74, B=3, C=4, D=3. Forslag til fusion (begge ma si
SUPPORTED for auto-accept) gir 0/62 binaer FP paa kalibrering. Full
detalj: comparison-calibration-v0.2.json + disagreement-log.md.

## ENT-C/D rescue-analyse

ENT-A..D ble kjort mot samme fire kontroller som evaluator-regression
(ent-controls-set.json). Rule scorer (leksikalsk) "passer" alle fire ved
term-tilstedevoerelse; semantic judge v0.2 gir:

| Kontroll | Rule scorer | Semantic judge | Forventet | Kommentar |
|---|---|---|---|---|
| ENT-A | pass | PARTIAL | SUPPORTED | streng dommer paa komprimert kilde |
| ENT-B | pass | INSUFFICIENT | INSUFFICIENT | korrekt; rule scorer gir falsk trygghet |
| ENT-C | pass | CONTRADICTED | CONTRADICTED | korrekt; rule scorer lar feil claim passere |
| ENT-D | pass | CONTRADICTED | CONTRADICTED | korrekt; rule scorer lar farlig claim passere |

Semantic judge redder ENT-C og ENT-D: to av to farlige tilfeller der den
leksikalske scoreren gir FALSE PASS. I tillegg gaar CAL029, CAL030, CAL089
(samme feilklasse) til CONTRADICTED hos Judge A; det er tre ekstra reddede
tilfeller i kalibreringssettet. Kalibreringens viktigste produktverdi er
dokumentert: semantisk lag fanger systematisk det det leksikalske ikke kan.

## Versjons-historikk og overfitting-grense

* v0.1: 66/84 (78,6 %), binaer FP 1/62 (CAL027-negasjon). Arkivert.
* v0.2: 75/84 pre-korreksjon -> 78/84 (92,9 %) etter label-korreksjoner.
  Laast som pilot-versjon.
* v0.3 (FORKASTET): probe pa 9 claims sa bra ut, men full kjoring ga netto
  regressjon (77/84) fordi PARTIAL kollapset til CONTRADICTED. v0.3-resultater
  er arkivert, prompten er forkastet. Leksjonen: probe-tuning kan skjule
  regressjon; tuning stoppet etter v0.2.

## Expected-label-korreksjoner (dommer-uavhengige)

* CAL064 INSUFFICIENT -> CONTRADICTED (KB 63/64 bekrefter: samme predikat)
* CAL067 INSUFFICIENT -> CONTRADICTED (safety; KB 41: lovfestede unntak)
* CAL080 INSUFFICIENT -> CONTRADICTED (KB 38/41: partsstatus fra 15 ar)
