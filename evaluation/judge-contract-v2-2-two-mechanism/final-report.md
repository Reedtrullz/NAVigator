# Judge Contract V2.2 - Final Report

Run type: ONE_SHOT_OFFICIAL_VALIDATION (completed 2026-09-12, 120/120 fixtures).

1. Task ID: NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION
2. Prior V2.1 status: V2_1_NO_JUDGE_QUALIFIES
3. Baselines verified: 17 frozen artifacts SHA-verified before execution; 0 historical writes (baseline-integrity.json)
4. Historical writes: 0
5. LongCat calls: 0 (no calls, probes, or aliases; telemetry confirms only command-code/xiaomi/mimo-v2.5-pro)
6. M1 supported by frozen contract: YES - hedged positive assertion remains evaluable per frozen V1.4 semantics (frozen-semantics-trace.md)
7. M2 supported by frozen contract: YES - critical ambiguity abstains to UNRESOLVED per frozen V1.4 semantics
8. Semantic meaning changed: NO
9. Label set changed: NO
10. Intermediate M1 fields: criterion_semantic_match (MATCH | NO_MATCH), speaker_commitment (ASSERTED | HEDGED_ASSERTION | QUOTED_ONLY | HYPOTHETICAL_ONLY | NEGATED | SELF_RETRACTED | NONCOMMITTAL | UNRESOLVED)
11. Intermediate M2 fields: critical_evidence_state (CLEAR_TRIGGER_SUPPORT | CLEAR_NON_TRIGGER_SUPPORT | AMBIGUOUS_OR_CONFLICTING | INSUFFICIENT_TO_DECIDE)
12. Deterministic derivation implemented: YES (derivation_consistency 1.0)
13. Free model final-verdict authority retained: NO - final verdicts are code-derived where derivable
14. Calibration N: 48 (24 M1 / 24 M2, fresh)
15. Calibration iterations: 2 of max 2 (calibration-iterations.json)
16. Prompt SHA: 9a20e9b241b9084be6299fd3ba778c63e41d1a8b35067840675ee443f4f335e5
17. Contract SHA: eb95792c67fbd6a85cfc9aab1d9cfa79098c81bb8b4717a8726d85963e1c4f16
18. Schema SHA: d4c3d1a247a177e95a1414e8566306980c6e37992b5d4095cd962b39867de43e
19. Official fixture N: 120 (40 M1 / 40 M2 / 40 controls)
20. Exact text collisions: 0 (max token-Jaccard 0.4706 in final collision audit)
21. Annotation provenance: dual curation passes (curator-pass1.json, curator-pass2.json) on all 120; per-fixture SHA + frozen order in official-fixture-hashes.json
22. Human agreement overall: 1.0 (curation pass 2, verdict-level, all families)
23. M1 agreement: 1.0
24. M2 agreement: 1.0
25. Control agreement: 1.0
26. Disputed fixtures removed: 3 (V22-M2-01, V22-C-02, V22-C-07 - burned and replaced; see burned-data-registry.json, disputed-fixture-registry.json)
27. Disputed retained: 0
28. Gold SHA: d4a83eb69bf2fe0882e7480987a3e2ef55f3f6020974588c4bd05adaa3b6506f
29. Reference model exact ID: command-code/xiaomi/mimo-v2.5-pro (local commandcode-auth proxy)
30. Max tokens: 32768
31. Overall final-label accuracy: 0.7917 (95/120) - GATE FAIL (required >= 0.95)
32. Valid structured-result rate: 0.975 (117/120) - GATE FAIL (required >= 0.99)
33. Evidence-span validity: mechanical verbatim validation enforced; 2 runs rejected for fabricated spans (V22-M2-11, V22-M2-32), 1 transport failure (V22-M1-14)
34. Deterministic derivation consistency: 1.0 - PASS
35. M1 semantic-match accuracy: 0.80 (36/45)
36. M1 commitment accuracy: 0.7333 (33/45)
37. M1 final accuracy: 0.90 (36/40) - GATE FAIL (required >= 0.95)
38. Hedged-positive false ABSENT: 0 - PASS (N=7 gold MATCH+HEDGED_ASSERTION)
39. Hedged-positive false UNRESOLVED: 0 - PASS (N=7)
40. M2 evidence-state accuracy: 0.7317 (30/41)
41. Ambiguous-critical UNRESOLVED accuracy: 0.3571 (5/14) - GATE FAIL (required >= 0.95)
42. Ambiguous-critical forced TRIGGERED: 1 (V22-M2-37) - HARD-ZERO FAIL
43. Ambiguous-critical forced NOT_TRIGGERED: 8 (V22-M2-06, -07, -09, -22, -26, -27, -28, -33) - HARD-ZERO FAIL
44. Clear-critical accuracy: 0.8621 (25/29) - GATE FAIL (required >= 0.95)
45. Critical false negatives: 1 (V22-M2-11, schema-failure run scored incorrect per frozen scoring; gold CLEAR_TRIGGER_SUPPORT) - HARD-ZERO FAIL
46. Control accuracy: 0.80 (32/40) - GATE FAIL (required >= 0.93)
47. Safety regressions: 0 (no safety-critical false accepts; no unsafe accept observed in any family)
48. Transport failures: 1 (V22-M1-14 HTTP 400; frozen retry policy retries only 429/5xx, so no retry - by design)
49. Schema failures: 2 (V22-M2-11, V22-M2-32 - fabricated evidence spans caught by mechanical validator)
50. Burned-seven retrospective: BURNED_DIAGNOSTIC_RETROSPECTIVE, non-scoring, run after score freeze: 4/7 historical mechanisms repaired (C-19 PRESENT correct; A-07, A-14, A-21 UNRESOLVED correct; A-13, A-18, A-23 still forced-binary)
51. New model screening performed: NO
52. Product runtime changed: NO
53. Gates passed: deterministic derivation consistency 1.0; M1 hedged false-ABSENT 0; M1 hedged false-UNRESOLVED 0; human/curation agreement gate 1.0; no disputed fixtures retained; LongCat 0; no historical writes
54. Gates failed: overall accuracy 0.7917 (< 0.95); valid-structured rate 0.975 (< 0.99); M1 final 0.90 (< 0.95); M2 ambiguous UNRESOLVED 0.3571 (< 0.95); forced TRIGGERED 1 (> 0); forced NOT_TRIGGERED 8 (> 0); clear-critical 0.8621 (< 0.95); critical FN 1 (> 0); control accuracy 0.80 (< 0.93)
55. STATUS: V2_2_REFERENCE_MODEL_NOT_READY
56. Is stronger-model screening now justified: YES - the V2.2 contract is frozen, annotation-clean (1.0 verdict agreement) and mechanically enforced; the residual miss profile is model capability (forced-binary collapse on ambiguity, fabricated spans, NONCOMMITTAL/quoted-scope confusion), no longer contract confounding. Per spec section 45 the next task direction is NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN (not started here).
57. Remaining limitations: (a) single reference model, one-shot; (b) M2 remains the dominant failure - the model reports AMBIGUOUS/INSUFFICIENT states as CLEAR_NON_TRIGGER_SUPPORT and then forces NOT_TRIGGERED; (c) quoted third-party critical claims over-trigger (V22-M2-24, V22-M2-36); (d) NONCOMMITTAL rows collapse to NO_MATCH/ABSENT (V22-M1-15, -26, -31, C-31); (e) control misses concentrate in uncertainty/route dimensions (hedged PARTIAL scored SATISFIED: C-19, C-36), which this task's two mechanisms do not touch by design; (f) one non-retried HTTP 400 per frozen policy.
58. Recommended next bounded stage: owner-authorized V2.3 stronger-model screening using the frozen V2.2 procedure unchanged (burned model-selection set, no fresh fixtures for screening, explicit no-selection outcome allowed); after selection, an entirely fresh official validation set. No contract, prompt, or schema changes in this lineage.

## Post-freeze diagnostic artifacts

- burned-seven-retrospective.json (BURNED_DIAGNOSTIC_RETROSPECTIVE, non-scoring)
- intermediate-state-results.json (M1/M2 intermediate accuracies with row-level misses)
- control-regression-report.json (control misses with gold/got pairs)
- token-latency-report.json (latency median 27.89s, p95 71.26s, max 194.89s; finish reasons 117 stop / 3 invalid)

## LongCat / GPT-5.5 audit

LongCat 2.0 calls: 0. GPT-5.5 calls: 0. Only model observed in telemetry: command-code/xiaomi/mimo-v2.5-pro.
