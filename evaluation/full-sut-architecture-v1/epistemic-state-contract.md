# Epistemic State Contract

Canonical states are the project's existing doctrine (frozen discovery
runtime + measurement lanes). No new states are introduced.

## States

| State | Meaning | Route-level | Top-level |
|---|---|---|---|
| FULLY_VERIFIED | Service, access condition, and contact route verified from an authoritative source in this execution. | Allowed | Allowed |
| ACCESS_PARTIAL | Service exists and partially verified access (e.g. existence + contact, but age gate or referral requirement unresolved). | Allowed | Allowed |
| EXISTENCE_ONLY | Source confirms the service type exists in this municipality, but access/contact is unverified. | Allowed | Allowed |
| UNVERIFIED | No authoritative verification; claim may exist only as uncertainty. | Allowed | Allowed |

DISCOVERY_INCOMPLETE is NOT an epistemic state; it is an execution_status
value (data/local-discovery-runtime-result-v1.schema.json) and maps to
top-level epistemic_state UNVERIFIED with a failure record.

## Precedence (S8 collapse rule)

Top-level state = min over tracks of per-track state, ordered
FULLY_VERIFIED > ACCESS_PARTIAL > EXISTENCE_ONLY > UNVERIFIED.
One UNVERIFIED track holds the top level at UNVERIFIED; this is honest and
non-negotiable.

## Who sets each state

| Stage | May set |
|---|---|
| S4 knowledge retrieval | EXISTENCE_ONLY at most (artifact confirms service type); never FULLY_VERIFIED (artifacts age). |
| S5 local discovery | Any state, derived mechanically from route_state: ROUTE_FULLY_VERIFIED -> FULLY_VERIFIED; ROUTE_ACCESS_PARTIAL -> ACCESS_PARTIAL; ROUTE_EXISTENCE_ONLY -> EXISTENCE_ONLY; ROUTE_UNVERIFIED -> UNVERIFIED. |
| S6 route reasoning | Downgrades only (e.g. age gate unresolved downgrades FULLY_VERIFIED to ACCESS_PARTIAL); may never upgrade a discovery-derived state. |
| S8 epistemic assignment | Collapse per precedence; sets defaults. |

## Invariants

1. No stage may upgrade beyond what its inputs mechanically justify.
2. FULLY_VERIFIED requires a CURRENT-freshness, municipal-or-higher authority
   provenance record with a verbatim span naming the access condition.
3. UNVERIFIED at top level with presented_as_complete=true is a schema
   violation: uncertainty_expressed must be non-empty when UNVERIFIED.
4. Failure states never change epistemic state by themselves; they constrain
   what could be verified.
