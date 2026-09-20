#!/usr/bin/env python3
"""Select 32 pilot cases, stratified by primary kb_ref, from the label-free V2 pool."""
import glob
import json
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(HERE, "..", "..", "RC2-V2-set")
OUT = os.path.join(HERE, "pilot-input.json")

rows = []
for p in sorted(glob.glob(os.path.join(V2, "candidates-*.json"))):
    rows += json.load(open(p))["candidates"]

# deterministic: sort by case_id, round-robin across distinct primary kb_refs
rows.sort(key=lambda c: c["case_id"])
by_ref = OrderedDict()
for c in rows:
    ref = c["sources"][0]["kb_ref"]
    by_ref.setdefault(ref, []).append(c)

picked = []
refs = list(by_ref)
i = 0
while len(picked) < 32:
    bucket = by_ref[refs[i % len(refs)]]
    if bucket:
        picked.append(bucket.pop(0))
    i += 1

picked.sort(key=lambda c: c["case_id"])
payload = {
    "purpose": "RC2-V3 annotation pilot input (label-free, spec 13)",
    "count": len(picked),
    "cases": [{"case_id": c["case_id"], "claim": c["claim"], "sources": c["sources"]}
              for c in picked],
}
with open(OUT, "w") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)
print(f"selected {len(picked)} cases across {len(set(c['sources'][0]['kb_ref'] for c in picked))} kb_refs -> {OUT}")
print("ids:", ", ".join(c["case_id"] for c in picked))

