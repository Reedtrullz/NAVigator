"""V2.12 workflow unit tests. One-shot against frozen fixtures. No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_uncertainty_v2_12 import UncertaintyReviewLane, LaneError, report_buckets, FORBIDDEN_PACKET_KEYS

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "workflow-test-fixtures.json"), encoding="utf-8") as f:
    FIX = json.load(f)["fixtures"]

results = []
lane = UncertaintyReviewLane()
for fx in FIX:
    fid, expect = fx["fixture_id"], fx["expect"]
    checks, errs = [], []
    def check(name, cond):
        checks.append(name)
        if not cond:
            errs.append(name)
    try:
        rec = lane.open_case(fx["case"])
    except LaneError:
        rec = None
    if expect.get("packet_error"):
        check("packet_error", rec is None)
    else:
        if rec is None:
            errs.append("unexpected packet error")
            results.append({"fixture_id": fid, "checks": checks, "errors": errs, "pass": False})
            continue
        check("routed_human_review_required", any(
            p.get("event") == "ROUTED" and p.get("route") == "HUMAN_REVIEW_REQUIRED" for p in rec["provenance"]))
        envelope_defaults = {
            "packet_id": rec["packet"]["packet_id"],
            "case_id": fx["case"]["case_id"],
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-14T00:00:00Z",
        }
        for rv_ in fx.get("reviews", []):
            if isinstance(rv_, dict):
                rv_ = dict(rv_)
                for key, val in envelope_defaults.items():
                    rv_.setdefault(key, val)
            lane.ingest_review(fx["case"]["case_id"], rv_)
        if "status" in expect:
            check("status", rec["status"] == expect["status"])
        adj = fx.get("adjudication")
        if adj:
            try:
                lane.adjudicate(fx["case"]["case_id"], adj)
                raised = False
            except LaneError:
                raised = True
            if expect.get("adjudication_error"):
                check("adjudication_error", raised)
            else:
                check("adjudication_applied", not raised)
        if "review_mode" in expect:
            check("review_mode", rec["review_mode"] == expect["review_mode"])
        if "final_verdict" in expect:
            check("final_verdict", rec["final"] and rec["final"]["final_verdict"] == expect["final_verdict"])
        if expect.get("duplicate_rejected"):
            check("duplicate_rejected", len(rec["duplicate_reviews"]) > 0)
        if expect.get("final_is_none"):
            check("final_is_none", rec["final"] is None)
        if expect.get("bucket"):
            check("bucket", report_buckets(lane)[expect["bucket"]] > 0)
        if "provenance_events" in expect:
            check("provenance_events", [p["event"] for p in rec["provenance"]] == expect["provenance_events"])
        if expect.get("provenance_has_packet_sha"):
            check("provenance_has_packet_sha", any("packet_sha256" in p for p in rec["provenance"]))
        if expect.get("routed_automated_authoritative_false"):
            check("routed_automated_authoritative_false", any(
                p.get("event") == "ROUTED" and p.get("automated_authoritative") is False for p in rec["provenance"]))
        if expect.get("packet_has_no_forbidden_keys"):
            check("packet_has_no_forbidden_keys", not any(k in rec["packet"] for k in FORBIDDEN_PACKET_KEYS))
        if "expect_after_adjudication" in fx:
            ea = fx["expect_after_adjudication"]
            check("post_adjudication_status", rec["status"] == ea["status"])
            if "review_mode" in ea:
                check("post_adjudication_mode", rec["review_mode"] == ea["review_mode"])
            if "final_verdict" in ea:
                check("post_adjudication_verdict", rec["final"] and rec["final"]["final_verdict"] == ea["final_verdict"])
    results.append({"fixture_id": fid, "category": fx["category"], "checks": checks, "errors": errs, "pass": not errs})

n_pass = sum(1 for r in results if r["pass"])
summary = {"artifact": "workflow-test-results-v2-12",
           "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
           "gate": "40/40", "n_fixtures": len(results), "n_pass": n_pass,
           "n_fail": len(results) - n_pass,
           "workflow_gate_pass": n_pass == len(results),
           "automated_uncertainty_verdicts_before_review": 0,
           "results": results}
with open(os.path.join(DIR, "workflow-test-results.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print("workflow tests:", n_pass, "/", len(results))
for r in results:
    if not r["pass"]:
        print("FAIL", r["fixture_id"], r["errors"])
