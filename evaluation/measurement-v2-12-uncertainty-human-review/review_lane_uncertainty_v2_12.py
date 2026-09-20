"""V2.12 uncertainty human-review lane runtime.

Authoritative semantic uncertainty judgement is human-only (AFK campaign
Stage 2C, 2026-09-14). The human supplies intermediate observations against
the frozen V2.7E uncertainty contract; uncertainty_derivation_v2_7e.py
(imported unmodified from the frozen lineage) supplies the final verdict
mechanically. No model calls, stdlib only.
"""
import datetime
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(DIR)
sys.path.insert(0, os.path.join(EVAL_DIR, "judge-contract-v2-7e-uncertainty-repair"))
import uncertainty_derivation_v2_7e as DERIV  # frozen module, never edited here

CONTRACT_VERSION = "semantic-judge-contract-v2-7e"
DIMENSION = "uncertainty"
FIELDS = ("uncertainty_requirement_mode", "uncertainty_output_behavior")
MODES = DERIV.BEHAVIORS and ("NONE", "EXPLICIT_LIMITATION", "NON_ASSERTION_CONSTRAINT", "COMPOUND")
FORBIDDEN_CASE_KEYS = ("final_gold", "gold", "model_verdict", "automated_verdict", "tag", "expected", "inter")


class LaneError(Exception):
    pass


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalized(text):
    return "".join(ch for ch in text.lower() if ch.isalnum() or ch.isspace()).strip()


def derive_final(judgment):
    """Mechanical derivation via the frozen V2.7E module. Component spans
    (when present) must be normalized-verbatim in the SUT output."""
    mode = judgment["uncertainty_requirement_mode"]
    behavior = judgment["uncertainty_output_behavior"]
    if mode == "NONE":
        if behavior != "NONE":
            raise LaneError("mode NONE requires behavior NONE (schema-invalid combination)")
        return "NOT_REQUIRED"
    if mode == "COMPOUND":
        comps = judgment.get("compound_components")
        if not isinstance(comps, list) or not comps:
            raise LaneError("COMPOUND requires non-empty compound_components")
        norm = []
        for c in comps:
            if not (isinstance(c, (list, tuple)) and len(c) == 2):
                raise LaneError("component must be [kind, behavior]")
            kind, beh = c
            if kind not in ("EXPRESSION", "NON_ASSERTION"):
                raise LaneError("invalid component kind: " + str(kind))
            if beh not in DERIV.BEHAVIORS:
                raise LaneError("invalid component behavior: " + str(beh))
            norm.append((kind, beh))
        return DERIV.derive_compound(norm)
    if behavior not in DERIV.BEHAVIORS:
        raise LaneError("unknown behavior: " + str(behavior))
    return DERIV.derive(mode, behavior)


def create_packet(case):
    for bad in FORBIDDEN_CASE_KEYS:
        if bad in case:
            raise LaneError("leakage field in case input: " + bad)
    for key in ("case_id", "criterion", "case_context", "sut_output"):
        value = case.get(key)
        if not isinstance(value, str) or not value.strip():
            raise LaneError("packet field missing/empty: " + key)
    packet = {
        "packet_id": "PKT-" + case["case_id"],
        "case_id": case["case_id"],
        "contract_version": CONTRACT_VERSION,
        "dimension": DIMENSION,
        "criterion": case["criterion"],
        "case_context": case["case_context"],
        "sut_output": case["sut_output"],
        "reviewer_instructions": [
            "Classify uncertainty_requirement_mode per V2.7E applicability rule.",
            "Classify uncertainty_output_behavior per V2.7E behavior definitions.",
            "For COMPOUND, list components as [kind, behavior].",
            "Provide verbatim evidence spans from the SUT output when a limitation or prohibited conclusion is expressed; otherwise empty.",
        ],
        "created_utc": _now(),
    }
    packet["packet_sha256"] = _sha(json.dumps(packet, sort_keys=True, ensure_ascii=False))
    return packet


FORBIDDEN_PACKET_KEYS = ("final_gold", "gold", "expected", "model_verdict", "automated_verdict", "tag")


