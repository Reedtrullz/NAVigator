# BACKEND SELECTION CONTRACT (RESTART DESIGN)

Status: DESIGNED_NOT_EXECUTED. The official benchmark never ran because the
credential gate failed for both external candidates. This document freezes
the selection design that was derived from task sections 10-34 so a future
bounded task can execute without redesign.

## Candidate set

1. BASELINE A - SITE_DIRECT_ONLY (control, always runs)
2. CANDIDATE B - Brave Search API (official structured API only; Brave HTML
   stays disqualified as the negative control)
3. CANDIDATE C - Tavily Search API (`include_answer = false`; answer text is
   never route evidence)

No additional candidate was added. The optional-candidate criteria in task
section 5 (public documented API, structured responses, intended
programmatic use, legitimate authentication, existing credential) were not
met by any further backend with an available credential, and speculative
additions were rejected per section 5.

## Frozen comparison parameters

- Same canonical queries for all candidates; queries come from the burned
  provider benchmark corpus (task section 17: >= 30 queries, >= 12 burned
  municipalities, mixed centrality, nested and difficult discovery targets,
  negative cases). Exact list must be re-derived from the V2 benchmark
  artifacts and frozen as `benchmark-corpus.json` before the run.
- Normalized result limit: top 10.
- Norway context where supported: country = Norway, Norwegian language.
- Two domain modes where supported (GENERAL, OFFICIAL-DOMAIN-BIASED),
  frozen before scoring; no post-hoc per-case mode switching.
- Fixed config only; no adaptive provider features (section 14).

## Gates (unchanged from task)

- QUERY_EXECUTION_RATE >= 95%
- RELEVANT_TARGET_RECALL >= 90%
- BOT_BLOCK_RATE = 0
- false failure -> NO_RESULTS = 0 (failure-simulation suite: 401/403, 429,
  timeout, malformed JSON, empty results, provider unavailable)
- SECRET_LEAK_SCAN = 0
- structured contract PASS (canonical provider states only)

## Selection priority

1. relevant-target recall, 2. query execution reliability, 3. official-domain
precision, 4. incremental recovery over site-direct, 5. operational
simplicity, 6. latency/cost. No forced winner; no threshold lowering.

## Invariants

- Search API output is discovery evidence only; final route evidence always
  comes from fetching the original public page via the existing
  FetchProvider (sections 12 and 24).
- Site-direct remains the primary discovery strategy (section 35).
- Tavily generated answers are never consumed by the route engine (section 13).

## Restart prerequisites

- Authorized credential for at least one candidate, supplied by the user via
  env var or approved secret path (no account creation, no plan activation).
- TASK-LOCK for a new task id; this task stays terminally closed.
