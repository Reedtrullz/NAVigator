# ADR-002: Provenance Model

Status: ACCEPTED (2026-09-14)

## Context

Claims about services, access conditions, and legal requirements must be
auditable back to sources, including through discovery link chains.

## Decision

Every claim and route carries provenance_ids pointing at provenance records
(provenance-contract.md). Records carry source_type, source_ref, verbatim
evidence_span, authority_level, freshness_class, conflicts_with, and
chain_parent_id. Discovery pages pass through the frozen runtime's
provenance graph; the SUT does not rebuild it.

## Consequences

- Absence of provenance structurally prevents claim assertion.
- Discovery failures produce ERROR_STATE provenance supporting uncertainty,
  never negative existence claims.
- Authority conflicts are recorded and resolved by frozen precedence.
