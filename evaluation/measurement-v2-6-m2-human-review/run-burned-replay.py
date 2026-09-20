"""Burned V2.5 replay (spec section 24): push the 60 frozen V2.5 pass1 human
judgments through the V2.6 review lane and require exact derived-state agreement.
No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_v2_6 import ReviewLane

DIR = os.path.dirname(os.path.abspath(__file__))
V25 = os.path.join(DIR, "..", "judge-contract-v2-5-m2-decomposition")

with open(os.path.join(V25, "boundary-calibration-a-pass1.json"), encoding="utf-8") as f:
    PASS1 = json.load(f)["items"]
with open(os.path.join(V25, "m2-fixtures-v2-5.json"), encoding="utf-8") as f:
    FIX = {x["id"]: x for x in json.load(f)["fixtures"]}

results, mismatches = [], []
lane = ReviewLane()
for item in PASS1:
    fid = item["id"]
    fixture = FIX[fid]
    case = {
        "case_id": fid,
        "criterion": fixture["crit"],
        "case_context": fixture["ctx"],
        "sut_output": fixture["sut"],
    }
    rec = lane.open_case(case)
    review = {
        "packet_id": rec["packet"]["packet_id"],
        "case_id": fid,
        "reviewer_id": "V25_PASS1_REPLAY",
        "contract_version": rec["packet"]["contract_version"],
        "reviewed_utc": "2026-09-13T00:00:00Z",
        "judgment": item["judgment"],
    }
    lane.ingest_review(fid, review)
    got = (rec["final"] or {}).get("derived_state")
    ok = rec["status"] == "HUMAN_REVIEW_RESOLVED" and got == item["derived_state"]
    results.append({"id": fid, "expected": item["derived_state"], "got": got, "pass": ok})
    if not ok:
        mismatches.append(fid)

summary = {
    "artifact": "burned-v2-5-replay-v2-6",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN_REVIEW-LANE",
    "n_items": len(results),
    "n_pass": sum(1 for r in results if r["pass"]),
    "replay_gate_pass": not mismatches,
    "mismatches": mismatches,
    "results": results,
}
with open(os.path.join(DIR, "burned-v2-5-replay.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print("burned replay:", summary["n_pass"], "/", len(results), "| mismatches:", mismatches)
