# Route Dataflow Trace (before Wave 1 repair)

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1 (RC-03 evidence)
Scope: S3-S10 structured-route dataflow, traced in source, not from prose.

## Stage-by-stage

### S3 decomposition
- File: `runtime/sut/phase2/pipeline.py`, `s3_decomposition`.
- Builds `ctx["tracks"]` from `decompose(user_query)`; each track has
  `track_id`, `domain`, `needs_local_discovery`. Tracks carry no route data.

### S4 knowledge retrieval
- File: `runtime/sut/phase2/knowledge.py`, `retrieve`; wired in
  `pipeline.py:s4_knowledge_retrieval`.
- Returns up to 5 records per track. Each record carries
  `claim` (verbatim span), `evidence_id` (E-Rnnn / E-Dnnn),
  `source_reference` (url/path), `authority`, `domain`.
- Stored in `ctx["_s4_records"]`. These are the only route-bearing
  signals for national (no-municipality) cases.

### S5 local discovery
- File: `runtime/sut/phase2/discovery_adapter.py`, `run_discovery_step`;
  wired in `pipeline.py:s5_local_discovery`.
- Gate: `needs_local_discovery AND municipality`. Corpus fact: all 120
  dev cases have no `location_context` (checked programmatically against
  the three aggregate case files), so every step returns
  `state=NOT_APPLICABLE` and `discovery_invoked=0` in frozen diagnostics.
- This part is contract-consistent (FC-03 doctrine: no municipality =>
  no local discovery => never a negative existence claim). It is not an
  adapter or wiring defect.

### S6 route reasoning
- File: `runtime/sut/phase2/routes.py`, `build_route_candidates`;
  wired in `pipeline.py:s6_route_reasoning`.
- Routes are built ONLY from `discovery.services`, and only when
  `discovery["state"] == "COMPLETED"`. With every step NOT_APPLICABLE,
  `_s6_routes == []` for all 120 cases.
- Loss point 1: S4 knowledge records never become structured
  route candidates, even though each record already carries
  `claim`, `evidence_id`, and `source_reference`.

### S7 evidence aggregation
- File: `runtime/sut/phase2/aggregate.py`, `build_claims`.
- Claims are built from `_s6_routes` (per-dimension) and `_s4_records`
  (knowledge_fact, state=VERIFIED). Knowledge claims exist, but they are
  not routes and do not feed route planning.

### S8 epistemic assignment
- File: `aggregate.py:derive_track_state`, used by
  `pipeline.py:s8_epistemic_assignment`.
- Knowledge-only tracks collapse to `EXISTENCE_ONLY` (frozen doctrine:
  S4 alone justifies existence only). Top-level state is the min over
  tracks. So the epistemic layer already "knows" national routes exist
  at EXISTENCE_ONLY strength; the route layer just has no objects.

### S9 answer planning
- File: `runtime/sut/phase3/planner.py`, `plan`.
`_evaluable_routes` filters `_s6_routes` to
FULLY_VERIFIED/ACCESS_PARTIAL/EXISTENCE_ONLY. Empty `_s6_routes` =>
no PRIMARY_ROUTE/SECONDARY_ROUTE blocks => `no_route_asserted=True`.
- Loss point 2: the plan consumes only discovery-derived route
  objects; EXISTENCE_ONLY knowledge-level routes are invisible here.

### S10 rendering
- File: `runtime/sut/phase3/render.py`.
`_route_line` renders strictly from plan blocks + `_s6_routes`.
INFO blocks render verbatim knowledge claims ("Nasjonal informasjon: ..."),
which is where concrete route prose appears in frozen answers.
- Loss point 3 (observational): route prose lives in INFO blocks
  while `routes[]` stays empty; downstream measurement sees
  presented routes with `no_route_asserted=true` (88 PREMATURE_ABSENCE
  in failure analysis).

## Conclusion

The defect is architectural, single-point: structured route objects are
created only from local discovery. National knowledge records that name
concrete services never reach the structured route layer, although they
carry the exact evidence/provenance fields the route schema needs.
Repair (RC-03) must build structured national route candidates from S4
records upstream of S9, reusing `EXISTENCE_ONLY` semantics and the
records' evidence_id / source_reference linkage, without inventing
access or contact verification.
