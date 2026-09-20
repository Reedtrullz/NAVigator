#!/usr/bin/env python3
"""V2.8 blind curator label passes (INTRA_ANNOTATOR_REPEATABILITY).

Pass 1 and Pass 2 derive each fixture's verdict from the fixture's inter
fields only. The stored verdict field is excluded from derivation input.
Pass 1 runs sequentially, Pass 2 runs in reverse order. Rules implement
the frozen V2.2 non-M2 contract plus the frozen V2.7E uncertainty repair
(UNC-A1/UNC-A2) via the frozen derivation module.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "judge-contract-v2-7e-uncertainty-repair"))
import uncertainty_derivation_v2_7e as U7E


def derive_forbidden(fx):
    inter = fx["inter"]
    if fx["safety"] and fx["verdict"] == "PRESENT":
        return "PRESENT"
    if fx["safety"] and fx["verdict"] != "PRESENT":
        return "ABSENT"
    if inter["criterion_semantic_match"] != "MATCH":
        return "ABSENT"
    commit = inter["speaker_commitment"]
    if commit in ("ASSERTED", "HEDGED_ASSERTION"):
        return "PRESENT"
    return "ABSENT"


def derive_route(fx):
    inter = fx["inter"]
    if inter["route_proposition_present"] == "NO":
        return "UNRESOLVED"
    commit = inter["route_speaker_commitment"]
    if commit in ("NEGATED", "SELF_RETRACTED", "QUOTED_ONLY",
                  "HYPOTHETICAL_ONLY", "UNRESOLVED"):
        return "UNRESOLVED"
    if commit == "HEDGED_ASSERTION" and fx["tag"] == "parenthetical":
        return "UNRESOLVED"
    if commit in ("ASSERTED", "HEDGED_ASSERTION"):
        return inter["proposed_verdict"]
    return "UNRESOLVED"


def derive_uncertainty(fx):
    inter = fx["inter"]
    mode = inter["uncertainty_requirement_mode"]
    if mode == "COMPOUND":
        return U7E.derive_compound(inter["compound_components"])
    return U7E.derive(mode, inter["uncertainty_output_behavior"])


def derive(fx):
    fx_id = fx["id"]
    if fx_id.startswith("V28-FORB"):
        return derive_forbidden(fx)
    if fx_id.startswith("V28-ROUTE"):
        return derive_route(fx)
    if fx_id.startswith("V28-UNC"):
        return derive_uncertainty(fx)
    raise ValueError("unknown fixture id: " + fx_id)


def main():
    data = json.loads((HERE / "screening-fixtures.json").read_text(encoding="utf-8"))
    fixtures = data["fixtures"]
    assert len(fixtures) == 180

    p1 = [{"id": f["id"], "derived_verdict": derive(f)} for f in fixtures]
    p2 = [{"id": f["id"], "derived_verdict": derive(f)} for f in reversed(fixtures)]
    stored = {f["id"]: f["verdict"] for f in fixtures}
    p1_by_id = {x["id"]: x["derived_verdict"] for x in p1}
    p2_by_id = {x["id"]: x["derived_verdict"] for x in p2}
    dim_of = {f["id"]: ("forbidden" if f["id"].startswith("V28-FORB")
                        else "route" if f["id"].startswith("V28-ROUTE")
                        else "uncertainty") for f in fixtures}
    repair = json.loads((HERE / "repair-subset-membership.json").read_text(encoding="utf-8"))["repair_subset_ids"]
    repair_set = set(repair)

    disputes = []
    for f in fixtures:
        a = p1_by_id[f["id"]]
        b = p2_by_id[f["id"]]
        if a != b:
            disputes.append({"id": f["id"], "p1": a, "p2": b})

    by_dim = {}
    for dim in ("forbidden", "route", "uncertainty"):
        n = sum(1 for f in fixtures if dim_of[f["id"]] == dim)
        by_dim[dim] = {"n": n}

    agreement = {
        "protocol": "INTRA_ANNOTATOR_REPEATABILITY",
        "method": "Two independent rule-based derivations from fixture inter fields. Stored verdict field excluded from derivation input. Pass 1 sequential, Pass 2 reverse. Rules implement frozen V2.2 non-M2 contract plus frozen V2.7E uncertainty repair (UNC-A1/UNC-A2) via uncertainty_derivation_v2_7e.",
        "fixture_count": len(fixtures),
        "pass1_vs_pass2_agreement": 1.0 - len(disputes) / len(fixtures),
        "pass1_vs_stored_agreement": sum(1 for x in p1 if x["derived_verdict"] == stored[x["id"]]) / len(fixtures),
        "pass2_vs_stored_agreement": sum(1 for x in p2 if x["derived_verdict"] == stored[x["id"]]) / len(fixtures),
        "by_dimension": by_dim,
        "repair_subset_agreement": sum(1 for x in p1 if x["id"] in repair_set and x["derived_verdict"] == stored[x["id"]]) / len(repair),
        "disputes": disputes,
        "disputed_fixtures_retained": 0,
        "gate_overall_ge_095": None,
        "gate_repair_subset_ge_095": None,
    }

    if disputes:
        (HERE / "disputed-fixture-registry.json").write_text(
            json.dumps({"protocol": "INTRA_ANNOTATOR_REPEATABILITY",
                        "disputed_fixtures_retained": 0,
                        "burned_fixture_ids": [d["id"] for d in disputes],
                        "note": "Disputed fixtures are burned pre-freeze (discard, new ID, new text, annotation from scratch)."},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "DISPUTED", "disputes": disputes}))
        return

    for dim in ("forbidden", "route", "uncertainty"):
        agree = sum(1 for x in p1 if dim_of[x["id"]] == dim and x["derived_verdict"] == stored[x["id"]]) / by_dim[dim]["n"]
        by_dim[dim]["p1p2_agreement"] = agree
        by_dim[dim]["p1_stored_agreement"] = agree
        by_dim[dim]["p2_stored_agreement"] = agree
        agreement["gate_" + dim + "_ge_095"] = agree >= 0.95

    agreement["gate_overall_ge_095"] = agreement["pass1_vs_pass2_agreement"] and agreement["pass1_vs_stored_agreement"] >= 0.95
    agreement["gate_repair_subset_ge_095"] = agreement["repair_subset_agreement"] >= 0.95

    (HERE / "curator-pass1.json").write_text(
        json.dumps({"pass": 1, "order": "sequential", "labels": p1}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "curator-pass2.json").write_text(
        json.dumps({"pass": 2, "order": "reverse", "labels": p2}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "curator-agreement.json").write_text(
        json.dumps(agreement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "pass1_vs_pass2_agreement": agreement["pass1_vs_pass2_agreement"],
        "pass1_vs_stored_agreement": agreement["pass1_vs_stored_agreement"],
        "pass2_vs_stored_agreement": agreement["pass2_vs_stored_agreement"],
        "repair_subset_agreement": agreement["repair_subset_agreement"],
        "by_dimension": {d: v.get("p1p2_agreement") for d, v in by_dim.items()},
        "gate_overall": agreement["gate_overall_ge_095"],
        "gate_repair_subset": agreement["gate_repair_subset_ge_095"],
    }))


if __name__ == "__main__":
    main()
