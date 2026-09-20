#!/usr/bin/env python3
"""Before-construction integrity snapshot (spec 2, 27, 36).

Hashes the frozen candidate components, the large sealed 60-case
validation, RC3G historical artifacts, and RC3.3.1 files. Asserts the
candidate manifest SHA and large-validation SHA. Writes only inside
the task sandbox."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
SEM = TASK.parent
ROOT = SEM.parent.parent

CANDIDATE_MANIFEST_SHA = (
    "c66c14a639afdcf98bc853f4fd0e8a4649c4f59aa16a65993d3390dce15fbdee")
LARGE_VALIDATION_SHA = (
    "15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(HERE))
    import write_guard
    write_guard.check(HERE / "before-hashes.json")

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

    large_path = ROOT / "evaluation/semantic-judge/rc3-1-proof-semantics"
    large_path = large_path / "corpus" / "validation-answer-key.sealed"
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
        "phase": "before-construction",
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA,
        "candidate_manifest_verified": True,
        "candidate_components": components,
        "large_validation": {
            "path": str(large_path),
            "sha256": large,
            "verified": True,
        },
        "rc3g_artifacts": rc3g_hashes,
        "rc31_files": rc31_hashes,
    }
    write_guard.write_text(HERE / "before-hashes.json",
                           json.dumps(out, indent=1) + "\n")
    print("BEFORE_INTEGRITY_OK manifest=" + CANDIDATE_MANIFEST_SHA)
    print("large_validation=" + large)


if __name__ == "__main__":
    main()
