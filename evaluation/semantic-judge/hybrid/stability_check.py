"""Reviewer stability on difficult claims (spec 28/30): N claims x 3 runs."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_DIR = os.path.join(os.path.dirname(HERE), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HERE)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
from reviewer import review_claim  # noqa: E402

SETS = [
    ("minimal-pairs", os.path.join(BENCH_DIR, "minimal-pairs.json")),
    ("minimal-pairs-supplement", os.path.join(BENCH_DIR, "minimal-pairs-supplement.json")),
    ("contra-insuff", os.path.join(BENCH_DIR, "contra-insuff.json")),
    ("modality", os.path.join(BENCH_DIR, "modality.json")),
    ("actor-scope", os.path.join(BENCH_DIR, "actor-scope.json")),
    ("locality", os.path.join(BENCH_DIR, "locality.json")),
    ("diagnostic-20", os.path.join(BENCH_DIR, "diagnostic-20.json")),
    ("novel-40", os.path.join(JUDGE_DIR, "novel-development-set.json")),
    ("calibration", os.path.join(SEM_DIR, "calibration-set.json")),
    ("holdout-v2-burned", os.path.join(SEM_DIR, "holdout-set.json")),
]

# First 30 review-layer errors from the iteration-B run.
IDS = ["MP-007A", "MP-009A", "MP-013B", "MP-014A", "MP-016A", "MP-015A",
       "CI-040", "CI-041", "CI-046", "CI-059", "CI-061", "CI-065",
       "MOD-13", "ACT-10", "ACT-19", "ACT-23", "ACT-25", "LOC-10",
       "LOC-20", "D20-L5", "N-S4", "N-S9", "N-A3", "N-L4", "N-C4",
       "N-C5", "N-R3", "N-O5", "CAL029", "CAL030"]
RUNS = 3


def main():
    claims = {}
    for name, path in SETS:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for c in (data.get("claims", data if isinstance(data, list) else [])):
            claims[(name, c["id"])] = c
    by_id = {cid: (name, claims[(name, cid)])
             for name, path in SETS
             for cid in [c["id"] for c in
                         (json.load(open(path, encoding="utf-8")).get(
                             "claims", []))]
             if cid in IDS}
    out = []
    n_calls = 0
    for cid in IDS:
        name, c = by_id[cid]
        src = c["source"]["text"]
        res = E.judge_claim(c["claim"], src)
        reason = auto_gate(c["id"], src, res)
        runs = []
        for _ in range(RUNS):
            rv = review_claim(c["claim"], src, res, reason)
            n_calls += 1
            ro = rv["reviewer_output"] or {}
            runs.append({"verdict": rv["final_verdict"],
                         "route": rv["route"],
                         "spans": (ro.get("support_span_ids") or [])
                         + (ro.get("contradiction_span_ids") or []),
                         "confidence": ro.get("confidence")})
        verdicts = {r["verdict"] for r in runs}
        accepted = {r["verdict"] for r in runs
                    if r["verdict"] not in ("REVIEW_REQUIRED",)
                    and r["route"] == "accepted"}
        out.append({
            "id": cid, "set": name, "runs": runs,
            "verdict_consistent": len(verdicts) == 1,
            "span_consistent": len({tuple(r["spans"]) for r in runs}) == 1,
            "conf_spread": (round(max(r["confidence"] for r in runs
                                      if r["confidence"] is not None)
                                  - min(r["confidence"] for r in runs
                                        if r["confidence"] is not None), 2)
                            if any(r["confidence"] is not None
                                   for r in runs) else None),
            "unstable_auto_accept": len(accepted) > 1,
            "any_auto_accept": bool(accepted),
        })
        flag = "UNSTABLE" if out[-1]["unstable_auto_accept"] else ("wobble" if len(verdicts) > 1 else "stable")
        print("%-10s %-22s %s" % (cid, name, flag))
    unsafe = [r for r in out if r["unstable_auto_accept"]]
    summary = {"n_claims": len(IDS), "runs_each": RUNS,
               "llm_calls": n_calls,
               "verdict_consistent": sum(r["verdict_consistent"]
                                         for r in out),
               "unstable_auto_accepts": len(unsafe),
               "results": out}
    with open(os.path.join(HERE, "results", "stability.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("STABILITY claims=%d calls=%d consistent=%d unstable_auto_accepts=%d"
          % (len(IDS), n_calls, summary["verdict_consistent"],
             len(unsafe)))


if __name__ == "__main__":
    main()
