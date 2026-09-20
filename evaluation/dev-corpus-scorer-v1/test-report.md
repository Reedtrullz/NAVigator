# test-report

## RED

Foerste kjoering etter test-fil og fixtures ble skrevet, foer implementasjon:

```
ModuleNotFoundError: No module named 'scorer'
```

Det er ekte RED: ingen produksjonskode eksisterte.

## Mellomliggende feil (bundet bugfix-pass)

1. Test-harness sammenlignet `scorer_notes` mot fixtures' `notes`-noekkel: rettet i test-harness.
2. Deterministisk forbidden-matching fanget ikke praefiks-token ("bup" i "bup automatisk"): la til token-basert matching.
3. Route-matching delte kun paa mellomrom ("skolen/helsesykepleier"): la til separator-bevisst tokenisering.
4. `FULLY_VERIFIED` ble normalisert til "fully_verified" og bommet paa claim-sammenligning: foldet understrek inn i normaliseringen.
5. Condition-map-noekler var ikke normalisert ("source_url" vs "source url"): frozen lookup-tabell normaliseres ved lasting.

Ingen endringer i fixtures' forventninger for aa skjule feil; alle endringer var i scorer eller test-harness.

## GREEN

```
gold leakage: GOLD_FIELDS_EXPOSED_TO_SUT = 0
fixtures: 26/26 PASS
schema shape: required keys and enums present
determinism: 3/3 byte-identical
ALL GREEN
```

## Dekning

* 26 fixtures (spec minimum 24): pass, fail, forbidden claim, critical error, uncertainty violation, route equivalent, route partial, missing provenance, execution failure, not applicable, unmapped condition fail-closed, stub-judge annotasjon.
* Gold-leakage: alle gold-noekler testet mot SUT-input-byggeren, 0 eksponerte.
* Determinisme: 3 kjoeringer av hele fixture-settet, byte-identisk (sha256 i `determinism-report.json`).
* Skjema: paakrevde resultatsnoekler og enums verifisert mot `scorer-result.schema.json`-definisjonen.

## Ikke testet her

Kjoring mot ekte 120-case SUT-output: krever Phase B med legitim SUT. Ikke utfoert; se `final-report.md`.
