# Quote-Aligner / Deterministic Polarity Engine (v0.5-prototype)

Deterministisk quote-aligner og polarity-motor som erstatter LLM-kall
(gpt-5.6-luna) i polarity-steget i semantic-judge. Null modellkall:
alle verdicts kommer fra regelbasert span-alignment mellom claim og source.

## Status

TASK-LOCK.json: SEMANTIC-JUDGE-DETERMINISTIC-POLARITY-ALIGNER, status
ACTIVE. Maks 2 implementerings-iterasjoner (A + B) er BRUKT. Ingen nye
motor-iterasjoner i denne task-lock; kun regresjonsfiks er tillatt.

## Kjoring

Fra repo-rot:

    cd "evaluation/semantic-judge/quote-aligner"
    python3 run_benchmarks.py --bench all        # alle bench + ent + stability
    python3 tests/test_polarity_engine.py        # 11/11 enhetstester

Resultater lander i results/qa05-*.json.

## Hovedresultater (siste fullkjoring)

| Bench | n | Acc | ContraP | InsufR | FP-Sup |
|---|---|---|---|---|---|
| minimal-pairs | 48 | 0.7083 | 0.6667 | 0.8462 | 0 |
| minimal-pairs-supplement | 4 | 0.75 | 0.6667 | - | 0 |
| contra-insuff | 69 | 0.7681 | 0.9583 | 0.9375 | 1 |
| modality | 30 | 0.7667 | 0.80 | 1.0 | 0 |
| actor-scope | 30 | 0.6333 | 0.0 | 0.8667 | 1 |
| locality | 20 | 0.90 | - | 1.0 | 0 |
| diagnostic-20 | 20 | 0.65 | 0.6667 | 0.60 | 2 |
| ent | 4 | 0.75 | 1.0 | 1.0 | 0 |
| stability 30x5 | 150 | 1.0 | 1.0 | 1.0 | 0 |

Determinisme: 5 identiske run-hasher (100 % reproducerbarhet).
Readiness: NOT_READY_FOR_BLIND_RECERTIFICATION (se final-report.md pkt 50).

## Filstruktur

- polarity_engine.py - motor: normalisering, atom-splitting, decide_atom, aggregering
- quote_aligner.py - span-alignment mot source-tekst
- run_benchmarks.py - deterministisk bench-harness (leser frosne v0.3/v0.4.1-set)
- tests/test_polarity_engine.py - 11 enhetstester (inline tekster, ingen case-ID-er)
- modality-map.json, predicate-map.json - frosne signal-kart
- TASK-LOCK.json - task-lock (skal ikke slettes)
- final-report.md - 52-punkts sluttrapport
- architecture.md - arkitekturbeskrivelse
- polarity-wobble-audit.md - v0.4.1 wobble-audit (grunnlaget for designet)

## Harde constraint

- Ingen case-ID-logikk (id_guard = 0 treff).
- Ingen modellkall i motoren eller harnessen.
- v0.2/v0.3/v0.4/v0.4.1 er frosne og read-only.
- Ikke start holdout-v3, blind-re-sertifisering eller live-dialog.
