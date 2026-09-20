# V1.6A.1 Final Report

## Terminal status

**`V1_6A1_TARGETED_CONFIRMATION_NOT_READY`**

The generalized out-of-inventory abstain repair is implemented and passes the
full unit suite and all burned-120 regression gates, but the fresh 60-fixture
targeted confirmation failed the overall/route precision gate (0.9677 < 0.99).
Per spec sections 21/27/32 the candidate is NOT frozen and no manifest is
created. No reruns, no post-execution rule edits, no tuning.

## Report

1. Task ID: `NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A1-ABSTAIN-REPAIR`
2. Prior V1.6A status: `V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY` (preserved)
3. Baseline integrity: 10/10 V1.6A artifacts SHA-verified (`baseline-integrity.json`)
4. Historical writes: 0
5. V1.6A gold SHA: `71c0b7fa01b17fb9cce21de272ffc56d3d26a17f2d05a0bd73fe4243bac3e1af` (prefix match `71c0b7fa`)
6. V1.6A 120 classified as burned: YES (`BURNED_PRECLASSIFIER_DEVELOPMENT_DATA`)
7. Annotation provenance correction preserved: YES — `INTRA_ANNOTATOR_REPEATABILITY = 1.0`, never labeled independent inter-annotator agreement (`historical-deviations.md`)
8. Historical execution-order deviation preserved: YES (official-run-before-gold incident retained)
9. Root cause reproduced: YES (`root-cause-reproduction.json`)
10. Historical failing rule: `BC_ROUTE_VAGUE_01` (only route rule firing without inventory grounding)
11. Repair hypothesis: frozen pre-implementation in `repair-hypothesis.md` — no deterministic route classification from vague constructions when the service noun cannot be grounded in the recognized inventory or another frozen high-precision rule
12. Case-specific fix: NO — generic rule only; no fixture IDs, no sentence matching, no municipality/NAV-specific logic, no model fallback
13. New TDD fixture: `FIX-ABSTAIN-01` (`Gjeldssenteret kan kanskje hjelpe deg med budsjett.` — not text-identical to VR-H-08)
14. RED observed: YES — 69/72 pass, 3 fail (`FIX-ABSTAIN-01`, `FIX-CE-03`, `FIX-CE-04`) against the byte-identical frozen V1.6A engine (`tdd-red-result.json`)
15. Counterexample tests N: 4 (`FIX-CE-01..04`)
16. Implementation delta: + `SERVICE_NOUN_STEMS`; + `_unknown_service_nouns()` (stem words not covered by any `ROUTE_TERMS` hit); + `BC_ROUTE_UNKNOWN_SERVICE_01` priority 25 firing `ABSTAIN_CONFLICT`; quoted/hypothetical guards extended to `route or unknown`
17. Existing unit tests: 67
18. New unit tests: 5
19. Total unit pass: 72/72 GREEN
20. VR-H-08 new result: `ABSTAIN` via `BC_ROUTE_UNKNOWN_SERVICE_01` (`ABSTAIN_CONFLICT`; conflicting lower-priority `BC_ROUTE_VAGUE_01` recorded)
21. Burned overall precision: 1.0 (108 non-abstain, 0 false) — was 0.9908
22. Burned route precision: 1.0 (44 non-abstain, 0 false) — was 0.9778; coverage 0.88 (was 0.90, accepted drop per spec section 12)
23. Burned uncertainty precision: 1.0 (unchanged)
24. Burned critical/scope precision: 1.0 (unchanged)
25. Burned false deterministic N: 0 (was 1)
26. Burned safety-critical false deterministic N: 0
27. Fresh targeted fixtures N: 60
28. Recognized-service N: 20
29. Out-of-inventory N: 20
30. Adversarial N: 20
31. Fixture SHA: see `targeted-fixture-hashes.json` (per-fixture + file SHA frozen before execution; engine SHA at freeze `40d85f317383…` recorded there in full)
32. Annotation provenance: `INTRA_ANNOTATOR_REPEATABILITY` (dual-pass, single curator; disclosed)
33. Fresh non-ABSTAIN N: 31
34. Fresh overall precision: **0.9677 — FAIL** (gate >= 0.99); single error `ADV-11`
35. Fresh route precision: **0.9677 — FAIL** (gate >= 0.99)
36. Out-of-inventory false deterministic N: **0** (spec section 24 gate PASSES)
37. Safety-critical false deterministic N: 0
38. Evidence-span validity: 100%
39. Fresh overall coverage: 0.5167 (secondary metric; no tuning performed)
40. Recognized-service coverage: 0.80
41. Out-of-inventory coverage: 0.40 (all 8 non-abstains are the independently grounded quote/hypothetical paths)
42. Adversarial coverage: 0.35
43. Preclassifier frozen: NO
44. Manifest SHA: NOT_CREATED (section 27 freeze conditions not met)
45. Semantic judge calls: 0
46. V1.6B run: NO
47. Runtime changed: NO
48. Product SUT run: NO
49. Gates passed: baseline integrity; root-cause reproduction; RED-first; 72/72 unit; all burned-120 gates (overall/route/family >= 0.98, 0 false deterministic, VR-H-08 abstains); fresh evidence-span validity 100%; fresh out-of-inventory false deterministic 0; fresh safety-critical 0
50. Gates failed: fresh overall non-ABSTAIN precision 0.9677 < 0.99; fresh route-family precision 0.9677 < 0.99 (single false deterministic `ADV-11`: engine emitted `ASSERTED` for a text whose known-route sentence resolves while the unknown-noun sentence does not; frozen gold `ABSTAIN`)
51. STATUS: `V1_6A1_TARGETED_CONFIRMATION_NOT_READY`
52. Recommended next bounded stage: separate repair task (suggested id `…V1_6A2-ROUTE-GROUNDING-REPAIR`) generalizing clause-level route grounding: assertion/retraction/negation rules currently fire from any inventory hit in the text even when the clause carrying the service noun is ungrounded. Also enforce the section 20 replacement policy for fixtures that a pre-execution QA pass leaves disputed (the `ADV-11` dispute was resolved instead of replaced — process error disclosed in `gold-qa-pass.json`). V1.6B re-screen remains blocked until a targeted confirmation passes.

## Diagnostics (non-blocking, marked burned)

- `burned-v1-4-counterfactual.json` — `BURNED_COUNTERFACTUAL_DIAGNOSTIC`; route coverage 0.40 -> 0.44, uncertainty 1.0 unchanged, boundary resolution 70% -> 72%
- `judge-call-reduction-estimate.json` — `BURNED_DIAGNOSTIC_ONLY`; estimated overall judge-call reduction 35% -> 36%
- 4 abstain-direction disagreements (`REC-V-02..04`, `ADV-08`): engine more conservative than gold; reported, not tuned

STOP. No model re-screen. No semantic judge calls. No product runtime. No full SUT. No fresh product holdout.
