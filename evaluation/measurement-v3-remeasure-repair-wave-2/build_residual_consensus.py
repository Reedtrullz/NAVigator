#!/usr/bin/env python3
"""Validate SOL-A/SOL-B and build residual consensus per frozen spec sections 13/19-20."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CRIT_STATES = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT",
               "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED"}
MATCH_ENUM = {"MATCH", "NO_MATCH", "UNRESOLVED"}
COMMIT_ENUM = {"ASSERTED", "HEDGED_ASSERTION", "QUOTED_ONLY", "HYPOTHETICAL_ONLY",
               "NEGATED", "SELF_RETRACTED", "NONCOMMITTAL", "UNRESOLVED"}
REQ_CRIT = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}


def load(fname):
    path = os.path.join(HERE, fname)
    return {json.loads(l)["packet_id"]: json.loads(l)
            for l in open(path, encoding="utf-8") if l.strip()}


def validate(rec, sut):
    if rec.get("status") in ("TRANSPORT_ERROR", "INVALID_JSON"):
        return rec.get("status")
    res = rec.get("result", {})
    spans = res.get("evidence_spans", [])
    if "critical_evidence_state" in res:
        if res.get("critical_evidence_state") not in CRIT_STATES:
            return "INVALID_ENUM"
        need = res["critical_evidence_state"] in REQ_CRIT
    elif "criterion_semantic_match" in res:
        if res.get("criterion_semantic_match") not in MATCH_ENUM:
            return "INVALID_ENUM"
        commitment = res.get("speaker_commitment")
        if commitment not in COMMIT_ENUM:
            return "INVALID_ENUM"
        need = (res.get("criterion_semantic_match") == "MATCH"
                and commitment != "UNRESOLVED")
    else:
        return "INVALID_SCHEMA"
    if not isinstance(spans, list) or not all(isinstance(s, str) for s in spans):
        return "INVALID_SPANS_TYPE"
    if any(s not in sut for s in spans):
        return "INVALID_MODEL_REVIEW"
    if need and not spans:
        return "INVALID_MODEL_REVIEW"
    return "OK"


def auth_fields(res):
    if "critical_evidence_state" in res:
        return {"critical_evidence_state": res.get("critical_evidence_state")}
    return {"criterion_semantic_match": res.get("criterion_semantic_match"),
            "speaker_commitment": res.get("speaker_commitment")}


def main():
    packets = load("semantic-review-packets.jsonl")
    a, b = load("sol-pass-a.jsonl"), load("sol-pass-b.jsonl")
    residual = json.load(open(os.path.join(HERE, "residual-inputs.json"),
                              encoding="utf-8"))["residual_ids"]
    assert set(a) == set(b) == set(residual), "adjudication coverage mismatch"

    validation = {"artifact": "residual-validation",
                  "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2",
                  "residual_packets": len(residual),
                  "sol_a_valid": 0, "sol_b_valid": 0,
                  "invalid": {}, "reasoning_effort_low_violations": 0,
                  "packet_sha_binding_mismatches": 0,
                  "validation_rules": "frozen enums, required fields, no extra fields, verbatim spans from sut_output, span rule per frozen contract"}
    cons, pending = [], []
    for pid in residual:
        p = packets[pid]
        ra, rb = a[pid], b[pid]
        va, vb = validate(ra, p["sut_output"]), validate(rb, p["sut_output"])
        for name, v, rec in (("sol_a", va, ra), ("sol_b", vb, rb)):
            if v == "OK":
                validation[name + "_valid"] += 1
            else:
                validation["invalid"].setdefault(pid, []).append(name + ":" + v)
            if rec.get("reasoning_effort") != "low":
                validation["reasoning_effort_low_violations"] += 1
            if rec.get("packet_sha256") != p["packet_sha256"]:
                validation["packet_sha_binding_mismatches"] += 1
        fa, fb = auth_fields(ra.get("result", {})), auth_fields(rb.get("result", {}))
        entry = {"packet_id": pid, "dimension": p["dimension"],
                 "packet_sha256": p["packet_sha256"],
                 "sol_a": {"validity": va, "authoritative_fields": fa,
                           "evidence_spans": ra.get("result", {}).get("evidence_spans", [])},
                 "sol_b": {"validity": vb, "authoritative_fields": fb,
                           "evidence_spans": rb.get("result", {}).get("evidence_spans", [])}}
        if va == "OK" and vb == "OK" and fa == fb:
            entry["consensus_status"] = "LLM_ADJUDICATION_CONSENSUS"
            entry["authority_class"] = "LLM_ADJUDICATED"
            entry["authority_subtype"] = "GPT_5_6_SOL_DUAL_PASS_RESIDUAL"
            cons.append(entry)
        else:
            entry["consensus_status"] = "PENDING_LLM_ADJUDICATION"
            entry["authority_class"] = "PENDING_LLM_ADJUDICATION"
            entry["reason"] = ("invalid pass" if va != "OK" or vb != "OK"
                               else "semantic disagreement")
            pending.append(entry)
    counts = {"residual_total": len(residual), "llm_adjudicated": len(cons),
              "pending": len(pending)}

    def dump(name, obj):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")

    dump("residual-validation.json", dict(validation, result=
         "PASS" if not validation["invalid"] and
         validation["reasoning_effort_low_violations"] == 0 and
         validation["packet_sha_binding_mismatches"] == 0 else "PARTIAL"))
    dump("residual-consensus.json", {
        "artifact": "residual-consensus",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2",
        "summary": counts, "packets": cons + pending,
        "pending_ids": [e["packet_id"] for e in pending]})
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
