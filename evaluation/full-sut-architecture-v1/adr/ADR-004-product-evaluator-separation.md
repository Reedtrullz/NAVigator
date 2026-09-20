# ADR-004: Product / Evaluator Separation

Status: ACCEPTED (2026-09-14)

## Context

Scorer, measurement lanes, and corpus live in the same repo as product
components. The gap report warns not to confuse them.

## Decision

Dependency direction is one-way (product-vs-measurement-boundary.md): the
product pipeline imports runtime/discovery and reads knowledge artifacts; it
never imports evaluation/. The runner and loader are evaluator-side tools
that execute the product. Gold exists only in evaluator hands: the loader
strips it, the scorer reads it, the SUT never sees it.
GOLD_VISIBLE_TO_SUT = 0. M2-workflow classification is evaluator-side
metadata; the SUT never emits or consumes it.

## Consequences

- No measurement component becomes a runtime dependency.
- Product human review is out of scope (not a requirement today); measurement
  human-review lanes stay evaluator-only.
- A future product operator queue would be a new owner decision, not a
  reuse of measurement lanes.
