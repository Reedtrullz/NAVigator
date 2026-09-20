# Final report - NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-4-QUOTA-SAFE-V1

Zero semantic model calls. Exact canon-hash semantic reuse only. Partial measurement; no certification.

Reuse joins: 0 exact-hash; 8 weak criterion-id joins. Weak joins (criterion-id only, no frozen packet hash): 8 -> ['DIS-109::critical_condition', 'DIS-109::forbidden:01', 'DIS-118::forbidden:01', 'ROUT-021::forbidden:02', 'ROUT-038::forbidden:02', 'ROUT-041::forbidden:01', 'ROUT-063::forbidden:01', 'ROUT-085::critical_condition']

Gold-changed cases (ROUT-061/070/073) are flagged separately in the transition artifact and never counted as product regressions against original-gold semantics.

1. Task ID: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-4-QUOTA-SAFE-V1
2. Wave-4 product manifest SHA: 4f55e6fb6c95fc7a3f136e0cc6bdae8cec2b1a07e1c082388f9ac6f7bf27d4e5
3. Wave-4 prediction SHA (set): a342ce264518bffc113a67b26b09291ab9636814ca91ec2beeb3c9c232795f65
4. Measurement revision SHA: db888c77ca7d319bef0b9754ac3fdb27f52de9b5af49fd86ad46f036f495d065
5. Wave-3 prediction SHA (set): 862d1056815804382968a341106302c3b7a54ecbddd16e1ebd423f600bcf4faa
6. Historical Wave-3 measurement SHA: bdede50d90b1ddc40ba30b3d617ebd2d2d0f35ef576e5a5861d6015095ee9a2e
7. Input integrity: 22 pins verified, 0 mismatches
8. New semantic model calls: 0
9. Wave-3 bridge deterministic criteria: 482
10. Wave-3 bridge exact semantic reuses: 96
11. Wave-3 bridge pending semantic criteria: 0
12. Wave-3 bridge authoritative total: 600
13. Wave-4 deterministic criteria: 482
14. Wave-4 semantic-owner criteria: 118
15. Wave-4 exact semantic reuses: 8
16. Reused LLM_REVIEWED: 0
17. Reused LLM_ADJUDICATED: 8
18. Wave-4 pending quota criteria: 110
19. Wave-4 authoritative total: 490
20. Wave-4 criterion coverage pct: 81.67
21. Semantic input hash contract: semantic-input-hash-contract.md (94959ec8524a6c36)
22. Fuzzy reuse count: 0
23. Semantic inference by agent: 0
24. Quota-resume packet count: 110
25. Future Astra minimum calls: 220
26. Packet leakage result: PASS
27. Packet reviewability result: PASS
28. Deterministic derivation kernel: judge_core_v2_13.derive_final
29. LLM calls during derivation: 0
30. Adapter-only comparable criteria: 588
31. Adapter-only improvements: 0
32. Adapter-only regressions: 0
33. Product-effect comparable criteria: 478
34. Product-effect improvements: 6
35. Product-effect regressions: 2
36. Structured route objects (cases): 62
37. Route/evidence joins (resolved/missing): 0/125
38. Structured adapter paths (cases): 62
39. Legacy adapter paths (cases): 58
40. Structured present + fallback used: 0
41. Complete Wave-4 semantic route PASS available?: no
42. Safety deterministic status: deterministic safety rows authoritative; semantic-dependent safety rows pending
43. RC-04 conclusion status: # Remaining RC-04 / RC-06 Assessment (carry-forward; semantic criteria pending quota)
44. RC-06 conclusion status: carried forward; semantic criteria pending quota
45. Fresh-holdout readiness: FRESH_HOLDOUT_READINESS_PENDING_COMPLETE_MEASUREMENT
46. Astra calls: 0
47. Sol calls: 0
48. Other semantic LLM calls: 0
49. Fallback model used: NO
50. SUT rerun: NO
51. Product changed: NO
52. Measurement changed: NO
53. Gold changed: NO
54. Fresh cases consumed: 0
55. Burned classification retained: BURNED_DEV_BASELINE_ONLY
56. Partial freeze SHA: ff0b7a41a2c30168f87695801cebc7225a4d3269eb1786f3b03694147caaf62e
57. Hashes verified: hashes.txt regenerated at close
58. STATUS: MEASUREMENT_V3_REMEASURE_WAVE_4_QUOTA_DEFERRED
59. Exact quota-resume task: resume runbook in quota-resume-runbook.md when Astra quota returns; Astra LOW only; no fallback models
