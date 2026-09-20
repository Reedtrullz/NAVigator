#!/usr/bin/env python3
# Runs the operator regression corpus; writes results.json. Exit 1 on drift.
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T1 = os.path.join(os.path.dirname(HERE), "tier1-proof")
sys.path.insert(0, T1)

import tier1_operators as ops
import proof_validator as pv


def evaluate(case):
    claim, src = case["claim"], case["source"]
    proofs, crashed = ops.run_operators(claim, src)
    valid = [p for p in proofs if pv.validate(p, claim, src)[0]]
    results = sorted({p["result"] for p in valid})
    contra = [p for p in valid if p["result"] == "CONTRADICTED"]
    expect = case["expect"]
    if expect == "conflict:REVIEW":
        return len(results) > 1
    if expect == "no-contradiction":
        return not contra and not crashed
    if expect == "abstain":
        return not valid and not crashed
    if expect.startswith("fire:"):
        want = expect.split(":", 1)[1]
        return results == [want] and not crashed
    return False


def main():
    cases = json.load(open(os.path.join(HERE, "cases.json")))
    out = {"n": len(cases), "pass": 0, "fail": 0, "results": []}
    for c in cases:
        ok = evaluate(c)
        out["pass" if ok else "fail"] += 1
        out["results"].append({"id": c["id"], "expect": c["expect"],
                               "pass": ok})
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"),
              ensure_ascii=False, indent=1)
    print("PASS", out["pass"], "FAIL", out["fail"])
    for r in out["results"]:
        if not r["pass"]:
            print("  DRIFT:", r["id"], "expected", r["expect"])
    sys.exit(1 if out["fail"] else 0)


if __name__ == "__main__":
    main()
