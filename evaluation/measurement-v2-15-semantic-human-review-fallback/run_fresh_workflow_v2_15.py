"""Fresh workflow validation for V2.15 (campaign Stage 2F). Runs the 120 fresh
fixtures through the full lane, re-runs deterministically and compares, then
executes 8 fail-closed probes. No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_semantic_v2_15 import LaneError, SemanticReviewLane  # noqa: E402

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), encoding="utf-8") as f:
    DATA = json.load(f)
FIX, PROBES = DATA["fixtures"], DATA["probes"]


def run_once():
    lane = SemanticReviewLane()
    out = {}
    for fx in FIX:
        fid = fx["fixture_id"]
        rec = lane.open_case(fx["case"])
        rv = {
            "packet_id": rec["packet"]["packet_id"],
            "case_id": fid,
            "reviewer_id": "H1",
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-14T00:00:00Z",
            "judgment": fx["judgment"],
        }
        lane.ingest_review(fid, rv)
        events = [p["event"] for p in rec["provenance"]]
        routed = any(p.get("event") == "ROUTED" and p.get("route") == "HUMAN_REVIEW_REQUIRED"
                     for p in rec["provenance"])
        packet_valid = rec["packet"]["packet_sha256"] == rec["provenance"][0]["packet_sha256"]
        ingested = any(e in ("REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED") for e in events)
        resolved = rec["status"] == "HUMAN_REVIEW_RESOLVED"
        final = (rec["final"] or {}).get("final_verdict")
        exp = fx["expect"]
        prov_complete = events == ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]
        automated_before_review = rec["final"] is not None and not any(
            e in ("REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED", "ADJUDICATION_APPLIED") for e in events)
        out[fid] = {
            "dimension": fx["case"]["dimension"],
            "routed": routed, "packet_valid": packet_valid, "ingested": ingested,
            "resolved": resolved, "verdict_ok": final == exp["verdict"],
            "prov_complete": prov_complete,
            "automated_before_review": automated_before_review,
            "verdict": final,
        }
    return lane, out


def run_probes():
    results = {}
    for probe in PROBES:
        kind = probe["kind"]
        lane = SemanticReviewLane()
        ok = False
        detail = None
        if kind in ("leakage_rejected", "dimension_rejected"):
            try:
                lane.open_case(probe["case"])
            except LaneError as exc:
                ok = True
                detail = str(exc)
        elif kind in ("pending_fail_closed", "span_not_verbatim_rejected",
                      "not_derivable_rejected"):
            lane.open_case(probe["case"])
            rec = lane.cases[probe["case"]["case_id"]]
            if kind == "pending_fail_closed":
                ok = rec["status"] == "HUMAN_REVIEW_PENDING" and rec["final"] is None
            else:
                rv = {
                    "packet_id": rec["packet"]["packet_id"],
                    "case_id": probe["case"]["case_id"],
                    "reviewer_id": "H1",
                    "contract_version": rec["packet"]["contract_version"],
                    "reviewed_utc": "2026-09-14T00:00:00Z",
                    "judgment": probe["judgment"],
                }
                lane.ingest_review(probe["case"]["case_id"], rv)
                ok = rec["status"] == "HUMAN_REVIEW_INVALID" and rec["final"] is None
                detail = rec["status"]
        results[probe["probe_id"]] = {"kind": kind, "pass": bool(ok), "detail": detail}
    return results


def main():
    lane1, first = run_once()
    lane2, second = run_once()
    deterministic = first == second
    probes = run_probes()

    gates = {
        "correct_routing_120": all(r["routed"] for r in first.values()),
        "automated_verdicts_before_human_0": not any(r["automated_before_review"] for r in first.values()),
        "packet_validity_120": all(r["packet_valid"] for r in first.values()),
        "review_ingestion_120": all(r["ingested"] for r in first.values()),
        "deterministic_final_derivation_120": all(r["resolved"] and r["verdict_ok"] for r in first.values()),
        "provenance_completeness_120": all(r["prov_complete"] for r in first.values()),
        "deterministic_rerun_stable": deterministic,
        "fail_closed_probes_8_pass": all(p["pass"] for p in probes.values()),
    }
    fails = [fid for fid, r in first.items() if not all(
        r[k] for k in ("routed", "packet_valid", "ingested", "resolved", "verdict_ok", "prov_complete"))]
    by_dim = {}
    for fid, r in first.items():
        d = r["dimension"]
        by_dim.setdefault(d, {"n": 0, "verdict_ok": 0})
        by_dim[d]["n"] += 1
        by_dim[d]["verdict_ok"] += 1 if r["verdict_ok"] else 0
    summary = {
        "artifact": "fresh-workflow-results-v2-15",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V2_15-SEMANTIC-HUMAN-REVIEW-FALLBACK",
        "n_fixtures": len(first),
        "n_probes": len(probes),
        "gates": gates,
        "fresh_workflow_gate_pass": all(gates.values()),
        "gate_names_failing": sorted(k for k, v in gates.items() if not v),
        "failing_fixtures": fails,
        "fail_closed_probes": probes,
        "per_dimension": by_dim,
        "results": first,
    }
    with open(os.path.join(DIR, "fresh-workflow-results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("fresh workflow:", "PASS" if summary["fresh_workflow_gate_pass"] else "FAIL",
          "| failing fixtures:", len(fails), "| failing gates:", summary["gate_names_failing"])
    for d, v in sorted(by_dim.items()):
        print(f"  {d}: {v['verdict_ok']}/{v['n']} verdicts correct")
    return 0 if summary["fresh_workflow_gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
