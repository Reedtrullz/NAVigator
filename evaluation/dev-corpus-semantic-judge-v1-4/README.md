# Dev Corpus Semantic Judge V1.4 — Boundary Agreement Repair

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_4-BOUNDARY-AGREEMENT-REPAIR

**Terminal status: DEV_CORPUS_SEMANTIC_JUDGE_V1_4_NOT_READY** (2026-09-11)

## What this task did

1. Repaired the agreement metric: free-text notes are excluded; score-bearing fields are compared per-field (route: proposition/commitment/verdict; uncertainty: mode/behavior/verdict), with mechanical zero-gates and derivation checks.
2. Validated the contract on human Calibration A (N=40, all agreements 1.0, no clarification needed; Calibration B therefore not required).
3. Built 100 fresh official fixtures (25/25/25/25) with a mechanical burned-text collision scan (0 collisions), corrected 5 evidence-span transcription slips + 1 fixture typo before gold freeze, and froze gold from dual blind human passes that agreed at 1.0 on every score-bearing field.
4. Ran the frozen mimo-v2.5 judge one-shot on all 100 fixtures (max_tokens 32768, temperature 0, no substantive reruns).

## Why NOT_READY

The model failed the >=0.95 hard gates: overall 0.8265, critical 0.8696 (1 FN), forbidden 0.92, route 0.76, uncertainty 0.76. Stability stage was preempted. The measurement system (contract + gold) is now demonstrably clean; the residual error is attributable to the model. Details: final-report.md (76 items).

## Artifact map

- TASK-LOCK.json — task scope, policies, terminal status
- baseline-integrity.json — 29 historical + 14 V1.3M artifact SHA verification (PASS)
- burned-data-registry.json — V1.3M Set A + V1.2 official 80 burned
- v1-3m-mechanical-reanalysis.json — historical Set A rescore under V1.4 definition (diagnostic only)
- agreement-contract.md, route-commitment-contract-v1-4.md, uncertainty-contract-v1-4.md, boundary-decision-trees.md — frozen contract documents
- boundary-calibration-a.json + calibration-a-label1/2 + calibration-a-agreement.json — human calibration (PASS 1.0)
- boundary-calibration-b.json / calibration-b-agreement.json — NOT CREATED: A passed at 1.0, B not required; never fabricated (spec deliverable recorded as N/A)
- semantic-judge-contract-v1-4.json + semantic-judge-result-v1-4.schema.json — frozen contract/schema
- model-config-v1-4.json — frozen judge config incl. official fixture/gold SHAs
- model-calibration.json + model-calibration-iter2/iter3 — burned model development (iter3 frozen at 22/24)
- official-validation-fixtures.json — 100 fresh fixtures (SHA registered pre-run)
- human-label-pass1/2.json + annotation-agreement.json — dual human gold gate (PASS 1.0)
- official-validation-gold.json — FROZEN gold (scoring contract + 40x5 stability preregistration)
- official-validation-results.json — one-shot model results + per-call telemetry
- transport-report.json, token-usage-report.json — capacity analysis
- semantic-judge-manifest-v1-4.json — SHAs of all frozen artifacts
- final-report.md — 76-item SLUTTRAPPORT

## Hard boundaries honored

No historical edits, no corpus/runtime changes, no full SUT run, no Phase B, no product holdout, no threshold derivation, no post-hoc token-budget changes, no GPT-5.5/GPT-5.6-Luna as judge. Secrets used at runtime only, never printed or persisted. The frozen V1.4 gold is reusable only as a sealed reference for future judge-lineage tasks.
