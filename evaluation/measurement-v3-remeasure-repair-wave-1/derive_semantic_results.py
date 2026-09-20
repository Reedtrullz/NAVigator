#!/usr/bin/env python3
"""Section 21: mechanical derivation of the 92 semantic criteria.

Frozen judge_core_v2_13.derive_final only; no LLM calls.
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")
CORE_PATH = os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist",
                         "judge_core_v2_13.py")
CORE_SHA = "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682"
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    actual = sha(CORE_PATH)
    if actual != CORE_SHA:
        raise SystemExit("DERIVATION_CORE_SHA_DRIFT: " + actual)
    spec = importlib.util.spec_from_file_location("judge_core_v2_13", CORE_PATH)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)

    freeze_sha = sha(os.path.join(HERE, "semantic-review-freeze-manifest.json"))
    packets = {json.loads(l)["packet_id"]: json.loads(l)
               for l in open(os.path.join(HERE, "semantic-review-packets.jsonl"),
                             encoding="utf-8") if l.strip()}
    raw_a, raw_b = {}, {}
    for name, acc in (("astra-pass-a.jsonl", raw_a),
                      ("astra-pass-b.jsonl", raw_b)):
        for l in open(os.path.join(HERE, name), encoding="utf-8"):
            if l.strip():
                rec = json.loads(l)
                acc[rec["packet_id"]] = l.rstrip("\n")
    consensus = json.load(open(os.path.join(HERE, "primary-consensus.json"),
                               encoding="utf-8"))
    residual = json.load(open(os.path.join(HERE, "residual-consensus.json"),
                              encoding="utf-8"))
    batch = json.load(open(os.path.join(HERE, "human-review-batch-manifest.json"),
                           encoding="utf-8"))
    meta = {h["packet_id"]: h for h in batch["packet_hashes"]}

    derived, pending = [], []
    for p in consensus["packets"]:
        if p["consensus_status"] != "LLM_CONSENSUS":
            continue
        pid = p["packet_id"]
        fields = p["astra_a"]["authoritative_fields"]
        verdict, basis = core.derive_final(p["dimension"], fields)
        derived.append({
            "criterion_id": meta[pid]["criterion_id"],
            "case_id": meta[pid]["case_id"],
            "dimension": p["dimension"], "packet_id": pid,
            "packet_sha256": p["packet_sha256"],
            "authority_class": "LLM_REVIEWED",
            "observation_source": "ASTRA_WAVE1_DUAL_PASS_CONSENSUS",
            "observation_model": "gpt-6-astra", "reasoning_effort": "low",
            "observation_fields": fields,
            "observation_record_shas": {
                "astra_a": hashlib.sha256(raw_a[pid].encode("utf-8")).hexdigest(),
                "astra_b": hashlib.sha256(raw_b[pid].encode("utf-8")).hexdigest()},
            "evidence_spans": p["astra_a"]["evidence_spans"],
            "derived_verdict": verdict,
            "derivation_rule": "judge_core_v2_13.derive_final",
            "derivation_core_sha256": CORE_SHA,
            "derivation_basis": basis, "status": "SCORED"})
    for p in residual["packets"]:
        if p["consensus_status"] != "HUMAN_ADJUDICATION_REQUIRED":
            continue
        pid = p["packet_id"]
        pending.append({
            "criterion_id": meta[pid]["criterion_id"],
            "case_id": meta[pid]["case_id"],
            "dimension": p["dimension"], "packet_id": pid,
            "packet_sha256": None,
            "authority_class": "PENDING_HUMAN_ADJUDICATION",
            "observation_source": "RESIDUAL_ADJUDICATION_NO_CONSENSUS",
            "observation_model": "gpt-6-astra", "reasoning_effort": "low",
            "pending_reason": p.get("reason"),
            "derived_verdict": None,
            "status": "HUMAN_ADJUDICATION_PENDING"})
    assert len(derived) == 88 and len(pending) == 4, (len(derived), len(pending))

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
           "derived_count": len(derived), "pending_count": len(pending),
           "derived_rows": derived, "pending_rows": pending}
    with open(os.path.join(HERE, "derived-measurement-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"derived": len(derived), "pending": len(pending),
                      "llm_calls": 0}, indent=1))


if __name__ == "__main__":
    main()
