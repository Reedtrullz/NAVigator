#!/usr/bin/env python3
"""Wave-4 quota-resume mechanical derivation of the 110 pending criteria.

Frozen judge_core_v2_13.derive_final only; LLM_CALLS_DURING_DERIVATION = 0.
Criterion mapping comes from the frozen Wave-4 partial pending rows."""
import hashlib
import importlib.util
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
PACKETS_FILE = os.path.join(SRC, "quota-resume-semantic-packets.jsonl")
PARTIAL = os.path.join(SRC, "wave4-partial-measurement-results.json")
CORE_PATH = os.path.join(REPO, "evaluation",
                         "judge-selection-v2-13-forbidden-route-specialist",
                         "judge_core_v2_13.py")
CORE_SHA = "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682"
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    actual = sha(CORE_PATH)
    if actual != CORE_SHA:
        raise SystemExit("DERIVATION_CORE_SHA_DRIFT: " + actual)
    spec = importlib.util.spec_from_file_location("judge_core_v2_13", CORE_PATH)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)

    packets = {json.loads(l)["packet_id"]: json.loads(l)
               for l in open(PACKETS_FILE, encoding="utf-8") if l.strip()}
    partial = json.load(open(PARTIAL, encoding="utf-8"))
    meta = {}
    for case in partial["cases"]:
        for row in case["criteria"]:
            if row["status"] == "PENDING_MODEL_REVIEW_QUOTA":
                meta[row["packet_id"]] = {"criterion_id": row["criterion_id"],
                                          "case_id": row["case_id"],
                                          "packet_sha256": row["packet_sha256"],
                                          "semantic_input_hash":
                                              row["provenance"]["semantic_input_hash"],
                                          "semantic_input_contract_sha256":
                                              row["provenance"]["semantic_input_contract_sha256"]}
    assert len(meta) == 110 and set(meta) == set(packets), "packet/pending mismatch"

    def load(fname):
        return {json.loads(l)["packet_id"]: l.rstrip("\n")
                for l in open(os.path.join(HERE, fname), encoding="utf-8")
                if l.strip()}

    raw_astra_a, raw_astra_b = load("astra-pass-a.jsonl"), load("astra-pass-b.jsonl")
    raw_sol_a, raw_sol_b = load("sol-pass-a.jsonl"), load("sol-pass-b.jsonl")
    consensus = json.load(open(os.path.join(HERE, "primary-consensus.json"),
                               encoding="utf-8"))
    residual = json.load(open(os.path.join(HERE, "residual-consensus.json"),
                              encoding="utf-8"))
    freeze_sha = sha(os.path.join(HERE, "semantic-review-freeze-manifest.json"))

    derived, pending = [], []
    for p in consensus["packets"]:
        if p["consensus_status"] != "LLM_CONSENSUS":
            continue
        pid = p["packet_id"]
        fields = p["astra_a"]["authoritative_fields"]
        verdict, basis = core.derive_final(p["dimension"], fields)
        m = meta[pid]
        derived.append({
            "criterion_id": m["criterion_id"], "case_id": m["case_id"],
            "dimension": p["dimension"], "packet_id": pid,
            "packet_sha256": p["packet_sha256"],
            "authority_class": "LLM_REVIEWED",
            "observation_source": "ASTRA_WAVE4_RESUME_DUAL_PASS_CONSENSUS",
            "observation_model": "gpt-6-astra", "reasoning_effort": "low",
            "observation_fields": fields,
            "observation_record_shas": {
                "astra_a": hashlib.sha256(raw_astra_a[pid].encode("utf-8")).hexdigest(),
                "astra_b": hashlib.sha256(raw_astra_b[pid].encode("utf-8")).hexdigest()},
            "evidence_spans": p["astra_a"]["evidence_spans"],
            "derived_verdict": verdict,
            "derivation_rule": "judge_core_v2_13.derive_final",
            "derivation_core_sha256": CORE_SHA,
            "derivation_basis": basis, "status": "SCORED"})
    for p in residual["packets"]:
        pid = p["packet_id"]
        if p["consensus_status"] == "LLM_ADJUDICATION_CONSENSUS":
            fields = p["sol_a"]["authoritative_fields"]
            verdict, basis = core.derive_final(p["dimension"], fields)
            m = meta[pid]
            derived.append({
                "criterion_id": m["criterion_id"], "case_id": m["case_id"],
                "dimension": p["dimension"], "packet_id": pid,
                "packet_sha256": p["packet_sha256"],
                "authority_class": "LLM_ADJUDICATED",
                "authority_subtype": "GPT_5_6_SOL_DUAL_PASS_RESIDUAL",
                "observation_source": "SOL_WAVE4_RESIDUAL_DUAL_PASS_CONSENSUS",
                "observation_model": "gpt-5.6-sol", "reasoning_effort": "low",
                "observation_fields": fields,
                "observation_record_shas": {
                    "sol_a": hashlib.sha256(raw_sol_a[pid].encode("utf-8")).hexdigest(),
                    "sol_b": hashlib.sha256(raw_sol_b[pid].encode("utf-8")).hexdigest()},
                "evidence_spans": p["sol_a"]["evidence_spans"],
                "derived_verdict": verdict,
                "derivation_rule": "judge_core_v2_13.derive_final",
                "derivation_core_sha256": CORE_SHA,
                "derivation_basis": basis, "status": "SCORED"})
        else:
            pending.append(pid)
    assert len(derived) == 110 and not pending, (len(derived), pending)
    assert {d["packet_id"] for d in derived} == set(packets)

    out = {"artifact": "derived-measurement-results", "task_id": TASK_ID,
           "derived_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "derivation_rule": {
               "source": "judge_core_v2_13.derive_final (frozen deterministic "
                         "mapper, unmodified)", "core_sha256": CORE_SHA,
               "contracts": {
                   "critical_condition": "semantic-judge-contract-v1-4",
                   "forbidden_claim": "semantic-judge-contract-v1-4",
                   "route_correctness": "semantic-judge-contract-v1-4",
                   "required_uncertainty": "semantic-judge-contract-v2-7e"}},
           "review_freeze_manifest_sha256": freeze_sha,
           "llm_calls_during_derivation": 0,
           "derived_count": len(derived), "pending_count": 0,
           "derived_rows": derived, "pending_rows": []}
    with open(os.path.join(HERE, "derived-measurement-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"derived": len(derived), "pending": 0, "llm_calls": 0},
                     indent=1))


if __name__ == "__main__":
    main()
