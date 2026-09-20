"""Fresh workflow validation for V2.12 (campaign Stage 2C). Runs the 60 fresh
fixtures through the full lane, then re-runs deterministically and compares.
Includes fail-closed probes: no verdict without review, leakage rejection,
pending state persistence. No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_uncertainty_v2_12 import LaneError, UncertaintyReviewLane

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), encoding="utf-8") as f:
    FIX = json.load(f)["fixtures"]


def run_once():
    lane = UncertaintyReviewLane()
    out = {}
    for fx in FIX:
        fid = fx["fixture_id"]
        rec = lane.open_case(fx["case"])
        rv = dict(fx["review"])
        rv.update({
            "packet_id": rec["packet"]["packet_id"],
            "case_id": fid,
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-14T00:00:00Z",
        })
        lane.ingest_review(fid, rv)
        events = [p["event"] for p in rec["provenance"]]
        routed = any(p.get("event") == "ROUTED" and p.get("route") == "HUMAN_REVIEW_REQUIRED"
                     for p in rec["provenance"])
        packet_valid = rec["packet"]["packet_sha256"] == rec["provenance"][0]["packet_sha256"]
        ingested = any(e in ("REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED") for e in events)
        resolved = rec["status"] == "HUMAN_REVIEW_RESOLVED"
        final = (rec["final"] or {}).get("final_verdict")
        exp = fx["expect"]
        # Expected provenance: accepted single review path.
        prov_complete = events == ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]
        automated_before_review = rec["final"] is not None and not any(
            e in ("REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED", "ADJUDICATION_APPLIED") for e in events)
        out[fid] = {
            "routed": routed, "packet_valid": packet_valid, "ingested": ingested,
            "resolved": resolved, "verdict_ok": final == exp["verdict"],
            "prov_complete": prov_complete,
            "automated_before_review": automated_before_review,
            "verdict": final,
        }
    return lane, out


def failclosed_probes():
    """Pending state persists without review; leakage fields rejected; no
    final verdict exists for either."""
    lane = UncertaintyReviewLane()
    case = {"case_id": "PROBE-PENDING", "criterion": "c", "case_context": "x",
            "sut_output": "s"}
    lane.open_case(case)
    rec = lane.cases["PROBE-PENDING"]
    pending_ok = rec["status"] == "HUMAN_REVIEW_PENDING" and rec["final"] is None
    leak = {"case_id": "PROBE-LEAK", "criterion": "c", "case_context": "x",
            "sut_output": "s", "gold": "NOT_REQUIRED"}
    leak_rejected = False
    try:
        lane.open_case(leak)
    except LaneError:
        leak_rejected = True
    any_resolved = any(v["status"] == "HUMAN_REVIEW_RESOLVED" for v in lane.cases.values())
    return {"pending_fail_closed": pending_ok and not any_resolved,
            "leakage_rejected": leak_rejected}


def report_resolved(lane):
    return {k: v["status"] == "HUMAN_REVIEW_RESOLVED" for k, v in lane.cases.items()}




def main():
    lane1, first = run_once()
    lane2, second = run_once()
    deterministic = first == second
    probes = failclosed_probes()

    gates = {
   "correct_routing_60": all(r["routed"] for r in first.values()),
   "automated_verdicts_before_human_0": not any(r["automated_before_review"] for r in first.values()),
   "packet_validity_60": all(r["packet_valid"] for r in first.values()),
   "review_ingestion_60": all(r["ingested"] for r in first.values()),
   "deterministic_final_derivation_60": all(r["resolved"] and r["verdict_ok"] for r in first.values()),
   "provenance_completeness_60": all(r["prov_complete"] for r in first.values()),
   "deterministic_rerun_stable": deterministic,
   "pending_fail_closed": probes["pending_fail_closed"],
   "leakage_rejected": probes["leakage_rejected"],
    }
    fails = [fid for fid, r in first.items() if not all(
   r[k] for k in ("routed", "packet_valid", "ingested", "resolved", "verdict_ok", "prov_complete"))]
    summary = {
   "artifact": "fresh-workflow-results-v2-12",
   "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
   "n_fixtures": len(first), "gates": gates,
   "fresh_workflow_gate_pass": all(gates.values()),
   "gate_names_passing": sorted(k for k, v in gates.items() if v),
   "gate_names_failing": sorted(k for k, v in gates.items() if not v),
   "failing_fixtures": fails,
   "fail_closed_probes": probes,
   "results": first,
    }
    with open(os.path.join(DIR, "fresh-workflow-results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("fresh workflow:", "PASS" if summary["fresh_workflow_gate_pass"] else "FAIL",
          "| failing:", fails, "| failing gates:", summary["gate_names_failing"])
    return 0 if summary["fresh_workflow_gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
