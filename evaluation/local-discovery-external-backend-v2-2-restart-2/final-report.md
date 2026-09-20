# FINAL REPORT - V2.2 RESTART-2 EXTERNAL BACKEND SELECTION

Task ID: `NAV-EXPLORE-LOCAL-DISCOVERY-EXTERNAL-BACKEND-SELECTION-V2_2-RESTART-2`
Authoritative contract: `evaluation/local-discovery-external-backend-v2-2/backend-selection-contract-restart.md` (frozen, unmodified)

## Terminal status

`NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES`

## Gate 0

- Tavily: TESTABLE (authorized TAVILY_API_KEY in project-local `.env.local`, mode 0600; value never printed or persisted).
- Brave Search API: NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL.
- Protocol V1 SHA `fb533d99...f99ca` MATCH; candidate V2 `74329662...a678` MATCH; V2.1 snapshot 7/7 MATCH (verified 3x).
- Historical files modified: 0. Fresh municipalities used: 0. Accounts created: 0. Keys generated: 0.
- Single-credential rule applied per restart-2 contract; at least one testable candidate existed, so the frozen contract proceeded.

## Benchmark

- 117 burned queries (13 burned municipalities), exact frozen benchmark, 0.5 s interval, single attempt per query.
- Two preregistered modes: GENERAL (gate-bearing) and OFFICIAL_DOMAIN_CONSTRAINED (diagnostic only).

| Backend | Execution | Recall (gold domain) | Precision | Bot-block | Median latency |
|---|---|---|---|---|---|
| SITE_DIRECT_ONLY (frozen V2 artifact) | 1.000 | 1.000 | 0.9846 | 0 | 345 ms |
| TAVILY_SEARCH_API (GENERAL, gate mode) | 0.8718 (102/117) | 0.8034 (94/117) | 0.3596 | 0 | 1247 ms |
| TAVILY_SEARCH_API (CONSTRAINED, diagnostic) | 0.6410 | 0.6410 | 0.6410 | 0 | 1658 ms |

Tavily failed the two preregistered GENERAL-mode gates: execution 87.18% < 95% and recall 80.34% < 90%. Bot-block 0, false provider-failure -> NO_RESULTS 0, structured contract PASS (20/20 adapter tests), secret handling PASS (SECRET_LEAK_SCAN = 0 over 30 files).

## Structural finding

Incremental target recovery over site-direct = 0/117 in both modes. Site-direct already covers every municipality in the burned corpus (117/117), and every Tavily gold-domain hit is a strict subset of site-direct hits. The external fallback would add zero targets on this corpus even if its own gates had passed.

## Selection and freezes

- Eligible backends: none. Frozen selection rule applied unchanged (no threshold changes). No primary backend selected.
- V2.2 runtime integration: NOT_RUN_NO_ELIGIBLE_BACKEND (see burned-integration-results.json).
- Forced-fallback tests: NOT_RUN_NO_ELIGIBLE_BACKEND (see forced-fallback-results.json).
- candidate-runtime-v2-2 freeze: NOT executed (prerequisite failed). provider-config-v2-2.json remains frozen as benchmark-time config (SHA `376c2f3c...d594`), superseded by this outcome.
- Production lineage remains V2.1 (site-direct primary).

## Engineering quality

- Thin Tavily adapter: one root-cause fix applied after red-first tests (parser-before-classification ordering); suite 20/20 after fix.
- Combined regressions: 115/115 OK (V1 49, V2 27, V2.1 19, V2.2 20).
- Failure simulations: fail-closed, 0 false NO_RESULTS.
- Runtime failures during official benchmark: 0.

## Readiness and limitations

- Fresh generalization eval is NOT justified by this outcome: no eligible external backend and zero demonstrated incremental value.
- Limitations: backend quality is the binding constraint (execution + recall), not adapter correctness. The recall definition relies on municipality-domain gold matching for the burned corpus; this is documented in the frozen contract. Tavily re-evaluation is only warranted if the service measurably improves.

## Recommended next step

Choose one, in a NEW task: (a) accept the site-direct-only lineage and drop the external fallback entirely, or (b) source a different structured search backend and benchmark it under a new preregistered contract. No fresh municipalities, no fresh eval, no Protocol V1 change, and no benchmark-query tuning in this task.

## Final integrity

All task JSONs validated; historical integrity re-verified post-run in historical-integrity.md. TASK-LOCK.json closed as CLOSED_TERMINAL with terminal_status NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES.
