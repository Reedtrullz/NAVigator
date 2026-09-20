# W4 Product Source Change Summary

## runtime/sut/phase2/routes.py

1. Extended `_valid_service_name` to reject sentence fragments and
   unresolved acronyms (shared gate for quoted/bold extraction).
2. Added `_SUBJECT_VERB_RE` fragment signature (closed word list) and
   wired it into `_is_sentence_fragment`.
3. Added `_valid_heading_label`, `_heading_marker_free`,
   `_heading_context_service_name` (verbatim single-match claim
   location -> nearest preceding heading, fail-closed) and
   `_bind_discovery_evidence` (per-source_url evidence partitioning
   with documented all-refs fallback).
4. `build_national_route_candidates`: heading rescue for non-table-row
   prose claims only, after quote/bold extraction fails.
5. `build_route_candidates`: evidence_refs now come from
   `_bind_discovery_evidence` instead of blanket enumeration.

## runtime/sut/phase3/finalize.py

6. Added `evidence.structured_routes` serialization of evaluable route
   objects (identity/label/track/state/access/population/scope/evidence/
   provenance/dims). `routes` remains labels-only. No schema change:
   `evidence` is `additionalProperties: true`.

## runtime/sut/phase3/test_route_binding_wave4.py

7. New: 19 W4 tests covering heading mint/rejection matrix, quoted/
   acronym gates, per-service evidence partitioning, serialization
   binding survival, labels-only parity, and no-route fail-closed.

## Pre-existing files: unmodified

All other SUT files, schemas, gold, predictions and Measurement V3
artifacts are byte-identical to the verified input pins.
