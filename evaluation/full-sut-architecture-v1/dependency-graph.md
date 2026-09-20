# Dependency Graph

Implementation order for the full SUT (product modules under runtime/sut/ unless noted; evaluator modules under evaluation/full-sut-implementation/).

    [frozen foundations: no work, verify only]
      runtime/discovery/* (V1)
      data/local-discovery-runtime-result-v1.schema.json
      evaluation/dev-corpus-scorer-v1/scorer.py (contract, frozen)

    1. schemas
       sut-input.schema.json, sut-output.schema.json (this dir, done in
       architecture task) -> product-side validator module runtime/sut/schemas.py
       (stdlib JSON subset validator pattern from runtime/discovery/schema.py)

    2. data files
       data/safety-triage-rules-v1.json
       data/rules-v1.json (structured rules registry, seeded from verified artifacts)
       data/knowledge-index-v1.json (artifact manifest)

    3. knowledge adapter
       runtime/sut/knowledge.py (index + query)  [depends: 2]

    4. discovery adapter
       runtime/sut/discovery_adapter.py  [depends: 1 (schemas), frozen discovery]

    5. decision context
       runtime/sut/context.py (typed DecisionContext + stage-state enum)

    6. safety triage
       runtime/sut/safety.py  [depends: 2 rules file, 5 context]

    7. decomposition
       runtime/sut/decompose.py  [depends: 5]

    8. route reasoning
       runtime/sut/routes.py  [depends: 2 rules, 3 knowledge, 4 discovery, 5]

    9. evidence aggregation + epistemic assignment
       runtime/sut/aggregate.py  [depends: 8]

    10. answer planning + rendering
        runtime/sut/answer.py  [depends: 9]

    11. pipeline composition (SUT entry)
        runtime/sut/pipeline.py (run(input) -> output)  [depends: 1,5,6,7,8,9,10]

    12. evaluator-side corpus loader
        evaluation/full-sut-implementation/sut_runner/loader.py  [depends: 1]

    13. evaluator-side runner
        evaluation/full-sut-implementation/sut_runner/run.py  [depends: 11, 12]

    14. measurement adapter
        evaluation/full-sut-implementation/sut_runner/measurement.py
        (raw-answer projection for scorer)  [depends: 13]

    15. E2E
        burned dev regression wiring (Phase 3 completion)  [depends: 14]

## Parallelizable

- 2 (data files) parallel with 1.
- 3 and 4 independent of each other; both block 8.
- 6 and 7 independent of each other; both block 11.

## No giant engine

Each numbered box is one module with one responsibility (33-file plan in
implementation-plan.md). The pipeline module composes; it contains no stage
logic.
