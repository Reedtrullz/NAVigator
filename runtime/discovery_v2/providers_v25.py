"""V2.5 discovery provider: bounded sitemapindex traversal and
render-on-empty-extraction, as a new-lineage subclass of the frozen
SiteDirectProviderV23. No case IDs, no municipality names, no gold URLs.

Root causes repaired (from the frozen V2.4 holdout mismatch analysis,
generalized to platform patterns, never to individual cases):
1. WordPress sitemapindex responses list child sitemaps; the frozen
   extractor only reads <loc> entries and keyword-filters URL paths, so an
   index with zero direct page URLs yields zero candidates even though the
   children list them. Fix: when direct extraction is empty and the body is
   a sitemapindex, fetch child sitemaps (bounded) and extract from them.
2. SPA-menu platforms return root HTML where static anchors are absent;
   renderer was never triggered because rendering only happened via the
   SPA-shell contract (200, ""). Fix: when a root is OK, nav links and
   sitemap both yield zero candidates, render the root once (bounded) and
   extract nav links from the rendered DOM. Fail closed: render failure
   keeps the NO_RESULTS path.
"""

import re

try:
    from .sitemap_fetch import bounded_fetch as _default_sitemap_fetch
except ImportError:  # direct-module import contexts
    _default_sitemap_fetch = None

from .providers import (
    MAX_SITE_RESULTS, NAV_KEYWORDS, ProviderResponse, SiteDirectProvider,
)
from urllib.parse import urljoin

from runtime.discovery.security import InvalidUrlError, validate_url

from .providers import _fold
from .render import render_url


SITEMAP_INDEX_MARKER = re.compile(
    r"<sitemapindex[\s>]|<sitemap>", re.IGNORECASE)
LOC_RE = re.compile(r"<loc>([^<]+)</loc>", re.IGNORECASE)
MAX_SITEMAP_INDEX_CHILDREN = 4


class SiteDirectProviderV25(SiteDirectProvider):
    """SiteDirectProviderV23 (budget 16) + index traversal + root render.

    The parent's discover() is reused until it produces zero results; this
    subclass only ADDS fallback steps after the frozen logic yields nothing,
    so every previously successful path is byte-identical in behavior.
    """

    def __init__(self, fetch_fn, roots=None, provider_id="site_direct",
                 sitemap_fetch_fn=None, render_fn=render_url):
        super().__init__(fetch_fn, roots=roots, provider_id=provider_id,
                         sitemap_fetch_fn=sitemap_fetch_fn)
        # V23/V24 parity: several root variants per municipality are probed
        # before the working platform root; the frozen base budget (8)
        # exhausts before the live root is reached. Same raised budget as
        # SiteDirectProviderV23 (16), still bounded.
        self._url_budget = 16
        self._render_fn = render_fn

    def discover(self, query):
        resp = super().discover(query)
        if resp.status == "SUCCESS" and resp.results:
            return resp
        # Frozen parent returned NO_RESULTS (or a failure). The parent has
        # already consumed URL budget for its attempts; add bounded extra
        # budget for the new fallback steps only.
        saved_budget = self._url_budget
        self._url_budget = max(saved_budget, 4)
        try:
            for root in self._candidate_roots():
                candidates = self._index_children(root)
                if candidates:
                    return self._success(query, candidates, root,
                                         "SITEMAP_INDEX_FOLLOW",
                                         [a for a in resp.attempts])
                candidates = self._rendered_nav_links(root)
                if candidates:
                    return self._success(query, candidates, root,
                                         "RENDERED_NAVIGATION_LINK",
                                         [a for a in resp.attempts])
            return resp
        finally:
            self._url_budget = saved_budget

    # -- helpers ----------------------------------------------------------

    def _candidate_roots(self):
        if self.roots:
            return list(self.roots)
        return []

    def _get(self, url):
        # Reuse the parent's bounded, validated fetch (budget-aware).
        return SiteDirectProvider._get(self, url)

    def _success(self, query, candidates, root, method, attempts):
        slug = _fold(query.split()[0])
        results = [{"url": r["url"], "title": r.get("title", ""),
                    "snippet": "", "provider": self.provider_id, "rank": i}
                   for i, r in enumerate(candidates, start=1)]
        resp = ProviderResponse(
            query=query, status="SUCCESS", results=results,
            provider=self.provider_id, discovery_method=method,
            error=None)
        resp.attempts = list(attempts) + [
            {"step": "v25_" + method.lower(), "url": root,
             "status": "OK"}]
        self.health.record("SUCCESS")
        # Overwrite the parent's cached NO_RESULTS for this municipality so
        # later planner queries hit the successful fallback result.
        self._cache[slug] = resp
        return resp

    def _sitemap_urls(self, xml):
        # Reuse the frozen extractor (keyword filter + validation + cap).
        return SiteDirectProvider._sitemap_urls(xml)

    def _index_children(self, root):
        sm_url = urljoin(root, "sitemap.xml")
        sm_status, sm_body = self._get(sm_url)
        if sm_status != "OK" or not sm_body:
            return []
        if not SITEMAP_INDEX_MARKER.search(sm_body[:4000]):
            return []
        if "<urlset" in sm_body[:4000].lower():
            return []
        results, seen = [], set()
        for loc in LOC_RE.findall(sm_body)[:MAX_SITEMAP_INDEX_CHILDREN]:
            child = loc.strip()
            if not child.startswith(("http://", "https://")):
                continue
            try:
                validate_url(child)
            except InvalidUrlError:
                continue
            c_status, c_body = self._get(child)
            if c_status != "OK" or not c_body:
                continue
            for r in self._sitemap_urls(c_body):
                if r["url"] in seen:
                    continue
                seen.add(r["url"])
                results.append(r)
                if len(results) >= MAX_SITE_RESULTS:
                    return results
        return results

    def _rendered_nav_links(self, root):
        if self._url_budget <= 0:
            return []
        self._url_budget -= 1
        try:
            status, dom = self._render_fn(root)
        except Exception:
            return []
        if status != 200 or not dom:
            return []
        return self._nav_links(dom, root)

    def _nav_links(self, html, base_url):
        return SiteDirectProvider._nav_links(html, base_url)
