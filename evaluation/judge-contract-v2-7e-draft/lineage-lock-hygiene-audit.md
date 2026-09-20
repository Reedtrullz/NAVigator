# Lineage Lock Hygiene Audit - 2026-09-13

Scope: all evaluation/*/TASK-LOCK.json files (39 total, maxdepth 2).
Purpose: prove no dangling ACTIVE lineage can collide with a future V2.7E
execution, and verify every historical lock is machine-readable.

## Findings

### F1 - Corrupted JSON lock repaired (syntax-only fix)

evaluation/dev-corpus-scorer-v1/TASK-LOCK.json failed json.load: line 16
was missing a trailing comma before "created". Any integrity audit reading
the lock registry would crash or silently skip this lineage - a fail-open
defect in the measurement hygiene chain.

Repair applied this audit: added the missing comma only. All values
byte-identical. Diff verified: exactly one character changed. Parsed OK
afterward: task_id NAV-EXPLORE-DEV-CORPUS-SCORER-V1, status
DEV_CORPUS_SCORER_V1_READY, updated/created 2026-09-10 unchanged.
SHA-256 after repair: d1488acce3da... (first 12 chars).

This was a JSON syntax corruption, not a semantic or historical status
change; the terminal status of the lineage is unchanged.

### F2 - Stale ACTIVE locks flagged, NOT touched (owner adjudication)

Two locks still carry status ACTIVE despite being superseded by later
terminal lineages in the same chain:

1. evaluation/dev-corpus-semantic-judge-v1-3/TASK-LOCK.json
   (NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3-BOUNDARY-CLARIFICATION,
   created 2026-09-10). Was blocked pre-observation with all 64 model
   calls rate-limited and zero annotations registered; later superseded
   by the V1.3M -> V1.4 -> V1.5A -> V1.6x and V2.x lineages, all terminal.

2. evaluation/judge-selection-v2-subskill/TASK-LOCK.json
   (NAV-EXPLORE-JUDGE-SELECTION-V2-SUBSKILL-SCREENING). Superseded by
   judge-selection-v2-1-no-longcat (terminal V2_1_NO_JUDGE_QUALIFIES)
   after the LongCat quota burn.

Both are historical records; per the frozen data-hygiene rule
(historical lineages and terminal statuses are never rewritten
retroactively) they were left byte-identical. Recommended owner action:
a one-time explicit adjudication task that marks each SUPERSEDED with a
pointer to the superseding terminal lineage, or confirms retention as-is.

### F3 - All other locks verified

The remaining 36 locks parse cleanly and their statuses are consistent
with the known chain: all non-flagged locks are in terminal, closed,
completed, blocked, or ready states matching their lineage outcomes.
No other dangling ACTIVE state exists. No lock in the measurement chain
(scorer, boundary, M2 lane, V2.x judge contracts) shows unexpected drift.

## Conclusion

No lineage lock collides with a future V2.7E execution. The V2.7E draft
lineage (TASK-SPEC-DRAFT.md, sha e755140ec9d1) remains the only
pre-execution artifact and stays DRAFT_NOT_AUTHORIZED.
