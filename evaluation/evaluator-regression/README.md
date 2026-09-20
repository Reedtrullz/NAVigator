# Evaluator-regresjon (kalibreringssuite)

Denne suiten provoer **evaluatoren** (scoreren i `evaluation/score_baseline.py`
og reglene i `run_evaluator_regression.py`) - ikke kunnskapbasen. KB-regresjonen
(`score_baseline.py` -> `baseline-results.json` / `final-results.json`) og denne
suiten kjoeres separat og skal aldri "fikses" ved aa endre KB for aa faa tester
gjennom.

## Kjoering

    python3 evaluation/score_baseline.py evaluation/final-results.json   # KB-regresjon (48 ruter)
    python3 evaluation/evaluator-regression/run_evaluator_regression.py  # denne suiten

Suiten skriver `results.json`, `metrics.json`, `subsuite-results.json` og
`calibration-report.md` i denne katalogen.

## Kontrolltyper

| Type | Fil | Antall | Krav |
|---|---|---|---|
| Positive kontroller | golden-ruter (foerste 24) | 24 (min 20) | TP |
| Negative kontroller | `controls.json` | 50 | TN, hard FAIL for safety/juridisk |
| Subtile negativer | `controls.json` (subtle=true) | 27 (min 25) | TN |
| Safety-kritiske | `controls.json` (safety=true) | 10 (min 10) | TN, FP=0 |
| Typed fact-mutasjoner | `mutations.json` | 46 (min 40) | oppdaget (TN) |
| Source entailment A-D | innbakt i runner | 4 | dokumentert lexikalsk limitasjon |
| Resolver-regresjon | innbakt i runner | 10 gyldige + 3 ugyldige | ugyldig -> teknisk, aldri FP |
| Akronymregresjon | innbakt i runner | 10 akronymer (akronym/fullt navn/begge) | alle ok |

## Metrikk

Confusion matrix (positiv = faglig korrekt svar): TP/TN/FP/FN + accuracy,
precision, recall, specificity, FPR, FNR. Gateverdier: safety-FP = 0,
subtile-FP = 0. Tekniske feil skilt ut som `TECHNICAL_FAIL` (resolver/akronym)
og holdt utenfor de faglige feilprediksjonene.

## Kjente begrensninger (dokumentert, ikke doelt)

1. Scoreren er **lexikalsk**: den kontrollerer termpresence i kilder, ikke
   semantisk entailment. ENT-C/ENT-D viser at feil claims kan faa lexikalsk
   "pass" mot relevante kilder; dette registreres som begrensning inntil en
   semantisk scorer (LLM-judge) innfoeres.
2. Mutasjonsdeteksjon er regelbasert per scenario (`MUTATION_RULES`) pluss
   programmatisk nummerdeteksjon: mutert faktum maa vaere til stede i tekst,
   original maa vaere borte, eller hard-fail maa fyre spesifikt paa den muterte
   varianten.
3. Id-serien i `mutations.json` har bevisste hull fra arbeidsloggen
   (MUT013/019/032/038/046-049/051-052); antallet som teller er rader i fila.
