#!/usr/bin/env python3
"""Wave-4 quota-resume primary A/B validation and consensus.

Imports the frozen Wave-3 comparator module so validation enums, span
checks, and consensus semantics are byte-identical. Inputs live in this
resume lineage; the frozen Wave-3/Wave-4-safe lineages are never written.
"""
import hashlib
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
PACKETS_FILE = os.path.join(SRC, "quota-resume-semantic-packets.jsonl")
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"

_spec = importlib.util.spec_from_file_location(
    "frozen_primary_consensus",
    os.path.join(REPO, "evaluation", "measurement-v3-remeasure-repair-wave-3",
                 "build_primary_consensus.py"))
_cons = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cons)
validate = _cons.validate
auth_fields = _cons.auth_fields


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_local(fname):
    path = os.path.join(HERE, fname)
    return {json.loads(l)["packet_id"]: json.loads(l)
            for l in open(path, encoding="utf-8") if l.strip()}


def main():
    packets = {json.loads(l)["packet_id"]: json.loads(l)
               for l in open(PACKETS_FILE, encoding="utf-8") if l.strip()}
    order = list(packets)
    a, b = load_local("astra-pass-a.jsonl"), load_local("astra-pass-b.jsonl")
    assert set(a) == set(b) == set(packets), "coverage mismatch"

    violations = []
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
        if va != "OK":
            violations.append({"packet_id": pid, "pass": "ASTRA_A",
                               "stored_status": ra.get("status"),
                               "canonical_validity": va})
        if vb != "OK":
            violations.append({"packet_id": pid, "pass": "ASTRA_B",
                               "stored_status": rb.get("status"),
                               "canonical_validity": vb})
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
        return sha_file(os.path.join(HERE, name))

    validation_sha = dump("astra-validation.json", {
        "artifact": "primary-review-validation",
        "task_id": TASK_ID,
        "passes_checked": counts["packets_total"] * 2,
        "valid_astra_a": counts["valid_astra_a"], "valid_astra_b": counts["valid_astra_b"],
        "invalid_records": violations,
        "note": "validation-only artifact; authoritative fields live in primary-consensus.json"})
    consensus_sha = dump("primary-consensus.json", {
        "artifact": "primary-consensus",
        "task_id": TASK_ID,
        "summary": counts, "packets": entries,
        "residual_ids": [r["packet_id"] for r in residual],
        "residual_reasons": residual})
    residual_sha = dump("residual-inputs.json", {
        "artifact": "residual-adjudication-inputs",
        "task_id": TASK_ID,
        "built_from": "quota-resume-semantic-packets.jsonl (frozen packet bodies only)",
        "excluded_fields": ["primary A/B results", "disagreement reasons", "gold",
                            "prior baseline", "prior Astra results"],
        "residual_ids": [r["packet_id"] for r in residual],
        "packets": [{k: p[k] for k in ("packet_id", "case_id", "case_context", "criterion",
                                       "dimension", "contract_version", "reviewer_instructions",
                                       "sut_output", "packet_sha256")}
                    for pid in [r["packet_id"] for r in residual]
                    for p in [packets[pid]]]})
    manifest = {
        "artifact": "primary-review-freeze-manifest",
        "task_id": TASK_ID,
        "frozen_before_residual_adjudication": True,
        "inputs": {
            "evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1/quota-resume-semantic-packets.jsonl":
                sha_file(PACKETS_FILE),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-pass-a.jsonl":
                sha_file(os.path.join(HERE, "astra-pass-a.jsonl")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-pass-b.jsonl":
                sha_file(os.path.join(HERE, "astra-pass-b.jsonl"))},
        "artifacts": {
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-validation.json": validation_sha,
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/primary-consensus.json": consensus_sha,
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/residual-inputs.json": residual_sha},
        "summary": counts}
    with open(os.path.join(HERE, "primary-review-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
