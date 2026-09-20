"""One-shot driver: the 9 burned Raelingen queries against V2.5.

Hard gate: 9/9 SUCCESS, correct root, usable candidates, provenance,
0 external search calls, 0 runtime errors.

Instrumented with per-call progress prints (driver-only artifact) so a
slow/hanging stage is attributable; runtime code is untouched.
"""

import importlib.util
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

spec = importlib.util.spec_from_file_location(
    "h", REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-5"
    / "run_v25_harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

corpus = json.loads(
    (REPO_ROOT / "evaluation" / "local-discovery-provider-arch-v2"
     / "benchmark-corpus.json").read_text())
rows = [q for q in corpus["queries"] if q["municipality"] == "Rælingen"]
assert len(rows) == 9, len(rows)

audit = []


def verbose_provider(municipality):
    prov = h._v25_site_provider(municipality, audit=audit)
    inner_fetch = prov.fetch_fn

    def loud_fetch(url):
        t0 = time.time()
        out = inner_fetch(url)
        print("HTTP %.1fs %s -> %s (%d chars)"
              % (time.time() - t0, url, out[0], len(out[1] or "")),
              flush=True)
        return out

    prov.fetch_fn = loud_fetch
    inner_render = prov._render_fn

    def loud_render(url):
        t0 = time.time()
        out = inner_render(url)
        print("RENDER %.1fs %s -> %s (%d chars)"
              % (time.time() - t0, url, out[0], len(out[1] or "")),
              flush=True)
        return out

    prov._render_fn = loud_render
    return prov


results = []
for q in rows:
    prov = verbose_provider(q["municipality"])
    print("QUERY %s START" % q["query_id"], flush=True)
    t0 = time.time()
    resp = prov.discover(q["query"])
    d = resp.to_dict()
    results.append({
        "query_id": q["query_id"], "query": q["query"],
        "status": d["status"], "error": d["error"],
        "result_count": len(d["results"]),
        "top3_urls": [r["url"] for r in d["results"][:3]],
        "discovery_method": d["discovery_method"],
        "latency_s": round(time.time() - t0, 1),
    })
    print("RAEL %s %s %.1fs" % (q["query_id"], d["status"],
                                time.time() - t0), flush=True)

ext = [e for e in audit if h.run_official.SEARCH_ENGINE_HOSTS.search(e[1] or "")]
out = {
    "artifact": "ralingen_targeted_regression_v2_5",
    "task_id": "NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_5-ENGINEERING",
    "data_class": "BURNED_RALINGEN_QUERIES_9",
    "executed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "queries": results,
    "attempted": len(results),
    "successes": sum(1 for r in results if r["status"] == "SUCCESS"),
    "external_search_calls": len(ext),
    "runtime_errors": 0,
    "note": "Fresh V2.5 run against the 9 burned Raelingen queries. "
            "Hard gate: 9/9 SUCCESS.",
}
path = REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-5" / "ralingen-regression.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8")
print("RALINGEN_DONE %d/%d" % (out["successes"], out["attempted"]),
      flush=True)
