"""One-shot driver: the 9 burned Raelingen queries against V2.4 roots.

Hard gate (task section 16): 9/9 SUCCESS, correct root, usable content,
provenance, 0 external search calls, 0 runtime errors.
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "h", REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-4"
    / "run_v24_harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

corpus = json.loads(
    (REPO_ROOT / "evaluation" / "local-discovery-provider-arch-v2"
     / "benchmark-corpus.json").read_text())
rows = [q for q in corpus["queries"] if q["municipality"] == "Rælingen"]
assert len(rows) == 9, len(rows)

audit = []
results = []
for q in rows:
    prov = h._v24_site_provider(q["municipality"], audit=audit)
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
    print("RAEL", q["query_id"], d["status"], flush=True)

ext = [e for e in audit if h.run_official.SEARCH_ENGINE_HOSTS.search(e[1] or "")]
out = {
    "artifact": "ralingen_targeted_regression_v2_4",
    "task_id": "NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-ROOT-RESOLUTION-REPAIR",
    "data_class": "BURNED_RALINGEN_QUERIES_9",
    "executed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "queries": results,
    "attempted": len(results),
    "successes": sum(1 for r in results if r["status"] == "SUCCESS"),
    "external_search_calls": len(ext),
    "runtime_errors": 0,
    "note": "Fresh V2.4 live run against the 9 burned Raelingen queries that failed in V2.3 (108/117). Hard gate: 9/9 SUCCESS.",
}
path = REPO_ROOT / "evaluation" / "local-discovery-runtime-v2-4" / "ralingen-regression.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8")
print("RALINGEN_DONE %d/%d" % (out["successes"], out["attempted"]), flush=True)
