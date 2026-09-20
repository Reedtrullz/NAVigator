"""Fresh workflow validation (spec sections 26-27). Runs the 60 fresh fixtures
through the full lane, then re-runs deterministically and compares. No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_v2_6 import ReviewLane

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), encoding="utf-8") as f:
    FIX = json.load(f)["fixtures"]


def run_once():
    lane = ReviewLane()
    out = {}
    for fx in FIX:
        fid = fx["fixture_id"]
        rec = lane.open_case(fx["case"])
        rv = dict(fx["review"])
        rv.update({
            "packet_id": rec["packet"]["packet_id"],
            "case_id": fid,
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-13T00:00:00Z",
        })
        lane.ingest_review(fid, rv)
        events = [p["event"] for p in rec["provenance"]]
        routed = any(p.get("event") == "ROUTED" and p.get("route") == "HUMAN_REVIEW_REQUIRED"
                     for p in rec["provenance"])
        packet_valid = rec["packet"]["packet_sha256"] == rec["provenance"][0]["packet_sha256"]
        ingested = "REVIEW_ACCEPTED" in events
        resolved = rec["status"] == "HUMAN_REVIEW_RESOLVED"
        derived = (rec["final"] or {}).get("derived_state")
        final = (rec["final"] or {}).get("final_label")
        exp = fx["expect"]
        prov_complete = events == ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]
        # Automated authoritative M2 verdict before human review = a final
        # derivation exists without any accepted human review event.
        has_accepted_review = any(
            p.get("event") in ("REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED", "ADJUDICATION_APPLIED")
            for p in rec["provenance"])
        automated_before_review = rec["final"] is not None and not has_accepted_review
        # Critical safety: TRIGGERED only when the human found trigger support.
        safety_ok = not (final == "TRIGGERED" and rv["judgment"]["trigger_support"] != "PRESENT")
        out[fid] = {
            "routed": routed, "packet_valid": packet_valid, "ingested": ingested,
            "resolved": resolved, "derived_ok": derived == exp["derived_state"],
            "final_ok": final == exp["final_label"], "prov_complete": prov_complete,
            "automated_before_review": automated_before_review, "safety_ok": safety_ok,
            "derived_state": derived, "final_label": final,
        }
    return out


first = run_once()
second = run_once()
deterministic = first == second

gates = {
    "correct_routing_60": all(r["routed"] for r in first.values()),
    "automated_m2_verdicts_before_human_0": not any(r["automated_before_review"] for r in first.values()),
    "packet_validity_60": all(r["packet_valid"] for r in first.values()),
    "review_ingestion_60": all(r["ingested"] for r in first.values()),
    "deterministic_final_derivation_60": all(r["resolved"] and r["derived_ok"] and r["final_ok"] for r in first.values()),
    "provenance_completeness_60": all(r["prov_complete"] for r in first.values()),
    "critical_safety_mismatch_0": all(r["safety_ok"] for r in first.values()),
    "deterministic_rerun_stable": deterministic,
}
fails = [fid for fid, r in first.items() if not all(
    r[k] for k in ("routed", "packet_valid", "ingested", "resolved", "derived_ok",
                   "final_ok", "prov_complete", "safety_ok"))]
summary = {
    "artifact": "fresh-workflow-results-v2-6",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
    "n_fixtures": len(first), "gates": gates,
    "fresh_workflow_gate_pass": all(gates.values()),
    "gate_names_passing": sorted(k for k, v in gates.items() if v),
    "gate_names_failing": sorted(k for k, v in gates.items() if not v),
    "failing_fixtures": fails,
    "results": first,
}
with open(os.path.join(DIR, "fresh-workflow-results.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print("fresh workflow:", "PASS" if summary["fresh_workflow_gate_pass"] else "FAIL",
      "| failing:", fails, "| failing gates:", summary["gate_names_failing"])
