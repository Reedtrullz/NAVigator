"""Auto-coverage with the hybrid auto-accept gates applied.

Same sets/protocol as measure_auto_coverage.py, but AUTO_* requires
auto_gate() == None.  Gated cases land in REVIEW_ROUTE.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_DIR = os.path.join(os.path.dirname(HERE), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HERE)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR), HERE):
    sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402

SETS = [
    ("minimal-pairs", os.path.join(BENCH_DIR, "minimal-pairs.json"), None),
    ("minimal-pairs-supplement", os.path.join(BENCH_DIR, "minimal-pairs-supplement.json"), None),
    ("contra-insuff", os.path.join(BENCH_DIR, "contra-insuff.json"), None),
    ("modality", os.path.join(BENCH_DIR, "modality.json"), None),
    ("actor-scope", os.path.join(BENCH_DIR, "actor-scope.json"), None),
    ("locality", os.path.join(BENCH_DIR, "locality.json"), None),
    ("diagnostic-20", os.path.join(BENCH_DIR, "diagnostic-20.json"), None),
    ("novel-40", os.path.join(JUDGE_DIR, "novel-development-set.json"), None),
    ("ent", os.path.join(SEM_DIR, "ent-controls-set.json"),
     os.path.join(SEM_DIR, "ent-controls-expected.json")),
    ("calibration", os.path.join(SEM_DIR, "calibration-set.json"),
     os.path.join(SEM_DIR, "expected-results.json")),
    ("holdout-v2-burned", os.path.join(SEM_DIR, "holdout-set.json"),
     os.path.join(SEM_DIR, "expected-holdout.json")),
]


def load_claims(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("claims", data if isinstance(data, list) else [])


def load_expected(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("expected", {})


def main():
    all_rows = []
    summary = {}
    for name, set_path, exp_path in SETS:
        claims = load_claims(set_path)
        expected = load_expected(exp_path)
        rows = []
        for c in claims:
            try:
                res = E.judge_claim(c["claim"], c["source"]["text"])
            except Exception as exc:
                res = {"verdict": "ERROR", "error": str(exc)}
            exp = expected.get(c["id"], {})
            exp_v = exp.get("verdict", c.get("expected"))
            reason = auto_gate(c["id"], c["source"]["text"], res)
            if reason is None:
                cat = ("AUTO_SUPPORTED" if res["verdict"] == "SUPPORTED"
                       else "AUTO_CONTRADICTED")
            else:
                cat = "REVIEW_ROUTE"
            rows.append({"id": c["id"], "expected": exp_v,
                         "raw_verdict": res.get("verdict"),
                         "category": cat, "gate_reason": reason})
        n = len(rows)
        s_rows = [r for r in rows if r["category"] == "AUTO_SUPPORTED"]
        c_rows = [r for r in rows if r["category"] == "AUTO_CONTRADICTED"]
        s_ok = sum(1 for r in s_rows if r["expected"] == "SUPPORTED")
        c_ok = sum(1 for r in c_rows if r["expected"] == "CONTRADICTED")
        summary[name] = {
            "n": n,
            "auto_decided": len(s_rows) + len(c_rows),
            "auto_coverage": round((len(s_rows) + len(c_rows)) / n, 4) if n else None,
            "auto_supported": len(s_rows),
            "auto_supported_correct": s_ok,
            "auto_supported_precision": round(s_ok / len(s_rows), 4) if s_rows else None,
            "auto_contradicted": len(c_rows),
            "auto_contradicted_correct": c_ok,
            "auto_contradicted_precision": round(c_ok / len(c_rows), 4) if c_rows else None,
            "review_routed": sum(1 for r in rows if r["category"] == "REVIEW_ROUTE"),
        }
        for r in rows:
            r["set"] = name
        all_rows.extend(rows)
    out = {"meta": {"engine": "quote-aligner-deterministic-v0.2",
                    "stage": "hybrid-gated-coverage",
                    "gate": "auto_gate.py v0.1"},
           "summary": summary, "rows": all_rows}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "gated-coverage.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    total_n = sum(s["n"] for s in summary.values())
    total_dec = sum(s["auto_decided"] for s in summary.values())
    total_s = sum(s["auto_supported"] for s in summary.values())
    total_s_ok = sum(s["auto_supported_correct"] for s in summary.values())
    total_c = sum(s["auto_contradicted"] for s in summary.values())
    total_c_ok = sum(s["auto_contradicted_correct"] for s in summary.values())
    print("%-24s %5s %7s %8s %9s %7s" % (
        "set", "n", "auto%", "S-prec", "C-prec", "review"))
    for name, s in summary.items():
        print("%-24s %5d %7.1f %8s %9s %7d" % (
            name, s["n"], 100 * s["auto_coverage"],
            s["auto_supported_precision"] if s["auto_supported_precision"] is not None else "-",
            s["auto_contradicted_precision"] if s["auto_contradicted_precision"] is not None else "-",
            s["review_routed"]))
    print("TOTAL n=%d auto=%d (%.1f%%) S-prec=%.4f C-prec=%.4f" % (
        total_n, total_dec, 100 * total_dec / total_n,
        total_s_ok / total_s if total_s else -1,
        total_c_ok / total_c if total_c else -1))


if __name__ == "__main__":
    main()
