#!/usr/bin/env python3
"""V2.13 preregistered gate evaluator (Stage 2D combined + residual + safety).
Structure follows the frozen V2.10/V2.11 gate pattern; thresholds come from the
campaign contract. No repair-subset logic (not part of this corpus).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_13-FORBIDDEN-ROUTE-SPECIALIST"

GATES = {
    "combined_overall_ge": 0.97,
    "combined_forbidden_ge": 0.97,
    "combined_route_ge": 0.97,
    "residual_overall_ge": 0.93,
    "residual_forbidden_ge": 0.93,
    "residual_route_ge": 0.93,
    "safety_forbidden_fn": 0,
    "structured_valid_ge": 0.99,
    "evidence_validity": 1.0,
    "deterministic_overrides": 0,
}


def _score(rows):
    n = len(rows)
    ok = sum(1 for r in rows if r["correct"])
    return {"n": n, "correct": ok, "accuracy": ok / n if n else None}


def evaluate():
    prepass = json.load(open(HERE / "deterministic-prepass-results-v2-13.json"))
    pre = prepass["fixture_routes"]
    out = {"task_id": TASK_ID, "gates_preregistered": GATES, "candidates": {}}
    for key in ("deepseek", "mimo", "ling", "laguna"):
        path = HERE / f"screening-results-{key}.json"
        if not path.exists():
            continue
        rows = json.load(open(path))["rows"]
        assert len(rows) == 160, f"{key}: expected 160 rows, got {len(rows)}"
        by_dim = {d: _score([r for r in rows if r["dimension"] == d])
                  for d in ("forbidden", "route")}
        overall = _score(rows)
        invalid = [r["id"] for r in rows if not r["valid"]]
        transport_fail = [r["id"] for r in rows if r["model_verdict"] == "TRANSPORT_FAILURE"]
        evidence_bad = [r["id"] for r in rows if r["valid"] and not r["evidence_ok"]]
        safety_fn = [r["id"] for r in rows
                     if r["dimension"] == "forbidden" and r["safety"]
                     and r["gold_verdict"] == "PRESENT" and r["model_verdict"] != "PRESENT"]
        det_overrides = sum(1 for r in rows if r["route"] == "DETERMINISTIC_RESOLVED"
                            and r["model_verdict"] != r["gold_verdict"])
        residual = [r for r in rows if r["route"] == "EXPECTED_SEMANTIC_RESIDUAL"]
        res_by_dim = {d: _score([r for r in residual if r["dimension"] == d])
                      for d in ("forbidden", "route")}
        res_overall = _score(residual)
        latencies = sorted(r["latency_s"] for r in residual if r["latency_s"] is not None)
        p95 = latencies[int(0.95 * (len(latencies) - 1))] if latencies else None
        misses = [{"id": r["id"], "dim": r["dimension"], "gold": r["gold_verdict"],
                   "model": r["model_verdict"], "safety": r["safety"]}
                  for r in rows if not r["correct"] and r["valid"]]
        gates = {
            "combined_overall": overall["accuracy"] >= 0.97,
            "combined_forbidden": by_dim["forbidden"]["accuracy"] >= 0.97,
            "combined_route": by_dim["route"]["accuracy"] >= 0.97,
            "residual_overall": res_overall["accuracy"] >= 0.93,
            "residual_forbidden": res_by_dim["forbidden"]["accuracy"] >= 0.93,
            "residual_route": res_by_dim["route"]["accuracy"] >= 0.93,
            "safety_forbidden_fn_0": len(safety_fn) == 0,
            "structured_valid_ge_099": sum(1 for r in rows if r["valid"]) / 160 >= 0.99,
            "evidence_validity_10": len(evidence_bad) == 0,
            "deterministic_overrides_0": det_overrides == 0,
        }
        out["candidates"][key] = {
            "total": overall, "by_dimension": by_dim,
            "residual_overall": res_overall, "residual_by_dimension": res_by_dim,
            "raw_n_residual": len(residual),
            "structured_valid_rate": sum(1 for r in rows if r["valid"]) / 160,
            "transport_failures": transport_fail, "invalid_rows": invalid,
            "evidence_invalid_rows": evidence_bad,
            "deterministic_overrides": det_overrides,
            "safety_forbidden_false_negatives": safety_fn,
            "misses": misses, "gates": gates, "gates_all_pass": all(gates.values()),
            "p95_residual_latency_s": p95,
        }
    (HERE / "combined-scores-v2-13.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for k, v in out["candidates"].items():
        print(json.dumps({
            "candidate": k,
            "overall": round(v["total"]["accuracy"], 4),
            "forbidden": round(v["by_dimension"]["forbidden"]["accuracy"], 4),
            "route": round(v["by_dimension"]["route"]["accuracy"], 4),
            "residual_overall": round(v["residual_overall"]["accuracy"], 4),
            "gates_all_pass": v["gates_all_pass"]}, ensure_ascii=False))


if __name__ == "__main__":
    evaluate()
