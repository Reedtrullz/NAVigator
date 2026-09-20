# Implementation Plan

Concrete plan for the three phases. Every file lists responsibility, public
interface, dependencies, and phase. Test order is TDD where logic exists.
No placeholders: each acceptance gate is mechanically checkable.

## Phase 1 - Skeleton / contracts

### Files

| File | Responsibility | Public interface | Dependencies |
|---|---|---|---|
| runtime/sut/__init__.py | package marker | - | - |
| runtime/sut/schemas.py | validate sut-input/v1 + sut-output/v1 + DecisionContext | validate_input(doc), validate_output(doc), validate_context(doc); SchemaError | schemas in this dir (copied into runtime/sut/schemas/ as frozen copies at Phase 1 start, SHA-verified) |
| runtime/sut/context.py | typed DecisionContext + stage-state enum + factory | make_context(sut_input), mark_stage(ctx, stage, state) | schemas.py |
| runtime/sut/pipeline.py | compose S1-S11 as pass-through skeleton (stages present, minimal logic) | run(input_dict, config) -> output_dict | schemas.py, context.py |
| data/safety-triage-rules-v1.json | frozen triage vocabulary (seeded from artifacts 26/45/57 safety content) | data file | - |
| data/rules-v1.json | structured rules registry (seed: R-PRI-4A-65D 65 days under 23; R-PAS-2-2A-10D 10-day assessment; R-EMERGENCY-113/116x) | data file | - |
| data/knowledge-index-v1.json | artifact manifest with class + freshness | data file | - |
| runtime/sut/pipeline.py stage stubs S1-S11 | each stage a function with signature stage(ctx) -> ctx | internal | context.py |
| evaluation/full-sut-implementation/sut_runner/__init__.py | evaluator package | - | - |
| evaluation/full-sut-implementation/sut_runner/loader.py | gold strip + integrity | load_corpus, strip_gold, iter_inputs; GoldLeakError | sut-input schema copy |
| evaluation/full-sut-implementation/sut_runner/run.py | execute + freeze | CLI: run(corpus, out, mode); writes predictions/, errors/, run-log.jsonl, predictions-manifest.json | loader.py, pipeline.run |

### TDD order

1. test_schemas.py: valid input round-trip -> run -> schemas.py passes.
2. test_context.py: context factory + stage marks -> context.py.
3. test_loader.py: load routing_cases.json, assert gold stripped, assert
   GoldLeakError on planted keys -> loader.py.
4. test_runner.py: run corpus in replay -> predictions exist for 120 cases,
   manifest SHAs match, no gold keys in any prediction (mechanical grep),
   run-log present -> run.py.

### Acceptance gates (Phase 1)

- python3 -m unittest discover -s runtime/sut -p 'test_*.py': all pass.
- python3 -m unittest discover -s evaluation/full-sut-implementation/sut_runner -p 'test_*.py': all pass.
- Runner freeze on all three corpus files completes; 120 prediction files;
  grep for gold field names in predictions/ returns 0 matches.
- Measurement V3 baseline manifest SHA unchanged (re-verified at Phase 1 end).

## Phase 2 - Pipeline integration

### Files

| File | Responsibility | Public interface | Dependencies |
|---|---|---|---|
| runtime/sut/knowledge.py | index + query over frozen manifest | load_index(), query(index, track) -> [KnowledgeEvidence] | data/knowledge-index-v1.json, artifacts |
| runtime/sut/discovery_adapter.py | adapter over frozen discovery | discover(request) -> DiscoveryOutcome per local-discovery-interface.md | runtime/discovery, frozen schema |
| runtime/sut/safety.py | deterministic triage | triage(query, profile, rules) -> SafetyState | data/safety-triage-rules-v1.json |
| runtime/sut/decompose.py | track splitting | decompose(input, safety) -> [Track] | context.py |
| runtime/sut/routes.py | eligibility + candidate routes | resolve_routes(tracks, evidence, discovery, profile, rules) -> [CandidateRoute] | rules, knowledge, discovery adapters |
| runtime/sut/aggregate.py | evidence merge + epistemic collapse | aggregate(ctx), assign_epistemic(ctx) | routes.py |
| evaluation/full-sut-implementation/fixtures/*.json | burned dev fixtures (22) | data files | - |

### TDD order

1. test_safety.py: all 20 safety_cases utterances -> correct priority +
   suppression -> safety.py.
2. test_decompose.py: 4 multi-domain fixtures + fallback -> decompose.py.
3. test_knowledge.py: span extraction verbatim on 5 artifacts -> knowledge.py.
4. test_discovery_adapter.py: 4 failure simulations + schema passthrough ->
   discovery_adapter.py.
5. test_routes.py: rules arithmetic (65-day, 10-day, referral) -> routes.py.
6. test_aggregate.py: merge/conflicts/precedence -> aggregate.py.
7. test_pipeline_integration.py: multi-track, fail-closed, source-unavailable,
   safety-priority scenarios -> pipeline.py wired with real stages.

### Acceptance gates (Phase 2)

- All unit + component + integration suites pass.
- Safety: 20/20 safety_cases triage correct on utterance text alone.
- FC-01..FC-05 tests demonstrably fire.
- Phase 1 suite still passes (no regression).

## Phase 3 - End-to-end

### Files

| File | Responsibility | Public interface | Dependencies |
|---|---|---|---|
| runtime/sut/answer.py | plan + render | plan_answer(ctx), render(plan) -> answer text | aggregate.py |
| evaluation/full-sut-implementation/sut_runner/measurement.py | raw-answer projection + capabilities | project_output(sut_output) -> scorer-compatible raw answer; capabilities_for(family) | measurement-v3-mapping.md |

### TDD order

1. test_answer.py: block ordering, presented_as_complete, verbatim spans ->
   answer.py.
2. test_measurement.py: projection covers all scorer fields for all 120
   projections (dry-run against scorer._normalize_raw_answer without
   scoring) -> measurement.py.
3. test_security.py: 4 security tests from security-architecture.md.
4. test_determinism.py: rerun frozen run in replay -> byte-identical.

### Acceptance gates (Phase 3)

- All suites pass; projection normalize-errors = 0 across 120 cases.
- Security suite passes.
- Determinism test passes (replay byte-identical).

## Commit / checkpoint boundaries

1. Checkpoint 1: Phase 1 schemas + loader + runner + frozen skeleton run
   (one commit; Phase 1 review + freeze).
2. Checkpoint 2: Phase 2 adapters + stages + fixtures + second frozen run
   (one commit; Phase 2 review + freeze).
3. Checkpoint 3: Phase 3 answer + measurement projection + security +
   determinism + third frozen run (one commit; Phase 3 review + freeze).

Each checkpoint is a separate reviewable unit; no phase starts before the
previous one is frozen.
