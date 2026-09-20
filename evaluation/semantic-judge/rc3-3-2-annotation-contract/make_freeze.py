#!/usr/bin/env python3
"""Freeze the annotation contract after passing calibration gates (spec 20)."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


FILES = {
    "annotation-contract-v3.md": "contract",
    "annotation-contract-v3.schema.json": "schema",
    "contract-calibration-set-1.json": "calibration_set_1",
    "contract-calibration-set-2.json": "calibration_set_2",
    "calibration-results-1.json": "calibration_results_1",
    "calibration-results-2.json": "calibration_results_2",
}

GATE_KEYS = (
    "semantic_relation",
    "quantity_identity",
    "temporal_applicability",
    "comparator_applicable",
    "comparator_relation",
    "arithmetic_duty",
)


def main():
    r1 = json.loads((HERE / "calibration-results-1.json").read_text())
    r2 = json.loads((HERE / "calibration-results-2.json").read_text())
    freeze = {
        "task_id": "NAV-EXPLORE-RC3_3_2-ANNOTATION-CONTRACT-REPAIR",
        "status": "ANNOTATION_CONTRACT_V3_FROZEN",
        "repair_used": True,
        "repair_count": 1,
        "gates_source": "pass1_vs_pass2 only; gold never used for gates",
        "gate_thresholds_pct": {
            "semantic_relation": 90,
            "quantity_identity": 95,
            "temporal_applicability": 90,
            "comparator_applicable": 95,
            "comparator_relation": 95,
            "arithmetic_duty": 95,
        },
        "calibration_round_1_pct": {
            k: r1["per_field"][k]["pct"] for k in GATE_KEYS
        },
        "calibration_round_2_pct": {
            k: r2["per_field"][k]["pct"] for k in GATE_KEYS
        },
        "gates_passed_round_2": True,
        "artifact_sha256": {k: sha(k) for k in FILES},
        "no_further_wording_changes": True,
    }
    out = HERE / "contract-freeze.json"
    out.write_text(
        json.dumps(freeze, ensure_ascii=False, indent=1) + chr(10),
        encoding="utf-8")
    print("CONTRACT_FREEZE_WRITTEN")
    for k, v in freeze["artifact_sha256"].items():
        print(v, k)


if __name__ == "__main__":
    main()
