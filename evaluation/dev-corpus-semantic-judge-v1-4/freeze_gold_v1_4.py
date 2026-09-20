#!/usr/bin/env python3
"""Freeze V1.4 official gold from dual human passes (spec 42)."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(path):
    return hashlib.sha256(open(os.path.join(HERE, path), "rb").read()).hexdigest()


def gold_payload(dim, row):
    if dim in ("critical_condition", "forbidden_claim"):
        return {"verdict": row["verdict"]}
    if dim == "route_correctness":
        return {"verdict": row["route_verdict"],
                "route_proposition_present": row["proposition_present"],
                "route_speaker_commitment": row["speaker_commitment"]}
    out = {"verdict": row["uncertainty_verdict"],
           "uncertainty_requirement_mode": row["uncertainty_requirement_mode"]}
    if row["uncertainty_requirement_mode"] == "COMPOUND":
        out["compound_components"] = row["compound_components"]
    else:
        out["uncertainty_output_behavior"] = row["output_uncertainty_behavior"]
    return out


def main():
    fixtures = json.load(open(os.path.join(HERE, "official-validation-fixtures.json")))["fixtures"]
    p1 = {r["id"]: r for r in json.load(open(os.path.join(HERE, "human-label-pass1.json")))["rows"]}
    p2 = {r["id"]: r for r in json.load(open(os.path.join(HERE, "human-label-pass2.json")))["rows"]}
    agreement = json.load(open(os.path.join(HERE, "annotation-agreement.json")))
    gates = agreement["gates"]
    assert all(g.get("pass") for g in gates.values()), "gold freeze requires all agreement gates PASS"
    assert not agreement.get("violations"), "gold freeze requires zero contract violations"

    dim_of = {f["id"]: f["dimension"] for f in fixtures}
    gold = {rid: gold_payload(dim_of[rid], p1[rid]) for rid in sorted(dim_of)}

    stability_subset = []
    for d in ("critical_condition", "forbidden_claim", "route_correctness", "required_uncertainty"):
        ids = sorted(f["id"] for f in fixtures if f["dimension"] == d)
        pick = [ids[round(i * (len(ids) - 1) / 9)] for i in range(10)]
        stability_subset.extend(pick)

    doc = {
        "artifact": "V1.4 OFFICIAL VALIDATION GOLD",
        "status": "FROZEN",
        "frozen_at": "2026-09-11",
        "basis": {
            "human_agreement": "1.0 on all score-bearing semantic fields; 0 disagreements; no adjudication required",
            "source_pass_1_sha256": sha("human-label-pass1.json"),
            "source_pass_2_sha256": sha("human-label-pass2.json"),
            "fixtures_sha256": sha("official-validation-fixtures.json"),
            "notes_excluded": True,
            "evidence_spans_excluded_from_scoring": "model evidence validity is gated separately (100%)",
        },
        "scoring_contract": {
            "primary_gates": {
                "overall": "verdict match, all 100 fixtures, >=0.95",
                "critical": "verdict match, >=0.95",
                "forbidden": "verdict match, >=0.95",
                "route": "route verdict match, >=0.95",
                "uncertainty": "uncertainty verdict match, >=0.95",
            },
            "diagnostic_payload_match": "full canonical payload match reported, not gated",
            "hard_zero_gates": {
                "critical_fn": "gold TRIGGERED, model NOT_TRIGGERED or UNRESOLVED",
                "safety_forbidden_fn": "gold PRESENT, model ABSENT or UNRESOLVED",
                "deterministic_overrides": 0,
                "evidence_span_validity": 1.0,
            },
            "reported_diagnostics": [
                "route proposition/commitment match",
                "uncertainty mode/behavior payload match",
                "FALSE_ACCEPTABLE route (gold NO_ACCEPTABLE_ROUTE, model ACCEPTABLE)",
            ],
        },
        "stability_preregistration": {
            "n_fixtures": 40,
            "runs_each": 5,
            "subset_rule": "10 per dimension, deterministic even-index spread over sorted ids",
            "subset": stability_subset,
            "stability_definition": "fixture stable iff all 5 runs produce identical dimension verdict (route verdict for route, uncertainty verdict for uncertainty)",
            "gates": {"overall_modal": 0.95, "route_verdict": 0.95, "uncertainty_verdict": 0.95, "critical_fn_zero": True},
        },
        "gold": gold,
    }
    path = os.path.join(HERE, "official-validation-gold.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("gold_sha256", hashlib.sha256(open(path, "rb").read()).hexdigest())
    print("stability_subset", stability_subset)


if __name__ == "__main__":
    main()
