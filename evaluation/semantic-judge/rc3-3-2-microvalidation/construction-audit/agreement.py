#!/usr/bin/env python3
"""PASS 1/PASS 2 agreement (spec 15) + adjudication gate prep."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(HERE))
import write_guard  # noqa: E402


def norm_qty(v):
    if v is None:
        return None
    s = str(v).strip().upper().replace(" ", "")
    return None if s in ("", "NULL", "NONE") else s


def norm_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "yes", "1")


def norm_rel(v):
    if v is None:
        return None
    s = str(v).strip()
    return {"EQ": "=", "GE": ">=", "GT": ">", "LE": "<=",
            "LT": "<"}.get(s.upper(), s)


def compare(pid, p2):
    disp = {}
    if pid["semantic_relation"] != p2.get("semantic_relation"):
        disp["semantic_relation"] = [pid["semantic_relation"],
                                     p2.get("semantic_relation")]
    q1, q2 = norm_qty(pid["semantic_quantity_identity"]), \
        norm_qty(p2.get("semantic_quantity_identity"))
    if q1 != q2:
        disp["semantic_quantity_identity"] = [q1, q2]
    if pid["temporal_applicability"] != p2.get("temporal_applicability"):
        disp["temporal_applicability"] = [pid["temporal_applicability"],
                                          p2.get("temporal_applicability")]
    c1 = pid["comparator_applicable"]
    c2 = norm_bool(p2.get("comparator_applicable"))
    if c1 != c2:
        disp["comparator_applicable"] = [c1, c2]
    r1, r2 = pid["comparator_relation"], norm_rel(p2.get("comparator_relation"))
    if r1 != r2:
        disp["comparator_relation"] = [r1, r2]
    if pid["aggregate_component_role"] != p2.get("aggregate_component_role"):
        disp["aggregate_component_role"] = [pid["aggregate_component_role"],
                                            p2.get("aggregate_component_role")]
    return disp


def main():
    pass1 = json.loads((HERE / "pass1-labels.json").read_text(
        encoding="utf-8"))["pass1_labels"]
    pass2 = json.loads((HERE / "labels-pass2-raw.json").read_text(
        encoding="utf-8"))
    fields = {"semantic_relation": [0, 0],
              "semantic_quantity_identity": [0, 0],
              "temporal_applicability": [0, 0],
              "comparator_applicable": [0, 0],
              "comparator_relation": [0, 0],
              "aggregate_component_role": [0, 0]}
    disputes = {}
    for cid in sorted(pass1):
        disp = compare(pass1[cid], pass2.get(cid, {}))
        if disp:
            disputes[cid] = disp
        for f in fields:
            if f == "semantic_quantity_identity":
                applicable = pass1[cid]["semantic_quantity_identity"] or \
                    norm_qty(pass2.get(cid, {}).get(f))
            elif f == "comparator_relation":
                applicable = pass1[cid]["comparator_applicable"] or \
                    norm_bool(pass2.get(cid, {}).get("comparator_applicable"))
            elif f == "comparator_applicable":
                applicable = pass1[cid]["semantic_quantity_identity"] or \
                    norm_qty(pass2.get(cid, {})
                             .get("semantic_quantity_identity"))
            else:
                applicable = True
            if applicable:
                fields[f][1] += 1
                if f not in disp:
                    fields[f][0] += 1
    summary = {}
    for f, (ok, n) in fields.items():
        summary[f] = {"agree": ok, "applicable": n,
                      "pct": round(100 * ok / n, 2) if n else None}
    result = {
        "per_field": summary,
        "dispute_cases": sorted(disputes),
        "dispute_count_cases": len(disputes),
        "disputes": disputes,
    }
    write_guard.write_text(
        HERE / "agreement.json",
        json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    sem = summary["semantic_relation"]["pct"]
    print("AGREEMENT", json.dumps(summary))
    print("DISPUTE_CASES", len(disputes))
    if sem is not None and sem < 90:
        print("ANNOTATION_CONTRACT_NOT_READY")


if __name__ == "__main__":
    main()
