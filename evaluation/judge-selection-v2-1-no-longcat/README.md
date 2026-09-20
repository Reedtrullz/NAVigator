# Judge Selection V2.1 (No LongCat)

Task ID: `NAV-EXPLORE-JUDGE-SELECTION-V2_1-NO-LONGCAT`

Screening lineage that supersedes the blocked LongCat-based V2 screening
(`evaluation/judge-selection-v2-subskill/`, preserved read-only). Pipeline
(fixtures, gold, prompt, scoring, A3 derive, gates) is verbatim V2; only the
model identifier and per-candidate checkpoint/smoke locations differ.

- Owner decision: LongCat 2.0 withdrawn from NAV Explore evaluator work
  (`LONGCAT_WITHDRAWN_BY_OWNER_QUOTA_CONSTRAINT`); daily quota too small.
- Old V2 runs are `INCOMPLETE_DIAGNOSTIC_HISTORY`; resume forbidden.
- mimo-v2-5-pro rerun forbidden (terminal `gates_all_pass=false` in V2).
- Frozen shortlist (priority order): mimo-v2-5, ling-3-0-flash-sante-free,
  poolside-laguna-s-2-1-free.

## Process

1. Smoke each candidate (1 technical judge call). Failing smoke excludes
   the candidate per the frozen shortlist rule.
2. One-shot full run per smoke-PASS candidate (72 fixtures; 69 judge calls
   + 3 A3-derived rows). Checkpoint saved per row.
3. Gates (identical V2): family acc >= 0.90; A critical FN = 0; C safety
   FN = 0; abstention precision >= 0.95 if rows; evidence validity 100%;
   zero transport/schema failures. Completeness distinguishes COMPLETE /
   `SCREENING_INCOMPLETE_QUOTA` / `SCREENING_INCOMPLETE_TRANSPORT`.
4. Stability (24 fixtures x 5 runs, modal >= 0.95) only for one-shot
   qualifiers.
5. `make_final_v2_1.py` freezes comparison, runs the LongCat zero-use
   audit (model-use identifiers, provenance docs allowlisted), applies the
   preregistered priority selection, and writes the terminal status.

## Known deviation (recorded, not patched mid-task)

`run_screening_v2_1.py` does not exit after a fresh smoke PASS under
`--smoke-only`; the same process proceeds into the full run. Per-candidate
one-shot semantics are nevertheless intact (each candidate ran in a single
process, single full pass). Regression fix is deferred to future R&D.

## Artifacts

- `TASK-LOCK.json` - task lock and terminal registration
- `owner-model-policy.json` - owner model authorization snapshot
- `baseline-integrity.json`, `old-v2-handoff.json` - frozen V2 baseline SHAs
- `candidate-inventory.json`, `candidate-shortlist-v2-1.json` - frozen shortlist
- `quota-capability-report.json` - pre-execution quota/cost assessment
- `screening-contract.json` - reference to authoritative frozen V2 contract
- `candidate-configs/` - frozen per-candidate configs
- `smoke-<key>.json` - smoke verdicts
- `checkpoint-<key>.json` - per-row run state
- `screening-results-v2-1-<key>.json` - one-shot gate results
- `stability-results-v2-1-<key>.json` - qualifier stability screens
- `candidate-comparison.json`, `longcat-zero-use-audit.json`,
  `final-report.md` - finalize outputs

## Status

See `final-report.md` and `TASK-LOCK.json` after finalization.
