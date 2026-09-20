#!/usr/bin/env python3
"""Section 21: freeze all semantic observations before gold derivation."""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3"
CORE_SHA = "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682"


def sha(path):
    return hashlib.sha256(open(os.path.join(HERE, path), "rb").read()).hexdigest()


def main():
    consensus = json.load(open(os.path.join(HERE, "primary-consensus.json"),
                               encoding="utf-8"))
    residual = json.load(open(os.path.join(HERE, "residual-consensus.json"),
                              encoding="utf-8"))
    det = json.load(open(os.path.join(HERE, "deterministic-results.json"),
                         encoding="utf-8"))

    llm_reviewed = [p for p in consensus["packets"]
                    if p["consensus_status"] == "LLM_CONSENSUS"]
    adjudicated = [p for p in residual["packets"]
                   if p["consensus_status"] == "LLM_ADJUDICATION_CONSENSUS"]
    pending = [p for p in residual["packets"]
               if p["consensus_status"] == "PENDING_LLM_ADJUDICATION"]
    by_packet = {p["packet_id"]: ("LLM_REVIEWED" if p in llm_reviewed else
                                  "LLM_ADJUDICATED" if p in adjudicated else
                                  "PENDING_LLM_ADJUDICATION")
                 for p in llm_reviewed + residual["packets"]}

    rows, counts = [], {"DETERMINISTIC": 0, "LLM_REVIEWED": 0,
                        "LLM_ADJUDICATED": 0,
                        "PENDING_LLM_ADJUDICATION": 0}
    for case in det["cases"]:
        for row in case["criteria"]:
            cls = (by_packet[row["packet_id"]] if row.get("packet_id")
                   else "DETERMINISTIC")
            counts[cls] += 1
            rows.append({"case_id": row["case_id"],
                         "criterion_id": row["criterion_id"],
                         "packet_id": row.get("packet_id"),
                         "authority_class": cls})
    assert len(rows) == 600, len(rows)

    authority_map = {
        "artifact": "authority-map", "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_criteria": 600, "authority_distribution": counts,
        "unmapped_pending_count": 0, "rows": rows}
    with open(os.path.join(HERE, "authority-map.json"), "w",
              encoding="utf-8") as f:
        json.dump(authority_map, f, indent=2, ensure_ascii=False)
        f.write("\n")

    files = ["astra-pass-a.jsonl", "astra-pass-b.jsonl",
             "primary-review-validation.json", "primary-consensus.json",
             "residual-inputs.json", "sol-pass-a.jsonl",
             "sol-pass-b.jsonl", "sol-transport-log.json",
             "residual-validation.json", "residual-consensus.json",
             "astra-config.json", "astra-transport-log.jsonl",
             "sol-config.json", "semantic-review-inputs-freeze-manifest.json",
             "authority-map.json"]
    manifest = {
        "artifact": "semantic-review-freeze-manifest", "task_id": TASK_ID,
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_order": "SEMANTIC_OBSERVATIONS_FROZEN_BEFORE_GOLD_DERIVATION",
        "purpose": "Section 21: prevent downstream gold/result knowledge from "
                   "altering review observations",
        "artifacts": [{"path": fn, "sha256": sha(fn)} for fn in files],
        "accepted_primary_observations": len(llm_reviewed),
        "accepted_adjudication_observations": len(adjudicated),
        "pending_residual_list": [p["packet_id"] for p in pending],
        "authority_distribution": counts,
        "transport_provenance": {
            "primary_transport_failures": 0,
            "adjudication_transport_failures": 0,
            "primary_model": "gpt-6-astra", "primary_reasoning_effort": "low",
            "residual_model": "gpt-5.6-sol",
            "residual_reasoning_effort": "low"},
        "derivation_core": {"module": "judge_core_v2_13.py",
                            "sha256": CORE_SHA,
                            "state": "FROZEN_UNMODIFIED"},
        "counts_at_freeze": {"llm_reviewed": len(llm_reviewed),
                             "llm_adjudicated": len(adjudicated),
                             "pending": len(pending)}}
    with open(os.path.join(HERE, "semantic-review-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"authority_distribution": counts,
                      "frozen_files": len(files)}, indent=1))


if __name__ == "__main__":
    main()
