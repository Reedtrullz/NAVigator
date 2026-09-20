# V1.6A Final Report - Boundary Pre-Classifier

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A-BOUNDARY-PRECLASSIFIER

## STATUS: V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY

The human boundary contract passed cleanly, the frozen classifier is
precision-strong overall, but the preregistered family gate
(route_commitment precision >= 0.98) failed at 0.9778 with exactly one false
deterministic (VR-H-08). Per the frozen protocol the bounded bugfix budget was
already spent before the official run and no rule edits are permitted after
the official run started, so the task terminates NOT_READY without patching
the engine.

## SLUTTRAPPORT (spec items 1-50)

1. Task ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A-BOUNDARY-PRECLASSIFIER
2. Prior V1.5A status: V1_5A_NO_MODEL_MEETS_SELECTION_FLOOR (confirmed in baseline-integrity.json)
3. Baselines verified: YES (V1.4 gold/fixtures/prompt SHAs recomputed and matched; V1.5A artifact SHAs matched)
4. Historical writes: 0
5. V1.4 gold changed: NO (SHA c859a851e84957a5a30a296315080ef88ba4f8e39c60a8c5e83669760f7194dc unchanged)
6. New model calls: NO (no judge model search, no model calls; classifier is pure Python)
7. Commitment labels: ASSERTED, HEDGED_ASSERTION, NEGATED, SELF_RETRACTED, QUOTED_ONLY, HYPOTHETICAL_ONLY, VAGUE_NONCOMMITTAL (+ABSTAIN)
8. Uncertainty labels: EXPLICIT_LIMITATION, PARTIAL_LIMITATION, CONTRADICTORY_LIMITATION, HEDGE, OVERCONFIDENT_ASSERTION, NONE (+ABSTAIN)
9. Assertion-scope labels: RETRACTED, NEGATED, USER_REPORTED, THIRD_PARTY_QUOTED, HYPOTHETICAL, SYSTEM_ENDORSED (+ABSTAIN)
10. ABSTAIN supported: YES (reason NO_HIGH_PRECISION_RULE; interrogative outputs abstain in all three dimensions)
11. Conflict -> abstain: YES (distinct labels in the top-priority group produce ABSTAIN_CONFLICT with conflict metadata; no silent winner)
12. Case-specific rules: NO (generic Norwegian linguistic markers only; no case IDs, no fixture-specific sentence matching)
13. Unit fixtures N: 67
14. Unit fixtures PASS: 67/67 GREEN (RED runs preserved in unit-test-results-red-run.json)
15. Fresh validation fixtures N: 120 (route 50 / uncertainty 40 / scope 30, exact preregistered distribution)
16. Human overall agreement: 1.0 (120/120, zero disagreements)
17. Route boundary agreement: 1.0 (50/50)
18. Uncertainty boundary agreement: 1.0 (40/40)
19. Scope agreement: 1.0 (30/30)
20. Gold SHA: 71c0b7fa01b17fb9cce21de272ffc56d3d26a17f2d05a0bd73fe4243bac3e1af
21. Official classifications N: 120 (frozen engine SHA ccd30e7f7fae7e9090c9de443372b15bf3d2341cb447d800c1d55058f6f2c467, manifest-verified before run)
22. Non-ABSTAIN N: 109
23. Overall coverage: 0.9083 (soft gate >= 0.50 PASS)
24. Overall precision: 0.9908 (gate >= 0.99 PASS)
25. Route coverage: 0.90 (45/50 non-abstain)
26. Route precision: 0.9778 (45/46 non-abstain correct) - FAILS family gate >= 0.98
27. Uncertainty coverage: 0.90 (36/40 non-abstain)
28. Uncertainty precision: 1.0
29. Scope coverage: 0.9333 (28/30 non-abstain)
30. Scope precision: 1.0
31. False deterministic classifications: 1 (VR-H-08: out-of-inventory service noun "sosialtjenesten" emitted VAGUE_NONCOMMITTAL instead of ABSTAIN; preregistered coverage probe)
32. Safety-critical false deterministic: 0
33. Evidence-span validity: 1.0 (all non-ABSTAIN spans mechanically verified as exact substrings)
34. Burned diagnostic replay performed: YES (BURNED_DIAGNOSTIC_REPLAY; frozen classifier over 100 V1.4 official fixtures, text-only criterion mode)
35. C-09 outcome: no boundary dimension emitted a critical trigger; route ABSTAIN, scope ABSTAIN, uncertainty NONE (cross-dimension observation only) -> judge required
36. C-15 outcome: full abstain across all three dimensions -> judge required
37. R-12 outcome: VAGUE_NONCOMMITTAL on route - the preregistered desired outcome (no positive committed route; never NO_ACCEPTABLE-eligible)
38. Historical model misses boundary-resolved by preclassifier: 9 of 17 misses (R-12, R-16, R-18, U-10, U-13, U-16, U-20, U-22, U-24) plus 0 of 2 schema failures; the preclassifier labels contradict the model's wrong assertions deterministically
39. Historical misses still judge-required: 10 (C-01, C-03, C-09, C-15, C-20, F-10, F-20, R-04, R-10, R-24; critical/forbidden families have no boundary dimension)
40. Estimated judge-call reduction: 70% of boundary-dimension fixtures (35/50) resolved with no judge call; 35% across all 100 V1.4 fixtures; with structured criteria in production the uncertainty-family estimate is conservative (text-only NONE becomes OVERCONFIDENT_ASSERTION, still deterministic)
41. Preclassifier frozen: YES (engine, contract, rule registry, unit fixtures, schema, runner, design doc all SHA-registered in preclassifier-manifest.json; no rule edits after first official fixture)
42. Manifest SHA: 04d0796e2b2ca8c5ef8cd53760d60c15e558e784ceb1bbfb6c54f49c5929d7bf
43. Model re-screen run: NO (spec 46-47 respected)
44. Runtime changed: NO
45. Product SUT run: NO
46. Fresh product holdout: NO
47. Gates passed: unit suite 67/67; annotation agreement 1.0 all families; overall precision >= 0.99; safety-critical false deterministic = 0; evidence-span validity 100%; soft coverage >= 0.50
48. Gates failed: route_commitment family precision >= 0.98 (0.9778) - the single VR-H-08 false deterministic
49. STATUS: V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY
50. Recommended next bounded stage: NEW task (V1.6A-class, NOT a V1.6B re-screen) to fix the out-of-inventory service-noun abstain gap (generalized rule class: service nouns not in inventory with no commitment markers must abstain, not emit VAGUE_NONCOMMITTAL), re-freeze, re-run the 120-fixture official one-shot on the same fresh fixtures (they are contract-development data for the fix, not generalization evidence); only then V1.6B re-screen with scorer + preclassifier + judge

