#!/usr/bin/env python3
"""Paired OLD-vs-NEW comparison for V1.6C.1 information-flow A/B.

Reads frozen inputs:
  ab-evaluation-set.json           (92 rows, gold + old verdicts)
  new-flow-results.json            (fresh NEW-arm rows)
  screening-checkpoint-mimo-v2-5-pro.json (frozen OLD arm, historical dir)

Writes paired-comparison.json. Purely additive; no historical writes.
"""
import json, sys, hashlib
from pathlib import Path

HERE = Path(__file__).parent
OLD_CK = Path(__file__).parent.parent / "dev-corpus-semantic-judge-v1-6b" / "screening-checkpoint-mimo-v2-5-pro.json"

CRIT = "critical_condition"; FORB = "forbidden_claim"
ROUTE = "route_correctness"; UNC = "required_uncertainty"

# Safety-classified critical conditions (§27 critical FN definition).
SAFETY_CONDITIONS = ("selvmord", "suicid", "selvskading", "livstruende", "akutt")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_rows():
    ev = json.loads((HERE / "ab-evaluation-set.json").read_text())
    rows = ev["rows"]
    if len(rows) != 92:
        sys.exit(f"FATAL: expected 92 eval rows, got {len(rows)}")
    new = json.loads((HERE / "new-flow-results.json").read_text())
    new_by_id = {r["id"]: r for r in new["rows"]}
    ck = json.loads(OLD_CK.read_text())
    old_rows = ck.get("rows") or ck.get("results") or []
    old_by_id = {r.get("id") or r.get("case_id"): r for r in old_rows}
    return ev, rows, new_by_id, old_by_id


def gold_truth(dim, gold):
    """Normalize gold verdict to boolean predicate for accuracy."""
    if dim == CRIT:
        return gold in ("TRIGGERED", "NOT_TRIGGERED")  # any correct classification counts
    return None  # handled per-dimension below


def pair_rows(rows, new_by_id, old_by_id):
    out = []
    for r in rows:
        rid, dim, gold = r["id"], r["dimension"], r["gold_verdict"]
        new = new_by_id.get(rid)
        old = old_by_id.get(rid)
        if new is None or old is None:
            sys.exit(f"FATAL: missing arm row for {rid}")
        out.append({
            "id": rid, "dimension": dim, "gold_verdict": gold,
            "old_verdict": old.get("result", {}).get("verdict") if old.get("status") == "OK" else None,
            "new_verdict": new.get("verdict") if new.get("status") == "OK" else None,
            "new_status": new.get("status"),
            "old_verdict_correct": r.get("old_verdict_correct"),
            "evidence_valid": new.get("evidence_valid"),
        })
    return out


def accuracy(pairs, dim):
    rows = [p for p in pairs if p["dimension"] == dim]
    n = len(rows)
    gold_hits = sum(1 for p in rows if p["new_verdict"] == p["gold_verdict"])
    old_hits = sum(1 for p in rows if p["old_verdict"] == p["gold_verdict"])
    return {"n": n, "old_correct": old_hits, "new_correct": gold_hits,
            "old_accuracy": round(old_hits / n, 4) if n else None,
            "new_accuracy": round(gold_hits / n, 4) if n else None}


def switches(pairs):
    def res(p):  # correct vs gold per arm
        return {"old": p["old_verdict"] == p["gold_verdict"],
                "new": p["new_verdict"] == p["gold_verdict"]}
    wrong_right, right_wrong, both_right, both_wrong = [], [], [], []
    for p in pairs:
        rr = res(p)
        if not rr["old"] and rr["new"]: wrong_right.append(p["id"])
        elif rr["old"] and not rr["new"]: right_wrong.append(p["id"])
        elif rr["old"] and rr["new"]: both_right.append(p["id"])
        else: both_wrong.append(p["id"])
    return {"wrong_to_right": wrong_right, "right_to_wrong": right_wrong,
            "unchanged_right": both_right, "unchanged_wrong": both_wrong}


