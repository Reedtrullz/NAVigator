"""Experimental V2.5 with source-specific route gates and explicit execution
accounting. Historical V1/V2 orchestrators and evaluations stay frozen.
"""

from datetime import datetime, timezone
from typing import Protocol
from runtime.discovery.contracts import ProtocolDefinition
from runtime.discovery.providers import FetchResult
from runtime.discovery.protocol import ProtocolLoader
from .contracts import DiscoveredService, QueryReport, Result, RunInput, RunResult
from .providers import ProviderResponse


class DiscoveryProvider(Protocol):
    def discover(self, query: str) -> ProviderResponse: ...
    def health(self) -> object: ...


class FetchProvider(Protocol):
    def fetch(self, url: str) -> FetchResult: ...

from runtime.discovery.classification import (
    AccessClassifier, EvidenceLedger, ProvenanceGraph,
)
from runtime.discovery.engine import DiscoveryPlanner, ServiceExtractor
from runtime.discovery.eligibility import age_in_bounds
from runtime.discovery.protocol import EXPECTED_PROTOCOL_SHA
from runtime.discovery.security import InvalidUrlError, is_official_domain, validate_url

from .classification_v25 import RouteEvaluatorV25


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_official_source(url: str) -> bool:
    """Retain a candidate only when it is plausibly an official source."""
    try:
        _ = validate_url(url)
    except InvalidUrlError:
        return False
    return is_official_domain(url) in ("municipal", "helsenorge", "health_enterprise")


_official = is_official_source


ROUTE_ORDER = [
    "ROUTE_FULLY_VERIFIED", "ROUTE_ACCESS_PARTIAL",
    "ROUTE_EXISTENCE_ONLY", "ROUTE_UNVERIFIED",
]


def run_v25(protocol: ProtocolDefinition | ProtocolLoader, input_data: RunInput,
            providers: DiscoveryProvider, fetch_provider: FetchProvider | None = None) -> RunResult:
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
    planner_queries = list(dict.fromkeys(q for step in plan if step["level"] in (1, 2)
                                        for q in step["queries"]))
    unsupported_levels = [step["level"] for step in plan if step["level"] not in (1, 2)]

    query_reports: list[QueryReport] = []
    candidates: list[tuple[Result, ProviderResponse]] = []
    for query in planner_queries:
        try:
            resp = providers.discover(query)
        except Exception as exc:
            resp = ProviderResponse(query, "TIMEOUT" if isinstance(exc, TimeoutError) else "INTERNAL_ERROR")
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
        if resp.status == "SUCCESS" and resp.results:
            candidates.extend((result, resp) for result in resp.results)

    # Candidate filtering: official/plausibly-municipal URLs only.
    selected: list[str] = []
    seen: set[str] = set()
    candidate_sources: dict[str, ProviderResponse] = {}
    for r, resp in candidates:
        url = r.get("url", "")
        if not url or url in seen:
            continue
        if is_official_source(url):
            seen.add(url)
            selected.append(url)
            candidate_sources[url] = resp

    # Provenance edges: provider result -> candidate URL (discovery evidence).
    for url in selected:
        source = candidate_sources[url]
        _ = graph.add_edge(
            from_node=source.provider,
            to_node=url,
            discovery_method=source.discovery_method or "QUERY_SEARCH",
            query_family=source.query,
            level=2,
        )

    fetch_errors: list[dict[str, str | None]] = []
    render_fallbacks = 0
    services: list[DiscoveredService] = []
    best_route = "ROUTE_UNVERIFIED"
    pages_fetched = 0
    attempted_fetches = 0

    for url in selected[:10]:
        try:
            _ = validate_url(url)
        except InvalidUrlError as exc:
            fetch_errors.append({"url": url, "error": "INVALID_URL",
                                 "detail": str(exc)})
            continue
        attempted_fetches += 1
        try:
            fr = fetch_provider.fetch(url)
        except Exception as exc:
            fetch_errors.append({"url": url, "error": "FETCH_FAILED", "detail": type(exc).__name__})
            continue
        if fr.status == "render_required":
            render_fallbacks += 1
            fetch_errors.append({"url": url, "error": "RENDER_REQUIRED",
                                 "detail": "JS-rendered shell; rendered fetch not available"})
            continue
        if fr.status != "success":
            fetch_errors.append({"url": url, "error": "FETCH_FAILED",
                                 "detail": fr.error})
            continue
        pages_fetched += 1
        if not is_official_source(fr.final_url):
            fetch_errors.append({"url": url, "error": "SOURCE_AUTHORITY_REJECTED"})
            continue
        source_url = fr.final_url
        if not extractor.html_to_text(fr.content).strip():
            continue
        if fr.content is None:
            continue
        extract = extractor.extract(fr.content, source_url)
        if not extract:
            continue
        for span_entry in extract.get("text_spans", []):
            _ = ledger.add(
                field=span_entry["label"],
                value=span_entry["span"][:200],
                source_url=source_url,
                source_title=extract.get("title", source_url),
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
        age_eligible = age_in_bounds(extract.get("age_bounds"), input_data.get("age"), extract.get("age_text"))
        eligibility = age_eligible is True
        route_state = evaluator.evaluate(
            service_verified=True,
            eligibility_verified=eligibility,
            access_methods=methods,
            access_clear=access_clear,
            contact_documented=bool(
                extract.get("access_markers", {}).get("contact_invitation")
                or access_clear),
            strong_access=strong_access,
            url=source_url,
        )
        services.append({
            "url": source_url,
            "title": extract.get("title"),
            "access_methods": methods,
            "self_referral": classification["self_referral"],
            "route_state": route_state,
            "age_text": extract.get("age_text"),
            "age_bounds": extract.get("age_bounds"),
            "age_input_eligible": age_eligible,
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
    protocol_completed = bool(planner_queries) and not (
        provider_failures or fetch_errors or unsupported_levels or len(selected) > 10)
    execution_status = "COMPLETE" if protocol_completed else "DISCOVERY_INCOMPLETE"

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
        "execution": {"revision": "discovery-execution/v1", "attempted_fetches": attempted_fetches,
                      "successful_fetches": pages_fetched, "protocol_completed": protocol_completed,
                      "services_found": len(services), "unsupported_levels": unsupported_levels,
                      "unfetched_candidates": max(0, len(selected) - 10)},
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
