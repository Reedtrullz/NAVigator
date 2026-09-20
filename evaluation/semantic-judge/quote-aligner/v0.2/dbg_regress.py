#!/usr/bin/env python3
"""Debug: trace each regression through the v0.2 decision path."""
import json
import os
import sys

sys.path.insert(0, "..")
from probe_dev import FILES, BENCH, QA05  # noqa: E402

import polarity_engine as pe  # noqa: E402
import polarity_engine_v02 as E  # noqa: E402
from polarity_engine import _claim_strength_veto  # noqa: E402

regress = []
for name in FILES:
    with open(os.path.join(BENCH, name + ".json")) as f:
        claims = {c["id"]: c for c in json.load(f)["claims"]}
    with open(os.path.join(QA05, "qa05-results-%s.json" % name)) as f:
        old = {r["id"]: r for r in json.load(f)["results"]}
    for cid, c in claims.items():
        got = E.judge_claim(c["claim"], c["source"]["text"])["verdict"]
        exp = c["expected"]
        if old.get(cid, {}).get("verdict") == exp and got != exp:
            regress.append((name, cid, c, exp, got))

for name, cid, c, exp, got in regress:
    src = c["source"]["text"]
    atoms = E.decompose_claim(c["claim"])
    print("== %s/%s exp=%s got=%s" % (name, cid, exp, got))
    print("   claim: %s" % c["claim"][:110])
    for i, a in enumerate(atoms, 1):
        base = pe.decide_atom(a, src)
        rep = E.align_atom(a, src)
        cand = rep["candidates"][0] if rep["candidates"] else None
        sent = cand["sentence"] if cand else ""
        nc = E._new_contra(a, src)
        guard = E._contra_guard(a, src, base) if base["verdict"] == "CONTRADICTED" else None
        resc = E._rescue_support(a, src)
        print("   A%d base=%s/%s" % (i, base["verdict"], base.get("rule")))
        print("      score=%.3f neg=%s uc=%s cap=%s son=%s" % (
            cand["score"] if cand else -1, rep["negated"],
            E._uncovered_core(a, sent), E._claim_actor_present(a, sent),
            E._same_object_negation(a, sent) if sent else None))
        print("      new_contra=%s guard=%s rescue=%s veto=%s" % (
            nc[0] if nc else None, guard, resc[0] if resc else None,
            _claim_strength_veto(a, src, sent)[0]
            if _claim_strength_veto(a, src, sent) else None))
