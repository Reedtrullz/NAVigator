"""V2.15 generic semantic human-review lane runtime (campaign Stage 2F).

Authoritative semantic judgement is human-only for all four dimensions
(AFK campaign Stage 2F, 2026-09-14). The human supplies intermediate
observations against the frozen per-dimension contracts; judge_core_v2_13
(imported unmodified from the frozen V2.11-lineage core) supplies the final
verdict mechanically via derive_final. No model calls, stdlib only.
"""
import datetime
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(DIR)
sys.path.insert(0, os.path.join(EVAL_DIR, "judge-selection-v2-13-forbidden-route-specialist"))
import judge_core_v2_13 as CORE  # frozen module, never edited here

LANE_VERSION = "semantic-human-review-lane-v2-15"
DIMENSIONS = ("critical_condition", "forbidden_claim", "route_correctness",
              "required_uncertainty")
DIMENSION_CONTRACT = {
    "critical_condition": "semantic-judge-contract-v1-4",
    "forbidden_claim": "semantic-judge-contract-v1-4",
    "route_correctness": "semantic-judge-contract-v1-4",
    "required_uncertainty": "semantic-judge-contract-v2-7e",
}
MATCH_STATES = CORE.MATCH_STATES
COMMITMENTS = CORE.COMMITMENTS
EVIDENCE_STATES = CORE.EVIDENCE_STATES
ROUTE_VERDICTS = CORE.ROUTE_VERDICTS
ROUTE_COMMITMENTS = CORE.COMMITMENTS
UNC_MODES = ("NONE", "EXPLICIT_LIMITATION", "NON_ASSERTION_CONSTRAINT", "COMPOUND")
UNC_BEHAVIORS = CORE.U7E.BEHAVIORS
FORBIDDEN_CASE_KEYS = ("final_gold", "gold", "model_verdict", "automated_verdict",
                       "tag", "expected", "inter")


class LaneError(Exception):
    pass


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


INSTRUCTIONS = {
    "critical_condition": [
        "Classify critical_evidence_state per the frozen v1-4 critical contract.",
        "Provide verbatim evidence spans from the SUT output that justify the state.",
    ],
    "forbidden_claim": [
        "Classify criterion_semantic_match and speaker_commitment per the frozen v1-4 forbidden contract.",
        "Provide verbatim evidence spans from the SUT output when the claim is expressed or implied.",
    ],
    "route_correctness": [
        "Classify route_proposition_present, route_speaker_commitment and proposed_verdict per the frozen v1-4 route contract.",
        "Only ASSERTED and HEDGED_ASSERTION commitments are evaluable; all other commitments propose UNRESOLVED.",
        "Provide verbatim evidence spans from the SUT output identifying the route proposition.",
    ],
    "required_uncertainty": [
        "Classify uncertainty_requirement_mode and uncertainty_output_behavior per the frozen V2.7E uncertainty contract.",
        "For COMPOUND, list components as objects {kind, behavior}.",
        "Provide verbatim evidence spans when a limitation or prohibited conclusion is expressed; otherwise empty.",
    ],
}


def _validate_judgment(dimension, judgment):
    """Enum-level schema validation only; semantics are derived mechanically
    by the frozen core afterwards. Non-derivable combinations fail closed."""
    if not isinstance(judgment, dict):
        return "judgment not object"
    if dimension == "critical_condition":
        if judgment.get("critical_evidence_state") not in EVIDENCE_STATES:
            return "invalid critical_evidence_state"
    elif dimension == "forbidden_claim":
        if judgment.get("criterion_semantic_match") not in MATCH_STATES:
            return "invalid criterion_semantic_match"
        if judgment.get("speaker_commitment") not in COMMITMENTS:
            return "invalid speaker_commitment"
    elif dimension == "route_correctness":
        if judgment.get("route_proposition_present") not in ("YES", "NO"):
            return "invalid route_proposition_present"
        if judgment.get("route_speaker_commitment") not in ROUTE_COMMITMENTS:
            return "invalid route_speaker_commitment"
        if judgment.get("proposed_verdict") not in ROUTE_VERDICTS:
            return "invalid proposed_verdict"
    elif dimension == "required_uncertainty":
        mode = judgment.get("uncertainty_requirement_mode")
        if mode not in UNC_MODES:
            return "invalid uncertainty_requirement_mode"
        if mode == "NONE":
            if judgment.get("uncertainty_output_behavior") != "NONE":
                return "NONE mode requires behavior NONE"
        elif mode == "COMPOUND":
            comps = judgment.get("compound_components")
            if not isinstance(comps, list) or not comps:
                return "COMPOUND requires compound_components"
            for c in comps:
                if not (isinstance(c, dict) and c.get("kind") in ("EXPRESSION", "NON_ASSERTION")
                        and c.get("behavior") in UNC_BEHAVIORS):
                    return "invalid compound component"
        else:
            if judgment.get("uncertainty_output_behavior") not in UNC_BEHAVIORS:
                return "invalid uncertainty_output_behavior"
    else:
        return "unknown dimension"
    spans = judgment.get("evidence_spans")
    if not isinstance(spans, list):
        return "evidence_spans not list"
    return None


