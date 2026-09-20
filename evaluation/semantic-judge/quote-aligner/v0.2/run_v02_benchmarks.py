#!/usr/bin/env python3
"""Benchmark harness for polarity engine v0.2.
Reuses the frozen v0.5 harness structure; outputs qa06-* under v0.2/results.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import polarity_engine_v02 as E  # noqa: E402

V041 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "v0.4.1")
BENCH_DIR = os.path.join(V041, "benchmarks")
BENCHES = ["minimal-pairs", "minimal-pairs-supplement", "contra-insuff",
           "modality", "actor-scope", "locality", "diagnostic-20"]


def grade(results):
    rows = [r for r in results["results"] if r.get("status") == "ok"]
    confusion = {}
    high_conf_errors = []
    per_dim = {}
    for r in rows:
        expected, got = r["expected"], r["verdict"]
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
        "confusion": {"%s->%s" % (e, g): v
                      for (e, g), v in sorted(confusion.items())},
        "per_dimension": per_dim,
        "high_confidence_errors": high_conf_errors,
    }


def run_bench(name, runs=1):
    with open(os.path.join(BENCH_DIR, name + ".json"), encoding="utf-8") as f:
        claims = json.load(f)["claims"]
    results = {"meta": {
        "set": name, "engine": "quote-aligner-deterministic-v0.2",
        "generated": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "deterministic": True,
    }, "results": []}
    for run in range(1, runs + 1):
        for c in claims:
            try:
                res = E.judge_claim(c["claim"], c["source"]["text"])
                row = {"id": c["id"], "run": run,
                       "expected": c["expected"],
                       "dimension": c.get("dimension"),
                       "focus": c.get("focus"), "note": c.get("note"),
                       **res, "status": "ok"}
            except Exception as exc:
                row = {"id": c["id"], "run": run,
                       "expected": c["expected"],
                       "status": "error: %s" % exc}
            results["results"].append(row)
    return results


def run_ent():
    base = os.path.dirname(os.path.dirname(HERE))
    with open(os.path.join(base, "ent-controls-set.json"), encoding="utf-8") as f:
        claims = json.load(f)
    with open(os.path.join(base, "ent-controls-expected.json"),
              encoding="utf-8") as f:
        expected = json.load(f).get("expected", {})
    claims_list = claims["claims"] if isinstance(claims, dict) else claims
    results = {"meta": {"set": "ent-controls",
                        "engine": "quote-aligner-deterministic-v0.2"},
               "results": []}
    for c in claims_list:
        exp = (expected.get(c["id"]) or {}).get("verdict")
        try:
            res = E.judge_claim(c["claim"], c["source"]["text"])
            results["results"].append({"id": c["id"], "run": 1,
                                       "expected": exp, **res,
                                       "status": "ok"})
        except Exception as exc:
            results["results"].append({"id": c["id"], "run": 1,
                                       "expected": exp,
                                       "status": "error: %s" % exc})
    return results


def main():
    outdir = os.path.join(HERE, "results")
    os.makedirs(outdir, exist_ok=True)
    summary = {}
    for name in BENCHES:
        results = run_bench(name)
        g = grade(results)
        summary[name] = g
        with open(os.path.join(outdir, "qa06-results-%s.json" % name),
                  "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        with open(os.path.join(outdir, "qa06-%s-grade.json" % name),
                  "w", encoding="utf-8") as f:
            json.dump({"bench": name, **g}, f, ensure_ascii=False, indent=1)
        print("== %s: n=%s acc=%s contraP=%s insufR=%s fpSup=%s" % (
            name, g["n"], g["accuracy"], g["contradiction_precision"],
            g["insufficiency_recall"], g["binary_false_support"]), flush=True)
    results = run_ent()
    g = grade(results)
    summary["ent"] = g
    with open(os.path.join(outdir, "qa06-results-ent.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    with open(os.path.join(outdir, "qa06-ent-grade.json"), "w",
              encoding="utf-8") as f:
        json.dump({"bench": "ent", **g}, f, ensure_ascii=False, indent=1)
    print("== ent: n=%s acc=%s" % (g["n"], g["accuracy"]), flush=True)
    ent_rows = [r for r in results["results"] if r.get("status") == "ok"]
    ent_ok = sum(1 for r in ent_rows if r["verdict"] == r["expected"])
    print("ENT pass: %d/%d" % (ent_ok, len(ent_rows)))
    with open(os.path.join(outdir, "qa06-summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
