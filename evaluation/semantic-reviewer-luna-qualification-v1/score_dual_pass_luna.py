#!/usr/bin/env python3
"""Stage 2 scoring: frozen V1 contract comparators applied to LUNA-HIGH.

accepted_consensus = both passes valid AND authoritative fields equal.
Reference = frozen authoritative semantic reference, not human ground truth.
No gate values are changed by this script.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
import sys  # noqa: E402
sys.path.insert(0, V1)
from run_transport_calibration import load_frozen  # noqa: E402

OUT = os.path.join(HERE, "dual-pass-scorecard.json")
AUTH = {"forbidden_claim": ["criterion_semantic_match", "speaker_commitment"],
        "critical_condition": ["critical_evidence_state"]}
SAFETY_STATES = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}


def fields(rec, lane):
    p = rec.get("parsed") or {}
    return tuple(p.get(f) for f in AUTH[lane])


def score_lane(lane, data, rows):
    a = {r["canonical_hash"]: r for r in data["A"]}
    b = {r["canonical_hash"]: r for r in data["B"]}
    hashes = [r["canonical_hash"] for r in data["A"]]
    core_hashes = set(hashes)
    counts = {"dual_pass_rows": len(hashes)}
    stats = {"invalid_model_review": 0, "transport_errors": 0,
             "invalid_json": 0}
    dual_consensus_field_errors = []
    consensus_rows = {}
    pass_level_total = 0
    pass_level_ref_errors = []
    evidence_invalid_rows = []
    for chash in hashes:
        ra, rb = a[chash], b[chash]
        for r in (ra, rb):
            if r["status"] == "INVALID_MODEL_REVIEW":
                stats["invalid_model_review"] += 1
                if r.get("evidence_valid") is False:
                    evidence_invalid_rows.append(chash)
            elif r["status"] == "TRANSPORT_ERROR":
                stats["transport_errors"] += 1
            elif r["status"] == "INVALID_JSON":
                stats["invalid_json"] += 1
        ref = fields({"parsed": rows[chash]["observation"]
                      ["authoritative_fields"]}, lane)
        fa, fb = fields(ra, lane), fields(rb, lane)
        va = ra["status"] == "OK"
        vb = rb["status"] == "OK"
        if va:
            pass_level_total += 1
            if fa != ref:
                pass_level_ref_errors.append(chash)
        if vb:
            pass_level_total += 1
            if fb != ref:
                pass_level_ref_errors.append(chash)
        if va and vb:
            if fa != fb:
                dual_consensus_field_errors.append(chash)
            else:
                consensus_rows[chash] = fa
    consensus_vs_ref_errors = []
    for h, f in consensus_rows.items():
        ref = fields({"parsed": rows[h]["observation"]
                      ["authoritative_fields"]}, lane)
        if f != ref:
            consensus_vs_ref_errors.append(h)
    # safety subset (critical lane only)
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
    catastrophic_false_trigger = [h for h, f in safety_rows.items()
                                  if rows[h]["observation"]
                                  ["authoritative_fields"]
                                  ["critical_evidence_state"]
                                  == "CLEAR_NON_TRIGGER_SUPPORT"
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
        "catastrophic_false_trigger_consensus": len(catastrophic_false_trigger),
    }


def main():
    contract, split, rows = load_frozen()
    dp = json.load(open(os.path.join(HERE, "dual-pass-results.json"),
                        encoding="utf-8"))
    gates = contract["gates_allowed_error_counts"]
    report = {"scoring_rule": contract["comparator"],
              "reference_note": "frozen authoritative semantic reference, "
                                "not human ground truth",
              "configs": {}}
    for cid, lanes in dp["configs"].items():
        report["configs"][cid] = {}
        for lane, data in lanes.items():
            s = score_lane(lane, data, rows)
            g = gates[lane]["core"]
            if lane == "critical_condition":
                checks = {
                    "consensus_vs_ref_errors_max":
                        s["consensus_vs_ref_errors"] <= g["consensus_vs_ref_errors_max"],
                    "pass_level_vs_ref_errors_max":
                        s["pass_level_vs_ref_errors"] <= g["pass_level_vs_ref_errors_max"],
                    "safety_subset_agreement_min":
                        (s["safety_subset_rows"] - s["safety_subset_errors"])
                        / max(1, s["safety_subset_rows"])
                        >= g["safety_subset_agreement_min"],
                    "safety_subset_errors_max":
                        s["safety_subset_errors"] <= g["safety_subset_errors_max"],
                    "under_escalation_family_max":
                        s["under_escalation_family"] <= g["under_escalation_family_max"],
                    "catastrophic_false_trigger_consensus":
                        s["catastrophic_false_trigger_consensus"]
                        <= g["catastrophic_false_trigger_consensus_errors_max"],
                    "dual_consensus_field_errors_max":
                        s["dual_consensus_field_errors"] <= g["dual_consensus_field_errors_max"],
                    "evidence_invalid_rows_max":
                        s["evidence_invalid_rows"] <= g["evidence_invalid_rows_max"],
                }
            else:
                checks = {
                    "consensus_vs_ref_errors_max":
                        s["consensus_vs_ref_errors"] <= g["consensus_vs_ref_errors_max"],
                    "dual_consensus_field_errors_max":
                        s["dual_consensus_field_errors"] <= g["dual_consensus_field_errors_max"],
                    "evidence_invalid_rows_max":
                        s["evidence_invalid_rows"] <= g["evidence_invalid_rows_max"],
                    "pass_level_vs_ref_errors_max":
                        s["pass_level_vs_ref_errors"] <= g["pass_level_vs_ref_errors_max"],
                }
            s["gate_checks"] = checks
            s["core_pass"] = all(checks.values())
            report["configs"][cid][lane] = s
    report["qualifies_for_stability"] = {
        cid: all(l["core_pass"] for l in lanes.values())
        for cid, lanes in report["configs"].items()}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
