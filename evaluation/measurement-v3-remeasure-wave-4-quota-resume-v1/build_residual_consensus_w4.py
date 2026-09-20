#!/usr/bin/env python3
"""Wave-4 quota-residual SOL validation and consensus.

Imports the frozen Wave-3 comparator module for byte-identical validation
and consensus semantics; paths point at this resume lineage."""
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
    "frozen_residual_consensus",
    os.path.join(REPO, "evaluation", "measurement-v3-remeasure-repair-wave-3",
                 "build_residual_consensus.py"))
_resc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_resc)
validate = _resc.validate
auth_fields = _resc.auth_fields


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_local(fname):
    path = os.path.join(HERE, fname)
    return {json.loads(l)["packet_id"]: json.loads(l)
            for l in open(path, encoding="utf-8") if l.strip()}


def main():
    packets = {json.loads(l)["packet_id"]: json.loads(l)
               for l in open(PACKETS_FILE, encoding="utf-8") if l.strip()}
    a, b = load_local("sol-pass-a.jsonl"), load_local("sol-pass-b.jsonl")
    residual = json.load(open(os.path.join(HERE, "residual-inputs.json"),
                              encoding="utf-8"))["residual_ids"]
    assert set(a) == set(b) == set(residual), "adjudication coverage mismatch"

    validation = {"artifact": "residual-validation", "task_id": TASK_ID,
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
        return sha_file(os.path.join(HERE, name))

    valid_sha = dump("residual-validation.json", dict(validation, result=
                     "PASS" if not validation["invalid"] and
                     validation["reasoning_effort_low_violations"] == 0 and
                     validation["packet_sha_binding_mismatches"] == 0 else "PARTIAL"))
    cons_sha = dump("residual-consensus.json", {
        "artifact": "residual-consensus", "task_id": TASK_ID,
        "summary": counts, "packets": cons + pending,
        "pending_ids": [e["packet_id"] for e in pending]})
    manifest = {
        "artifact": "semantic-review-freeze-manifest", "task_id": TASK_ID,
        "frozen_before_derivation": True,
        "inputs": {
            "evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1/quota-resume-semantic-packets.jsonl":
                sha_file(PACKETS_FILE),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-pass-a.jsonl":
                sha_file(os.path.join(HERE, "astra-pass-a.jsonl")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-pass-b.jsonl":
                sha_file(os.path.join(HERE, "astra-pass-b.jsonl")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/sol-pass-a.jsonl":
                sha_file(os.path.join(HERE, "sol-pass-a.jsonl")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/sol-pass-b.jsonl":
                sha_file(os.path.join(HERE, "sol-pass-b.jsonl"))},
        "artifacts": {
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/astra-validation.json": sha_file(os.path.join(HERE, "astra-validation.json")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/primary-consensus.json": sha_file(os.path.join(HERE, "primary-consensus.json")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/residual-inputs.json": sha_file(os.path.join(HERE, "residual-inputs.json")),
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/residual-validation.json": valid_sha,
            "evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1/residual-consensus.json": cons_sha},
        "summary": counts}
    with open(os.path.join(HERE, "semantic-review-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