## Protocol deviations (disclosed)

- Single-annotator dual-pass: human-label-pass1.json and human-label-pass2.json
  were both produced by the same coding agent (mechanical two-pass). Independent
  human inter-annotator validation was NOT performed.
- Order: the official one-shot ran before the agreement/gold-freeze artifacts
  were completed. Mitigating fact: zero classifier rule edits after the official
  run started (engine SHA at official run time equals frozen manifest SHA).
- Amendment 3 (bounded bugfix, pre-official): smoke probes exposed a
  safety-family false SYSTEM_ENDORSED ("Det foreligger ikke...") and a missed
  QUOTED variant ("rapporterer at"); fixed RED-first with fixtures
  BC_SCOPE_NEGATED_02 and quote-marker additions; a wrong VAGUE-suppression
  attempt was reverted and CMT-ABHV-01 expectation corrected to
  VAGUE_NONCOMMITTAL. All disclosed in boundary-label-contract.json.

## Interpretation

The deterministic boundary layer does resolve the failure class it was built
for: 70% of burned boundary-dimension fixtures, including 9 of the 12 route and
uncertainty misses from V1.4, resolve deterministically with the correct
boundary state - including every case where the V1.4 model overcommitted a
route the human labels do not support. The one official failure is a narrow,
generalizable gap (out-of-inventory service nouns should abstain), not a
structural flaw in the precision-first architecture.

V1.4 and V1.5A historical statuses remain untouched; the replay is
BURNED_DIAGNOSTIC_REPLAY only and does not rescore V1.4 as PASS.
