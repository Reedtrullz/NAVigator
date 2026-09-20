#!/usr/bin/env python3
"""V1.6A official one-shot pre-classifier validation (frozen classifier)."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    fixtures = json.loads((HERE / "boundary-validation-fixtures.json").read_text())["fixtures"]
    manifest = json.loads((HERE / "preclassifier-manifest.json").read_text())

    # FROZEN STATE VERIFICATION (must hold exactly; otherwise abort before classification)
    engine_sha = sha256(HERE / "boundary_preclassifier.py")
    checks = {
        "boundary_preclassifier.py": (engine_sha, manifest["frozen_engine_sha256"]),
        "boundary-label-contract.json": (sha256(HERE / "boundary-label-contract.json"), manifest["contract_sha256"]),
        "rule-registry.json": (sha256(HERE / "rule-registry.json"), manifest["rule_registry_sha256"]),
        "unit-fixtures.json": (sha256(HERE / "unit-fixtures.json"), manifest["unit_fixtures_sha256"]),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            print(f"FROZEN_STATE_MISMATCH: {name} {actual} != {expected}")
            return 2

    unit = json.loads((HERE / "unit-test-results.json").read_text())
    if not unit["all_pass"] or unit["fixtures"] != manifest["unit_suite"]["fixtures"]:
        print("UNIT_STATE_MISMATCH")
        return 2

    from boundary_preclassifier import classify

    results = []
    for fx in fixtures:
        out = classify(fx["text"], fx.get("criterion"))
        dim = out[fx["focus_dimension"]]
        row = {
            "id": fx["id"],
            "focus_dimension": fx["focus_dimension"],
            "expected": fx["expected_label"],
            "label": dim["label"],
            "abstained": dim["abstained"],
            "rule_id": dim.get("rule_id"),
            "evidence_span": dim.get("evidence_span"),
            "evidence_span_valid": bool(dim["abstained"] or (dim.get("evidence_span") and dim["evidence_span"] in fx["text"])),
        }
        if "reason" in dim:
            row["reason"] = dim["reason"]
        if "conflict" in dim:
            row["conflict"] = dim["conflict"]
        results.append(row)

    doc = {
        "run_type": "OFFICIAL_ONE_SHOT",
        "engine_sha256": engine_sha,
        "manifest_verified": True,
        "fixtures": len(fixtures),
        "results": results,
    }
    (HERE / "official-preclassifier-results.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    report = subprocess.run(
        [sys.executable, str(HERE / "precision_coverage_report.py")], capture_output=True, text=True
    )
    print(report.stdout)
    if report.returncode != 0:
        print(report.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
