"""V2.5 access regression driver: 9 burned targets (frozen evaluator is
correct for this comparison: it must reproduce the frozen V2.3 baseline
states, not the V2.5 cap)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "h", REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-5"
    / "run_v25_harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

h.run_official.run_access()
