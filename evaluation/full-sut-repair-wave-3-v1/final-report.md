# Wave 3 Final Report — NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1

Candidate: W3-RC-A v1 (only attempt; max 2 allowed, 1 used).
Scope: route proposition construction only. No Measurement V3 run, no scoring,
no gold access, no fresh cases, no safety-policy change, no RC-04/RC-06 work.

1. **Task ID**: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1
2. **Starting Wave-2 SUT SHA**: routes.py a543c2f7...f94d3751 (Wave-2); all other 23 components unchanged
3. **Starting Wave-2 manifest**: evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json, sha256 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e (24/24 components verified at task start)
4. **Scope-gate SHA**: evaluation/post-wave2-p0-routing-wave3-scope-gate-v1/hashes.txt sha256 5ed519d1a0212ac4cacc30e0dae71bbd524e29ebc19d116f7fcdb977035c4260
5. **Gate 0**: PASS (gate0-report.json): import smoke 14/14, baseline 216/216, control-character scan clean
6. **Proven route-proposition root cause**: primary A — `national_service_name()` accepted only quoted/bold spans; markdown-table service names in first column are plain text, so no SERVICE CANDIDATE (and hence no route proposition) was ever minted for identity-table rows; secondary D — the bold path accepted front-matter labels (`Hensikt` etc.), minting fragment-like targets. See route-proposition-root-cause.md.
7. **Root-cause confidence**: A PROVEN, D PROVEN (mechanism); B, C, E, G, H, I exonerated by source reading; no fix based on low-confidence hypotheses
8. **Owning SUT stage/module**: runtime/sut/phase2/routes.py (S6 route construction)
9. **Service-candidate representation**: verbatim first-cell service name from the governing identity-table row, validated against frozen header whitelist {instans, tjeneste, service}; fail-closed on ambiguity
10. **Route-proposition representation**: RouteCandidate objects with service_name, self_referral, route_state, track binding; unchanged downstream planner/renderer contract
11. **Access-path representation**: self_referral derived from positive self-contact markers and negative/positive outranking; UNCLEAR default (spec section 11 forbids discarding routes on unknown optional access detail)
12. **Conditions representation**: carried by claim text and evidence attachment; no new condition model (scope-bounded)
13. **Track-binding mechanism**: unchanged RC-08 per-track records; structured extraction runs on per-track evidence only (tests 10-11)
14. **Provenance mechanism**: unchanged P-K provenance numbering; every route entry carries evidence_ids + provenance_ids (39/39 valid)
15. **Source changes**: runtime/sut/phase2/routes.py only (W3-RC-A structured first-column extraction + metadata-label reject list on the lexical fallback); no planner/renderer/finalize/schema/safety changes were mechanically necessary
16. **New tests**: runtime/sut/phase2/test_route_propositions.py (26 tests: section-18 matrix 1-20 + ceiling case + section-19 zero-gates), tracked in w3-rc-a-tests.json (file sha256 46291a029745db45bbb4cba326a9a38ac5a4fdd8dc1cbe55e17cf659b45aa71d)
17. **Raw KB fragment gate**: PASS (test_17; diagnostic FRAGMENT_LIKE=4 is heuristic-only, see remaining-findings.json W3-RES-01/02)
18. **Section-heading gate**: PASS (test_18; ROUT-072 also dropped its former Hensikt fragment vs Wave 2)
19. **Source-ref gate**: PASS (test_19)
20. **Route track-binding gate**: PASS (section-19 zero gates + 39/39 replay entries bound)
21. **Route provenance gate**: PASS (STRUCTURED_ROUTE_WITHOUT_PROVENANCE=0; 39/39 entries with evidence_ids+provenance_ids)
22. **Rendered/structured consistency**: PASS (0 divergence cases; RENDERED_ROUTE_WITHOUT_STRUCTURED_ROUTE=0)
23. **Supported-route preservation**: PASS (SUPPORTED_ROUTE_LOST_BEFORE_FINAL_OUTPUT=0)
24. **Acute safety invariant**: PASS (test_06; safety.py hash-unchanged; acute/suppressed inputs mint no routes)
25. **Full test count/result**: 242 passed, 0 failed (was 216 pre-Wave-3; +26 new route tests)
26. **Phase 1 regression**: PASS (included in full suite; runtime/sut core tests green)
27. **Phase 2 regression**: PASS (aggregate/decompose/discovery_adapter/knowledge/knowledge_scoping/routes/route_targets/safety suites green, unmodified)
28. **Phase 3 regression**: PASS (test_phase3.py 22/22, test_planner_scoping.py 2/2, unmodified)
29. **Wave-1 regressions**: PASS (all Wave-1-era test files green unmodified)
30. **Wave-2 regressions**: PASS (all Wave-2 test files green unmodified; Wave-2 manifest pin verified)
31. **Evaluator imports into product**: 0 (PRODUCT_IMPORTS_EVALUATION=0; separation tests green)
32. **Candidate source SHA**: runtime/sut/phase2/routes.py 29b0bd44ee5ad4e7e3bbca492f34958e3cbb570fd45e0231d7c0c7c13213d7fa
33. **Candidate manifest SHA**: 6c1f7d4b4b52eeabc16a13e0c34d9cdd332a6acd532cd33ddb796660fd2be14f (repaired-sut-manifest.json; all 24 component hashes re-verified against live files at close, 0 mismatches)
34. **Candidate attempts**: 1 of max 2 (v1; no second attempt needed)
35. **120-case structural replay performed?**: YES (runs/structural-120-replay-v1/, official, one-shot)
36. **Replay SUCCESS**: 120/120
37. **Execution failures**: 0
38. **Crashes**: 0
39. **Schema validity**: 120/120 outputs schema-valid
40. **Route propositions produced**: 39 entries across 28 cases (Wave-2: 24 entries across 20 cases)
41. **Routes empty**: 92 cases (Wave-2: 100)
42. **Routes non-empty**: 28 cases (Wave-2: 20)
43. **Actionable targets**: 39/39 route entries structurally valid with track binding + provenance; 24 distinct route labels
44. **Fragment-like targets**: 4 labels flagged by diagnostic-only heuristic (NAV x2: legitimate 3-letter acronym false positive; URL x2: pre-existing Wave-2 lexical-fallback junk; see remaining-findings.json)
45. **Junk targets**: 0 (JUNK_ROUTE_PASS; RC-07 digit-free junk rule populated and green in Wave 3)
46. **Routes with track binding**: 39/39
47. **Routes with provenance**: 39/39
48. **No_route consistency**: PASS (no_route_asserted flag vs routes content: 0 mismatches)
49. **Rendered/structured consistency**: PASS (0 mismatches; same as item 22, both gates reported)
50. **Gold-blind route funnel**: R0=92 -> R3PLUS_STRUCTURAL_PASS_CANDIDATE=28 (routing 52->23, safety 18->2, discovery_adversarial 22->3); semantic stages R3/R4 not measurable gold-blind and explicitly reserved for Measurement V3 (route-funnel-gold-blind.json)
51. **Determinism**: PASS (independent full rerun into runs/determinism-check-v1/; 120/120 prediction files byte-identical by SHA-256)
52. **Safety logic changed?**: NO (safety.py unchanged; EMERGENCY_TRIGGER_LOGIC_CHANGED=false; all 61 safety-related tests pass)
53. **Measurement V3 changed?**: NO (no measurement run, no measurement file touched)
54. **Gold changed?**: NO (gold SHA pins match TASK-LOCK; no gold file read into product logic)
55. **Historical predictions changed?**: NO (HISTORICAL_PREDICTIONS_MUTATED=false; Wave-2 prediction manifests untouched)
56. **RC-04 implemented?**: NO (deferred per spec section 23; no uncertainty/failure-path work)
57. **RC-06 implemented?**: NO (deferred per spec section 23; no renderer cleanup)
58. **Scorer quirks encoded into product?**: NO (measurement-sensitivity-nonfixes.md recorded; no PREMATURE_ABSENCE avoidance, no garanti-token avoidance)
59. **Fresh cases consumed?**: 0
60. **Overfit findings**: none; no case IDs, corpus strings, or expected verdicts in runtime (id-guard clean; anti-tuning attested in manifest); fixes are structural (header-gated table extraction), not case-shaped
61. **Remaining known issues**: W3-RES-01 acronym heuristic false positive (diagnostic-only); W3-RES-02 pre-existing URL lexical-fallback labels; W3-RES-03 doc-26 section-8 header-whitelist ceiling; W3-RES-04 row-prefix access-marker ceiling; W3-RES-05 header whitelist frozen without tilbud — see remaining-findings.json
62. **STATUS**: FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT
63. **Recommended next bounded task**: owner-authorized Measurement V3 remeasure of the frozen Wave-3 candidate (same remeasure contract as Waves 1-2); no repair work in that task

