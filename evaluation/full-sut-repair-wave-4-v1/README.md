# NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-4-V1

Terminal status: `FULL_SUT_REPAIR_WAVE_4_READY_FOR_REMEASUREMENT`.

Bounded product + measurement-compatibility repair lineage after the Wave 3 remeasure. Two scoped changes, one frozen product candidate:

1. **Phase A product**: generic route-target rescue from heading context (fail-closed), shared service-identity gate rejecting fragment labels and unresolved acronyms, per-route evidence binding to own source URL, and additive `evidence.structured_routes` serialization in finalize (no schema file mutated).
2. **Phase B measurement compatibility**: new pure observation adapter `measurement_route_adapter.py` (Measurement V3.1) exposing structured route objects; legacy labels-only path preserved verbatim; route semantic standard, gold, and scorer unchanged.

## Verification evidence

- Full SUT suite: 261/261; evaluator-import isolation PASS; product imports evaluation = 0.
- Structural 120-case replay: 120 executions schema-valid; 125/125 routes with structured objects; all binding-missing counts 0; 0 fragment/junk labels; 0 no-route inconsistencies; 0 rendering fidelity violations; determinism 25/25 pairs.
- Measurement compatibility tests: 13/13. Cross-boundary contract tests: 8/8.
- Real-replay adapter mode counts: 62 STRUCTURED_V2_2 / 58 LEGACY_LABELS_ONLY.
- Historical predictions, measurements, gold, schemas: unchanged (verified pins in input-integrity.json).

## Key SHAs

- Product candidate manifest: `4f55e6fb6c95fc7a3f136e0cc6bdae8cec2b1a07e1c082388f9ac6f7bf27d4e5`
- Measurement revision manifest: `db888c77ca7d319bef0b9754ac3fdb27f52de9b5af49fd86ad46f036f495d065`
- New measurement source (adapter): `a7ef277bc0eb8d1c7627277178dcbc26b33e5ccc39ddfc675ec184231e3db1e3`
- Old measurement source pin: `ce7277aa365d4143563cfaa09dfd52712a89a0abd8515f075658b1d683964a29`

See final-report.md for the full 58-item report and remaining-findings.json for explicit non-goals and ceilings. Hard stop: remeasurement is a separate owner-authorized task.
