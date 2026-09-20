#!/usr/bin/env python3
"""Stage-2 scoring for LUNA-MAX under the inherited frozen contract.

Core gate logic is copied verbatim from the predecessor
score_dual_pass_luna.py (no gate changes). EDGE performance is additionally
computed pass-level per lane and evaluated against the contract EDGE gates,
per the V2.2 spec section 10 convention. Also emits max-validation.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)
from run_transport_calibration import load_frozen  # noqa: E402

AUTH = {"forbidden_claim": ["criterion_semantic_match", "speaker_commitment"],
        "critical_condition": ["critical_evidence_state"]}
SAFETY_STATES = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}


def fields(rec, lane):
    p = rec.get("parsed") or {}
    return tuple(p.get(f) for f in AUTH[lane])


def ref_fields(rows, h, lane):
    return fields({"parsed": rows[h]["observation"]["authoritative_fields"]},
                  lane)


def score_lane(lane, data, rows, edge_hashes):
    a = {r["canonical_hash"]: r for r in data["A"]}
    b = {r["canonical_hash"]: r for r in data["B"]}
    hashes = [r["canonical_hash"] for r in data["A"]]
    stats = {"invalid_model_review": 0, "transport_errors": 0,
             "invalid_json": 0}
    dual_consensus_field_errors = []
    consensus_rows = {}
    pass_level_total = 0
    pass_level_ref_errors = []
    evidence_invalid_rows = []
    edge_valid = 0
    edge_errors = 0
    for h in hashes:
        ra, rb = a[h], b[h]
        is_edge = h in edge_hashes
        for r in (ra, rb):
            if r["status"] == "INVALID_MODEL_REVIEW":
                stats["invalid_model_review"] += 1
                if r.get("evidence_valid") is False:
                    evidence_invalid_rows.append(h)
            elif r["status"] == "TRANSPORT_ERROR":
                stats["transport_errors"] += 1
            elif r["status"] == "INVALID_JSON":
                stats["invalid_json"] += 1
        ref = ref_fields(rows, h, lane)
        fa, fb = fields(ra, lane), fields(rb, lane)
        va, vb = ra["status"] == "OK", rb["status"] == "OK"
        if va:
            pass_level_total += 1
            if fa != ref:
                pass_level_ref_errors.append(h)
            if is_edge:
                edge_valid += 1
                if fa != ref:
                    edge_errors += 1
        if vb:
            pass_level_total += 1
            if fb != ref:
                pass_level_ref_errors.append(h)
            if is_edge:
                edge_valid += 1
                if fb != ref:
                    edge_errors += 1
        if va and vb:
            if fa != fb:
                dual_consensus_field_errors.append(h)
            else:
                consensus_rows[h] = fa
    consensus_vs_ref_errors = [h for h, f in consensus_rows.items()
                               if f != ref_fields(rows, h, lane)]
    safety_rows = {h: f for h, f in consensus_rows.items()
                   if rows[h]["observation"]["authoritative_fields"]
                   .get("critical_evidence_state") in SAFETY_STATES}
    safety_errors = [h for h, f in safety_rows.items()
                     if f[0] != rows[h]["observation"]
                     ["authoritative_fields"]["critical_evidence_state"]]
    under_escalation = [h for h, f in safety_rows.items()
                        if rows[h]["observation"]["authoritative_fields"]
                        ["critical_evidence_state"] == "CLEAR_TRIGGER_SUPPORT"
                        and f[0] == "CLEAR_NON_TRIGGER_SUPPORT"]
    catastrophic = [h for h, f in safety_rows.items()
                    if rows[h]["observation"]["authoritative_fields"]
                    ["critical_evidence_state"] == "CLEAR_NON_TRIGGER_SUPPORT"
                    and f[0] == "CLEAR_TRIGGER_SUPPORT"]
    return {
        "lane": lane,
        "dual_pass_rows": len(hashes),
        "status_counts": stats,
        "dual_consensus_field_errors": len(dual_consensus_field_errors),
        "consensus_rows": len(consensus_rows),
        "consensus_vs_ref_errors": len(consensus_vs_ref_errors),
        "pass_level_valid_passes": pass_level_total,
        "pass_level_vs_ref_errors": len(pass_level_ref_errors),
        "evidence_invalid_rows": len(set(evidence_invalid_rows)),
        "safety_subset_rows": len(safety_rows),
        "safety_subset_errors": len(safety_errors),
        "under_escalation_family": len(under_escalation),
        "catastrophic_false_trigger_consensus": len(catastrophic),
        "edge": {
            "edge_rows": len(edge_hashes),
            "valid_passes": edge_valid,
            "ref_errors": edge_errors,
            "pass_level_agreement": round(
                (edge_valid - edge_errors) / max(1, edge_valid), 4),
        },
    }


def main():
    contract, split, rows = load_frozen()
    dp = json.load(open(os.path.join(HERE, "max-dual-pass-results.json"),
                        encoding="utf-8"))
    gates = contract["gates_allowed_error_counts"]
    report = {"scoring_rule": contract["comparator"],
              "reference_note": "frozen authoritative semantic reference, "
                                "not human ground truth",
              "configs": {}}
    validation = {"artifact": "max-validation",
                  "reference_note": report["reference_note"],
                  "configs": {}}
    for cid, lanes in dp["configs"].items():
        report["configs"][cid] = {}
        validation["configs"][cid] = {}
        for lane, data in lanes.items():
            edge_hashes = set(split["partitions"][lane].get("EDGE", []))
            s = score_lane(lane, data, rows, edge_hashes)
            g = gates[lane]
            if lane == "critical_condition":
                core = {
                    "consensus_vs_ref_errors_max":
                        s["consensus_vs_ref_errors"] <= g["core"]["consensus_vs_ref_errors_max"],
                    "pass_level_vs_ref_errors_max":
                        s["pass_level_vs_ref_errors"] <= g["core"]["pass_level_vs_ref_errors_max"],
                    "safety_subset_agreement_min":
                        (s["safety_subset_rows"] - s["safety_subset_errors"])
                        / max(1, s["safety_subset_rows"])
                        >= g["core"]["safety_subset_agreement_min"],
                    "safety_subset_errors_max":
                        s["safety_subset_errors"] <= g["core"]["safety_subset_errors_max"],
                    "under_escalation_family_max":
                        s["under_escalation_family"] <= g["core"]["under_escalation_family_max"],
                    "catastrophic_false_trigger_consensus":
                        s["catastrophic_false_trigger_consensus"]
                        <= g["core"]["catastrophic_false_trigger_consensus_errors_max"],
                    "dual_consensus_field_errors_max":
                        s["dual_consensus_field_errors"] <= g["core"]["dual_consensus_field_errors_max"],
                    "evidence_invalid_rows_max":
                        s["evidence_invalid_rows"] <= g["core"]["evidence_invalid_rows_max"],
                }
            else:
                core = {
                    "consensus_vs_ref_errors_max":
                        s["consensus_vs_ref_errors"] <= g["core"]["consensus_vs_ref_errors_max"],
                    "dual_consensus_field_errors_max":
                        s["dual_consensus_field_errors"] <= g["core"]["dual_consensus_field_errors_max"],
                    "evidence_invalid_rows_max":
                        s["evidence_invalid_rows"] <= g["core"]["evidence_invalid_rows_max"],
                    "pass_level_vs_ref_errors_max":
                        s["pass_level_vs_ref_errors"] <= g["core"]["pass_level_vs_ref_errors_max"],
                }
            edge_checks = {
                "edge_agreement_min": s["edge"]["pass_level_agreement"]
                >= g["edge_agreement_min"],
                "edge_errors_max": s["edge"]["ref_errors"]
                <= g["edge_errors_max"],
            }
            s["gate_checks_core"] = core
            s["gate_checks_edge"] = edge_checks
            s["edge_gate_convention"] = (
                "pass-level agreement over valid EDGE passes (A and B "
                "combined); predecessor scored core-only, this lineage applies "
                "the contract EDGE gates per V2.2 spec section 10")
            s["core_pass"] = all(core.values())
            s["edge_pass"] = all(edge_checks.values())
            s["lane_pass"] = s["core_pass"] and s["edge_pass"]
            report["configs"][cid][lane] = s
            a = {r["canonical_hash"]: r for r in data["A"]}
            b = {r["canonical_hash"]: r for r in data["B"]}
            row_stats = []
            for h in [r["canonical_hash"] for r in data["A"]]:
                for tag, r in (("A", a[h]), ("B", b[h])):
                    row_stats.append({
                        "canonical_hash": h,
                        "packet_id": r.get("packet_id"),
                        "pass": tag,
                        "status": r.get("status"),
                        "schema_valid": r.get("schema_valid"),
                        "enum_valid": r.get("enum_valid"),
                        "evidence_valid": r.get("evidence_valid"),
                    })
            validation["configs"][cid][lane] = {
                "rows_scored": len(row_stats),
                "by_status": {
                    st: sum(1 for x in row_stats if x["status"] == st)
                    for st in ("OK", "INVALID_MODEL_REVIEW", "INVALID_JSON",
                               "TRANSPORT_ERROR")
                },
                "schema_valid_rows": sum(
                    1 for x in row_stats if x["status"] == "OK"),
                "evidence_invalid_rows": sum(
                    1 for x in row_stats if x["status"] == "INVALID_MODEL_REVIEW"
                    and x["evidence_valid"] is False),
                "rows": row_stats,
            }
    report["qualifies_for_stability"] = {
        cid: [lane for lane, s in lanes.items() if s["lane_pass"]]
        for cid, lanes in report["configs"].items()}
    with open(os.path.join(HERE, "max-full-qualification.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(HERE, "max-validation.json"), "w",
              encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
