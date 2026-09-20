# Final report - NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1

1. Task ID: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1.
2. Starting SUT SHA: Phase 3 manifest 485ecbe5d6957c4c8a34e37ac17986e1fe7a827aa6b7e819cb011924fcabfdce; failure-analysis deliverable hash c61992616dfd8ec7adc54851edc43c9a31fe4cd750a1f1c2d3ea5574569329e0.
3. Starting Phase 3 manifest: 485ecbe5d6957c4c8a34e37ac17986e1fe7a827aa6b7e819cb011924fcabfdce (verified in input-integrity.json).
4. Failure-analysis manifest: evaluation/full-sut-burned-baseline-failure-analysis-v1/ deliverable hash c61992616dfd8ec7adc54851edc43c9a31fe4cd750a1f1c2d3ea5574569329e0.
5. Gate 0 result: GATE0_PASS (imports resolve to runtime/, 0 control-character hits, 134 tests collected pre-repair).
6. RC-01 proven root cause: strict post-normalization input schema rejected legitimate caller profile shapes (null age, nested/scalar context, household_children) while the loader passed them faithfully; classified class A (supported inputs not accepted), verified in rc01-root-cause.md.
7. RC-01 source changes: normalize_input() in runtime/sut/context.py (v1: null age, nested context merge, household_children; v2: scalar profile.context wrapped to context.situational_context, idempotent, fail-closed for unsupported shapes) plus nullable age / optional household_children in sut-input.schema.json.
8. RC-01 tests: 28 in scope (17 in test_input_normalization.py incl. end-to-end scalar-context acceptance with a generic fixture, 11 in test_context.py); full suite 170 passed, 0 failed.
9. Known input failures remaining: 0 (v2 official replay: 0 input hard failures).
10. RC-02 proven root cause: class_collapse table in data/safety-triage-rules-v2.json mapped 8 of 12 classified classes to ACUTE_RISK_NOW and safety.py collapsed all classes to that priority, producing blanket emergency triage.
11. RC-02 source changes: collapse table reduced in the frozen-rules file; safety.py carries the classified 12-class name to emission; sut-output.schema.json accepts the 12-class vocabulary plus URGENT_NOT_ACUTE / NOT_ACUTE bookkeeping priorities; unknown states still coerce fail-closed to ACUTE_RISK_NOW.
12. RC-02 deterministic authority preserved: yes - frozen-rules deterministic triage, same signal matching and negation guard, no LLM or new model authority.
13. Acute safety invariant result: PASS (RC-02 test matrix; explicit acute invariants hold after repair).
14. Triage distribution after repair: ACUTE_RISK_NOW 16, URGENT_NOT_ACUTE 3, NOT_ACUTE 101; 12 distinct safety classes represented (safety_class_distribution in structural-replay-diagnostics.json).
15. RC-03 proven root cause: route candidates were only built when discovery state was COMPLETED (discovery never invoked on dev inputs) and finalize route-label consistency compared non-transliterated labels against the ASCII answer; verified in rc03-root-cause.md.
16. Discovery invocation root cause: structural, not a defect - no dev case carries location_context.municipality, so run_discovery_step() returns NOT_APPLICABLE before run_discovery(); the 16 SUCCESS / 104 RECOVERABLE local_discovery stage states are stage-bookkeeping in _stage_state(), not discovery executions.
17. RC-03 source changes: build_national_route_candidates() in routes.py (deterministic national candidates with P-K provenance refs), pipeline.py wiring of national candidates into route reasoning, finalize.py ascii_text-consistent route label check.
18. Structured route count: 30 route entries across 23 cases, 13 distinct labels.
19. Route provenance result: 23/23 route-bearing cases have provenance; 0 cases with routes but no provenance; all P-K linkage targets resolve.
20. Rendered-route/structured-route consistency: RENDERED_ROUTE_WITHOUT_STRUCTURED_ROUTE = 0 (only route-like rendered lines are the four frozen acute-safety instruction lines, which are emergency instructions, not discovery routes).
21. no_route_asserted consistency: 97 true / 23 false, 0 mismatches against routes[].
22. Full test-suite result: 170 passed, 0 failed (regression-results.json).
23. Phase 1 regression: PASS (input normalization/context within the full suite).
24. Phase 2 regression: PASS (safety, routes, aggregate, pipeline within the full suite).
25. Phase 3 regression: PASS (planner, render, finalize within the full suite).
26. Evaluator imports into product: 0 (runtime/sut/test_separation.py suite holds).
27. Candidate source SHA: runtime/sut/context.py = 078bcf3fb566e3f02a05a23e69835d88e863b1ef4a3c69a6df240537835fa0a3 (only changed SUT component vs v1; all 24 component SHAs in hashes.txt).
28. Candidate manifest SHA: e19dd2d6d5329ef3fe85e1719fdc879717563a2e18dc561812b5e6d2a7035f27 (repaired-sut-manifest.json).
29. Full 120 replay attempted: yes - v1 (failed RC-01 gate) and v2 (official); both preserved under runs/.
30. Replay crashes: 0 (v2 official).
31. Replay schema validity: 120/120 outputs schema-valid.
32. Replay input hard failures: 0.
33. Discovery invoked count: 0 (structural: no location_context in the burned corpus; matches historical behavior).
34. routes-empty count: 97 cases.
35. routes-nonempty count: 23 cases (30 route entries).
36. Unprovenanced route count: 0.
37. Determinism result: PASS - independent rerun, 120/120 prediction files byte-identical by SHA-256.
38. Historical predictions mutated: NO (Phase 3 predictions untouched; v1/v2 replays in new lineage dirs).
39. Gold used by product: NO (loader strips gold; strict separation tests pass).
40. Measurement V3 scoring run: NO.
41. RC-04 implemented: NO (remaining-rc04-06-findings.json).
42. RC-05 implemented: NO.
43. RC-06 implemented: NO.
44. Overfit findings: none - no case IDs, corpus literals, or expected verdicts in runtime logic; the v2 fix is a generic scalar-context normalization rule verified idempotent.
45. Remaining known issues: RC-04/05/06 open (uncertainty on failure path, evidence completeness assembly, renderer noise); route labels are knowledge-record claims whose quality is a measurement question, not a structural one; local discovery behavior remains unexercised by this corpus.
46. Frozen candidate attempts: 2 (maximum 2 allowed; v1 superseded, v2 frozen).
47. STATUS: FULL_SUT_REPAIR_WAVE_1_READY_FOR_REMEASUREMENT.
48. Recommended next bounded task: owner-authorized Measurement V3 re-measurement of the frozen v2 candidate only; RC-04/05/06 remain queued behind that result. No SUT changes, no fresh holdout, no deploy in that task.
