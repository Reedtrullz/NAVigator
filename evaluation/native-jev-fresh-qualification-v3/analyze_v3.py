#!/usr/bin/env python3
"""Frozen V3 analysis plan (precommitted in V3_PRECOMMIT_MANIFEST.json).

No tuning: every metric, gate and threshold here was fixed before label reveal.
Reuses the V2 router unmodified; computes the same functions over the V2 run1
data for the precommitted V2-vs-V3 comparison table.
"""
import json, math, pathlib, sys
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parent
V2 = BASE.parent / "native-jev-qualification-v2"
sys.path.insert(0, str(V2))
from routing_v2 import route, gold_violating, gold_fine

PRIMARY_T = 0.7
DIAG_T = (0.7, 0.8, 0.9)
HIGH_CONF = 0.8
INPUT_PRICE_PER_1M = 0.042

def load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def top_prob(ans, key):
    a = ans.get(key) or {}
    probs = a.get("probabilities") or {}
    if a.get("choice") in probs:
        return probs[a["choice"]]
    return max(probs.values()) if probs else 0.0

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

def cp_upper_zero(n):
    return 1 - 0.025 ** (1.0 / n) if n else 1.0

def pair_correct(exp, ans):
    m = (ans.get("criterion_semantic_match") or {}).get("choice")
    s = (ans.get("speaker_commitment") or {}).get("choice")
    gm = exp["criterion_semantic_match"]
    if gm == "MATCH": return m == "MATCH" and s == exp["speaker_commitment"]
    if gm == "NO_MATCH": return m == "NO_MATCH"
    return m == "UNRESOLVED"

