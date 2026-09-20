#!/usr/bin/env python3
"""Reconcile deliverable names for the Wave-4 quota resume lineage.

Creates thin config artifacts for the already-executed Astra and Sol runs,
a source manifest pinning the frozen quota-safe inputs, and exact byte
copies of the residual-validation and derived-results artifacts under the
spec-required names. No measurement or review output is modified.
"""
import hashlib
import json
import os
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    astra_records = []
    for fname in ("astra-pass-a.jsonl", "astra-pass-b.jsonl"):
        astra_records.extend(
            json.loads(l) for l in open(os.path.join(HERE, fname),
                                        encoding="utf-8") if l.strip())
    retries = sum(len(r.get("transport_attempts") or []) for r in astra_records)
    models = {r["model"] for r in astra_records}
    efforts = {r["reasoning_effort"] for r in astra_records}
    cfg_hashes = {r["request_config_hash"] for r in astra_records}
    assert models == {"gpt-6-astra"} and efforts == {"low"}
    assert len(astra_records) == 220 and retries == 0
    with open(os.path.join(HERE, "astra-config.json"), "w",
              encoding="utf-8") as f:
        json.dump({
            "artifact": "astra-review-config",
            "task_id": TASK_ID,
            "recorded_after_execution": True,
            "model": "gpt-6-astra",
            "reasoning_effort": "LOW",
            "reasoning_effort_enforcement": "hard; MEDIUM/HIGH/MAX forbidden",
            "transport": "local proxy http://127.0.0.1:10100/v1/chat/completions",
            "auth": "bearer token from existing auth store; never printed, "
                    "logged, or persisted in artifacts",
            "passes": ["ASTRA-A", "ASTRA-B"],
            "call_count": {"ASTRA-A": 110, "ASTRA-B": 110},
            "transport_retries_observed": retries,
            "request_config_hash": sorted(cfg_hashes),
            "prompt_and_validation_technique":
                "frozen Wave-3 run_astra_review.py imported unchanged",
            "retry_policy": "ONE technical transport retry only; "
                            "schema-invalid or disagreeing output NOT retried",
            "blindness": "A and B blind to each other, to historical verdicts, "
                         "to gold, and to prior model results",
        }, f, indent=2, ensure_ascii=False)
        f.write("\n")

    sol_records = []
    for fname in ("sol-pass-a.jsonl", "sol-pass-b.jsonl"):
        sol_records.extend(
            json.loads(l) for l in open(os.path.join(HERE, fname),
                                        encoding="utf-8") if l.strip())
    sol_retries = sum(
        e.get("outcome") == "TRANSPORT_ERROR"
        for e in json.load(open(os.path.join(HERE, "sol-transport-log.json"),
                                encoding="utf-8")).get("events", []))
    sol_models = {r["model"] for r in sol_records}
    sol_efforts = {r["reasoning_effort"] for r in sol_records}
    sol_cfg_hashes = {r["request_config_hash"] for r in sol_records}
    assert sol_models == {"gpt-5.6-sol"} and sol_efforts == {"low"}
    assert len(sol_records) == 8 and sol_retries == 0
    with open(os.path.join(HERE, "sol-config.json"), "w",
              encoding="utf-8") as f:
        json.dump({
            "artifact": "sol-residual-review-config",
            "task_id": TASK_ID,
            "recorded_after_execution": True,
            "lane": "residual_adjudication",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "LOW",
            "reasoning_effort_enforcement": "hard; MEDIUM/HIGH/MAX forbidden",
            "transport": "local proxy http://127.0.0.1:10100/v1/chat/completions "
                         "(existing authorized stack only)",
            "auth": "bearer token from existing auth store; never printed, "
                    "logged, or persisted in artifacts",
            "passes": ["SOL-A", "SOL-B"],
            "call_count": {"SOL-A": 4, "SOL-B": 4},
            "transport_retries_observed": sol_retries,
            "request_config_hash": sorted(sol_cfg_hashes),
            "prompt_and_validation_technique":
                "frozen Wave-3 run_residual_adjudication.py imported unchanged",
            "consensus_rule": "both passes valid AND authoritative semantic "
                              "fields identical => LLM_ADJUDICATED/"
                              "GPT_5_6_SOL_DUAL_PASS_RESIDUAL; otherwise "
                              "PENDING_LLM_ADJUDICATION; no third pass",
            "blindness": "SOL-B blind to SOL-A; both blind to Astra outputs, "
                         "prior results, and gold",
        }, f, indent=2, ensure_ascii=False)
        f.write("\n")

    pins = {
        "source_lineage_task_id":
            "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-4-QUOTA-SAFE-V1",
        "source_terminal_state":
            "MEASUREMENT_V3_REMEASURE_WAVE_4_QUOTA_DEFERRED",
        "source_partial_freeze_manifest_sha256":
            sha256(os.path.join(SRC, "wave4-partial-measurement-freeze-manifest.json")),
        "source_partial_measurement_results_sha256":
            sha256(os.path.join(SRC, "wave4-partial-measurement-results.json")),
        "quota_resume_manifest_sha256":
            sha256(os.path.join(SRC, "quota-resume-manifest.json")),
        "quota_resume_semantic_packets_sha256":
            sha256(os.path.join(SRC, "quota-resume-semantic-packets.jsonl")),
        "quota_resume_packet_count": 110,
        "wave3_compat_bridge_results_sha256":
            sha256(os.path.join(SRC, "wave3-compat-bridge-results.json")),
        "wave3_historical_results_sha256": sha256(os.path.join(
            REPO, "evaluation", "measurement-v3-remeasure-repair-wave-3",
            "wave3-combined-measurement-results.json")),
        "original_provenance_corrected_baseline_sha256": sha256(os.path.join(
            REPO, "evaluation",
            "measurement-v3-final-authority-provenance-repair-v1",
            "combined-measurement-results-complete-provenance-corrected.json")),
        "resume_semantic_review_freeze_manifest_sha256": sha256(
            os.path.join(HERE, "semantic-review-freeze-manifest.json")),
    }
    assert pins["source_partial_freeze_manifest_sha256"].startswith("ff0b7a41a2c30168")
    assert pins["source_partial_measurement_results_sha256"] == (
        "30999cb8b4c135acce255bdd83effe98935fcbbe657f1b6ecc90d8380bba8dc5")
    with open(os.path.join(HERE, "resume-source-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump({"artifact": "resume-source-manifest", "task_id": TASK_ID,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime()),
                   **pins}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    shutil.copyfile(os.path.join(HERE, "residual-validation.json"),
                    os.path.join(HERE, "sol-validation.json"))
    shutil.copyfile(os.path.join(HERE, "derived-measurement-results.json"),
                    os.path.join(HERE, "derived-resume-results.json"))
    print("astra_calls:", len(astra_records), "sol_calls:", len(sol_records),
          "retries:", retries, sol_retries)
    print("resume-source-manifest pins verified")


if __name__ == "__main__":
    main()
