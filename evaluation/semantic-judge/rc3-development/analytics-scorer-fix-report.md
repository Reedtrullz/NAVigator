# Analytics Scorer Fix Report (spec 41)

ANALYTICS_FIX_NOT_EVALUATOR_CHANGE

## Bug

The frozen RC2 scorer (score_frozen_predictions.py,
SEMANTIC_CONFUSION_ORDER) labeled the predicted-review column
"REVIEW_REQUIRED_PREDICTED_ONLY" and emitted it with zeroed cells, so
predicted-REVIEW cells vanished from the semantic confusion display.
Row sums did not equal class denominators (e.g. SUPPORTED row summed
to 30 against a 39-row class). Official metrics were unaffected:
scoring used prediction rows directly, not the display.

## Fix (report-only)

New tool `analytics_confusion.py` in rc3-development/: re-renders the
corrected display from any confusion artifact, validates missing
cells, row totals against class denominators and the grand total,
and flags violations instead of hiding them. No frozen RC2 artifact
was touched (hash check OK after fix).

## Regression test

`tests/test_analytics.py`: 2/2 PASS -

1. full display: row totals equal class denominators (39/40/41/40),
   grand total 160 = denominator;
2. the frozen buggy shape (missing REVIEW column) is flagged as a
   violation, never passed silently.

## Verified outputs

- Corrected post-freeze semantic-confusion.json: 0 violations,
  grand total 160.
- official-score.json confusion (buggy display): exit 1 with
  violations listed, as intended.