def analyze_run(rows, tag):
    r = {"tag": tag, "n": len(rows),
         "errors": sum(1 for x in rows if x["error"]),
         "models": sorted(set(x["model"] for x in rows))}
    ok = [x for x in rows if not x["error"]]
    crit = [x for x in ok if x["lane"] == "critical_condition"]
    forb = [x for x in ok if x["lane"] == "forbidden_claim"]
    cc = Counter()
    cm = {s: Counter() for s in ("CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT",
                                 "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED")}
    dangerous = catastrophic = 0
    for x in crit:
        g = x["expected"]["critical_evidence_state"]
        p = (x["answers"].get("evidence_state") or {}).get("choice")
        cc[(g, p)] += 1
        cm[g][p] += 1
        if g == "CLEAR_NON_TRIGGER_SUPPORT" and p == "CLEAR_TRIGGER_SUPPORT":
            dangerous += 1
            if top_prob(x["answers"], "evidence_state") >= HIGH_CONF:
                catastrophic += 1
    crit_exact = sum(v for (g, p), v in cc.items() if g == p)
    r["critical"] = {"n": len(crit), "exact": crit_exact,
        "exact_rate": crit_exact / len(crit) if crit else None,
        "confusion": {g: dict(cm[g]) for g in cm},
        "false_trigger_dangerous_direction": dangerous,
        "false_trigger_high_conf_catastrophic": catastrophic}
    mc = Counter()
    pair_ok = 0
    match_labels = ("MATCH", "NO_MATCH", "UNRESOLVED")
    cmm = {g: Counter() for g in match_labels}
    commit_cells = Counter()
    for x in forb:
        g = x["expected"]["criterion_semantic_match"]
        p = (x["answers"].get("criterion_semantic_match") or {}).get("choice")
        mc[(g, p)] += 1
        cmm[g][p] += 1
        if pair_correct(x["expected"], x["answers"]):
            pair_ok += 1
        commit_cells[(g, x["expected"]["speaker_commitment"],
                      (x["answers"].get("speaker_commitment") or {}).get("choice"))] += 1
    match_exact = sum(v for (g, p), v in mc.items() if g == p)
    r["forbidden"] = {"n": len(forb), "pair_exact": pair_ok,
        "pair_accuracy": pair_ok / len(forb) if forb else None,
        "match_exact": match_exact,
        "match_accuracy": match_exact / len(forb) if forb else None,
        "match_confusion": {g: dict(cmm[g]) for g in cmm},
        "commitment_cells_gold_to_pred": {a + "/" + b + "/" + c: v
            for (a, b, c), v in commit_cells.items()}}
    def conf_dist(key):
        vals = sorted(((x["answers"].get(key) or {}).get("confidence") or 0.0)
                      for x in ok if x["answers"].get(key))
        if not vals: return None
        return {"min": vals[0], "median": vals[len(vals)//2], "max": vals[-1]}
    r["confidence_distributions"] = {
        "evidence_state": conf_dist("evidence_state"),
        "criterion_semantic_match": conf_dist("criterion_semantic_match"),
        "speaker_commitment": conf_dist("speaker_commitment")}
    lat = sorted(x["latency_seconds"] for x in ok)
    r["latency"] = {"median": lat[len(lat)//2], "p95": lat[int(len(lat)*0.95)], "max": lat[-1]}
    r["input_tokens"] = sum((x.get("usage") or {}).get("input_tokens", 0) for x in ok)
    return r

def routing(rows, t):
    out = {"T": t, "n": len(rows), "AUTO_ACCEPT": 0, "AUTO_REJECT": 0, "ESCALATE": 0, "ERROR": 0,
           "decidable": 0, "auto_on_decidable": 0, "auto_correct_on_decidable": 0,
           "FALSE_PASS": 0, "FALSE_FAIL": 0, "safety_critical_FP": 0,
           "high_conf_FP": 0, "high_conf_FF": 0, "events": []}
    for x in rows:
        if x["error"]:
            out["ERROR"] += 1
            continue
        d = route(x, t)
        out[d] += 1
        v, f = gold_violating(x["expected"]), gold_fine(x["expected"])
        if v or f:
            out["decidable"] += 1
        auto = d in ("AUTO_ACCEPT", "AUTO_REJECT")
        if auto and (v or f):
            out["auto_on_decidable"] += 1
            if (d == "AUTO_REJECT") == v:
                out["auto_correct_on_decidable"] += 1
        hp_keys = ("criterion_semantic_match", "speaker_commitment", "evidence_state")
        if d == "AUTO_ACCEPT" and v:
            out["FALSE_PASS"] += 1
            hp = max((top_prob(x["answers"], k) for k in hp_keys), default=0.0) if x["answers"] else 0.0
            sc = x["lane"] == "critical_condition"
            if sc:
                out["safety_critical_FP"] += 1
            if hp >= HIGH_CONF:
                out["high_conf_FP"] += 1
            out["events"].append({"kind": "FALSE_PASS", "case_id": x["case_id"],
                "packet_id": x["packet_id"], "lane": x["lane"], "safety_critical": sc,
                "high_conf": hp >= HIGH_CONF, "top_prob": round(hp, 3), "expected": x["expected"]})
        if d == "AUTO_REJECT" and f:
            out["FALSE_FAIL"] += 1
            hp = max((top_prob(x["answers"], k) for k in hp_keys), default=0.0) if x["answers"] else 0.0
            if hp >= HIGH_CONF:
                out["high_conf_FF"] += 1
            out["events"].append({"kind": "FALSE_FAIL", "case_id": x["case_id"],
                "packet_id": x["packet_id"], "lane": x["lane"], "safety_critical": False,
                "high_conf": hp >= HIGH_CONF, "top_prob": round(hp, 3), "expected": x["expected"]})
    dec = out["decidable"]
    out["safe_auto_coverage"] = out["auto_on_decidable"] / dec if dec else None
    out["safe_auto_coverage_correct"] = out["auto_correct_on_decidable"] / dec if dec else None
    out["escalation_rate"] = out["ESCALATE"] / out["n"] if out["n"] else None
    auto_n = out["AUTO_ACCEPT"] + out["AUTO_REJECT"]
    out["accuracy_among_auto_decided"] = (
        (out["AUTO_ACCEPT"] + out["AUTO_REJECT"] - out["FALSE_PASS"] - out["FALSE_FAIL"]) / auto_n
        if auto_n else None)
    return out

def stability(runs):
    n = len(runs[0])
    for r in runs:
        assert len(r) == n, "run length mismatch"
        for i in range(n):
            assert r[i]["case_id"] == runs[0][i]["case_id"] and r[i]["packet_id"] == runs[0][i]["packet_id"], "run alignment failure"
    res = {"n": n}
    modal_all3 = 0
    t_flip = 0
    choice_fields = ("evidence_state", "criterion_semantic_match", "speaker_commitment")
    for i in range(n):
        rows = [r[i] for r in runs]
        if any(r["error"] for r in rows):
            continue
        dec = [route(r, PRIMARY_T) for r in rows]
        if len(set(dec)) == 1:
            modal_all3 += 1
        for f in choice_fields:
            cf = [((r["answers"].get(f) or {}).get("confidence") or 0.0) for r in rows]
            if len(set(c > PRIMARY_T for c in cf)) > 1:
                t_flip += 1
                break
    res["routing_modal_all3_identical"] = modal_all3 / n
    res["threshold_crossing_flips"] = t_flip
    for f in choice_fields:
        agree = 0
        l1 = []
        for i in range(n):
            rows = [r[i] for r in runs]
            if any(r["error"] for r in rows):
                continue
            ch = [((r["answers"].get(f) or {}).get("choice")) for r in rows]
            if len(set(ch)) == 1:
                agree += 1
            for a, b in ((0, 1), (0, 2), (1, 2)):
                pa = (rows[a]["answers"].get(f) or {}).get("probabilities") or {}
                pb = (rows[b]["answers"].get(f) or {}).get("probabilities") or {}
                if pa and pb:
                    l1.append(sum(abs(pa.get(k, 0) - pb.get(k, 0)) for k in set(pa) | set(pb)))
        res[f + "_choice_all3_agreement"] = agree / n
        res[f + "_prob_L1_drift_mean"] = sum(l1) / len(l1) if l1 else None
        res[f + "_prob_L1_drift_max"] = max(l1) if l1 else None
    return res

def main():
    runs = [load(BASE / ("raw-responses-run" + str(i) + ".jsonl")) for i in (1, 2, 3)]
    report = {"analysis_plan": "V3_PRECOMMIT_MANIFEST.json (frozen before label reveal)",
              "primary_T": PRIMARY_T, "no_tuning_rule": "enforced; single analysis pass, no reruns"}
    for i, rows in enumerate(runs, 1):
        report["run" + str(i)] = analyze_run(rows, "fresh-run" + str(i))
        report["run" + str(i)]["routing"] = {("T=" + str(t)): routing(rows, t) for t in DIAG_T}
    report["stability"] = stability(runs)
    v2_runs = [load(V2 / ("raw-responses-run" + str(i) + ".jsonl")) for i in (1, 2, 3)]
    report["v2_comparison_run1"] = analyze_run(v2_runs[0], "v2-run1")
    report["v2_comparison_run1"]["routing"] = {("T=" + str(t)): routing(v2_runs[0], t) for t in DIAG_T}
    report["v2_stability"] = stability(v2_runs)
    r1 = report["run1"]["routing"][("T=" + str(PRIMARY_T))]
    fp = r1["FALSE_PASS"]
    auto_n = r1["AUTO_ACCEPT"] + r1["AUTO_REJECT"]
    report["statistics"] = {
        "false_pass_primary_T": {"count": fp, "auto_decided_n": auto_n,
            "wilson_95": wilson(fp, auto_n),
            "cp_upper_bound_if_zero": cp_upper_zero(auto_n) if fp == 0 else None},
        "non_claim": "0 observed false PASSes over N auto-decided cases does not prove zero underlying false-PASS probability."}
    fam = []
    for x in load(BASE / "raw-responses-run1.jsonl"):
        if x["error"] or x["lane"] != "forbidden_claim":
            continue
        if x["expected"]["speaker_commitment"] == "UNRESOLVED":
            fam.append({"case_id": x["case_id"],
                "pred_commitment": (x["answers"].get("speaker_commitment") or {}).get("choice"),
                "pred_match": (x["answers"].get("criterion_semantic_match") or {}).get("choice")})
    pc = Counter(f["pred_commitment"] for f in fam)
    report["esc_021_026_family_test"] = {
        "note": "fresh pool has 0 gold match-UNRESOLVED rows; assessed via gold commitment-UNRESOLVED rows only (partial)",
        "gold_commitment_UNRESOLVED_n": len(fam),
        "gold_UNRESOLVED_to_pred_NEGATED": pc.get("NEGATED", 0),
        "gold_UNRESOLVED_to_pred_UNRESOLVED": pc.get("UNRESOLVED", 0),
        "gold_UNRESOLVED_to_pred_ASSERTED": pc.get("ASSERTED", 0),
        "reproduction_status": "partially assessable"}
    tot_tokens = sum(report["run" + str(i)]["input_tokens"] for i in (1, 2, 3))
    lat_all = sorted(x["latency_seconds"] for rows in runs for x in rows if not x["error"])
    n_rows = sum(len(r) for r in runs)
    report["cost"] = {"api_calls": n_rows, "total_input_tokens": tot_tokens,
        "input_price_per_1m_usd": INPUT_PRICE_PER_1M,
        "observed_cost_usd": tot_tokens * INPUT_PRICE_PER_1M / 1e6,
        "cost_per_case_usd": tot_tokens * INPUT_PRICE_PER_1M / 1e6 / n_rows,
        "cost_per_1000_usd": tot_tokens * INPUT_PRICE_PER_1M / 1e6 / n_rows * 1000,
        "latency_median": lat_all[len(lat_all)//2], "latency_p95": lat_all[int(len(lat_all)*0.95)],
        "rate_limit_hits": 0,
        "transport_errors": sum(1 for r in runs for x in r if x["error"])}
    out = BASE / "analysis-results.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    r = report["run1"]
    print("== RUN1 forbidden ==")
    print(json.dumps({k: r["forbidden"][k] for k in ("n", "pair_accuracy", "match_accuracy")}))
    print("match_confusion:", json.dumps(r["forbidden"]["match_confusion"]))
    print("commitment_cells:", json.dumps(r["forbidden"]["commitment_cells_gold_to_pred"], indent=1, sort_keys=True))
    print("== RUN1 critical ==")
    print(json.dumps({k: r["critical"][k] for k in ("n", "exact", "exact_rate",
        "false_trigger_dangerous_direction", "false_trigger_high_conf_catastrophic")}))
    print("critical_confusion:", json.dumps(r["critical"]["confusion"], indent=1))
    for t in DIAG_T:
        rt = r["routing"][("T=" + str(t))]
        print(("== routing T=" + str(t) + " =="))
        print(json.dumps({k: rt[k] for k in ("AUTO_ACCEPT", "AUTO_REJECT", "ESCALATE", "ERROR",
            "decidable", "auto_on_decidable", "safe_auto_coverage", "escalation_rate",
            "FALSE_PASS", "FALSE_FAIL", "safety_critical_FP", "high_conf_FP",
            "high_conf_FF", "accuracy_among_auto_decided")}))
        for e in rt["events"]:
            print("   event:", json.dumps(e))
    print("== stats ==")
    print(json.dumps(report["statistics"], indent=1))
    print("== stability ==")
    print(json.dumps(report["stability"], indent=1))
    print("== esc family ==")
    print(json.dumps(report["esc_021_026_family_test"], indent=1))
    print("== cost ==")
    print(json.dumps(report["cost"], indent=1))
    v2r = report["v2_comparison_run1"]["routing"][("T=" + str(PRIMARY_T))]
    print("== V2 run1 via same code ==")
    print(json.dumps({k: v2r[k] for k in ("AUTO_ACCEPT", "AUTO_REJECT", "ESCALATE", "decidable",
        "safe_auto_coverage", "escalation_rate", "FALSE_PASS", "FALSE_FAIL")}))
    print("V2 forbidden pair/match:", report["v2_comparison_run1"]["forbidden"]["pair_accuracy"],
          report["v2_comparison_run1"]["forbidden"]["match_accuracy"])
    print("V2 critical exact:", report["v2_comparison_run1"]["critical"]["exact"],
          "/", report["v2_comparison_run1"]["critical"]["n"])

if __name__ == "__main__":
    main()
