#!/usr/bin/env python3
"""v0.3 metrics: grade v0.3/results/*.json against expected verdict keys."""
import argparse, json, os
from collections import Counter, defaultdict

CLASSES = ["SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]

def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return round(p, 3), round(r, 3), round(f, 3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--expected", required=True)
    ap.add_argument("--set-file", default=None, help="set json with claims/flags (stability)")
    ap.add_argument("--stability", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = json.load(open(args.results))["results"]
    exp_data = json.load(open(args.expected))
    if isinstance(exp_data, dict) and "expected" in exp_data:
        exp = exp_data["expected"]
    elif isinstance(exp_data, dict) and "claims" in exp_data:
        exp = {c["id"]: {"verdict": c["expected"],
                         "group": c.get("near_miss_kind", c.get("group", "adversarial"))}
               for c in exp_data["claims"] if "expected" in c}
    else:
        raise SystemExit("expected file must have 'expected' or 'claims' key")
    flags_by_id = {}
    if args.set_file:
        setdata = json.load(open(args.set_file))
        for c in setdata.get("claims", setdata.get("cases", [])):
            flags_by_id[c["id"]] = c.get("flags", [])

    err_rows = [r for r in rows if r.get("status") != "ok"]
    ok_rows = [r for r in rows if r.get("status") == "ok" and r["id"] in exp]

    report = {"results_file": args.results, "n_rows": len(rows),
              "n_graded": len(ok_rows), "n_run_errors": len(err_rows),
              "run_error_ids": [r["id"] for r in err_rows]}

    if args.stability:
        by_id = defaultdict(list)
        for r in ok_rows:
            by_id[r["id"]].append(r)
        inconsistent = []
        flips = {"safety": [], "numeric": [], "temporal": []}
        for cid, rs in sorted(by_id.items()):
            vs = [r["verdict"] for r in rs]
            if len(set(vs)) > 1:
                inconsistent.append({"id": cid, "verdicts": vs,
                                     "flags": flags_by_id.get(cid, [])})
                fl = set(flags_by_id.get(cid, []))
                for g in flips:
                    if g in fl:
                        flips[g].append(cid)
        modal = {}
        for cid, rs in by_id.items():
            modal[cid] = Counter(r["verdict"] for r in rs).most_common(1)[0][0]
        graded = [(cid, v) for cid, v in modal.items() if cid in exp]
        correct = sum(1 for cid, v in graded if v == exp[cid]["verdict"])
        report["stability"] = {
            "n_ids": len(by_id), "runs_per_id": sorted({len(rs) for rs in by_id.values()}),
            "modal_consistency": round(1 - len(inconsistent) / len(by_id), 4) if by_id else 0,
            "inconsistent_ids": inconsistent,
            "flips": flips,
            "modal_accuracy": round(correct / len(graded), 4) if graded else 0,
        }
    else:
        confusion = defaultdict(Counter)
        misses = []
        for r in ok_rows:
            e = exp[r["id"]]["verdict"]
            g = r["verdict"]
            confusion[e][g] += 1
            if e != g:
                misses.append({
                    "id": r["id"], "expected": e, "got": g,
                    "confidence": r.get("confidence"),
                    "group": exp[r["id"]].get("group"),
                    "high_conf": (r.get("confidence") or 0) >= 0.95,
                    "reason": (r.get("response") or {}).get("reason", ""),
                })
        per_class = {}
        for c in CLASSES:
            tp = confusion[c][c]
            fp = sum(confusion[o][c] for o in CLASSES if o != c)
            fn = sum(confusion[c][o] for o in CLASSES if o != c)
            p, r_, f = prf(tp, fp, fn)
            per_class[c] = {"precision": p, "recall": r_, "f1": f, "support": tp + fn}
        macro_f1 = round(sum(per_class[c]["f1"] for c in CLASSES) / len(CLASSES), 4)
        groups = defaultdict(lambda: {"n": 0, "correct": 0, "binary_fp": 0, "critical_fp": 0})
        for r in ok_rows:
            e = exp[r["id"]]
            g = groups[e.get("group", "none")]
            g["n"] += 1
            if r["verdict"] == e["verdict"]:
                g["correct"] += 1
            if e["verdict"] != "SUPPORTED" and r["verdict"] == "SUPPORTED":
                g["binary_fp"] += 1
                if e.get("group") in ("numeric", "safety", "temporal"):
                    g["critical_fp"] += 1
        unsupported = [r for r in ok_rows if exp[r["id"]]["verdict"] != "SUPPORTED"]
        bin_fp = sum(1 for r in unsupported if r["verdict"] == "SUPPORTED")
        flagged_errors = sum(1 for m in misses if m["high_conf"])
        report.update({
            "accuracy": round(sum(1 for r in ok_rows if r["verdict"] == exp[r["id"]]["verdict"]) / len(ok_rows), 4) if ok_rows else 0,
            "macro_f1": macro_f1,
            "per_class": per_class,
            "confusion": {e: dict(g) for e, g in sorted(confusion.items())},
            "group_stats": {k: v for k, v in sorted(groups.items())},
            "binary": {"unsupported_total": len(unsupported), "fp": bin_fp,
                       "fp_rate": round(bin_fp / len(unsupported), 4) if unsupported else 0},
            "high_conf_errors": flagged_errors,
            "misses": misses,
        })
    text_out = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text_out)
    print(text_out)

if __name__ == "__main__":
    main()
