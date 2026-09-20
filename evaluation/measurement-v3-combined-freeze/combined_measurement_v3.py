"""Stage 3 combined measurement engine (AFK campaign).

Routes each item to exactly one authoritative owner:
  1. deterministic scorer (dev-corpus-scorer-v1, SemanticJudgeStub),
  2. M2 human-review lane (V2.6) for M2-workflow critical cases,
  3. generic semantic human-review lane (V2.15) for all four semantic dims.
Boundary rule: deterministic scorer notes that require semantic judgment
(SEMANTIC_JUDGE_STUB family) escalate to the generic human-review lane and
never produce a final label by themselves. No automated semantic verdicts.
No model calls. Stdlib only.
"""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(DIR)
sys.path.insert(0, EVAL_DIR)
sys.path.insert(0, os.path.join(EVAL_DIR, "dev-corpus-scorer-v1"))
sys.path.insert(0, os.path.join(EVAL_DIR, "measurement-v2-6-m2-human-review"))
sys.path.insert(0, os.path.join(EVAL_DIR, "measurement-v2-15-semantic-human-review-fallback"))

import scorer as SCORER  # noqa: E402
import review_lane_v2_6 as M2  # noqa: E402
import review_lane_semantic_v2_15 as SEM  # noqa: E402

ENGINE_VERSION = "combined-measurement-v3"
ESCALATION_NOTES = ("SEMANTIC_JUDGE_STUB", "PARAPHRASE_NOT_DETERMINISTICALLY_MATCHED",
                    "CRITICAL_CONDITION_UNMAPPED")
NOTE_TO_DIMENSION = {
    "SEMANTIC_JUDGE_STUB": "forbidden_claim",
    "PARAPHRASE_NOT_DETERMINISTICALLY_MATCHED": "forbidden_claim",
    "CRITICAL_CONDITION_UNMAPPED": "critical_condition",
}
FORBIDDEN_ITEM_KEYS = ("final_gold", "gold", "expected", "model_verdict",
                       "automated_verdict", "tag")
RESPONSIBILITY_MAP = {
    "deterministic": ["scorer_deterministic_criteria"],
    "automated_semantic": [],
    "human_review": [
        "m2_lane_critical_condition_decomposed",
        "generic_lane_critical_condition",
        "generic_lane_forbidden_claim",
        "generic_lane_route_correctness",
        "generic_lane_required_uncertainty",
    ],
}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def route(item):
    """Single authoritative owner per item. Raises on leakage keys."""
    for bad in FORBIDDEN_ITEM_KEYS:
        if bad in item:
            raise ValueError("leakage field in item: " + bad)
    wf = item["workflow"]
    if wf == "scorer":
        return "DETERMINISTIC_SCORER_V1"
    if wf == "m2":
        return "M2_LANE_V2_6"
    if wf == "semantic":
        return "GENERIC_LANE_V2_15"
    raise ValueError("unknown workflow: " + str(wf))


def run_scorer_item(item, escalate=True):
    """Deterministic scoring; boundary escalation to the generic lane when the
    deterministic layer cannot resolve semantics on its own."""
    scored = SCORER.score_case(item["case"], item["raw_answer"],
                               item["capabilities"], SCORER.SemanticJudgeStub())
    out = {"item_id": item["item_id"], "workflow": "scorer",
           "scorer_result": scored, "engine_version": ENGINE_VERSION}
    hit = [n for n in scored["scorer_notes"] if n in ESCALATION_NOTES]
    if hit and escalate:
        dimension = NOTE_TO_DIMENSION[hit[0]]
        lane = SEM.SemanticReviewLane()
        rec = lane.open_case({
            "case_id": "ESC-" + str(item["item_id"]),
            "dimension": dimension,
            "criterion": item["escalation_criterion"],
            "case_context": item["case"].get("utterance", ""),
            "sut_output": json.dumps(item["raw_answer"], ensure_ascii=False)
            if not isinstance(item["raw_answer"], str) else item["raw_answer"],
        })
        out["escalated"] = True
        out["escalation_notes"] = hit
        out["escalation_dimension"] = dimension
        out["review_record"] = rec
        out["final"] = None
        out["status"] = rec["status"]
        out["authoritative_owner"] = "GENERIC_LANE_V2_15"
    else:
        out["escalated"] = False
        out["final"] = scored
        out["status"] = "DETERMINISTIC_FINAL"
        out["authoritative_owner"] = "DETERMINISTIC_SCORER_V1"
    return out


