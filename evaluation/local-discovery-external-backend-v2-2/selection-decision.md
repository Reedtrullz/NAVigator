# SELECTION DECISION

No backend was selected. The credential gate (task sections 7-9) resolved
before any benchmark run:

- `BRAVE_API_CREDENTIAL = NOT_AVAILABLE`
- `TAVILY_API_CREDENTIAL = NOT_AVAILABLE`

Per task section 9, the terminal status is
`BACKEND_SELECTION_BLOCKED_BY_CREDENTIALS`. Site-direct results may be
reported but no external backend may be frozen. The selection rule and
comparison design are preserved for a future task in
`backend-selection-contract-restart.md`.

Runtime consequence: the V2 lineage remains site-direct-first with the
external fallback effectively disabled (Brave HTML adapter retained only as
the documented negative control). No runtime code was changed by this task.
