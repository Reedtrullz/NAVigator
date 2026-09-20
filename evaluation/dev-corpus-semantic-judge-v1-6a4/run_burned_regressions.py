#!/usr/bin/env python3
"""V1.6A.4 burned regression: A4 classify() must be byte-identical to A3 on
the three legacy dimensions across all burned sets; forbidden_claim output is
diagnostic-only (no gate)."""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3")
sys.path.insert(0, A3)

from boundary_preclassifier import classify as a3_classify
from a4_boundary_preclassifier import classify as a4_classify


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_set(fix_path, gold_path, gold_key=None):
    fdoc = json.load(open(fix_path))
    fx = fdoc["fixtures"] if isinstance(fdoc, dict) and "fixtures" in fdoc else fdoc
    gdoc = json.load(open(gold_path))
    glist = gdoc["gold"] if isinstance(gdoc, dict) and "gold" in gdoc else gdoc
    gold = {}
    for x in glist:
        k = x.get(gold_key) if gold_key else x.get("id")
        gold[k] = x
    return fx, gold


def compare_set(name, fx, focus_key="focus_dimension"):
    legacy_dims = ("route_commitment", "uncertainty_behavior", "assertion_scope")
    mismatches = []
    diag = {"n": 0, "labels": {}}
    for x in fx:
        a3 = a3_classify(x["text"], x.get("criterion"))
        a4 = a4_classify(x["text"], x.get("criterion"))
        focus = x.get(focus_key, "route_commitment")
        d3, d4 = a3.get(focus, {}), a4.get(focus, {})
        if d3.get("label") != d4.get("label") or d3.get("abstained") != d4.get("abstained"):
            mismatches.append({"id": x["id"], "dim": focus,
                               "a3": d3.get("label"), "a4": d4.get("label")})
        for dim in legacy_dims:
            d3, d4 = a3.get(dim, {}), a4.get(dim, {})
            if d3.get("label") != d4.get("label") or d3.get("abstained") != d4.get("abstained"):
                mismatches.append({"id": x["id"], "dim": dim,
                                   "a3": d3.get("label"), "a4": d4.get("label")})
        fc = a4.get("forbidden_claim", {})
        diag["n"] += 1
        diag["labels"][fc.get("label", "MISSING")] = diag["labels"].get(fc.get("label", "MISSING"), 0) + 1
    return mismatches, diag


def run_set(artifact, basis, fix_path, gold_path, gold_key=None):
    fx, gold = load_set(fix_path, gold_path, gold_key)
    mismatches, diag = compare_set(basis, fx)
    doc = {
        "artifact": artifact,
        "run_type": "BURNED_REGRESSION_ONLY",
        "basis": basis,
        "a3_engine_sha256": sha(os.path.join(A3, "boundary_preclassifier.py")),
        "a4_engine_sha256": sha(os.path.join(HERE, "a4_boundary_preclassifier.py")),
        "fixtures": len(fx),
        "acceptance": "legacy three-dimension output byte-identical to A3; forbidden_claim diagnostic-only",
        "legacy_dimension_mismatches": mismatches,
        "legacy_regression_pass": len(mismatches) == 0,
        "forbidden_claim_diagnostic": diag,
        "hard_gates": {
            "legacy_byte_identical": len(mismatches) == 0,
        },
        "all_gates_pass": len(mismatches) == 0,
    }
    out = os.path.join(HERE, artifact + ".json")
    with open(out, "w") as fh:
        fh.write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print("%s: fixtures=%d legacy_mismatches=%d pass=%s fc_diag=%s" % (
        artifact, len(fx), len(mismatches), doc["all_gates_pass"], diag["labels"]))
    return doc["all_gates_pass"]


if __name__ == "__main__":
    ok = True
    ok &= run_set(
        "burned-120-regression", "120 burned V1.6A fixtures (BURNED_PRECLASSIFIER_DEVELOPMENT_DATA)",
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a", "boundary-validation-fixtures.json"),
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a", "boundary-validation-gold-v1-6a.json"))
    ok &= run_set(
        "burned-targeted60-regression", "60 burned V1.6A.1 targeted fixtures (BURNED_DIAGNOSTIC_DATA)",
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a1", "targeted-validation-fixtures.json"),
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a1", "targeted-validation-gold.json"))
    ok &= run_set(
        "burned-v1-6a2-80-regression", "80 burned official V1.6A.2 fixtures (BURNED_BOUNDARY_DIAGNOSTIC_DATA)",
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a2", "official-validation-fixtures.json"),
        os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a2", "official-validation-gold.json"),
        gold_key="fixture_id")
    print("BURNED_REGRESSIONS_" + ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)
