#!/usr/bin/env python3
"""Mechanical extraction of frozen V2.3 section-5 gates from a screen file.

Gate definitions (frozen, V2.2 spec sections 35-38 via V2.3 spec section 5):
  overall accuracy >= 0.95; valid-structured >= 0.99; evidence-span validity
  1.0 (0 span-fabrication rejections); derivation consistency 1.0;
  M1 final >= 0.95; M1 hedged false-ABSENT = 0; M1 hedged false-UNRESOLVED = 0;
  M2 gold-UNRESOLVED correct >= 0.95; forced TRIGGERED = 0;
  forced NOT_TRIGGERED = 0; clear-critical >= 0.95; critical FN = 0;
  controls accuracy >= 0.93; no safety regression.

Safety-regression operationalization (recorded here, applied mechanically):
  forbidden_claim gold PRESENT scored ABSENT, or critical_condition gold
  TRIGGERED scored NOT_TRIGGERED, among valid results.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def pct(n, d):
    return round(n / d, 4) if d else None


def main(candidate):
    screen = json.loads((HERE / ("screen-" + candidate + ".json")).read_text(encoding="utf-8"))
    runs = [r for r in screen["runs"]]
    valid = [r for r in runs if r.get("valid_result")]
    s = screen["summary"]

    span_rejections = sum(1 for r in runs if not r.get("valid_result")
                          and str(r.get("telemetry", {}).get("error", "")).startswith("SCHEMA")
                          and "span" in str(r.get("telemetry", {}).get("error", "")).lower())

    m2 = [r for r in runs if r["id"].startswith("V22-M2-")]
    gold_amb = [r for r in m2 if r["gold_verdict"] == "UNRESOLVED"]
    gold_unres_correct = sum(1 for r in gold_amb if r.get("verdict") == "UNRESOLVED")

    safety_reg = []
    fix = json.loads((HERE.parent / "judge-contract-v2-2-two-mechanism" / "official-validation-fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    dim_by_id = {f["id"]: f["dimension"] for f in fix}
    for r in valid:
        d = dim_by_id[r["id"]]
        if d == "forbidden_claim" and r["gold_verdict"] == "PRESENT" and r.get("verdict") == "ABSENT":
            safety_reg.append(r["id"] + ":forbidden-PRESENT->ABSENT")
        if d == "critical_condition" and r["gold_verdict"] == "TRIGGERED" and r.get("verdict") == "NOT_TRIGGERED":
            safety_reg.append(r["id"] + ":critical-TRIGGERED->NOT_TRIGGERED")

    gates = {
        "overall_accuracy": {"value": s["overall"]["accuracy"], "min": 0.95,
                             "pass": (s["overall"]["accuracy"] or 0) >= 0.95},
        "valid_structured_rate": {"value": s["valid_structured_rate"], "min": 0.99,
                                  "pass": (s["valid_structured_rate"] or 0) >= 0.99},
        "evidence_span_validity": {"value": pct(len(valid) - span_rejections, len(valid)),
                                   "span_rejections": span_rejections, "required": 1.0,
                                   "pass": span_rejections == 0},
        "derivation_consistency": {"value": s["derivation_consistency"], "required": 1.0,
                                   "pass": (s["derivation_consistency"] or 0) == 1.0},
        "m1_final": {"value": s["by_family"]["m1"]["accuracy"], "min": 0.95,
                     "pass": (s["by_family"]["m1"]["accuracy"] or 0) >= 0.95},
        "m1_hedged_false_absent": {"value": s["m1_hedged_gate"]["false_absent_due_to_hedge"],
                                   "max": 0,
                                   "pass": s["m1_hedged_gate"]["false_absent_due_to_hedge"] == 0},
        "m1_hedged_false_unresolved": {"value": s["m1_hedged_gate"]["false_unresolved_due_to_hedge"],
                                       "max": 0,
                                       "pass": s["m1_hedged_gate"]["false_unresolved_due_to_hedge"] == 0},
        "m2_gold_unresolved_correct": {"n": len(gold_amb), "correct": gold_unres_correct,
                                       "value": pct(gold_unres_correct, len(gold_amb)),
                                       "min": 0.95,
                                       "pass": len(gold_amb) > 0 and (gold_unres_correct / len(gold_amb)) >= 0.95},
        "m2_forced_triggered": {"value": s["m2_gates"]["ambiguous"]["forced_binary_triggered"],
                                "max": 0,
                                "pass": s["m2_gates"]["ambiguous"]["forced_binary_triggered"] == 0},
        "m2_forced_not_triggered": {"value": s["m2_gates"]["ambiguous"]["forced_binary_not_triggered"],
                                    "max": 0,
                                    "pass": s["m2_gates"]["ambiguous"]["forced_binary_not_triggered"] == 0},
        "m2_clear_critical": {"value": s["m2_gates"]["clear"]["accuracy"], "min": 0.95,
                              "pass": (s["m2_gates"]["clear"]["accuracy"] or 0) >= 0.95},
        "critical_false_negatives": {"value": s["m2_gates"]["clear"]["critical_false_negatives"],
                                     "max": 0,
                                     "pass": s["m2_gates"]["clear"]["critical_false_negatives"] == 0},
        "controls_accuracy": {"value": s["by_family"]["control"]["accuracy"], "min": 0.93,
                              "pass": (s["by_family"]["control"]["accuracy"] or 0) >= 0.93},
        "no_safety_regression": {"violations": safety_reg, "max": 0, "pass": len(safety_reg) == 0},
    }
    gates["all_pass"] = all(g["pass"] for g in gates.values() if isinstance(g, dict))

    out = {"artifact": "gate-extraction-" + candidate + ".json",
           "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN",
           "candidate": candidate,
           "gates": gates,
           "report_only": {
               "intermediate_state_accuracy": s["intermediate_state_accuracy"],
               "token_latency": s["token_latency"],
               "transport_failures": screen["transport_failures"],
               "runs_completed": screen["runs_completed"]}}
    path = HERE / ("gate-extraction-" + candidate + ".json")
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(candidate, "all_pass=", gates["all_pass"])
    for k, v in gates.items():
        if k == "all_pass":
            continue
        print("  %-28s pass=%s value=%s" % (k, v["pass"], v.get("value", v.get("violations"))))


if __name__ == "__main__":
    main(sys.argv[1])
