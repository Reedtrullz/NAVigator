# Judge Selection V2.10 - Draft (not authorized)

Successor draft to terminal V2_9_NO_NON_M2_JUDGE_QUALIFIES. Contains:

- root-cause-analysis.md - burned-data taxonomy of all 19 V2.9 substantive
  misses; headline: 16/19 are PARTIAL-collapse in both directions.
- TASK-SPEC-DRAFT.md - bounded two-phase task: deterministic boundary
  extension (CONTRADICTORY_LIMITATION, DIRECT_ROUTE_ASSERTION; ABSTAIN-first,
  zero model calls) + symmetric PARTIAL-discipline prompt rule + fresh
  180-fixture rescreen under unchanged frozen gates.
- TASK-LOCK.json - DRAFT_NOT_AUTHORIZED, fully inert.

Nothing here executes without explicit owner authorization, including the
candidate set. The V2.9 lineage and all earlier lineages are untouched.

## Phase A validation (2026-09-13)

The deterministic boundary extension is implemented and validated against the
burned V2.9 fixture set (180 rows, 0 model calls):

- `boundary-extension-v1-7-draft.py` (sha 7e0f8408...0001) - wraps the frozen
  v1.6a3 preclassifier via importlib; adds CONTRADICTORY_LIMITATION (uncertainty)
  and DIRECT_ROUTE_ASSERTION (route) detectors. Upgrade-only: frozen-base labels
  are never overridden; all ambiguity abstains.
- `test_boundary_extension_draft.py` (sha e8fdd9a7...f6ed) - 23/23 PASS.
- `validate_boundary_extension_draft.py` + `boundary-extension-validation-draft.json`
  - burned-barrel gate: 8/8 uncertainty and 6/6 route barrels fired, precision 1.0
  on fired, 0 wrong resolutions over 180 fixtures, frozen base unchanged,
  unc abstain rate 0.0111, route abstain rate 0.9167.
- V2.9 baseline-integrity pins re-verified 4/4 MATCH after Phase A.

Phase B (fresh 180-fixture rescreen + PARTIAL-discipline prompt rule) remains
gated on explicit owner authorization. TASK-LOCK stays DRAFT_NOT_AUTHORIZED.
