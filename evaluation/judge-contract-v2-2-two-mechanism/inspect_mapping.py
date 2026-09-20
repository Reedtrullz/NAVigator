#!/usr/bin/env python3
"""Read-only: dump V2 gold verdicts with fixture text for mapping verification."""
import json

GOLD = "judge-selection-v2-subskill/judge-selection-gold.json"
FIX = {
    "a": "judge-selection-v2-subskill/family-a-fixtures.json",
    "b": "judge-selection-v2-subskill/family-b-fixtures.json",
    "c": "judge-selection-v2-subskill/family-c-fixtures.json",
}

gold = {g["fixture_id"]: g for g in json.load(open(GOLD))["gold"]}
fixtures = {}
for key, path in FIX.items():
    d = json.load(open(path))
    for f in d["fixtures"]:
        fixtures[f["id"]] = f

want = [w.strip().upper() for w in ("c-04 c-05 c-06 c-07 c-08 c-09 c-10 c-11 c-12 c-13 c-14 c-15 c-16 c-17 c-18 c-20").split()]
for fid in want:
    g = gold.get(fid)
    fx = fixtures.get(fid, {})
    if not g:
        print("===", fid, "MISSING")
        continue
    print("===", fid, g["dimension"], "gold:", g["verdict"])
    print("   crit:", fx.get("crit", "")[:170])
    print("   sut:", fx.get("sut", "")[:250])
