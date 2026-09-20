#!/usr/bin/env python3
"""Section 23: terminal Wave-3 measurement freeze BEFORE baseline comparison."""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3"
FILES = ["TASK-LOCK.json", "input-integrity.json", "measurement-routing.json",
         "deterministic-results.json", "semantic-review-packets.jsonl",
         "semantic-review-packet-manifest.json",
         "semantic-review-leakage-audit.json",
         "semantic-reviewability-audit.json", "astra-config.json",
         "astra-pass-a.jsonl", "astra-pass-b.jsonl",
         "astra-transport-log.jsonl", "primary-review-validation.json",
         "primary-consensus.json", "residual-inputs.json",
         "residual-leakage-audit.json", "sol-config.json",
         "sol-pass-a.jsonl", "sol-pass-b.jsonl", "sol-transport-log.json",
         "residual-validation.json", "residual-consensus.json",
         "semantic-review-freeze-manifest.json",
         "derived-measurement-results.json",
         "wave3-combined-measurement-results.json",
         "wave3-aggregate-metrics.json"]


def main():
    results = json.load(open(os.path.join(HERE, "wave3-combined-measurement-results.json"),
                             encoding="utf-8"))
    manifest = {
        "artifact": "wave3-measurement-freeze-manifest", "task_id": TASK_ID,
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_order": "MEASUREMENT_FROZEN_BEFORE_OLD_BASELINE_COMPARISON",
        "coverage_at_freeze": results["coverage"],
        "verdict_counts_at_freeze": results["verdict_counts"],
        "pending_set": sorted(
            c["criterion_id"] for case in results["cases"]
            for c in case["criteria"]
            if c["status"] == "LLM_ADJUDICATION_PENDING"),
        "semantic_review_freeze_manifest_sha256":
            results["semantic_review_freeze_manifest_sha256"],
        "artifacts": [{"path": fn,
                       "sha256": hashlib.sha256(
                           open(os.path.join(HERE, fn), "rb").read()).hexdigest()}
                      for fn in FILES],
        "authority_mix": {
            "DETERMINISTIC": results["coverage"]["DETERMINISTIC"],
            "LLM_REVIEWED": results["coverage"]["LLM_REVIEWED"],
            "LLM_ADJUDICATED": results["coverage"]["LLM_ADJUDICATED"],
            "HUMAN_REVIEWED": results["coverage"]["HUMAN_REVIEWED"],
            "PENDING_LLM_ADJUDICATION":
                results["coverage"]["PENDING_LLM_ADJUDICATION"]},
        "hard_invariants": {
            "SUT_RERUN": False, "MEASUREMENT_CHANGED": False,
            "GOLD_CHANGED": False, "CORPUS_CHANGED": False,
            "OLD_BASELINE_CHANGED": False, "WAVE1_MEASUREMENT_CHANGED": False,
            "TUNING": False}}
    with open(os.path.join(HERE, "wave3-measurement-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for art in manifest["artifacts"]:
            f.write(f"{art['sha256']}  {art['path']}\n")
    print(json.dumps({"frozen_files": len(FILES),
                      "coverage": results["coverage"],
                      "verdict_counts": results["verdict_counts"]}, indent=1))


if __name__ == "__main__":
    main()
