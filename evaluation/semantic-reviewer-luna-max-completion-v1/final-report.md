# FINAL REPORT - NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-MAX-COMPLETION-V1

1. **Task ID**: NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-MAX-COMPLETION-V1
2. **Predecessor lineage**: NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-QUALIFICATION-V1 (`evaluation/semantic-reviewer-luna-qualification-v1`, terminal `NO_LUNA_REVIEWER_CONFIG_QUALIFIES`, immutable; 41/41 hashes re-verified)
3. **Predecessor qualification contract SHA256**: `a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f` (byte-copied as `inherited-contract.json`)
4. **Reference corpus SHA256**: `b85caaaa64f3393f27f8177f0b4979e6139c0ff8d18ee3c80efb45eab9e11c2b` (plus exclusions/conflicts/provenance and split pins in `input-integrity.json`, all PASS)
5. **Why continuation was required**: MAX passed frozen screening for both lanes but was never run through Stage-2/Stage-3 because the predecessor's frozen cheapest-sufficient policy stopped after HIGH failed; the predecessor's universal conclusion was therefore under-supported. This lineage completed only the missing branch. HIGH results remain valid; no corruption or invalidation.
6. **Frozen MAX config verified**: YES. `inherited-max-config.json` SHA256 `89e12976b6f134daecb55d68f41536b1e5eee0b9b0dbe2242e067799f5bf754b`, byte-identical to predecessor pin; model gpt-5.6-luna, reasoning_effort MAX, frozen local proxy route.
7. **Screening previously passed**: YES, both lanes (frozen predecessor baseline: 90 calls / 330,899 tokens; 0 transport errors).
8. **New HIGH calls**: 0
9. **New Astra calls**: 0
10. **New Sol calls**: 0
11. **MAX forbidden pass A calls**: 147 (one technical retry policy; 0 retries used, 0 transport errors, 0 rate-limit events)
12. **MAX forbidden pass B calls**: 147
13. **MAX critical pass A calls**: 80
14. **MAX critical pass B calls**: 80
15. **Schema validity** (schema_valid AND enum_valid per pass event): forbidden 292/294; critical 160/160.
16. **Evidence validity** (per pass event): forbidden 288/294 (4 rows had >=1 invalid pass, 4 invalid pass events total incl. schema); critical 90/160 (48 rows with >=1 invalid pass; 70/80 rows INVALID_MODEL_REVIEW overall).
17. **Forbidden consensus coverage**: 128/147 = 87.07% (gate context: consensus errors vs reference 6 > max 2 -> FAIL).
18. **Forbidden Tier-A agreement** (accepted-consensus rows matching frozen authoritative reference): 122/128 = 95.31% agreement; gate is error-count based: 6 errors > max 2 -> FAIL.
19. **Forbidden EDGE agreement**: pass-level 0.9333 (25 errors / 286 valid passes); agreement floor 0.92 PASS, error gate <=2 FAIL (4 errors).
20. **Forbidden qualification**: FAIL (`MAX_NOT_QUALIFIED`). All four core gates exceeded; EDGE error gate exceeded.
21. **Critical consensus coverage**: 30/80 = 37.50% (70/80 rows INVALID_MODEL_REVIEW).
22. **Critical Tier-A agreement**: 19/30 = 63.33% (11 consensus errors > max 0 -> FAIL).
23. **Safety-subset agreement**: 23/23 subset rows evaluated; 8 errors -> 65.22% agreement (gates 1.0 agreement / 0 errors -> FAIL).
24. **Dangerous-direction errors**: under-escalation family 1 (ref CLEAR_TRIGGER_SUPPORT -> CLEAR_NON_TRIGGER_SUPPORT); catastrophic false-trigger consensus escapes 1 (gate 0 -> FAIL).
25. **Critical evidence validity**: 90/160 valid pass events; evidence-invalid rows 48 > max 0 -> FAIL.
26. **Critical qualification**: FAIL (`MAX_NOT_QUALIFIED`).
27. **Stability run**: NO. Frozen stage order forbids Stage 3 for lanes failing Stage 2.
28. **Stability result**: `NOT_RUN_NO_LANE_PASSED_STAGE_2` (protocol-correct absence, recorded in `max-stability.json`).
29. **MAX tokens/calls (this lineage, incl. frozen screening baseline)**: 544 calls; input 1,849,736; output 163,441 (reasoning 112,217); total 2,013,177. Stage-2 portion: 454 calls / 1,682,278 tokens; 0 retries, 0 rate-limit events; Stage-2 latency mean 5.96 s (forbidden) / 7.92 s (critical).
30. **Frozen HIGH tokens/calls (predecessor, unchanged)**: 544 calls / 2,014,991 total tokens.
31. **Relative token ratio MAX vs HIGH**: 0.999 (MAX reasoning consumed essentially the same tokens and still failed; no cost advantage).
32. **Luna forbidden final decision**: `NO_LUNA_CONFIG_QUALIFIES`
33. **Luna critical final decision**: `NO_LUNA_CONFIG_QUALIFIES`
34. **Any qualified Luna lane?**: NO.
35. **Historical predecessor mutated**: NO (all predecessor hashes verified before and unchanged; predecessor TASK-LOCK remains closed with its original terminal status).
36. **Qualification gates changed**: NO (inherited contract byte-identical; scoring uses predecessor core gates verbatim; EDGE gates applied per-lane per V2.2 lineage convention, both PASS-direction gates evaluated, no threshold altered).
37. **Semantic prompt changed**: NO (verbatim inherited reviewer prompt/config).
38. **Fresh cases consumed**: 0.
39. **STATUS**: `NO_LUNA_REVIEWER_CONFIG_QUALIFIES_CONFIRMED`
40. **Next owner task**: owner decision only. The frozen review router keeps PRIMARY = GPT_6_ASTRA_LOW for both lanes with activation_authorized = false. No Luna activation, no gate changes, no new screening, no fresh holdout, and no product changes are authorized from this task. Any new candidate family or router change requires a separate owner-authorized task.

## Interpretation (non-scoring)

The completion answers the predecessor gap cleanly: MAX reasoning effort does
not repair HIGH's semantic failures. Forbidden lanes degrade through reference
disagreement and evidence-scope errors; critical lanes are dominated by invalid
reviews (70/80 rows), collapsing consensus coverage to 37.5% with safety-gate
violations including one catastrophic false-trigger escape. MAX matches HIGH's
token cost almost exactly, so there is no remaining cost/quality tradeoff to
pursue within the Luna family.
