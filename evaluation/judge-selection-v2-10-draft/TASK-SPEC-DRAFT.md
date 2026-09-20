# TASK SPEC DRAFT - NAV-EXPLORE-JUDGE-SELECTION-V2_10-BOUNDARY-EXTENSION-AND-RESCREEN

Status: DRAFT_NOT_AUTHORIZED. Execution-inert until explicit owner
authorization. No model calls, no fixture generation, no writes outside this
lineage before authorization.

## 1. PURPOSE

After V2_9_NO_NON_M2_JUDGE_QUALIFIES, take the one bounded stage that the
V2.9 root-cause evidence supports: extend the frozen deterministic/boundary
layer with two precision-first classes, add a symmetric PARTIAL-discipline
rule to the judge prompt, and re-screen on entirely fresh fixtures under the
unchanged frozen gates. Chain position: V2.9 (terminal) -> V2.10 (this task)
-> combined measurement freeze only after a qualifier passes fresh validation.

Basis (burned diagnostics, not generalization evidence):
root-cause-analysis.md in this lineage.

## 2. PHASE A - BOUNDARY EXTENSION (0 model calls)

Extend the boundary layer as a new versioned artifact (boundary_preclassifier
v1.7 or successor; frozen input artifacts unchanged):

- CONTRADICTORY_LIMITATION -> deterministic UNRESOLVED
- DIRECT_ROUTE_ASSERTION -> deterministic ACCEPTABLE

Hard requirements:
- precision-first, conservative, ABSTAIN on any doubt (architecture section 1)
- new classes are additive; all existing frozen boundary behavior unchanged
- validated on burned V2.9 fixtures: 100% precision on every V2.9 barrel where
  each class fires; zero new wrong resolutions; ABSTAIN rate reported
- unit tests for both classes, including near-miss non-firing cases

Phase A gate: validation PASS with zero false resolutions. Failure -> STOP,
status V2_10_BOUNDARY_EXTENSION_FAILED. Do not relax detectors.

## 3. PHASE B - FRESH RESCREEN

Prompt: one preregistered addition to the frozen V2.9 prompt (iteration
accounting continues; max 2 further iterations): symmetric PARTIAL-discipline
rule. No other prompt changes. Calibration on fresh synthetic fixtures
(burned) before official run.

Fixtures: 180 entirely fresh, same generator discipline, 0 collisions vs all
historical texts including V2.9; 60/60/60; deterministic prepass rerun with
the extended boundary layer; repair subset and trap registry rebuilt fresh.
Gold via established dual-pass derivation.

Official run: one-shot per candidate, same frozen gates and evaluator logic
(verbatim V2.8/V2.9 scorer logic; gate values unchanged), no reruns, transport
failures invalid without retry.

Candidates: EXPLICITLY_NAMED_IN_OWNER_AUTHORIZATION only. No discovery, no
post-start expansion, no best-of-bad. Re-nomination of V2.9 candidates is an
owner decision.

## 4. HARD LOCKS

- historical_writes_allowed = false (V2.9 lineage untouched)
- gate_value_changes_allowed = false
- score_label_changes_allowed = false
- m2_lane_changes_allowed = false
- product_runtime_changes_allowed = false
- longcat_allowed = false, gpt_5_5_allowed = false
- boundary extension must ABSTAIN rather than guess
- v2_9_benchmark_reuse = false (burned; no textual variants)
- subagents_allowed_max = 2, default command-code/xiaomi-mimo-v2.5

## 5. TERMINAL STATUSES

Exactly one:
- V2_10_NON_M2_JUDGE_SELECTED_FOR_FRESH_VALIDATION (all frozen gates pass)
- V2_10_NO_NON_M2_JUDGE_QUALIFIES (no candidate passes; no best-of-bad)
- V2_10_BOUNDARY_EXTENSION_FAILED (Phase A gate fails)
- V2_10_BASELINE_MISMATCH / V2_10_GOLD_NOT_READY / V2_10_INVALID

## 6. HARD STOP

After terminal status: STOP. No fresh validation, no combined freeze, no
product work without new explicit owner authorization.
