"""run_discovery: orchestrate the frozen discovery protocol end-to-end.

In replay mode all inputs come from fixtures (captured pages + search
manifests). In live mode HttpSearchProvider and HttpFetchProvider are used.
No municipality-specific branching exists here.
"""

import re
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urlparse

from .protocol import ProtocolLoader, EXPECTED_PROTOCOL_SHA
from .security import validate_url, InvalidUrlError, is_official_domain
from .engine import DiscoveryPlanner, LinkExplorer, ServiceExtractor
from .classification import EvidenceLedger, AccessClassifier, RouteEvaluator, ProvenanceGraph


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_discovery(protocol, input_data, fixtures=None, mode="replay"):
    """Execute discovery for one municipality and return the result package."""
    municipality = input_data["municipality"]
    run_id = "%s-%s" % (municipality.lower().replace(" ", "-"), mode)

    # Accept either an already-loaded protocol dict or a ProtocolLoader.
    if not isinstance(protocol, dict):
        protocol = protocol.load()

    # Providers
    if mode == "replay":
        from .providers import ReplaySearchProvider, ReplayFetchProvider
        search_provider = ReplaySearchProvider(fixtures.get("search_index", {}))
        fetch_provider = ReplayFetchProvider(fixtures.get("pages", {}))
    else:
        from .providers import HttpSearchProvider, HttpFetchProvider
        search_provider = HttpSearchProvider()
        fetch_provider = HttpFetchProvider()

    planner = DiscoveryPlanner(protocol)
    explorer = LinkExplorer(fetch_provider, max_depth=2, max_pages=20)
    extractor = ServiceExtractor()
    ledger = EvidenceLedger()
    classifier = AccessClassifier()
    evaluator = RouteEvaluator()
    graph = ProvenanceGraph()

    plan = planner.plan(municipality)
    errors = []
    pages_fetched = 0
    render_fallbacks = 0
    discovered_urls = set()
    searches = []

    # --- Level 0 / 1 / 2: search-driven discovery ---
    fixture_search = fixtures.get("search_index", {}) if mode == "replay" else {}
    fixture_pages = fixtures.get("pages", {}) if mode == "replay" else {}

    # Build the per-municipality search keys: search_index stores results
    # keyed by template query. In replay, only queries present in the fixture
    # manifest are run (queries the original research actually executed).
    for step in plan:
        if step["level"] not in (1, 2):
            continue
        for query in step["queries"]:
            sr = search_provider.search(query)
            if sr.results:
                searches.append({"query": query, "level": step["level"],
                                 "results": [{"url": r["url"], "title": r.get("title", "")}
                                             for r in sr.results]})
                for r in sr.results:
                    discovered_urls.add(r["url"])
                    graph.add_edge(
                        from_node="QUERY_SEARCH",
                        to_node=r["url"],
                        discovery_method="QUERY_SEARCH",
                        query_family=query,
                        level=step["level"],
                    )

    # --- Level 0: known URLs from fixture (if provided) ---
    known_urls = fixtures.get("known_urls", []) if mode == "replay" else []
    for u in known_urls:
        if not _url_matches_municipality(u, municipality):
            continue
        if u not in discovered_urls:
            discovered_urls.add(u)
            graph.add_edge(from_node="KNOWN_URL", to_node=u,
                           discovery_method="KNOWN_PAGE_CONTENT", level=0)

    # --- Level 2: follow links from fetched pages ---
    # (LinkExplorer handles the per-page link following and discovery edges)

    # --- Fetch and extract from each discovered URL ---
    page_extracts = []
    for url in sorted(discovered_urls):
        try:
            validate_url(url)
        except InvalidUrlError as exc:
            errors.append({"url": url, "error": "INVALID_URL", "detail": str(exc)})
            continue
        fr = fetch_provider.fetch(url)
        pages_fetched += 1
        if fr.status == "render_required":
            render_fallbacks += 1
            errors.append({"url": url, "error": "RENDER_REQUIRED",
                           "detail": "JS-rendered shell; rendered fetch not available"})
            continue
        if fr.status != "success":
            errors.append({"url": url, "error": "FETCH_FAILED", "detail": fr.error})
            continue

        extract = extractor.extract(fr.content, url)
        if extract:
            page_extracts.append(extract)
            # Log nav edges for links found on this page (provenance)
            for link in LinkExplorer._extract_links(fr.content, url):
                if link not in discovered_urls:
                    graph.add_edge(from_node=url, to_node=link,
                                   discovery_method="NAVIGATION_LINK", level=2)

        # Evidence ledger entries
        for span_entry in (extract or {}).get("text_spans", []):
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

    # --- Aggregate per-service and route evaluation ---
    services = []
    input_age = input_data.get("age")
    best_access_methods = ["UNCLEAR"]
    best_self_referral = "UNCLEAR"
    any_access_clear = False
    any_contact = False
    any_age_eligible = False
    any_target_group_documented = False

    for pe in page_extracts:
        classification = classifier.classify(pe)
        service_name = _derive_service_name(pe["url"], pe)
        service = {
            "name": service_name,
            "source_url": pe["url"],
            "state": "SERVICE_VERIFIED",
            "access_methods": classification["methods"],
            "self_referral": classification["self_referral"],
            "access_markers": pe.get("access_markers", {}),
            "age_text": pe.get("age_text"),
            "age_bounds": pe.get("age_bounds"),
            "age_universal": pe.get("age_universal"),
            "target_group": pe.get("target_group"),
            "evidence_spans": pe.get("text_spans", []),
        }
        services.append(service)
        age_ok = _age_in_documented_bounds(
            pe.get("age_bounds"), pe.get("age_universal"), input_age)
        service["age_input_eligible"] = age_ok if (pe.get("age_bounds") or pe.get("age_universal")) else None
        if pe.get("target_group"):
            any_target_group_documented = True
        if classification["methods"] != ["UNCLEAR"]:
            any_access_clear = True
            best_access_methods = classification["methods"]
            best_self_referral = classification["self_referral"]
            any_contact = True
    # Strong access evidence = explicit self-contact, form, or drop-in (E1/E2).
    # A bare phone/contact invitation only supports ACCESS_PARTIAL.
    strong_access = any(
        s for s in services
        if s.get("access_markers", {}).get("explicit_self_contact")
        or "APPLICATION_FORM" in (s.get("access_methods") or [])
        or "DIRECT_DROPIN" in (s.get("access_methods") or [])
        or "DIRECT_EMAIL" in (s.get("access_methods") or [])
    )
    weak_access = any_access_clear and not strong_access

    service_verified = bool(services)
    eligibility_verified = any(
        s.get("age_text") or s.get("age_universal") or s.get("target_group")
        for s in services)
    route_state = evaluator.evaluate(
        service_verified=service_verified,
        eligibility_verified=eligibility_verified,
        access_methods=best_access_methods,
        access_clear=any_access_clear,
        contact_documented=any_contact,
        strong_access=strong_access,
    )

    # Terminal state
    if any_access_clear and route_state == "ROUTE_FULLY_VERIFIED":
        terminal_state = "ACCESS_VERIFIED"
    elif route_state in ("ROUTE_ACCESS_PARTIAL", "ROUTE_EXISTENCE_ONLY"):
        terminal_state = "PUBLIC_DATA_EXHAUSTED"
    elif route_state == "ROUTE_UNVERIFIED":
        terminal_state = "PUBLIC_DATA_EXHAUSTED"
    else:
        terminal_state = "PUBLIC_DATA_EXHAUSTED"

    # Execution status: DISCOVERY_INCOMPLETE if any fetch/search errors blocked
    # the protocol from reaching a genuine terminal state, or if zero evidence
    # was gathered (no pages fetched) so an empty result cannot be mistaken
    # for a completed protocol run.
    blocking_errors = [e for e in errors if e["error"] in (
        "FETCH_FAILED", "RENDER_REQUIRED", "SEARCH_FAILED", "RATE_LIMITED")]
    execution_status = ("DISCOVERY_INCOMPLETE"
                        if blocking_errors or pages_fetched == 0 else "COMPLETE")

    # Uncertainty wording from frozen protocol
    uncertainty = _uncertainty_wording(protocol, route_state, any_access_clear)

    return {
        "run_id": run_id,
        "mode": mode,
        "input": input_data,
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": EXPECTED_PROTOCOL_SHA,
        "started_at": None,  # set by caller for determinism
        "discovery_plan": plan,
        "searches": searches,
        "pages_fetched": pages_fetched,
        "render_fallbacks": render_fallbacks,
        "discovered_urls": sorted(discovered_urls),
        "services": services,
        "route_state": route_state,
        "terminal_state": terminal_state,
        "execution_status": execution_status,
        "access_methods": best_access_methods,
        "self_referral": best_self_referral,
        "uncertainty_output": uncertainty,
        "evidence": ledger.entries,
        "provenance_graph": graph.edges,
        "errors": errors,
    }


