"""V2.5 unit tests: discovery fallbacks + FV provenance gate.

Purely offline: fake fetch/render functions, no network. Run with:
  python -m unittest runtime.discovery_v2.tests_v25
"""

import unittest
from urllib.parse import urlparse

from runtime.discovery_v2.providers_v25 import SiteDirectProviderV25
from runtime.discovery_v2.classification_gate_v25 import is_service_specific_url
from runtime.discovery_v2.classification_v25 import RouteEvaluatorV25


ROOT_HTML = (
    '<html><body>'
    '<a href="/tjenester/psykisk-helse/">Psykisk helse</a>'
    '</body></html>'
)
INDEX_XML = (
    '<?xml version="1.0"?><sitemapindex>'
    '<sitemap><loc>https://x.bedreinnsats.no/wp-sitemap-posts-page-1.xml</loc></sitemap>'
    '</sitemapindex>'
)
CHILD_XML = (
    '<?xml version="1.0"?><urlset>'
    '<url><loc>https://x.bedreinnsats.no/ung/psykisk-helse/</loc></url>'
    '</urlset>'
)


class FakeFetch:
    """(status, body) fetch_fn with a per-URL script."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        return self.responses.get(url, (404, ""))


def make_provider(responses, render_dom=None):
    fetch = FakeFetch(responses)

    def render_fn(url):
        return (200, render_dom) if render_dom else (0, "")

    prov = SiteDirectProviderV25(
        fetch_fn=fetch, roots=["https://x.example.com/"], render_fn=render_fn)
    return prov, fetch


class TestSitemapIndexFollow(unittest.TestCase):
    def test_index_children_become_candidates(self):
        responses = {
            "https://x.example.com/": (200, "<html>nav</html>"),
            "https://x.example.com/sitemap.xml": (200, INDEX_XML),
            "https://x.bedreinnsats.no/wp-sitemap-posts-page-1.xml": (200, CHILD_XML),
        }
        prov, _ = make_provider(responses)
        resp = prov.discover("Test psykisk helse")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "SITEMAP_INDEX_FOLLOW")
        self.assertTrue(any("psykisk-helse" in r["url"] for r in resp.results))


class TestRenderOnEmptyExtraction(unittest.TestCase):
    def test_rendered_root_yields_nav_links(self):
        responses = {
            "https://x.example.com/": (200, "<html><body>js menu</body></html>"),
            "https://x.example.com/sitemap.xml": (404, ""),
        }
        prov, _ = make_provider(responses, render_dom=ROOT_HTML)
        resp = prov.discover("Test psykisk helse")
        self.assertEqual(resp.status, "SUCCESS")
        self.assertEqual(resp.discovery_method, "RENDERED_NAVIGATION_LINK")

    def test_render_failure_stays_no_results(self):
        responses = {
            "https://x.example.com/": (200, "<html><body>js menu</body></html>"),
            "https://x.example.com/sitemap.xml": (404, ""),
        }
        prov, _ = make_provider(responses, render_dom=None)
        resp = prov.discover("Test psykisk helse")
        self.assertEqual(resp.status, "NO_RESULTS")


class TestFvProvenanceGate(unittest.TestCase):
    def test_section_page_capped(self):
        ev = RouteEvaluatorV25()
        state = ev.evaluate(
            service_verified=True, eligibility_verified=True,
            access_methods=["DIRECT_PHONE"], access_clear=True,
            contact_documented=True, strong_access=True,
            url="https://www.gjesdal.example/tjenester/barnehage-skole-og-familie/")
        self.assertEqual(state, "ROUTE_ACCESS_PARTIAL")

    def test_service_page_keeps_fv(self):
        ev = RouteEvaluatorV25()
        state = ev.evaluate(
            service_verified=True, eligibility_verified=True,
            access_methods=["DIRECT_PHONE"], access_clear=True,
            contact_documented=True, strong_access=True,
            url="https://www.sola.example/tjenester/rask-psykisk-helsehjelp/")
        self.assertEqual(state, "ROUTE_FULLY_VERIFIED")

    def test_generic_slug_rule(self):
        self.assertFalse(is_service_specific_url(
            "https://www.sola.example/helse-og-sosial/"))
        self.assertTrue(is_service_specific_url(
            "https://www.moss.example/alle-tjenester/helse-omsorg-og-mestring/psykisk-helse/"))
        self.assertFalse(is_service_specific_url(
            "https://www.moss.example/tjenester/"))


class TestParentPathUnchanged(unittest.TestCase):
    def test_frozen_success_path_still_wins(self):
        # Parent nav-link success must return identical method/urls, with no
        # extra fetches from the fallback layer.
        responses = {
            "https://x.example.com/": (200, ROOT_HTML),
        }
        prov, fetch = make_provider(responses, render_dom=ROOT_HTML)
        resp = prov.discover("Test psykisk helse")
        self.assertEqual(resp.discovery_method, "NAVIGATION_LINK")
        self.assertEqual([c for c in fetch.calls if "sitemap" in c], [])


if __name__ == "__main__":
    unittest.main()
