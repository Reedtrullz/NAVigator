#!/usr/bin/env python3
"""Compute V1.6A precision/coverage metrics from official one-shot results."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent


def main() -> int:
    res = json.loads((HERE / "official-preclassifier-results.json").read_text())
    fixtures = json.loads((HERE / "boundary-validation-fixtures.json").read_text())["fixtures"]
    results = res["results"]
    if len(results) != len(fixtures):
        print("ROW_COUNT_MISMATCH")
        return 2

    engine_sha = hashlib.sha256((HERE / "boundary_preclassifier.py").read_bytes()).hexdigest()
    if engine_sha != res.get("engine_sha256"):
        print("ENGINE_STATE_MISMATCH")
        return 2

    families = ["route_commitment", "uncertainty_behavior", "assertion_scope"]
    report = {"engine_sha256": engine_sha, "official_classifications_n": len(results), "families": {}}
    for fam in families:
        rows = [r for r in results if r["focus_dimension"] == fam]
        non_abstain = [r for r in rows if not r["abstained"]]
        correct = [r for r in non_abstain if r["label"] == r["expected"]]
        abstain_rows = [r for r in rows if r["abstained"]]
        abstain_correct = [r for r in abstain_rows if r["expected"] == "ABSTAIN"]
        false_det = [r for r in non_abstain if r["label"] != r["expected"]]
        ev_valid = all(r["evidence_span_valid"] for r in non_abstain)
        report["families"][fam] = {
            "n": len(rows),
            "non_abstain_n": len(non_abstain),
            "abstain_n": len(abstain_rows),
            "coverage": round(len(non_abstain) / len(rows), 4),
            "precision": round(len(correct) / len(non_abstain), 4) if non_abstain else None,
            "abstain_rate": round(len(abstain_rows) / len(rows), 4),
            "abstain_recall": round(len(abstain_correct) / len(abstain_rows), 4) if abstain_rows else None,
            "false_deterministic_n": len(false_det),
            "false_deterministic_ids": [r["id"] for r in false_det],
            "evidence_span_validity": 1.0 if ev_valid else 0.0,
        }

    non_abstain_all = [r for r in results if not r["abstained"]]
    correct_all = [r for r in non_abstain_all if r["label"] == r["expected"]]
    report["overall"] = {
        "non_abstain_n": len(non_abstain_all),
        "coverage": round(len(non_abstain_all) / len(results), 4),
        "abstain_rate": round(1 - len(non_abstain_all) / len(results), 4),
        "precision": round(len(correct_all) / len(non_abstain_all), 4) if non_abstain_all else None,
        "false_deterministic_n": sum(1 for r in non_abstain_all if r["label"] != r["expected"]),
        "evidence_span_validity": 1.0 if all(r["evidence_span_valid"] for r in non_abstain_all) else 0.0,
    }

    # safety/critical family = assertion_scope; hard-zero false deterministics there
    report["hard_gates"] = {
        "overall_precision_ge_0_99": report["overall"]["precision"] is not None and report["overall"]["precision"] >= 0.99,
        "family_precision_ge_0_98": all(f["precision"] is not None and f["precision"] >= 0.98 for f in report["families"].values()),
        "safety_false_deterministic_zero": report["families"]["assertion_scope"]["false_deterministic_n"] == 0,
        "evidence_span_validity_100": report["overall"]["evidence_span_validity"] == 1.0,
        "coverage_ge_0_50_soft": report["overall"]["coverage"] >= 0.50,
    }

    (HERE / "precision-coverage-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
