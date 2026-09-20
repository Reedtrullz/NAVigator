# FINAL REPORT - NAV-EXPLORE-MEASUREMENT-V3-BURNED-BASELINE-V1

Terminal status: MEASUREMENT_V3_BURNED_BASELINE_HUMAN_REVIEW_PENDING (successful terminal state; human review pending by design).

## 51-point report

1. Task ID: NAV-EXPLORE-MEASUREMENT-V3-BURNED-BASELINE-V1
2. Phase 3 status: FULL_SUT_PHASE_3_READY (frozen, immutable input)
3. Phase 3 manifest SHA: 485ecbe5d6957c4c8a34e37ac17986e1fe7a827aa6b7e819cb011924fcabfdce
4. Official prediction SHA basis: per-family frozen predictions-manifest.json (safety 08d64b58..., routing 5a15f020..., discovery_adversarial fc4a87cb...; full values in baseline-freeze-manifest.json)
5. Measurement V3 status: frozen, immutable, used as-is
6. Measurement V3 manifest SHA: 331310497a6630dcefc2990079593eed048b9dc4808e8800b0b94b73cb9847c7
7. Corpus manifest SHA: 9c265731e6e17ea54844b6db646dac4abe1901e49ee1c5ce56c3ec081db177ef
8. Gold integrity: gold-model.md SHA 994ab1885b81d85a378ad3744930c2b9fc11cfe3e9dbc6df7bfa65f729949804; loader strip_gold executed for all 120 burned dev cases; gold leak audit 0
9. Historical writes: none to upstream lineages; only this task's output directory was written
10. Predictions edited? NO
11. Predictions rerun? NO
12. Cases N: 120
13. Predictions N: 120
14. Alignment: aligned_120_120 = true; 0 duplicate / 0 missing / 0 extra / 0 id mismatches (case-prediction-alignment.json)
15. Total criteria: 600
16. Deterministic criteria N: 526
17. Human-review criteria N: 74
18. Automated/deterministic coverage: 87.67% overall (critical_condition 91.67%, forbidden_claim 46.67%, route_correctness 100% of applicable, required_uncertainty 100%, evidence_completeness 100%)
19. M2 review N: 0 (scorer input has no M2-workflow decomposition fields; routing rationale recorded in partial-aggregate-metrics.json)
20. Forbidden review N: 64
21. Route review N: 0
22. Uncertainty review N: 0
23. Human reviews completed N: 0 (Batch 1 is a separate task and was not started)
24. Human reviews pending N: 74 (10 critical_condition + 64 forbidden_claim)
25. Gold visible in review packets? NO (0 packets with gold visible; leakage audit clean)
26. Expected verdict visible? NO (0 expected labels, 0 model verdicts visible in packets)
27. Product runtime failures: 0 runtime crashes; 98 RECOVERABLE failure states
28. Terminal product failures: 9, all S1 input-schema rejections
29. Schema-valid predictions: 120/120 prediction files parsed and scored; SUT execution-level result 111 SUCCESS / 9 TERMINAL
30. Provenance completeness: 610/610 claims have provenance entries (291 directly linked, per frozen Phase 3 data)
31. Deterministic scorer metrics: critical_condition 110 CRITICAL_ERROR; forbidden_claim 53 CLAIM_ABSENT_TAKEN + 3 CLAIM_PRESENT; route_correctness 108 NO_ACCEPTABLE_ROUTE; required_uncertainty 83 NOT_REQUIRED / 34 PARTIAL / 1 SATISFIED / 2 VIOLATED; evidence completeness mean 0.6833, 82/120 fully complete
32. Fail-closed metrics: all 74 review-required criteria routed to HUMAN_REVIEW_PENDING with 0 authority overlap, 0 packets missing, 0 deterministic criteria carrying a packet
33. Review packet validity: 74/74 valid (review-packet-leakage-audit.json)
34. Review routing correctness: 67 escalated items, 74 pending criteria with valid packets, 0 pending without packet, 0 duplicate authoritative owners
35. Review batch SHA: human-review-batch-manifest.json = 4e7fc67946469f57a0e4729d92409b5b64f86cc67a914f7ebf43ae193c3ebd8a
36. Measurement routing determinism: MEASUREMENT_ROUTING_DETERMINISM_PASS (2 runs, 120/120 semantically identical; only wall-clock fields differ, documented)
37. Product source changed? NO
38. Measurement source changed? NO (the only code touched in this task was this task-local runner's audit scan scope)
39. Fresh data used? NO
40. Burned/dev label present? YES: BURNED_DEV_BASELINE_ONLY (README.md and this report); partial baseline, not a certification artifact
41. Fully complete baseline? NO - by architecture: 526/600 deterministic, 74/600 intentionally HUMAN_REVIEW_PENDING (not semantic failures and not UNRESOLVED)
42. Metrics blocked by human review: complete aggregate metrics require Batch 1 review of the 74 frozen packets
43. Product findings N: 3 notable (9 terminal S1 input-schema rejections; discovery invoked 0/120; epistemic states EXISTENCE_ONLY 98 / UNVERIFIED 22 - see product-diagnostics.json)
44. Measurement findings N: 2 notable (forbidden_claim automation only covers 46.67% of criteria, driving the 74-packet queue; M2 lane N=0 by input contract)
45. Baseline freeze SHA: baseline-freeze-manifest.json = 554e7d4a3c91f3cf928eb17e147046434c20ec71dbacd818616a99c9f23c03c9; hashes.txt = fa350d9ce26096453ab9cdd7b00dc5fa13160d7b801f3e1f6b1ee01d50ec7ac8
46. Fresh holdout run? NO
47. Deployment? NO
48. Gates passed: alignment 120/120; determinism PASS; packet validity 74/74; leakage 0; duplicate owners 0; routing correctness 0 missing packets / 0 deterministic-owner overlap; all 16 freeze pins verified; 4 upstream pins re-found by SHA; 3/3 family manifest pins OK; security audit 0 hits; integrity check 13/14 pre-repair SHAs matched with the 1 mismatch being the intentionally regenerated audit artifact
49. Gates failed: none
50. STATUS: MEASUREMENT_V3_BURNED_BASELINE_HUMAN_REVIEW_PENDING
51. Recommended next bounded stage: NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1 - human review of the 74 frozen packet SHAs only; reviewer batch works on the already-frozen packet hashes; no SUT rerun, no re-scoring, no packet regeneration

## Audit-repair history (full chain)

1. Stage-1 audit scanned run_baseline.py: 10 hits, all the runner's own pattern literals.
2. Patch 1: run_baseline.py excluded from scan scope.
3. Post-patch rerun: still 10 hits; mechanical attribution proved all 10 lived in security-audit.json itself (the audit's hits list embeds the pattern literals, and each rescan reintroduced them - self-referential loop). No real secret or credential existed at any point.
4. Patch 2: security-audit.json excluded; the next rerun then produced 1 hit: freeze-repair-record.json contains the word "secret" in its documentation text. The assertion fired before any file was written; state unchanged.
5. Patch 3 (final): AUDIT_META_ARTIFACTS = (run_baseline.py, security-audit.json, freeze-repair-record.json). No other files, no detection-rule changes.
6. Final audit: 16 files scanned, credential_or_secret_hits = 0, audit_meta_exclusions = 3, non_meta_artifacts_dropped_from_security_scan = 0.
7. Integrity gate before re-freeze: all 13 immutable artifacts (including deterministic-scores.json, measurement-routing-results.json, partial-aggregate-metrics.json, automated-coverage-report.json, human-review-packets.jsonl) matched their pre-repair SHAs exactly. Only security-audit.json differs - it is the regenerated repair output itself.

Freeze events:

- First freeze attempt (2026-09-14T13:06:48Z): INVALIDATED_BEFORE_TERMINAL; manifest SHA c07dee611edc94f5cd2fd72310074212ce31630fa01ce5838ee7fce8d84ac717 preserved in freeze-repair-record.json. Never deleted or rewritten into the new freeze.
- Final freeze: sole authoritative terminal freeze; 16 pins, 0 mismatches.

SCORING_RESULTS_CHANGED_DURING_AUDIT_REPAIR = false (SHA-verified)
REVIEW_PACKETS_CHANGED_DURING_AUDIT_REPAIR = false (SHA-verified)

Interpretation guard: the 74 HUMAN_REVIEW_PENDING criteria are an expected architecture outcome, not semantic failures and not UNRESOLVED verdicts. No complete-baseline claim is made; the baseline is BURNED_DEV_BASELINE_ONLY.
