# Phase 3 Design Lock

Task: NAV-EXPLORE-FULL-SUT-IMPLEMENTATION-PHASE-3

## Scope

Phase 3 implements S9 (answer planning), S10 (deterministic rendering),
and S11 (final validation / fail-closed output) on top of the frozen
Phase 2 DecisionContext stages S1-S8. No Phase 1/2 or Measurement V3
files are modified. No product LLM calls exist at any stage.

## Stage contracts

### S9 Answer planner (runtime/sut/phase3/planner.py)

Input: DecisionContext with S1-S8 structured state. Output: AnswerPlan
with blocks in frozen order:

1. SAFETY_INSTRUCTION (if safety lane active)
2. FAILURE_NOTICE for each terminal failure
3. INFO per national knowledge record
4. FAILURE_NOTICE per source conflict
5. PRIMARY_ROUTE (first evaluable) then SECONDARY_ROUTE
6. UNCERTAINTY
7. PROVENANCE_LIST

Route ordering is deterministic tuple sort: domain priority ->
epistemic strength -> scenario relevance -> access verification ->
service-name length -> input order. No weighted scores.

Evaluable states: FULLY_VERIFIED, ACCESS_PARTIAL, EXISTENCE_ONLY.
UNVERIFIED routes are never emitted as route blocks.

presented_as_complete requires: no terminal failure, no discovery
incompleteness, no S3 skip, at least one discovery step, and every
track in an evaluable state.

### S10 Renderer (runtime/sut/phase3/render.py)

Pure template rendering over the AnswerPlan. Dynamic strings are
ASCII-transliterated (ae/oe/aa) through one shared function so claim
and route substrings stay exact. Sections joined with blank lines.
Same input state always produces byte-identical output.

### S11 Finalizer (runtime/sut/phase3/finalize.py)

Consistency gates before schema validation:

- answer-plan claims are a subset of structured claims (knowledge_fact
  dimension only)
- every rendered route label is a substring of its structured route
- span refs resolve to real route IDs / known uncertainty tokens
- FC-03 negative-existence guard: discovery incomplete or no-route
  output must never contain a negative-existence phrase

Any gate failure or schema failure produces a fail-closed
EXECUTION_FAILED output via the Phase 2 helper.

## Known coverage boundaries (documented honestly)

FULLY_VERIFIED and _s7_conflicts are unreachable through the natural
replay corpus (no strong_access services in burned discovery data;
claim subjects never collide). Both are covered at component level
with synthetic ctx fixtures. Dev conflict fixtures are labeled
synthetic-only in dev-fixtures.json.

Phase 3 output claims is deliberately scoped to knowledge_fact
dimension strings. Enum-typed dimension claims from Phase 2 are
internal state, not user-facing statements, and are not copied into
the answer surface.

## Determinism

S9-S11 are pure functions of ctx. No timestamps, no random, no LLM.
The loader fixes executed_at per run so structural predictions are
byte-reproducible.
