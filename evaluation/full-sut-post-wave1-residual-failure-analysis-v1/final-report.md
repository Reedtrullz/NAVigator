# Final Report - Post-Wave-1 Residual Failure Analysis V1

1. Task ID: NAV-EXPLORE-FULL-SUT-POST-WAVE1-RESIDUAL-FAILURE-ANALYSIS-V1
2. Wave-1 measurement freeze: final 600-row artifact SHA-256 1f4aac89aa90ef2e5b7e2da2455249633cf2d2c12c7856c64b202a5e45e5e7c1 (matches comparator manifest pin; measurement-freeze manifest pinned at evaluation/measurement-v3-remeasure-repair-wave-1/wave1-measurement-freeze-manifest.json)
3. Product candidate: Wave-1 repaired SUT (FULL_SUT_REPAIR_WAVE_1_CANDIDATE_FROZEN, candidate v2, runtime wave1-rc01+rc02+rc03-v2); repaired-sut-manifest.json SHA-256 e19dd2d6d5329ef3fe85e1719fdc879717563a2e18dc561812b5e6d2a7035f27
4. Measurement integrity: all 6 pins verified; comparator lock closed at MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE; SOURCE_CHANGED=false, PREDICTIONS_CHANGED=false, GOLD_CHANGED=false, MEASUREMENT_CHANGED=false, predictions_rerun=false, llm_semantic_calls=0
5. Total criteria: 600
6. PASS: 290
7. FAIL: 244
8. DEGRADED: 36
9. UNRESOLVED: 18
10. N/A: 12
11. Hard-fail rate: 0.4150 (FAIL / 588 applicable)
12. Non-pass rate: 0.5068 ((FAIL+UNRESOLVED+DEGRADED) / 588)
13. Cases with residual issue: 120/120
14. Residual criterion count: 298 (FAIL+UNRESOLVED+DEGRADED)
15. New failure-family count: 7 (PW1-R1..PW1-R7, re-clustered from scratch)
16. Dominant residual family: PW1-R1 Route-target selection absent (108 criteria, 108 cases)
17. Dominant owning SUT stage: route emission / route-target selection over KB
18. Route criteria total: 108 evaluable (12 N/A)
19. Route PASS: 0
20. Route FAIL: 108
21. No-route-generated count: 88 empty + 8 junk-only = 96 (A_NO_ROUTE_GENERATED / A_NO_ROUTE_GENERATED_JUNK_ONLY)
22. Wrong-route-target count: 12 (B_WRONG_ROUTE_TARGET; content is KB fragments, not service targets)
23. Wrong-access-path count: 0 (not separately observable at 0 route-target matches; category remains defined)
24. Route-condition-error count: 0 (not observed)
25. Route-provenance-failure count: 0 as standalone class; all 12 content routes lack provenance URLs (observable in funnel), but classification resolves to A/B at target level
26. Epistemic-route-failure count: 0 observed
27. Renderer-only routing count: 0 observed (renderer faithfully renders upstream content)
28. RC-01 status: CLOSED (input/schema mechanism eliminated; 3 residual provenance rows DIS-096/DIS-099/ROUT-053 are the PW1-R5/PW1-R6 evidence-attachment defect, unchanged from old baseline)
29. RC-02 status: PARTIALLY_EFFECTIVE (under-triage 0/20; urgency level correct 19/20; 19 exact-category mismatches remain, over-triage dominant; SAF-009/019 uncertainty repairs held at PARTIAL)
30. RC-03 structural status: PARTIALLY_EFFECTIVE (20/108 emit a routes field; 88 empty, 8 junk)
31. RC-03 semantic status: STILL_REQUIRED (0/108 PASS; KB-fragment routes; route-target selection over the KB missing or unreachable)
32. RC-04 status: DO_NOT_RECOMMEND_YET (0 VIOLATED; 36 PARTIAL uncertainty rows are downstream of route/retrieval absence; re-assess after RC-07/RC-08)
33. RC-05 status: NARROW_STANDALONE_COMPONENT_JUSTIFIED (~60% attachment defect: 23 PROV_HAS_URL_NOT_ATTACHED + 3 RC-01 rows -> RC-10; ~40% downstream: 15 NO_PROVENANCE_ENTRIES wait for RC-08)
34. RC-06 status: MOSTLY_PRESENTATION_ONLY (renderer repair deprioritized; measurement-relevant contamination belongs to upstream retrieval scoping PW1-R4)
35. Forbidden-claim residual count: 6 (all retrieval contamination; ROUT-042 additionally LABEL_SENSITIVITY_KNOWN and excluded from repair sizing, so 5 proven product-side)
36. Retrieval contamination finding: 104/120 answers with 2+ national blocks (645 total, max 15), 75/120 claims fields and 2/120 routes fields polluted; median answer 1879.5 chars; one shared upstream retrieval/aggregation mechanism hypothesized (MEDIUM stage confidence, HIGH mechanism confidence)
37. Highest-leverage next repair: RC-08 retrieval scoping (upstream enabler; feeds routes, forbidden residual, and the 15 NO_PROVENANCE_ENTRIES rows; largest structural unblock ahead of RC-07)
38. Second repair priority: RC-10 evidence attachment (26 criteria: 23 evidence + 3 RC-01 rows; isolated, deterministic, LOW risk)
39. Repairs that should wait: RC-09 premature-absence guard and RC-12 uncertainty wording (downstream shadows of route/retrieval emptiness; re-derive after RC-08+RC-10+RC-07 and re-measurement), renderer dedup until after RC-08, and RC-07 itself only after RC-08
40. Safety blockers: none new in Wave 1. Under-triage = 0, no gold-ACUTE case downgraded, no critical unsafe auto asserted. Residual safety issue is category granularity (over-triage dominant), not triage direction.
41. Fresh holdout readiness: NOT_READY_FOR_FRESH_HOLDOUT (dominant mechanisms structural: 0/108 route PASS, contamination in 104/120 answers, 69 downstream premature-absence FAILs)
42. SUT changed? NO
43. Gold changed? NO
44. Measurement changed? NO
45. Predictions rerun? NO
46. Fresh cases consumed? NO (0)
47. STATUS: FULL_SUT_POST_WAVE1_RESIDUAL_FAILURE_ANALYSIS_COMPLETE
48. Recommended next bounded task: owner decision on a single bounded Wave 2 - implement RC-08 (retrieval scoping) + RC-10 (evidence attachment) + RC-11 (safety category vocabulary) as independent repairs, then RC-07 (route-target selection), then frozen re-measurement with Wave-1-style deltas; no fresh holdout, no new blind set
