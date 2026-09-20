# V2.7D Final Report - Shared Miss Diagnosis

1. Task ID: NAV-EXPLORE-JUDGE-CONTRACT-V2_7D-SHARED-MISS-DIAGNOSIS
2. Prior V2.7 status: V2_7_NO_NON_M2_JUDGE_QUALIFIES
3. Baselines verified: 13/13 SHA pins recomputed and matched (baseline-integrity.json)
4. Historical writes: 0
5. Model calls: 0
6. Contract changed: NO
7. Diagnostic fixture N: 90 (UNC 36 / ROUTE 36 / FORB 18)
8. Exact-text collisions: 0 (vs 4568 historical texts)
9. Annotation provenance: INTRA_ANNOTATOR_REPEATABILITY (same annotator, two blind stance-controlled passes)
10. Raw overall agreement: 81/90 = 0.900
11. Uncertainty agreement: 27/36 = 0.750
12. Route agreement: 36/36 = 1.000
13. Forbidden agreement: 18/18 = 1.000
14. PARTIAL<->UNRESOLVED disagreements: 9 (all on UNC-28..36)
15. SATISFIED<->UNRESOLVED disagreements: 0
16. ACCEPTABLE<->PARTIAL disagreements: 0
17. ACCEPTABLE<->UNRESOLVED disagreements: 0
18. Forbidden confusion pairs: 0 (all preregistered pairs zero)
19. Fixture defects: 0
20. Genuine contract disagreements: 9
21. Uncertainty diagnosis: CONTRACT_BOUNDARY_INSTABILITY_SUPPORTED. Root: UNC-A1 (frozen judge-core table maps CONTRADICTORY_LIMITATION to PARTIAL while burned V2.7 gold used UNRESOLVED) plus UNC-A2 (UNCLEAR_PROSE behavior undefined). The frozen contract is internally inconsistent on one central boundary.
22. Route diagnosis: MODEL_BIAS_SUPPORTED. Hedged-positive routes are perfectly human-stable on fresh data; ROUTE-22/23 shared misses were verdict-level model errors. ROUTE-A1/A2 remain minor documented ambiguities.
23. Forbidden diagnosis: MODEL_BIAS_SUPPORTED. FORB-13 was a model match-judgment error on the paraphrase boundary (FORB-A1 uncalibrated MATCH threshold); fresh near-match rows were 100 percent human-stable PRESENT.
24. Hedged-positive route human-stable: YES (1.00 on fresh set)
25. Intentional ambiguity UNRESOLVED human-stable: NO. The same annotator produced two defensible readings, splitting 9/18 boundary rows (PARTIAL vs UNRESOLVED). The contract is coarser than stable human use on contradictory/garbled/self-retracted limitation prose; UNRESOLVED adjudication on this boundary is not deterministic.
26. FORB-13 mechanism identified: YES - model match-judgment error on a human-stable paraphrase boundary; FORB-A1 calibration gap noted for future work.
27. Historical UNC-46/47: gold questionable - UNRESOLVED was unreachable through the frozen judge-core table for the model behavior; UNC-48/49: genuinely ambiguous under frozen contract (UNC-A1/A2 realized).
28. Historical ROUTE-22/23: consistent with the frozen contract; model bias, not contract failure.
29. Historical FORB-13: consistent with the frozen contract; model error on paraphrase matching.
30. New model screening run: NO
31. Product runtime changed: NO
32. Gates: PASS - zero fixture collisions, zero fixture defects, route and forbidden human-stable (>=0.95), no unexpected confusion pairs, raw agreement frozen pre-adjudication. FAIL - uncertainty agreement 0.75 < 0.95 with one central boundary over 1 disagreement.
33. STATUS: V2_7D_CONTRACT_REPAIR_REQUIRED
34. Is further model screening justified: YES. Route and forbidden shared misses were model-level errors on human-stable boundaries, so fresh judge screening remains scientifically justified after contract-boundary repair lands.
35. Is contract repair required: YES. The uncertainty family is human-unstable (0.75) because the frozen contract text and the frozen judge-core behavior table conflict on CONTRADICTORY_LIMITATION and leave UNCLEAR_PROSE undefined.
36. Recommended next bounded stage: a separate owner-authorized uncertainty-contract repair task that resolves UNC-A1 (align frozen table and prose semantics for contradictory/garbled/self-retracted limitation behavior) and defines UNCLEAR_PROSE (UNC-A2), then re-verifies human stability on fresh fixtures. Model screening only after the contract boundary is stable. No repair was performed in this task per spec.

Hard locks honored: 0 model calls, 0 contract changes, 0 historical writes, 0 product changes, 0 subagents.
