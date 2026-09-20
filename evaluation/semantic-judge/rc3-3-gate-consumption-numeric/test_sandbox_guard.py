"""Sandbox guard tests (spec sections 2, 3, 47). Run directly."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sandbox_guard import assert_writable, TASK_ROOT


def test():
    failures = []

    # 1. historical source path rejected
    src = os.path.join(
        TASK_ROOT, "..", "rc3-1-proof-semantics", "TASK-LOCK.json")
    try:
        assert_writable(src)
        failures.append("rc3-1 path accepted")
    except PermissionError:
        pass

    # 2. RC3.2 task directory rejected
    rc32 = os.path.join(
        TASK_ROOT, "..", "rc3-2-boundary-aware-relation", "x.json")
    try:
        assert_writable(rc32)
        failures.append("rc3-2 path accepted")
    except PermissionError:
        pass

    # 3. traversal rejected after resolution
    trav = os.path.join(
        TASK_ROOT, "..", "..", "rc3-1-support-boundary", "x.json")
    try:
        assert_writable(trav)
        failures.append("traversal path accepted")
    except PermissionError:
        pass

    # 4. legitimate task-local path accepted
    ok = os.path.join(TASK_ROOT, "results", "sandbox-ok.txt")
    resolved = assert_writable(ok)
    if not resolved.startswith(TASK_ROOT):
        failures.append("task-local path rejected wrongly")

    print("SANDBOX_GUARD_TESTS:", "PASS" if not failures else failures)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    test()
