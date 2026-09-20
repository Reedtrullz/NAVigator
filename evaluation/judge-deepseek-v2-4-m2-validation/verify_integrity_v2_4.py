#!/usr/bin/env python3
"""V2.4 resume/integrity gate: verify frozen anchors and result SHAs."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
EVAL = HERE.parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    by_sha = {}
    for path in EVAL.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        by_sha.setdefault(sha256(path), []).append(str(path.relative_to(EVAL)))

    report = {"anchors": {}, "iteration_results": {}, "overall": "PASS"}

    lock = json.loads((HERE / "TASK-LOCK.json").read_text(encoding="utf-8"))
    for name, expected in sorted(lock.get("frozen_anchors", {}).items()):
        found = by_sha.get(expected, [])
        report["anchors"][name] = {"sha": expected, "found": found, "ok": bool(found)}
        if not found:
            report["overall"] = "FAIL"

    comparison = json.loads(
        (HERE / "calibration-comparison.json").read_text(encoding="utf-8"))
    for it in comparison.get("iterations", []):
        rel = "calibration-results-iter%d.json" % it["iteration"]
        actual = sha256(HERE / rel)
        ok = actual == it["results_sha"]
        report["iteration_results"][rel] = {
            "expected": it["results_sha"], "actual": actual, "ok": ok}
        if not ok:
            report["overall"] = "FAIL"

    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
