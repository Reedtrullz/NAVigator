# Next Task: Phase 1 Implementation

Copy-paste-ready task for the owner to authorize after this architecture task
reaches terminal status.

---

NY OPPGAVE - FULL SUT IMPLEMENTATION PHASE 1

## TASK ID

NAV-EXPLORE-FULL-SUT-IMPLEMENTATION-PHASE-1

Arbeidsmappe: /Users/reidar/Projectos/NAV Explore

Autoritativ arkitektur:
evaluation/full-sut-architecture-v1/ (frozen; manifest SHA registreres ved
oppgavestart).

## Scope

Kun Phase 1 fra implementation-plan.md:

1. runtime/sut/ pakke: schemas.py, context.py, pipeline.py (pass-through
   skeleton S1-S11).
2. Datafiler: data/safety-triage-rules-v1.json, data/rules-v1.json,
   data/knowledge-index-v1.json (frosne data, seedet fra allerede validerte
   artefakter; ingen ny research).
3. Evaluator-side: evaluation/full-sut-implementation/sut_runner/ med
   loader.py (gold strip + integritet) og run.py (execute once, freeze,
   aldri score inline).
4. Tester: test_schemas.py, test_context.py, test_loader.py, test_runner.py.

## Harde regler

- Ingen Phase 2 (ingen kunnskaps-/discovery-adaptere, ingen ekte ruting).
- Ingen scoring i runner-prosessen; ingen gold i noen prediction-fil.
- Ingen endring i evaluation/measurement-v3-combined-freeze/,
  evaluation/dev-corpus-scorer-v1/, runtime/discovery/,
  runtime/discovery_v2/.
- Ingen LLM-stadier; ingen live discovery; ingen deployment.
- GOLD_VISIBLE_TO_SUT = 0 verifiseres mekanisk.

## Testkommandoer

    python3 -m unittest discover -s runtime/sut -p 'test_*.py'
    python3 -m unittest discover -s evaluation/full-sut-implementation/sut_runner -p 'test_*.py'
    python3 -m sut_runner.run --corpus evaluation/dev-corpus-v1/cases/safety_cases.json --out evaluation/full-sut-implementation/runs/<run-id>/ --mode replay
    (og tilsvarende for routing_cases.json og discovery_adversarial_cases.json)

## Akseptanser

1. Alle unittest-suiter passer.
2. Freeze fullforer for alle 120 caser; 120 prediction-filer + manifest med
   SHA-er.
3. grep etter gold-feltnavn i predictions/ gir 0 treff.
4. Measurement V3 manifest SHA uendret ved oppgaveslutt.
5. Run-log.jsonl finnes per run med stage/state/latency.

## Terminalstatus

Velg nøyaktig én:

- FULL_SUT_PHASE_1_READY - alle akseptanser passer; skeleton freeze registrert.
- FULL_SUT_PHASE_1_FAILED - en akseptanse feiler; ingen iterative fiks-runder
  utover én begrenset bugfix-pass.
- FULL_SUT_PHASE_1_INVALID - frozen baseline eller arkitekturmanifest
  kompromittert.

## Stopp

Ved terminalstatus: STOPP. Ingen Phase 2 uten ny eksplisitt oppgave.

---
