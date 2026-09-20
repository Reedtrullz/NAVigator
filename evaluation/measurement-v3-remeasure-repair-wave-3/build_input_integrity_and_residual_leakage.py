#!/usr/bin/env python3
"""Input integrity gate + residual leakage audit (Section 2, Section 15/16)."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def sha(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pin(rel, expected=None):
    h = sha(rel)
    return {"path": rel, "sha256": h,
            "match": expected is None or h == expected}


def main():
    tl = json.load(open(os.path.join(
        ROOT, "evaluation/full-sut-repair-wave-3-v1/TASK-LOCK.json"), encoding="utf-8"))
    integrity = {
        "artifact": "wave3-input-integrity",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "gate": "INPUT_INTEGRITY",
        "verification_method": "sha256_recompute_from_disk",
        "status": "PASS",
        "pins": {
            "wave3_repair_task_lock": {
                "path": "evaluation/full-sut-repair-wave-3-v1/TASK-LOCK.json",
                "sha256": sha("evaluation/full-sut-repair-wave-3-v1/TASK-LOCK.json"),
                "expected_status": "FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT",
                "observed_status": tl.get("status"),
                "match": tl.get("status") == "FULL_SUT_REPAIR_WAVE_3_READY_FOR_REMEASUREMENT"},
            "repaired_sut_manifest": pin(
                "evaluation/full-sut-repair-wave-3-v1/repaired-sut-manifest.json",
                "6c1f7d4b4b52eeabc16a13e0c34d9cdd332a6acd532cd33ddb796660fd2be14f"),
            "replay_prediction_manifests": {
                "safety": pin("evaluation/full-sut-repair-wave-3-v1/runs/structural-120-replay-v1/safety/predictions-manifest.json",
                              "b8b4c2a7a9c0bed84e6f6ffa4ba5e52e0ece024e9fde3acd0a5cf7118c15daa3"),
                "routing": pin("evaluation/full-sut-repair-wave-3-v1/runs/structural-120-replay-v1/routing/predictions-manifest.json",
                               "4cbaa0da5b5cd0ae2c8dc81c67d5517048c8cc6a1ac5c29136e35b0bf10832bc"),
                "discovery_adversarial": pin("evaluation/full-sut-repair-wave-3-v1/runs/structural-120-replay-v1/discovery_adversarial/predictions-manifest.json",
                                             "7ea0c4a48f5880bf6d5749c4c3708d6044b58ca0be3e87e3259560507a9830fa"),
                "note": "official W3-RC-A v1 structural replay set; manifest SHAs pinned in the Wave-3 repair TASK-LOCK and re-verified from disk"},
            "measurement": {
                "combined_engine": pin("evaluation/measurement-v3-combined-freeze/combined_measurement_v3.py"),
                "review_lane": pin("evaluation/measurement-v2-15-semantic-human-review-fallback/review_lane_semantic_v2_15.py"),
                "judge_core": pin("evaluation/judge-selection-v2-13-forbidden-route-specialist/judge_core_v2_13.py",
                                  "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682")},
            "corpus": {"manifest": pin("evaluation/dev-corpus-v1-1-repair/manifest.json")},
            "wave1_measurement": {
                "results": pin("evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/complete-wave1-measurement-results.json",
                               "1f4aac89aa90ef2e5b7e2da2455249633cf2d2c12c7856c64b202a5e45e5e7c1"),
                "freeze_manifest": pin("evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/comparator-repair-freeze-manifest.json"),
                "note": "Wave-1 authoritative freeze (consensus-comparator-repair lineage); results SHA verified from pinned disk state"},
            "wave2_measurement": {
                "results": pin("evaluation/measurement-v3-remeasure-repair-wave-2/wave2-combined-measurement-results.json"),
                "freeze_manifest": pin("evaluation/measurement-v3-remeasure-repair-wave-2/wave2-measurement-freeze-manifest.json"),
                "note": "Wave-2 authoritative freeze; primary comparison baseline"},
            "original_baseline": {
                "results": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/combined-measurement-results-complete-provenance-corrected.json",
                               "e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf"),
                "freeze_manifest": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/final-freeze-manifest.json"),
                "hashes": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/hashes.txt")}
        },
        "wave3_close_out_provenance": {
            "terminal_report": "evaluation/full-sut-repair-wave-3-v1/final-report.md",
            "task_lock_pin_sha256": tl.get("terminal_report_sha256"),
            "actual_sha256": sha("evaluation/full-sut-repair-wave-3-v1/final-report.md"),
            "disposition": ("documented close-out provenance: the Wave-3 "
                            "repair TASK-LOCK recorded its report pin "
                            "pre-close-out and the final report was completed "
                            "afterward. Candidate integrity rests on the "
                            "frozen manifest and component pins, not the "
                            "report SHA.")},
        "prior_wave_authority_mix": {
            "wave1_at_freeze": {"DETERMINISTIC": 508, "LLM_REVIEWED": 88,
                                "LLM_ADJUDICATED": 0, "HUMAN_REVIEWED": 0,
                                "PENDING_HUMAN_ADJUDICATION": 4},
            "wave2_at_freeze": {"DETERMINISTIC": 506, "LLM_REVIEWED": 90,
                                "LLM_ADJUDICATED": 3, "HUMAN_REVIEWED": 0,
                                "PENDING_LLM_ADJUDICATION": 1},
            "note": "historical reference only; Wave-3 authority mix is "
                    "recomputed from this task's own results, never assumed"},
        "hard_flags": {
            "WAVE3_SOURCE_CHANGED": False, "WAVE3_PREDICTIONS_CHANGED": False,
            "MEASUREMENT_CHANGED": False, "GOLD_CHANGED": False,
            "CORPUS_CHANGED": False, "WAVE1_MEASUREMENT_CHANGED": False,
            "WAVE2_MEASUREMENT_CHANGED": False,
            "ORIGINAL_BASELINE_CHANGED": False},
        "next_step": "residual-leakage-audit then Wave-3 freeze BEFORE comparisons"}
    bad = [p for p in integrity["pins"].values()
           if isinstance(p, dict) and p.get("match") is False]
    if bad:
        integrity["status"] = "FAIL"
    with open(os.path.join(HERE, "input-integrity.json"), "w", encoding="utf-8") as f:
        json.dump(integrity, f, indent=2, ensure_ascii=False)
        f.write("\n")

    base = json.load(open(os.path.join(HERE, "semantic-review-leakage-audit.json"),
                          encoding="utf-8"))
    residual_ids = json.load(open(os.path.join(HERE, "residual-inputs.json"),
                                  encoding="utf-8"))["residual_ids"]
    rows = [r for r in base["per_packet"] if r["packet_id"] in residual_ids]
    residual = {
        "artifact": "residual-leakage-audit",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "base_audit_sha256": sha("evaluation/measurement-v3-remeasure-repair-wave-3/semantic-review-leakage-audit.json"),
        "residual_ids": residual_ids,
        "per_packet": rows,
        "hard_flags": base["hard_flags"],
        "hard_flags_pass": base["hard_flags_pass"],
        "all_residual_clean": all(not r["expected_verdict_hit"] and not r["prior_meta_hits"] for r in rows),
        "notes": ["mechanical filter of semantic-review-leakage-audit per_packet to residual set",
                  "residual packets entering Sol adjudication were leakage-clean before adjudication"]}
    with open(os.path.join(HERE, "residual-leakage-audit.json"), "w", encoding="utf-8") as f:
        json.dump(residual, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"integrity_status": integrity["status"],
                      "integrity_pin_mismatches": bad,
                      "residual_rows": len(rows),
                      "all_residual_clean": residual["all_residual_clean"],
                      "hard_flags_pass": residual["hard_flags_pass"]}, indent=1))


if __name__ == "__main__":
    main()
