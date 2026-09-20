#!/usr/bin/env python3
"""v0.4 metrics: grade results against expected verdicts.

Extends the v0.3 metrics with structured-relation stability (per-field
consistency of the extracted evidence relation across runs) and relation
types on every miss. No claim-id logic here; dev-analysis id groupings
live in a data file (results/dev-analysis.json), not in code."""
import argparse
import json
import os
from collections import Counter, defaultdict

CLASSES = ["SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED",
           "INSUFFICIENT_EVIDENCE"]
RELATION_FIELDS = ["relation", "relation_type", "subject_match",
                   "scope_match", "time_match", "actor_match",
                   "modality_relation", "numeric_relation",
                   "negation_relation", "verdict"]


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return round(p, 3), round(r, 3), round(f, 3)


def relation_of(row):
    rels = []
    for ar in row.get("atom_results") or []:
        rels.append(ar.get("relation") or {})
    return rels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--expected", required=True)
    ap.add_argument("--set-file", default=None)
    ap.add_argument("--stability", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = json.load(open(args.results))["results"]
    exp_data = json.load(open(args.expected))
    if isinstance(exp_data, dict) and "expected" in exp_data:
        exp = exp_data["expected"]
    elif isinstance(exp_data, dict) and "claims" in exp_data:
        exp = {c["id"]: {"verdict": c["expected"]}
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
        verdict_inconsistent = []
        field_stats = {f: {"consistent_ids": 0, "inconsistent_ids": [],
                           "modal_agreement": []} for f in RELATION_FIELDS}
        flips = {"safety": [], "numeric": [], "temporal": []}
        for cid, rs in sorted(by_id.items()):
            vs = [r["verdict"] for r in rs]
            if len(set(vs)) > 1:
                verdict_inconsistent.append({"id": cid, "verdicts": vs,
                                             "flags": flags_by_id.get(cid, [])})
                fl = set(flags_by_id.get(cid, []))
                for g in flips:
                    if g in fl:
                        flips[g].append(cid)
            for field in RELATION_FIELDS:
                if field == "verdict":
                    vals = vs
                else:
                    vals = []
                    for r in rs:
                        rels = relation_of(r)
                        vals.append(";".join(sorted({str(x.get(field))
                                                     for x in rels})))
                counter = Counter(vals)
                modal, count = counter.most_common(1)[0]
                agreement = count / len(vals)
                fs = field_stats[field]
                if len(set(vals)) == 1:
                    fs["consistent_ids"] += 1
                else:
                    fs["inconsistent_ids"].append(
                        {"id": cid, "values": vals})
                fs["modal_agreement"].append(round(agreement, 3))
        n_ids = len(by_id)
        report["stability"] = {
            "n_ids": n_ids,
            "runs_per_id": sorted({len(rs) for rs in by_id.values()}),
            "verdict_modal_consistency": round(
                1 - len(verdict_inconsistent) / n_ids, 4) if n_ids else 0,
            "verdict_inconsistent_ids": verdict_inconsistent,
            "field_consistency": {
                f: {"rate": round(s["consistent_ids"] / n_ids, 4) if n_ids else 0,
                    "mean_modal_agreement": round(
                        sum(s["modal_agreement"]) / len(s["modal_agreement"]), 4)
                    if s["modal_agreement"] else 0,
                    "inconsistent_ids": s["inconsistent_ids"][:20],
                    "n_inconsistent": len(s["inconsistent_ids"])}
                for f, s in field_stats.items()},
            "flips": flips,
        }
        graded = [(cid, Counter(r["verdict"] for r in rs).most_common(1)[0][0])
                  for cid, rs in by_id.items() if cid in exp]
        correct = sum(1 for cid, v in graded if v == exp[cid]["verdict"])
        report["stability"]["modal_accuracy"] = round(correct / len(graded), 4) if graded else 0
    else:
        confusion = defaultdict(Counter)
        misses = []
        for r in ok_rows:
            e = exp[r["id"]]["verdict"]
            g = r["verdict"]
            confusion[e][g] += 1
            if e != g:
                rels = relation_of(r)
                misses.append({
                    "id": r["id"], "expected": e, "got": g,
                    "confidence": r.get("confidence"),
                    "group": exp[r["id"]].get("group"),
                    "high_conf": (r.get("confidence") or 0) >= 0.95,
                    "relation_types": [x.get("relation_type") for x in rels],
                    "relations": [x.get("relation") for x in rels],
                    "reason": (r.get("atom_results") or [{}])[0].get("reason", ""),
                })
        per_class = {}
        for c in CLASSES:
            tp = confusion[c][c]
            fp = sum(confusion[o][c] for o in CLASSES if o != c)
            fn = sum(confusion[c][o] for o in CLASSES if o != c)
            p, r_, f = prf(tp, fp, fn)
            per_class[c] = {"precision": p, "recall": r_, "f1": f,
                            "support": tp + fn}
        macro_f1 = round(sum(per_class[c]["f1"] for c in CLASSES) / len(CLASSES), 4)
        groups = defaultdict(lambda: {"n": 0, "correct": 0, "binary_fp": 0,
                                      "critical_fp": 0})
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
        report.update({
            "accuracy": round(sum(1 for r in ok_rows
                                  if r["verdict"] == exp[r["id"]]["verdict"])
                              / len(ok_rows), 4) if ok_rows else 0,
            "macro_f1": macro_f1,
            "per_class": per_class,
            "confusion": {e: dict(g) for e, g in sorted(confusion.items())},
            "group_stats": {k: v for k, v in sorted(groups.items())},
            "binary": {"unsupported_total": len(unsupported), "fp": bin_fp,
                       "fp_rate": round(bin_fp / len(unsupported), 4)
                       if unsupported else 0},
            "high_conf_errors": [m for m in misses if m["high_conf"]],
            "misses": misses,
        })
    text_out = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text_out)
    brief = {k: report[k] for k in ("accuracy", "macro_f1") if k in report}
    if "stability" in report:
        brief = {"verdict_modal_consistency":
                 report["stability"]["verdict_modal_consistency"],
                 "modal_accuracy": report["stability"]["modal_accuracy"],
                 "field_consistency": {f: s["rate"] for f, s in
                                       report["stability"]["field_consistency"].items()}}
    print(json.dumps(brief, ensure_ascii=False))
    if args.out:
        print("wrote", args.out)


if __name__ == "__main__":
    main()
