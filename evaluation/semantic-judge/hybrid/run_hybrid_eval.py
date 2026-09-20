"""Full hybrid evaluation: engine -> gates -> reviewer -> fusion.

Writes results/hybrid-eval.json with per-set metrics, review routing,
reviewer fidelity, and cost accounting (spec 32).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_DIR = os.path.join(os.path.dirname(HERE), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HERE)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.join(os.path.dirname(JUDGE_DIR)), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
from reviewer import review_claim  # noqa: E402

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


def main(limit_review=None):
    all_rows = []
    summary = {}
    n_calls = 0
    t0 = time.time()
    for name, set_path, exp_path in SETS:
        claims = load_claims(set_path)
        expected = load_expected(exp_path)
        rows = []
        for c in claims:
            src = c["source"]["text"]
            res = E.judge_claim(c["claim"], src)
            exp = expected.get(c["id"], {})
            exp_v = exp.get("verdict", c.get("expected"))
            reason = auto_gate(c["id"], src, res)
            row = {"id": c["id"], "set": name, "expected": exp_v,
                   "engine_verdict": res["verdict"], "gate_reason": reason}
            if reason is None:
                row["final"] = res["verdict"]
                row["path"] = "auto"
            else:
                if limit_review and n_calls >= limit_review:
                    row["final"] = "REVIEW_LIMIT"
                    row["path"] = "review_skipped"
                else:
                    rv = review_claim(c["claim"], src, res, reason)
                    n_calls += 1
                    row["final"] = rv["final_verdict"]
                    row["route"] = rv["route"]
                    row["path"] = "review"
                    row["reviewer_output"] = rv["reviewer_output"]
                    row["threshold"] = rv["threshold"]
            rows.append(row)
        # metrics
        n = len(rows)
        auto_rows = [r for r in rows if r["path"] == "auto"]
        final_decided = [r for r in rows if r["final"] in (
            "SUPPORTED", "CONTRADICTED", "PARTIAL", "INSUFFICIENT")]
        correct = sum(
            1 for r in final_decided
            if r["final"] == r["expected"])
        s_auto = [r for r in auto_rows if r["final"] == "SUPPORTED"]
        c_auto = [r for r in auto_rows if r["final"] == "CONTRADICTED"]
        summary[name] = {
            "n": n,
            "auto": len(auto_rows),
            "review": sum(1 for r in rows if r["path"] == "review"),
            "final_decided": len(final_decided),
            "final_correct": correct,
            "selective_accuracy": round(correct / len(final_decided), 4)
            if final_decided else None,
            "auto_s": len(s_auto),
            "auto_s_correct": sum(1 for r in s_auto
                                  if r["expected"] == "SUPPORTED"),
            "auto_c": len(c_auto),
            "auto_c_correct": sum(1 for r in c_auto
                                  if r["expected"] == "CONTRADICTED"),
            "review_required": sum(1 for r in rows
                                   if r["final"] == "REVIEW_REQUIRED"),
        }
        all_rows.extend(rows)
        print("%-24s n=%3d auto=%3d review=%3d acc=%s" % (
            name, n, len(auto_rows),
            summary[name]["review"],
            summary[name]["selective_accuracy"]))
    total_n = sum(s["n"] for s in summary.values())
    total_dec = sum(s["final_decided"] for s in summary.values())
    total_ok = sum(s["final_correct"] for s in summary.values())
    total_auto = sum(s["auto"] for s in summary.values())
    total_review = sum(s["review"] for s in summary.values())
    out = {
        "meta": {"stage": "hybrid-iteration-B",
                 "model": "openai/gpt-5.6-luna", "temperature": 0,
                 "elapsed_s": round(time.time() - t0, 1)},
        "summary": summary, "rows": all_rows,
        "totals": {
            "n": total_n, "final_decided": total_dec,
            "final_correct": total_ok,
            "selective_accuracy": round(total_ok / total_dec, 4)
            if total_dec else None,
            "auto": total_auto, "review": total_review,
            "llm_calls": n_calls,
            "review_rate": round(total_review / total_n, 4),
        },
    }
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "hybrid-eval.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("TOTAL n=%d decided=%d acc=%.4f auto=%d review=%d calls=%d" % (
        total_n, total_dec, out["totals"]["selective_accuracy"],
        total_auto, total_review, n_calls))


if __name__ == "__main__":
    lim = None
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            lim = int(a.split("=")[1])
    main(limit_review=lim)
