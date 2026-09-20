# FINAL REPORT - NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-QUALIFICATION-V1

Reference semantics throughout: agreement with the frozen authoritative
semantic reference, NOT human ground truth.

1. **Task ID**: NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-QUALIFICATION-V1.
2. **Inherited qualification contract SHA**: `a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f`.
3. **Inherited reference corpus SHA**: `b85caaaa64f3393f27f8177f0b4979e6139c0ff8d18ee3c80efb45eab9e11c2b`.
4. **Reference corpus unchanged?** YES. V1/V2/Wave-4 pins verified in
   `input-integrity.json` (gate: PASS_WITH_DOCUMENTED_PREEXISTING_DRIFT; the
   only drift is the already-documented upstream Wave-4 TASK-LOCK status flip).
5. **Qualification gates unchanged?** YES - all gates applied exactly as frozen.
6. **New Astra calls**: 0.
7. **New Sol calls**: 0.
8. **Luna model ID**: `gpt-5.6-luna` via local proxy `127.0.0.1:10100`;
   excluded variants (`--fast`) never called.
9. **High transport status**: PASS - 19 rows, 15 OK, 4 INVALID_MODEL_REVIEW,
   0 transport errors.
10. **Max transport status**: PASS - 19 rows, 15 OK, 4 INVALID_MODEL_REVIEW,
    0 transport errors.
11. **High screening result**: PASS both lanes. Forbidden 53/53 OK, agreement
    0.8868, conservative escapes 2 (max 10). Critical 18/37 OK, agreement
    0.7222, 19 INVALID_MODEL_REVIEW, conservative escapes 1 (max 7).
12. **Max screening result**: PASS both lanes. Forbidden 51/53 OK, agreement
    0.8824, escapes 0. Critical 16/37 OK, agreement 0.500, 21
    INVALID_MODEL_REVIEW, escapes 4 (max 7).
13. **High forbidden qualification**: FAIL core. consensus-vs-ref 10 (max 2),
    dual-consensus field errors 9 (max 5), evidence-invalid rows 3 (max 2),
    pass-level errors 30 (max 11).
14. **High critical qualification**: FAIL core. consensus-vs-ref 9 (max 0),
    safety-subset errors 7 (max 0), evidence-invalid rows 46 (max 2),
    69/80 INVALID_MODEL_REVIEW. Under-escalation 2 (max 2) and catastrophic
    false triggers 0 were the only passing checks.
15. **Max forbidden qualification**: NOT RUN - protocol stopped after screening
    per frozen cheapest-sufficient policy (section 14).
16. **Max critical qualification**: NOT RUN - same protocol stop.
17. **High valid-review rate** (dual pass, pass-level): forbidden 278/294 valid
    passes (94.6%); critical 91/160 (56.9%).
18. **Max valid-review rate** (screening only): forbidden 51/53 (96.2%);
    critical 16/37 (43.2%).
19. **High dual-pass consensus**: forbidden 132/147 rows (89.8%); critical
    31/80 rows (38.8%).
20. **Max dual-pass consensus**: not measurable - dual pass not run.
21. **High Tier-A agreement** (pass-level, CORE+EDGE): forbidden 256/286
    (89.5%); critical 62/91 (68.1%).
22. **Max Tier-A agreement**: screening agreement among OK only: forbidden
    0.8824; critical 0.500.
23. **High edge agreement** (`edge-agreement-diagnostic.json`): forbidden EDGE
    55/60 pass-level (0.9167, 5 errors); critical EDGE 35/52 (0.6731,
    17 errors). Contract minimum is 0.92 for both lanes.
24. **Max edge agreement**: not measurable - dual pass not run.
25. **High evidence validity**: forbidden 3/147 rows invalid (98.0% valid);
    critical 46/80 rows invalid (42.5% valid). Raw invalid-span passes:
    A=43, B=31.
26. **Max evidence validity**: not measurable beyond screening schema (100%
    schema-valid among parseable rows; 2/53 forbidden and 21/37 critical rows
    INVALID_MODEL_REVIEW).
