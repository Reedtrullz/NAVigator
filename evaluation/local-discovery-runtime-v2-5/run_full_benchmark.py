"""V2.5 full official benchmark driver (frozen burned corpus, 117 queries).

Invokes the frozen run_official.run_benchmark() through the V2.5 harness:
identical corpus and metrics, with the V2.5 provider + FV gate. Output:
site-direct-benchmark.json + benchmark-results.json in the V2.5 dir.
"""

import json
import shutil
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

h.run_official.run_benchmark()
shutil.copyfile(h.V25_TASK_DIR / "site-direct-benchmark.json",
                h.V25_TASK_DIR / "benchmark-results.json")
