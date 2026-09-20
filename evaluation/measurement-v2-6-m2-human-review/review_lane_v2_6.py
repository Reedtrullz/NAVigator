"""V2.6 M2 human-review lane runtime.

Authoritative M2 critical-condition judgement is human-only (owner decision 2026-09-13).
This module never issues an automated M2 verdict: the human supplies intermediate
observations; the frozen deterministic derivation table supplies the final label.
No model calls, stdlib only.
"""
import datetime
import hashlib
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_VERSION = "m2-decomposition-v2-5"
FIELDS = ("trigger_support", "non_trigger_support", "evidence_conflict", "evidence_sufficiency")
ENUMS = {
    "trigger_support": ("PRESENT", "ABSENT", "UNRESOLVED"),
    "non_trigger_support": ("PRESENT", "ABSENT", "UNRESOLVED"),
    "evidence_conflict": ("YES", "NO", "UNRESOLVED"),
    "evidence_sufficiency": ("SUFFICIENT", "INSUFFICIENT", "UNRESOLVED"),
}
# Frozen final mapping from V2.5 frozen-semantics-trace (sha 89b67c0b...eb794).
FINAL_MAP = {"CLEAR_TRIGGER_SUPPORT": "TRIGGERED", "CLEAR_NON_TRIGGER_SUPPORT": "NOT_TRIGGERED"}
FORBIDDEN_CASE_KEYS = ("final_gold", "gold", "model_verdict", "automated_verdict", "tag", "expected")


class LaneError(Exception):
    pass


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


with open(os.path.join(DIR, "deterministic-derivation-table.json"), encoding="utf-8") as _f:
    _TABLE = json.load(_f)["rows"]


def derive_state(inter):
    """Exact-match lookup in the frozen 81-row table; unknown -> UNRESOLVED (conservative)."""
    for row in _TABLE:
        if all(row[f] == inter[f] for f in FIELDS):
            return row["derived_state"]
    return "UNRESOLVED"


def final_label(state):
    return FINAL_MAP.get(state, "UNRESOLVED")


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
        "criterion": case["criterion"],
        "case_context": case["case_context"],
        "sut_output": case["sut_output"],
        "source_evidence_spans": list(case.get("source_evidence_spans", [])),
        "created_utc": _now(),
    }
    packet["packet_sha256"] = _sha(json.dumps(packet, sort_keys=True, ensure_ascii=False))
    return packet


def validate_packet(packet):
    if not isinstance(packet, dict):
        return False, "not object"
    if packet.get("contract_version") != CONTRACT_VERSION:
        return False, "contract_version"
    for key in FORBIDDEN_PACKET_KEYS:
        if key in packet:
            return False, "leakage field present: " + key
    for key in ("packet_id", "case_id", "criterion", "case_context", "sut_output", "created_utc", "packet_sha256"):
        if key not in packet:
            return False, "missing " + key
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if packet["packet_sha256"] != _sha(json.dumps(body, sort_keys=True, ensure_ascii=False)):
        return False, "sha mismatch"
    return True, "ok"


FORBIDDEN_PACKET_KEYS = ("final_gold", "gold", "expected", "model_verdict", "automated_verdict", "tag")


def validate_review(packet, review):
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
    for field in FIELDS:
        if judgment.get(field) not in ENUMS[field]:
            return False, "invalid " + field
    spans = judgment.get("evidence_spans")
    if not isinstance(spans, list):
        return False, "evidence_spans not list"
    needs_span = judgment["trigger_support"] == "PRESENT" or judgment["non_trigger_support"] == "PRESENT"
    if needs_span and len(spans) < 1:
        return False, "missing required evidence span"
    if not needs_span and spans:
        return False, "spans only allowed with PRESENT support"
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
    judgment = record.get("final_judgment")
    if not isinstance(judgment, dict):
        return False, "final_judgment not object"
    for field in FIELDS:
        if judgment.get(field) not in ENUMS[field]:
            return False, "invalid " + field
    spans = judgment.get("evidence_spans")
    if not isinstance(spans, list):
        return False, "evidence_spans not list"
    needs_span = judgment["trigger_support"] == "PRESENT" or judgment["non_trigger_support"] == "PRESENT"
    if needs_span and len(spans) < 1:
        return False, "missing required evidence span"
    if not needs_span and spans:
        return False, "spans only allowed with PRESENT support"
    return True, "ok"


class ReviewLane:
    """Per-case workflow state machine. Fail-closed: no final label without valid human labels."""

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
            "dimension": "critical_condition", "automated_authoritative": False})
        rec["status"] = "HUMAN_REVIEW_PENDING"
        rec["provenance"].append({"event": "STATUS", "state": "HUMAN_REVIEW_PENDING", "utc": _now()})
        self.cases[case["case_id"]] = rec
        return rec

    def _resolve(self, rec, judgment, mode, provenance_event, reviewer_id):
        inter = {f: judgment[f] for f in FIELDS}
        state = derive_state(inter)
        final = final_label(state)
        rec["review_mode"] = mode
        rec["final"] = {
            "derived_state": state,
            "final_label": final,
            "derivation": "frozen-derivation-table-exact-match",
            "contract_version": CONTRACT_VERSION,
        }
        rec["provenance"].append({
            "event": provenance_event, "utc": _now(), "reviewer_id": reviewer_id,
            "packet_sha256": rec["packet"]["packet_sha256"], "contract_version": CONTRACT_VERSION,
            "intermediate_labels": inter,
            "evidence_spans": list(judgment["evidence_spans"]),
            "derived_state": state, "final_label": final})
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
        if rec["reviews"]:  # second independent reviewer, dual blind mode
            first = rec["reviews"][0]["judgment"]
            if all(first[f] == review["judgment"][f] for f in FIELDS):
                rec["reviews"].append(review)
                return self._resolve(rec, review["judgment"], "DUAL_BLIND_REVIEW_AGREED", "DUAL_REVIEW_ACCEPTED", review["reviewer_id"])
            rec["reviews"].append(review)
            # Disagreement supersedes the first reviewer's single-review resolution;
            # a stale final label must not survive into the disagreement state.
            rec["review_mode"] = None
            rec["final"] = None
            rec["status"] = "HUMAN_REVIEW_DISAGREEMENT"
            rec["provenance"].append({
                "event": "DUAL_REVIEW_DISAGREEMENT", "utc": _now(),
                "reviewer_a": rec["reviews"][0]["reviewer_id"], "reviewer_b": review["reviewer_id"],
                "field_diffs": [f for f in FIELDS if first[f] != review["judgment"][f]]})
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
    buckets = {"automatically_scored": 0, "human_reviewed": 0, "unresolved": 0, "execution_failed": 0}
    for rec in lane.cases.values():
        if rec["status"] == "HUMAN_REVIEW_RESOLVED":
            buckets["human_reviewed"] += 1
        elif rec["status"] in ("HUMAN_REVIEW_PENDING", "HUMAN_REVIEW_REQUIRED",
                              "HUMAN_REVIEW_INVALID", "HUMAN_REVIEW_DISAGREEMENT"):
            buckets["unresolved"] += 1
    return buckets
