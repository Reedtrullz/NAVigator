"""V2.4 official-run harness (thin, new-lineage).

Reuses the frozen V2.3 run_official.py runners byte-unmodified via importlib.
Three swaps only:
1. canonical_roots -> canonical_roots_v24 (the V2.4 root repair) in the
   site-direct provider factory.
2. Provider class name prefix stays SiteDirectProviderV23 (budget 16,
   reused unchanged; the V2.4 behavioral delta is roots only).
3. Output files land in the V2.4 task directory, not the historical dir.

No historical file is written; no frozen source is edited.
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import runtime.discovery_v2.roots as _v23_roots  # noqa: E402
from runtime.discovery_v2.roots_v24 import canonical_roots_v24  # noqa: E402

V23_RUNNER = (REPO_ROOT / "evaluation"
              / "local-discovery-site-direct-only-v2-3" / "run_official.py")
V24_TASK_DIR = REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-4"

spec = importlib.util.spec_from_file_location("run_official_v24", V23_RUNNER)
run_official = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_official)


def _v24_site_provider(municipality, audit):
    from runtime.discovery_v2.cli_v23 import SiteDirectProviderV23
    from runtime.discovery_v2.render import RenderFetchFn
    fetch_fn = run_official.RenderFetchFn(
        run_official._FetchFnHttp(), audit=audit, max_renders=4)
    return SiteDirectProviderV23(
        fetch_fn=fetch_fn,
        roots=canonical_roots_v24(municipality) if municipality else None,
    )


run_official.build_site_provider = _v24_site_provider
run_official.write_json = lambda name, obj: (V24_TASK_DIR / name).write_text(
    json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    # run_official.main() parses sys.argv itself (phase = argv[1]).
    run_official.main()


if __name__ == "__main__":
    main()
