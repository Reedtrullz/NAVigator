#!/usr/bin/env python3
"""Run one or all v0.4 benchmarks and grade predicted vs expected.
Resumable via the same incremental results file the main CLI writes."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import semantic_judge_v04 as sj
import run_semantic_judge as base
judge_registry = {**base.JUDGES,
                  "C": {"model": "gpt-5.6-luna",
                        "label": "judge-c-gpt-5.6-luna"}}

BENCHES = ["minimal-pairs", "contra-insuff", "modality", "actor-scope",
           "locality"]


def grade(results):
    rows = [r for r in results["results"] if r.get("status") == "ok"]
    confusion = {}
    high_conf_errors = []
    per_dim = {}
    for r in rows:
        expected = r["expected"]
        got = r["verdict"]
        key = (expected, got)
        confusion[key] = confusion.get(key, 0) + 1
        d = per_dim.setdefault(r.get("dimension") or r.get("focus") or "all",
                               {"n": 0, "ok": 0})
        d["n"] += 1
        if got == expected:
            d["ok"] += 1
        elif float(r.get("confidence") or 0) >= 0.95:
            high_conf_errors.append({"id": r["id"], "expected": expected,
                                     "got": got,
                                     "confidence": r.get("confidence"),
                                     "relation": (r.get("atom_results") or [{}])[0]
                                       .get("relation", {}).get("relation_type")})
    correct = sum(v for (e, g), v in confusion.items() if e == g)
    return {"n": len(rows), "accuracy": round(correct / len(rows), 4) if rows else None,
            "confusion": {f"{e}->{g}": v for (e, g), v in sorted(confusion.items())},
            "per_dimension": per_dim,
            "high_confidence_errors": high_conf_errors}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default="all", choices=BENCHES + ["all"])
    ap.add_argument("--judge", default="A", choices=["A", "B", "C"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()
    benches = BENCHES if args.bench == "all" else [args.bench]
    judge = judge_registry[args.judge]
    home = base.build_home()
    summary = {}
    for bench in benches:
        with open(os.path.join(HERE, "benchmarks", bench + ".json"),
                  encoding="utf-8") as f:
            claims = json.load(f)["claims"]
        if args.ids:
            wanted = {x.strip() for x in args.ids.split(",")}
            claims = [c for c in claims if c["id"] in wanted]
        if args.limit:
            claims = claims[: args.limit]
        out_path = os.path.join(HERE, "results",
                                f"v04-results-{bench}-{args.judge}-{judge['label']}.json")
        results = {"meta": {
            "set": bench, "judge": args.judge, "model": judge["model"],
            "version": "semantic-judge-v0.4",
            "decompose_prompt_sha256": base.sha256_of(sj.DECOMPOSE_PROMPT),
            "relation_prompt_sha256": base.sha256_of(sj.RELATION_PROMPT),
            "generated": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc).isoformat(),
        }, "results": []}
        if os.path.exists(out_path):
            with open(out_path, encoding="utf-8") as f:
                results = json.load(f)
        done = {(r["id"], r.get("run", 1)) for r in results["results"]}
        total = len(claims)
        for i, c in enumerate(claims, 1):
            if (c["id"], 1) in done:
                continue
            try:
                res = sj.judge_claim(home, judge["model"], c, args.timeout)
                row = {"id": c["id"], "run": 1, "expected": c["expected"],
                       "dimension": c.get("dimension"), "focus": c.get("focus"),
                       "note": c.get("note"), **res, "status": "ok"}
            except Exception as exc:
                row = {"id": c["id"], "run": 1, "expected": c["expected"],
                       "status": f"error: {exc}"}
            results["results"].append(row)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=1)
            print(f"[{bench} {i}/{total}] {c['id']} -> {row.get('verdict', row.get('status'))}", flush=True)
        summary[bench] = grade(results)
        with open(os.path.join(HERE, "results", f"v04-{bench}-grade.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"bench": bench, **summary[bench]}, f,
                      ensure_ascii=False, indent=1)
        print(f"== {bench}: n={summary[bench]['n']} accuracy={summary[bench]['accuracy']}", flush=True)
        for k, v in summary[bench]["confusion"].items():
            print(f"   {k}: {v}")
    print(json.dumps({b: {"accuracy": s["accuracy"], "n": s["n"]}
                      for b, s in summary.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
