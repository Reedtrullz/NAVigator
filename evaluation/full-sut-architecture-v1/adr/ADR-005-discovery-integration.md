# ADR-005: Local Discovery Integration

Status: ACCEPTED (2026-09-14)

## Context

The repo has frozen, validated discovery lineages (runtime/discovery V1;
runtime/discovery_v2 V2.4/V2.5). The SUT needs local-service evidence.

## Decision

The SUT calls discovery through one adapter (local-discovery-interface.md)
pinned to one frozen target (V1 core, or a specific V2.x candidate recorded
in adapter config). Discovery logic is never copied or reimplemented. The
adapter translates DiscoveryOutcome (frozen schema) into pipeline inputs
(route_state -> epistemic state per epistemic-state-contract.md) and wraps
failures without swallowing them.

## Consequences

- Discovery improvements stay in the frozen lineage; the adapter is the only
  product-side surface.
- Replay mode is the harness default; live discovery requires explicit task
  authorization and is recorded per run.
