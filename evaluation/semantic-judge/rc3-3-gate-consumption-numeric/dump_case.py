#!/usr/bin/env python3
"""Diagnostic: dump claim, evidence, gold and prediction for case IDs."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_local.engine import evaluate_case  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(ROOT, "fresh-cases.json")))["cases"]
ids = sys.argv[1:] or ["R33-002"]
for cid in ids:
    c = next(x for x in cases if x["case_id"] == cid)
    r = evaluate_case(c)
    print("=" * 30, cid, "=" * 30)
    print("CLAIM:", c["claim"])
    print("GOLD:", c["rel"])
    print("PRED:", r["verdict"], "|", r["atoms"][0].get("relation_rule"))
    for s in c["evidence"]:
        print("  SPAN:", s["text"])
