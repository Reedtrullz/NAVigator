#!/usr/bin/env python3
"""Build input-integrity.json for the consensus comparator repair task.

Re-verifies the frozen upstream lineage, residual inputs, Sol observations,
derivation kernel, pre-Wave-1 burned baseline and frozen comparison builder,
then pins all of them. No LLM calls, no file writes outside this task dir."""
import hashlib
import importlib.util
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
UP = os.path.join(EVAL, "measurement-v3-wave1-residual-llm-adjudication-v1")
RC01 = os.path.join(EVAL, "measurement-v3-remeasure-repair-wave-1")
CORE = os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist",
                    "judge_core_v2_13.py")
OLD = os.path.join(EVAL, "measurement-v3-final-authority-provenance-repair-v1",
                   "combined-measurement-results-complete-provenance-corrected.json")
PINS = {
    "upstream/measurement-manifest.json": "71a0b22441d69924226bf7835dc441df1b779e76dfbfff7fc867010c96c017fd",
    "upstream/TASK-LOCK.json": "3e5fd8b11ae7c118247ad3e6c16e9406bb9c2b1d728bcf5733a3af9df3cd2c7b",
    "upstream/wave1-remeasurement-complete-after-secondary-residual.json": "25dca5775bf76f223247d05364cbba1479d887b3f26718b0ced085fc847dc7d8",
    "upstream/sol-blind-inputs.json": "851e80069366322a47e4f137490402b9a41f2f5ac541de54938d561fced2f533",
    "upstream/sol-pass-a.jsonl": "46e9855d4848ecdb5ca85bcb6b9aa495b4b036d3ce2e29c4686e410765524cb3",
    "upstream/sol-pass-b.jsonl": "45547f0c0bf3448396fbd8cea97d159ad23a7c34464f60adc5d2a59c8bd0890e",
    "upstream/sol-adjudication-frozen-observations.json": "b2d1bf1ea1863d254a025882f52c881d37b9ebc96752241f2bac5148d714980b",
    "derivation/judge_core_v2_13.py": "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682",
    "pre-wave1-baseline/combined-measurement-results-complete-provenance-corrected.json": "e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf",
    "pre-wave1-baseline/build_baseline_comparison.py": "635bb2acbfdfad109ce7c3e70db8e6a000151724474b68d29014a3c1ee4cc11c",
}
LABEL = {
    "upstream/measurement-manifest.json": "frozen Wave-1 residual lineage manifest (lock pin)",
    "upstream/TASK-LOCK.json": "upstream terminal TASK-LOCK (file SHA)",
    "upstream/wave1-remeasurement-complete-after-secondary-residual.json": "upstream 600-row state with 4 pending rows",
    "upstream/sol-blind-inputs.json": "4 frozen residual packets",
    "upstream/sol-pass-a.jsonl": "Sol blind pass A observations",
    "upstream/sol-pass-b.jsonl": "Sol blind pass B observations",
    "upstream/sol-adjudication-frozen-observations.json": "frozen observation artifact",
    "derivation/judge_core_v2_13.py": "frozen deterministic derivation kernel",
    "pre-wave1-baseline/combined-measurement-results-complete-provenance-corrected.json": "old burned baseline (provenance-corrected)",
    "pre-wave1-baseline/build_baseline_comparison.py": "frozen semantic_state definition source",
}
RESIDUAL_PIDS = ["PKT-ESC-DIS-118", "PKT-ESC-ROUT-026-F01",
                 "PKT-ESC-ROUT-031-F01", "PKT-ESC-ROUT-037"]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    checks, pins = {}, {}
    lock = json.load(open(os.path.join(UP, "TASK-LOCK.json"), encoding="utf-8"))
    checks["upstream_lock_terminal"] = (
        lock["status"] == "CLOSED"
        and lock["terminal_status"]
        == "MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING")

    inputs = json.load(open(os.path.join(UP, "sol-blind-inputs.json"),
                            encoding="utf-8"))["packets"]
    by_pid = {p["packet_id"]: p["packet_sha256"] for p in inputs}
    checks["residual_packets_frozen"] = all(
        by_pid.get(pid) for pid in RESIDUAL_PIDS)

    def load(name):
        return {json.loads(l)["packet_id"]: json.loads(l)
                for l in open(os.path.join(UP, name), encoding="utf-8")
                if l.strip()}
    a, b = load("sol-pass-a.jsonl"), load("sol-pass-b.jsonl")
    checks["sol_observations_complete"] = (
        set(a) == set(RESIDUAL_PIDS) and set(b) == set(RESIDUAL_PIDS))
    checks["sol_records_schema_valid"] = all(
        r.get("status") == "OK"
        and set(r["result"]) == {"criterion_semantic_match",
                                 "speaker_commitment", "evidence_spans",
                                 "rationale"}
        for rec in (a, b) for r in rec.values())

    sut = {p["packet_id"]: p for p in inputs}
    checks["packet_sha_bindings_valid"] = all(
        rec.get("packet_sha256") == sut[pid]["packet_sha256"]
        for rec in (a, b) for pid, rec in rec.items())
    checks["required_evidence_valid_both_passes"] = all(
        all(span in sut[pid]["sut_output"]
            for span in rec["result"]["evidence_spans"])
        for rec in (a, b) for pid, rec in rec.items())

    spec = importlib.util.spec_from_file_location("judge_core_v2_13", CORE)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    checks["derivation_kernel_loads"] = hasattr(core, "derive_final")

    up_results = json.load(open(os.path.join(
        UP, "wave1-remeasurement-complete-after-secondary-residual.json"),
        encoding="utf-8"))
    checks["authoritative_596_rows"] = (
        up_results["coverage"]["AUTHORITATIVE_TOTAL"] == 596
        and up_results["coverage"]["PENDING_HUMAN_ADJUDICATION"] == 4)

    for label, digest in PINS.items():
        path = os.path.join(EVAL if label.startswith(("upstream/",
            "derivation/", "pre-wave1-baseline/")) else HERE, label)
        if label.startswith("upstream/"):
            path = os.path.join(UP, label.split("/", 1)[1])
        elif label.startswith("derivation/"):
            path = CORE
        elif label.startswith("pre-wave1-baseline/"):
            base, name = label.split("/", 1)
            path = os.path.join(RC01 if name == "build_baseline_comparison.py"
                                else os.path.dirname(OLD), name)
        actual = sha(path)
        pins[label] = {"sha256": actual, "matches": actual == digest,
                       "label": LABEL[label]}
    checks["all_pins_match"] = all(p["matches"] for p in pins.values())

    doc = {
        "artifact": "input-integrity",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "llm_calls": 0,
        "checks": checks,
        "all_checks_pass": all(checks.values()) and all(
            p["matches"] for p in pins.values()),
        "pins": pins,
    }
    with open(os.path.join(HERE, "input-integrity.json"), "w",
              encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"checks": checks, "all_pass": doc["all_checks_pass"]},
                     indent=1))


if __name__ == "__main__":
    main()
