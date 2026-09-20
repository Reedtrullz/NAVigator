# ADR-001: SUT Boundary

Status: ACCEPTED (2026-09-14)

## Context

The measurement system needs a stable contract for what the product must
produce. The repo has a frozen scorer, frozen discovery runtimes, and a
120-case dev corpus, but no end-to-end pipeline that a scorer can consume.

## Decision

The SUT is a single canonical pipeline with one input schema (sut-input/v1)
and one output schema (sut-output/v1), as defined in sut-boundary.md. The SUT
receives no gold, no corpus family, no scorer metadata; it executes once per
case; it emits structured output that maps 1:1 to the scorer's raw-answer
fields plus product-level extensions (tracks, provenance, epistemic state,
failures).

## Consequences

- Measurement consumes structured fields, not prose heuristics.
- The runner, loader, and scorer stay evaluator-side; the product pipeline
  never imports evaluation/.
- Any future interface change is a schema version bump with a migration
  note; the scorer contract v1 stays frozen.
