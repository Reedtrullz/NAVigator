"""V2.6 workflow test runner (spec section 22-23). One-shot against frozen fixtures. No model calls.

Fixtures carry reviewer content (reviewer_id + judgment); the harness adds the
transport envelope required by human-review-result.schema.json. Existing keys are
never overwritten, so deliberately malformed fixtures remain malformed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_v2_6 import ReviewLane, LaneError, report_buckets

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "workflow-test-fixtures.json"), encoding="utf-8") as f:
    FIX = json.load(f)["fixtures"]

results = []
lane = ReviewLane()
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
        check("routed_human_review_required", any(p.get("event") == "ROUTED" and p.get("route") == "HUMAN_REVIEW_REQUIRED" for p in rec["provenance"]))
        if expect.get("packet_has_source_spans"):
            check("packet_has_source_spans", len(rec["packet"]["source_evidence_spans"]) > 0)
        envelope_defaults = {
            "packet_id": rec["packet"]["packet_id"],
            "case_id": fx["case"]["case_id"],
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-13T00:00:00Z",
        }
        for rv in fx.get("reviews", []):
            if isinstance(rv, dict):
                rv = dict(rv)
                for key, val in envelope_defaults.items():
                    rv.setdefault(key, val)
            lane.ingest_review(fx["case"]["case_id"], rv)
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
        if "final_label" in expect:
            check("final_label", rec["final"] and rec["final"]["final_label"] == expect["final_label"])
        if "derived_state" in expect:
            check("derived_state", rec["final"] and rec["final"]["derived_state"] == expect["derived_state"])
        if expect.get("duplicate_rejected"):
            check("duplicate_rejected", len(rec["duplicate_reviews"]) > 0)
        if expect.get("final_is_none"):
            check("final_is_none", rec["final"] is None)
        if expect.get("bucket"):
            check("bucket", report_buckets(lane)[expect["bucket"]] > 0)
        if "provenance_events" in expect:
            check("provenance_events", [p["event"] for p in rec["provenance"]] == expect["provenance_events"])
        if "provenance_contract_version" in expect:
            check("provenance_contract_version", any(p.get("contract_version") == expect["provenance_contract_version"] for p in rec["provenance"]))
        if expect.get("provenance_has_packet_sha"):
            check("provenance_has_packet_sha", any("packet_sha256" in p for p in rec["provenance"]))
        if "expect_after_adjudication" in fx:
            ea = fx["expect_after_adjudication"]
            check("post_adjudication_status", rec["status"] == ea["status"])
            if "review_mode" in ea:
                check("post_adjudication_mode", rec["review_mode"] == ea["review_mode"])
            if "final_label" in ea:
                check("post_adjudication_label", rec["final"] and rec["final"]["final_label"] == ea["final_label"])
    results.append({"fixture_id": fid, "category": fx["category"], "checks": checks, "errors": errs, "pass": not errs})

n_pass = sum(1 for r in results if r["pass"])
summary = {"artifact": "workflow-test-results-v2-6",
           "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
           "gate": "40/40",
           "n_fixtures": len(results),
           "n_pass": n_pass,
           "n_fail": len(results) - n_pass,
           "workflow_gate_pass": n_pass == len(results),
           "automated_m2_verdicts_before_review": 0,
           "results": results}
with open(os.path.join(DIR, "workflow-test-results.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print("workflow tests:", n_pass, "/", len(results))
for r in results:
    if not r["pass"]:
        print("FAIL", r["fixture_id"], r["errors"])
