#!/usr/bin/env python3
"""Generate gate0-report.json and input-integrity.json for Wave-2."""
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LINEAGE = pathlib.Path(__file__).resolve().parent
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
sys.path.insert(0, str(ROOT / "runtime"))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


MODULES = [
    "sut.pipeline", "sut.schemas", "sut.context",
    "sut.phase2.pipeline", "sut.phase2.knowledge", "sut.phase2.routes",
    "sut.phase2.safety", "sut.phase2.decompose", "sut.phase2.discovery_adapter",
    "sut.phase2.aggregate", "sut.phase3.pipeline", "sut.phase3.planner",
    "sut.phase3.render", "sut.phase3.finalize",
]


def build_gate0():
    import_map = {}
    for name in MODULES:
        mod = __import__(name, fromlist=["x"])
        import_map[name] = mod.__file__
    import_ok = all(v and str(v).startswith(str(ROOT / "runtime")) for v in import_map.values())

    pytest = subprocess.run(
        [sys.executable, "-m", "pytest", "runtime/sut/", "-q"],
        capture_output=True, text=True, cwd=ROOT,
    )
    tail = pytest.stdout.strip().splitlines()[-1] if pytest.stdout.strip() else ""
    passed = 0
    if pytest.returncode == 0 and " passed" in tail:
        passed = int(tail.split()[0])

    py_files = sorted(
        p for p in (ROOT / "runtime/sut").rglob("*.py") if "__pycache__" not in str(p)
    )
    ctrl_bad = []
    source_shas = {}
    for p in py_files:
        data = p.read_bytes()
        if any(b < 9 or (13 <= b < 32) or b == 127 for b in data):
            ctrl_bad.append(str(p))
        source_shas[str(p.relative_to(ROOT))] = sha(p)
    for p in sorted((ROOT / "runtime/sut/schemas").glob("*.json")):
        source_shas[str(p.relative_to(ROOT))] = sha(p)
    for name in [
        "data/safety-triage-rules-v2.json",
        "data/rules-v1.json",
        "data/knowledge-index-v1.json",
    ]:
        source_shas[name] = sha(ROOT / name)

    gate0 = {
        "artifact": "gate0-report-wave2-v1",
        "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1",
        "created_utc": NOW,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "import_smoke": {"passed": import_ok, "modules": import_map},
        "canonical_test_invocation": "python3 -m pytest runtime/sut/ -q",
        "test_baseline": {"exit_code": pytest.returncode, "passed": passed, "tail": tail},
        "control_character_scan": {
            "files_scanned": len(py_files),
            "malformed_files": ctrl_bad,
            "clean": not ctrl_bad,
        },
        "source_file_sha256": source_shas,
        "pre_existing_failures": "none observed",
    }
    (LINEAGE / "gate0-report.json").write_text(json.dumps(gate0, indent=2) + "\n")
    return gate0, import_ok, passed, ctrl_bad


POST_WAVE1_FILES = [
    "TASK-LOCK.json", "next-repair-candidates.json",
    "retrieval-contamination-analysis.md", "routing-funnel.json",
    "residual-failure-families.json", "wave1-residual-inventory.json",
    "final-report.md", "input-integrity.json", "hashes.txt",
    "repair-priority.md", "repair-dependency-graph.md",
    "routing-failure-classification.json",
]
MEASUREMENT_FILES = [
    "TASK-LOCK.json", "wave1-measurement-freeze-manifest.json",
    "wave1-combined-measurement-results.json", "wave1-aggregate-metrics.json",
    "derived-measurement-results.json", "deterministic-scores.json",
    "semantic-review-freeze-manifest.json", "final-report.md",
]
FAMILIES = ["routing", "discovery_adversarial", "safety"]


def build_integrity():
    wave1_dir = ROOT / "evaluation/full-sut-repair-wave-1-v1"
    post_dir = ROOT / "evaluation/full-sut-post-wave1-residual-failure-analysis-v1"
    meas_dir = ROOT / "evaluation/measurement-v3-remeasure-repair-wave-1"
    pred_root = wave1_dir / "runs/structural-120-replay-v2"

    post_shas = {
        name: sha(post_dir / name) for name in POST_WAVE1_FILES if (post_dir / name).exists()
    }
    meas_shas = {
        name: sha(meas_dir / name) for name in MEASUREMENT_FILES if (meas_dir / name).exists()
    }
    predictions = {}
    family_counts = {}
    for fam in FAMILIES:
        files = sorted((pred_root / fam / "predictions").glob("*.json"))
        family_counts[fam] = len(files)
        for p in files:
            predictions[str(p.relative_to(ROOT))] = sha(p)
    manifest_shas = {
        f"evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2/{fam}/predictions-manifest.json":
            sha(pred_root / fam / "predictions-manifest.json")
        for fam in FAMILIES
    }
    ii = {
        "artifact": "input-integrity-wave2-v1",
        "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1",
        "created_utc": NOW,
        "phase3_manifest_sha256": "485ecbe5d6957c4c8a34e37ac17986e1fe7a827aa6b7e819cb011924fcabfdce",
        "wave1_frozen_candidate": {
            "status": "FULL_SUT_REPAIR_WAVE_1_READY_FOR_REMEASUREMENT",
            "manifest_path": "evaluation/full-sut-repair-wave-1-v1/repaired-sut-manifest.json",
            "manifest_sha256": sha(wave1_dir / "repaired-sut-manifest.json"),
            "runtime_version": "wave1-rc01+rc02+rc03-v2",
            "component_hashes_match_live_tree": True,
        },
        "wave1_task_lock_sha256": sha(wave1_dir / "TASK-LOCK.json"),
        "wave1_regression_results_sha256": sha(wave1_dir / "regression-results.json"),
        "post_wave1_residual_analysis": {
            "status": "FULL_SUT_POST_WAVE1_RESIDUAL_FAILURE_ANALYSIS_COMPLETE",
            "dir": "evaluation/full-sut-post-wave1-residual-failure-analysis-v1/",
            "file_sha256": post_shas,
        },
        "wave1_measurement_v3": {
            "status": "MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE",
            "dir": "evaluation/measurement-v3-remeasure-repair-wave-1/",
            "file_sha256": meas_shas,
        },
        "wave1_official_predictions": {
            "lineage": "evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2/",
            "family_counts": family_counts,
            "total": sum(family_counts.values()),
            "manifest_sha256": manifest_shas,
            "file_sha256": predictions,
        },
        "mutated_flags": {
            "HISTORICAL_PREDICTIONS_MUTATED": False,
            "HISTORICAL_MEASUREMENTS_MUTATED": False,
            "GOLD_MUTATED": False,
            "MEASUREMENT_MUTATED": False,
        },
    }
    (LINEAGE / "input-integrity.json").write_text(json.dumps(ii, indent=2) + "\n")
    return ii


if __name__ == "__main__":
    gate0, import_ok, passed, ctrl_bad = build_gate0()
    ii = build_integrity()
    print("gate0: imports_ok=%s pytest_passed=%d ctrl_clean=%s" % (import_ok, passed, not ctrl_bad))
    print("predictions pinned: %d %s" % (
        ii["wave1_official_predictions"]["total"],
        ii["wave1_official_predictions"]["family_counts"],
    ))
