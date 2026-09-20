# ADR-006: LLM Authority Boundary

Status: ACCEPTED (2026-09-14)

## Context

LLMs may help with language work, but several decision classes must never
rest on model output alone.

## Decision

An LLM may (in later phases): language understanding, decomposition
proposals, synthesis, answer drafting, semantic mapping. An LLM may never be
the sole authority for: emergency escalation (deterministic triage S2 must
already catch corpus safety cases), deterministic eligibility (rules
registry), source existence (discovery evidence), provenance (mechanical
records), verified contact/access (discovery route states), hard legal
deadlines (rules registry).

Phases 1-3 of the implementation plan contain no LLM stage; the pipeline is
deterministic end to end. If an LLM stage is introduced later: its output is
a proposal validated against the deterministic layer; on any conflict the
deterministic result wins; model/config/prompt-version register in the run
manifest; external content enters prompts as data-only quoted spans.

## Consequences

- Safety-critical correctness does not depend on model stability.
- The product can adopt LLM assistance incrementally without re-architecting.
- Determinism of Phases 1-3 makes prediction freeze byte-reproducible.
