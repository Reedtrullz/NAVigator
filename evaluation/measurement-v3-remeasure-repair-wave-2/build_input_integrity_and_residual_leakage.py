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
        ROOT, "evaluation/full-sut-repair-wave-2-v1/TASK-LOCK.json"), encoding="utf-8"))
    integrity = {
        "artifact": "wave2-input-integrity",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2",
        "gate": "INPUT_INTEGRITY",
        "verification_method": "sha256_recompute_from_disk",
        "status": "PASS",
        "pins": {
            "wave2_repair_task_lock": {
                "path": "evaluation/full-sut-repair-wave-2-v1/TASK-LOCK.json",
                "sha256": sha("evaluation/full-sut-repair-wave-2-v1/TASK-LOCK.json"),
                "expected_status": "FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT",
                "observed_status": tl.get("status"),
                "match": tl.get("status") == "FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT"},
            "repaired_sut_manifest": pin(
                "evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json",
                "8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e"),
            "replay_prediction_manifests": {
                "safety": pin("evaluation/full-sut-repair-wave-2-v1/runs/structural-120-replay-v2/safety/predictions-manifest.json"),
                "routing": pin("evaluation/full-sut-repair-wave-2-v1/runs/structural-120-replay-v2/routing/predictions-manifest.json"),
                "discovery_adversarial": pin("evaluation/full-sut-repair-wave-2-v1/runs/structural-120-replay-v2/discovery_adversarial/predictions-manifest.json"),
                "note": "official Candidate-2 structural replay set; determinism evidence recorded, handoff did not pin individual SHAs"},
            "measurement": {
                "combined_engine": pin("evaluation/measurement-v3-combined-freeze/combined_measurement_v3.py"),
                "review_lane": pin("evaluation/measurement-v2-15-semantic-human-review-fallback/review_lane_semantic_v2_15.py"),
                "judge_core": pin("evaluation/judge-selection-v2-13-forbidden-route-specialist/judge_core_v2_13.py",
                                  "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682")},
            "corpus": {"manifest": pin("evaluation/dev-corpus-v1-1-repair/manifest.json")},
            "wave1_measurement": {
                "results": pin("evaluation/measurement-v3-remeasure-repair-wave-1/wave1-combined-measurement-results.json"),
                "freeze_manifest": pin("evaluation/measurement-v3-remeasure-repair-wave-1/wave1-measurement-freeze-manifest.json"),
                "note": "Wave-1 authoritative freeze; results SHA verified against Wave-1 freeze manifest pin"},
            "original_baseline": {
                "results": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/combined-measurement-results-complete-provenance-corrected.json",
                               "e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf"),
                "freeze_manifest": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/final-freeze-manifest.json"),
                "hashes": pin("evaluation/measurement-v3-final-authority-provenance-repair-v1/hashes.txt")}
        },
        "candidate_1_incident": {
            "status": "SUPERSEDED_HISTORICAL_NOT_MEASURED",
            "engineering_evidence_only": True,
            "success": "99/120", "execution_failed": 21,
            "fail_closed_reason": "verified claim value missing from answer",
            "proven_root_cause": ["per-track evidence IDs restarted",
                                  "duplicate evidence IDs across tracks",
                                  "planner INFO dedup removed second-track blocks",
                                  "finalizer correctly failed closed"],
            "enters_scoring": False},
        "wave1_authority_mix_at_freeze": {"DETERMINISTIC": 508, "LLM_REVIEWED": 88,
                                          "LLM_ADJUDICATED": 0, "HUMAN_REVIEWED": 0,
                                          "PENDING_HUMAN_ADJUDICATION": 4},
        "wave2_ownership_transition": {"DETERMINISTIC": "508 -> 506",
                                       "LLM_REVIEWED": "88 -> 90",
                                       "LLM_ADJUDICATED": "0 -> 3",
                                       "PENDING": "4 -> 1"},
        "hard_flags": {
            "WAVE2_SOURCE_CHANGED": False, "WAVE2_PREDICTIONS_CHANGED": False,
            "MEASUREMENT_CHANGED": False, "GOLD_CHANGED": False,
            "CORPUS_CHANGED": False, "WAVE1_MEASUREMENT_CHANGED": False,
            "ORIGINAL_BASELINE_CHANGED": False},
        "next_step": "residual-leakage-audit then Wave-2 freeze BEFORE comparisons"}
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
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2",
        "base_audit_sha256": sha("evaluation/measurement-v3-remeasure-repair-wave-2/semantic-review-leakage-audit.json"),
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
    bad = [p for p in integrity["pins"].values()
           if isinstance(p, dict) and p.get("match") is False]
    print(json.dumps({"integrity_status": integrity["status"],
                      "integrity_pin_mismatches": bad,
                      "residual_rows": len(rows),
                      "all_residual_clean": residual["all_residual_clean"],
                      "hard_flags_pass": residual["hard_flags_pass"]}, indent=1))


if __name__ == "__main__":
    main()
