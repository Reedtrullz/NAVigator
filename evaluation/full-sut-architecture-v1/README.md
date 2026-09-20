# Full SUT Architecture V1

Task: NAV-EXPLORE-FULL-SUT-ARCHITECTURE-V1

This directory contains the architecture and implementation plan for the full
NAV Explore SUT (system under test): a legitimate end-to-end product pipeline
that consumes a user case and emits a structured, measurable answer.

Authoritative inputs:

- Frozen measurement baseline: evaluation/measurement-v3-combined-freeze/
  (manifest SHA 331310497a6630dcefc2990079593eed048b9dc4808e8800b0b94b73cb9847c7,
  status MEASUREMENT_V3_COMBINED_FREEZE_READY, 22/22 artifacts byte-stable).
- Gap report: evaluation/measurement-v3-combined-freeze/full-sut-gap-report.md
  (read in full; extracted in gap-report-extraction.md).
- Frozen local-discovery runtime lineages: runtime/discovery/ (V1) and
  runtime/discovery_v2/ (V2.4/V2.5 candidates), reused as components, not copied.

This task produces architecture + implementation plan ONLY:

- no product runtime implementation,
- no fresh product holdout,
- no measurement-system changes,
- no deployment.

Document map:

| Document | Question it answers |
|---|---|
| gap-report-extraction.md | What does measurement expect, what is missing? |
| existing-component-inventory.json | What already exists, callable, frozen? |
| product-vs-measurement-boundary.md | What is product vs evaluator? |
| sut-boundary.md | What does the SUT accept and return? |
| canonical-pipeline.md | What are the ordered pipeline stages? |
| decision-context.schema.json | Canonical internal state (DecisionContext). |
| sut-input.schema.json | Canonical SUT input. |
| sut-output.schema.json | Canonical SUT output. |
| provenance-contract.md | How claims trace to evidence. |
| epistemic-state-contract.md | Canonical epistemic states and setters. |
| fail-closed-contract.md | Per-stage failure semantics. |
| local-discovery-interface.md | Frozen discovery runtime adapter contract. |
| knowledge-layer-interface.md | How knowledge artifacts are consumed. |
| measurement-v3-mapping.md | SUT output to Measurement V3 field map. |
| corpus-loader-design.md | Gold-stripping loader contract. |
| execution-harness-design.md | Runner: execute once, freeze, never score inline. |
| security-architecture.md | SSRF, injection, secrets, trust boundaries. |
| adr/ | Six architecture decision records. |
| dependency-graph.md | Implementation order. |
| implementation-phases.md | Three phases with gates. |
| test-strategy.md | Unit / component / integration / E2E. |
| implementation-plan.md | Exact files, TDD order, test commands, gates. |
| next-task-phase1.md | Copy-paste-ready Phase 1 task. |
| final-report.md | Terminal report. |
