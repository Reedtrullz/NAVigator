#!/usr/bin/env python3
"""One-shot read-only helper: locate the seven burned V2.1 miss rows."""
import json

GOLD = "judge-selection-v2-subskill/judge-selection-gold.json"
FIXA = "judge-selection-v2-subskill/family-a-fixtures.json"
FIXC = "judge-selection-v2-subskill/family-c-fixtures.json"
MIMO = "judge-selection-v2-1-no-longcat/checkpoint-mimo-v2-5.json"
LING = "judge-selection-v2-1-no-longcat/checkpoint-ling-3-0-flash-sante-free.json"
SHARED = {"A-07", "A-13", "A-14", "A-18", "A-21", "A-23", "C-19"}

gold = {g["fixture_id"]: g for g in json.load(open(GOLD))["gold"]}
fixtures = {}
for path in (FIXA, FIXC):
    d = json.load(open(path))
    for f in d["fixtures"]:
        fixtures[f["id"]] = f
mimo = {r["id"]: r for r in json.load(open(MIMO))["rows"]}
ling = {r["id"]: r for r in json.load(open(LING))["rows"]}

for fid in sorted(SHARED, key=lambda x: (x[0], int(x.split("-")[1]))):
    g = gold[fid]
    m, l = mimo[fid], ling[fid]
    print("===", fid, g["dimension"], "gold:", g["verdict"])
    mv = m.get("result", {}).get("verdict") if isinstance(m.get("result"), dict) else m.get("verdict")
    lv = l.get("result", {}).get("verdict") if isinstance(l.get("result"), dict) else l.get("verdict")
    print("  mimo:", m.get("status"), mv, "| ling:", l.get("status"), lv)
    fx = fixtures.get(fid, {})
    print("  tag:", fx.get("tag"))
    print("  ctx:", fx.get("ctx", "")[:150])
    print("  crit:", fx.get("crit", "")[:250])
    print("  sut:", fx.get("sut", "")[:350])
    print("  why:", fx.get("why", "")[:200])
