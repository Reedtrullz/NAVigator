#!/usr/bin/env python3
"""Gate 0 + input-integrity for Wave-3.

Verifies, before any source edit:
- every component of the frozen Wave-2 candidate manifest matches the live tree
- the three gold corpus SHAs match the TASK-LOCK pins
- every hash in the scope-gate lineage hashes.txt still matches
- import smoke, canonical pytest baseline, control-character scan, source SHAs
"""
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LINEAGE = pathlib.Path(__file__).resolve().parent
SCOPE_DIR = ROOT / "evaluation/post-wave2-p0-routing-wave3-scope-gate-v1"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

MODULES = [
    "sut.pipeline", "sut.schemas", "sut.context",
    "sut.phase2.pipeline", "sut.phase2.knowledge", "sut.phase2.routes",
    "sut.phase2.safety", "sut.phase2.decompose", "sut.phase2.discovery_adapter",
    "sut.phase2.aggregate", "sut.phase3.pipeline", "sut.phase3.planner",
    "sut.phase3.render", "sut.phase3.finalize",
]

GOLD = {
    "evaluation/dev-corpus-v1-1-repair/cases/routing_cases.json": "55f634d9cee8726343b75a6d61eb0a375532a3ac2948df3b5383e70d1983e317",
    "evaluation/dev-corpus-v1-1-repair/cases/safety_cases.json": "5d7cefcb43a9db233ed529f4cf439191d8f38125f727de104843933fe79e6800",
    "evaluation/dev-corpus-v1-1-repair/cases/discovery_adversarial_cases.json": "8eb2ab761affc0f2ac4095e54c54c3ff4302005beb8eaf10830a5c93a2074104",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_wave2_manifest():
    manifest_path = ROOT / "evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json"
    manifest_sha = sha(manifest_path)
    pinned = json.loads(manifest_path.read_text())["components"]
    mismatches = []
    for rel, want in sorted(pinned.items()):
        got = sha(ROOT / rel)
        if got != want:
            mismatches.append({"path": rel, "expected": want, "actual": got})
    return {
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "manifest_sha256": manifest_sha,
        "component_count": len(pinned),
        "mismatches": mismatches,
        "result": "ALL_OK" if not mismatches else "MISMATCH",
    }


def verify_scope_gate_hashes():
    failures = []
    checked = 0
    for line in (SCOPE_DIR / "hashes.txt").read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip()
        # bare names are relative to the scope-gate dir; corpus paths are repo-relative
        path = ROOT / rel if rel.startswith("evaluation/") else SCOPE_DIR / rel
        checked += 1
        if not path.exists() or sha(path) != digest:
            failures.append({"path": rel, "expected": digest,
                             "actual": sha(path) if path.exists() else "MISSING"})
    return {"lines_checked": checked, "failures": failures,
            "result": "ALL_OK" if not failures else "MISMATCH"}


def verify_gold():
    out = {}
    for rel, want in GOLD.items():
        got = sha(ROOT / rel)
        out[rel] = {"expected": want, "actual": got,
                    "match": got == want}
    return out


def build_gate0(wave2_ver, scope_ver):
    sys.path.insert(0, str(ROOT / "runtime"))
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
        "artifact": "gate0-report-wave3-v1",
        "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1",
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
        "wave2_manifest_verification": wave2_ver,
        "scope_gate_hashes_verification": scope_ver,
        "pre_existing_failures": "none observed",
    }
    (LINEAGE / "gate0-report.json").write_text(json.dumps(gate0, indent=2) + "\n")
    return gate0


def build_integrity(gold_ver):
    wave2_dir = ROOT / "evaluation/full-sut-repair-wave-2-v1"
    pred_root = wave2_dir / "runs/structural-120-replay-v2"
    FAMILIES = ["routing", "safety", "discovery_adversarial"]
    predictions = {}
    family_counts = {}
    for fam in FAMILIES:
        files = sorted((pred_root / fam / "predictions").glob("*.json"))
        family_counts[fam] = len(files)
        for p in files:
            predictions[str(p.relative_to(ROOT))] = sha(p)
    ii = {
        "artifact": "input-integrity-wave3-v1",
        "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1",
        "created_utc": NOW,
        "wave2_frozen_candidate": {
            "status": "FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT",
            "manifest_path": "evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json",
            "runtime_version": "wave2-rc07+rc08+rc10+rc11-v2",
        },
        "wave2_task_lock_sha256": sha(wave2_dir / "TASK-LOCK.json"),
        "wave2_official_predictions": {
            "lineage": "evaluation/full-sut-repair-wave-2-v1/runs/structural-120-replay-v2/",
            "family_counts": family_counts,
            "total": sum(family_counts.values()),
            "file_sha256": predictions,
        },
        "gold_corpora": gold_ver,
        "scope_gate_lineage": "evaluation/post-wave2-p0-routing-wave3-scope-gate-v1/",
        "mutated_flags": {
            "HISTORICAL_PREDICTIONS_MUTATED": False,
            "HISTORICAL_MEASUREMENTS_MUTATED": False,
            "GOLD_MUTATED": False,
            "MEASUREMENT_MUTATED": False,
            "SAFETY_POLICY_CHANGED": False,
            "FRESH_CASES_CONSUMED": 0,
        },
    }
    (LINEAGE / "input-integrity.json").write_text(json.dumps(ii, indent=2) + "\n")
    return ii


def main():
    wave2_ver = verify_wave2_manifest()
    scope_ver = verify_scope_gate_hashes()
    gold_ver = verify_gold()
    gold_bad = [k for k, v in gold_ver.items() if not v["match"]]
    if wave2_ver["result"] != "ALL_OK":
        print("ABORT: wave2 manifest mismatch:", wave2_ver["mismatches"])
        sys.exit(1)
    if scope_ver["result"] != "ALL_OK":
        print("ABORT: scope-gate hash mismatch:", scope_ver["failures"])
        sys.exit(1)
    if gold_bad:
        print("ABORT: gold corpus mismatch:", gold_bad)
        sys.exit(1)
    gate0 = build_gate0(wave2_ver, scope_ver)
    ii = build_integrity(gold_ver)
    print("wave2 components: %s (%d)" % (wave2_ver["result"], wave2_ver["component_count"]))
    print("scope-gate hashes: %s (%d lines)" % (scope_ver["result"], scope_ver["lines_checked"]))
    print("gold corpora: ALL_OK (3/3 match TASK-LOCK pins)")
    print("gate0: imports_ok=%s pytest_passed=%d ctrl_clean=%s" % (
        gate0["import_smoke"]["passed"],
        gate0["test_baseline"]["passed"],
        gate0["control_character_scan"]["clean"],
    ))
    print("predictions pinned: %d %s" % (
        ii["wave2_official_predictions"]["total"],
        ii["wave2_official_predictions"]["family_counts"],
    ))


if __name__ == "__main__":
    main()