def validate_packet(packet):
    if not isinstance(packet, dict):
        return False, "not object"
    if packet.get("contract_version") != CONTRACT_VERSION:
        return False, "contract_version"
    if packet.get("dimension") != DIMENSION:
        return False, "dimension"
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
    """Structural validation of a human review. Semantics are never machine-
    judged; labels are only checked against the frozen V2.7E enums. Spans
    must be verbatim substrings of the SUT output whenever provided."""
    if not isinstance(review, dict):
        return False, "not object"
    for key in ("packet_id", "case_id", "reviewer_id", "contract_version", "reviewed_utc", "judgment"):
        if key not in review:
            return False, "missing " + key
    if review["packet_id"] != packet["packet_id"]:
        return False, "packet mismatch"
    if review["case_id"] != packet["case_id"]:
        return False, "case mismatch"
    if review["contract_version"] != CONTRACT_VERSION:
        return False, "contract_version"
    judgment = review.get("judgment")
    if not isinstance(judgment, dict):
        return False, "judgment not object"
    mode = judgment.get("uncertainty_requirement_mode")
    behavior = judgment.get("uncertainty_output_behavior")
    if mode not in ("NONE", "EXPLICIT_LIMITATION", "NON_ASSERTION_CONSTRAINT", "COMPOUND"):
        return False, "invalid uncertainty_requirement_mode"
    if mode == "NONE":
        if behavior != "NONE":
            return False, "NON_ASSERTION_CONSTRAINT to NOT_REQUIRED is schema-invalid; same for NONE mode with nonzero behavior"
    else:
        if mode == "COMPOUND":
            comps = judgment.get("compound_components")
            if not isinstance(comps, list) or not comps:
                return False, "COMPOUND requires compound_components"
            for c in comps:
                if not (isinstance(c, (list, tuple)) and len(c) == 2
                        and c[0] in ("EXPRESSION", "NON_ASSERTION")
                        and c[1] in DERIV.BEHAVIORS):
                    return False, "invalid compound component"
        elif behavior not in DERIV.BEHAVIORS:
            return False, "invalid uncertainty_output_behavior"
    spans = judgment.get("evidence_spans")
    if not isinstance(spans, list):
        return False, "evidence_spans not list"
    for span in spans:
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
    if record.get("contract_version") != CONTRACT_VERSION:
        return False, "contract_version"
    try:
        derive_final(record["final_judgment"])
    except LaneError as exc:
        return False, "final_judgment: " + str(exc)
    return True, "ok"


class UncertaintyReviewLane:
    """Per-case workflow state machine. Fail-closed: no final verdict without
    valid human labels. Mechanical derivation only, after valid human input."""

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
            "packet_sha256": packet["packet_sha256"], "contract_version": CONTRACT_VERSION})
        rec["provenance"].append({
            "event": "ROUTED", "route": "HUMAN_REVIEW_REQUIRED", "utc": _now(),
            "dimension": DIMENSION, "automated_authoritative": False})
        rec["status"] = "HUMAN_REVIEW_PENDING"
        rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_PENDING", "utc": _now()})
        self.cases[case["case_id"]] = rec
        return rec

    def _resolve(self, rec, judgment, mode, provenance_event, actor):
        final = derive_final(judgment)
        rec["review_mode"] = mode
        rec["final"] = {
            "final_verdict": final,
            "derivation": "frozen-v2-7e-derivation-module",
            "contract_version": CONTRACT_VERSION,
        }
        rec["provenance"].append({
            "event": provenance_event, "utc": _now(), "actor": actor,
            "packet_sha256": rec["packet"]["packet_sha256"], "contract_version": CONTRACT_VERSION,
            "intermediate_labels": {f: judgment.get(f) for f in FIELDS},
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
            rec["duplicate_reviews"].append({"reviewer_id": review["reviewer_id"], "utc": _now(), "action": "REJECTED_DUPLICATE"})
            rec["provenance"].append({
                "event": "DUPLICATE_REVIEW_REJECTED", "utc": _now(), "reviewer_id": review["reviewer_id"]})
            return rec
        if rec["reviews"]:  # dual blind mode
            first = rec["reviews"][0]["judgment"]
            def _sig(j):
                return (j.get("uncertainty_requirement_mode"),
                        j.get("uncertainty_output_behavior"),
                        tuple(tuple(c) for c in j.get("compound_components") or []))
            if _sig(first) == _sig(review["judgment"]):
                rec["reviews"].append(review)
                return self._resolve(rec, review["judgment"], "DUAL_BLIND_REVIEW_AGREED", "DUAL_REVIEW_ACCEPTED", review["reviewer_id"])
            rec["reviews"].append(review)
            rec["review_mode"] = None
            rec["final"] = None
            rec["status"] = "HUMAN_REVIEW_DISAGREEMENT"
            rec["provenance"].append({
                "event": "DUAL_REVIEW_DISAGREEMENT", "utc": _now(),
                "reviewer_a": rec["reviews"][0]["reviewer_id"], "reviewer_b": review["reviewer_id"],
                "field_diffs": [f for f in FIELDS if first.get(f) != review["judgment"].get(f)]
                + (["compound_components"] if _sig(first)[2] != _sig(review["judgment"])[2] else [])})
            rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_DISAGREEMENT", "utc": _now()})
            return rec
        rec["reviews"].append(review)
        return self._resolve(rec, review["judgment"], "SINGLE_HUMAN_REVIEW", "REVIEW_ACCEPTED", review["reviewer_id"])

    def adjudicate(self, case_id, record):
        rec = self.cases[case_id]
        if rec["status"] != "HUMAN_REVIEW_DISAGREEMENT":
            raise LaneError("adjudication only allowed from HUMAN_REVIEW_DISAGREEMENT")
        ok, why = validate_adjudication(record)
        if not ok:
            raise LaneError("adjudication invalid: " + why)
        rec["adjudication"] = record
        return self._resolve(rec, record["final_judgment"], "DUAL_BLIND_REVIEW_WITH_ADJUDICATION", "ADJUDICATION_APPLIED", "ADJUDICATOR")


def report_buckets(lane):
    buckets = {"human_reviewed": 0, "unresolved": 0}
    for rec in lane.cases.values():
        if rec["status"] == "HUMAN_REVIEW_RESOLVED":
            buckets["human_reviewed"] += 1
        else:
            buckets["unresolved"] += 1
    return buckets
