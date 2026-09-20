# RC-07 Route-Selection Dataflow (before repair)

Pipeline: track -> scoped evidence -> service candidates -> route candidates
-> target selection -> access-path selection -> structured route -> planning.

## Observed behavior (probe evidence)

Query "Hvor kan vi fa hjelp til psykisk helse for vaar datter paa 19 aar?",
age 19, no municipality (discovery NOT_APPLICABLE):

- retrieval returns 2 FROZEN_RULE records and 3 research records, all three
  from POINT_IN_TIME scenario docs (71/72 lineage) or gap register;
- `build_national_route_candidates` excludes gap/historical records, so the
  national route list is empty and `no_route_asserted = true`;
- the same services ("Rask psykisk helsehjelp", "Helsestasjon for ungdom")
  exist as bold-marked rows in CURRENT docs 25/26, which never reach a
  retrieval slot because POINT_IN_TIME scenario docs out-score them lexically.

With a municipality, discovery produces correctly structured routes
("Helsestasjon For Ungdom Drammen", "Rask Psykisk Helsehjelp"), so the local
path is healthy; the defect is the national path.

## Root causes

- **R1 (empty routes)**: POINT_IN_TIME scenario snapshots crowd CURRENT
  reference docs out of the 5 retrieval slots for generic domain queries.
  Generic epistemic ordering defect: current research must outrank snapshots.
- **R2 (KB-fragment / junk routes)**: route targets are extracted from any
  quoted or bold segment of an evidence sentence. Quoted numeric/temporal
  facts (e.g. "opptil 20 ar") can become route names; a route target must be
  a service concept, not an evidence fragment.
- **R3 (missing track binding)**: national routes bind `track_domain` from
  the record's primary `domain` tag. A multi-domain doc (e.g. 31 =
  mental_health + education) retrieved under its secondary track produces a
  route bound to the primary domain; S8 then sees knowledge for a track the
  route does not belong to.

## Repair design

- Retrieval: CURRENT research fills slots before POINT_IN_TIME snapshots;
  gap reserve unchanged (max 1). Generic ordering, no benchmark tuning.
- Route targets: reject extracted names containing digits (numeric/temporal
  facts are not service concepts). Deterministic guard, documented ceiling:
  grounded extraction remains lexical; no new model authority.
- Binding: S4 stamps `track_domain` per retrieval; S8 knowledge filtering and
  national route binding use that stamp; planner INFO blocks scope by it and
  dedupe by evidence_id.
- No-route behavior unchanged: unsupported candidates keep routes absent and
  fail closed (search failure is never service absence).
