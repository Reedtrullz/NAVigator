# Fail-Closed Contract

Every pipeline stage S1-S11 maps its outcome to exactly one of:

| State | Meaning | Pipeline effect |
|---|---|---|
| SUCCESS | Completed fully. | Downstream proceeds normally. |
| PARTIAL | Completed with degraded completeness, no error. | Downstream proceeds; degraded slots marked. |
| RECOVERABLE | Stage failed but pipeline can continue honestly. | Downstream proceeds with UNVERIFIED/absent inputs; failure recorded. |
| TERMINAL | Pipeline cannot continue honestly. | execution_status=EXECUTION_FAILED, presented_as_complete=false, no further stages emit claims. |

## Per-stage table

| Stage | RECOVERABLE case | TERMINAL case | Fail-closed output rule |
|---|---|---|---|
| S1 input normalization | none (validated input) | malformed input schema | EXECUTION_FAILED, empty claims, no routes. |
| S2 safety triage | none | rule file missing/invalid (FC-01) | TERMINAL by design: an unverifiable safety layer must not answer. |
| S3 decomposition | falls back to single track | none | Track count >= 1 always. |
| S4 knowledge retrieval | artifact missing/unreadable -> NO_KNOWLEDGE_EVIDENCE per track | none | Track proceeds; no legal claims without artifact evidence. |
| S5 local discovery | DISCOVERY_INCOMPLETE / provider failure -> UNVERIFIED locality | none | Search failure NEVER becomes negative existence (FC-03). |
| S6 route reasoning | no candidate route -> no_route_asserted=true per track | rules registry invalid (FC-02) | No fabricated routes; eligibility unknown -> uncertainty entry. |
| S7 evidence aggregation | none | none | Pass-through cannot fail. |
| S8 epistemic assignment | none | none | Defaults to UNVERIFIED on unresolved input. |
| S9 answer planning | minimal honest answer on empty inputs | none | Degraded block list always renderable. |
| S10 answer rendering | template missing -> plain span listing | none | No invented text; quotes verbatim. |
| S11 output emission | none | own-output schema violation (bug) | Raw context dumped to harness error store; EXECUTION_FAILED. |

## Named invariants

FC-01: Safety rule file integrity is a hard precondition. Missing, corrupt,
or unparseable safety triage data => TERMINAL. The SUT never answers with an
unverified safety layer.

FC-02: The deterministic rules registry is a hard precondition for
deterministic eligibility claims. Registry invalid => eligibility answers
downgrade to uncertainty, never to guessed eligibility.

FC-03: search failed != service does not exist. Discovery/provider failure
yields UNVERIFIED + failure record; the answer must not claim the service is
absent, and forbidden negative-existence claims are structurally impossible
because no source supports them.

FC-04: source unavailable != negative evidence. Missing artifacts/pages leave
claims unmade, not inverted.

FC-05: presented_as_complete=false whenever any RECOVERABLE or TERMINAL
failure affects the answer. A degraded answer is labeled degraded.

## Execution status mapping

    TERMINAL in any stage               -> EXECUTION_FAILED
    S5 RECOVERABLE (discovery failed)   -> DISCOVERY_INCOMPLETE
    otherwise                           -> SUCCESS

The scorer's critical rule on EXECUTION_FAILED + presented_as_complete=true
can never fire because FC-05 forces presented_as_complete=false on any
execution failure.
