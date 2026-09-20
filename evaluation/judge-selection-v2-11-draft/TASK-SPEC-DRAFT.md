# TASK SPEC DRAFT - NAV-EXPLORE-JUDGE-SELECTION-V2_11-FRESH-CANDIDATE-SCREENING

Status: DRAFT_NOT_AUTHORIZED. Execution-inert until explicit owner
authorization. No model calls, no fixture generation, no writes outside this
lineage before authorization.

## 1. PURPOSE

After V2_10_NO_NON_M2_JUDGE_QUALIFIES, screen never-screened authorized
candidate models for the non-M2 semantic judge role, under the unchanged
frozen gates, with three process repairs derived from burned V2.10
diagnostics. Chain position: V2.10 (terminal) -> V2.11 (this task) -> fresh
validation of any qualifier (separate task) -> combined measurement freeze.

## 2. BURNED-DIAGNOSTIC BASIS (not generalization evidence)

From V2.10 calibration (25 fixtures x 2 candidates x 2 iterations):

- Both candidates reached 21/25 = 0.84; each was exactly 3 prompt-fixable
  rows from 0.96. The frozen 0.90 iteration gate is reachable.
- Persistent shared misses are the ambiguity-semantics boundary (UNC-05
  garbled prose, UNC-06 generic-vs-explicit limitation) plus hedged-route
  granularity: precisely the class the deterministic/boundary layer absorbs.
- DeepSeek was byte-identical across iterations at temperature 0: prompt
  work can be inert on a candidate. Detect this cheaply before spending a
  preregistered iteration (see prompt-sensitivity probe, section 5).
- V210C-FORB-01..06 gold contradicts the frozen derivation convention
  (positive-confirmation SUTs labeled NEGATED/ABSENT vs the FORB-32..39
  convention). Calibration gold must be dual-pass annotated, not asserted
  single-pass by a generator.
- Mimo iteration 2 fixed forbidden to 7/7 after the V2.10 prompt
  clarifications: the iter-2 V2.10 prompt (sha 66004e30...2682) is the
  correct starting point.

## 3. CANDIDATE SET (requires owner confirmation at authorization)

Never screened for the judge role; all in the standing authorized model list:

1. command-code/inclusionai-ling-3.0-flash-sante:free
2. command-code/poolside-laguna-s-2.1-free

Owner may add or substitute at authorization time. No candidate additions
after execution start. No LongCat. No GPT-5.5.

## 4. PHASE A - FIXTURES, GOLD, CONSISTENCY (0 model calls)

A1. Screening set: reuse the frozen, never-model-exposed V2.10 official
    screening set (screening-fixtures.json sha256 7afa5c9e...9dfa4c, gold
    efac73c40ca63b55...8f5f, prepass 39bf8aa3a54be3b1...82e6). Zero model
    exposure is the provenance argument. Alternative (owner override):
    generate 180 fresh fixtures under the same generator contract.
A2. New burned calibration set (25 fixtures, 12 traps), generator updated so
    that: every gold is machine-checked derivable from its inter block via
    the frozen derive_final; no fixture may encode the FORB-01..06 vs
    FORB-32..39 contradiction; calibration gold is dual-pass annotated with
    an agreement gate (mismatches -> discard fixture, new ID, from scratch).
A3. Collision audit against all historical lineages: 0 required.
A4. Gate: gold-derivation consistency 100%, collision count 0, dual-pass
    calibration gold agreement 100% after adjudication. Failure -> STOP,
    V2_11_GOLD_NOT_READY.

## 5. PHASE B - CALIBRATION WITH SENSITIVITY PROBE

B1. Starting prompt: the frozen V2.10 iter-2 prompt (sha 66004e30...2682).
B2. Smoke + prompt-sensitivity probe first: run 6 fixture rows, then rerun
    them under a preregistered trivial reordering of two prompt rules. A
    candidate whose outputs are byte-identical under both is flagged
    PROMPT_INERT and excluded from prompt iterations (its calibration result
    stands as-is; no iteration is burned on it).
B3. Calibration: 25 rows per candidate, per-row checkpointing, max 2
    iterations, preregistered iteration gate unchanged: strict improvement
    AND overall >= 0.90 AND 0 trap overcommit.
B4. Failure after budget -> candidate out; document; no forced rerun.

## 6. OFFICIAL SCREENING (qualifiers only)

One-shot, 180 rows, pipeline-connected (DETERMINISTIC_RESOLVED rows consume
zero judge calls), 1 technical retry on 429/5xx only, checkpointed. Gate
evaluator: eval_gates_v2_10.py verbatim (sha baedee48...8821a basis), frozen
values unchanged. Then stability (qualifiers, 3 runs, >= 0.95), comparison
freeze, selection per frozen tie-break or NO_QUALIFIES terminal.

## 7. REPORTING (honest coverage, goal section 4)

Report separately: AUTOMATED_JUDGE_ACCURACY, AUTOMATED_JUDGE_COVERAGE
(residual vs total), HUMAN_REVIEWED_CRITERIA (M2 lane, unchanged),
HUMAN_REVIEW_PENDING/DISAGREEMENT counters, and
FINAL_COMBINED_MEASUREMENT_COMPLETENESS. Never merge M2 human coverage into
model accuracy.

## 8. TERMINAL STATUSES

- V2_11_NON_M2_JUDGE_SELECTED_FOR_FRESH_VALIDATION
- V2_11_NO_NON_M2_JUDGE_QUALIFIES
- V2_11_GOLD_NOT_READY
- V2_11_BASELINE_MISMATCH
- V2_11_INVALID

## 9. HARD STOP

At terminal status: STOP. No fresh validation, no combined scorer freeze,
no product runtime changes, no next lineage, without new explicit owner
authorization.
