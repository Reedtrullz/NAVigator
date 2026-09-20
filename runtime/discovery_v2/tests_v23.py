"""V2.3 site-direct-only regression suite (task section 12 A-H + extras).

Proves the V2.3 invariants without touching historical modules: no external
search provider exists on the runtime path, credentials are absent, SPA
render fallback works without any search API, required site-direct failures
stay fail-closed, and exhaustion is only authorized after levels were
attempted.
"""

import importlib.util
import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery.protocol import ProtocolLoader  # noqa: E402
from runtime.discovery.providers import (  # noqa: E402
    FetchResult, HttpFetchProvider, ReplayFetchProvider,
)
from runtime.discovery.security import InvalidUrlError  # noqa: E402
from runtime.discovery_v2.orchestrator import run_v2  # noqa: E402
from runtime.discovery_v2.providers import (  # noqa: E402
    CompositeDiscoveryProvider, ExternalSearchProvider, SiteDirectProvider,
)
from runtime.discovery_v2.render import (  # noqa: E402
    RenderAwareFetchProvider, RenderFetchFn, RenderReplayFetchProvider,
    render_url,
)
from runtime.discovery_v2.roots import canonical_roots  # noqa: E402

PROTOCOL_PATH = REPO_ROOT / "data" / "local-service-discovery-protocol-v1.json"
RUNNER_PATH = (REPO_ROOT / "evaluation"
               / "local-discovery-site-direct-only-v2-3" / "run_official.py")

SITE_HTML = (
    "<html><body>"
    '<a href="/helse/psykisk-helse/">Psykisk helse</a>'
    '<a href="/om-kommunen/">Om kommunen</a>'
    "</body></html>"
)

RENDERED_SITE_HTML = (
    "<html><body><div id='app'>"
    '<a href="/helse/psykisk-helse/">Psykisk helse</a>'
    "</div></body></html>"
)

SITEMAP_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<urlset>"
    "<url><loc>https://www.hasvik.kommune.no/om-kommunen/</loc></url>"
    "<url><loc>https://www.hasvik.kommune.no/psykisk-helse/</loc></url>"
    "</urlset>"
)

SERVICE_PAGE = (
    "<html><head><title>Lavterskel psykisk helsehjelp</title></head><body>"
    "<p>Kommunen tilbyr lavterskel psykisk helsehjelp til voksne."
    " Du kan ta kontakt selv uten henvisning.</p>"
    "<p>Ring 12345678 for timebestilling.</p>"
    "</body></html>"
)

SEARCH_HOSTS = ("google", "bing", "duckduckgo", "brave.com", "tavily",
                "search.api", "ecosia", "startpage", "yandex", "baidu")


def fake_fetch(pages):
    def fetch_fn(url):
        return pages.get(url, (404, ""))
    return fetch_fn


def load_protocol():
    return ProtocolLoader(str(PROTOCOL_PATH)).load()


def input_for(name, age=22):
    return {"municipality": name, "municipality_number": None, "age": age,
            "need": "mental_health_low_threshold", "urgency": "non_acute"}


