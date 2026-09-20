#!/usr/bin/env python3
"""Diagnostic: dump parsed numeric quantities and prediction per case."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_local.numeric import (parse_quantities, derived_quantities,
                                  numeric_relation, numeric_gate)
from engine_local.engine import evaluate_case

ROOT = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(ROOT, "fresh-cases.json")))["cases"]
ids = sys.argv[1:] or ["R33-082"]


def brief(q):
    return (q["quantity_type"], q["value"], q.get("range_bounds"),
            q["unit"], q["comparator"], q["period"], q["role"],
            (q.get("object_binding") or "")[:26],
            q.get("provenance", {}).get("claim_span")
            or q.get("provenance", {}).get("evidence_span"))


for cid in ids:
    c = next(x for x in cases if x["case_id"] == cid)
    all_text = " ".join(s["text"] for s in c["evidence"])
    print("=" * 24, cid, "=" * 24)
    print("CLAIM:", c["claim"])
    for q in parse_quantities(c["claim"]):
        print("  CQ:", brief(q))
    print("EVID :", all_text)
    for q in parse_quantities(all_text):
        print("  EQ:", brief(q))
    for q in derived_quantities(all_text):
        print("  DQ:", brief(q))
    print("numeric_relation:", numeric_relation(c["claim"], all_text),
          "gate:", numeric_gate(c["claim"], all_text))
    r = evaluate_case(c)
    a = r["atoms"][0]
    print("PRED:", r["verdict"], "| rule:", a["rule"],
          "| rel:", a.get("relation"), "| rel_rule:", a.get("relation_rule"))
