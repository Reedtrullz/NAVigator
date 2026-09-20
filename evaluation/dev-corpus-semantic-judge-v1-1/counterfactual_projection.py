#!/usr/bin/env python3
"""Mechanisk kontrafaktisk projeksjon av frosne V1-resultater paa V1.1 kontrakt.

BURNED_COUNTERFACTUAL_NOT_VALIDATION: ingen modellkall, ingen historical
skriving. Leser kun evaluation/dev-corpus-semantic-judge-v1/ resultater.
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "dev-corpus-semantic-judge-v1")

ROUTE_MAP = {
    "CANONICAL_ACCEPTABLE": "ACCEPTABLE",
    "EQUIVALENT_ACCEPTABLE": "ACCEPTABLE",
}


def project(verdict, dimension):
    if dimension == "route_equivalence":
        return ROUTE_MAP.get(verdict, verdict)
    return verdict


def main():
    with open(os.path.join(V1, "official-validation-results.json"), encoding="utf-8") as f:
        v1 = json.load(f)
    with open(os.path.join(V1, "stability-results.json"), encoding="utf-8") as f:
        stab = json.load(f)

    rows = []
    for r in v1["rows"]:
        projected = project(r["actual"], r["dimension"])
        projected_gold = project(r["gold"], r["dimension"])
        rows.append({
            "id": r["id"], "dimension": r["dimension"],
            "gold_v1": r["gold"],
            "gold_v1_1": projected_gold,
            "actual_v1": r["actual"],
            "actual_v1_1": projected,
            "correct_v1": r["correct"],
            "correct_v1_1": projected == projected_gold,
        })
    total = len(rows)
    correct_v1 = sum(r["correct_v1"] for r in rows)
    correct_v11 = sum(r["correct_v1_1"] for r in rows)
    route = [r for r in rows if r["dimension"] == "route_equivalence"]
    route_v1 = sum(r["correct_v1"] for r in route)
    route_v11 = sum(r["correct_v1_1"] for r in route)
    boundary_fixed = sum(1 for r in route if not r["correct_v1"] and r["correct_v1_1"])

    stab_rows = []
    for s in stab["rows"]:
        projected = [project(v, s["dimension"]) for v in s["verdicts"]]
        counts = Counter(projected)
        modal_n = counts.most_common(1)[0][1]
        stab_rows.append({
            "id": s["id"], "dimension": s["dimension"],
            "verdicts_v1": s["verdicts"],
            "verdicts_v1_1": projected,
            "modal_agreement_v1": s["modal_agreement"],
            "modal_agreement_v1_1": modal_n / stab["runs_per_fixture"],
        })
    stable_v1 = sum(1 for s in stab_rows if s["modal_agreement_v1"] >= 0.95)
    stable_v11 = sum(1 for s in stab_rows if s["modal_agreement_v1_1"] >= 0.95)

    out = {
        "marker": "BURNED_COUNTERFACTUAL_NOT_VALIDATION",
        "method": "mechanical-only map CANONICAL_ACCEPTABLE->ACCEPTABLE, EQUIVALENT_ACCEPTABLE->ACCEPTABLE; ingen modellkall",
        "source_artifacts": {
            "official_results": "evaluation/dev-corpus-semantic-judge-v1/official-validation-results.json",
            "stability_results": "evaluation/dev-corpus-semantic-judge-v1/stability-results.json",
        },
        "official_validation": {
            "fixtures": total,
            "v1_overall_accuracy": round(correct_v1 / total, 4),
            "projected_v1_1_overall_accuracy": round(correct_v11 / total, 4),
            "route_n": len(route),
            "v1_route_accuracy": round(route_v1 / len(route), 4),
            "projected_v1_1_route_accuracy": round(route_v11 / len(route), 4),
            "boundary_misses_fixed": boundary_fixed,
        },
        "stability_projection": {
            "derivable": True,
            "fixtures": len(stab_rows),
            "v1_stability_rate": round(stable_v1 / len(stab_rows), 4),
            "projected_v1_1_stability_rate": round(stable_v11 / len(stab_rows), 4),
            "note": "modal agreement beregnet paa projiserte verdier; V1 verdict-sekvenser er uendret",
        },
        "rows": rows,
        "stability_rows": stab_rows,
    }
    with open(os.path.join(HERE, "burned-counterfactual-projection.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"overall: V1 {out['official_validation']['v1_overall_accuracy']} -> "
          f"projected {out['official_validation']['projected_v1_1_overall_accuracy']}")
    print(f"route: V1 {out['official_validation']['v1_route_accuracy']} -> "
          f"projected {out['official_validation']['projected_v1_1_route_accuracy']}")
    print(f"stability: V1 {out['stability_projection']['v1_stability_rate']} -> "
          f"projected {out['stability_projection']['projected_v1_1_stability_rate']}")


if __name__ == "__main__":
    main()
