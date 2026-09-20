#!/usr/bin/env python3
"""Diagnostic: dump boundary dimension evidence for failing cases."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_local.boundary import compare  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(ROOT, "fresh-cases.json")))["cases"]
ids = sys.argv[1:] or ["R33-002"]
for cid in ids:
    c = next(x for x in cases if x["case_id"] == cid)
    all_text = " ".join(s["text"] for s in c["evidence"])
    d = compare(c["claim"], all_text)
    de = d.get("dimension_evidence") or {}
    print(cid, d["overall"], "|", c["claim"][:70])
    for k, v in de.items():
        print("   ", k, v.get("state"), "|", v.get("rule"))
