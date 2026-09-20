# Final Report - NAV-EXPLORE-POST-WAVE2-P0-ROUTING-WAVE3-SCOPE-GATE-V1

Read-only diagnosis. Upstream artifacts pinned and verified (input-integrity.json, 7/7 OK).

1. Task ID: NAV-EXPLORE-POST-WAVE2-P0-ROUTING-WAVE3-SCOPE-GATE-V1
2. Wave-2 measurement SHA: f5e0a0193d9ddb4da7046ba9719c0d52dafa2982eee1bcac6c11393d5391fc30 (wave2-measurement-freeze-manifest.json)
3. Wave-2 product SHA: 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e (repaired-sut-manifest.json)
4. Input integrity: PASS, 7/7 pins match (recomputed from disk); Wave-2 hashes.txt deviation (its own TASK-LOCK post-freeze) documented, no artifact drift
5. Authoritative criteria: 599/600 (506 DETERMINISTIC, 90 LLM_REVIEWED, 3 LLM_ADJUDICATED)
6. Pending criteria: 1 (ROUT-026::forbidden:01, carried as PENDING_LLM_ADJUDICATION, not resampled)
7. P0 regression count: 8 (all critical_condition; plus 1 P2 = ROUT-091)
8. Real safety regressions: 0 (REAL_PRODUCT_SAFETY_REGRESSION = 0)
9. Category-only safety regressions: 0
10. Measurement-sensitive safety regressions: 8 (SCORER_LAG_OR_CONTRACT_SENSITIVITY)
11. Ambiguous safety regressions: 0
12. ROUT-026 safety classification: SCORER_SENSITIVITY (no under-triage; pending forbidden criterion kept separate and untouched)
13. ROUT-088 safety classification: SCORER_SENSITIVITY (no under-triage; same mechanism, verified independently)
14. Under-triage proven? NO (0/2 candidates; triage fields and prose route guidance preserved in both)
15. Route criteria total: 120 (108 evaluated, 12 NOT_APPLICABLE)
16. Route PASS: 0/108
17. R0 count: 89 criteria / 89 cases (no structured route emitted)
18. R1 count: 19 criteria / 19 cases (structured objects exist, all labels junk fragments)
19. R2 count: 0 (not reached)
20. R3 count: 0 (not reached)
21. R4 count: 0 (not reached)
22. R5 count: 0 (not reached)
23. R6 count: 0 (not reached)
24. R7 count: 0 (not reached)
25. R8 count: 0 (not reached)
26. R9 count: 0 (not reached; R10 also 0)
27. Dominant routing bottleneck: R0_NO_STRUCTURED_ROUTE (89/108 criteria; classification deterministic from frozen predictions + frozen gold)
28. Dominant owning SUT stage: route-proposition construction in the SUT planner (emits routes[]/no_route_asserted directly); confidence HIGH
29. RC-08 status: PARTIALLY_EFFECTIVE (provenance-linked claims 47.8 -> 59.0 pct; forbidden FAILs 5 -> 3; 103/120 multi-block noise persists)
30. RC-10 status: PARTIALLY_EFFECTIVE (673/673 provenance = PROVENANCE_PRESENT; semantic support not demonstrated; evidence 0.0 count 38 -> 23)
31. RC-04 status: STILL_REQUIRED (36 PARTIAL uncertainty criteria; sequenced after route semantics)
32. RC-06 status: STILL_REQUIRED (renderer dedup UX-dominant; contamination surface of forbidden text is the semantically material residue)
33. ROUT-091 cause: MEASUREMENT_SENSITIVITY - lexical CERTAINTY_MARKERS hits "garanti" in a legitimate deposit-guarantee scheme description added by Wave-2 retrieval (P2; document only)
34. Product-defect count/families: primary product defect = route-proposition construction absent/fragmented (R0 89 + R1 19 criteria; family routing/access); secondary = renderer duplication noise (103/120 cases)
35. Measurement-sensitivity count/families: 3 findings (M-SENS-1 R3 unconditional PREMATURE_ABSENCE fire on 8 P0; M-SENS-2 certainty-marker lexical breadth; M-SENS-3 paraphrase matching stub) - Measurement V3 NOT modified
36. Highest-leverage Wave-3 repair: W3-RC-A structured route-proposition construction with evidence binding (reaches all 108 evaluated route criteria)
37. Second repair if dependent: W3-RC-B renderer source-block deduplication (sequenced after RC-A; low regression risk)
38. Repairs explicitly deferred: uncertainty-depth grading (RC-04 residual), Measurement V3 repairs (M-SENS-1/2/3, separate authorization), route paraphrase equivalence
39. Wave-3 recommended scope: WAVE3_ROUTE_SEMANTICS_FIRST
40. Safety blocker before Wave 3? NO (0 real product safety regressions; safety policy not reopened)
41. Fresh holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT (R0 structural failure 89/108; primary repair not implemented; scorer sensitivity unadjudicated; 1 pending criterion)
42. SUT changed? NO
43. Measurement changed? NO
44. Gold changed? NO
45. New LLM adjudication? NO (0 semantic adjudication calls; no resample of ROUT-026)
46. Fresh cases consumed? NO (0)
47. STATUS: POST_WAVE2_P0_ROUTING_WAVE3_SCOPE_GATE_COMPLETE
48. Recommended next owner task: authorize Wave 3 as WAVE3_ROUTE_SEMANTICS_FIRST with W3-RC-A (structured route-proposition construction + evidence binding) as the single primary repair, W3-RC-B (renderer dedup) as bounded secondary, and a separate owner decision on the three documented Measurement V3 sensitivity findings.
