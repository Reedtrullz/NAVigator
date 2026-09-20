#!/usr/bin/env python3
"""Per-case internals probe for RC3.3 fix plans A-I (read-only)."""
import json
import sys

sys.path.insert(0, ".")
from engine_local import engine  # noqa: E402
from engine_local.numeric import (  # noqa: E402
    _best_binding, _compare, _compare_coverage, _identity, _aggregate_ok,
    numeric_relation, parse_quantities, derived_quantities)


CASES = ["R33-050", "R33-057", "R33-073", "R33-085", "R33-134", "R33-033",
         "R33-053"]

cases = {c["case_id"]: c for c in json.load(open("fresh-cases.json"))["cases"]}

for cid in CASES:
    c = cases[cid]
    text = c["claim"]
    spans = c["evidence"]
    all_text = " ".join(s["text"] for s in spans)
    res = engine.evaluate_atom(text, spans)
    dims = res.get("boundary") or {}
    de = dims.get("dimension_evidence") or {}
    print("==", cid, "gold:", c["rel"], "pred:", res["verdict"],
          "rule:", res.get("rule"), "rel:", res.get("relation"),
          "rel_rule:", res.get("relation_rule"))
    print("   claim:", text)
    print("   evid :", all_text)
    print("   dims overall:", dims.get("overall"),
          "blocking:", dims.get("blocking_dimensions"))
    for dname in ("polarity", "modality", "condition", "actor", "scope",
                  "clause_coverage"):
        d = de.get(dname) or {}
        if d.get("state"):
            print("   dim", dname, "=", d.get("state"), "rule:",
                  d.get("rule"))
    nrel = numeric_relation(text, all_text)
    if nrel:
        print("   numeric:", nrel)
        cqs = parse_quantities(text)
        eqs = parse_quantities(all_text) + derived_quantities(all_text)
        if cqs and eqs:
            for i, cq in enumerate(cqs):
                cands = [eq for eq in eqs
                         if _identity(cq, eq) and _aggregate_ok(cq, eq, eqs)]
                if not cands:
                    print("   CQ%d %s %s: no cands" %
                          (i, cq["quantity_type"], cq["comparator"]))
                    continue
                eq = _best_binding(cq, cands)
                cov = _compare_coverage(cq, eq, text)
                print("   CQ%d %s %s %s bind=%r -> eq %s %s %s bind=%r"
                      " cov=%s cmp=%s" %
                      (i, cq["quantity_type"], cq["comparator"],
                       cq["value"], cq["object_binding"],
                       eq["quantity_type"], eq["comparator"], eq["value"],
                       eq["object_binding"], cov, _compare(cq, eq)))
    print()
