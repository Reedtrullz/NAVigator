"""V2.5 official-run harness (thin, new-lineage).

Reuses the frozen V2.3 run_official.py runners byte-unmodified via
importlib. Exactly three swaps:
1. build_site_provider -> V2.5 provider (sitemapindex follow + render on
   empty extraction; V2.4 canonical roots retained).
2. run_v2 -> run_v25 (frozen orchestrator + service-specific FV gate).
3. run_official.TASK_DIR -> this task directory, so every artifact write
   (and the audit phase's reads) land in the V2.5 task dir. This also fixes
   the V2.4 harness gap where its audit phase read V2.3 artifacts.

No historical file is written; no frozen source is edited.
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

V23_RUNNER = (REPO_ROOT / "evaluation"
              / "local-discovery-site-direct-only-v2-3" / "run_official.py")
V25_TASK_DIR = REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-5"

spec = importlib.util.spec_from_file_location("run_official_v25", V23_RUNNER)
run_official = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_official)

from runtime.discovery_v2.orchestrator_v25 import run_v25  # noqa: E402
from runtime.discovery_v2.roots_v24 import canonical_roots_v24  # noqa: E402
from runtime.discovery_v2.cli_v23 import _FetchFnHttp  # noqa: E402
from runtime.discovery_v2.providers_v25 import SiteDirectProviderV25  # noqa: E402
from runtime.discovery_v2.render import RenderFetchFn  # noqa: E402


def _v25_site_provider(municipality, audit):
    fetch_fn = RenderFetchFn(_FetchFnHttp(), audit=audit, max_renders=4)
    return SiteDirectProviderV25(
        fetch_fn=fetch_fn,
        roots=canonical_roots_v24(municipality) if municipality else None,
    )


run_official.build_site_provider = _v25_site_provider
run_official.run_v2 = run_v25
run_official.TASK_DIR = V25_TASK_DIR


def main():
    # run_official.main() parses sys.argv itself (phase = argv[1]).
    run_official.main()


if __name__ == "__main__":
    main()
