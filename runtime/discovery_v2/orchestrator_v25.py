"""V2.5 orchestrator: frozen V2 run_v2 with exactly two behavioral deltas:

1. RouteEvaluatorV25 replaces RouteEvaluator, capping ROUTE_FULLY_VERIFIED
   when provenance is section-level (service-specific provenance gate).
2. The candidate URL is passed to the evaluator so the gate can apply.

The frozen runtime/discovery_v2/orchestrator.py is untouched. This module
is a verbatim copy of run_v2 (frozen SHA
1c9545b16357ab413baf0b36bbcb3617a6a35baa67a81b99a56902208db62b95) with the
two marked V2.5 lines; any further drift must be justified in the task
report. No case IDs, no municipality names, no expected labels.
"""

import re
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urlparse

from runtime.discovery.classification import (
    AccessClassifier, EvidenceLedger, ProvenanceGraph,
)
from runtime.discovery.engine import DiscoveryPlanner, ServiceExtractor
from runtime.discovery.orchestrator import EXPECTED_PROTOCOL_SHA
from runtime.discovery.security import InvalidUrlError, is_official_domain, validate_url

from .classification_v25 import RouteEvaluatorV25


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fold(name):
    s = unicodedata.normalize("NFKD", name.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\u00e6", "ae").replace("\u00f8", "o").replace("\u00e5", "a")
    return s


def _official(url, municipality):
    """Retain a candidate only when it is plausibly an official source."""
    try:
        validate_url(url)
    except InvalidUrlError:
        return False
    cls = is_official_domain(url)
    if cls in ("municipal", "intermunicipal", "helsenorge", "health_enterprise"):
        return True
    host = (urlparse(url).hostname or "").lower()
    name = _fold(municipality)
    return bool(name) and (name in host or name.replace("ae", "a") in host)


ROUTE_ORDER = [
    "ROUTE_FULLY_VERIFIED", "ROUTE_ACCESS_PARTIAL",
    "ROUTE_EXISTENCE_ONLY", "ROUTE_UNVERIFIED",
]


def run_v25(protocol, input_data, providers, fetch_provider=None):
    """Run one municipality through V2.5 discovery + capped V1 semantics."""
    if not isinstance(protocol, dict):
        protocol = protocol.load()
    municipality = input_data["municipality"]
    run_id = "%s-v2-5" % municipality.lower().replace(" ", "-")

    if fetch_provider is None:
        from runtime.discovery.providers import HttpFetchProvider
        fetch_provider = HttpFetchProvider()

    extractor = ServiceExtractor()
    ledger = EvidenceLedger()
    classifier = AccessClassifier()
    evaluator = RouteEvaluatorV25()
    graph = ProvenanceGraph()

    plan = DiscoveryPlanner(protocol).plan(municipality)
    planner_queries = [q for step in plan if step["level"] in (1, 2)
                       for q in step["queries"]]

    query_reports = []
    chosen = None
    for query in planner_queries:
        resp = providers.discover(query)
        d = resp.to_dict()
        query_reports.append({
            "query": query,
            "status": d["status"],
            "result_count": len(d["results"]),
            "provider": d["provider"],
            "discovery_method": d["discovery_method"],
            "fallback_log": d["fallback_log"],
            "attempts": d["attempts"],
        })
        if chosen is None:
            chosen = resp
        if resp.status == "SUCCESS" and resp.results:
            chosen = resp
            break

    # Candidate filtering: official/plausibly-municipal URLs only.
    selected = []
    seen = set()
    for r in (chosen.results if chosen else []):
        url = r.get("url", "")
        if not url or url in seen:
            continue
        if _official(url, municipality):
            seen.add(url)
            selected.append(url)
        if len(selected) >= 20:
            break

    # Provenance edges: provider result -> candidate URL (discovery evidence).
    for url in selected:
        graph.add_edge(
            from_node=chosen.provider if chosen else "DISCOVERY",
            to_node=url,
            discovery_method=(chosen.discovery_method if chosen else None) or "QUERY_SEARCH",
            query_family=chosen.query if chosen else None,
            level=2,
        )

    fetch_errors = []
    render_fallbacks = 0
    services = []
    best_route = "ROUTE_UNVERIFIED"
    pages_fetched = 0

    for url in selected[:10]:
        try:
            validate_url(url)
        except InvalidUrlError as exc:
            fetch_errors.append({"url": url, "error": "INVALID_URL",
                                 "detail": str(exc)})
            continue
        fr = fetch_provider.fetch(url)
        pages_fetched += 1
        if fr.status == "render_required":
            render_fallbacks += 1
            fetch_errors.append({"url": url, "error": "RENDER_REQUIRED",
                                 "detail": "JS-rendered shell; rendered fetch not available"})
            continue
        if fr.status != "success":
            fetch_errors.append({"url": url, "error": "FETCH_FAILED",
                                 "detail": fr.error})
            continue
        extract = extractor.extract(fr.content, url)
        if not extract:
            continue
        for span_entry in extract.get("text_spans", []):
            ledger.add(
                field=span_entry["label"],
                value=span_entry["span"][:200],
                source_url=url,
                source_title=extract.get("title", url),
                span=span_entry["span"],
                retrieved_at=fr.retrieved_at or _now_iso(),
                fetch_method=fr.fetch_method,
                content_hash=fr.content_hash,
                confidence_state="EXTRACTED_SPAN",
            )
        classification = classifier.classify(extract)
        methods = classification["methods"]
        access_clear = methods != ["UNCLEAR"]
        strong_access = bool(
            extract.get("access_markers", {}).get("explicit_self_contact")
            or "APPLICATION_FORM" in methods
            or "DIRECT_DROPIN" in methods
            or "DIRECT_EMAIL" in methods
        )
        eligibility = bool(extract.get("age_text") or extract.get("age_universal")
                           or extract.get("target_group"))
        route_state = evaluator.evaluate(
            service_verified=True,
            eligibility_verified=eligibility,
            access_methods=methods,
            access_clear=access_clear,
            contact_documented=bool(
                extract.get("access_markers", {}).get("contact_invitation")
                or access_clear),
            strong_access=strong_access,
            url=url,  # V2.5 delta: provenance gate input
        )
        services.append({
            "url": url,
            "title": extract.get("title"),
            "access_methods": methods,
            "self_referral": classification["self_referral"],
            "route_state": route_state,
            "age_text": extract.get("age_text"),
            "target_group": extract.get("target_group"),
            "evidence_spans": extract.get("text_spans", []),
        })

    if services:
        best_route = sorted((s["route_state"] for s in services),
                            key=ROUTE_ORDER.index)[0]

    if best_route == "ROUTE_FULLY_VERIFIED":
        terminal_state = "ACCESS_VERIFIED"
    else:
        terminal_state = "PUBLIC_DATA_EXHAUSTED"

    provider_failures = [q for q in query_reports
                         if q["status"] not in ("SUCCESS", "NO_RESULTS")]
    execution_status = ("COMPLETE" if pages_fetched > 0
                        else "DISCOVERY_INCOMPLETE")

    uncertainty = protocol["uncertainty_outputs"]
    if best_route == "ROUTE_FULLY_VERIFIED":
        uncertainty_output = uncertainty["VERIFIED_ROUTE"]
    elif services:
        uncertainty_output = uncertainty["SERVICE_FOUND_ACCESS_UNCLEAR"]
    else:
        uncertainty_output = uncertainty["NO_VERIFIED_ROUTE_AFTER_PROTOCOL"]

    return {
        "run_id": run_id,
        "runtime": "discovery_v2_5",
        "mode": "live",
        "input": input_data,
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": EXPECTED_PROTOCOL_SHA,
        "executed_at": _now_iso(),
        "query_families_used": planner_queries,
        "queries": query_reports,
        "provider_chain": providers.health(),
        "fallback_log": [f for q in query_reports for f in q["fallback_log"]],
        "selected_candidates": selected,
        "pages_fetched": pages_fetched,
        "render_fallbacks": render_fallbacks,
        "services": services,
        "route_state": best_route,
        "terminal_state": terminal_state,
        "execution_status": execution_status,
        "provider_failures": provider_failures,
        "fetch_errors": fetch_errors,
        "uncertainty_output": uncertainty_output,
        "evidence": ledger.entries,
        "provenance_graph": graph.edges,
    }
