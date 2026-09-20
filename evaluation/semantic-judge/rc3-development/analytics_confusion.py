"""Report-only semantic confusion display (ANALYTICS_FIX_NOT_EVALUATOR_CHANGE).

RC2 bug (spec 41): the frozen scorer dropped predicted-REVIEW cells from
the semantic confusion display, so row sums did not equal class
denominators. This tool re-renders a corrected display from any
confusion artifact and validates display invariants. It never imports
evaluator runtime code and never changes frozen artifacts.
"""
import json
import sys

SEMANTIC_CLASSES = ["SUPPORTED", "CONTRADICTED",
                    "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
PREDICTED_COLUMNS = SEMANTIC_CLASSES + ["REVIEW_REQUIRED"]


def render(confusion, expected_totals=None):
    """confusion: {expected_class: {predicted_column: count}}.
    Returns a display dict with row totals, grand total, and invariant
    violations. expected_totals: optional {class: n} check."""
    rows = {}
    violations = []
    for cls in SEMANTIC_CLASSES:
        cells = confusion.get(cls, {})
        missing = [c for c in PREDICTED_COLUMNS if c not in cells]
        if missing:
            violations.append("missing_cells:%s:%s" % (cls, missing))
        row_total = sum(cells.get(c, 0) for c in PREDICTED_COLUMNS)
        rows[cls] = {"cells": {c: cells.get(c, 0)
                               for c in PREDICTED_COLUMNS},
                     "row_total": row_total}
        if expected_totals and cls in expected_totals \
                and row_total != expected_totals[cls]:
            violations.append("row_total_mismatch:%s:%d!=%d" %
                              (cls, row_total, expected_totals[cls]))
    grand = sum(r["row_total"] for r in rows.values())
    if expected_totals and grand != sum(expected_totals.values()):
        violations.append("grand_total_mismatch:%d!=%d" %
                          (grand, sum(expected_totals.values())))
    return {"rows": rows, "grand_total": grand,
            "violations": violations}


def main():
    if len(sys.argv) != 3:
        print("usage: analytics_confusion.py <confusion.json> <total>")
        return 2
    conf = json.load(open(sys.argv[1]))
    if "rows_expected_columns_predicted" in conf:
        conf = conf["rows_expected_columns_predicted"]
    arg = sys.argv[2]
    if arg.startswith("{"):
        totals = json.loads(arg)
    else:
        n = int(arg)
        totals = {cls: n for cls in SEMANTIC_CLASSES}
    disp = render(conf, totals)
    print(json.dumps(disp, ensure_ascii=False, indent=1))
    return 1 if disp["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
