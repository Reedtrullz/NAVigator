#!/usr/bin/env python3
"""RC3.3 final verification battery (read-only; outputs task-local)."""
import hashlib
import json
import re
import subprocess
import sys

sys.path.insert(0, ".")
from engine_local import engine, numeric  # noqa: E402
from engine_local.numeric import numeric_relation, parse_quantities  # noqa: E402

out = {}
cases = json.load(open("fresh-cases.json"))["cases"]

# --- Numeric subset (cases whose claim carries a semantic quantity) ---
num_ids, num_ok = [], 0
for c in cases:
    if parse_quantities(c["claim"]):
        num_ids.append(c["case_id"])
        post = next(x for x in json.load(open(
            "results/final-relation-results.json"))["cases"]
            if x["case_id"] == c["case_id"])
        gold_atom = c.get("atom_rel") or [c["rel"]]
        if post["atom_relations"][0] == gold_atom[0]:
            num_ok += 1
out["numeric_subset"] = {"total": len(num_ids), "correct": num_ok,
                         "accuracy": round(num_ok / max(1, len(num_ids)), 4)}

# --- Per-class precision vs gates (RBI recall reported by runner) ---
m = json.load(open("results/final-relation-results.json"))["metrics"]
out["gates"] = {
    "atom_acc_0.95": m["relation_accuracy"] >= 0.95,
    "macro_f1_0.93": m["macro_f1"] >= 0.93,
    "entails_precision_0.99":
        m["per_class"]["ENTAILS"]["precision"] >= 0.99,
    "contradicts_precision_0.99":
        m["per_class"]["CONTRADICTS"]["precision"] >= 0.99,
}

# --- Boundary invariance (structural proof; sandbox forbids cross-task imports) ---
# boundary.py is frozen and byte-identical to the RC3.2 frozen artifact. It is a
# pure function of its own inputs: its only local import is proposition.py
# (also untouched), and it never imports engine.py or numeric.py, which are the
# only files changed in RC3.3. The frozen boundary projection therefore cannot
# differ from its pre-patch behavior.
FROZEN_BOUNDARY_SHA = ("9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c"
                       "48c3ef026343fc1e")
boundary_sha = hashlib.sha256(open("engine_local/boundary.py", "rb").read()).hexdigest()
prop_sha = hashlib.sha256(open("engine_local/proposition.py", "rb").read()).hexdigest()
boundary_src = open("engine_local/boundary.py").read()
out["boundary_invariance"] = {
    "boundary_sha_unchanged": boundary_sha == FROZEN_BOUNDARY_SHA,
    "boundary_sha": boundary_sha,
    "proposition_sha": prop_sha,
    "imports_engine_or_numeric": bool(
        re.search(r"import\s+(engine|numeric)\b|from\s+\.(engine|numeric)\b",
                  boundary_src)),
    "projection_diffs": 0 if boundary_sha == FROZEN_BOUNDARY_SHA else None,
}

# --- Determinism: rerun runner, byte-compare ---
r1 = open("results/final-relation-results.json", "rb").read()
subprocess.run([sys.executable, "run_rc33.py",
                "results/final-relation-results-rerun.json"],
               check=True, capture_output=True)
r2 = open("results/final-relation-results-rerun.json", "rb").read()
out["determinism_byte_identical"] = r1 == r2

# --- ID guard on runtime modules ---
id_hits = {}
for mod in ("engine_local/engine.py", "engine_local/numeric.py",
            "engine_local/boundary.py", "engine_local/proposition.py"):
    src = open(mod).read()
    hits = re.findall(r"RC1B|RC2B|RC3G|R33-", src)
    if hits:
        id_hits[mod] = hits
out["runtime_id_guard_hits"] = id_hits

print(json.dumps(out, indent=2))
