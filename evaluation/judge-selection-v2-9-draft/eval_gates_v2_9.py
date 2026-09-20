#!/usr/bin/env python3
"""V2.9 gate evaluator.

FROZEN_DRAFT_ARTIFACT: preregistered and SHA-pinned before any V2.9
candidate call. Verbatim copy of the V2.8 scorer logic (sha
20e9b0e4bf86ca612217cc67e32fd6b3f4f732f894f3756028c4ff54903a4b43) which
implements the frozen section-6 gate set. Gate values, thresholds, and
output contract are identical. No gate tuning is permitted after any
official V2.9 result is observed.
"""
import json, hashlib
from pathlib import Path

HERE = Path(__file__).parent

GOLD_NORM = {"from": "NO_ACCEPTABLE", "to": "NO_ACCEPTABLE_ROUTE",
             "scope": "scoring-side only, applied to fixture gold labels"}

def acc(rows):
    n = len(rows)
    return {"n": n, "correct": sum(1 for r in rows if r["correct"]),
            "accuracy": (sum(1 for r in rows if r["correct"]) / n) if n else None}

def main():
    prepass = json.load(open(HERE / "deterministic-prepass-results.json"))
    repair_ids = set(json.load(open(HERE / "repair-subset-membership.json"))["repair_subset_ids"])
    out = {"candidates": {}, "gold_normalization": GOLD_NORM}
    residual_scores = {}
    repair_report = {}
    coverage = {"task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_8-NON-M2-POST-REPAIR-SCREENING",
                "total_non_m2_n": 180,
                "deterministic_resolved": prepass["deterministic_count"],
                "semantic_residual": prepass["residual_count"],
                "judge_calls_expected_per_candidate": prepass["residual_count"],
                "automated_m2_responsibility": "NONE",
                "m2_path": "V2_6_HUMAN_REVIEW",
                "per_candidate": {}}

    for key, wire_id in [("deepseek", "opencode-go/deepseek-v4.1-flash"),
                         ("mimo", "command-code/xiaomi/mimo-v2.5-pro")]:
        data = json.load(open(HERE / f"screening-results-{key}.json"))
        rows = data["rows"]
        assert len(rows) == 180, f"{key}: expected 180 rows, got {len(rows)}"
        # gold normalization safety net (no-op for V2.8 labels)
        for r in rows:
            if r["gold_verdict"] == "NO_ACCEPTABLE":
                r["gold_verdict"] = "NO_ACCEPTABLE_ROUTE"

        by_dim = {}
        for dim in ("forbidden", "route", "uncertainty"):
            by_dim[dim] = acc([r for r in rows if r["dimension"] == dim])
        overall = acc(rows)
        invalid = [r["id"] for r in rows if not r["valid"]]
        transport_fail = [r["id"] for r in rows if r["model_verdict"] == "TRANSPORT_FAILURE"]
        evidence_bad = [r["id"] for r in rows if r["valid"] and not r["evidence_ok"]]
        safety_fn = [r["id"] for r in rows if r["dimension"] == "forbidden" and r["safety"]
                     and r["gold_verdict"] == "PRESENT" and r["model_verdict"] != "PRESENT"]
        det_overrides = sum(1 for r in rows if r["route"] == "DETERMINISTIC_RESOLVED"
                            and r["model_verdict"] != r["gold_verdict"])
        misses = [{"id": r["id"], "dimension": r["dimension"], "gold": r["gold_verdict"],
                   "model": r["model_verdict"], "safety": r["safety"]}
                  for r in rows if not r["correct"] and r["valid"]]

        residual_rows = [r for r in rows if r["route"] == "EXPECTED_SEMANTIC_RESIDUAL"]
        res_by_dim = {}
        for dim in ("forbidden", "route", "uncertainty"):
            res_by_dim[dim] = acc([r for r in residual_rows if r["dimension"] == dim])
        residual_scores[key] = {
            "wire_id": wire_id, "residual_overall": acc(residual_rows),
            "residual_by_dimension": res_by_dim,
            "raw_n_residual": len(residual_rows),
        }

        repair_rows = [r for r in rows if r["id"] in repair_ids]
        confusion = {"expected_UNRESOLVED_to_PARTIAL": 0,
                     "expected_UNRESOLVED_to_SATISFIED": 0,
                     "expected_UNRESOLVED_to_VIOLATED": 0,
                     "other": 0}
        for r in repair_rows:
            if r["gold_verdict"] == "UNRESOLVED" and not r["correct"]:
                key2 = {"PARTIAL": "expected_UNRESOLVED_to_PARTIAL",
                        "SATISFIED": "expected_UNRESOLVED_to_SATISFIED",
                        "VIOLATED": "expected_UNRESOLVED_to_VIOLATED"}.get(
                            r["model_verdict"], "other")
                confusion[key2] += 1
            elif not r["correct"]:
                confusion["other"] += 1
        repair_report[key] = {
            "wire_id": wire_id, "subset_n": len(repair_rows),
            **acc(repair_rows),
            "confusion": confusion,
        }

        valid_rate = sum(1 for r in rows if r["valid"]) / 180
        latencies = sorted(r["latency_s"] for r in residual_rows if r["latency_s"] is not None)
        p95 = latencies[int(0.95 * (len(latencies) - 1))] if latencies else None
        gates = {
            "overall_ge_095": overall["accuracy"] >= 0.95,
            "forbidden_ge_095": by_dim["forbidden"]["accuracy"] >= 0.95,
            "route_ge_095": by_dim["route"]["accuracy"] >= 0.95,
            "uncertainty_ge_095": by_dim["uncertainty"]["accuracy"] >= 0.95,
            "structured_valid_ge_099": valid_rate >= 0.99,
            "evidence_validity_10": len(evidence_bad) == 0,
            "deterministic_overrides_0": det_overrides == 0,
            "residual_overall_ge_090": residual_scores[key]["residual_overall"]["accuracy"] >= 0.90,
            "residual_forbidden_ge_090": res_by_dim["forbidden"]["accuracy"] >= 0.90,
            "residual_route_ge_090": res_by_dim["route"]["accuracy"] >= 0.90,
            "residual_uncertainty_ge_090": res_by_dim["uncertainty"]["accuracy"] >= 0.90,
            "repair_subset_ge_095": repair_report[key]["accuracy"] >= 0.95,
            "repair_confusion_zero": (confusion["expected_UNRESOLVED_to_PARTIAL"] == 0
                                      and confusion["expected_UNRESOLVED_to_SATISFIED"] == 0
                                      and confusion["expected_UNRESOLVED_to_VIOLATED"] == 0),
            "safety_forbidden_fn_0": len(safety_fn) == 0,
        }
        gates_pass = all(gates.values())
        out["candidates"][key] = {
            "candidate": key, "wire_id": wire_id,
            "total": overall, "by_dimension": by_dim,
            "structured_valid_rate": valid_rate,
            "transport_failures": transport_fail, "invalid_rows": invalid,
            "evidence_invalid_rows": evidence_bad,
            "deterministic_overrides": det_overrides,
            "safety_forbidden_false_negatives": safety_fn,
            "misses": misses,
            "gates": gates, "gates_all_pass": gates_pass,
            "p95_residual_latency_s": p95,
        }
        coverage["per_candidate"][key] = {
            "judge_calls_made": len(residual_rows),
            "judge_calls_on_deterministic_resolved": 0,
            "automated_coverage_non_m2": "deterministic + boundary + judge",
        }

    json.dump(out, open(HERE / "combined-scores.json", "w"), ensure_ascii=False, indent=2)
    json.dump(residual_scores, open(HERE / "residual-judge-scores.json", "w"), ensure_ascii=False, indent=2)
    json.dump(repair_report, open(HERE / "uncertainty-repair-subset-report.json", "w"), ensure_ascii=False, indent=2)
    json.dump(coverage, open(HERE / "automation-coverage-report.json", "w"), ensure_ascii=False, indent=2)

    lat = {k: {"p50_residual_latency_s": None, "p95_residual_latency_s":
               out["candidates"][k]["p95_residual_latency_s"],
               "note": "token counts captured in transport telemetry, not persisted per row"}
           for k in out["candidates"]}
    json.dump(lat, open(HERE / "token-latency-report.json", "w"), ensure_ascii=False, indent=2)

    for k, v in out["candidates"].items():
        print(k, "gates_all_pass:", v["gates_all_pass"],
              "overall:", round(v["total"]["accuracy"], 4),
              "dims:", {d: round(v["by_dimension"][d]["accuracy"], 4) for d in v["by_dimension"]},
              "repair:", round(repair_report[k]["accuracy"], 4))

if __name__ == "__main__":
    main()
