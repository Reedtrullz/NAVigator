#!/usr/bin/env python3
"""Section 23: terminal Wave-1 measurement freeze BEFORE baseline comparison."""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1"
FILES = ["TASK-LOCK.json", "input-integrity.json", "measurement-routing.json",
         "deterministic-results.json", "semantic-review-packets.jsonl",
         "semantic-review-packet-manifest.json",
         "semantic-review-leakage-audit.json",
         "semantic-reviewability-audit.json", "astra-config.json",
         "astra-pass-a.jsonl", "astra-pass-b.jsonl",
         "primary-review-validation.json", "primary-consensus.json",
         "residual-inputs.json", "residual-leakage-audit.json",
         "adjudication-pass-a.jsonl", "adjudication-pass-b.jsonl",
         "adjudication-validation.json", "residual-consensus.json",
         "semantic-review-freeze-manifest.json",
         "derived-measurement-results.json",
         "wave1-combined-measurement-results.json",
         "wave1-aggregate-metrics.json"]


def main():
    results = json.load(open(os.path.join(HERE, "wave1-combined-measurement-results.json"),
                             encoding="utf-8"))
    manifest = {
        "artifact": "wave1-measurement-freeze-manifest", "task_id": TASK_ID,
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_order": "MEASUREMENT_FROZEN_BEFORE_OLD_BASELINE_COMPARISON",
        "coverage_at_freeze": results["coverage"],
        "artifacts": [{"path": fn,
                       "sha256": hashlib.sha256(
                           open(os.path.join(HERE, fn), "rb").read()).hexdigest()}
                      for fn in FILES],
        "authority_mix": {
            "DETERMINISTIC": 508, "LLM_REVIEWED": 88,
            "LLM_ADJUDICATED": 0, "HUMAN_REVIEWED": 0,
            "PENDING_HUMAN_ADJUDICATION": 4},
        "hard_invariants": {
            "SUT_RERUN": False, "MEASUREMENT_CHANGED": False,
            "GOLD_CHANGED": False, "CORPUS_CHANGED": False,
            "OLD_BASELINE_CHANGED": False, "TUNING": False}}
    with open(os.path.join(HERE, "wave1-measurement-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for art in manifest["artifacts"]:
            f.write(f"{art['sha256']}  {art['path']}\n")
    print(json.dumps({"frozen_files": len(FILES),
                      "coverage": results["coverage"]}, indent=1))


if __name__ == "__main__":
    main()
