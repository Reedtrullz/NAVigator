#!/usr/bin/env python3
"""Freeze TASK-LOCK.json, write hashes.txt, and verify every pin."""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1"
TERMINAL = "MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    artifacts = sorted(
        f for f in os.listdir(HERE)
        if os.path.isfile(os.path.join(HERE, f))
        and f not in ("TASK-LOCK.json", "hashes.txt")
        and not f.endswith(".pyc"))
    hashes = {name: sha(os.path.join(HERE, name)) for name in artifacts}
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for name, digest in hashes.items():
            f.write(digest + " " + name + chr(10))

    manifest = json.load(open(os.path.join(
        HERE, "comparator-repair-freeze-manifest.json"), encoding="utf-8"))
    input_integrity = json.load(open(os.path.join(
        HERE, "input-integrity.json"), encoding="utf-8"))

    lock = {
        "task_id": TASK_ID,
        "task_family": "measurement-v3",
        "status": "CLOSED",
        "terminal_status": TERMINAL,
        "classification": "BURNED_DEV_BASELINE_ONLY",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "branch": "A_CONSENSUS_COMPARATOR_IMPLEMENTATION_DEFECT",
        "measurement_contract_changed": False,
        "new_llm_calls": 0,
        "semantic_observations_changed": False,
        "sut_rerun": False,
        "predictions_changed": False,
        "gold_changed": False,
        "upstream_lineage_untouched": True,
        "comparator_replay": {
            "packets": 4,
            "corrected_rule_consensus": 4,
            "whole_object_consensus": 0,
            "derived_verdicts": {
                "PKT-ESC-DIS-118": "PRESENT",
                "PKT-ESC-ROUT-026-F01": "ABSENT",
                "PKT-ESC-ROUT-031-F01": "ABSENT",
                "PKT-ESC-ROUT-037": "ABSENT",
            },
        },
        "final_authority_mix": {
            "TOTAL": 600,
            "DETERMINISTIC": 508,
            "LLM_REVIEWED": 88,
            "LLM_ADJUDICATED": 4,
            "HUMAN_REVIEWED": 0,
            "PENDING": 0,
        },
        "terminal_aggregates": {
            "HARD_FAIL_RATE_AUTHORITATIVE": 0.415,
            "NON_PASS_RATE_AUTHORITATIVE": 0.5068,
            "APPLICABLE_DENOMINATOR": 588,
            "PASS": 290,
            "FAIL": 244,
            "UNRESOLVED": 18,
            "DEGRADED": 36,
            "ABSENT_OR_NOT_APPLICABLE": 12,
        },
        "hashes_txt_sha256": sha(os.path.join(HERE, "hashes.txt")),
        "comparator_repair_freeze_manifest_sha256": sha(os.path.join(
            HERE, "comparator-repair-freeze-manifest.json")),
        "input_integrity_all_checks_pass": input_integrity["all_checks_pass"],
        "freeze_manifest_all_pins_verified": all(
            sha(os.path.join(HERE, name)) == pin["sha256"]
            for name, pin in manifest["pins"].items()),
        "terminal_manifest_sha256": sha(os.path.join(
            HERE, "complete-wave1-measurement-results.json")),
        "terminal_manifest_sha256_subject":
            "complete-wave1-measurement-results.json",
        "lock_self_sha256_note": (
            "recorded externally in the session report; a lock cannot contain "
            "its own hash"),
        "hard_stop": [
            "no new LLM reviews", "no human reviews", "no SUT changes",
            "no RC-04/05/06 implementation", "no fresh holdout", "no deploy",
            "next owner decision uses the complete frozen Wave-1 delta",
        ],
    }

    with open(os.path.join(HERE, "TASK-LOCK.json"), "w",
              encoding="utf-8") as f:
        json.dump(lock, f, indent=2, ensure_ascii=False)
        f.write(chr(10))

    verify = {}
    with open(os.path.join(HERE, "hashes.txt"), encoding="utf-8") as f:
        for line in f:
            digest, name = line.split()
            verify[name] = sha(os.path.join(HERE, name)) == digest
    result = {
        "artifacts_hashed": len(hashes),
        "hash_verification_all_pass": all(verify.values()),
        "terminal_manifest_sha256": lock["terminal_manifest_sha256"],
    }
    print(json.dumps(result, indent=1))
    assert result["hash_verification_all_pass"]


if __name__ == "__main__":
    main()
