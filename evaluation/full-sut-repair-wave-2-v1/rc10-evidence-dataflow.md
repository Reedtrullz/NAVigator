# RC-10 Root Cause: Evidence Attachment Dataflow

## Root cause

The frozen Wave-1 output carried a flat evidence pool plus provenance
records, but no per-route or per-claim ownership link inside the output
itself. Three consequences, matching post-Wave-1 families PW1-R5 and PW1-R6:

1. 23/38 zero-evidence cases had provenance entries with source URLs that
   were never copied into the evidence dict (PROV_HAS_URL_NOT_ATTACHED).
2. 15/38 had no provenance entries at all, downstream of retrieval
   contamination (addressed by RC-08, expected to improve, not verified here).
3. Safety cases carried correct top-level safety_priority but never copied it
   into evidence.

## Repair design

- The frozen scorer contract requires routes to be an array of label strings
  (sut-output.schema.json). Route objects in that field would break schema
  validation, so routes stays labels-only. Per-route and per-claim evidence
  lives under the additive evidence map (additionalProperties: true):
  - evidence.route_evidence[route_id] = {evidence_ids, provenance_ids,
    source_url?}
  - evidence.claim_evidence[claim_id] = {evidence_ids, provenance_ids}
  The scorer checks only required gold fields in evidence; additive keys are
  scorer-safe.
- Shared helpers _route_evidence(ctx, route) and _claim_evidence(ctx) live
  in phase2/pipeline.py and are imported by phase3/finalize.py.
- Provenance resolution: local routes resolve source_url plus P-Dxxx via
  source_ref match; national routes use pre-resolved P-K%03d refs validated
  against emitted provenance records. Unresolved refs are dropped, never
  fabricated. National-route P-K numbering shares the _provenance_records
  counter (verified).
- evidence.safety_priority mirrors the fine triage class (shared with RC-11).

Test note: the irrelevant-source case injects a same-track record; the
pipeline's own consistency check fails closed on cross-domain injection,
which is correct behavior, not a test defect.
