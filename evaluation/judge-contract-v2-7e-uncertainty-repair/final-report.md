# Judge Contract V2.7E - Final Report

Task: NAV-EXPLORE-JUDGE-CONTRACT-V2_7E-UNCERTAINTY-CONTRACT-REPAIR
Authoritative spec: evaluation/judge-contract-v2-7e-draft/TASK-SPEC-DRAFT.md (sha256 e755140ec9d1dfb119180b9d55428934dfc74fa4727dfb95ba332efd182c5eab, re-verified pre-execution)
Owner authorization: explicit, in-thread 2026-09-13.

## 1. Prerequisites and integrity

1. Prerequisite pins verified: 15/15 (9 baseline + 6 V2.7D lineage), SHA-256 match, baseline-integrity.json
2. V2.7E draft artifacts re-verified: 7/7 (spec, contract, decision tree, derivation module, Set A draft, generator, gate evaluator), drift-free
3. Historical writes: 0 (V2.7, V2.7D, and all prior lineages untouched; V2.7D remains V2_7D_CONTRACT_REPAIR_REQUIRED)
4. Stale historical TASK-LOCKs (v1-3, v2-subskill): NOT touched, per authorization scope
5. Model calls: 0 (SEMANTIC_JUDGE_CALLS = 0; LongCat calls = 0; no GPT-5.5)
6. Subagents used: 0

## 2. Repair execution

7. Repair scope honored: exactly UNC-A1 and UNC-A2; no other semantic boundary changed
8. Mechanical diff vs V1.4 uncertainty_model: 1 changed table cell (EXPLICIT_LIMITATION x CONTRADICTORY_LIMITATION PARTIAL -> UNRESOLVED), UNCLEAR_PROSE added (behavior + 2 table rows + definition), documentation strings; all other cells identical
9. Score labels changed: NO (SATISFIED / PARTIAL / VIOLATED / NOT_REQUIRED / UNRESOLVED preserved)
10. Route/forbidden/M2/deterministic-boundary/product runtime changed: NO
11. Frozen contract sha256: 7648039ea570
12. Frozen decision tree sha256: b027dfa56f97
13. Frozen derivation module sha256: 5d5ee2ae00b9
14. Frozen module selfcheck: PASS (UNC-A1 + UNC-A2 active, all other V1.4 cells preserved)

## 3. Calibration

15. Set A: 32 fresh fixtures, 9 preregistered tag classes, frozen from verified draft without regeneration (calibration-set-a.json sha256 4acf2556496b)
16. Collision audit: 0 exact-text collisions vs 75 historical JSON blobs across dev-corpus-v1, v1-4, v2-7, v2-7d (collision-audit.json)
17. Annotation provenance: INTRA_ANNOTATOR_REPEATABILITY, two blind stance-controlled passes (table-first sequential; semantics-first reverse), no expected labels/tags consulted, passes independent
18. Pass 1 labels: 32; Pass 2 labels: 32
19. Raw agreement frozen pre-adjudication: 32/32 = 1.0000 (calibration-set-a-agreement.json sha256 dd51551623aa)
20. Gate overall >= 0.95: PASS (1.0)
21. Targeted zero-gates (contradictory/garbled-unclear/self-retracted): PASS (0 disagreements across all 10 boundary rows)
22. Boundary pair check: no disagreement on any row; no confusion pairs
23. Clarification pass used: NO (not needed; Set A passed)
24. Set B: NOT REQUIRED (Set A passed)
25. Adjudication: none required (zero disagreements; raw agreement is final)

## 4. Verdict derivation

26. Both passes derived verdicts through the frozen v2.7e derivation module (imported, not reimplemented)
27. UNC-A1 rows: all contradictory/self-retracted rows -> UNRESOLVED in both passes
28. UNC-A2 rows: all unclear-prose rows -> UNRESOLVED in both passes
29. NON_ASSERTION rows: absence of prohibited conclusion -> SATISFIED; asserted prohibited conclusion -> VIOLATED; no NON_ASSERTION_CONSTRAINT -> NOT_REQUIRED errors
30. PARTIAL rows: real incomplete qualifications -> PARTIAL in both passes
31. NONE-mode rows: NOT_REQUIRED in both passes

## 5. Terminal

32. Terminal status: V2_7E_CONTRACT_REPAIRED_AND_STABLE
33. Meaning: uncertainty contract boundary repaired and shown human-stable under the preregistered V2.7E calibration protocol. NOT judge selection, NOT model validation, NOT certification.
34. Judge screening: NOT started (requires separate owner authorization)
35. Next natural stage (NOT authorized, NOT started): new non-M2 judge screening under the repaired frozen contract, fresh fixture set, preregistered gates.
