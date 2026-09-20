#!/usr/bin/env python3
"""Blast-radius scan for planned RC3.3 fix plans F-I (read-only)."""
import json
import re
import sys

sys.path.insert(0, ".")
from engine_local import engine  # noqa: E402
from engine_local.numeric import (  # noqa: E402
    derived_quantities, numeric_relation, parse_quantities)
from engine_local.proposition import content_tokens  # noqa: E402


def spans_of(c):
    return [s if isinstance(s, dict) else {"span_id": "S%d" % j, "text": s}
            for j, s in enumerate(c.get("evidence") or [])]


def text_of(c):
    return c.get("claim") or ""


cases = json.load(open("fresh-cases.json"))["cases"]

rule_hits = {}
r25_entails = []
for c in cases:
    cid = c["case_id"]
    text, spans = text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    res = engine.evaluate_atom(text, spans)
    rule = res.get("rule") or ""
    rel = res.get("relation") or res.get("verdict")
    rule_hits.setdefault(rule, []).append(cid)
    if rule == "R25-coverage" and rel == "ENTAILS":
        ct = content_tokens(text)
        et = content_tokens(all_text)
        first = ct[0] if ct else "?"
        matched = any(engine._mtok(first, u) for u in et)
        ev_kan = bool(re.search(r"\bkan\b", all_text.lower()))
        cl_kan = bool(re.search(r"\bkan\b", text.lower()))
        r25_entails.append((cid, first, matched, ev_kan, cl_kan,
                            text[:60]))

print("== RL-polarity-opposition hits ==")
print(rule_hits.get("RL-polarity-opposition", []))
print()
print("== NOT_REQUIRED claim + uten/ingen evidence ==")
print("== claim 'ikke krav' style + ev 'uten X' ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    if (re.search(r"ikke krav|ikke nodvendig|ikke obligatorisk|krever "
                  r"ikke|frivillig", text.lower())
            and re.search(r"\b(uten|ingen)\b", all_text.lower())):
        print(cid, "| claim:", text[:60], "| ev:", all_text[:60])
print()
print("== med mindre on both sides + mirror ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    if (re.search(r"med mindre", text.lower())
            and re.search(r"med mindre|unntak", all_text.lower())):
        print(cid, "| mirror:", engine._negation_mirror(text, all_text),
              "| claim:", text[:60])
print()
print("== evidence 'kan selv' cases ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    if re.search(r"kan\s+selv|selv\s+(?:samtykke|bestemme)",
                 all_text.lower()):
        res = engine.evaluate_atom(text, spans)
        print(cid, "claim_alltid:", bool(re.search(r"alltid", text.lower())),
              "pred:", res["verdict"], "| claim:", text[:55])
print()
print("== cov>=HIGH ENTAILS battery cases: first-token/role check ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    res = engine.evaluate_atom(text, spans)
    rel = res.get("relation") or res.get("verdict")
    if rel == "ENTAILS":
        ct = engine.content_tokens(text)
        et = set(engine.content_tokens(all_text))
        first = ct[0] if ct else None
        if first and not any(engine._mtok(first, u) for u in et):
            print(cid, "first-unmatched:", first, "| ev:", all_text[:60])
print("== selected rule distribution ==")
for r, ids in sorted(rule_hits.items()):
    if r and any(k in r for k in ("RL-polarity", "R25", "RL-evidence",
                                  "RL-dim-modality-licensed")):
        print(r, ids)
print()
print("== R25-coverage ENTAILS (cid, first, matched, ev_kan, cl_kan) ==")
for row in r25_entails:
    print(row)
print()
print("== men ikke / men bare / enkelte across all cases ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    et = " ".join(s["text"] for s in spans).lower()
    flags = []
    if re.search(r"men ikke|men bare", et):
        flags.append("EV-MEN")
    if re.search("enkelte", et):
        flags.append("EV-ENKELTE")
    if re.search(r"men ikke|men bare", text.lower()):
        flags.append("CLAIM-MEN")
    if flags:
        res = engine.evaluate_atom(text, spans)
        print(cid, flags, "pred=", res.get("verdict"),
              "rule=", res.get("rule"), "|", text[:55])
print()
print("== evidence-kan ENTAILS cases ==")
for c in cases:
    cid, text, spans = c["case_id"], text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    res = engine.evaluate_atom(text, spans)
    rel = res.get("relation") or res.get("verdict")
    if (rel == "ENTAILS" and re.search(r"\bkan\b", all_text.lower())
            and not re.search(r"\bkan\b", text.lower())):
        print(cid, "rule=", res.get("rule"), "| claim:", text[:55],
              "| ev:", all_text[:70])
print()
print("== numeric candidates for failing numeric cases ==")
for want in ("R33-077", "R33-110", "R33-113", "R33-120", "R33-090"):
    c = next(x for x in cases if x["case_id"] == want)
    text, spans = text_of(c), spans_of(c)
    all_text = " ".join(s["text"] for s in spans)
    print("--", want, "CLAIM:", text)
    for q in parse_quantities(text):
        print("  CQ", q["quantity_type"], q["value"], q["comparator"],
              q.get("range_bounds"), q["object_binding"], q["role"])
    eqs = parse_quantities(all_text) + derived_quantities(all_text)
    for q in eqs:
        print("  EQ", q["quantity_type"], q["value"], q["comparator"],
              q.get("range_bounds"), q["object_binding"], q["role"],
              q["derivation"])
    print("  numeric_relation:", numeric_relation(text, all_text))