def derive_final(dimension, judgment):
    """Mechanical derivation via the frozen V2.13 core. Raises ValueError on
    non-derivable label combinations (fail-closed upstream)."""
    return CORE.derive_final(dimension, judgment)


def create_packet(case):
    for bad in FORBIDDEN_CASE_KEYS:
        if bad in case:
            raise LaneError("leakage field in case input: " + bad)
    dimension = case.get("dimension")
    if dimension not in DIMENSIONS:
        raise LaneError("unknown dimension: " + str(dimension))
    for key in ("case_id", "criterion", "case_context", "sut_output"):
        value = case.get(key)
        if not isinstance(value, str) or not value.strip():
            raise LaneError("packet field missing/empty: " + key)
    contract = DIMENSION_CONTRACT[dimension]
    packet = {
        "packet_id": "PKT-" + case["case_id"],
        "case_id": case["case_id"],
        "lane_version": LANE_VERSION,
        "contract_version": contract,
        "dimension": dimension,
        "criterion": case["criterion"],
        "case_context": case["case_context"],
        "sut_output": case["sut_output"],
        "reviewer_instructions": INSTRUCTIONS[dimension],
        "created_utc": _now(),
    }
    packet["packet_sha256"] = _sha(json.dumps(packet, sort_keys=True, ensure_ascii=False))
    return packet


FORBIDDEN_PACKET_KEYS = ("final_gold", "gold", "expected", "model_verdict",
                         "automated_verdict", "tag")


def validate_packet(packet):
    if not isinstance(packet, dict):
        return False, "not object"
    if packet.get("dimension") not in DIMENSIONS:
        return False, "dimension"
    if packet.get("contract_version") != DIMENSION_CONTRACT[packet["dimension"]]:
        return False, "contract_version"
    if packet.get("lane_version") != LANE_VERSION:
        return False, "lane_version"
    for key in FORBIDDEN_PACKET_KEYS:
        if key in packet:
            return False, "leakage field present: " + key
    for key in ("packet_id", "case_id", "criterion", "case_context", "sut_output",
                "reviewer_instructions", "created_utc", "packet_sha256"):
        if key not in packet:
            return False, "missing " + key
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if packet["packet_sha256"] != _sha(json.dumps(body, sort_keys=True, ensure_ascii=False)):
        return False, "sha mismatch"
    return True, "ok"


def validate_review(packet, review):
    """Structural + enum validation of a human review. Spans must be verbatim
    substrings of the SUT output whenever provided."""
    if not isinstance(review, dict):
        return False, "not object"
    for key in ("packet_id", "case_id", "reviewer_id", "contract_version", "reviewed_utc", "judgment"):
        if key not in review:
            return False, "missing " + key
    if review["packet_id"] != packet["packet_id"]:
        return False, "packet mismatch"
    if review["case_id"] != packet["case_id"]:
        return False, "case mismatch"
    if review["contract_version"] != packet["contract_version"]:
        return False, "contract_version"
    err = _validate_judgment(packet["dimension"], review["judgment"])
    if err:
        return False, err
    for span in review["judgment"].get("evidence_spans", []):
        if not isinstance(span, str) or span not in packet["sut_output"]:
            return False, "span not verbatim in SUT output"
    return True, "ok"


def validate_adjudication(record):
    if not isinstance(record, dict):
        return False, "not object"
    if record.get("adjudicated") is not True:
        return False, "not adjudicated"
    if record.get("model_outputs_visible_to_adjudicator") is not False:
        return False, "adjudicator saw model outputs"
    for key in ("case_id", "contract_version", "final_judgment", "adjudication_note"):
        if key not in record:
            return False, "missing " + key
    return True, "ok"


def _sig(judgment):
    return json.dumps(judgment, sort_keys=True, ensure_ascii=False)


