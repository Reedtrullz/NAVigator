# FINAL REPORT — NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-4-V1

Date: 2026-09-17. Terminal status: `FULL_SUT_REPAIR_WAVE_4_READY_FOR_REMEASUREMENT`.

1. **Task ID**: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-4-V1.
2. **Starting Wave-3 product SHA**: routes.py pre-task `29b0bd44ee5ad4e7e3bbca492f34958e3cbb570fd45e0231d7c0c7c13213d7fa` (input-integrity pin, verified match).
3. **Starting Measurement SHA**: `combined_measurement_v3.py` = `ce7277aa365d4143563cfaa09dfd52712a89a0abd8515f075658b1d683964a29` (old-source pin in measurement-revision-manifest.json).
4. **Scope-gate SHA**: TASK-LOCK `eff414fb98fb6faa7676750ce9baa1a97a15ddd166f697554002f9426b3ff262`; final-report `4746715b393407e313fa310b6fd6fa6675aea8ac650e89c3e92d33b462a8b0ec` (post-wave3-p0-binding-wave4-scope-gate-v1, both verified match).
5. **Input integrity**: PASS. All 9 pins matched (routes.py, wave3 SUT manifest, wave3 measurement freeze, wave3 combined results, judge_core_v2_13, dev corpus v1.1 repair manifest, wave3 routing predictions manifest, scope-gate TASK-LOCK and final report). Mutations: historical predictions/measurements/gold/scope-gate lineage = false.
6. **Gate 0**: PASS. Python 3.14.6; routes.py imports; 0 control characters in SUT Python; test inventory 12 phase-2 + 2 phase-3 + 10 top-level. Wave-3 route state entering W4: R0 unmatched 84, R1 label-only 9, R3 no-route-asserted 11, R5 render mismatch 4; binding B4 non-service-label 16, B5 labels-only serialization 23.
7. **Product route-target root cause**: prose claims under service headings minted no route target although the heading is the service identity (R0, 84/108). Fixed generically by a fail-closed heading-context rescue: claim must appear verbatim on exactly one line of the referenced source document; nearest preceding heading becomes candidate after identity gates; table rows excluded (W3 header-identity-gate domain).
8. **Product binding root cause**: (B4) quoted/bold extraction minted non-service labels — fixed by shared `_valid_service_name` identity gate rejecting sentence-fragment signatures and unresolved all-caps acronyms while accepting documented service acronyms (BUP, HABU, RPH, DPS, HFU, PPT). (B5) finalize dropped structured route objects and kept only display labels — fixed by per-route structured serialization.
9. **Route object before**: finalize serialized display labels only (`routes` list); identity, target, access, conditions, track, route state, and evidence refs existed only transiently in phase-2 structures and were lost before output.
10. **Route object after**: per-route structured objects serialized additively to `evidence.structured_routes` with route_id, service_identity, display_label, track_domain, route_state, access_model, self_referral, target_population, scope, evidence_refs, provenance_refs, dims. Public `routes` list remains labels-only.
11. **Stable route identity mechanism**: explicit `service_identity` distinct from `display_label`; identity survives even when display labels differ (compat test test_06).
12. **Service target representation**: `target_population` field per structured route.
13. **Display label representation**: unchanged labels-only public `routes` list; label also mirrored inside the structured object.
14. **Access representation**: `access_model` plus `self_referral` per route.
15. **Condition representation**: `dims` (conditions) per route; missing conditions remain incomplete in observations (test_04).
16. **Track binding**: `track_domain` per route; track binding missing = 0 across all 120 replay executions.
17. **Evidence binding**: discovery routes bind to evidence rows of their own source URL (`_bind_discovery_evidence`); documented fallback ceiling: records without source_url bind all refs.
18. **Serialization binding**: additive `evidence.structured_routes` map, `additionalProperties: true` in the frozen output schema; no schema file mutated.
19. **Product source changes**: runtime/sut/phase2/routes.py (extraction gates, heading rescue, evidence binding), runtime/sut/phase3/finalize.py (structured_routes serialization), runtime/sut/phase3/test_route_binding_wave4.py (new W4 tests).
20. **Product tests**: full suite 261/261 OK (`PYTHONPATH=runtime python3 -m unittest discover -s runtime/sut -p 'test_*.py'`); evaluator-import isolation PASS (sut.test_separation).
21. **Product hard gates**: RAW_KB_FRAGMENT_AS_ROUTE_TARGET = 0; NON_SERVICE_LABEL_AS_ROUTE_TARGET = 0; ROUTE_WITHOUT_TRACK_BINDING = 0; ROUTE_WITHOUT_PROVENANCE = 0; ROUTE_BINDING_LOST_DURING_SERIALIZATION = 0; SUPPORTED_ROUTE_LOST_BEFORE_OUTPUT = 0; RENDERED_ROUTE_WITHOUT_STRUCTURED_ROUTE = 0; PRODUCT_IMPORTS_EVALUATION = 0; CASE_IDS_IN_RUNTIME = false; SCHEMA_FILES_MUTATED = false; GOLD_MUTATED = false.
22. **Product candidate SHA**: content SHA of wave4-product-candidate-manifest.json = `4f55e6fb6c95fc7a3f136e0cc6bdae8cec2b1a07e1c082388f9ac6f7bf27d4e5` (an earlier 479083… value in w4-product-tests.json was a path-string hashing mistake, corrected during the session).
23. **Product candidate manifest SHA**: same value as item 22: `4f55e6fb…f27d4e5`.
24. **Product candidate attempts**: 1 of max 2 used (NAV-EXPLORE-W4-PRODUCT-CANDIDATE-1).
25. **120-case product replay**: 120 executions across routing (75), discovery_adversarial (25), safety (20); all families structurally clean.
26. **Executions successful**: 120/120.
27. **Schema validity**: 120/120.
28. **Structured route objects**: 125/125 routes carry structured objects (equal to total routes).
29. **Actionable targets**: 125 total (95 routing + 22 discovery_adversarial + 8 safety).
30. **Route/evidence joins**: evidence_join_missing = 0 across all families.
31. **Access bindings**: access_binding_missing = 0 across all families.
32. **Condition bindings**: condition_binding_missing = 0 across all families.
33. **No-route consistency**: no_route_inconsistent = 0 (no genuine no_route_asserted contradicted by present structured routes).
34. **Product determinism**: 25/25 re-executed discovery_adversarial pairs deterministic (predictions identical modulo executed_at); differing = 0.
35. **Measurement historical version preserved**: yes. Historical Measurement V3 untouched; old source pinned; adapter is a separate new module.
36. **Measurement adapter root cause**: frozen scorer could not observe structured route objects because finalize never serialized them; the measurement side also had no structured observation path. W4 adds a pure observation layer; no verdict logic moved.
37. **Measurement compatibility changes**: new `measurement_route_adapter.py` (Measurement V3.1 Route Object Adapter): STRUCTURED_V2_2 mode reads `evidence.structured_routes` fail-closed (evaluable requires identity present and route_state not UNVERIFIED); LEGACY_LABELS_ONLY via separate `observe_routes_legacy` with identical field shape and None identity/target/conditions; structured presence never falls back to labels; adapter never mutates answers, scores, or compares against gold.
38. **Route semantic standard changed**: NO (frozen standard/gold/scorer semantics unchanged; asserted in measurement-revision-manifest).
39. **Gold semantics changed**: NO.
40. **Measurement compatibility tests**: 13/13 OK (measurement_compatibility_tests.py to measurement-compatibility-tests.json), incl. wrong-route rejection, provenance-only non-evaluability, legacy preservation, structured-presence-no-fallback, no verdict tokens in observations.
41. **Wrong-route rejection preserved**: YES (test_02: wrong service target remains wrong; test_07: evidence from wrong route does not bind).
42. **Provenance-only PASS prevented**: YES (test_05: provenance-only is not evaluable; test_13: counterfactual C — evidence alone never makes a route).
43. **Measurement revision SHA**: new source (adapter) `a7ef277bc0eb8d1c7627277178dcbc26b33e5ccc39ddfc675ec184231e3db1e3`; historical old source `ce7277aa…964a29` unchanged.
44. **Measurement revision manifest SHA**: `db888c77ca7d319bef0b9754ac3fdb27f52de9b5af49fd86ad46f036f495d065`.
45. **Cross-boundary tests**: 8/8 OK (discovery to build_route_candidates to serialize (finalize field mapping) to adapter to observation): identity, access, conditions, track, evidence linkage preserved; serialized shape matches real ROUT-021 structured_routes keys; product pipeline produces structured routes; no product-to-evaluation imports (grep excludes pre-existing test_separation docstring).
46. **Product imports evaluator**: NO (0 hits).
47. **Scorer quirks fixed**: NO (out of scope; MS-01..06 remain historical).
48. **Historical predictions changed**: NO (byte-identical; input-integrity mutation flags false).
49. **Historical measurements changed**: NO.
50. **Gold changed**: NO.
51. **RC-04 implemented**: NO (deferred per spec section 35).
52. **RC-06 implemented**: NO (deferred per spec section 35).
53. **Fresh cases consumed**: 0. Fresh holdout untouched.
54. **Overfit findings**: none. No case IDs or burned-corpus strings in runtime logic; id-guard grep over runtime/sut = 0 hits; heading rescue and identity gates are generic lexical mechanisms, fail-closed; no tuning against expected verdicts (no gold used anywhere in this task).
55. **Remaining route-target issues**: R3-family (no_route_asserted where gold expects routes) semantic correctness is not measurable gold-blind; structural no-route consistency is clean, but final semantic judgment belongs to the remeasure task. Known ceilings: verbatim single-line claim requirement for the heading rescue; fail-closed on ambiguous/unreadable sources.
56. **Remaining binding issues**: 58/120 historical predictions are LEGACY_LABELS_ONLY by design (structured_routes did not exist at their freeze time; no routes minted). Evidence-binding fallback binds all refs when a service record lacks source_url. RC-04/RC-06 deferred. See remaining-findings.json.
57. **STATUS**: `FULL_SUT_REPAIR_WAVE_4_READY_FOR_REMEASUREMENT` (Phase A PASS, Phase B PASS, Phase C PASS, candidate and manifests frozen; 1/2 candidate attempts used).
58. **Recommended next task**: separate owner-authorized Measurement V3 remeasure of the 120 frozen replay predictions with the frozen V3.1 adapter (62 STRUCTURED_V2_2 + 58 LEGACY_LABELS_ONLY), followed by the deferred fresh holdout only after remeasure adjudication. No remeasure, fresh holdout, SUT change, or tuning is started in this task.