def load_runner():
    spec = importlib.util.spec_from_file_location("v23_run_official",
                                                  RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_v2_with_site(site, municipality, fetch_provider=None):
    comp = CompositeDiscoveryProvider([site])
    return run_v2(load_protocol(), input_for(municipality), comp,
                  fetch_provider=fetch_provider or ReplayFetchProvider({}))


class TestNoExternalRuntimePath(unittest.TestCase):
    """A: no external credentials; B: site-direct works; C: external
    unavailability cannot block site-direct execution."""

    def test_runtime_starts_without_external_credentials(self):
        runner = load_runner()
        os.environ["TAVILY_API_KEY"] = "presence-only"
        os.environ["BRAVE_API_KEY"] = "presence-only"
        try:
            scrub = runner.scrub_credentials()
            self.assertEqual(sorted(scrub["scrubbed_keys"]),
                             ["BRAVE_API_KEY", "TAVILY_API_KEY"])
            self.assertNotIn("TAVILY_API_KEY", os.environ)
            self.assertNotIn("BRAVE_API_KEY", os.environ)
            self.assertFalse(scrub["values_read"])
            self.assertFalse(scrub["values_persisted"])
        finally:
            os.environ.pop("TAVILY_API_KEY", None)
            os.environ.pop("BRAVE_API_KEY", None)
        site = SiteDirectProvider(
            fetch_fn=fake_fetch({
                "https://www.hasvik.kommune.no/": (200, SITE_HTML),
            }),
            roots=["https://www.hasvik.kommune.no/"])
        fetch = RenderReplayFetchProvider({
            "https://www.hasvik.kommune.no/helse/psykisk-helse/": {
                "content": SERVICE_PAGE, "status": 200,
                "captured_at": "FIXTURE_TIME"},
        })
        result = run_v2_with_site(site, "Hasvik", fetch_provider=fetch)
        self.assertEqual(result["execution_status"], "COMPLETE")
        self.assertTrue(result["services"])

    def test_no_external_backend_configured_site_direct_works(self):
        site = SiteDirectProvider(
            fetch_fn=fake_fetch({
                "https://www.hasvik.kommune.no/": (200, SITE_HTML),
            }),
            roots=["https://www.hasvik.kommune.no/"])
        resp = site.discover("Hasvik psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "NAVIGATION_LINK")

    def test_external_backend_unavailable_does_not_block(self):
        consulted = []

        def broken_external(query):
            consulted.append(query)
            raise OSError("network unavailable (no credentials, no backend)")

        dead = ExternalSearchProvider(fetch_fn=broken_external,
                                      min_interval_s=0)
        site = SiteDirectProvider(
            fetch_fn=fake_fetch({
                "https://www.hasvik.kommune.no/": (200, SITE_HTML),
            }),
            roots=["https://www.hasvik.kommune.no/"])
        # External listed first on purpose: even then site-direct runs.
        comp = CompositeDiscoveryProvider([dead, site])
        resp = comp.discover("Hasvik psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.provider, "site_direct")
        self.assertEqual(consulted, ["Hasvik psykisk helse voksne"])


class TestFailureSemantics(unittest.TestCase):
    """D: provider failure stays DISCOVERY_INCOMPLETE; E: exhaustion only
    after levels attempted."""

    def _run(self, pages):
        site = SiteDirectProvider(
            fetch_fn=fake_fetch(pages),
            roots=["https://www.hasvik.kommune.no/"])
        return run_v2_with_site(site, "Hasvik")

    def test_required_site_direct_failure_is_discovery_incomplete(self):
        result = self._run({
            "https://www.hasvik.kommune.no/": (403, "denied"),
        })
        self.assertEqual(result["services"], [])
        self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")
        self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertEqual(result["terminal_state"], "PUBLIC_DATA_EXHAUSTED")
        self.assertTrue(result["provider_failures"])
        self.assertEqual(result["provider_failures"][0]["status"],
                         "BOT_BLOCKED")

    def test_exhaustion_requires_levels_attempted(self):
        empty_site = ("<html><body><p>Om kommunen og kontakt oss</p>"
                      "</body></html>")
        site = SiteDirectProvider(
            fetch_fn=fake_fetch({
                "https://www.hasvik.kommune.no/": (200, empty_site),
                "https://www.hasvik.kommune.no/sitemap.xml": (404, ""),
            }),
            roots=["https://www.hasvik.kommune.no/"])
        resp = site.discover("Hasvik psykisk helse voksne")
        self.assertEqual(resp.status, "NO_RESULTS")
        steps = [a["step"] for a in resp.attempts]
        self.assertIn("root", steps)
        self.assertIn("sitemap", steps)
        result = run_v2_with_site(site, "Hasvik")
        self.assertEqual(result["terminal_state"], "PUBLIC_DATA_EXHAUSTED")
        self.assertEqual(result["services"], [])


class TestRenderFallback(unittest.TestCase):
    """F: SPA render fallback works without any search API."""

    def test_render_fetch_fn_converts_spa_shell(self):
        audit = []
        render_calls = []
        fetch_fn = RenderFetchFn(
            fake_fetch({"https://www.ralingen.kommune.no/": (200, "")}),
            render_fn=lambda url: (200, RENDERED_SITE_HTML),
            audit=audit)
        site = SiteDirectProvider(
            fetch_fn=fetch_fn,
            roots=["https://www.ralingen.kommune.no/"])
        resp = site.discover("R\u00e6lingen psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "NAVIGATION_LINK")
        self.assertEqual(fetch_fn.render_count, 1)
        self.assertIn(("http", "https://www.ralingen.kommune.no/"), audit)
        self.assertIn(("render", "https://www.ralingen.kommune.no/"), audit)
        self.assertEqual(render_calls, [])

    def test_render_failure_stays_fail_closed(self):
        fetch_fn = RenderFetchFn(
            fake_fetch({"https://www.ralingen.kommune.no/": (200, "")}),
            render_fn=lambda url: (0, ""))
        site = SiteDirectProvider(
            fetch_fn=fetch_fn,
            roots=["https://www.ralingen.kommune.no/"])
        resp = site.discover("R\u00e6lingen psykisk helse voksne")
        self.assertNotEqual(resp.status, "SUCCESS")

    def test_render_aware_provider_success_and_failure(self):
        class _FakeHttp(HttpFetchProvider):
            def fetch(self, url):
                return FetchResult(
                    url=url, status="render_required", content=None,
                    content_hash=None, fetch_method="http_get",
                    retrieved_at=None, error="RENDER_REQUIRED", final_url=url)

        class _RenderAware(RenderAwareFetchProvider, _FakeHttp):
            pass

        ok = _RenderAware(render_fn=lambda url: (200, SERVICE_PAGE))
        fr = ok.fetch("https://www.ralingen.kommune.no/artikkel/x")
        self.assertEqual(fr.status, "success")
        self.assertEqual(fr.fetch_method, "rendered_browser")
        self.assertIn("Lavterskel", fr.content)
        bad = _RenderAware(render_fn=lambda url: (0, ""))
        fr = bad.fetch("https://www.ralingen.kommune.no/artikkel/x")
        self.assertEqual(fr.status, "render_required")

    def test_render_security_blocks_private_targets(self):
        audit = []
        fetch_fn = RenderFetchFn(
            fake_fetch({"http://127.0.0.1/x": (200, "")}),
            render_fn=lambda url: (200, "should-not-render"),
            audit=audit)
        status, body = fetch_fn("http://127.0.0.1/x")
        self.assertEqual((status, body), (200, ""))
        self.assertNotIn(("render", "http://127.0.0.1/x"), audit)
        with self.assertRaises(InvalidUrlError):
            render_url("http://127.0.0.1:9222/json")

    def test_replay_render_manifest_is_explicit(self):
        fetch = RenderReplayFetchProvider(
            {}, render_manifest={
                "https://www.ralingen.kommune.no/": RENDERED_SITE_HTML})
        fr = fetch.fetch("https://www.ralingen.kommune.no/")
        self.assertEqual(fr.status, "success")
        self.assertEqual(fr.fetch_method, "rendered_browser")
        fr = fetch.fetch("https://www.ralingen.kommune.no/missing")
        self.assertEqual(fr.status, "failed")


class TestSiteDirectLevels(unittest.TestCase):
    """G: sitemap path without search API; root rule without gold."""

    def test_sitemap_path_without_search_api(self):
        site = SiteDirectProvider(
            fetch_fn=fake_fetch({
                "https://www.hasvik.kommune.no/":
                    (200, "<html><body><p>Kontakt oss</p></body></html>"),
                "https://www.hasvik.kommune.no/sitemap.xml":
                    (200, SITEMAP_XML),
            }),
            roots=["https://www.hasvik.kommune.no/"])
        resp = site.discover("Hasvik psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "SITEMAP")
        urls = [r["url"] for r in resp.results]
        self.assertIn("https://www.hasvik.kommune.no/psykisk-helse/", urls)

    def test_root_rule_tries_canonical_candidates(self):
        # V2.3 root rule (no gold): pattern candidates, not injected roots.
        site = SiteDirectProvider(fetch_fn=fake_fetch({
            "https://www.hasvik.kommune.no/": (404, ""),
            "https://hasvik.kommune.no/": (200, SITE_HTML),
        }), roots=canonical_roots("Hasvik"))
        resp = site.discover("Hasvik psykisk helse voksne")
        self.assertEqual(resp.status, "SUCCESS")
        roots = [a["url"] for a in resp.attempts if a["step"] == "root"]
        self.assertEqual(roots, ["https://www.hasvik.kommune.no/",
                                 "https://hasvik.kommune.no/"])

    def test_root_rule_transliteration_variants(self):
        # Registered domain variants: Raelingen's site lives on
        # ralingen.kommune.no (ae compressed to a); rule is pattern-based.
        roots = canonical_roots("Rælingen")
        self.assertIn("https://www.ralingen.kommune.no/", roots)
        self.assertIn("https://ralingen.kommune.no/", roots)
        site = SiteDirectProvider(fetch_fn=fake_fetch({
            "https://www.raelingen.kommune.no/": (404, ""),
            "https://raelingen.kommune.no/": (404, ""),
            "https://www.ralingen.kommune.no/": (200, ""),
        }), roots=roots)
        # Bare provider, SPA shell body: root reached but no content;
        # later roots 404 -> fail-closed PROVIDER_UNAVAILABLE, never folded
        # into NO_RESULTS (render path is what converts the shell).
        resp = site.discover("Rælingen psykisk helse voksne")
        self.assertEqual(resp.status, "PROVIDER_UNAVAILABLE")
        tried = [a["url"] for a in resp.attempts if a["step"] == "root"]
        self.assertEqual(tried, roots)


class TestNoHiddenExternalCalls(unittest.TestCase):
    """H: no hidden external HTTP search calls on the V2.3 path."""

    def test_no_search_hosts_in_v23_audit(self):
        audit = []
        site = SiteDirectProvider(
            fetch_fn=RenderFetchFn(
                fake_fetch({
                    "https://www.hasvik.kommune.no/": (200, SITE_HTML),
                }),
                audit=audit),
            roots=["https://www.hasvik.kommune.no/"])
        fetch = RenderReplayFetchProvider({
            "https://www.hasvik.kommune.no/helse/psykisk-helse/": {
                "content": SERVICE_PAGE, "status": 200,
                "captured_at": "FIXTURE_TIME"},
        })
        result = run_v2_with_site(site, "Hasvik", fetch_provider=fetch)
        self.assertEqual(result["execution_status"], "COMPLETE")
        for kind, url in audit:
            self.assertFalse(any(h in url.lower() for h in SEARCH_HOSTS),
                             "external search host in audit: %s" % url)
            self.assertIn(kind, ("http", "render"))


class TestCodeHygiene(unittest.TestCase):
    def test_no_case_ids_or_search_backends_in_v23_code(self):
        for rel in ("runtime/discovery_v2/render.py",
                    "evaluation/local-discovery-site-direct-only-v2-3/"
                    "run_official.py"):
            src = (REPO_ROOT / rel).read_text()
            self.assertIsNone(re.search(r"RC1B|RC2B", src), rel)
            self.assertNotIn("make_brave_provider", src, rel)
            self.assertNotIn("make_tavily_provider", src, rel)


if __name__ == "__main__":
    unittest.main()
