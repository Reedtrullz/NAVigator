# V2.10 Final Report - Non-M2 Judge Rescreen (Phase B)

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_10-BOUNDARY-EXTENSION-AND-RESCREEN
Terminal status: **V2_10_NO_NON_M2_JUDGE_QUALIFIES**

## Entry state

Phase A (boundary extension) was validated in the prior session: 180 screening
fixtures (60/60/60), 0 historical collisions, 127-entry replacement mapping,
prepass 80 DETERMINISTIC_RESOLVED / 12 EXTENSION_RESOLVED / 88
EXPECTED_SEMANTIC_RESIDUAL, construction-discipline assert added (0 failures).
Gold frozen as screening-gold.json (sha256 efac73c40ca63b55...8f5f), prepass
sha256 39bf8aa3a54be3b1...82e6. Smoke passed for both candidates (0 retries).

## Calibration iteration 1 (both candidates)

25 burned fixtures, 12 traps, gates: strict improvement + overall >= 0.90 +
0 trap overcommit.

- deepseek-v4.1-flash: 21/25 = 0.84, overcommit 1 (V210C-UNC-05 trap).
- mimo-v2.5-pro: 21/25 = 0.84, overcommit 0.

Miss classes (both candidates): hedged/asserted positive route downgraded to
PARTIAL (ROUTE-10 / ROUTE-02); generic hedge scored as full satisfaction of an
explicit-limitation criterion (UNC-06, gold PARTIAL); garbled prose scored
PARTIAL instead of UNRESOLVED (UNC-05 trap); DeepSeek only: negated forbidden
claim scored PRESENT (FORB-01); MiMo only: self-retracted route scored
NO_ACCEPTABLE_ROUTE (FORB-04 trap).

## Bounded prompt iteration (iteration 2)

One preregistered bounded pass was applied to judge_core_v2_10.py, four
general contract clarifications, no fixture references, no gate changes:

1. Generic uncertainty does not alone satisfy an explicit-limitation
   requirement; hedged-but-clear positive commits remain evaluable (rule 8).
2. Forbidden commitment is judged toward the positive proposition (paraphrase
   of criterion content), not toward the criterion's negative wording.
3. Explicit correction with clear final position ends a retraction; clear final
   position is not SELF_RETRACTED; without a new concrete route, commitment is
   UNRESOLVED.
4. Incoherent or fragmentary limitation text is UNCLEAR_PROSE, never
   PARTIAL_LIMITATION.

Iter-2 prompt sha256: 66004e3038eb4830...b02682

## Calibration iteration 2 (both candidates)

- deepseek-v4.1-flash: 21/25 = 0.84, overcommit 1. Misses byte-identical to
  iteration 1: the clarifications produced zero behavioral change at
  temperature 0.
- mimo-v2.5-pro: 21/25 = 0.84, overcommit 1 (regressed V210C-UNC-05 trap from
  UNRESOLVED to PARTIAL). Fixed both forbidden misses (7/7), but route dropped
  to 8/10 (ROUTE-09 PARTIAL -> NO_ACCEPTABLE_ROUTE) and uncertainty to 6/8.

Both candidates fail the iteration gate: neither shows strict improvement,
both remain at 0.84 < 0.90, and both now carry 1 trap overcommit. The
preregistered iteration budget (max 2 iterations) is exhausted.

## Calibration-only observation (recorded, not acted on)

V210C-FORB-01 (and its block) is inconsistent with the V210-FORB-32..39
convention: paraphrases of negatively-phrased criteria are labeled NEGATED/ABSENT
in the former but the semantically identical form is ASSERTED/PRESENT in the
latter. Both models answered the frozen-derivation-correct value (ASSERTED ->
PRESENT). This is a generator-convention defect in the burned calibration set,
documented here as LABEL_SENSITIVITY_ONLY. It does not affect the official
screening set: all six FORB negation rows there are DETERMINISTIC_RESOLVED and
never reach the judge.

## Terminal decision

Per the frozen selection principle (no best-of-bad selection), neither
candidate advances to official screening or stability. Iteration budget is
exhausted; no further prompt changes are permitted in this task.

Official screening was NOT run (no qualifier). Stability was NOT run.
No combined scorer freeze. No product runtime changes. No fresh holdout.

## Frozen artifacts (sha256)

See comparison-freeze-v2-10.json for the complete registry, including
calibration-results-iter1/2, metrics-iter1/2, the iter-2 prompt, screening
fixtures/gold, and prepass.

## Hard stop

Task closed at terminal status. New judge screening, prompt tuning, contract
changes, V2.11, full SUT runs, product integration, and product fresh holdout
all require a new explicit owner authorization.