def _derive_service_name(url, extract):
    """Derive a stable service name from the URL slug, or the page title."""
    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1] if path else url
    slug = re.sub(r"-+", " ", slug).strip()
    name = slug.title() if slug else url
    if extract.get("title") and len(name) <= 3:
        name = extract["title"]
    return name


def _age_in_documented_bounds(age_bounds, age_universal, age):
    """Input-age check against documented bounds. Returns True when the page
    documents a universal offer or the age falls inside documented bounds."""
    if age_universal:
        return True
    if not age_bounds:
        return False
    low = age_bounds.get("min")
    high = age_bounds.get("max")
    if age is None:
        return low is None and high is None
    if low is not None and age < low:
        return False
    if high is not None and age > high:
        return False
    return True


def _url_matches_municipality(url, municipality):
    """Generic input-driven scoping: a known URL is admissible for a run only
    if its host contains the normalized municipality name. Mirrors live
    behavior (search queries are municipality-scoped) with no name lists or
    per-municipality branching in code."""
    def fold(s):
        s = unicodedata.normalize("NFKD", s)
        s = "".join(c for c in s if not unicodedata.combining(c))
        return s.replace("æ", "ae").replace("ø", "o").replace("å", "a")
    host = urlparse(url).netloc.lower()
    name = fold(municipality.strip().lower())
    # Domain names typically drop the ae digraph (e.g. host spellings that omit it).
    return name in host or name.replace("ae", "a") in host


def _uncertainty_wording(protocol, route_state, access_clear):
    """Return frozen uncertainty wording from the protocol."""
    u = protocol["uncertainty_outputs"]
    if route_state == "ROUTE_FULLY_VERIFIED":
        return u["VERIFIED_ROUTE"]
    if route_state in ("ROUTE_ACCESS_PARTIAL", "ROUTE_EXISTENCE_ONLY"):
        return u["SERVICE_FOUND_ACCESS_UNCLEAR"]
    return u["NO_VERIFIED_ROUTE_AFTER_PROTOCOL"]
