#!/usr/bin/env python3
"""Historical integrity snapshot for the annotation-contract task.

Hashes the frozen candidate manifest and components, the existing 30-case
micro-validation file, the large sealed 60-case validation, and RC3G/RC3.3.1
historical artifacts. Asserts the known SHAs before any annotation work.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
ROOT = SEM.parent.parent

CANDIDATE_MANIFEST_SHA = (
    "c66c14a639afdcf98bc853f4fd0e8a4649c4f59aa16a65993d3390dce15fbdee")
CASES_SHA = (
    "c231979d969f945184adaac9ad6fdd0b193c545dda96415b62facd57e4cfa20b")
LARGE_VALIDATION_SHA = (
    "15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rc31 = SEM / "rc3-3-1-residual-contradiction"
    manifest_path = rc31 / "candidate-prevalidation" / "manifest.json"
    assert sha(manifest_path) == CANDIDATE_MANIFEST_SHA, \
        "candidate manifest SHA mismatch"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    components = {}
    for rel, expected in manifest["components"].items():
        p = rc31 / rel
        if not p.exists():
            p = ROOT / rel
        actual = sha(p)
        components[rel] = {
            "resolved_path": str(p),
            "sha256": actual,
            "matches_manifest": actual == expected,
        }

    cases_path = SEM / "rc3-3-2-microvalidation" / \
        "microvalidation-cases.json"
    cases_sha = sha(cases_path)
    assert cases_sha == CASES_SHA, "30-case file SHA mismatch"

    large_path = ROOT / "evaluation/semantic-judge/rc3-1-proof-semantics" / \
        "corpus" / "validation-answer-key.sealed"
    large = sha(large_path)
    assert large == LARGE_VALIDATION_SHA, "large validation SHA mismatch"

    rc3g = SEM / "rc3-generalization-holdout"
    rc3g_files = ["generalization-cases.json", "answer-key.sealed",
                  "construction-audit.sealed", "blind-manifest.json",
                  "TASK-LOCK.json", "author_cases_main.py",
                  "construction_tools.py", "seal_holdout.py"]
    rc3g_hashes = {f: sha(rc3g / f)
                   for f in rc3g_files if (rc3g / f).exists()}

    rc31_hashes = {p.name: sha(p)
                   for p in sorted(rc31.iterdir()) if p.is_file()}

    out = {
        "phase": "task-start",
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA,
        "candidate_manifest_verified": True,
        "candidate_components": components,
        "microvalidation_cases": {
            "path": str(cases_path),
            "sha256": cases_sha,
            "verified": True,
        },
        "large_validation": {
            "path": str(large_path),
            "sha256": large,
            "verified": True,
        },
        "rc3g_artifacts": rc3g_hashes,
        "rc31_files": rc31_hashes,
    }
    (HERE / "integrity-start.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("INTEGRITY_START_OK")
    print("candidate_manifest=" + CANDIDATE_MANIFEST_SHA)
    print("cases=" + cases_sha)
    print("large_validation=" + large)
    print("components_ok=" +
          str(all(v["matches_manifest"] for v in components.values())))


if __name__ == "__main__":
    main()