class SemanticReviewLane:
    """Per-case workflow state machine. Fail-closed: no final verdict without
    valid human labels. Mechanical derivation only, after valid human input.
    A judgment the frozen core cannot derive is rejected, not guessed."""

    def __init__(self):
        self.cases = {}

    def open_case(self, case):
        packet = create_packet(case)
        ok, why = validate_packet(packet)
        if not ok:
            raise LaneError("packet invalid: " + why)
        rec = {
            "packet": packet,
            "status": "HUMAN_REVIEW_REQUIRED",
            "review_mode": None,
            "reviews": [],
            "adjudication": None,
            "final": None,
            "duplicate_reviews": [],
            "provenance": [],
        }
        rec["provenance"].append({
            "event": "PACKET_CREATED", "utc": packet["created_utc"],
            "packet_sha256": packet["packet_sha256"],
            "lane_version": LANE_VERSION, "contract_version": packet["contract_version"]})
        rec["provenance"].append({
            "event": "ROUTED", "route": "HUMAN_REVIEW_REQUIRED", "utc": _now(),
            "dimension": packet["dimension"], "automated_authoritative": False})
        rec["status"] = "HUMAN_REVIEW_PENDING"
        rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_PENDING", "utc": _now()})
        self.cases[case["case_id"]] = rec
        return rec

    def _resolve(self, rec, judgment, mode, provenance_event, actor):
        dimension = rec["packet"]["dimension"]
        try:
            final, basis = derive_final(dimension, judgment)
        except (ValueError, KeyError) as exc:
            rec["status"] = "HUMAN_REVIEW_INVALID"
            rec["provenance"].append({
                "event": "REVIEW_REJECTED", "utc": _now(), "actor": actor,
                "reason": "not derivable under frozen contract: " + str(exc)})
            rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_INVALID", "utc": _now()})
            return rec
        rec["review_mode"] = mode
        rec["final"] = {
            "final_verdict": final,
            "derivation_basis": basis,
            "derivation": "frozen-judge-core-v2-13-deterministic-mapper",
            "contract_version": rec["packet"]["contract_version"],
        }
        rec["provenance"].append({
            "event": provenance_event, "utc": _now(), "actor": actor,
            "packet_sha256": rec["packet"]["packet_sha256"],
            "contract_version": rec["packet"]["contract_version"],
            "intermediate_labels": {k: v for k, v in judgment.items() if k != "evidence_spans"},
            "evidence_spans": list(judgment.get("evidence_spans", [])),
            "final_verdict": final})
        rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_RESOLVED", "utc": _now()})
        rec["status"] = "HUMAN_REVIEW_RESOLVED"
        return rec

    def ingest_review(self, case_id, review):
        rec = self.cases[case_id]
        ok, why = validate_review(rec["packet"], review)
        if not ok:
            rec["status"] = "HUMAN_REVIEW_INVALID"
            rec["provenance"].append({
                "event": "REVIEW_REJECTED", "utc": _now(), "reason": why,
                "reviewer_id": str(review.get("reviewer_id", "")) if isinstance(review, dict) else ""})
            rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_INVALID", "utc": _now()})
            return rec
        if any(r["reviewer_id"] == review["reviewer_id"] for r in rec["reviews"]):
            rec["duplicate_reviews"].append({"reviewer_id": review["reviewer_id"], "utc": _now(),
                                             "action": "REJECTED_DUPLICATE"})
            rec["provenance"].append({
                "event": "DUPLICATE_REVIEW_REJECTED", "utc": _now(), "reviewer_id": review["reviewer_id"]})
            return rec
        if rec["reviews"]:  # dual blind mode
            first = rec["reviews"][0]["judgment"]
            if _sig(first) == _sig(review["judgment"]):
                rec["reviews"].append(review)
                return self._resolve(rec, review["judgment"], "DUAL_BLIND_REVIEW_AGREED",
                                     "DUAL_REVIEW_ACCEPTED", review["reviewer_id"])
            rec["reviews"].append(review)
            rec["review_mode"] = None
            rec["final"] = None
            rec["status"] = "HUMAN_REVIEW_DISAGREEMENT"
            rec["provenance"].append({
                "event": "DUAL_REVIEW_DISAGREEMENT", "utc": _now(),
                "reviewer_a": rec["reviews"][0]["reviewer_id"], "reviewer_b": review["reviewer_id"]})
            rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_DISAGREEMENT", "utc": _now()})
            return rec
        rec["reviews"].append(review)
        return self._resolve(rec, review["judgment"], "SINGLE_HUMAN_REVIEW", "REVIEW_ACCEPTED",
                             review["reviewer_id"])

    def adjudicate(self, case_id, record):
        rec = self.cases[case_id]
        if rec["status"] != "HUMAN_REVIEW_DISAGREEMENT":
            raise LaneError("adjudication only allowed from HUMAN_REVIEW_DISAGREEMENT")
        ok, why = validate_adjudication(record)
        if not ok:
            raise LaneError("adjudication invalid: " + why)
        err = _validate_judgment(rec["packet"]["dimension"], record["final_judgment"])
        if err:
            raise LaneError("adjudication judgment: " + err)
        rec["adjudication"] = record
        return self._resolve(rec, record["final_judgment"], "DUAL_BLIND_REVIEW_WITH_ADJUDICATION",
                             "ADJUDICATION_APPLIED", "ADJUDICATOR")


def report_buckets(lane):
    buckets = {"human_reviewed": 0, "unresolved": 0}
    for rec in lane.cases.values():
        if rec["status"] == "HUMAN_REVIEW_RESOLVED":
            buckets["human_reviewed"] += 1
        else:
            buckets["unresolved"] += 1
    return buckets
