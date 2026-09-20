# RC-03 Root Cause: structured routes lost before answer planning

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1
Companion evidence: route-dataflow-before.md (stage-by-stage trace with source locations).

## Symptom

All 120 frozen Phase 3 predictions emit `routes = []` and
`no_route_asserted = true`, while user-facing prose recommends concrete
services in INFO blocks. Failure analysis: 108/108 route criteria FAIL,
88 PREMATURE_ABSENCE, `discovery_invoked = 0` everywhere.

## Diagnosis (source-verified, three linked mechanisms)

1. **Route objects come only from local discovery.**
   `s6_route_reasoning` (`runtime/sut/phase2/pipeline.py`) builds
   candidates solely from `_s5_steps`; `build_route_candidates`
   (`routes.py`) returns `[]` unless `discovery["state"] == "COMPLETED"`.
   S4 knowledge records never become route candidates, although each
   already carries `claim`, `evidence_id`, and `source_reference`.
2. **The planner consumes only discovery routes.**
   `phase3/planner.py:_evaluable_routes` filters `_s6_routes`; empty
   input means no PRIMARY_ROUTE/SECONDARY_ROUTE blocks and
   `no_route_asserted = True`. EXISTENCE_ONLY knowledge-level routes are
   invisible to planning even though S8 already assigns
   `EXISTENCE_ONLY` to knowledge-only tracks.
3. **Route prose lives in INFO blocks only.**
   `render.py` prints verbatim knowledge claims ("Nasjonal informasjon:
   ..."), so the user sees concrete routes while `routes[]` stays empty.
   Downstream measurement sees presented routes with
   `no_route_asserted = true`.

### Discovery invocation

`discovery_invoked = 0` is contract-consistent, not an adapter defect:
the S5 gate is `needs_local_discovery AND municipality`
(`pipeline.py:s5_local_discovery`); every dev input lacks
`location_context.municipality`, so every step is NOT_APPLICABLE
(FC-03: never a negative existence claim from absent discovery).
National routes are valid without discovery; the defect is that none
exist structurally.

## Additional finalize defect (same repair scope)

`finalize.py:_route_labels_substring_of_answer` checks the raw route
label against the rendered answer, but `render.py:ascii_text()`
transliterates ae/oe/aa. A national route whose service name contains
Norwegian characters would fail the consistency gate and fail-closed the
whole output. The check must compare `ascii_text(label)` against the
answer.

## Repair design (deterministic, no schema change)

1. New builder `build_national_route_candidates(records, discovery_service_count)`
   in `routes.py`, appended to `_s6_routes` after discovery routes in
   `s6_route_reasoning` (phase3 imports the module, so one edit serves
   both pipelines):
   - Inputs: S4 doc records only (`source_type == "PROJECT_RESEARCH"`,
     `gap_state is None`, `historical_research is False` — i.e. current,
     non-gap, non-rule records). FROZEN_RULE and GAP records stay
     uncertainty-only per existing doctrine.
   - Conservative grounded service-name extraction from the verbatim
     claim: quoted segments and bold (`**...**`) markers only; a record
     with neither yields no route. No corpus strings, no case IDs, no
     service lexicon.
   - Deduplicate by (track_domain, service_type), keep first.
   - Dims: `service_exists` VERIFIED and `scenario_relevant` VERIFIED
     (grounded in the verbatim claim), age/access/contact UNRESOLVED
     -> `EXISTENCE_ONLY` via the existing `_route_state`. No invented
     access or contact verification.
   - `scope = "NATIONAL"`, `evidence_refs = [rec.evidence_id]`,
     `provenance_refs = [P-K id]` computed with the same numbering rule
     as `_provenance_records` (P-K offset by prior discovery services),
     so every structured route has provenance linkage.
2. `_route_labels_substring_of_answer` compares `ascii_text(label)`.
3. Top-level `safety_priority` coercion in finalize accepts the 12-class
   vocabulary (RC-02 integration point); `_failed_output` stays
   fail-closed ACUTE_RISK_NOW.

Hard targets: RENDERED_ROUTE_WITHOUT_STRUCTURED_ROUTE = 0 and
STRUCTURED_ROUTE_WITHOUT_PROVENANCE = 0, with
routes_nonempty => no_route_asserted = false preserved by the existing
`no_route_asserted = not evaluable` emission.

