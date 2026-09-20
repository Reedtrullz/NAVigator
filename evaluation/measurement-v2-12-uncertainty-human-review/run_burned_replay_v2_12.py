"""V2.12 burned replay: replay frozen V2.7E Set A and V2.8 uncertainty subset
through the uncertainty human-review lane and mechanically compare derived
verdicts against the frozen historical labels.

Pre-registered span rule: V2.8 gold spans were recorded historically with minor
case/punctuation variance (e.g. V28-UNC-26). This replay resolves each gold
span to the verbatim SUT substring using normalized containment (lowercase,
strip non-alnum except spaces). Live lane ingestion keeps strict verbatim
validation. Set A labels carry no spans, so this rule only affects V2.8.

No model calls. Stdlib only. Historical files are read-only.
"""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(DIR)
sys.path.insert(0, DIR)
from review_lane_uncertainty_v2_12 import (  # noqa: E402
    LaneError, UncertaintyReviewLane, validate_packet)

REPLAY_REVIEWER = "burned-replay-reviewer"


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def resolve_span_normalized(sut, span):
    """Map a normalized span to the verbatim substring of sut. Returns None
    when the normalized span is not contained in the normalized SUT output."""
    index_map = []
    norm_chars = []
    for i, ch in enumerate(sut):
        if ch.isalnum() or ch.isspace():
            norm_chars.append(ch.lower() if ch.isalnum() else ch)
            index_map.append(i)
    norm_sut = "".join(norm_chars).strip()
    # account for leading whitespace stripped from norm_sut
    lead = len(norm_chars) - len("".join(norm_chars).lstrip())
    norm_span = "".join(ch.lower() if ch.isalnum() else ch for ch in span
                        if ch.isalnum() or ch.isspace()).strip()
    if not norm_span:
        return None
    pos = norm_sut.find(norm_span)
    if pos < 0:
        return None
    start = index_map[pos + lead]
    end = index_map[pos + lead + len(norm_span) - 1]
    return sut[start:end + 1]


def build_case(fixture):
    return {
        "case_id": fixture["id"],
        "criterion": fixture["crit"],
        "case_context": fixture["ctx"],
        "sut_output": fixture["sut"],
    }


def build_review(packet, judgment, reviewer_id):
    return {
        "packet_id": packet["packet_id"],
        "case_id": packet["case_id"],
        "reviewer_id": reviewer_id,
        "contract_version": packet["contract_version"],
        "reviewed_utc": "BURNED_REPLAY",
        "judgment": judgment,
    }


def judgment_from_flat(mode, behavior, comps=None, spans=None):
    j = {
        "uncertainty_requirement_mode": mode,
        "uncertainty_output_behavior": behavior,
        "evidence_spans": spans or [],
    }
    if comps:
        j["compound_components"] = comps
    return j


def replay_set_a(lane, mismatches, span_failures):
    base = os.path.join(EVAL_DIR, "judge-contract-v2-7e-uncertainty-repair")
    frozen = json.load(open(os.path.join(base, "calibration-set-a.json")))
    pass1 = json.load(open(os.path.join(base, "calibration-set-a-pass1.json")))["labels"]
    pass2 = json.load(open(os.path.join(base, "calibration-set-a-pass2.json")))["labels"]
    d1 = {l["id"]: l for l in pass1}
    d2 = {l["id"]: l for l in pass2}
    results = []
    for fixture in frozen["fixtures"]:
        cid = fixture["id"]
        case = build_case(fixture)
        rec = lane.open_case(case)
        ok, why = validate_packet(rec["packet"])
        if not ok:
            raise LaneError("packet invalid for " + cid + ": " + why)
        l1, l2 = d1[cid], d2[cid]
        r1 = build_review(rec["packet"], judgment_from_flat(l1["mode"], l1["behavior"]), REPLAY_REVIEWER + "-1")
        lane.ingest_review(cid, r1)
        v1 = rec["final"]["final_verdict"]
        r2 = build_review(rec["packet"], judgment_from_flat(l2["mode"], l2["behavior"]), REPLAY_REVIEWER + "-2")
        lane.ingest_review(cid, r2)
        v2 = rec["final"]["final_verdict"] if rec["final"] else None
        row = {
            "case_id": cid,
            "recorded_pass1": l1["verdict"],
            "derived_pass1": v1,
            "recorded_pass2": l2["verdict"],
            "derived_pass2": v2,
            "final_status": rec["status"],
            "review_mode": rec["review_mode"],
            "match": v1 == l1["verdict"] and v2 == l2["verdict"],
        }
        if not row["match"]:
            mismatches.append(row)
        results.append(row)
    return results