## Artifact integrity note

The w3-rc-a-tests.json wrapper hashes to 31be0af7485d7efef6e0d889f7ab097b6ed8a76c18112b7892912f165d515e01; the referenced test file test_route_propositions.py hashes to 46291a029745db45bbb4cba326a9a38ac5a4fdd8dc1cbe55e17cf659b45aa71d. Both verified live at close; no stale pins exist inside any frozen artifact.

## Close-out record

Closing timestamp (UTC): 2026-09-16T18:57:59Z. TASK-LOCK closed as
FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT immediately after this report was
finalized; the frozen candidate manifest (repaired-sut-manifest.json) and hashes.txt
component pins above were not modified at close. Replay prediction-manifest SHAs and
the Wave-3 test-file SHA were appended to hashes.txt as post-freeze tracking entries.
This file's own sha256 at close: c9506c33be61b4a57246ea66134e677e12a5537f49cb31c9c8a5f0f4f79e0465.

SHA scope clarification (post-freeze, 2026-09-16): c9506c33be61b4a57246ea66134e677e12a5537f49cb31c9c8a5f0f4f79e0465 is the sha256 of the 63-item report content immediately prior to this close-out record; that content hash is what TASK-LOCK.terminal_report_sha256 pins. The final on-disk file including this close-out record and this clarification necessarily hashes to a different value; that final value is recorded in the session log, not chased self-referentially here.
