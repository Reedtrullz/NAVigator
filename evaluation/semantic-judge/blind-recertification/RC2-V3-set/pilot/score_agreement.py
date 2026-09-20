#!/usr/bin/env python3
"""Score pilot agreement between two independent annotation passes (spec 13)."""
import json
import os
import sys

SLOTS = ("semantic_truth", "proof_safe", "product_action")


def score(file_a, file_b):
    a = {r["case_id"]: r for r in json.load(open(file_a))}
    b = {r["case_id"]: r for r in json.load(open(file_b))}
    ids = sorted(set(a) & set(b))
    missing = sorted(set(a) ^ set(b))
    out = {"n_scored": len(ids), "missing_cases": missing, "slots": {}, "disagreements": {}}
    for slot in SLOTS:
        same = sum(1 for i in ids if a[i][slot] == b[i][slot])
        out["slots"][slot] = {
            "agreement": round(same / len(ids), 4) if ids else 0.0,
            "same": same, "n": len(ids),
        }
        dis = [(i, a[i][slot], b[i][slot]) for i in ids if a[i][slot] != b[i][slot]]
        out["disagreements"][slot] = dis
    return out


if __name__ == "__main__":
    r = score(sys.argv[1], sys.argv[2])
    print(json.dumps(r["slots"], indent=1))
    if r["missing_cases"]:
        print("MISSING:", r["missing_cases"])
    for slot, dis in r["disagreements"].items():
        if dis:
            print(f"--- {slot} disagreements ({len(dis)}) ---")
            for cid, x, y in dis:
                print(f"  {cid}: {x} vs {y}")
    gate = all(v["agreement"] >= 0.90 for v in r["slots"].values())
    print("GATE:", "PASS (>=0.90 all three)" if gate else "FAIL (<0.90 on at least one slot)")
    sys.exit(0 if gate else 1)

