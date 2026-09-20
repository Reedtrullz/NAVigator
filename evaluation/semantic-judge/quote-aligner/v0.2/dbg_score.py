#!/usr/bin/env python3
"""Debug: align-score discrimination between gold-SUP and FP-SUP rescues."""
import json
import os
import sys

sys.path.insert(0, "..")
from probe_dev import load_misses, FILES, BENCH  # noqa: E402

import polarity_engine_v02 as E  # noqa: E402
from polarity_engine import _claim_strength_veto  # noqa: E402

GOLD = {"ACT-08", "ACT-10", "ACT-19", "ACT-23", "D20-A5", "MOD-14"}
FP = {"ACT-27", "LOC-17", "ACT-06", "ACT-24", "D20-L3", "CI-043",
      "CI-054", "CI-057", "MP-001B", "MP-007B", "CI-039", "MOD-02",
      "D20-M4"}

for m in load_misses():
    if m["id"] not in GOLD | FP:
        continue
    for i, a in enumerate(E.decompose_claim(m["claim"]), 1):
        rep = E.align_atom(a, m["source"])
        if not rep["candidates"]:
            continue
        c = rep["candidates"][0]
        sent = c["sentence"]
        uc = E._uncovered_core(a, sent)
        cap = E._claim_actor_present(a, sent)
        tag = "GOLD" if m["id"] in GOLD else "FP"
        print("%s %-8s A%d score=%.3f uc=%s cap=%s resc=%s veto=%s" % (
            tag, m["id"], i, c["score"], uc, cap,
            bool(E._rescue_support(a, m["source"])),
            bool(_claim_strength_veto(a, m["source"], sent))))

FP_CLAIMS = {}
for name in FILES:
    with open(os.path.join(BENCH, name + ".json")) as f:
        for c in json.load(f)["claims"]:
            FP_CLAIMS[c["id"]] = (name, c)
for cid in sorted(FP):
    name, c = FP_CLAIMS[cid]
    src = c["source"]["text"]
    for i, a in enumerate(E.decompose_claim(c["claim"]), 1):
        rep = E.align_atom(a, src)
        if not rep["candidates"]:
            continue
        cc = rep["candidates"][0]
        sent = cc["sentence"]
        uc = E._uncovered_core(a, sent)
        cap = E._claim_actor_present(a, sent)
        print("FP   %-8s A%d score=%.3f uc=%s cap=%s resc=%s veto=%s son=%s" % (
            cid, i, cc["score"], uc, cap,
            bool(E._rescue_support(a, src)),
            bool(_claim_strength_veto(a, src, sent)),
            E._same_object_negation(a, sent)))
