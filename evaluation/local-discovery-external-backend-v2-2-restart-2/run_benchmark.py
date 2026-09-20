"""Official comparative benchmark runner (RESTART-2 frozen contract).

Runs the frozen 117-query burned corpus against the Tavily Search API in
both frozen modes (GENERAL gate-bearing, OFFICIAL_DOMAIN_CONSTRAINED
diagnostic). One attempt per query, 0.5 s interval, no retries, no
evasion, no query rewriting. Results are frozen to JSON unmodified;
analysis happens only after the run completes (task section 30).
"""

import json
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery_v2.tavily import make_tavily_provider  # noqa: E402
from runtime.discovery_v2.orchestrator import _official  # noqa: E402

CORPUS_PATH = REPO_ROOT / "evaluation" / "local-discovery-provider-arch-v2" / "benchmark-corpus.json"
OUT_DIR = REPO_ROOT / "evaluation" / "local-discovery-external-backend-v2-2-restart-2"


def fold(name):
    s = unicodedata.normalize("NFKD", name.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s


def regdom(host):
    parts = (host or "").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def muni_domains(name):
    slug = fold(name)
    return [slug + ".kommune.no", "www." + slug + ".kommune.no"]


def run_mode(mode, queries):
    provider = make_tavily_provider(max_queries_per_run=500, min_interval_s=0.5)
    rows = []
    started = time.time()
    for i, q in enumerate(queries, start=1):
        include_domains = (muni_domains(q["municipality"])
                           if mode == "OFFICIAL_DOMAIN_CONSTRAINED" else None)
        provider.fetch_fn = _make_fetch(include_domains)
        resp = provider.discover(q["query"])
        d = resp.to_dict()
        urls = [r["url"] for r in d["results"][:10]]
        hosts = [urlparse(u).hostname or "" for u in urls]
        gold_reg = {regdom(urlparse(u).hostname or "") for u in q["gold_urls"]}
        gold_exact = any(u.rstrip("/") in {g.rstrip("/") for g in q["gold_urls"]}
                         for u in urls)
        gold_domain_hit = any(regdom(h) in gold_reg for h in hosts)
        official = [h for h, u in zip(hosts, urls) if _official(u, q["municipality"])]
        precision = (len(official) / len(urls)) if urls else 0.0
        rows.append({
            "query_id": q["query_id"],
            "municipality": q["municipality"],
            "centrality_class": q["centrality_class"],
            "status": d["status"],
            "error": d["error"],
            "result_count": d["result_count"] if "result_count" in d else len(d["results"]),
            "top10_urls": urls,
            "gold_url_exact": gold_exact,
            "gold_domain_hit": gold_domain_hit,
            "official_domain_precision": round(precision, 4),
            "latency_ms": (resp.attempts[0].get("latency_ms") if resp.attempts else 0),
        })
        if i % 20 == 0 or i == len(queries):
            print("PROGRESS %s %d/%d elapsed=%.0fs" % (mode, i, len(queries), time.time() - started), flush=True)
    return rows, provider.health.to_dict(), time.time() - started


def _make_fetch(include_domains):
    import runtime.discovery_v2.tavily as t
    def _fetch(query):
        return t.tavily_fetch_fn(query, timeout=15,
                                 include_domains=include_domains)
    return _fetch


def main():
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    queries = corpus["queries"]
    assert len(queries) == 117, len(queries)
    out = {}
    for mode in ("GENERAL", "OFFICIAL_DOMAIN_CONSTRAINED"):
        rows, health, elapsed = run_mode(mode, queries)
        out[mode] = {"rows": rows, "health": health, "elapsed_s": round(elapsed, 1)}
        (OUT_DIR / ("tavily-%s-rows.json" % mode.lower())).write_text(
            json.dumps({"mode": mode, "rows": rows, "health": health,
                        "elapsed_s": round(elapsed, 1)},
                       ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print("MODE_DONE %s rows=%d health=%s" % (mode, len(rows), json.dumps(health)), flush=True)
    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
