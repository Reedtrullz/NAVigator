# Repair Dependency Graph (Post-Wave-1)

Read-only planning artifact. No candidate is implemented in this task.

## Nodes

- RC-08 retrieval scoping (PW1-R4): unblocks clean inputs for routes and evidence.
- RC-10 evidence attachment (PW1-R5 sub 1, PW1-R6): standalone-safe; does not depend on RC-08.
- RC-11 safety category vocabulary (PW1-R3): standalone-safe; no dependency on retrieval.
- RC-07 route-target selection (PW1-R1): depends on RC-08 (targets must come from scoped retrieval).
- RC-09 premature-absence guard (PW1-R2): deferred; re-derive after RC-08 + RC-10 + RC-07.
- RC-12 uncertainty qualification (PW1-R7): deferred; re-evaluate after RC-07/RC-08.

## Edges

```
RC-08 --> RC-07 --> RC-09 (re-assessment) --> RC-12 (re-assessment)
RC-10 (independent)
RC-11 (independent)
```

## Rationale

1. RC-08 is upstream of nearly everything observable: it feeds routes (PW1-R1), the 15 NO_PROVENANCE_ENTRIES evidence rows, and the forbidden-claim residual. Doing RC-07 before RC-08 would emit targets mined from contaminated fragments and re-create B_WRONG_ROUTE_TARGET by construction.
2. RC-10 and RC-11 are isolated, deterministic, low/medium-risk and can proceed in any order or in parallel with RC-08.
3. RC-09 and RC-12 are deliberately deferred: their residual criteria are largely downstream shadows of route/retrieval emptiness (premature absence when nothing is emitted; unqualifiable route when no route is named). Repairing them first risks tuning shadows.

## Wave-2 recommendation shape

Owner decision requested for one bounded Wave 2 in the order: RC-08 + RC-10 + RC-11 (independent, parallelizable), then RC-07, then re-measure before touching RC-09/RC-12. No new blind set; Wave-1-style frozen measurement with deltas.
