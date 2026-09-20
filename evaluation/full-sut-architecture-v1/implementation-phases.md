# Implementation Phases

Based on the gap report's three-phase recommendation, adapted per
gap-report-extraction.md section 5 (lane ingestion moves to a separate
evaluator follow-up; product phases stay three).

## Phase 1 - SUT skeleton / contracts

- Scope: schemas validated in code (runtime/sut/schemas.py), DecisionContext
  (context.py), safety + rules + knowledge-index data files, pipeline module
  with pass-through stage composition (no sophisticated answering yet),
  evaluator-side corpus loader (loader.py) + runner (run.py) with prediction
  freeze.
- Interfaces: run(input)->output per sut-output/v1; loader API per
  corpus-loader-design.md; runner CLI per execution-harness-design.md.
- Prerequisites: architecture freeze (this task); measurement V3 baseline
  intact; discovery V1 frozen (verified).
- Test gates: schema round-trip tests; gold-strip guard test; runner executes
  all 120 corpus cases in replay mode and freezes predictions; zero gold in
  any prediction file; runner emits run-log.jsonl.
- Terminal deliverable: frozen run directory from the skeleton executing the
  full corpus (answers will be minimal/degraded; correctness comes later).
- What remains: real retrieval/discovery/reasoning (Phase 2), measurement
  adapter (Phase 3).

## Phase 2 - Decision pipeline integration

- Scope: knowledge adapter (knowledge.py), discovery adapter
  (discovery_adapter.py), safety triage (safety.py), decomposition
  (decompose.py), route reasoning (routes.py), aggregation + epistemic
  (aggregate.py).
- Interfaces: per dependency-graph.md; adapter contracts per
  local-discovery-interface.md and knowledge-layer-interface.md.
- Prerequisites: Phase 1 frozen; rules/index data files SHA-pinned.
- Test gates: safety triage catches all 20 safety_cases utterances
  deterministically; discovery adapter failure simulations pass;
  fail-closed contract tests (FC-01..FC-05); epistemic precedence tests;
  no-regression on Phase 1 skeleton tests.
- Terminal deliverable: pipeline produces full structured output on replay
  fixtures; second frozen corpus run.
- What remains: answer rendering polish, measurement adapter, E2E scoring.

## Phase 3 - End-to-end answer pipeline

- Scope: answer planner + renderer (answer.py), measurement adapter
  (measurement.py: raw-answer projection + capabilities wiring), observability
  hardening, security tests, burned dev regression readiness.
- Interfaces: measurement-v3-mapping.md fields all direct/derived.
- Prerequisites: Phase 2 frozen.
- Test gates: third frozen corpus run; scorer adapter can consume all 120
  raw-answer projections without normalize errors; security test list from
  security-architecture.md passes; replay determinism (byte-identical rerun
  under same SHAs).
- Terminal deliverable: SUT baseline runnable end to end against Measurement
  V3; full SUT definition-of-done checklist (spec 36) evaluable.
- What remains: burned dev regression execution (separate task), any future
  fresh holdout (separate owner-authorized task), evaluator-side lane
  ingestion CLI (separate evaluator task).

## Explicitly out of all three phases

Product human review, LLM stages, live discovery without authorization,
measurement system changes, deployment.
