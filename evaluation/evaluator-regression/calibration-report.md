# Evaluator-kalibreringsrapport (30.08.2026)

Suite: evaluation/evaluator-regression/ - tester evaluatoren (ikke KB).

## Confusion matrix (positiv = faglig korrekt)

| | Predicted FAIL | Predicted PASS |
|---|---|---|
| Actual korrekt (positive) | FN 0 | TP 24 |
| Actual feil (negative+mutasjoner) | TN 96 | FP 0 |

- Accuracy: 1.00
- Precision: 1.00
- Recall: 1.00
- Specificity: 1.00
- FPR: 0.00
- FNR: 0.00
- Safety-kritiske (kontroller+mutasjoner): n=20, TN=20, FP=0 (FP maa vaere 0)
- Subtle: n=73, TN=73, FP=0
- Tekniske feil (resolver/akronym): 0 (skilt fra faglig utfall)

## 0-5 score-kalibrering

- Snittscore korrekt gjenkjent: 5.00
- Snittscore oppdagede negative: 1.00
- Konklusjon: INFORMATIV

## Mutasjonsdeknapp

- Mutasjoner: 46, oppdaget: 46, miss: 0

## Source entailment (lexikalsk begrensning)

- ENT-A (SUPPORTS): lexical_pass=True - bevisfinnelse er ikke semantisk entailment
- ENT-B (CORRECT-CLAIM-WEAK-SOURCE): lexical_pass=True - bevisfinnelse er ikke semantisk entailment
- ENT-C (WRONG-CLAIM-RELEVANT-SOURCE): lexical_pass=True - bevisfinnelse er ikke semantisk entailment
- ENT-D (WRONG-CLAIM-CONTRADICTING-SOURCE): lexical_pass=True - bevisfinnelse er ikke semantisk entailment

## Resolver

- 48 -> 48-barnebidrag-i-dybden.md
- 16-livssituasjoner -> DIR:16-livssituasjoner
- 70-lokalt/trondheim -> DIR:70-lokalt/trondheim
- legal-index.json -> data/legal-index.json
- services-index.json -> data/services-index.json
- familieokonomi-regler.json -> data/familieokonomi-regler.json
- local-services-trondheim.json -> data/local-services-trondheim.json
- 70-lokalt/trondheim/08-mari-case.md -> 70-lokalt/trondheim/08-mari-case.md
- 08-mari-case -> 70-lokalt/trondheim/08-mari-case.md
- 57-nodhjelp-og-akutte-situasjoner -> 57-nodhjelp-og-akutte-situasjoner.md
- 99999 -> None
- ikke-en-fil.json -> None
- 70-lokalt/trondheim/99-finnes-ikke.md -> None

## Akronymer

- BUP: acronym=True full=True both=True
- HABU: acronym=True full=True both=True
- PPT: acronym=True full=True both=True
- RPH: acronym=True full=True both=True
- DPS: acronym=True full=True both=True
- AAP: acronym=True full=True both=True
- SFO: acronym=True full=True both=True
- HFU: acronym=True full=True both=True
- BFT: acronym=True full=True both=True
- NAV: acronym=True full=True both=True

## Begrensninger

- Dagens scorer er lexikalsk: den kontrollerer termpresence, ikke semantisk entailment.
- Source entailment C/D kan therefore passere lexikalsk; dette er dokumentert, ikke dolt.
- Mutasjonsdetektorer er programmatiske (mutat faktum ma vaere til stede, original ma vaere borte).