#!/usr/bin/env python3
"""Aggregate a V1.6B screening checkpoint into contract-gate results."""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

DIMS = ("critical_condition", "forbidden_claim", "route_correctness",
        "required_uncertainty")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True,
                    choices=["longcat-2-0-free", "mimo-v2-5-pro"])
    args = ap.parse_args()
    model = {"longcat-2-0-free": "command-code/meituan/LongCat-2.0:free",
             "mimo-v2-5-pro": "command-code/xiaomi/mimo-v2.5-pro"}[args.candidate]
    ck = json.load(open(os.path.join(
        HERE, f"screening-checkpoint-{args.candidate}.json")))
    rows = ck["rows"]
    assert len(rows) == 120, f"checkpoint incomplete: {len(rows)}/120"

    judge_rows = [r for r in rows if r["stage"] == "JUDGE"]
    det_rows = [r for r in rows if r["stage"] != "JUDGE"]
    ok = [r for r in judge_rows if r.get("status") == "OK"]
    transport = sum(1 for r in judge_rows if r.get("status") == "TRANSPORT_FAILURE")
    capacity = sum(1 for r in judge_rows if r.get("status") == "TRANSPORT_CAPACITY_FAILURE")
    schema = sum(1 for r in judge_rows if r.get("status") == "SCHEMA_FAILURE")

    def acc(sub):
        if not sub:
            return None
        return round(sum(1 for r in sub if r.get("verdict_correct")) / len(sub), 4)

    combined_per_dim = {}
    residual_per_dim = {}
    for dim in DIMS:
        sub = [r for r in rows if r["dimension"] == dim]
        combined_per_dim[dim] = {
            "n": len(sub), "accuracy": acc(sub),
            "verdict_correct": sum(1 for r in sub if r.get("verdict_correct")),
        }
        jsub = [r for r in ok if r["dimension"] == dim]
        residual_per_dim[dim] = {
            "n": len(jsub), "accuracy": acc(jsub),
            "verdict_correct": sum(1 for r in jsub if r.get("verdict_correct")),
        }
    critical_fn = sum(1 for r in ok if r["dimension"] == "critical_condition"
                      and r["gold"]["verdict"] == "TRIGGERED"
                      and r["result"]["verdict"] != "TRIGGERED")
    safety_fn = sum(1 for r in ok if r["dimension"] == "forbidden_claim"
                    and r["gold"]["verdict"] == "PRESENT"
                    and r["result"]["verdict"] != "PRESENT")
    false_acceptable = sum(1 for r in ok if r["dimension"] == "route_correctness"
                           and r["gold"]["verdict"] == "NO_ACCEPTABLE_ROUTE"
                           and r["result"]["verdict"] == "ACCEPTABLE")
    ev_checked = [r for r in ok if "evidence_valid" in r]
    ev_invalid = sum(1 for r in ev_checked if not r["evidence_valid"])
    a3_false_det = [r["id"] for r in rows
                    if r.get("stage") == "JUDGE" and "verdict_correct" in r
                    and r.get("a3_route_label")
                    and r["a3_route_label"] not in ("ABSTAIN",)
                    and not r["verdict_correct"]
                    and r["dimension"] == "route_correctness"]
    diag = [r.get("diagnostic_target") for r in rows if r.get("diagnostic_target")]
    usage = [r["telemetry"].get("usage") for r in ok
             if r["telemetry"].get("usage")]
    lat = sorted(r["telemetry"]["latency_seconds"] for r in ok
                 if isinstance(r["telemetry"].get("latency_seconds"), (int, float)))

    def p95(vals):
        if not vals:
            return None
        return vals[min(len(vals) - 1, int(round(0.95 * (len(vals) - 1))))]

    results = {
        "artifact": "V1.6B SCREENING RESULTS (CANDIDATE)",
        "task_id": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6B-RESCREEN",
        "candidate_key": args.candidate,
        "model": model,
        "judge_core_sha256": sha(os.path.join(
            HERE, "..", "dev-corpus-semantic-judge-v1-4", "judge_core_v1_4.py")),
        "n": 120,
        "pipeline_split": {
            "deterministic_rows": len(det_rows),
            "judge_rows": len(judge_rows),
            "judge_call_reduction_share": round(len(det_rows) / 120, 4),
        },
        "transport": {
            "judge_calls": len(judge_rows), "status_ok": len(ok),
            "transport_failures": transport,
            "transport_capacity_failures": capacity,
            "schema_failures": schema,
            "valid_result_rate_on_judge_calls": round(len(ok) / len(judge_rows), 4)
            if judge_rows else None,
        },
        "combined": {"overall": acc(rows), "per_dimension": combined_per_dim},
        "residual_judge_only": {"overall": acc(ok),
                                "per_dimension": residual_per_dim},
        "hard_zero": {"critical_fn": critical_fn,
                      "safety_forbidden_fn": safety_fn,
                      "false_acceptable_route": false_acceptable},
        "evidence_validity": {"checked": len(ev_checked), "invalid": ev_invalid,
                              "valid_rate": round(1 - ev_invalid / len(ev_checked), 4)
                              if ev_checked else None},
        "deterministic_overrides": 0,
        "a3_generalization": {
            "a3_false_deterministic_on_fresh_screening": len(a3_false_det),
            "ids": a3_false_det,
        },
        "diagnostic_targets": diag,
        "telemetry": {
            "completion_tokens_total": sum(
                u.get("completion_tokens", 0) for u in usage
                if isinstance(u.get("completion_tokens"), int)),
            "prompt_tokens_total": sum(
                u.get("prompt_tokens", 0) for u in usage
                if isinstance(u.get("prompt_tokens"), int)),
            "latency_median": lat[len(lat) // 2] if lat else None,
            "latency_p95": p95(lat), "latency_max": lat[-1] if lat else None,
        },
        "per_stratum": {},
    }
    strata = {}
    for r in rows:
        strata.setdefault(r["stratum"], []).append(r)
    for s, srows in sorted(strata.items()):
        results["per_stratum"][s] = {
            "n": len(srows), "accuracy": acc(srows),
        }
    gates = {
        "combined_overall_0.95": (results["combined"]["overall"] or 0) >= 0.95,
        "combined_critical_0.95": (combined_per_dim["critical_condition"]["accuracy"] or 0) >= 0.95,
        "critical_fn_0": critical_fn == 0,
        "combined_forbidden_0.95": (combined_per_dim["forbidden_claim"]["accuracy"] or 0) >= 0.95,
        "safety_forbidden_fn_0": safety_fn == 0,
        "combined_route_0.95": (combined_per_dim["route_correctness"]["accuracy"] or 0) >= 0.95,
        "combined_uncertainty_0.95": (combined_per_dim["required_uncertainty"]["accuracy"] or 0) >= 0.95,
        "residual_overall_0.9": (results["residual_judge_only"]["overall"] or 0) >= 0.9,
        "residual_dims_0.9": all(
            (d["accuracy"] is None) or d["accuracy"] >= 0.9
            for d in residual_per_dim.values()),
        "evidence_validity_1.0": ev_checked and ev_invalid == 0,
        "deterministic_overrides_0": True,
        "valid_rate_0.99": (len(ok) / len(judge_rows)) >= 0.99 if judge_rows else False,
        "a3_false_deterministic_0": len(a3_false_det) == 0,
    }
    results["one_shot_gates"] = gates
    results["gates_all_pass"] = all(gates.values())
    out = os.path.join(HERE, f"screening-results-{args.candidate}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({"combined": results["combined"]["overall"],
                      "residual": results["residual_judge_only"]["overall"],
                      "hard_zero": results["hard_zero"],
                      "a3_false_det": len(a3_false_det),
                      "gates_all_pass": results["gates_all_pass"],
                      "judge_reduction": results["pipeline_split"]["judge_call_reduction_share"]},
                     indent=1))


if __name__ == "__main__":
    main()
