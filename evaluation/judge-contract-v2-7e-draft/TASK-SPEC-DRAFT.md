# TASK SPEC DRAFT - NAV-EXPLORE-JUDGE-CONTRACT-V2_7E-UNCERTAINTY-CONTRACT-REPAIR

Status: DRAFT_NOT_AUTHORIZED

This draft is execution-inert until the owner explicitly authorizes it in a
separate task message. No model calls, no contract writes outside this new
lineage, and no historical writes are permitted before that authorization.

## 1. PURPOSE

Repair the two frozen uncertainty-contract defects diagnosed by
NAV-EXPLORE-JUDGE-CONTRACT-V2_7D-SHARED-MISS-DIAGNOSIS and re-verify human
stability on entirely fresh fixtures. This task does NOT screen judge models
and does NOT validate any model.

Chain position: V2.7D (terminal V2_7D_CONTRACT_REPAIR_REQUIRED) -> V2.7E
(this task) -> judge screening (separate authorized task).

## 2. PREREQUISITE FROZEN PINS (verify at execution start)

- v1_4_semantic_contract f545b54b3295 dev-corpus-semantic-judge-v1-4/semantic-judge-contract-v1-4.json
- v2_2_frozen_non_m2_prompt_contract 5d5bbf9db626 judge-contract-v2-2-two-mechanism/judge_core_v2_2.py
- v2_2_official_scoring 75dddedb275a judge-contract-v2-2-two-mechanism/run_official_v2_2.py
- v2_6_m2_human_review_manifest e2513c3dceef measurement-v2-6-m2-human-review/m2-human-review-lane-v2-6-manifest.json
- v2_7_screening_fixtures 6f4279c2fa2e judge-selection-v2-7-non-m2/screening-fixtures.json
- v2_7_gold 4e016848c843 judge-selection-v2-7-non-m2/screening-gold.json
- deterministic_scorer_v1 8d36606861bb dev-corpus-scorer-v1/scorer.py
- deterministic_scorer_contract 94d8146272e7 dev-corpus-scorer-v1/scorer-contract-v1.json
- a3_boundary_preclassifier_v1_6a3 21047fdaaaa4 dev-corpus-semantic-judge-v1-6a3/boundary_preclassifier.py

V2.7D lineage pins (all under evaluation/judge-contract-v2-7d-shared-miss-diagnosis/):

- TASK-LOCK.json b1a58246fbd2 (TERMINAL / V2_7D_CONTRACT_REPAIR_REQUIRED)
- raw-agreement.json 865637590ae3
- adjudication-results.json f9461f8891ce
- final-report.md 7728662ed9e8
- uncertainty-boundary-report.json 45ccba725510
- historical-retrospective.json a48d95653b1b

Any pin mismatch: STOP with V2_7E_BASELINE_MISMATCH. No repair of pins.

## 3. HARD LOCKS

- model_calls_allowed = false (entire task)
- historical_writes_allowed = false
- v1_4_contract_file_edits_allowed = false (new contract file in new lineage only)
- judge_core_v2_2_file_edits_allowed = false (new derivation file in new lineage only)
- route_semantics_changes_allowed = false
- forbidden_semantics_changes_allowed = false
- m2_lane_changes_allowed = false
- score_label_changes_allowed = false (labels remain SATISFIED / PARTIAL / VIOLATED / NOT_REQUIRED / UNRESOLVED)
- product_runtime_changes_allowed = false
- subagents_allowed_max = 2 (GPT-5.6-Luna default; never GPT-5.5)
- burned_v2_7_set_reuse_as_validation = false

## 4. REPAIR TARGETS (preregistered canonical semantics)

### UNC-A1: contradictory limitation behavior

The frozen table maps EXPLICIT_LIMITATION x CONTRADICTORY_LIMITATION to
PARTIAL, while burned V2.7 gold used UNRESOLVED (UNC-46/47). Fresh human
calibration split 9/18 boundary rows on this behavior. Preregistered repair:

CONTRADICTORY_LIMITATION (limitation prose that contradicts itself, is garbled,
or retracts itself) does not communicate a usable epistemic limitation.

- Canonical uncertainty verdict: UNRESOLVED.
- The PARTIAL table row for this behavior is removed in the new contract.
- PARTIAL remains valid only for limitation prose that communicates a real,
  identifiable, incomplete qualification.

### UNC-A2: unclear prose behavior

