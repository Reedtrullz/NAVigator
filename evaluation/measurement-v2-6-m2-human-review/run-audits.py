"""Leakage and provenance audits (spec sections 27 and deliverables). No model calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_lane_v2_6 import FORBIDDEN_CASE_KEYS, FORBIDDEN_PACKET_KEYS, ReviewLane

DIR = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


# --- Leakage audit: any leakage field reaching a constructed packet? ---
wf = load("workflow-test-fixtures.json")["fixtures"]
fw = load("fresh-workflow-fixtures.json")["fixtures"]
leak_hits = []

for fx in wf:
    lane = ReviewLane()
    try:
        rec = lane.open_case(fx["case"])
    except Exception:
        continue
    found = [k for k in FORBIDDEN_PACKET_KEYS if k in rec["packet"]]
    if found:
        leak_hits.append({"suite": "workflow-test", "fixture": fx["fixture_id"], "fields": found})

for fx in fw:
    lane = ReviewLane()
    rec = lane.open_case(fx["case"])
    found = [k for k in FORBIDDEN_PACKET_KEYS if k in rec["packet"]]
    if found:
        leak_hits.append({"suite": "fresh-workflow", "fixture": fx["fixture_id"], "fields": found})

# Runtime guard must reject every forbidden key.
guard_rejects_all = True
for key in FORBIDDEN_CASE_KEYS:
    lane = ReviewLane()
    case = {"case_id": "GUARD-1", "criterion": "c", "case_context": "x", "sut_output": "y", key: "LEAK"}
    try:
        lane.open_case(case)
        guard_rejects_all = False
    except Exception:
        pass

leakage = {
    "artifact": "leakage-audit-v2-6",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
    "forbidden_case_keys": list(FORBIDDEN_CASE_KEYS),
    "forbidden_packet_keys": list(FORBIDDEN_PACKET_KEYS),
    "packets_scanned": len([f for f in wf]) + len(fw),
    "leak_findings": leak_hits,
    "leakage_count": len(leak_hits),
    "runtime_guard_rejects_all_forbidden_keys": guard_rejects_all,
    "leakage_gate_pass": len(leak_hits) == 0 and guard_rejects_all,
}
with open(os.path.join(DIR, "leakage-audit.json"), "w", encoding="utf-8") as f:
    json.dump(leakage, f, indent=1, ensure_ascii=False)

# --- Provenance audit: completeness on resolved cases across all suites ---
def provenance_complete(rec):
    events = [p["event"] for p in rec["provenance"]]
    opened = events[:3] == ["PACKET_CREATED", "ROUTED", "STATUS"]
    # Legitimate resolved patterns after the canonical opening trio.
    tails = (
        ["REVIEW_ACCEPTED", "STATUS"],
        ["REVIEW_ACCEPTED", "STATUS", "DUAL_REVIEW_ACCEPTED", "STATUS"],
        ["REVIEW_ACCEPTED", "STATUS", "DUAL_REVIEW_DISAGREEMENT", "STATUS", "ADJUDICATION_APPLIED", "STATUS"],
        ["REVIEW_ACCEPTED", "STATUS", "DUPLICATE_REVIEW_REJECTED"],
    )
    tail_ok = any(events[3:] == t for t in tails)
    closed = rec["status"] == "HUMAN_REVIEW_RESOLVED" and (events[-1] == "STATUS" or events[-1] == "DUPLICATE_REVIEW_REJECTED")
    sha_present = all("packet_sha256" in p for p in rec["provenance"] if p["event"] == "PACKET_CREATED")
    return opened and tail_ok and closed and sha_present

counts = {"workflow_test": {"n": 0, "complete": 0}, "burned_replay": {"n": 0, "complete": 0},
          "fresh_workflow": {"n": 0, "complete": 0}}
for suite in counts.values():
    suite["resolved"] = 0


def envelope(rec, case_id):
    return {
        "packet_id": rec["packet"]["packet_id"], "case_id": case_id,
        "contract_version": rec["packet"]["contract_version"],
        "reviewed_utc": "2026-09-13T00:00:00Z",
    }

for fx in wf:
    lane = ReviewLane()
    try:
        rec = lane.open_case(fx["case"])
    except Exception:
        continue
    counts["workflow_test"]["n"] += 1
    for rv in fx.get("reviews", []):
        if isinstance(rv, dict):
            r2 = dict(rv)
            r2.update(envelope(rec, fx["case"]["case_id"]))
            lane.ingest_review(fx["case"]["case_id"], r2)
    if fx.get("adjudication") is not None:
        try:
            lane.adjudicate(fx["case"]["case_id"], fx["adjudication"])
        except Exception:
            pass
    if rec["status"] == "HUMAN_REVIEW_RESOLVED":
        counts["workflow_test"]["resolved"] += 1
        if provenance_complete(rec):
            counts["workflow_test"]["complete"] += 1

v25 = load("../judge-contract-v2-5-m2-decomposition/boundary-calibration-a-pass1.json")["items"]
fix25 = {x["id"]: x for x in load("../judge-contract-v2-5-m2-decomposition/m2-fixtures-v2-5.json")["fixtures"]}
for item in v25:
    fx = fix25[item["id"]]
    lane = ReviewLane()
    rec = lane.open_case({"case_id": item["id"], "criterion": fx["crit"], "case_context": fx["ctx"], "sut_output": fx["sut"]})
    counts["burned_replay"]["n"] += 1
    review = {"reviewer_id": "V25_PASS1_REPLAY", "judgment": item["judgment"]}
    review.update(envelope(rec, item["id"]))
    lane.ingest_review(item["id"], review)
    if rec["status"] == "HUMAN_REVIEW_RESOLVED":
        counts["burned_replay"]["resolved"] += 1
        if provenance_complete(rec):
            counts["burned_replay"]["complete"] += 1

for fx in fw:
    lane = ReviewLane()
    rec = lane.open_case(fx["case"])
    counts["fresh_workflow"]["n"] += 1
    rv = dict(fx["review"])
    rv.update(envelope(rec, fx["fixture_id"]))
    lane.ingest_review(fx["fixture_id"], rv)
    if rec["status"] == "HUMAN_REVIEW_RESOLVED":
        counts["fresh_workflow"]["resolved"] += 1
        if provenance_complete(rec):
            counts["fresh_workflow"]["complete"] += 1

provenance = {
    "artifact": "provenance-audit-v2-6",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
    "resolved_case_provenance": counts,
    "all_resolved_complete": all(v["complete"] == v["resolved"] for v in counts.values()),
    "provenance_gate_pass": all(v["complete"] == v["resolved"] for v in counts.values()),
}
with open(os.path.join(DIR, "provenance-audit.json"), "w", encoding="utf-8") as f:
    json.dump(provenance, f, indent=1, ensure_ascii=False)

print("leakage:", leakage["leakage_count"], "findings | guard ok:", guard_rejects_all)
print("provenance complete:", provenance["all_resolved_complete"], counts)
