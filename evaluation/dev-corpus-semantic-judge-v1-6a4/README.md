# V1.6A.4 - Assertion Strength / Endorsement Strength Grounding

Task: `NAV-EXPLORE-DEV-CORPUS-BOUNDARY-V1_6A4-ASSERTION-STRENGTH-GROUNDING`

Terminal status: **`V1_6A4_NOT_READY`** (fail-closed after the fresh
official one-shot). `NEXT_STAGE_REQUIRES_ARCHITECTURE_DECISION = true`.
No A5, no V1.6B rescreen, no engine patching, no reruns.

## What This Was

The last pre-authorized deterministic expansion
(`V1_6A4_LAST_PREAUTHORIZED_DETERMINISTIC_EXPANSION = true`) of the boundary
pre-classifier: an attempt to extract assertion strength (ASSERTED vs HEDGED,
REPORTED, QUOTED_ONLY, HYPOTHETICAL, NEGATED, SELF_RETRACTED, VAGUE) with
>= 0.99 precision on top of the frozen V1.6A.1/A.2/A.3 layers.

## Outcome in Brief

- Fresh TDD: RED 5/30 on A3, GREEN 30/30 on A4.
- Burned regressions: 0 mismatches on all legacy dimensions (120/60/80 sets).
- Engine frozen before fresh fixtures: `22a5f61c...`.
- Fresh official one-shot (60 fixtures): precision 0.368 vs >= 0.99 gate,
  36 false deterministics, 3/60 abstains, 2 evidence-invalid rows.
  All 6 hard gates failed. The one-shot is spent.
- Exit question: `BORDERLINE_SEMANTIC_RULE_SYSTEM`.
- Complexity: +173 LOC, +8 rules bought development wins but not fresh
  precision; 5 of 9 failure families require semantic scope composition.

Read `final-report.md` for the full account; `failure-family-analysis.json`
and `complexity-accounting.json` hold the postmortem detail.

## Artifact Map

| File | Contents |
|---|---|
| `TASK-LOCK.json` | task lock, terminal status |
| `capability-proof.md` | pre-implementation capability argument |
| `tdd-fixtures.json`, `tdd-red-result.json`, `tdd-green-result.json`, `run_tdd.py` | fresh TDD evidence |
| `run_burned_regressions.py`, `burned-120-regression.json`, `burned-targeted60-regression.json`, `burned-v1-6a2-80-regression.json` | burned cascade |
| `candidate-freeze-before-fresh.json` | pre-fixture engine freeze (8 SHAs) |
| `official-validation-fixtures.json`, `official-validation-gold-v1_6a4.json`, `official-fixture-hashes.json` | blind fresh validation set (frozen) |
| `run_official_validation.py`, `official-validation-results.json` | spent one-shot and results |
| `failure-family-analysis.json` | 9-family taxonomy of all 38 bad rows |
| `complexity-accounting.json` | before/after rule complexity vs yield |
| `a4_boundary_preclassifier.py` | frozen A4 engine (unchanged post-failure) |
| `final-report.md` | terminal report |

## Lineage

Sits on top of `../dev-corpus-semantic-judge-v1-6a3/boundary_preclassifier.py`
(`21047fda...`), which was verified intact. The A1/A2/A3 layers and all
historical PASS statuses are untouched. This directory is closed; the next
deterministic expansion or a combined-pipeline re-screen requires a separate
explicit architecture decision by the owner.
