# Wave 2 Source Change Summary

Attempt 1 of max 2. Diff base: Wave-1 frozen candidate manifest
components (evaluation/full-sut-repair-wave-1-v1/repaired-sut-manifest.json,
24 components; all 18 untouched components verified byte-identical).

## Changed components (6)

| File | Wave-1 SHA-256 prefix | Wave-2 SHA-256 prefix | RCs |
|---|---|---|---|
| data/knowledge-index-v1.json | b83a0808ee8b | c8de229b663e | RC-08 (metadata: doc domains array) |
| runtime/sut/phase2/knowledge.py | 7b33b160805a | d9e3c54e64cb | RC-08, RC-07 |
| runtime/sut/phase2/pipeline.py | 2c9eba079b57 | 3735239efa36 | RC-07, RC-08, RC-10, RC-11 |
| runtime/sut/phase2/routes.py | 20580dcd48c7 | a543c2f70f3e | RC-07 |
| runtime/sut/phase3/finalize.py | 304683957ff5 | c6fa207d20a3 | RC-10, RC-11 |
| runtime/sut/phase3/planner.py | 02f151558083 | 835530d9c1e1 | RC-08, RC-07 |

Full hashes: hashes.txt (lineage freeze).

## Not changed

- runtime/sut/phase2/safety.py and all emergency-trigger logic
  (EMERGENCY_TRIGGER_LOGIC_CHANGED = false)
- runtime/sut/schemas/* (frozen scorer contracts; additive evidence keys are
  schema-safe under additionalProperties)
- discovery adapter, decompose, aggregate, render, context, pipeline root
- all gold, measurement, prediction, and evaluation artifacts

## New / updated tests

Six test files covering the spec matrices (RC-08 13, RC-07 12, RC-10 11,
RC-11 18 incl. the updated pinned expectation). Full suite: 215/215 passed.

## Anti-tuning attestation

- No case IDs, corpus strings, expected verdicts, or benchmark-specific route
  mappings in runtime logic (id-guard scan: 0 hits on runtime, tests excluded).
- All fixes are generic mechanisms: domain-scoped retrieval, CURRENT-before-
  snapshot slot ordering, service-concept target guard, per-route/per-claim
  evidence attachment, fine-class emission.
- No evaluator/measurement imports in runtime code; the one pre-existing
  evaluation-path reference (discovery_adapter fixture manifest) is unchanged
  from the Wave-1 pin.
