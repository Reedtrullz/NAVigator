"""Analytics scorer display regression (spec 41).

Guards the report-only confusion renderer: row totals must equal the
expected class denominator when all predicted cells are present, and
the renderer must flag the frozen RC2 scorer bug (missing REVIEW
column) instead of silently hiding it. EVALUATOR CHANGE: none.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analytics_confusion import render


def test_full_display_totals_match_denominator():
    conf = {
        "SUPPORTED": {"SUPPORTED": 30, "CONTRADICTED": 0,
                      "PARTIALLY_SUPPORTED": 0,
                      "INSUFFICIENT_EVIDENCE": 0,
                      "REVIEW_REQUIRED": 9},
        "CONTRADICTED": {"SUPPORTED": 2, "CONTRADICTED": 23,
                         "PARTIALLY_SUPPORTED": 0,
                         "INSUFFICIENT_EVIDENCE": 0,
                         "REVIEW_REQUIRED": 15},
        "PARTIALLY_SUPPORTED": {"SUPPORTED": 1, "CONTRADICTED": 1,
                                "PARTIALLY_SUPPORTED": 0,
                                "INSUFFICIENT_EVIDENCE": 0,
                                "REVIEW_REQUIRED": 39},
        "INSUFFICIENT_EVIDENCE": {"SUPPORTED": 0, "CONTRADICTED": 0,
                                  "PARTIALLY_SUPPORTED": 0,
                                  "INSUFFICIENT_EVIDENCE": 0,
                                  "REVIEW_REQUIRED": 40},
    }
    totals = {"SUPPORTED": 39, "CONTRADICTED": 40,
              "PARTIALLY_SUPPORTED": 41, "INSUFFICIENT_EVIDENCE": 40}
    out = render(conf, totals)
    assert out["violations"] == [], out["violations"]
    assert out["grand_total"] == 160


def test_frozen_scorer_bug_is_flagged():
    # The frozen RC2 scorer emitted confusion WITHOUT the REVIEW
    # column (all predicted-REVIEW cells dropped). The renderer must
    # report violations, not pass silently.
    conf = {
        "SUPPORTED": {"SUPPORTED": 30, "CONTRADICTED": 0,
                      "PARTIALLY_SUPPORTED": 0,
                      "INSUFFICIENT_EVIDENCE": 0,
                      "REVIEW_REQUIRED_PREDICTED_ONLY": 0},
        "CONTRADICTED": {"SUPPORTED": 2, "CONTRADICTED": 23,
                         "PARTIALLY_SUPPORTED": 0,
                         "INSUFFICIENT_EVIDENCE": 0,
                         "REVIEW_REQUIRED_PREDICTED_ONLY": 0},
        "PARTIALLY_SUPPORTED": {"SUPPORTED": 1, "CONTRADICTED": 1,
                                "PARTIALLY_SUPPORTED": 0,
                                "INSUFFICIENT_EVIDENCE": 0,
                                "REVIEW_REQUIRED_PREDICTED_ONLY": 0},
        "INSUFFICIENT_EVIDENCE": {"SUPPORTED": 0, "CONTRADICTED": 0,
                                  "PARTIALLY_SUPPORTED": 0,
                                  "INSUFFICIENT_EVIDENCE": 0,
                                  "REVIEW_REQUIRED_PREDICTED_ONLY": 0},
    }
    totals = {"SUPPORTED": 39, "CONTRADICTED": 40,
              "PARTIALLY_SUPPORTED": 41, "INSUFFICIENT_EVIDENCE": 40}
    out = render(conf, totals)
    assert out["violations"], "bug must be flagged"


if __name__ == "__main__":
    test_full_display_totals_match_denominator()
    test_frozen_scorer_bug_is_flagged()
    print("analytics display regression: 2/2 PASS")
