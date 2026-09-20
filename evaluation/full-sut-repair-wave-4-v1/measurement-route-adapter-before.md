# Measurement route adapter: before state

## How frozen Measurement V3 consumes routes today

The frozen scorer (evaluation/dev-corpus-scorer-v1/scorer.py) reads only
answer["routes"] (display labels) in _score_routes. It normalizes label
strings and applies the frozen alias table and stub equivalence. It cannot
see the structured route object that Wave 4 now serializes into
answer["evidence"]["structured_routes"]:

- route identity (service_identity) and display label
- target population and access model
- per-route conditions (dims), track domain, route state
- joined evidence_refs and provenance_refs

## Why that loses the join

Two different services with similar label text collapse to the same
normalized label; a correct service with a wrong access path is
indistinguishable from a fully correct route at observation time.
Per-route evidence binding in the product is invisible to the
label-global scorer.

## Constraint carried into the adapter design

The scorer is frozen and must not change (TASK-LOCK scorer_edits_allowed
= false). The adapter exposes structured observations to the existing
comparison logic without altering route semantics, gold, or thresholds.
Legacy labels-only behavior stays available through an explicitly
separated fallback for historical predictions.
