# Test Strategy

Pyramid, repo-native. Test files live beside their modules
(runtime/sut/test_*.py; evaluation/full-sut-implementation/sut_runner/test_*.py)
in the repo's existing unittest style (runtime/discovery/tests.py pattern).
No new test framework.

## Unit

| Target | Tests |
|---|---|
| schemas.py | valid sut-input/output round-trips; rejection of missing/mistyped scorer fields; epistemic enum enforcement; failure-record shape. |
| context.py | DecisionContext construction; stage-state transitions; default states. |
| safety.py | rule matching per signal; ACUTE suppression flag; rule-file corruption -> FC-01 terminal. |
| decompose.py | conjunction split; single-domain fallback; safety cap propagation. |
| routes.py | rules-registry eligibility arithmetic (age gates, 65-day rule); referral requirement lookup; uncertainty entry on unknown eligibility. |
| aggregate.py | evidence map merge; dedupe; conflict marking; provenance id integrity. |
| epistemic (aggregate.py) | precedence collapse; S6 downgrade-only; UNVERIFIED + presented_as_complete=true rejection. |
| loader.py | gold strip; GoldLeakError on planted gold keys; SHA registry verification; count verification. |

## Component

| Target | Tests |
|---|---|
| discovery_adapter.py | frozen-schema passthrough; route_state -> epistemic mapping; four failure simulations (missing municipality, provider timeout, SSRF reject, malformed result). |
| knowledge.py | index build from manifest; verbatim span extraction; authority/freshness classification; gap-register -> uncertainty path. |
| answer.py | block ordering (safety first); presented_as_complete logic; verbatim span quoting (answer contains span). |
| measurement.py | raw-answer projection contains every scorer-required field; capabilities wiring per corpus family. |

## Integration

| Target | Tests |
|---|---|
| pipeline (multi-track) | synthetic mental-health + housing + finance input -> three tracks, priority order, aggregated output. |
| pipeline (fail-closed) | discovery failure -> DISCOVERY_INCOMPLETE, UNVERIFIED, uncertainty present, no negative existence claim. |
| pipeline (source unavailable) | artifact missing -> NO_KNOWLEDGE_EVIDENCE -> uncertainty, claim not made. |
| pipeline (safety priority) | acute utterance -> suppressed_routing, emergency route only, other tracks suppressed. |
| runner end-to-end | full 120-case replay run freezes predictions + manifest; no scorer import in runner process; gold absent from all prediction files. |

## E2E (Phase 3 and beyond)

| Target | Tests |
|---|---|
| burned dev regression | scorer consumes frozen projections for all 120 cases without normalize errors; results recorded; NO inline scoring ever. |
| determinism | byte-identical rerun of the same frozen run (same corpus + component SHAs) in replay mode. |
| security suite | the four security tests from security-architecture.md. |

## Product dev fixtures (spec 35)

A small burned-only development set, created in Phase 2, stored under
evaluation/full-sut-implementation/fixtures/: 10 synthetic multi-track cases,
6 fail-closed cases, 6 safety-priority cases. Distinct from dev-corpus-v1;
never reused for fresh holdout; gold-free by construction (expected outcomes
are structural, not label-based).

## Test commands

    python3 -m unittest discover -s runtime/sut -p 'test_*.py'
    python3 -m unittest discover -s evaluation/full-sut-implementation/sut_runner -p 'test_*.py'
    python3 -m sut_runner.run --corpus evaluation/dev-corpus-v1/cases/routing_cases.json --out ... --mode replay
