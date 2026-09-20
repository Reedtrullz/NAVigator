# RC-07 Root Cause: Route-Target Semantic Selection

Full pre-repair trace with probe evidence lives in
route-selection-dataflow-before.md. Summary of the three generalized defects:

- **R1 (empty routes, 88/108)**: POINT_IN_TIME scenario snapshot docs
  out-scored CURRENT reference docs lexically for generic domain queries,
  crowding current service documentation out of the 5 retrieval slots. The
  national route candidate builder correctly excludes gap/historical records,
  so the route list arrived empty.
- **R2 (junk routes, 8/108)**: route targets were extracted from any quoted
  or bold segment of an evidence sentence. Quoted numeric or temporal facts
  (e.g. age limits) became route names. A route target must be a service
  concept, not an evidence fragment.
- **R3 (track binding)**: national routes bound track_domain from the
  record's primary domain tag even when the record was retrieved under a
  secondary track, so downstream knowledge filtering saw a mismatch.

## Repair implemented (generic, no benchmark references)

- Retrieval slot ordering now fills CURRENT research before POINT_IN_TIME
  snapshots (phase2/knowledge.py). Gap-reserve behavior unchanged.
- Route-target extraction rejects candidate names containing digits;
  numeric/temporal facts are not service concepts (phase2/routes.py).
  Documented ceiling: grounded extraction remains lexical; no new model
  authority was introduced.
- Track-domain binding is stamped per retrieval and used consistently by S8
  knowledge filtering, national route binding, and planner INFO scoping.
- No-route behavior unchanged: unsupported candidates keep routes absent and
  fail closed. Search failure is never treated as service absence.

Local discovery routes were already healthy pre-repair and are untouched.
