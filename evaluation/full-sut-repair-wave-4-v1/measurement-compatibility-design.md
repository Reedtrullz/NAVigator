# Measurement compatibility design: V3.1 route object adapter

## Scope

New module measurement_route_adapter.py in this lineage directory. It is a
pure observation layer:

- consumes answer["evidence"]["structured_routes"] when present and
  non-empty (mode STRUCTURED_V2_2);
- falls back to answer["routes"] labels only through the explicitly
  separated observe_routes_legacy function (mode LEGACY_LABELS_ONLY);
- never mutates the answer, never scores, never compares against gold.

## What it exposes per route

route_id, identity (service_identity), display_label, target
(target_population), access_model, conditions (dims), track_domain,
route_state, evidence_refs, provenance_refs, and a fail-closed evaluable
flag (identity present and route_state not UNVERIFIED).

## What it does NOT do

- No acceptable-route gold change, no alias table change, no threshold
  change.
- No pass/fail logic: comparison remains the frozen scorer job.
- No labels-only shortcut when structured fields are present.
- No case IDs or burned-corpus strings.

## Version and freeze

Historical Measurement V3 (evaluation/measurement-v3-combined-freeze/) is
untouched; its combined_measurement_v3.py SHA is the old-source pin and the
adapter module SHA is the new-source pin in
measurement-revision-manifest.json. No measurement changes after freeze.
