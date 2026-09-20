# dev-corpus-scorer-v1

Reproducerbar scorer for det burned 120-case dev-korpuset i
`evaluation/dev-corpus-v1/`.

## Status

Se `TASK-LOCK.json` og `final-report.md`.

## Arkitektur

```
CASE INPUT (gold stripped)
   -> SYSTEM UNDER TEST
   -> RAW ANSWER
   -> NORMALIZER
   -> SCORER (deterministisk lag + pluggbar semantisk lag)
   -> PER-CASE RESULT + AGGREGATER
```

Gold er kun lesbar for scoreren. SUT-motoren mottar en execution copy
der alle gold-felter er fjernet. Invarianten
`GOLD_FIELDS_EXPOSED_TO_SUT = 0` testes eksplisitt i `test_scorer.py`.

## Filer

* `scorer-design.md`: arkitektur og regler
* `scorer.py`: implementasjon (stdlib Python)
* `test_scorer.py`: fixture-selftest, gold-leakage-test, determinisme
* `scorer-fixtures.json`: 26 syntetiske SUT-outputs (testdata, ikke NAV-eval-data)
* `scorer-contract-v1.json`: frozen kontrakt
* `scorer-result.schema.json`: per-case output-skjema
* `scorer-manifest.json`: sha256 over alle leveransefiler

## Kjoring

```
python3 test_scorer.py
```

Skriptet skriver `scorer-fixture-results.json` og `determinism-report.json`
naar alle tester gaar gront.
