#!/usr/bin/env python3
"""Audit: currently-correct cases whose rescue survived via son-bypass."""
import json
import os
import sys

sys.path.insert(0, "..")
from probe_dev import FILES, BENCH  # noqa: E402

import polarity_engine as pe  # noqa: E402
import polarity_engine_v02 as E  # noqa: E402
from polarity_engine import _claim_strength_veto  # noqa: E402

hits = []
for name in FILES:
    with open(os.path.join(BENCH, name + ".json")) as f:
        claims = json.load(f)["claims"]
    for c in claims:
        if E.judge_claim(c["claim"], c["source"]["text"])["verdict"] \
                != c["expected"]:
            continue
        src = c["source"]["text"]
        for i, a in enumerate(E.decompose_claim(c["claim"]), 1):
            base = pe.decide_atom(a, src)
            if base["verdict"] != "CONTRADICTED" and \
                    base["verdict"] != "INSUFFICIENT_EVIDENCE":
                continue
            rep = E.align_atom(a, src)
            if not rep["candidates"]:
                continue
            sent = rep["candidates"][0]["sentence"]
            veto = _claim_strength_veto(a, src, sent)
            if not veto or veto[0] in E._PASS_VETO:
                continue
            if E._veto_explained(veto[0], a, sent):
                continue
            son = E._same_object_negation(a, sent)
            neg_eq = rep["negated"] == E._has_neg_wb(E.strip_parens(sent))
            lencap = (len(E._uncovered_core(a, sent)) <= 1
                      and E._claim_actor_present(a, sent))
            if son and neg_eq:
                hits.append((name, c["id"], i, base["verdict"],
                             base.get("rule"), veto[0]))
            elif lencap:
                hits.append((name, c["id"], i, base["verdict"],
                             base.get("rule"), veto[0] + " [len1cap]"))
for h in hits:
    print("%-24s %-8s A%d base=%s/%-30s veto=%s" % h)
