"""V2.4 access regression driver: 9 burned targets, current source truth."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "h", REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-4"
    / "run_v24_harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

h.run_official.run_access()
