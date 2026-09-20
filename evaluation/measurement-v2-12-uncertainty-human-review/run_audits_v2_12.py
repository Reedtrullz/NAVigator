"""V2.12 audits: leakage, provenance completeness, process integrity.
No model calls. Historical files read-only."""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from review_lane_uncertainty_v2_12 import (  # noqa: E402
    FORBIDDEN_CASE_KEYS, FORBIDDEN_PACKET_KEYS, UncertaintyReviewLane)
from run_burned_replay_v2_12 import replay_set_a, replay_v28  # noqa: E402


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# --- Leakage audit ---
wf = load("workflow-test-fixtures.json")["fixtures"]
fw = load("fresh-workflow-fixtures.json")["fixtures"]
leak_hits = []

for suite, fixtures in (("workflow-test", wf), ("fresh-workflow", fw)):
    for fx in fixtures:
        lane = UncertaintyReviewLane()
        try:
            rec = lane.open_case(fx["case"])
        except Exception:
            continue
        found = [k for k in FORBIDDEN_PACKET_KEYS if k in rec["packet"]]
        if found:
            leak_hits.append({"suite": suite, "fixture": fx["fixture_id"], "fields": found})

guard_rejects_all = True
for key in FORBIDDEN_CASE_KEYS:
    lane = UncertaintyReviewLane()
    case = {"case_id": "GUARD-1", "criterion": "c", "case_context": "x",
            "sut_output": "y", key: "LEAK"}
    try:
        lane.open_case(case)
        guard_rejects_all = False
    except Exception:
        pass

leakage = {
    "artifact": "leakage-audit-v2-12",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
    "forbidden_case_keys": list(FORBIDDEN_CASE_KEYS),
    "forbidden_packet_keys": list(FORBIDDEN_PACKET_KEYS),
    "packets_scanned": len(wf) + len(fw),
    "leak_findings": leak_hits,
    "leakage_count": len(leak_hits),
    "runtime_guard_rejects_all_forbidden_keys": guard_rejects_all,
    "leakage_gate_pass": len(leak_hits) == 0 and guard_rejects_all,
}
with open(os.path.join(DIR, "leakage-audit.json"), "w", encoding="utf-8") as f:
    json.dump(leakage, f, indent=1, ensure_ascii=False)

# --- Provenance audit: replay every suite, check resolved provenance ---
ALLOWED_TAILS = (
    ["REVIEW_REJECTED", "STATUS"],
    ["REVIEW_REJECTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"],
    ["REVIEW_ACCEPTED", "STATUS"],
    ["REVIEW_ACCEPTED", "STATUS", "DUAL_REVIEW_ACCEPTED", "STATUS"],
    ["REVIEW_ACCEPTED", "STATUS", "DUAL_REVIEW_DISAGREEMENT", "STATUS",
     "ADJUDICATION_APPLIED", "STATUS"],
    ["REVIEW_ACCEPTED", "STATUS", "DUPLICATE_REVIEW_REJECTED"],
)


def provenance_complete(rec):
    events = [p["event"] for p in rec["provenance"]]
    opened = events[:3] == ["PACKET_CREATED", "ROUTED", "STATUS"]
    tail_ok = any(events[3:] == t for t in ALLOWED_TAILS)
    closed = rec["status"] == "HUMAN_REVIEW_RESOLVED" and events[-1] in ("STATUS", "DUPLICATE_REVIEW_REJECTED")
    sha_present = all("packet_sha256" in p for p in rec["provenance"] if p["event"] == "PACKET_CREATED")
    return opened and tail_ok and closed and sha_present


counts = {"workflow_test": {"n": 0, "resolved": 0, "complete": 0},
          "burned_replay": {"n": 0, "resolved": 0, "complete": 0},
          "fresh_workflow": {"n": 0, "resolved": 0, "complete": 0}}


def envelope(rec, case_id):
    return {"packet_id": rec["packet"]["packet_id"], "case_id": case_id,
            "contract_version": rec["packet"]["contract_version"],
            "reviewed_utc": "2026-09-14T00:00:00Z"}


for fx in wf:
    lane = UncertaintyReviewLane()
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

burned_lane = UncertaintyReviewLane()
mismatches, span_failures = [], []
set_a_rows = replay_set_a(burned_lane, mismatches, span_failures)
v28_rows = replay_v28(burned_lane, mismatches, span_failures)
counts["burned_replay"]["n"] = len(set_a_rows) + len(v28_rows)
for rec in burned_lane.cases.values():
    if rec["status"] == "HUMAN_REVIEW_RESOLVED":
        counts["burned_replay"]["resolved"] += 1
        if provenance_complete(rec):
            counts["burned_replay"]["complete"] += 1

for fx in fw:
    lane = UncertaintyReviewLane()
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
    "artifact": "provenance-audit-v2-12",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
    "resolved_case_provenance": counts,
    "all_resolved_complete": all(v["complete"] == v["resolved"] for v in counts.values()),
    "provenance_gate_pass": all(v["complete"] == v["resolved"] for v in counts.values()),
}
with open(os.path.join(DIR, "provenance-audit.json"), "w", encoding="utf-8") as f:
    json.dump(provenance, f, indent=1, ensure_ascii=False)

# --- Process audit: frozen inputs unchanged vs recorded replay inputs;
# fresh workflow rerun reproduces recorded verdicts ---
replay_recorded = load("burned-replay-results.json")
base_7e = os.path.join(os.path.dirname(DIR), "judge-contract-v2-7e-uncertainty-repair")
base_v28 = os.path.join(os.path.dirname(DIR), "judge-selection-v2-8-non-m2-post-repair")
inputs_now = {
    "v2_7e_set_a": {
        "calibration-set-a.json": sha256_file(os.path.join(base_7e, "calibration-set-a.json")),
        "calibration-set-a-pass1.json": sha256_file(os.path.join(base_7e, "calibration-set-a-pass1.json")),
        "calibration-set-a-pass2.json": sha256_file(os.path.join(base_7e, "calibration-set-a-pass2.json")),
    },
    "v2_8_uncertainty_subset": {
        "screening-fixtures.json": sha256_file(os.path.join(base_v28, "screening-fixtures.json")),
        "screening-gold.json": sha256_file(os.path.join(base_v28, "screening-gold.json")),
    },
}
inputs_unchanged = inputs_now == replay_recorded["inputs_sha256"]

_, rerun = None, None
sys.path.insert(0, DIR)
from run_fresh_workflow_v2_12 import run_once  # noqa: E402

_, rerun = run_once()
recorded = load("fresh-workflow-results.json")["results"]
verdicts_match = all(
    rerun[fid]["verdict"] == recorded[fid]["verdict"] for fid in recorded)
counts_match = set(rerun) == set(recorded)

process = {
    "artifact": "process-audit-v2-12",
    "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
    "burned_replay_inputs_unchanged": inputs_unchanged,
    "fresh_workflow_rerun_idempotent": verdicts_match and counts_match,
    "burned_replay_replayed_clean": len(mismatches) == 0 and len(span_failures) == 0,
    "process_gate_pass": inputs_unchanged and verdicts_match and counts_match
    and len(mismatches) == 0 and len(span_failures) == 0,
}
with open(os.path.join(DIR, "process-audit.json"), "w", encoding="utf-8") as f:
    json.dump(process, f, indent=1, ensure_ascii=False)

print("leakage:", leakage["leakage_count"], "findings | guard ok:", guard_rejects_all)
print("provenance complete:", provenance["all_resolved_complete"], counts)
print("process:", "PASS" if process["process_gate_pass"] else "FAIL")

