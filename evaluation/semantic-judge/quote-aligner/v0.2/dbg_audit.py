#!/usr/bin/env python3
"""Audit: which v0.2 mechanisms carry each currently-correct verdict."""
import json
import os
import sys

sys.path.insert(0, "..")
from probe_dev import FILES, BENCH, QA05  # noqa: E402

import polarity_engine as pe  # noqa: E402
import polarity_engine_v02 as E  # noqa: E402

usage = {}
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
            rep = E.align_atom(a, src)
            if not rep["candidates"]:
                continue
            sent = rep["candidates"][0]["sentence"]
            score = rep["candidates"][0]["score"]
            uc = E._uncovered_core(a, sent)
            cap = E._claim_actor_present(a, sent)
            resc = E._rescue_support(a, src)
            guard = (E._contra_guard(a, src, base)
                     if base["verdict"] == "CONTRADICTED" else None)
            hedge = (E._any_form(E._fold(E.strip_parens(a)),
                                 E.LEX["hedge_modifiers"])
                     and E._any_form(E._fold(E.strip_parens(sent)),
                                     E.LEX["hedge_modifiers"]))
            pure_cov = bool(
                resc and not uc and not cap
                and not E._staff_support(a, sent)
                and pe._numeric_state(a, sent, src)[0] != "equal"
                and not hedge)
            weak_cap = bool(resc and uc and cap and score < 0.6)
            flags = (
                ("no_guard_rescue", resc and
                 base["verdict"] == "CONTRADICTED" and not guard),
                ("pure_cov", pure_cov),
                ("weak_cap", weak_cap),
                ("guard_neg", guard == "guard_negation_scope"),
                ("guard_other", guard and guard != "guard_negation_scope"),
            )
            for flag, on in flags:
                if on:
                    usage.setdefault(flag, []).append(
                        "%s/%s" % (name, c["id"]))
for flag in sorted(usage):
    ids = usage[flag]
    print("%s (%d): %s" % (flag, len(ids), " ".join(ids)))
