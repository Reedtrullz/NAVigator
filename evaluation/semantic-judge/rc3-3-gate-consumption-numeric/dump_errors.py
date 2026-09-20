#!/usr/bin/env python3
"""Diagnostic: dump every suite error with its fired rule."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_local.engine import evaluate_case  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(ROOT, "fresh-cases.json")))["cases"]
for c in cases:
    r = evaluate_case(c)
    rels = [a.get("relation") or a["verdict"] for a in r["atoms"]]
    gold = c.get("atom_rel") or [c["rel"]] * len(rels)
    if rels == gold:
        continue
    for a in r["atoms"]:
        print(c["case_id"], "gold=" + c["rel"],
              "pred=" + (a.get("relation") or a["verdict"]),
              "rule=" + a.get("rule", "?"),
              "|", c["claim"][:70])
    print()
