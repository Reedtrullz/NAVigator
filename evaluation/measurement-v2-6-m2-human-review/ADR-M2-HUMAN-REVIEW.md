# ADR: M2 critical-condition judgement moves to an explicit human-review lane

## Context

Single-model automation of the M2 (critical_condition) semantic judgement failed repeatedly despite a clean foundation:

- The V2.5 human decomposition contract was fully annotatable: 60/60 fixtures, all agreement gates at 1.0.
- The evidence-state was decomposed into four orthogonal intermediate observations with an 81-row deterministic derivation table; no derivation-table defects were found.
- DeepSeek-v4.1-flash, the only authorized reference model, still failed calibration: derived-final accuracy 0.500 (iteration 0) and 0.833 (iteration 1) against a >=0.95 gate, with persistent conflict under-reporting and 1 critical false negative in both iterations.
- Earlier lineages (V2.2, V2.3, V2.4, V1.6B, C1) independently showed the same failure family: ambiguous or insufficient critical_condition evidence is forced toward TRIGGERED or NOT_TRIGGERED instead of UNRESOLVED.
- Terminal status: V2_5_REFERENCE_MODEL_CANNOT_USE_DECOMPOSITION. Decision gate answer: NO_M2_MODEL_LIMIT.

## Decision

Owner decision 2026-09-13: automated semantic judges shall no longer issue authoritative M2 critical_condition verdicts in the measurement system. All semantic M2 critical-condition judgements are routed to an explicit human-review lane (HUMAN_REVIEW_REQUIRED) until a future automated evaluator independently proves the required safety and reliability gates under a future owner decision.

This is the measurement system's authoritative architecture, not a temporary workaround. It changes the measurement/evaluator system only; NAV Explore product runtime, user-facing safety routing, and emergency handling are untouched.

## Consequences

- Reduced automated coverage: M2 semantic coverage is 0% authoritative automated by design (AUTOMATED_SCORING_COVERAGE reports this explicitly).
- Increased measurement reliability: critical-condition verdicts come from a human-validated decomposition contract with mechanical derivation, not from a model that demonstrably forces ambiguous evidence binary.
- Explicit human workload: every M2 criterion in a measurement run requires one (labeled SINGLE_HUMAN_REVIEW) or two blind reviews plus adjudication when reviewers disagree. HUMAN_REVIEW_PENDING is fail-closed; missing reviews are never automatic passes.
- The remaining semantic judge lane can specialize on non-M2 dimensions (forbidden, route, uncertainty) without M2 performance in its candidate gates. This is an architecture boundary (M2 not in automated judge responsibility), not a gate lowering.
- Future model screening (e.g. a V2.7 non-M2 screen) must use the new responsibility boundary from V2.6. The 12-model V2.4 draft remains NOT_OWNER_AUTHORIZED.
- Safety reporting: critical-condition performance is reported as HUMAN_REVIEW_M2, never as model safety accuracy.

## Scope invariants

- V2.5 semantic meaning is frozen; no M2 label changes.
- Reviewer is blind to final gold and to all automated model verdicts.
- Human observes; code derives the final label via the frozen derivation table.
- No model calls are required or used inside this lane.
