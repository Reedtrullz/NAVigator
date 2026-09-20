# Final Report - Post-Wave-3 P0 + RC04/Binding Wave-4 Scope Gate V1

Task ID: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY. Read-only diagnosis; all numbers verified from frozen artifacts on disk.

1. Task ID: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
2. Wave-3 product SHA: 6c1f7d4b4b52eeabc16a13e0c34d9cdd332a6acd532cd33ddb796660fd2be14f (repaired-sut-manifest.json, pin verified)
3. Wave-3 measurement SHA: 6385bcd98596350ac4f12fa612bacbacf92d625d81105d3cf7dbe3e2f5d05d54 (wave3-measurement-freeze-manifest.json, pin verified)
4. Input integrity: INPUT_INTEGRITY_PASS (input-integrity.json)
5. Total P0 regressions: 5
6. Real product safety regressions: 0
7. Authority-transition confounds: 4 (ROUT-022/031/033/047; W2 Astra dual-pass pseudo-route suppression -> W3 deterministic generic-R3-fires-first)
8. Measurement sensitivities: 6 registered findings (MS-01..MS-06 in measurement-sensitivity-findings.json)
9. Representation-only regressions: 1 (ROUT-069)
10. Ambiguous P0: 0
11. ROUT-069 classification: PRODUCT_REPRESENTATION_CHANGE (condition=null; W2 NO_CRITICAL_ERROR vs W3 CRITICAL_ERROR; owner DETERMINISTIC both waves; W2 pass was a junk-route artifact)
12. ROUT-030 classification: NOT_A_REGRESSION (lateral FAIL->FAIL)
13. Safety blocker? NO (no Wave-4 safety-first gate triggered; broad safety logic must not be reopened)
14. Route criteria total: 108
15. Route PASS: 0
16. Route propositions analyzed: 39 entries across 28 emitting cases (23 routing, 3 safety, 2 discovery-emit sets per frozen classification)
17. B0 count: 0
18. B1 count: 0
19. B2 count: 0
20. B3 count: 0 (rejected with documented mechanism: labels and evidence_refs are born together in build_route_candidates before serialization)
21. B4 count: 16
22. B5 count: 23
23. B6 count: 0
24. B7 count: 0
25. B8 count: 0
26. B9 count: 0 (registered as secondary flag on all 39 entries: binding exists but measurement cannot observe it)
27. Dominant binding failure: B5_ROUTE_OBJECT_COPIES_PROVENANCE_ONLY (serialized labels-only list separates labels from keyed evidence)
28. Dominant owning module: serialization shape - runtime/sut/phase2/pipeline.py (~L372-401) + runtime/sut/phase3/finalize.py (~L232-267); scorer consumption in evaluation/dev-corpus-scorer-v1/scorer.py _score_routes
29. Provenance-present count: 39/39
30. Semantically-supporting-evidence count: 0 (not deterministically measurable under frozen judge stub; SemanticJudgeStub.route_equivalent = false)
31. Same-target evidence count: 39/39 same-track; 23 structurally same-service-candidate (SERVICE class); semantic same-target not assessable
32. Access-path evidence count: 39/39 mechanically attached
33. Condition evidence count: 39/39 mechanically attached
34. Route failures attributable to binding: 0 (a perfect join alone flips no verdicts; 0 exact label-gold matches across 39 entries)
35. Route failures independent of binding: 108
36. Target-selection failures remaining: 84 (R0_NO_STRUCTURED_ROUTE)
37. Access-path failures remaining: 0
38. Condition failures remaining: 4 (R5)
39. Measurement-sensitive route failures: 2 (ROUT-040/061 PARTIAL token-substring artifacts)
40. Historical RC-04 meaning: uncertainty-depth grading (36 criteria graded PARTIAL; post-Wave-2 rc04-assessment.md) - intact and untouched
41. Binding defect same as RC-04? NO
42. New repair ID needed? YES: W4-RC-A
43. Independent uncertainty defect remains? YES (INDEPENDENT_RC04_UNCERTAINTY_DEFECT; deferred as W4-RC-C)
44. RC-06 needed in Wave 4? NO (renderer not in Wave-4 scope; presentation noise is active but does not destroy structured route semantics)
45. W3-RES material findings: none MATERIAL_TO_BINDING or MATERIAL_TO_ROUTE_TARGET (w3-res-binding-assessment.md; URL-shaped FRAGMENT labels fold into B4 label quality)
46. Highest-leverage Wave-4 repair: W4-RC-A (route-to-evidence semantic binding + structured route evaluation, coupled pair)
47. Second dependent repair if any: W4-RC-B (access/condition binding, strictly after A)
48. Repairs deferred: W4-RC-C (independent uncertainty), W4-RC-D (folded into A; reopen only for quantified residual)
49. Wave-4 recommended scope: WAVE4_ROUTE_TARGET_PLUS_BINDING (exactly one; see wave4-scope-recommendation.md)
50. Fresh holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT
51. SUT changed? NO
52. Measurement changed? NO
53. Gold changed? NO
54. New semantic model calls? NO
55. Fresh cases consumed? NO
56. STATUS: POST_WAVE3_P0_BINDING_WAVE4_SCOPE_GATE_COMPLETE
57. Recommended next owner task: explicit owner authorization for Wave 4 under scope WAVE4_ROUTE_TARGET_PLUS_BINDING (W4-RC-A implementation with the full regression suite listed in wave4-repair-candidates.json). No Wave-4 work starts without that authorization.
