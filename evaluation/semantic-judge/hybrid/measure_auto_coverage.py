"""Measure deterministic auto-decision coverage for the hybrid layer.

Classifies quote-aligner v0.2 output into hybrid categories:
  AUTO_SUPPORTED / AUTO_CONTRADICTED (clean proof, no review flag)
  NO_EVIDENCE (INSUFFICIENT) / AMBIGUOUS (PARTIAL) / REVIEW flag
and computes auto-decision precision against expected verdicts.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_DIR = os.path.join(os.path.dirname(HERE), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HERE)
BENCH_DIR = os.path.join(os.path.dirname(HERE), "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR)):
    sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402

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


def classify(row):
    verdict = row.get("verdict")
    if verdict == "SUPPORTED":
        return ("AUTO_SUPPORTED" if not row.get("review_required")
                else "REVIEW_FLAG")
    if verdict == "CONTRADICTED":
        return ("AUTO_CONTRADICTED" if not row.get("review_required")
                else "REVIEW_FLAG")
    if verdict == "PARTIALLY_SUPPORTED":
        return "AMBIGUOUS"
    return "NO_EVIDENCE"


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
                res["status"] = "ok"
            except Exception as exc:
                res = {"verdict": "ERROR", "status": "error: %s" % exc}
            exp = expected.get(c["id"], {})
            exp_v = exp.get("verdict", c.get("expected"))
            cat = classify(res)
            rows.append({"id": c["id"], "expected": exp_v,
                         "raw_verdict": res.get("verdict"),
                         "confidence": res.get("confidence"),
                         "category": cat})
        decided = [r for r in rows
                   if r["category"] in ("AUTO_SUPPORTED", "AUTO_CONTRADICTED")]
        n = len(rows)
        s_rows = [r for r in decided if r["category"] == "AUTO_SUPPORTED"]
        c_rows = [r for r in decided if r["category"] == "AUTO_CONTRADICTED"]
        s_ok = sum(1 for r in s_rows if r["expected"] == "SUPPORTED")
        c_ok = sum(1 for r in c_rows if r["expected"] == "CONTRADICTED")
        summary[name] = {
            "n": n,
            "auto_decided": len(decided),
            "auto_coverage": round(len(decided) / n, 4) if n else None,
            "auto_supported": len(s_rows),
            "auto_supported_correct": s_ok,
            "auto_supported_precision": round(s_ok / len(s_rows), 4) if s_rows else None,
            "auto_contradicted": len(c_rows),
            "auto_contradicted_correct": c_ok,
            "auto_contradicted_precision": round(c_ok / len(c_rows), 4) if c_rows else None,
            "review_routed": n - len(decided),
            "no_evidence": sum(1 for r in rows if r["category"] == "NO_EVIDENCE"),
            "ambiguous": sum(1 for r in rows if r["category"] == "AMBIGUOUS"),
            "review_flag": sum(1 for r in rows if r["category"] == "REVIEW_FLAG"),
        }
        for r in rows:
            r["set"] = name
        all_rows.extend(rows)
    out = {"meta": {"engine": "quote-aligner-deterministic-v0.2",
                    "stage": "hybrid-auto-coverage"},
           "summary": summary, "rows": all_rows}
    path = os.path.join(HERE, "results", "auto-coverage.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    total_n = sum(s["n"] for s in summary.values())
    total_dec = sum(s["auto_decided"] for s in summary.values())
    total_s = sum(s["auto_supported"] for s in summary.values())
    total_s_ok = sum(s["auto_supported_correct"] for s in summary.values())
    total_c = sum(s["auto_contradicted"] for s in summary.values())
    total_c_ok = sum(s["auto_contradicted_correct"] for s in summary.values())
    print("%-24s %5s %7s %8s %9s %9s %9s" % (
        "set", "n", "auto%", "S-prec", "C-prec", "noEv", "revRt"))
    for name, s in summary.items():
        print("%-24s %5d %7.1f %8s %9s %9d %9d" % (
            name, s["n"], 100 * s["auto_coverage"],
            s["auto_supported_precision"] if s["auto_supported_precision"] is not None else "-",
            s["auto_contradicted_precision"] if s["auto_contradicted_precision"] is not None else "-",
            s["no_evidence"], s["review_routed"]))
    print("TOTAL n=%d auto=%d (%.1f%%) S-prec=%.4f C-prec=%.4f" % (
        total_n, total_dec, 100 * total_dec / total_n,
        total_s_ok / total_s if total_s else -1,
        total_c_ok / total_c if total_c else -1))


if __name__ == "__main__":
    main()