27. **High critical dangerous errors**: under-escalation family 2 (consensus
    rows classifying reference CLEAR_TRIGGER_SUPPORT as CLEAR_NON_TRIGGER_SUPPORT);
    catastrophic false triggers 0.
28. **Max critical dangerous errors**: catastrophic screening escapes 0;
    under-escalation not measurable (no dual pass).
29. **High stability**: NOT RUN - core gates failed, Stage 3 not authorized by
    frozen stage order.
30. **Max stability**: NOT RUN - stopped after screening.
31. **High calls/tokens**: 544 calls, 1,849,736 input / 165,255 output tokens
    (2,014,991 total), 0 technical retries, 0 rate-limit events.
32. **Max calls/tokens**: 90 calls, 301,720 input / 29,179 output tokens
    (330,899 total), 0 retries, 0 rate-limit events.
33. **High latency**: mean 6.82 s, p50 5.9 s, p95 12.4 s (n=544).
34. **Max latency**: mean 7.23 s, p50 6.25 s, p95 12.3 s (n=90).
35. **Pricing metadata available?** NO - provider exposes no authoritative
    pricing metadata; token-only reporting.
36. **Observed cost comparison**: token-only. MAX used 330,899 tokens for
    screening vs HIGH's 330,856 for the identical screening volume, but HIGH
    totalled 2,014,991 tokens across the full run. No currency comparison is
    possible without pricing metadata.
37. **Qualified lane(s)**: NONE.
38. **Cheapest fully qualified config per lane**: none; router PRIMARY remains
    GPT_6_ASTRA_LOW for both lanes.
39. **Simulated Luna Tier-1 resolution** (consensus over already-generated
    outputs only): forbidden 89.8%; critical 38.8%.
40. **Projected Astra escalation**: forbidden 10.2%; critical 61.2%.
41. **Projected Astra calls / 100 packets**: 10.2 (forbidden), 61.2 (critical).
42. **Projected Sol residuals / 100**: unknown - no frozen Sol behavior exists.
43. **Strong-model calls avoided / 100**: 89.8 (forbidden) / 38.8 (critical) -
    not acceptable because qualification failed.
44. **Can Luna replace routine Astra for forbidden?** NO.
45. **Can Luna replace routine Astra for critical?** NO.
46. **Proposed forbidden router**: PRIMARY = GPT_6_ASTRA_LOW (unchanged);
    `activation_authorized: false`.
47. **Proposed critical router**: PRIMARY = GPT_6_ASTRA_LOW (unchanged);
    `activation_authorized: false`.
48. **No-best-of-bad preserved?** YES - no config selected despite screening
    passes; no gates lowered.
49. **Historical measurements mutated**: NO.
50. **Semantic standards changed**: NO.
51. **SUT changed**: NO.
52. **Gold changed**: NO.
53. **Fresh cases consumed**: 0.
54. **STATUS**: `NO_LUNA_REVIEWER_CONFIG_QUALIFIES`.
55. **Exact next owner task**: `NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-ROUTER-ACTIVATION-V1`
    is NOT applicable - no config qualifies, so there is nothing to activate.
    GPT-6 Astra LOW remains the primary reviewer for both lanes. Any further
    candidate screening (e.g. a V3 lineage with a different model) requires a
    separate explicit owner authorization.

## Failure character (evidence, not tuning)

83/227 dual-pass rows carry at least one error kind. Dominant patterns:
evidence-span invalidity concentrated in the critical lane (74 invalid-span
passes across A/B against 46 evidence-invalid rows after dedup), 69/80
critical INVALID_MODEL_REVIEW rows (model refuses/returns unusable reviews on
critical-lane content), and consensus that disagrees with the frozen reference
when it exists (10/132 forbidden, 9/31 critical). CORE rows dominate the
errors; critical EDGE agreement is also below the 0.92 contract minimum.
These numbers are reported as burned qualification evidence only.

Hard stop respected: no router activation, no gate changes, no historical
mutation, no fresh holdout, no SUT changes.
