# SELECTION DECISION (frozen rule, no threshold changes)

Outcome: **NO SELECTION.** `NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES`.

## Gate evaluation (GENERAL mode preregistered as gate basis)

| Gate | Threshold | Tavily (GENERAL) | Verdict |
|---|---|---|---|
| Query execution rate | >= 95% | 87.18% (102/117) | FAIL |
| Relevant-target recall (gold domain) | >= 90% | 80.34% (94/117) | FAIL |
| Bot-block rate | 0 | 0 | PASS |
| False provider-failure -> NO_RESULTS | 0 | 0 (20/20 failure-sim tests) | PASS |
| Structured contract | PASS | PASS (canonical statuses, transport metadata) | PASS |
| Secret handling | PASS | PASS (SECRET_LEAK_SCAN = 0 / 30 files) | PASS |

Brave Search API: `NOT_TESTABLE_NO_AUTHORIZED_CREDENTIAL` (never benchmarked;
Brave HTML remains the disqualified negative control).

## Structural finding (primary R&D result)

Site-direct covers 117/117 municipalities in the frozen V2 baseline
(recall 1.0). Every Tavily gold-domain hit is a strict subset of
site-direct hits: `incremental_target_recovery_over_site_direct = 0/117`
in both modes. The external fallback would add nothing on this corpus
even if its own gates had passed.

## Per-mode diagnostics (not gates)

- CONSTRAINED (include_domains = kommunens domene): execution 64.10%,
  recall 64.10%, precision 0.6410. Lower than GENERAL on every gate
  metric; consistent with the preregistered rationale that domain
  restriction does not rescue weak execution. Reported for completeness.
- Raelingen: 0/9 in both modes (SPA/render-heavy site; Tavily never
  surfaces its gold target). Site-direct handles it via navigation.

## Decision

No eligible backend -> no primary selection, no V2.2 integration run,
no forced-fallback tests, no candidate freeze. The frozen
provider-config-v2-2.json remains frozen as the benchmark-time config
and is superseded (not rewritten) by this outcome: the production
lineage stays V2.1 (site-direct primary, external fallback effectively
unavailable until a passing structured backend exists).
