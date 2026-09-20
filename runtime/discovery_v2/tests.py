"""unittest suite for discovery runtime V2 (stdlib only).

Failure simulations prove the core invariant: a provider failure is never
folded into NO_RESULTS and never produces a false NO_LOCAL_MATCH.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery.engine import ServiceExtractor  # noqa: E402
from runtime.discovery.protocol import ProtocolLoader, EXPECTED_PROTOCOL_SHA  # noqa: E402
from runtime.discovery.providers import ReplayFetchProvider  # noqa: E402
from runtime.discovery.security import validate_url  # noqa: E402

from runtime.discovery_v2.brave import brave_parser, make_brave_provider  # noqa: E402
from runtime.discovery_v2.orchestrator import run_v2  # noqa: E402
from runtime.discovery_v2.providers import (  # noqa: E402
    CompositeDiscoveryProvider, ExternalSearchProvider, ProviderHealth,
    ProviderResponse, SiteDirectProvider, classify_http_response,
)


PROTOCOL_PATH = REPO_ROOT / "data" / "local-service-discovery-protocol-v1.json"

ANOMALY_BODY = (
    "<html><head><title>Attention Required</title></head><body>"
    "<h2>Captcha</h2><p>Verify you are a human to continue.</p></body></html>"
)

SITE_HTML = (
    '<html><body>'
    '<a href="/helse/psykisk-helse/">Psykisk helse</a>'
    '<a href="/tjenester/rus-og-avhengighet/">Rus og avhengighet</a>'
    '<a href="/om-kommunen/">Om kommunen</a>'
    '</body></html>'
)

SERVICE_PAGE = (
    '<html><head><title>Lavterskel psykisk helsehjelp</title></head><body>'
    '<p>Kommunen tilbyr lavterskel psykisk helsehjelp til voksne.'
    ' Du kan ta kontakt selv uten henvisning.</p>'
    '<p>Ring 12345678 for timebestilling.</p>'
    '</body></html>'
)


def fake_fetch_factory(pages=None):
    pages = pages or {}

    def fetch_fn(url):
        if url in pages:
            return pages[url]
        return (404, "")
    return fetch_fn


def load_protocol():
    return ProtocolLoader(str(PROTOCOL_PATH)).load()


def input_for(name):
    return {"municipality": name, "municipality_number": None, "age": 22,
            "need": "mental_health_low_threshold", "urgency": "non_acute"}


class TestClassifyHttpResponse(unittest.TestCase):
    def test_canonical_statuses_complete(self):
        from runtime.discovery_v2.providers import CANONICAL_STATUSES
        self.assertEqual(set(CANONICAL_STATUSES), {
            "SUCCESS", "NO_RESULTS", "RATE_LIMITED", "BOT_BLOCKED",
            "AUTH_REQUIRED", "PROVIDER_UNAVAILABLE", "TIMEOUT",
            "INVALID_RESPONSE", "INTERNAL_ERROR"})

    def test_429_is_rate_limited(self):
        self.assertEqual(classify_http_response(429, ""), "RATE_LIMITED")

    def test_403_is_bot_blocked(self):
        self.assertEqual(classify_http_response(403, ""), "BOT_BLOCKED")

    def test_anomaly_page_is_bot_blocked_not_no_results(self):
        # Verified DDG anomaly shape: HTTP 202, tiny body, bot markers.
        self.assertEqual(classify_http_response(202, ANOMALY_BODY, []),
                         "BOT_BLOCKED")

    def test_empty_parse_without_markers_is_no_results(self):
        body = "<html><body>" + ("x" * 4000) + "</body></html>"
        self.assertEqual(classify_http_response(200, body, []), "NO_RESULTS")

    def test_parsed_results_success(self):
        parsed = [{"url": "https://x.kommune.no/", "title": "t"}]
        self.assertEqual(classify_http_response(200, "ok", parsed), "SUCCESS")


class TestProviderHealth(unittest.TestCase):
    def test_untested_is_healthy(self):
        self.assertTrue(ProviderHealth("p").healthy)

    def test_blocked_is_unhealthy(self):
        h = ProviderHealth("p")
        h.record("BOT_BLOCKED")
        self.assertFalse(h.healthy)
        self.assertEqual(h.to_dict()["failure_class"], "BOT_BLOCKED")

    def test_majority_success_is_healthy(self):
        h = ProviderHealth("p")
        h.record("SUCCESS")
        h.record("NO_RESULTS")
        h.record("SUCCESS")
        self.assertTrue(h.healthy)


class TestExternalSearchProvider(unittest.TestCase):
    def test_budget_exhaustion_is_rate_limited(self):
        calls = []

        def fetch_fn(q):
            calls.append(q)
            return (200, "<html><a href='https://a.kommune.no/psykisk'>x</a></html>")
        p = ExternalSearchProvider(fetch_fn=fetch_fn, parser=brave_parser,
                                   max_queries_per_run=2, min_interval_s=0)
        for _ in range(2):
            p.discover("q")
        resp = p.discover("q3")
        self.assertEqual(resp.status, "RATE_LIMITED")
        self.assertEqual(resp.error, "QUERY_BUDGET_EXHAUSTED")
        self.assertEqual(len(calls), 2)

    def test_timeout_classified(self):
        def fetch_fn(q):
            raise TimeoutError("t")
        p = ExternalSearchProvider(fetch_fn=fetch_fn, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "TIMEOUT")

    def test_backend_exception_fail_closed(self):
        def fetch_fn(q):
            raise RuntimeError("boom")
        p = ExternalSearchProvider(fetch_fn=fetch_fn, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "INTERNAL_ERROR")


class TestBraveParser(unittest.TestCase):
    def test_extracts_external_links_excluding_brave(self):
        html = ('<a href="https://search.brave.com/help">help</a>'
                '<a href="https://bamble.kommune.no/psykisk">Bamble psykisk</a>')
        out = brave_parser(html)
        self.assertEqual([r["url"] for r in out],
                         ["https://bamble.kommune.no/psykisk"])


class TestSiteDirectProvider(unittest.TestCase):
    def test_nav_link_discovery(self):
        fetch_fn = fake_fetch_factory({
            "https://www.bamble.kommune.no/": (200, SITE_HTML),
        })
        p = SiteDirectProvider(fetch_fn=fetch_fn)
        resp = p.discover("Bamble psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "NAVIGATION_LINK")
        urls = [r["url"] for r in resp.results]
        self.assertIn("https://www.bamble.kommune.no/helse/psykisk-helse/", urls)
        self.assertNotIn("https://www.bamble.kommune.no/om-kommunen/", urls)

    def test_sitemap_fallback(self):
        fetch_fn = fake_fetch_factory({
            "https://www.bamble.kommune.no/": (200, "<html><body>tom</body></html>"),
            "https://www.bamble.kommune.no/sitemap.xml": (
                200, "<urlset><url><loc>https://www.bamble.kommune.no/psykisk-helse</loc></url></urlset>"),
        })
        p = SiteDirectProvider(fetch_fn=fetch_fn)
        resp = p.discover("Bamble psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "SITEMAP")

    def test_bot_blocked_root_is_not_no_results(self):
        fetch_fn = fake_fetch_factory({
            "https://www.bamble.kommune.no/": (403, "denied"),
        })
        p = SiteDirectProvider(fetch_fn=fetch_fn)
        resp = p.discover("Bamble psykisk helse voksne")
        self.assertEqual(resp.status, "BOT_BLOCKED")

    def test_known_roots_stage_a(self):
        fetch_fn = fake_fetch_factory({
            "https://ralingen.bedreinnsats.no/": (200, SITE_HTML),
        })
        p = SiteDirectProvider(fetch_fn=fetch_fn,
                               roots=["https://ralingen.bedreinnsats.no/"])
        resp = p.discover("Rælingen psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")

    def test_private_root_rejected(self):
        p = SiteDirectProvider(fetch_fn=fake_fetch_factory(),
                               roots=["file:///etc/passwd"])
        resp = p.discover("Bamble psykisk helse voksne")
        self.assertNotEqual(resp.status, "SUCCESS")


class TestComposite(unittest.TestCase):
    def test_no_silent_fallback_logged(self):
        bad = SiteDirectProvider(fetch_fn=fake_fetch_factory(),
                                 roots=["https://x.example/"])
        bad.provider_id = "site_direct"
        good = ExternalSearchProvider(
            fetch_fn=lambda q: (200, '<a href="https://bamble.kommune.no/psykisk">p</a>'),
            parser=brave_parser, provider_id="brave_html", min_interval_s=0)
        comp = CompositeDiscoveryProvider([bad, good])
        resp = comp.discover("Bamble psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.fallback_log[0]["provider"], "site_direct")
        self.assertTrue(resp.fallback_log[0]["fallback_authorized"])

    def test_all_failures_preserved(self):
        blocked = SiteDirectProvider(fetch_fn=fake_fetch_factory(),
                                     roots=["https://x.example/"])
        rate = ExternalSearchProvider(fetch_fn=lambda q: (429, ""),
                                      min_interval_s=0)
        comp = CompositeDiscoveryProvider([blocked, rate])
        resp = comp.discover("Bamble psykisk helse voksne")
        self.assertEqual(resp.status, "RATE_LIMITED")
        self.assertEqual([f["status"] for f in resp.fallback_log],
                         ["PROVIDER_UNAVAILABLE", "RATE_LIMITED"])


class TestOrchestratorV2(unittest.TestCase):
    def _run(self, pages, municipality="Bamble"):
        protocol = load_protocol()
        site = SiteDirectProvider(
            fetch_fn=fake_fetch_factory(pages),
            roots=["https://www.%s.kommune.no/" % municipality.lower()])
        comp = CompositeDiscoveryProvider([site])
        fetch = ReplayFetchProvider({
            "https://www.%s.kommune.no/helse/psykisk-helse/" % municipality.lower(): {
                "content": SERVICE_PAGE, "status": 200, "captured_at": "FIXTURE_TIME"},
        })
        return run_v2(protocol, input_for(municipality), comp,
                      fetch_provider=fetch)

    def test_end_to_end_service_found(self):
        result = self._run({
            "https://www.bamble.kommune.no/": (200, SITE_HTML),
        })
        self.assertEqual(result["runtime"], "discovery_v2")
        self.assertEqual(result["protocol_sha256"], EXPECTED_PROTOCOL_SHA)
        self.assertTrue(result["services"])
        self.assertEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")
        self.assertEqual(result["terminal_state"], "ACCESS_VERIFIED")
        self.assertEqual(result["execution_status"], "COMPLETE")

    def test_provenance_edges_present(self):
        result = self._run({
            "https://www.bamble.kommune.no/": (200, SITE_HTML),
        })
        self.assertTrue(result["provenance_graph"])
        edge = result["provenance_graph"][0]
        self.assertEqual(edge["discovery_method"], "NAVIGATION_LINK")

    def test_provider_failure_is_not_no_local_match(self):
        # Site root blocked: provider failure must not fabricate a service.
        result = self._run({
            "https://www.bamble.kommune.no/": (403, "denied"),
        })
        self.assertEqual(result["services"], [])
        self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")
        self.assertTrue(result["provider_failures"])
        self.assertEqual(result["provider_failures"][0]["status"],
                         "BOT_BLOCKED")

    def test_unsupported_fully_verified_impossible(self):
        # Search result alone (no fetchable page) cannot verify a route:
        # provenance invariant. Candidate page missing -> no services.
        protocol = load_protocol()
        site = SiteDirectProvider(
            fetch_fn=fake_fetch_factory({
                "https://www.bamble.kommune.no/": (200, SITE_HTML),
            }),
            roots=["https://www.bamble.kommune.no/"])
        comp = CompositeDiscoveryProvider([site])
        result = run_v2(protocol, input_for("Bamble"), comp,
                        fetch_provider=ReplayFetchProvider({}))
        self.assertEqual(result["services"], [])
        self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")

    def test_extract_only_real_service_text(self):
        ex = ServiceExtractor().extract(SERVICE_PAGE,
                                        "https://www.bamble.kommune.no/x")
        self.assertTrue(ex["access_markers"]["explicit_self_contact"])


class TestFrozenCompliance(unittest.TestCase):
    def test_protocol_unchanged(self):
        loader = ProtocolLoader(str(PROTOCOL_PATH))
        loader.load()
        self.assertEqual(loader.actual_sha, EXPECTED_PROTOCOL_SHA)

    def test_no_municipality_names_in_v2_code(self):
        for f in ("providers.py", "brave.py", "orchestrator.py", "cli.py"):
            src = (REPO_ROOT / "runtime" / "discovery_v2" / f).read_text(
                encoding="utf-8")
            self.assertNotIn("Bamble", src)
            self.assertNotIn("Rælingen", src)


if __name__ == "__main__":
    unittest.main()
