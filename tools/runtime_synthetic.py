import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
from typing import cast
from runtime.type_support import object_mapping, string

ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "sut.phase2.test_privacy_scope",
    "sut.phase2.test_semantic_normalization",
    "sut.phase2.test_source_admission",
    "sut.phase2.test_evidence_integrity",
    "sut.phase3.test_rejection_synthetic",
    "sut.phase3.test_runtime_synthetic",
    "runtime.discovery_v2.test_fetch_accounting",
    "runtime.discovery.test_host_policy",
    "sut.phase2.test_type_boundaries",
)


def main() -> int:
    candidate_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert candidate_sha == os.environ.get("RUNTIME_CANDIDATE_SHA", candidate_sha)
    evidence = object_mapping(cast(object, json.loads(
        (ROOT / "docs/runtime-type-evidence-2026-10-12.json").read_text())))
    source_hashes = {path: string(digest) for path, digest in
                     object_mapping(evidence["runtime_source_hashes"]).items()}
    hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
              for path in source_hashes}
    manifest = hashlib.sha256(json.dumps(hashes, sort_keys=True,
                                        separators=(",", ":")).encode()).hexdigest()
    assert hashes == source_hashes, "Verified runtime source changed"
    assert manifest == evidence["runtime_source_manifest_sha256"]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock = time.monotonic()
    with patch("socket.getaddrinfo", side_effect=AssertionError("NO_REAL_DNS")) as dns, \
         patch("socket.create_connection", side_effect=AssertionError("NO_REAL_CONNECTION")) as connect, \
         patch("subprocess.run", side_effect=AssertionError("NO_REAL_SUBPROCESS")) as child, \
         patch("subprocess.Popen", side_effect=AssertionError("NO_REAL_BROWSER")) as browser:
        suites = {module: unittest.defaultTestLoader.loadTestsFromName(module) for module in MODULES}
        counts = {module: suite.countTestCases() for module, suite in suites.items()}
        result = unittest.TestResult()
        _ = unittest.TestSuite(suites.values()).run(result)
        attempts = dict(zip(("dns", "socket_connection", "subprocess", "browser"),
                            (guard.call_count for guard in (dns, connect, child, browser))))
    passed = (result.wasSuccessful() and result.testsRun == 68 and not result.skipped
              and not result.expectedFailures and not any(attempts.values()))
    print(json.dumps({
        "schema_version": "navigator-runtime-ci/v1",
        "candidate_sha": candidate_sha,
        "runtime_source_manifest_sha256": manifest,
        "python_version": sys.version,
        "started_at_utc": started,
        "completed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - clock, 3),
        "module_test_counts": counts,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "guard_attempts": attempts,
        "failure_details": [{"test": str(test), "traceback": trace}
                            for test, trace in result.failures + result.errors],
        "passed": passed,
    }, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
