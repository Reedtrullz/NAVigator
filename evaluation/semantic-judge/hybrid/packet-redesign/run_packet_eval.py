"""Packet-v2.1 evaluation runner (Iteration A).

Same claim sets and engine/gate flow as run_hybrid_eval.py; review-path
claims go through reviewer_v2.review_claim_v2 with per-atom packets.
All verdict labels are normalized before accuracy math.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HY = os.path.dirname(HERE)
JUDGE_DIR = os.path.join(os.path.dirname(HY), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HY)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR), HY, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
import packet_router  # noqa: E402
from reviewer_v2 import review_claim_v2, prompt_meta  # noqa: E402

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

NORM = {"INSUFFICIENT_EVIDENCE": "INSUFFICIENT",
        "PARTIALLY_SUPPORTED": "PARTIAL"}
NOTD = {"REVIEW_REQUIRED", "NO_EVIDENCE", "AMBIGUOUS"}
DECIDED = ("SUPPORTED", "CONTRADICTED", "PARTIAL", "INSUFFICIENT")


def norm(v):
    return NORM.get(v, v)


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="all",
                    help="comma-separated set names, or 'all'")
    ap.add_argument("--s0-mode", default="no_s0",
                    choices=["include", "no_s0", "fallback"])
    ap.add_argument("--max-spans", type=int, default=6)
    ap.add_argument("--limit-review", type=int, default=None,
                    help="max LLM review calls")
    ap.add_argument("--dry-run", action="store_true",
                    help="build packets only, no LLM calls")
    ap.add_argument("--out", default="results/automatic-packet-results.json")
    args = ap.parse_args()

    selected = (SETS if args.sets == "all" else
        [s for s in SETS if s[0] in args.sets.split(",")])
    if not selected:
        sys.exit("no sets matched: %s" % args.sets)

    rows, summary = [], {}
    n_calls = n_fidelity_fail = 0
    t0 = time.time()
    for name, set_path, exp_path in selected:
        claims = load_claims(set_path)
        expected = load_expected(exp_path)
        set_rows = []
        for c in claims:
            src = c["source"]["text"]
            res = E.judge_claim(c["claim"], src)
            exp_v = norm(expected.get(c["id"], {}).get(
                "verdict", c.get("expected")))
            reason = auto_gate(c["id"], src, res)
            row = {"id": c["id"], "set": name, "expected": exp_v,
                   "engine_verdict": norm(res["verdict"]),
                   "gate_reason": reason}
            if reason is None:
                row["final"] = norm(res["verdict"])
                row["path"] = "auto"
            elif args.dry_run:
                pkt = packet_router.build_v2_packet(
                    c["claim"], src, res, reason,
                    s0_mode=args.s0_mode, max_spans=args.max_spans)
                row.update(path="packet_only", final=None,
                           n_spans=len(pkt["candidate_spans"]),
                           approx_packet_tokens=sum(
                               len(s["text"]) for s in pkt["candidate_spans"]) // 4)
            elif args.limit_review is not None and n_calls >= args.limit_review:
                row.update(final="REVIEW_LIMIT", path="review_skipped")
            else:
                rv = review_claim_v2(
                    c["claim"], src, res, reason,
                    s0_mode=args.s0_mode, max_spans=args.max_spans)
                n_calls += 1
                final = norm(rv["final_verdict"])
                route = rv["route"]
                if route.startswith("fidelity_failed"):
                    n_fidelity_fail += 1
                row.update(final=final, path="review", route=route,
                           n_spans=rv["n_spans"],
                           approx_packet_tokens=rv["approx_packet_tokens"],
                           atom_results=rv["atom_results"],
                           reason_code=(rv["reviewer_output"] or {}).get(
                               "reason_code"))
            set_rows.append(row)

        rows.extend(set_rows)
        auto = [r for r in set_rows if r["path"] == "auto"]
        review = [r for r in set_rows if r["path"] == "review"]
        decided = [r for r in set_rows if r["final"] in DECIDED]
        correct = [r for r in decided if r["final"] == r["expected"]]
        s_auto = [r for r in auto if r["final"] == "SUPPORTED"]
        c_auto = [r for r in auto if r["final"] == "CONTRADICTED"]
        summary[name] = {
            "n": len(set_rows),
            "auto": len(auto),
            "review": len(review),
            "packet_only": sum(1 for r in set_rows if r["path"] == "packet_only"),
            "decided": len(decided),
            "correct": len(correct),
            "selective_accuracy": round(len(correct) / len(decided), 4)
            if decided else None,
            "auto_supported": len(s_auto),
            "auto_supported_fp": sum(1 for r in s_auto if r["expected"] != "SUPPORTED"),
            "auto_contra": len(c_auto),
            "auto_contra_fp": sum(1 for r in c_auto if r["expected"] != "CONTRADICTED"),
            "review_required": sum(1 for r in set_rows if r["final"] == "REVIEW_REQUIRED"),
            "fidelity_failed": sum(1 for r in review
                                   if str(r.get("route", "")).startswith("fidelity_failed")),
        }
        print("%-24s n=%3d auto=%3d review=%3d acc=%s" % (
            name, summary[name]["n"], summary[name]["auto"],
            summary[name]["review"], summary[name]["selective_accuracy"]))

    total_n = sum(s["n"] for s in summary.values())
    total_dec = sum(s["decided"] for s in summary.values())
    total_ok = sum(s["correct"] for s in summary.values())
    total_auto = sum(s["auto"] for s in summary.values())
    total_review = sum(s["review"] for s in summary.values())
    out = {
        "meta": {"stage": "packet-v2.1-iteration-A",
                 "s0_mode": args.s0_mode, "max_spans": args.max_spans,
                 "dry_run": args.dry_run,
                 "prompt_meta": prompt_meta(),
                 "elapsed_s": round(time.time() - t0, 1)},
        "summary": summary, "rows": rows,
        "totals": {
            "n": total_n, "decided": total_dec, "correct": total_ok,
            "selective_accuracy": round(total_ok / total_dec, 4)
            if total_dec else None,
            "auto": total_auto, "review": total_review,
            "llm_calls": n_calls,
            "review_rate": round(total_review / total_n, 4) if total_n else None,
            "fidelity_failures": n_fidelity_fail,
            "auto_supported_fp": sum(s["auto_supported_fp"] for s in summary.values()),
            "auto_contra_fp": sum(s["auto_contra_fp"] for s in summary.values()),
        },
    }
    out_path = os.path.join(HERE, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("TOTAL n=%d decided=%d acc=%s auto=%d review=%d calls=%d fid_fail=%d" % (
        total_n, total_dec, out["totals"]["selective_accuracy"],
        total_auto, total_review, n_calls, n_fidelity_fail))


if __name__ == "__main__":
    main()
