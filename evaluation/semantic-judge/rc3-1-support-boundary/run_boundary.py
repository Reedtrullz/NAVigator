"""Boundary harness for the RC3.1 engine (provenance-logged).
 
Frozen operationalization of the metrics in boundary-metrics-v1.json:
 
- A proof is AUTO_SUPPORTED-eligible iff the atom verdict is ENTAILS and
  (when the engine reports a boundary) overall == BOUNDARY_COMPATIBLE.
- FALSE_AUTO_SUPPORT_BOUNDARY: eligible proofs on cases whose expected_support
  is INCOMPATIBLE or UNRESOLVED.
- support_boundary_precision: eligible proofs on COMPATIBLE cases / all eligible.
- entailed_support_recall: eligible proofs on COMPATIBLE cases / all COMPATIBLE.
- Subgroup accuracy (strict class match):
    COMPATIBLE   correct iff eligible
    INCOMPATIBLE correct iff blocked from auto AND classified CONTRADICTS
    UNRESOLVED   correct iff AMBIGUOUS or boundary BOUNDARY_UNRESOLVED
  Blocked-but-unclassified outcomes (RBI/UNRELATED on INCOMPATIBLE cases) count
  as incorrect: the boundary must be explicit, not merely rejected.
"""
import hashlib
import json
import os
import platform
import sys
from collections import Counter
 
HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.abspath(os.path.join(HERE, "..", "rc3-1-proof-semantics"))
sys.path.insert(0, PROOF_DIR)
 
import rc3_1_engine.engine as engine  # noqa: E402
 
 
def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
 
 
def provenance():
    return {
        "engine_file": engine.__file__,
        "engine_sha256": sha256(engine.__file__),
        "engine_version": getattr(engine, "__version__", "unversioned"),
        "python_version": platform.python_version(),
    }
 
 
def eligible(verdict, boundary):
    if verdict != "ENTAILS":
        return False
    if boundary is None:
        return True
    return boundary.get("overall") == "BOUNDARY_COMPATIBLE"
 
 
def unresolved(verdict, boundary):
    if verdict == "AMBIGUOUS":
        return True
    return boundary is not None and boundary.get("overall") == "BOUNDARY_UNRESOLVED"
 
 
def run_fresh_suite(cases):
    rows = []
    for c in cases:
        r = engine.evaluate_case({"case_id": c["case_id"], "claim": c["claim"],
                                  "evidence": c["evidence"]})
        a = r["atoms"][0]
        v, b = a["verdict"], a.get("boundary")
        el = eligible(v, b)
        exp = c["expected_support"]
        ok = ((exp == "COMPATIBLE" and el)
              or (exp == "INCOMPATIBLE" and not el and v == "CONTRADICTS")
              or (exp == "UNRESOLVED" and unresolved(v, b)))
        rows.append({"case_id": c["case_id"], "group": c["group"],
                     "expected": exp, "verdict": v, "rule": a["rule"],
                     "boundary": b, "eligible": el, "correct": ok})
    el_rows = [r for r in rows if r["eligible"]]
    comp = [r for r in rows if r["expected"] == "COMPATIBLE"]
    metrics = {
        "FALSE_AUTO_SUPPORT_BOUNDARY": sum(1 for r in el_rows
                                           if r["expected"] != "COMPATIBLE"),
        "support_boundary_precision": (sum(1 for r in el_rows
                                           if r["expected"] == "COMPATIBLE")
                                       / len(el_rows)) if el_rows else None,
        "entailed_support_recall": (sum(1 for r in el_rows
                                        if r["expected"] == "COMPATIBLE")
                                    / len(comp)) if comp else None,
    }
    for g in sorted({r["group"] for r in rows}):
        sub = [r for r in rows if r["group"] == g]
        metrics[g + "_boundary_accuracy"] = (sum(1 for r in sub if r["correct"])
                                             / len(sub))
    return {"n": len(rows), "metrics": metrics, "rows": rows,
            "outcome_counts": dict(Counter(r["verdict"] for r in rows))}
 
 
def run_train(cases):
    rows = []
    correct = 0
    unsound_eligible = 0
    unsound_rows = []
    for c in cases:
        r = engine.evaluate_case(c)
        exp = c["rel"]
        got = r["verdict"]
        if exp == got:
            correct += 1
        # AUTO_SUPPORTED is authorized at product level: top ENTAILS with
        # every atom boundary-compatible. An entailed atom inside a
        # PARTIAL/CONTRADICTS product never reaches auto-support.
        if (r["verdict"] == "ENTAILS" and exp != "ENTAILS"
                and all(a.get("boundary", {}).get("overall")
                        == "BOUNDARY_COMPATIBLE" for a in r["atoms"])):
            unsound_eligible += 1
            unsound_rows.append({"case_id": c["case_id"],
                                 "verdict": r["verdict"]})
        rows.append({"case_id": c["case_id"], "expected": exp, "got": got,
                     "rules": [a["rule"] for a in r["atoms"]]})
    n = len(cases)
    return {"n": n, "relation_correct": correct,
            "relation_accuracy": correct / n,
            "unsound_eligible_support_atoms": unsound_eligible,
            "unsound_rows": unsound_rows,
            "rows": rows}
 
 
def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "baseline-results.json"
    fresh = json.load(open(os.path.join(HERE, "fresh-boundary-cases.json"),
                           encoding="utf-8"))
    train = json.load(open(os.path.join(PROOF_DIR, "corpus", "train-cases.json"),
                           encoding="utf-8"))
    fresh_res = run_fresh_suite(fresh["cases"])
    train_res = run_train(train["cases"])
    result = {"provenance": provenance(), "fresh_suite": fresh_res,
              "burned_train": train_res}
    with open(os.path.join(HERE, out_path), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({"provenance": result["provenance"],
                      "fresh_metrics": fresh_res["metrics"],
                      "fresh_outcomes": fresh_res["outcome_counts"],
                      "train_accuracy": train_res["relation_accuracy"],
                      "train_unsound_eligible":
                          train_res["unsound_eligible_support_atoms"]},
                     ensure_ascii=False, indent=1))
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
