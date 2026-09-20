#!/usr/bin/env python3
"""Section 17: terminal complete Wave-4 measurement freeze BEFORE the
deferred comparisons. Hashes every measurement, review, and resume
artifact; the comparison phase only reads these frozen files.
"""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"
FILES = ["TASK-LOCK.json", "input-integrity.json",
         "resume-source-manifest.json", "astra-config.json",
         "astra-pass-a.jsonl", "astra-pass-b.jsonl",
         "astra-validation.json", "primary-consensus.json",
         "primary-review-freeze-manifest.json", "sol-config.json",
         "sol-pass-a.jsonl", "sol-pass-b.jsonl", "sol-transport-log.json",
         "sol-validation.json", "residual-validation.json",
         "residual-consensus.json", "semantic-review-freeze-manifest.json",
         "derived-measurement-results.json", "derived-resume-results.json",
         "completed-wave4-measurement-results.json",
         "completed-wave4-aggregate-metrics.json", "merge-invariants.json"]


def main():
    results = json.load(open(os.path.join(
        HERE, "completed-wave4-measurement-results.json"), encoding="utf-8"))
    manifest = {
        "artifact": "completed-wave4-measurement-freeze-manifest",
        "task_id": TASK_ID,
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_order": "MEASUREMENT_FROZEN_BEFORE_DEFERRED_COMPARISONS",
        "coverage_at_freeze": results["coverage"],
        "verdict_counts_at_freeze": results["verdict_counts"],
        "semantic_review_freeze_manifest_sha256":
            results["semantic_review_freeze_manifest_sha256"],
        "derivation": results["derivation"],
        "artifacts": [{"path": fn,
                       "sha256": hashlib.sha256(open(os.path.join(HERE, fn),
                                                           "rb").read()).hexdigest()}
                      for fn in FILES],
        "authority_mix": {
            "DETERMINISTIC": results["coverage"]["DETERMINISTIC"],
            "REUSED_LLM_ADJUDICATED":
                results["coverage"]["REUSED_LLM_ADJUDICATED"],
            "LLM_REVIEWED": results["coverage"]["LLM_REVIEWED"],
            "LLM_ADJUDICATED": results["coverage"]["LLM_ADJUDICATED"],
            "PENDING_MODEL_REVIEW_QUOTA":
                results["coverage"]["PENDING_MODEL_REVIEW_QUOTA"]},
        "hard_invariants": {
            "SUT_RERUN": False, "MEASUREMENT_CHANGED": False,
            "GOLD_CHANGED": False, "CORPUS_CHANGED": False,
            "PACKETS_REGENERATED": False,
            "QUOTA_SAFE_FREEZE_MUTATED": False,
            "NO_CONSENSUS_HUNTING": True,
            "FRESH_CASES_CONSUMED": 0}}
    with open(os.path.join(HERE,
                           "completed-wave4-measurement-freeze-manifest.json"),
              "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for art in manifest["artifacts"]:
            f.write("%s  %s\n" % (art["sha256"], art["path"]))
    print(json.dumps({"frozen_files": len(FILES),
                      "coverage": results["coverage"]}, indent=1))


if __name__ == "__main__":
    main()