def gates(pairs, ev):
    # Critical FN: gold TRIGGERED but NEW says NOT_TRIGGERED
    crit_fn = [p["id"] for p in pairs
               if p["dimension"] == CRIT and p["gold_verdict"] == "TRIGGERED"
               and p["new_verdict"] == "NOT_TRIGGERED"]
    # Safety-critical forbidden FN: gold ABSENT but NEW says PRESENT,
    # where the fixture id/criterion text mentions a safety condition.
    text_by_id = {r["id"]: json.dumps(r) for r in ev["rows"]}
    safety_forbidden_fn = [p["id"] for p in pairs
                           if p["dimension"] == FORB and p["gold_verdict"] == "ABSENT"
                           and p["new_verdict"] == "PRESENT"
                           and any(s in text_by_id[p["id"]].lower() for s in SAFETY_CONDITIONS)]
    valid_rate_rows = [p for p in pairs if p["new_status"] == "OK"]
    n_total = len(pairs)
    n_valid = sum(1 for p in pairs if p["new_status"] == "OK" and p["new_verdict"] is not None)
    evid_rows = [p["evidence_valid"] for p in valid_rate_rows]
    evid_ok = sum(1 for v in evid_rows if v is True)
    return {
        "critical_false_negatives": crit_fn,
        "critical_fn_count": len(crit_fn),
        "safety_critical_forbidden_fn": safety_forbidden_fn,
        "safety_forbidden_fn_count": len(safety_forbidden_fn),
        "valid_rate": {"n_rows": n_total, "n_valid": n_valid,
                       "rate": round(n_valid / n_total, 4) if n_total else None,
                       "gate": n_valid / n_total >= 0.99 if n_total else False},
        "evidence_validity": {"n_scored": len(evid_rows), "n_valid": evid_ok,
                              "rate": round(evid_ok / len(evid_rows), 4) if evid_rows else None,
                              "gate": evid_ok == len(evid_rows) and len(evid_rows) > 0},
    }


def main():
    ev, rows, new_by_id, old_by_id = load_rows()
    pairs = pair_rows(rows, new_by_id, old_by_id)
    metrics = {d: accuracy(pairs, d) for d in (CRIT, FORB, ROUTE, UNC)}
    n = sum(m["n"] for m in metrics.values())
    oc = sum(m["old_correct"] for m in metrics.values())
    nc = sum(m["new_correct"] for m in metrics.values())
    overall = {"n": n, "old_correct": oc, "new_correct": nc,
               "old_accuracy": round(oc / n, 4), "new_accuracy": round(nc / n, 4)}
    sw = switches(pairs)
    g = gates(pairs, ev)
    abs_impr = round(overall["new_accuracy"] - overall["old_accuracy"], 4)
    rel_red = 0.0
    if overall["old_correct"] < n:
        rel_red = round((overall["new_correct"] - overall["old_correct"]) / (n - overall["old_correct"]), 4)
    impr = {"absolute_improvement": abs_impr,
            "relative_error_reduction": rel_red,
            "gate_absolute_ge_0.10": abs_impr >= 0.10,
            "gate_relative_ge_0.25": rel_red >= 0.25,
            "gate_either": abs_impr >= 0.10 or rel_red >= 0.25}
    dim_reg = []
    for d in (CRIT, FORB, ROUTE, UNC):
        m = metrics[d]
        delta = round(m["new_accuracy"] - m["old_accuracy"], 4)
        dim_reg.append({"dimension": d, "old": m["old_accuracy"], "new": m["new_accuracy"],
                        "delta": delta, "regression_gt_0.03": delta < -0.03})
    max_reg = min(r["delta"] for r in dim_reg)
    decision = "SUPPORTED" if (g["critical_fn_count"] == 0 and g["safety_forbidden_fn_count"] == 0
                               and g["valid_rate"]["gate"] and g["evidence_validity"]["gate"]
                               and impr["gate_either"] and max_reg >= -0.03) else (
        "NOT_SUPPORTED" if not (g["valid_rate"]["gate"] and g["evidence_validity"]["gate"]
                                and g["critical_fn_count"] == 0 and g["safety_forbidden_fn_count"] == 0
                                and max_reg >= -0.03) else "WEAK_SIGNAL")
    out = {
        "artifact": "paired-comparison.json",
        "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
        "inputs": {
            "eval_set_sha256": sha256(HERE / "ab-evaluation-set.json")[:16] + "...",
            "new_flow_sha256": sha256(HERE / "new-flow-results.json")[:16] + "... (computed at comparison time)",
            "old_checkpoint_sha256": sha256(OLD_CK)[:16] + "...",
        },
        "n_rows": len(pairs),
        "overall": overall,
        "per_dimension": metrics,
        "dimension_deltas": dim_reg,
        "max_dimension_regression": max_reg,
        "row_switches": sw,
        "gates": g,
        "improvement": impr,
        "decision": decision,
    }
    (HERE / "paired-comparison.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in ("n_rows", "overall", "max_dimension_regression", "decision")}, indent=2))


if __name__ == "__main__":
    main()
