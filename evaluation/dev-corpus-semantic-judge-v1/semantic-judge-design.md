# semantic-judge-design V1

## Formaal

Gjoere det semantiske dommerlaget bak frozen Scorer V1 til et validert
maaleinstrument. Dette er IKKE runtime-development. Scorer V1, corpus
og gold er immutable; alle sha-verifikasjoner i `baseline-integrity.json`.

## Arkitektur

```
CASE -> gold stripped -> SUT -> FROZEN PREDICTION
  -> DETERMINISTIC SCORER (Scorer V1, uendret)
  -> kun UNRESOLVED dimensjoner -> SEMANTIC JUDGE (GPT-5.6-Luna)
  -> deterministisk span-validering -> semantic result eller UNRESOLVED
```

Deterministic-first er hard: en terminal deterministisk vurdering kan
aldri overstyres av dommeren. Adapteret kaller kun dommeren naar
deterministisk resultat er UNRESOLVED (eller canonical ekvivalent).

## Dimensjoner og frozen label-sett

| Dimensjon | Labels |
|---|---|
| critical_condition | TRIGGERED / NOT_TRIGGERED / UNRESOLVED |
| forbidden_claim | PRESENT / ABSENT / UNRESOLVED |
| route_equivalence | CANONICAL_ACCEPTABLE / EQUIVALENT_ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE / UNRESOLVED |
| uncertainty | SATISFIED / PARTIAL / VIOLATED / NOT_REQUIRED / UNRESOLVED |

Ingen free-form overall verdict, ingen answer-quality-score.

## Kriterieseparasjon

Hvert judge-kall mottar KUN: case_context (utterance), den ENE
gold-criterion som scores, og SUT-answer. Ikke hele gold-record.
Case-ID har ingen semantisk betydning og brukes kun til logging.

## Evidence spans

Alle non-UNRESOLVED verdicts krever minst ett evidence span som er
verbatim-substring (etter normalisering) av SUT-answer. Valideres
deterministisk; brudd gir verdict INVALID -> fail closed til UNRESOLVED.

## Injection-robusthet

SUT-answer-tekst behandles utelukkende som innhold. Instruksjoner i
answer-teksten (f.eks. "ignore the scoring rules") skal aldri folges.
Testes med dedikerte injection-fixtures.

## Retry-policy (preregistrert, frosset)

1. Schema-invalid response: maks 1 teknisk retry (samme input, uendret prompt).
2. Substantivt merkelig verdict: INGEN retry.
3. Timeout/provider-feil: execution failure, registreres, ingen silent retry.
4. Etter mislykket teknisk retry: verdict = UNRESOLVED (fail closed).

## Valideringsprotokoll

1. Kalibreringssett (20 andre fixtures) for prompt-utvikling. Blir burned.
2. Freeze contract (prompt-hash, config, retry-policy) foer official run.
3. 60+ validation fixtures dobbelt-labelt i to blinde pass; disagreement
   adjudiceres foer judge kjoeres; gold fryses med SHA.
4. Official one-shot run mot frozen contract. Ingen prompt-endring etterpaa.
5. Stabilitet: minst 20 fixtures x 5 kjoeringer, modal agreement >= 95%.
6. Schema-failure tester: deterministisk validator skal feile malformed
   JSON, invalid enum, manglende span, span ikke i answer, ekstra felt.
7. Integrasjon: ny adapter-linje `dev-corpus-scorer-v1-semantic/`;
   deterministic-first, ingen override; testet med mock-judge + ekte kall.

## No-override-registrering

Alle integrajsonstester loggar om noen deterministisk terminal verdi ble
overstyrt. Forventet count: 0.
