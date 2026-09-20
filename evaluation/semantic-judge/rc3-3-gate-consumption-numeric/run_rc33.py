#!/usr/bin/env python3
"""RC3.3 runner: evaluate the fresh suite and report relation metrics."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from engine_local.engine import evaluate_case  # noqa: E402

UNRES = "NUMERIC_RELEVANT_BUT_UNRESOLVED"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def main():
    suite_path = os.path.join(ROOT, "fresh-cases.json")
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "results", "baseline-results.json")
    cases = json.load(open(suite_path))["cases"]
    out = {"suite": "RC3_3_RELATION_RESULTS", "cases": []}
    per_class = {}
    total = correct = 0
    for c in cases:
        r = evaluate_case(c)
        atom_rels = [a.get("relation") or a["verdict"] for a in r["atoms"]]
        gold_rels = c.get("atom_rel") or [c["rel"]] * len(atom_rels)
        total += len(gold_rels)
        for p, g in zip(atom_rels, gold_rels):
            per_class.setdefault(g, {"tp": 0, "fp": 0, "fn": 0})
            if p == g:
                correct += 1
                per_class[g]["tp"] += 1
            else:
                per_class[g]["fn"] += 1
                per_class.setdefault(p, {"tp": 0, "fp": 0, "fn": 0})
                per_class[p]["fp"] += 1
        out["cases"].append({"case_id": c["case_id"], "truth": c["rel"],
                             "verdict": r["verdict"],
                             "atom_relations": atom_rels})
    f1s = []
    for k, v in per_class.items():
        p = v["tp"] / (v["tp"] + v["fp"]) if v["tp"] + v["fp"] else 0.0
        r = v["tp"] / (v["tp"] + v["fn"]) if v["tp"] + v["fn"] else 0.0
        v["precision"] = round(p, 4)
        v["recall"] = round(r, 4)
        v["f1"] = round(2 * p * r / (p + r), 4) if p + r else 0.0
        if v["tp"] + v["fn"]:
            f1s.append(v["f1"])
    out["metrics"] = {
        "relation_accuracy": round(correct / max(1, total), 4),
        "macro_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        "per_class": per_class,
        "relation_total": total,
    }
    out["provenance"] = {
        "engine_sha256": sha256(os.path.join(ROOT, "engine_local",
                                             "engine.py")),
        "boundary_sha256": sha256(os.path.join(ROOT, "engine_local",
                                               "boundary.py")),
        "numeric_sha256": sha256(os.path.join(ROOT, "engine_local",
                                              "numeric.py")),
        "suite_sha256": sha256(suite_path),
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    m = out["metrics"]
    print("relation_accuracy:", m["relation_accuracy"])
    print("macro_f1:", m["macro_f1"])
    for k in sorted(per_class):
        v = per_class[k]
        print("  %-24s P=%.3f R=%.3f F1=%.3f (tp=%d fp=%d fn=%d)"
              % (k, v["precision"], v["recall"], v["f1"], v["tp"], v["fp"],
                 v["fn"]))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
