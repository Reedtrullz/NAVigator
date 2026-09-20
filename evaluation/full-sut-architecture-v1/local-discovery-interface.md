# Local Discovery Interface

The SUT consumes the frozen discovery runtime as a component. Discovery logic
is NOT copied, forked, or reimplemented (ADR-005).

## Component of record

runtime/discovery/ (V1 frozen core: engine.py, classification.py, security.py,
protocol.py, orchestrator.py). The V2.4/V2.5 candidates
(runtime/discovery_v2/) are frozen evaluation lineages; if Phase 2 wiring
needs V2.4 semantics (root resolution, section-level provenance), the adapter
targets the specific frozen candidate module and records which one in its
config. One adapter, one pinned target, no silent switching.

## Adapter contract (product-side module runtime/sut/discovery_adapter.py, Phase 2)

    discover(request) -> DiscoveryOutcome

DiscoveryRequest:

| Field | Type | Notes |
|---|---|---|
| municipality | string | Required for discovery-type needs. Absent -> adapter returns NOT_APPLICABLE, never guesses. |
| age | int/null | From profile. |
| need_type | enum | MUNICIPAL_MENTAL_HEALTH, HFU, FAMILY_CENTER, GENERAL_LOCAL. |
| urgency | enum | ACUTE, URGENT, ROUTINE. ACUTE bypasses discovery entirely (safety path owns routing). |
| mode | enum | REPLAY (deterministic, harness default), LIVE (recorded per execution). |

DiscoveryOutcome:

| Field | Type | Notes |
|---|---|---|
| route_state | enum | ROUTE_FULLY_VERIFIED / ROUTE_ACCESS_PARTIAL / ROUTE_EXISTENCE_ONLY / ROUTE_UNVERIFIED (frozen schema). |
| execution_status | enum | COMPLETE / DISCOVERY_INCOMPLETE (frozen schema). |
| provenance_graph | object | Passed through from the frozen runtime; adapter does not rebuild it. |
| evidence | list | Page records with URLs + verbatim spans. |
| terminal_state | enum | ACCESS_VERIFIED / REFERRAL_VERIFIED / PUBLIC_DATA_EXHAUSTED (frozen schema). |
| error | object/null | Structured failure; adapter wraps, never swallows. |

## Mapping into the pipeline

- route_state -> per-route epistemic_state via the frozen mapping in
  epistemic-state-contract.md (S5 -> S6 inputs).
- execution_status=DISCOVERY_INCOMPLETE -> failure record stage=local_discovery
  state=RECOVERABLE; FC-03 applies.
- PUBLIC_DATA_EXHAUSTED is an honest terminal of DISCOVERY, not of existence:
  the track ends at EXISTENCE_ONLY/UNVERIFIED with an uncertainty entry, never
  a negative claim.

## Failure simulations owned by the adapter (Phase 2 tests)

1. municipality absent -> NOT_APPLICABLE, no fetch.
2. provider timeout -> ROUTE_UNVERIFIED + DISCOVERY_INCOMPLETE, failure record.
3. blocked/SSRF URL attempt -> security layer rejects (runtime/discovery/
   security.py), failure record, no content used.
4. malformed discovery result -> schema validation fails -> failure record.

The frozen runtime's own test suites remain authoritative for the runtime;
adapter tests cover only the adapter boundary.
