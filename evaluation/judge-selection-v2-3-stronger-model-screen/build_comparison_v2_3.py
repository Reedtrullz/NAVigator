#!/usr/bin/env python3
"""Freeze candidate comparison BEFORE any selection statement (section 8.9)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
CANDIDATES = ["mimo-v2-5", "ling-3-0-flash-sante-free", "poolside-laguna-s-2-1-free",
              "deepseek-v4-1-flash"]
PRIORITY = {"mimo-v2-5": 1, "ling-3-0-flash-sante-free": 2,
            "poolside-laguna-s-2-1-free": 3, "deepseek-v4-1-flash": 4}


def load(name):
    p = HERE / name
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    candidates = {}
    for c in CANDIDATES:
        screen = load("screen-" + c + ".json")
        gates = load("gate-extraction-" + c + ".json")
        stab = load("stability-" + c + ".json")
        if screen is None and gates is None:
            candidates[c] = {"priority": PRIORITY[c], "screened": False}
            continue
        g = gates["gates"] if gates else None
        candidates[c] = {
            "priority": PRIORITY[c],
            "model": screen["model"],
            "screened": True,
            "runs_completed": screen["runs_completed"],
            "transport_failures": screen["transport_failures"],
            "overall_accuracy": screen["summary"]["overall"]["accuracy"],
            "gates_all_pass": g["all_pass"] if g else None,
            "failed_gates": sorted(k for k, v in (g or {}).items()
                                   if isinstance(v, dict) and not v.get("pass")),
            "stability": ({"agreement_rate": stab["one_shot_agreement"]["rate"],
                           "stability_pass": stab["stability_pass"]} if stab else None),
            "qualifies": bool(g and g["all_pass"] and stab and stab["stability_pass"]),
        }

    qualifiers = sorted((c for c, v in candidates.items() if v.get("qualifies")),
                        key=lambda c: PRIORITY[c])
    out = {"artifact": "candidate-comparison",
           "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN",
           "comparison_frozen_before_selection": True,
           "selection_rule": "V2.3 spec section 6 verbatim; highest-priority qualifier; no best-of-bad",
           "candidates": candidates,
           "qualifiers": qualifiers,
           "selected": qualifiers[0] if qualifiers else None,
           "selected_model": candidates[qualifiers[0]]["model"] if qualifiers else None}
    (HERE / "candidate-comparison.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(json.dumps({c: {"screened": v.get("screened"),
                          "overall": v.get("overall_accuracy"),
                          "gates": v.get("gates_all_pass"),
                          "failed": v.get("failed_gates"),
                          "stab": (v.get("stability") or {}).get("stability_pass"),
                          "qualifies": v.get("qualifies")}
                      for c, v in candidates.items()}, indent=2))
    print("SELECTED:", out["selected"] or "NONE -> V2_3_NO_MODEL_QUALIFIES")


if __name__ == "__main__":
    main()
