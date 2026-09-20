"""Write-path guard for RC3.3 (spec section 2).

All task writes must land inside the RC3.3 task root. Resolved paths
landing in any forbidden historical tree fail closed, including under
symlink or .. traversal. Reads outside the root are unaffected.
"""
import os

TASK_ROOT = os.path.dirname(os.path.abspath(__file__))

FORBIDDEN_PREFIXES = (
    "rc2-development",
    "rc3-1-proof-semantics",
    "rc3-1-support-boundary",
    "rc3-1-relation-repair",
    "rc3-2-boundary-aware-relation",
    "rc3-generalization-holdout",
    "Obsidian",
    "obsidian",
)


def _forbidden(resolved):
    parts = resolved.split(os.sep)
    for p in FORBIDDEN_PREFIXES:
        if p in parts:
            return True
    return False


def assert_writable(path):
    """Raise PermissionError unless path resolves inside TASK_ROOT
    and outside every forbidden tree. Returns the resolved path."""
    resolved = os.path.realpath(os.path.abspath(path))
    if not resolved.startswith(TASK_ROOT + os.sep):
        raise PermissionError(
            "write-sandbox violation: outside task root: %s" % resolved)
    if _forbidden(resolved):
        raise PermissionError(
            "write-sandbox violation: forbidden tree: %s" % resolved)
    return resolved


def safe_output_path(raw):
    """Validate a --output argument and create parent dirs if needed."""
    resolved = assert_writable(raw)
    d = os.path.dirname(resolved)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    return resolved
