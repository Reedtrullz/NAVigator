# ADR-003: Fail-Closed State Propagation

Status: ACCEPTED (2026-09-14)

## Context

Stages fail differently; the pipeline needs one honest vocabulary so a failed
stage never silently becomes a confident answer.

## Decision

Per-stage states SUCCESS / PARTIAL / RECOVERABLE / TERMINAL with the mapping
and invariants in fail-closed-contract.md (FC-01 through FC-05). Terminal
failures force EXECUTION_FAILED + presented_as_complete=false. Discovery
failure maps to DISCOVERY_INCOMPLETE, and search failure never yields a
negative existence claim.

## Consequences

- presented_as_complete is an honest completeness signal the scorer's
  critical rules can rely on.
- Safety triage data corruption stops the SUT entirely rather than answering
  with an unverified safety layer.
