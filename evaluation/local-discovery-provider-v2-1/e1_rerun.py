"""E1 readiness re-run on BURNED data (task V2.1 adapter correctness).

Method identical to fresh-eval V2 E1: frozen run_v2 stack, site-direct
only (external disabled) for 5 burned municipalities; then a 5-query
single-shot probe of the frozen brave_html adapter (2 s interval, no
retries, no evasion). No fresh municipalities, no sample building.
"""

import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery.protocol import ProtocolLoader  # noqa: E402
from runtime.discovery_v2.brave import (  # noqa: E402
    brave_parser, make_brave_provider,
)
from runtime.discovery_v2.orchestrator import run_v2  # noqa: E402
from runtime.discovery_v2.providers import (  # noqa: E402
    BOT_MARKERS, CompositeDiscoveryProvider, SiteDirectProvider,
)

PROTOCOL_PATH = REPO_ROOT / "data" / "local-service-discovery-protocol-v1.json"
OUT_PATH = REPO_ROOT / "evaluation" / "local-discovery-provider-v2-1" / "provider-readiness-v2-1.json"

# Stage-A roots exactly as recorded in fresh-eval V2 provider-readiness.json;
# empty roots use the frozen www.<kommune>.kommune.no pattern.
SITE_MUNICIPALITIES = [
    {"municipality": "Alta", "roots": ["https://www.alta.kommune.no/"]},
    {"municipality": "Farsund", "roots": []},
    {"municipality": "Sor-Varanger", "roots": []},
    {"municipality": "Alstahaug", "roots": ["https://www.alstahaug.kommune.no/"]},
    {"municipality": "Hasvik", "roots": ["https://hasvik.kommune.no/"]},
]

EXTERNAL_QUERIES = [
    "Alta kommune psykisk helse voksne",
    "Farsund kommune psykisk helse kontakt",
    "Hasvik kommune helsestasjon",
    "Alstahaug kommune psykisk helse rus",
    "Sor-Varanger kommune rask psykisk helsehjelp",
]


def input_for(name):
    return {"municipality": name, "municipality_number": None, "age": 22,
            "need": "mental_health_low_threshold", "urgency": "non_acute"}


class _LiveHttp:
    """Same convention as V2 E1: real curl via V1 HttpFetchProvider."""

    def __init__(self):
        from runtime.discovery.providers import HttpFetchProvider
        self.inner = HttpFetchProvider()

    def __call__(self, url):
        fr = self.inner.fetch(url)
        if fr.status == "success":
            return (200, fr.content or "")
        if fr.status == "render_required":
            return (200, "")
        m = re.search(r"HTTP (\d{3})", fr.error or "")
        return (int(m.group(1)) if m else 0, "")


def run_site_direct():
    protocol = ProtocolLoader(str(PROTOCOL_PATH)).load()
    from runtime.discovery_v2.sitemap_fetch import bounded_fetch
    runs = []
    for m in SITE_MUNICIPALITIES:
        site = SiteDirectProvider(
            fetch_fn=_LiveHttp(),
            roots=m["roots"] or None,
            sitemap_fetch_fn=bounded_fetch)
        comp = CompositeDiscoveryProvider([site])
        result = run_v2(protocol, input_for(m["municipality"]), comp)
        queries = result["queries"]
        runs.append({
            "municipality": m["municipality"],
            "roots": m["roots"],
            "execution_status": result["execution_status"],
            "route_state": result["route_state"],
            "pages_fetched": result["pages_fetched"],
            "services_n": len(result["services"]),
            "selected_n": len(result["selected_candidates"]),
            "provenance_edges_n": len(result["provenance_graph"]),
            "provider_failures_n": len(result["provider_failures"]),
            "fetch_errors_n": len(result["fetch_errors"]),
            "queries_n": len(queries),
            "first_provider_status": queries[0]["status"] if queries else None,
        })
    return runs


def run_external_probe():
    provider = make_brave_provider(max_queries_per_run=5, min_interval_s=2.0)
    out = []
    for q in EXTERNAL_QUERIES:
        resp = provider.discover(q)
        att = resp.attempts[0] if resp.attempts else {}
        body = att.get("body")
        body_present = isinstance(body, str)
        marker_in_window = False
        if body_present:
            from runtime.discovery_v2.providers import MAX_SCAN_BYTES
            marker_in_window = bool(BOT_MARKERS.search(body[:MAX_SCAN_BYTES]))
        out.append({
            "query": q,
            "status": resp.status,
            "result_count": len(resp.results),
            "error": resp.error,
            "curl_exit": att.get("curl_exit"),
            "http_status": att.get("http_status"),
            "initial_url": att.get("initial_url"),
            "final_url": att.get("final_url"),
            "num_redirects": att.get("num_redirects"),
            "body_truncated": att.get("body_truncated"),
            "body_sha256": hashlib.sha256(
                body.encode("utf-8", errors="replace")).hexdigest()
            if body_present else None,
            "challenge_detected": marker_in_window,
        })
        time.sleep(2.0)
    return out


def main():
    site_runs = run_site_direct()
    external = run_external_probe()
    site_ok = all(r["execution_status"] == "COMPLETE" and
                  r["provenance_edges_n"] > 0 for r in site_runs)
    success_n = sum(1 for e in external if e["status"] == "SUCCESS")
    result = {
        "artifact": "E1_provider_readiness_v2_1",
        "task_id": "NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-V2_1-ADAPTER-CORRECTNESS",
        "data_class": "BURNED_MUNICIPALITIES_ONLY",
        "fresh_municipalities_used": 0,
        "site_direct": {"runs": site_runs, "gate_5_of_5": site_ok},
        "external_brave": {"queries": external,
                           "successful_executions": success_n,
                           "attempted": len(external),
                           "gate_ge_4_of_5": success_n >= 4,
                           "status_counts": {s: sum(1 for e in external
                                              if e["status"] == s)
                                              for s in set(e["status"]
                                              for e in external)}},
    }
    OUT_PATH.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(json.dumps({"site_gate": site_ok, "external_success": success_n,
                      "external_gate": success_n >= 4,
                      "external_statuses": result["external_brave"]["status_counts"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