def run_m2_item(item):
    lane = M2.ReviewLane()
    rec = lane.open_case(item["case"])
    for i, rv0 in enumerate(item.get("reviews", [])):
        rv = dict(rv0)
        rv.setdefault("packet_id", rec["packet"]["packet_id"])
        rv.setdefault("case_id", item["case"]["case_id"])
        rv.setdefault("contract_version", rec["packet"]["contract_version"])
        rv.setdefault("reviewed_utc", "2026-09-14T00:00:00Z")
        try:
            rec = lane.ingest_review(item["case"]["case_id"], rv)
        except M2.LaneError:
            pass
    if item.get("adjudication"):
        try:
            rec = lane.adjudicate(item["case"]["case_id"], item["adjudication"])
        except M2.LaneError:
            pass
    final = rec.get("final")
    if isinstance(final, dict):
        final = final.get("final_label")
    return {"item_id": item["item_id"], "workflow": "m2",
            "status": rec["status"], "final": final,
            "review_mode": rec["review_mode"], "record": rec,
            "authoritative_owner": "M2_LANE_V2_6", "engine_version": ENGINE_VERSION}


def run_semantic_item(item):
    lane = SEM.SemanticReviewLane()
    rec = lane.open_case(item["case"])
    for i, j in enumerate(item.get("judgments", [])):
        rv = {"reviewer_id": "R" + str(i + 1), "judgment": j,
              "packet_id": rec["packet"]["packet_id"],
              "case_id": item["case"]["case_id"],
              "contract_version": rec["packet"]["contract_version"],
              "reviewed_utc": "2026-09-14T00:00:00Z"}
        try:
            rec = lane.ingest_review(item["case"]["case_id"], rv)
        except SEM.LaneError:
            pass
    if item.get("adjudication"):
        try:
            rec = lane.adjudicate(item["case"]["case_id"], item["adjudication"])
        except SEM.LaneError:
            pass
    final = None
    if rec["status"] == "HUMAN_REVIEW_RESOLVED" and rec["final"]:
        final = rec["final"].get("final_verdict", rec["final"].get("final_label"))
    return {"item_id": item["item_id"], "workflow": "semantic",
            "status": rec["status"], "final": final,
            "review_mode": rec["review_mode"], "record": rec,
            "authoritative_owner": "GENERIC_LANE_V2_15", "engine_version": ENGINE_VERSION}


def run_item(item):
    owner = route(item)
    if owner == "DETERMINISTIC_SCORER_V1":
        return run_scorer_item(item)
    if owner == "M2_LANE_V2_6":
        return run_m2_item(item)
    return run_semantic_item(item)


def provenance_complete_review(rec):
    events = [p["event"] for p in rec["provenance"]]
    if events[:3] != ["PACKET_CREATED", "ROUTED", "STATUS"]:
        return False
    if rec["status"] == "HUMAN_REVIEW_RESOLVED":
        # Duplicate-review rejection is a valid terminal tail with no STATUS.
        if events[-1] not in ("STATUS", "DUPLICATE_REVIEW_REJECTED"):
            return False
    elif events[-1] != "STATUS":
        return False
    need_sha = ("PACKET_CREATED", "REVIEW_ACCEPTED", "DUAL_REVIEW_ACCEPTED",
                "ADJUDICATION_APPLIED")
    for p in rec["provenance"]:
        if p["event"] in need_sha and "packet_sha256" not in p:
            return False
    routed = [p for p in rec["provenance"] if p["event"] == "ROUTED"]
    return all("dimension" in p and p.get("automated_authoritative") is False
               for p in routed)


def combined_report(results):
    r = {"engine_version": ENGINE_VERSION, "n_items": len(results),
         "deterministic_criteria": {"scored_final": 0},
         "automated_semantic_criteria": {"present": False,
                                         "automated_judge_accuracy": None,
                                         "automated_judge_coverage": 0.0},
         "human_reviewed_criteria": {"resolved": 0},
         "review_pending": 0, "review_invalid": 0, "review_disagreement": 0,
         "execution_failure": 0,
         "human_review_coverage": None, "final_measurement_completeness": None,
         "master_accuracy": None}
    for res in results:
        st = res["status"]
        if st == "DETERMINISTIC_FINAL":
            r["deterministic_criteria"]["scored_final"] += 1
        elif st == "HUMAN_REVIEW_RESOLVED":
            r["human_reviewed_criteria"]["resolved"] += 1
        elif st == "HUMAN_REVIEW_PENDING":
            r["review_pending"] += 1
        elif st == "HUMAN_REVIEW_INVALID":
            r["review_invalid"] += 1
        elif st == "HUMAN_REVIEW_DISAGREEMENT":
            r["review_disagreement"] += 1
        else:
            r["execution_failure"] += 1
    total = r["n_items"]
    human_total = (r["human_reviewed_criteria"]["resolved"] + r["review_pending"]
                   + r["review_invalid"] + r["review_disagreement"])
    if human_total:
        r["human_review_coverage"] = (r["human_reviewed_criteria"]["resolved"]
                                      / human_total)
    r["final_measurement_completeness"] = ((r["deterministic_criteria"]["scored_final"]
                                            + r["human_reviewed_criteria"]["resolved"])
                                           / total if total else 0.0)
    return r
