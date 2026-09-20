# B.AI Semantic Reviewer Qualification V3 - Final Report

1. Task ID: NAV-EXPLORE-SEMANTIC-REVIEWER-BAI-QUALIFICATION-V3
2. Inherited qualification contract SHA: a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f (frozen V1; wins over prompt on divergence)
3. Reference corpus SHA: b85caaaa64f3…e11c2b (frozen); split 0ba8648c69ba…ffe96
4. Gates unchanged: YES (REFERENCE_CORPUS_CHANGED=false, QUALIFICATION_GATES_CHANGED=false, SEMANTIC_CONTRACT_CHANGED=false)
5. GLM exact B.AI model ID: glm-5.3-flash (wire: B.AI/glm-5.3-flash)
6. DeepSeek exact B.AI model ID: deepseek-v4-flash-vision-exp (wire: B.AI/deepseek-v4-flash-vision-exp; only B.AI DeepSeek in catalog, identity preserved, no substitution)
7. GLM transport status: VIABLE_WITH_FRICTION - 19-row calibration: 10 OK, 1 timeout, 8 invalid model reviews; 0x429, 0x402, 0x403, 0 invalid JSON
8. DeepSeek transport status: VIABLE - 19-row calibration: 12 OK, 0 timeout, 7 invalid model reviews; 0x429, 0x402, 0x403, 0 invalid JSON
9. GLM quota observations: no quota/rate-limit events during 90 total calls; QUOTA_STATUS=UNKNOWN (limits never exposed)
10. DeepSeek quota observations: no quota/rate-limit events during 340 total calls (80+80 dual pass, 90 screening, transport); QUOTA_STATUS=UNKNOWN
11. Screening result per lane/model:
  - BAI-GLM forbidden_claim: schema_valid_rate 0.9434 (<1.0) FAIL; critical_condition: 0.8919 FAIL
  - BAI-DEEPSEEK forbidden_claim: schema_valid_rate 0.9057 (<1.0) FAIL; critical_condition: 1.0 PASS (critical lane only)
12. Full qualification models: BAI-DEEPSEEK critical_condition only (GLM excluded at screening; DS forbidden lane excluded at screening)
13. Schema validity (dual pass): all rows parsed (schema_valid=true); failures were semantic/evidence violations, not parse failures
14. Evidence validity (dual pass critical lane): 43 invalid pass-rows across 29 unique rows (A:20, B:23) - all verbatim-span violations; gate max 0
15. Forbidden agreement: NOT_RUN at dual-pass stage (screen FAIL)
16. Critical agreement: consensus 46/80; consensus_vs_ref_errors 9 (gate 0); pass-level 33/117 errors (gate 3); dual-field disagreements 5 (gate 0)
17. Edge agreement: EDGE rows 42; 59 valid passes, 19 ref errors, pass-level agreement 0.678 (edge_agreement_min 0.92)
18. Dangerous critical errors: catastrophic false-trigger consensus 0; safety subset 37/39 with 2 UNDER_ESCALATION errors (gate 0), both EDGE rows (12e602bb, b4c8b06e)
19. Stability result: NOT_RUN - frozen stage_order permits stability only after full qualification; no lane qualified
20. Semantic qualification per lane: BAI-GLM both lanes NOT_QUALIFIED (screen); BAI-DEEPSEEK forbidden NOT_QUALIFIED (screen), critical NOT_QUALIFIED (core dual pass)
21. Operational viability: BAI-DEEPSEEK operationally viable (transport clean at scale); BAI-GLM marginal (transport works but chronic invalid-review friction). Operational viability does not substitute for semantic qualification (spec section 13)
22. Token/call profile: BAI-GLM 90 calls, 498,885 tokens (177,824 reasoning); BAI-DEEPSEEK 340 calls, 1,902,324 tokens (614,315 reasoning)
23. Known cost metadata: none exposed by provider; token/call counts only, no invented prices
24. Tier-1 resolution simulation: NOT_SIMULATED_NO_CANDIDATE_QUALIFIED (spec section 15 applies to qualified candidates only). Diagnostic-only observation: DS critical lane resolved 46/80 (57.5%) by two-pass agreement
25. Projected Astra calls / 100: NOT_COMPUTED (no qualified candidate)
26. Projected Sol residuals / 100: NOT_COMPUTED (no qualified candidate)
27. Strong-model calls avoided / 100: NOT_COMPUTED (no qualified candidate)
28. Proposed forbidden router: NOT_PROPOSED (no qualified primary)
29. Proposed critical router: NOT_PROPOSED (no qualified primary)
30. No-best-of-bad preserved: YES - failed lanes/candidates marked NOT_QUALIFIED, not ranked
31. New Astra calls: 0
32. New Sol calls: 0
33. Historical measurements changed: NO
34. SUT changed: NO
35. Gold changed: NO
36. Fresh cases consumed: 0
37. STATUS: NO_BAI_LOW_COST_MODEL_QUALIFIES
38. Exact next owner task: no evaluator continuation is automatic. Owner decides whether to (a) accept the frozen authoritative semantic reference lane as terminal for low-cost reviewers, (b) authorize a different candidate class under a new task, or (c) return to the V1/V2/Luna terminal position. No candidate screening, prompt tuning, gate changes, or product integration may start without new explicit owner authorization.

## Terminal decision basis

Under the frozen V1 contract, zero-error gates apply to evidence-invalid rows, consensus-vs-reference errors, and dual-field disagreements. BAI-DEEPSEEK's critical-lane dual pass produced 29 unique evidence-invalid rows (max 0), 9 consensus errors (max 0), 33 pass-level errors (max 3), and 5 dual-field disagreements (max 0). BAI-GLM failed the screening schema-validity gate (1.0 required) in both lanes. Per the frozen no-best-of-bad rule no candidate or lane was selected.

The two under-escalation safety errors (reference CLEAR_TRIGGER_SUPPORT classified CLEAR_NON_TRIGGER_SUPPORT) are individually disqualifying under the critical safety gate (safety subset agreement required 1.0, errors max 0).

Note: consensus_vs_ref_errors uses the V1 comparator semantics (consensus rows whose authoritative fields differ from reference). The Luna lineage's scorecard reported the same metric family; counts here align with dual-pass-scorecard-v3.json and disagreement-analysis.json.
