#!/usr/bin/env python3
"""Field agreement per annotation-contract v3 (spec 18/24).

Usage: agreement_v3.py <gold-or-pass1.json> <pass2.json> <out.json>
The first argument is either an embedded-gold file (calibration) or the
pass-1 annotations file (final passes). This script only computes
agreement statistics after both passes have completed.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

FIELDS = ["semantic_relation", "quantity_identity", "quantity_value_claim",
          "quantity_value_source", "role", "temporal_applicability",
          "comparator_applicable", "comparator_relation",
          "arithmetic_duty"]


def load_annotations(path, gold=False):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if gold:
        return {x["case_id"]: x for x in d["gold"]}
    return d["annotations"]


def main():
    a_path, b_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    a = load_annotations(a_path, gold="--gold" in sys.argv)
    b = load_annotations(b_path)
    ids = sorted(set(a) & set(b))
    stats = {f: {"agree": 0, "applicable": 0} for f in FIELDS}
    disputes = {}
    for cid in ids:
        x, y = a[cid], b[cid]
        d = {}
        for f in FIELDS:
            applicable = True
            if f == "quantity_identity":
                applicable = "NOT_APPLICABLE" not in (
                    x.get("quantity_identity"), y.get("quantity_identity"))
            elif f in ("quantity_value_claim", "quantity_value_source"):
                applicable = not (
                    x.get(f) is None and y.get(f) is None)
            elif f == "role":
                applicable = "NOT_APPLICABLE" not in (
                    x.get("role"), y.get("role"))
            elif f == "temporal_applicability":
                applicable = "NOT_APPLICABLE" not in (
                    x.get("temporal_applicability"),
                    y.get("temporal_applicability"))
            elif f == "comparator_relation":
                applicable = x.get("comparator_applicable") or \
                    y.get("comparator_applicable")
            if applicable:
                stats[f]["applicable"] += 1
                if x.get(f) == y.get(f):
                    stats[f]["agree"] += 1
                else:
                    d[f] = [x.get(f), y.get(f)]
        if d:
            disputes[cid] = d
    summary = {}
    for f, s in stats.items():
        pct = round(100 * s["agree"] / s["applicable"], 2) \
            if s["applicable"] else None
        summary[f] = {"agree": s["agree"], "applicable": s["applicable"],
                      "pct": pct}
    kinds = Counter(f for d in disputes.values() for f in d)
    out = {"n_cases": len(ids), "per_field": summary,
           "dispute_field_counts": dict(kinds),
           "dispute_cases": sorted(disputes), "disputes": disputes}
    Path(out_path).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=1))
    print("DISPUTE_CASES", len(disputes))


if __name__ == "__main__":
    main()
