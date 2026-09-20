#!/usr/bin/env python3
"""Deterministic benchmark harness for the quote-aligner polarity engine.
Reads frozen v0.4.1 benchmark sets read-only; no model calls anywhere.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polarity_engine as pe

V041 = os.path.join(os.path.dirname(HERE), "v0.4.1")
V03 = os.path.join(os.path.dirname(HERE), "v0.3")
BENCH_DIR = os.path.join(V041, "benchmarks")
BENCHES = ["minimal-pairs", "minimal-pairs-supplement", "contra-insuff",
           "modality", "actor-scope", "locality", "diagnostic-20"]


def grade(results):
    rows = [r for r in results["results"] if r.get("status") == "ok"]
    confusion = {}
    high_conf_errors = []
    per_dim = {}
    for r in rows:
        expected = r["expected"]
        got = r["verdict"]
        confusion[(expected, got)] = confusion.get((expected, got), 0) + 1
        d = per_dim.setdefault(r.get("dimension") or r.get("focus") or "all",
                               {"n": 0, "ok": 0})
        d["n"] += 1
        if got == expected:
            d["ok"] += 1
        elif float(r.get("confidence") or 0) >= 0.95:
            high_conf_errors.append({"id": r["id"], "expected": expected,
                                     "got": got,
                                     "rule": (r.get("atom_results") or [{}])[0].get("rule")})
    correct = sum(v for (e, g), v in confusion.items() if e == g)
    pred_con = sum(v for (e, g), v in confusion.items() if g == "CONTRADICTED")
    tp_con = confusion.get(("CONTRADICTED", "CONTRADICTED"), 0)
    exp_ins = sum(v for (e, g), v in confusion.items()
                  if e == "INSUFFICIENT_EVIDENCE")
    tp_ins = confusion.get(("INSUFFICIENT_EVIDENCE", "INSUFFICIENT_EVIDENCE"), 0)
    fp_support = sum(v for (e, g), v in confusion.items()
                     if g == "SUPPORTED" and e != "SUPPORTED")
    return {
        "n": len(rows),
        "accuracy": round(correct / len(rows), 4) if rows else None,
        "contradiction_precision": round(tp_con / pred_con, 4) if pred_con else None,
        "insufficiency_recall": round(tp_ins / exp_ins, 4) if exp_ins else None,
        "binary_false_support": fp_support,
        "confusion": {f"{e}->{g}": v for (e, g), v in sorted(confusion.items())},
        "per_dimension": per_dim,
        "high_confidence_errors": high_conf_errors,
    }


def run_bench(name, runs=1):
    with open(os.path.join(BENCH_DIR, name + ".json"), encoding="utf-8") as f:
        claims = json.load(f)["claims"]
    results = {"meta": {
        "set": name, "engine": "quote-aligner-deterministic",
        "version": "semantic-judge-quote-aligner-v0.5-prototype",
        "generated": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "deterministic": True,
    }, "results": []}
    for run in range(1, runs + 1):
        for c in claims:
            try:
                res = pe.judge_claim(c["claim"], c["source"]["text"])
                row = {"id": c["id"], "run": run,
                       "expected": c["expected"],
                       "dimension": c.get("dimension"),
                       "focus": c.get("focus"), "note": c.get("note"),
                       **res, "status": "ok"}
            except Exception as exc:
                row = {"id": c["id"], "run": run,
                       "expected": c["expected"],
                       "status": f"error: {exc}"}
            results["results"].append(row)
    return results


def run_ent():
    with open(os.path.join(os.path.dirname(HERE), "ent-controls-set.json"),
              encoding="utf-8") as f:
        claims = json.load(f)
    with open(os.path.join(os.path.dirname(HERE),
                           "ent-controls-expected.json"),
              encoding="utf-8") as f:
        expected = json.load(f).get("expected", {})
    claims_list = claims["claims"] if isinstance(claims, dict) else claims
    results = {"meta": {"set": "ent-controls", "engine": "quote-aligner-deterministic"},
               "results": []}
    for c in claims_list:
        cid = c["id"]
        exp = (expected.get(cid) or {}).get("verdict") if isinstance(expected, dict) else expected.get(cid)
        try:
            res = pe.judge_claim(c["claim"], c["source"]["text"] if isinstance(c.get("source"), dict) else c.get("source", ""))
            row = {"id": cid, "run": 1, "expected": exp, **res,
                   "status": "ok"}
        except Exception as exc:
            row = {"id": cid, "run": 1, "expected": exp,
                   "status": f"error: {exc}"}
        results["results"].append(row)
    return results


def run_stability(runs=5):
    with open(os.path.join(V03, "stability-set.json"), encoding="utf-8") as f:
        claims = json.load(f)["claims"]
    with open(os.path.join(V03, "expected-stability.json"),
              encoding="utf-8") as f:
        expected = json.load(f)["expected"]
    results = {"meta": {"set": "stability", "runs": runs,
                        "engine": "quote-aligner-deterministic"},
               "results": []}
    run_hashes = []
    for run in range(1, runs + 1):
        run_rows = []
        for c in claims:
            res = pe.judge_claim(c["claim"], c["source"]["text"])
            row = {"id": c["id"], "run": run,
                   "expected": expected[c["id"]]["verdict"],
                   **res, "status": "ok"}
            results["results"].append(row)
            run_rows.append(row)
        # Exclude the run counter so identical verdicts hash identically.
        payload = [{k: v for k, v in row.items() if k != "run"}
                   for row in run_rows]
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        run_hashes.append(hashlib.sha256(blob.encode()).hexdigest())
    results["meta"]["run_hashes"] = run_hashes
    results["meta"]["identical_across_runs"] = len(set(run_hashes)) == 1
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default="all",
                    choices=BENCHES + ["ent", "stability", "all"])
    args = ap.parse_args()
    todo = BENCHES + ["ent", "stability"] if args.bench == "all" else [args.bench]
    summary = {}
    for name in todo:
        if name == "ent":
            results = run_ent()
        elif name == "stability":
            results = run_stability(runs=5)
        else:
            results = run_bench(name)
        g = grade(results)
        if name == "stability":
            g["identical_across_runs"] = results["meta"]["identical_across_runs"]
        summary[name] = g
        out = os.path.join(HERE, "results",
                           f"qa05-results-{name}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        with open(os.path.join(HERE, "results", f"qa05-{name}-grade.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"bench": name, **g}, f, ensure_ascii=False, indent=1)
        print(f"== {name}: n={g['n']} acc={g['accuracy']} "
              f"contraP={g['contradiction_precision']} "
              f"insufR={g['insufficiency_recall']} "
              f"fpSup={g['binary_false_support']}", flush=True)
    with open(os.path.join(HERE, "results", "qa05-summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: {"accuracy": v["accuracy"], "n": v["n"]}
                      for k, v in summary.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