def replay_v28(lane, mismatches, span_failures):
    base = os.path.join(EVAL_DIR, "judge-selection-v2-8-non-m2-post-repair")
    with open(os.path.join(base, "screening-fixtures.json")) as fh:
        raw = json.load(fh)
    fixtures = raw if isinstance(raw, list) else raw.get("fixtures", raw.get("cases", []))
    gold = json.load(open(os.path.join(base, "screening-gold.json")))["gold"]
    unc = [f for f in fixtures if "UNC" in str(f.get("id", ""))]
    results = []
    for fixture in unc:
        cid = fixture["id"]
        g = gold[cid]
        inter = g["inter"]
        mode = inter["uncertainty_requirement_mode"]
        # Historical COMPOUND rows carry only compound_components in inter;
        # behavior is component-derived there. Non-COMPOUND rows must have it.
        behavior = inter.get("uncertainty_output_behavior")
        comps = inter.get("compound_components")
        if mode != "COMPOUND" and behavior is None:
            raise LaneError("non-COMPOUND gold row missing behavior: " + cid)
        spans = []
        for span in g.get("spans", []):
            resolved = span if span in fixture["sut"] else resolve_span_normalized(fixture["sut"], span)
            if resolved is None:
                span_failures.append({"case_id": cid, "span": span})
            else:
                spans.append(resolved)
        case = build_case(fixture)
        rec = lane.open_case(case)
        ok, why = validate_packet(rec["packet"])
        if not ok:
            raise LaneError("packet invalid for " + cid + ": " + why)
        review = build_review(rec["packet"], judgment_from_flat(mode, behavior, comps, spans), REPLAY_REVIEWER)
        lane.ingest_review(cid, review)
        derived = rec["final"]["final_verdict"] if rec["final"] else None
        row = {
            "case_id": cid,
            "recorded": g["verdict"],
            "derived": derived,
            "final_status": rec["status"],
            "review_mode": rec["review_mode"],
            "match": derived == g["verdict"],
        }
        if not row["match"]:
            mismatches.append(row)
        results.append(row)
    return results


def main():
    lane = UncertaintyReviewLane()
    mismatches = []
    span_failures = []
    set_a = replay_set_a(lane, mismatches, span_failures)
    v28 = replay_v28(lane, mismatches, span_failures)
    buckets = {"resolved": 0, "unresolved": 0}
    for rec in lane.cases.values():
        if rec["status"] == "HUMAN_REVIEW_RESOLVED":
            buckets["resolved"] += 1
        else:
            buckets["unresolved"] += 1
    set_a_pass = all(r["match"] for r in set_a)
    v28_pass = all(r["match"] for r in v28)
    gates = {
        "set_a_all_match": set_a_pass,
        "set_a_count": len(set_a) == 32,
        "v28_all_match": v28_pass,
        "v28_count": len(v28) == 60,
        "all_resolved": buckets["unresolved"] == 0,
        "span_resolution_failures_zero": len(span_failures) == 0,
        "mismatches_zero": len(mismatches) == 0,
    }
    inputs = {
        "v2_7e_set_a": {
            "calibration-set-a.json": sha256_file(os.path.join(
                EVAL_DIR, "judge-contract-v2-7e-uncertainty-repair/calibration-set-a.json")),
            "calibration-set-a-pass1.json": sha256_file(os.path.join(
                EVAL_DIR, "judge-contract-v2-7e-uncertainty-repair/calibration-set-a-pass1.json")),
            "calibration-set-a-pass2.json": sha256_file(os.path.join(
                EVAL_DIR, "judge-contract-v2-7e-uncertainty-repair/calibration-set-a-pass2.json")),
        },
        "v2_8_uncertainty_subset": {
            "screening-fixtures.json": sha256_file(os.path.join(
                EVAL_DIR, "judge-selection-v2-8-non-m2-post-repair/screening-fixtures.json")),
            "screening-gold.json": sha256_file(os.path.join(
                EVAL_DIR, "judge-selection-v2-8-non-m2-post-repair/screening-gold.json")),
        },
    }
    out = {
        "replay": "V2.12_BURNED_REPLAY_UNCERTAINTY_HUMAN_REVIEW_LANE",
        "lane": "review_lane_uncertainty_v2_12.py",
        "inputs_sha256": inputs,
        "summary": {
            "set_a_cases": len(set_a),
            "v28_cases": len(v28),
            "resolved": buckets["resolved"],
            "unresolved": buckets["unresolved"],
            "mismatches": len(mismatches),
            "span_resolution_failures": len(span_failures),
        },
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "set_a_results": set_a,
        "v28_results": v28,
        "mismatch_rows": mismatches,
        "span_failure_rows": span_failures,
    }
    out_path = os.path.join(DIR, "burned-replay-results.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("burned replay: set_a {}/{}, v28 {}/{}, resolved {}, span_failures {}".format(
        sum(1 for r in set_a if r["match"]), len(set_a),
        sum(1 for r in v28 if r["match"]), len(v28),
        buckets["resolved"], len(span_failures)))
    print("gates:", "PASS" if out["all_gates_pass"] else "FAIL")
    return 0 if out["all_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