UNCLEAR_PROSE is not defined by the frozen contract. Preregistered definition:

UNCLEAR_PROSE: the limitation-related output text cannot be classified as
communicating a limitation, failing to communicate one, or making a specific
prohibited over-conclusion, because the text is incoherent, fragmentary, or
self-contradictory at the sentence level.

- Canonical uncertainty verdict: UNRESOLVED.
- UNCLEAR_PROSE is a behavior input, not a score label.

The new contract must include an updated uncertainty decision tree that
resolves both defects, in frozen order, and preserves all other V1.4
uncertainty semantics verbatim.

## 5. DATA HYGIENE

- The 9 V2.7D disagreement rows (UNC-28..36) are burned contract-development
  data for this task: diagnostic leads only, never validation data, no textual
  variants or near-copies in any fresh set.
- The V1.2 official 80-set remains burned. The V2.7 burned set remains burned.
- The 90 V2.7D diagnostic fixtures remain burned for validation reuse.
- Fixture provenance and collision audit required for every fresh set
  (0 exact-text collisions against all historical sets).

## 6. FRESH HUMAN CALIBRATION

Set A: 32 entirely new uncertainty fixtures covering at minimum:
- clear limitation communicated (SATISFIED)
- limitation absent where required (VIOLATED)
- no uncertainty requirement (NOT_REQUIRED)
- contradictory limitation prose (target boundary)
- garbled limitation prose (target boundary)
- self-retracted limitation prose (target boundary)
- unclear prose (target boundary)
- real but incomplete qualification (PARTIAL)

Two blind intra-annotator passes, provenance declared
INTRA_ANNOTATOR_REPEATABILITY. Raw agreement frozen before adjudication.

Gates (pre-adjudication):
- overall >= 0.95
- no confusion pair other than preregistered boundary pairs above 0
- targeted zero gates: contradictory/garbled/self-retracted/unclear rows must
  not disagree at all (0 disagreements across these classes)

If Set A fails: one bounded clarification pass on contract text is allowed,
then Set B of 32 entirely new fixtures with identical gates. No contract text
changes after Set B labeling starts.

If Set B fails: STOP with V2_7E_REPAIR_CONTRACT_NOT_READY. No model calls.

## 7. FREEZE AND TERMINAL

On pass: freeze semantic-judge-contract-v2-7e.json (with updated uncertainty
decision tree), uncertainty-decision-tree-v2-7e.md, and the derivation file
uncertainty_derivation_v2_7e.py (new lineage; never edits judge_core_v2_2.py).
Record SHA-256 for all frozen artifacts in the manifest.

Terminal statuses (exactly one):
- V2_7E_CONTRACT_REPAIRED_AND_STABLE (all gates pass, contract frozen)
- V2_7E_REPAIR_CONTRACT_NOT_READY (Set B or repeated Set A gates fail)
- V2_7E_BASELINE_MISMATCH (prerequisite pin mismatch)
- V2_7E_INVALID (leakage, historical mutation, model calls, protocol violation)

V2_7E_CONTRACT_REPAIRED_AND_STABLE means the contract is ready for a separate
owner-authorized judge-screening task. It is NOT judge selection, NOT model
validation, and NOT certification.

## 8. DELIVERABLES

evaluation/judge-contract-v2-7e-uncertainty-repair/
- TASK-LOCK.json
- README.md
- baseline-integrity.json
- burned-data-registry.json
- uncertainty-repair-analysis.md (UNC-A1 + UNC-A2 resolution rationale)
- semantic-judge-contract-v2-7e.json
- uncertainty-decision-tree-v2-7e.md
- uncertainty_derivation_v2_7e.py
- calibration-set-a.json
- calibration-set-a-pass1.json
- calibration-set-a-pass2.json
- calibration-set-a-agreement.json
- boundary-clarification-log.md (only if clarification pass used)
- calibration-set-b.json (only if Set A fails once)
- calibration-set-b-pass1.json
- calibration-set-b-pass2.json
- calibration-set-b-agreement.json
- collision-audit.json
- manifest-v2-7e.json
- final-report.md

No downstream artifacts may be fabricated if an earlier gate stops the task.

## 9. STOP CONDITION

When the task reaches a terminal status: STOP. Do not start judge screening,
model selection, prompt tuning, fresh product evaluation, or any next stage
without a new explicit owner authorization.
