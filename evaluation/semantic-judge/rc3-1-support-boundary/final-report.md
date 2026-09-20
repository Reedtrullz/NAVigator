# RC3.1 Auto-Support Boundary Repair - Final Report

Task ID: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR
Dates: 2026-09-05 to 2026-09-06
Subagents: 0 used (budget 2; GPT-5.6-Luna policy honored, no GPT-5.5)

# Section 62 report items

1. Task ID: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR.
2. Prior status: RC3_1_PROOF_NOT_READY (from NAV-EXPLORE-RC3_1-PROOF-SEMANTICS-REPAIR).
3. Historical artifacts unchanged: verified (source-integrity-report.md; RC3G, RC3.1 corpus, RC2 official artifacts all MATCH/RECORDED).
4. Validation seal unchanged: SHA-256 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159, identical before and after.
5. Validation accessed: NO. Never decrypted, inspected, or executed against.
6. Runtime compile gate: PASS (py_compile on all runtime files).
7. Runtime import gate: PASS (actual import of the target engine file, path logged in every run).
8. Control-character scan: PASS (0 backspace/NUL/unexpected C0 hits).
9. Test harness engine path: /Users/reidar/Projectos/NAV Explore/evaluation/semantic-judge/rc3-1-proof-semantics/rc3_1_engine/engine.py.
10. Test harness engine SHA-256: c4bc71862febf51783e2e48550f899746f9a6d0cb00f03a84d084edcd8fdce37.
11. Boundary contract SHA-256: 794c9788b88f04eb88594b6f8a86be6649d607feaf69f3bf0e5ab8e8682fb71c.
12. Boundary metric SHA-256: 9c6ccbcd5870d82ede809fe9fa0b6fa4fd73a0bd7a85bd737dba0a751b44fe23.
13. Boundary dimensions: polarity, modality, actor, temporal, locality/organizational scope, condition, exception, numeric_quantity, clause_coverage (9 dimensions, per-dimension MATCH / LICENSED_ENTAILMENT / MISMATCH / UNKNOWN / NOT_APPLICABLE).
14. AUTO_SUPPORTED eligibility rule: the source proposition must entail the claim proposition and all ten contract conditions must hold simultaneously (contract section 3); any failing dimension forbids auto.
15. UNKNOWN handling: UNKNOWN or UNRESOLVED on any relevant dimension blocks AUTO_SUPPORTED (fail closed, returns an explicit non-auto proof state).
16. Modality table summary: directional source-to-claim table. REQUIRED->PERMITTED licensed; PERMITTED->REQUIRED not entailment; CONDITIONAL_ENTITLEMENT->ENTITLED requires condition binding; NOT_REQUIRED->REQUIRED same proposition is contradiction; PROHIBITED->REQUIRED/PERMITTED mismatch; DEFAULT_RULE->REQUIRED unknown unless explicitly binding. This task corrected PERMITTED->CONDITIONAL_ENTITLEMENT to LICENSED_ENTAILMENT and DISCRETIONARY->PERMITTED to MISMATCH.
17. Negation binding model: negation binds to the predicate/clause it governs; exact-token probes (substring bug fixed); an aligned span that ignores a governing negation yields polarity MISMATCH.
18. Condition binding model: a claim that drops a required source condition is MISMATCH. Condition-floor asymmetry: an evidence-side condition against a conditionless claim mismatches only when the claim is REQUIRED/ENTITLED or the evidence carries a bare/kun restriction; otherwise UNKNOWN (fail closed, preserves licensed condition inheritance).
19. Exception binding model: an applicable source exception whose situation the claim falls inside blocks the proof (MISMATCH); irrelevant exceptions are NOT_APPLICABLE. Applicable exceptions can never be discarded for auto.
20. Actor/scope model: exact actor or documented compatible relation; Norwegian definite-form suffix matching (e.g. fastlegen vs helsestasjonen mismatch); generic-population directionality (claim 'barn' matches evidence 'barn_u18', reverse is UNKNOWN). Locality scope must agree or be licensed.
21. Clause coverage model: a lexical hit is insufficient when a later qualifier, negation, condition, or exception inside the same governing structure changes modality, polarity, or applicability; unresolvable governing structure yields UNKNOWN and fail-closes. Regex use is documented and fail-closed (contract section 6).
22. Fresh boundary suite N: 80 cases.
23. Compatible cases: 37.
24. Incompatible cases: 35.
25. Unresolved cases: 8.
26. Negation cases: 20.
27. Modality cases: 20.
28. Condition/exception cases: 15.
29. Actor/scope cases: 15.
30. Other qualifier cases: 10 (temporal/local/numeric).
31. Baseline FALSE_AUTO_SUPPORT_BOUNDARY: 27.
32. Baseline support_boundary_precision: 0.5345.
33. Baseline entailed_support_recall: 0.7949.
34. Implementation summary: boundary.py implements proposition extraction and nine-dimension comparison; engine.py enforces fail-closed support eligibility (eligible only when atom verdict is ENTAILS and boundary overall is BOUNDARY_COMPATIBLE); modality-boundary-table.json freezes the directional modality relations.
35. Bounded bugfix used: YES (one pass, generalized fixes only per spec section 29; see README Key decisions).
36. Final FALSE_AUTO_SUPPORT_BOUNDARY: 0.
37. Final support_boundary_precision: 1.0.
38. Critical support precision: 1.0.
39. Final entailed_support_recall: 0.9730.
40. Negation boundary accuracy: 1.0.
41. Modality boundary accuracy: 0.95.
42. Condition/exception accuracy: 1.0.
43. Actor/scope accuracy: 1.0.
44. Semantically unsound eligible support proofs: 0 (fresh suite and burned train, product-level count).
45. Determinism: 100% (byte-identical double runs on both days; quote-aligner 5-run determinism also clean).
46. Boundary gates passed: FALSE_AUTO_SUPPORT_BOUNDARY=0; support precision 1.0 >= 0.99; critical precision 1.0; entailed recall 0.9730 >= 0.85; negation 1.0; modality 0.95; condition/exception 1.0; actor/scope 1.0; unsound eligible = 0; determinism 100%.
47. Boundary gates failed: none.
48. Burned TRAIN relation accuracy: 0.5161 (64/124). Down from 0.8468 because the fail-closed boundary moves previously-entailed predictions into explicit non-auto states; recorded as accepted accuracy cost, not a proof-safety regression (train-comparison.json).
49. Burned TRAIN unsound count: 0 (product-level definition; baseline 25 was atom-level and is not directly comparable).
50. Burned TRAIN negation: not computed at train subgroup level in this task; fresh-suite negation accuracy is 1.0.
51. Overall proof-dev gates pass: NO (relation accuracy 0.5161 < 0.95 per spec section 32).
52. RC2 regression: 37/37 PASS.
53. Tier-1: PASS (conflicts=0, new_invalid_proofs=[], critical_auto_errors_after=[]).
54. Tier-1 operators: 43/43 PASS.
55. Operator regression: 23/23 PASS.
56. RC3 development tests: 24 passed.
57. Quote-aligner: 0 regressions (7 pre-existing residuals unchanged); determinism clean; id guard 0 violations.
58. KB: 48/48 BESTATT, 0 DELVIS, 0 FEILET.
59. Runtime robustness: engine probes ALL PASS.
60. id_guard: 0 runtime hits (RC1B / RC2B / RC3G / RC31- case literals; docs/test provenance references only).
61. Candidate boundary frozen: YES (candidate-boundary/, status BOUNDARY_CANDIDATE_FROZEN, per spec section 39).
62. Candidate manifest SHA-256: see candidate-boundary/hashes.txt (recorded at freeze).
63. STATUS: BOUNDARY_REPAIR_PASS_PROOF_NOT_READY.
64. Should sealed validation be opened next? NO. Remaining relation classes must be repaired first (spec section 32); validation stays sealed.
65. Remaining proof weaknesses: burned-train relation accuracy 0.5161 driven by fail-closed routing of previously-entailed classes; modality coverage miss RC31-BDY-0033 (coverage-mid compatibility); temporal proper-noun miss RC31-BDY-0077; condition-floor UNKNOWN band could over-block some train relation classes; temporal/local/numeric subgroup at 0.90 (not a gate).
66. Recommended next step: a relation-class repair task (generalized, no case-ID rules) to lift relation accuracy to >= 0.95 with unsound = 0 and decomposition gate still passing, without opening the sealed validation; only then schedule the sealed 60-case validation run in a separate task.

# Gate summary

BOUNDARY_REPAIR_STATUS: PASS.
OVERALL_PROOF_READINESS: NOT READY.
Final status (exactly one, per spec section 41): BOUNDARY_REPAIR_PASS_PROOF_NOT_READY.

No new blind set was built, no certification was run, no routing or reviewer tuning occurred, and the sealed validation was not opened.
