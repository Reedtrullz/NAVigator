#!/usr/bin/env python3
"""Full-set regression check: v0.2 vs qa05 baselines.
regression = qa05 verdict correct, v0.2 verdict wrong
residual   = qa05 verdict already wrong, v0.2 still wrong
Usage: python3 check_regress.py [-v]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from probe_dev import FILES, BENCH, QA05  # noqa: E402

import polarity_engine_v02 as E  # noqa: E402

regress, residual = [], []
for name in FILES:
    with open(os.path.join(BENCH, name + ".json"), encoding="utf-8") as f:
        claims = {c["id"]: c for c in json.load(f)["claims"]}
    with open(os.path.join(QA05, "qa05-results-%s.json" % name),
              encoding="utf-8") as f:
        old = {r["id"]: r for r in json.load(f)["results"]}
    for cid, c in claims.items():
        got = E.judge_claim(c["claim"], c["source"]["text"])["verdict"]
        exp = c["expected"]
        o = old.get(cid, {}).get("verdict")
        if o == exp and got != exp:
            regress.append((name, cid, exp, got, c["claim"]))
        elif o != exp and got != exp:
            residual.append((name, cid, exp, got, c["claim"]))

print("REGRESSIONS: %d" % len(regress))
for name, cid, exp, got, claim in regress:
    print("  %-24s %-8s exp=%-22s got=%s" % (name, cid, exp, got))
    if "-v" in sys.argv:
        print("      claim: %s" % claim[:120])
print("RESIDUALS: %d" % len(residual))
for name, cid, exp, got, claim in residual:
    print("  %-24s %-8s exp=%-22s got=%s" % (name, cid, exp, got))
    if "-v" in sys.argv:
        print("      claim: %s" % claim[:120])
