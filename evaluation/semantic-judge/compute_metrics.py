#!/usr/bin/env python3
"""Metrics for semantic-judge pilot (semantic-judge-v0.1).

Leser judge-resultater + ground truth (aldri judge-input) og skriver
metrics.json + calibration-report.md. Stotter calibration/holdout/ent-controls.
"""
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

VERDICTS = ["SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
UNSUP = {"CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"}
SAFETY_GROUPS = {"safety", "injection"}
CRITICAL_GROUPS = {"safety", "injection", "numeric", "temporal"}


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def per_class_metrics(cm):
    out = {}
    for v in VERDICTS:
        tp = cm[v][v]
        fp = sum(cm[w][v] for w in VERDICTS if w != v)
        fn = sum(cm[v][w] for w in VERDICTS if w != v)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[v] = {"precision": round(prec, 3), "recall": round(rec, 3),
                  "f1": round(f1, 3), "support": tp + fn}
    return out


def evaluate(set_name, judge_label):
    suffix = os.environ.get("JUDGE_VERSION", "v0.3")
    res = load(f"judge-results-{set_name}-{judge_label}-{suffix}.json")
    # calibration/holdout metrics use run 1 only; consistency uses all runs
    rows = {r["id"]: r for r in res["results"] if r.get("run", 1) == 1}
    if set_name == "ent-controls":
        exp = load("ent-controls-expected.json")["expected"]
        claims = {c["id"]: c["claim"] for c in load("ent-controls-set.json")["claims"]}
    elif set_name == "holdout":
        exp = load("expected-holdout.json")["expected"]
        claims = {c["id"]: c["claim"] for c in load("holdout-set.json")["claims"]}
    else:
        exp = load("expected-results.json")["expected"]
        claims = {c["id"]: c["claim"] for c in load(f"{set_name}-set.json")["claims"]}
    cm = defaultdict(Counter)
    conf_buckets = defaultdict(Counter)
    group_stats = defaultdict(lambda: {"n": 0, "correct": 0, "binary_fp": 0, "critical_fp": 0})
    misses = []
    for cid, e in exp.items():
        row = rows.get(cid)
        if row is None or row.get("status") != "ok" or not row.get("response"):
            misses.append({"id": cid, "expected": e["verdict"], "issue": "missing-or-error"})
            continue
        got = row["response"].get("verdict")
        conf = float(row["response"].get("confidence", 0.5))
        cm[e["verdict"]][got] += 1
        if 0.5 <= conf < 0.7:
            b = "0.5-0.69"
        elif 0.7 <= conf < 0.85:
            b = "0.70-0.84"
        elif 0.85 <= conf < 0.95:
            b = "0.85-0.94"
        else:
            b = "0.95-1.0"
        conf_buckets[b][got == e["verdict"]] += 1
        g = group_stats[e.get("group", "?")]
        g["n"] += 1
        correct = got == e["verdict"]
        if correct:
            g["correct"] += 1
        if e["verdict"] in UNSUP and got == "SUPPORTED":
            g["binary_fp"] += 1
            if e["group"] in SAFETY_GROUPS:
                g["critical_fp"] += 1
        if e["verdict"] in UNSUP and got == "SUPPORTED" and e["group"] in CRITICAL_GROUPS:
            pass
        if not correct:
            misses.append({
                "id": cid, "expected": e["verdict"], "got": got, "confidence": conf,
                "group": e.get("group", "?"), "claim": claims.get(cid, ""),
                "judge_reason": row["response"].get("reason", ""),
            })
    # confidence-bucket accuracy
    conf_acc = {}
    for b, c in conf_buckets.items():
        tot = c[True] + c[False]
        conf_acc[b] = {"n": tot, "accuracy": round(c[True] / tot, 3) if tot else None}
    # consistency over runs (where run>1 exists)
    per_id_runs = defaultdict(list)
    for r in res["results"]:
        if r.get("status") == "ok" and r.get("response"):
            per_id_runs[r["id"]].append((r.get("run", 1), r["response"].get("verdict"), float(r["response"].get("confidence", 0.5))))
    consistency = {"claims_with_multiple_runs": 0, "identical_all_runs": 0, "claims": {}}
    spreads = []
    for cid, rs in per_id_runs.items():
        if len(rs) < 2:
            continue
        verdicts = [v for _, v, _ in rs]
        confs = [c for _, _, c in rs]
        spread = round(max(confs) - min(confs), 3)
        spreads.append(spread)
        consistency["claims_with_multiple_runs"] += 1
        same = len(set(verdicts)) == 1
        if same:
            consistency["identical_all_runs"] += 1
        consistency["claims"][cid] = {"runs": len(rs), "verdicts": verdicts,
                                      "identical": same, "confidence_spread": spread}
    if spreads:
        s = sorted(spreads)
        n = len(s)
        consistency["median_confidence_spread"] = s[n // 2] if n % 2 else round((s[n//2 - 1] + s[n//2]) / 2, 3)
    return {
        "set": set_name, "judge": judge_label,
        "n": sum(cm[e][g] for e in VERDICTS for g in VERDICTS),
        "accuracy": None,
        "confusion": {e: dict(cm[e]) for e in VERDICTS},
        "per_class": per_class_metrics(cm),
        "group_stats": {g: dict(v) for g, v in group_stats.items()},
        "confidence_buckets": conf_acc,
        "consistency": consistency,
        "misses": misses,
    }


def finalize(m):
    total = sum(sum(row.values()) for row in m["confusion"].values())
    correct = sum(m["confusion"].get(v, {}).get(v, 0) for v in VERDICTS)
    m["n"] = total
    m["accuracy"] = round(correct / total, 4) if total else None
    binary_fp = sum(m["confusion"][e].get("SUPPORTED", 0) for e in VERDICTS if e != "SUPPORTED")
    unsup_n = sum(sum(m["confusion"][e].values()) for e in VERDICTS if e != "SUPPORTED")
    m["binary"] = {"unsupported_total": unsup_n, "unsupported_to_supported_fp": binary_fp,
                   "fp_rate": round(binary_fp / unsup_n, 4) if unsup_n else None}
    return m


def main():
    jobs = [("calibration", "judge-a-gpt-5.5"), ("holdout", "judge-a-gpt-5.5")]
    suffix = os.environ.get("JUDGE_VERSION", "v0.3")
    outputs = []
    for set_name, label in jobs:
        m = finalize(evaluate(set_name, label))
        out_path = os.path.join(HERE, f"metrics-{set_name}-{label}-{suffix}.json")
        with open(out_path, "w") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)
        outputs.append((out_path, m))
        print(f"WROTE {out_path}  n={m['n']} accuracy={m['accuracy']} "
              f"binary_fp={m['binary']['unsupported_to_supported_fp']}/{m['binary']['unsupported_total']}")
        print("misses:")
        for miss in m["misses"]:
            print(f"  {miss['id']}: expected={miss['expected']} got={miss.get('got')} conf={miss.get('confidence')} [{miss.get('group')}]")

if __name__ == "__main__":
    main()
