#!/usr/bin/env python3
"""Primary ASTRA A/B validation and consensus per frozen spec sections 13-16."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CRIT_STATES = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT",
               "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED"}
MATCH_ENUM = {"MATCH", "NO_MATCH", "UNRESOLVED"}
COMMIT_ENUM = {"ASSERTED", "HEDGED_ASSERTION", "QUOTED_ONLY", "HYPOTHETICAL_ONLY",
               "NEGATED", "SELF_RETRACTED", "NONCOMMITTAL", "UNRESOLVED"}
REQ_CRIT = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(fname):
    path = os.path.join(HERE, fname)
    return {json.loads(l)["packet_id"]: json.loads(l)
            for l in open(path, encoding="utf-8") if l.strip()}


def validate(rec, sut):
    if rec.get("status") == "TRANSPORT_ERROR":
        return "TRANSPORT_ERROR"
    if rec.get("status") == "INVALID_JSON":
        return "INVALID_JSON"
    res = rec.get("result", {})
    spans = res.get("evidence_spans", [])
    if "critical_evidence_state" in res:
        if res.get("critical_evidence_state") not in CRIT_STATES:
            return "INVALID_ENUM"
        need = res["critical_evidence_state"] in REQ_CRIT
    elif "criterion_semantic_match" in res:
        if (res.get("criterion_semantic_match") not in MATCH_ENUM
                or res.get("speaker_commitment") not in COMMIT_ENUM):
            return "INVALID_ENUM"
        need = (res.get("criterion_semantic_match") == "MATCH"
                and res.get("speaker_commitment") != "UNRESOLVED")
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
    a, b = load("astra-pass-a.jsonl"), load("astra-pass-b.jsonl")
    manifest = json.load(open(os.path.join(HERE, "semantic-review-packet-manifest.json"),
                              encoding="utf-8"))
    order = [h["packet_id"] for h in manifest["packet_hashes"]]
    assert set(a) == set(b) == set(packets) == set(order), "coverage mismatch"

    evidence = {"artifact": "primary-evidence-validation", "passes_checked": len(order) * 2,
                "violations": [], "legal_empty_span_cases": 0}
    entries, residual, counts = [], [], {
        "packets_total": len(order), "valid_astra_a": 0, "valid_astra_b": 0,
        "invalid_pass_packets": 0, "llm_consensus": 0, "disagreement": 0,
        "by_lane": {}}

    for pid in order:
        p = packets[pid]
        ra, rb = a[pid], b[pid]
        va, vb = validate(ra, p["sut_output"]), validate(rb, p["sut_output"])
        if va == "OK":
            counts["valid_astra_a"] += 1
        if vb == "OK":
            counts["valid_astra_b"] += 1
        fa, fb = auth_fields(ra.get("result", {})), auth_fields(rb.get("result", {}))
        entry = {"packet_id": pid, "dimension": p["dimension"],
                 "packet_sha256": p["packet_sha256"],
                 "astra_a": {"validity": va, "authoritative_fields": fa,
                             "evidence_spans": ra.get("result", {}).get("evidence_spans", [])},
                 "astra_b": {"validity": vb, "authoritative_fields": fb,
                             "evidence_spans": rb.get("result", {}).get("evidence_spans", [])}}
        lane = counts["by_lane"].setdefault(
            p["dimension"], {"invalid": 0, "disagreement": 0, "llm_consensus": 0})
        if va != "OK" or vb != "OK":
            entry["consensus_status"] = "INVALID_MODEL_REVIEW"
            entry["invalid_passes"] = [s for s, v in (("ASTRA_A", va), ("ASTRA_B", vb)) if v != "OK"]
            counts["invalid_pass_packets"] += 1
            lane["invalid"] += 1
            residual.append({"packet_id": pid, "reason": "INVALID_MODEL_REVIEW",
                             "invalid_passes": entry["invalid_passes"]})
        elif fa == fb:
            entry["consensus_status"] = "LLM_CONSENSUS"
            entry["authority_class"] = "LLM_REVIEWED"
            counts["llm_consensus"] += 1
            lane["llm_consensus"] += 1
        else:
            entry["consensus_status"] = "LLM_REVIEW_DISAGREEMENT"
            entry["differing_fields"] = [k for k in fa if fa[k] != fb.get(k)]
            counts["disagreement"] += 1
            lane["disagreement"] += 1
            residual.append({"packet_id": pid, "reason": "LLM_REVIEW_DISAGREEMENT",
                             "differing_fields": entry["differing_fields"]})
        entries.append(entry)

    counts["residual_total"] = len(residual)

    def dump(name, obj):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")

    dump("primary-review-validation.json", {
        "artifact": "primary-review-validation",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "passes_checked": counts["packets_total"] * 2,
        "valid_astra_a": counts["valid_astra_a"], "valid_astra_b": counts["valid_astra_b"],
        "invalid_records": [
            {"packet_id": rec["packet_id"], "pass": rec.get("pass", ""),
             "stored_status": rec.get("status"),
             "canonical_validity": validate(rec, packets[rec["packet_id"]]["sut_output"])}
            for rec in sorted(list(a.values()) + list(b.values()),
                              key=lambda r: (r["packet_id"], r.get("pass", "")))
            if rec.get("status") != "OK"
            or validate(rec, packets[rec["packet_id"]]["sut_output"]) != "OK"],
        "evidence": evidence})
    dump("primary-consensus.json", {
        "artifact": "primary-consensus",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "summary": counts, "packets": entries,
        "residual_ids": [r["packet_id"] for r in residual],
        "residual_reasons": residual})
    dump("residual-inputs.json", {
        "artifact": "residual-adjudication-inputs",
        "built_from": "semantic-review-packets.jsonl (frozen packet bodies only)",
        "excluded_fields": ["primary A/B results", "disagreement reasons", "gold",
                            "prior baseline", "prior Astra results"],
        "residual_ids": [r["packet_id"] for r in residual],
        "packets": [{k: p[k] for k in ("packet_id", "case_id", "case_context", "criterion",
                                       "dimension", "contract_version", "reviewer_instructions",
                                       "sut_output", "packet_sha256")}
                    for pid in [r["packet_id"] for r in residual]
                    for p in [packets[pid]]]})
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
