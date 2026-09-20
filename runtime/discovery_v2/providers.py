"""Provider contract V2: canonical statuses, health, classification, and
composable discovery providers.

Providers only discover candidate URLs. All access classification and route
evaluation stays in runtime.discovery (frozen, no semantic rewrite).
"""

import re
import time
import unicodedata
from urllib.parse import urljoin

from runtime.discovery.security import InvalidUrlError, validate_url

try:
    from .sitemap_fetch import bounded_fetch as _default_bounded_fetch
except ImportError:  # direct-module import contexts
    _default_bounded_fetch = None

CANONICAL_STATUSES = [
    "SUCCESS", "NO_RESULTS", "RATE_LIMITED", "BOT_BLOCKED",
    "AUTH_REQUIRED", "PROVIDER_UNAVAILABLE", "TIMEOUT",
    "INVALID_RESPONSE", "INTERNAL_ERROR",
]

# Markers observed in verified bot-block/anomaly pages (DDG 202 body, Bing
# challenge page). A page matching these is never classified NO_RESULTS.
BOT_MARKERS = re.compile(
    r"(captcha|unusual traffic|verify you are (?:a )?human|are you a robot|"
    r"access denied|just a moment|anomaly|bot detection|challenge)",
    re.IGNORECASE,
)

MIN_VALID_BODY_BYTES = 3000

# Bounded challenge-scan window (V2.1): challenge evidence is scanned over
# the full response body within the existing response-size cap; never
# unbounded memory scanning.
MAX_SCAN_BYTES = 2 * 1024 * 1024


def _has_html_structure(body):
    """A 2xx body without HTML document structure cannot establish a
    valid empty result set."""
    low = (body or "").lower()
    return "<html" in low and "</html>" in low


class ProviderResponse:
    """Canonical V2 provider result (contract v2 schema)."""

    def __init__(self, query, status, results=None, error=None, provider="",
                 latency_ms=0, discovery_method=None):
        assert status in CANONICAL_STATUSES, status
        self.query = query
        self.status = status
        self.results = results or []
        self.error = error
        self.provider = provider
        self.latency_ms = latency_ms
        self.discovery_method = discovery_method
        self.fallback_log = []
        self.attempts = []

    def to_dict(self):
        return {
            "query": self.query,
            "status": self.status,
            "results": list(self.results),
            "error": self.error,
            "provider": self.provider,
            "latency_ms": self.latency_ms,
            "discovery_method": self.discovery_method,
            "fallback_log": list(self.fallback_log),
            "attempts": list(self.attempts),
        }


class ProviderHealth:
    """Explicit health/readiness state per provider."""

    def __init__(self, provider):
        self.provider = provider
        self.successful_queries = 0
        self.attempted_queries = 0
        self.failure_class = None

    def record(self, status):
        self.attempted_queries += 1
        if status == "SUCCESS":
            self.successful_queries += 1
        else:
            self.failure_class = status

    @property
    def healthy(self):
        if self.attempted_queries == 0:
            return True  # untested providers start as ready
        rate = self.successful_queries / self.attempted_queries
        return rate >= 0.5 and self.failure_class != "BOT_BLOCKED"

    def to_dict(self):
        return {
            "provider": self.provider,
            "healthy": self.healthy,
            "failure_class": self.failure_class,
            "successful_queries": self.successful_queries,
            "attempted_queries": self.attempted_queries,
        }


def classify_http_response(status_code, body, parsed_results=None):
    """Map a search-backend HTTP fetch to a canonical status.

    V2.1 frozen order: transport failure, explicit HTTP status, challenge
    content (bounded scan), parsed results, validity, NO_RESULTS last.
    """
    if status_code == 0:
        return "PROVIDER_UNAVAILABLE"
    if status_code == 429:
        return "RATE_LIMITED"
    if status_code == 401:
        return "AUTH_REQUIRED"
    if status_code == 403:
        return "BOT_BLOCKED"
    if status_code >= 500:
        return "PROVIDER_UNAVAILABLE"
    if status_code >= 400:
        return "INVALID_RESPONSE"
    scan = (body or "")[:MAX_SCAN_BYTES]
    if BOT_MARKERS.search(scan):
        return "BOT_BLOCKED"
    if parsed_results:
        return "SUCCESS"
    if not _has_html_structure(scan):
        return "INVALID_RESPONSE"
    if len(scan) < MIN_VALID_BODY_BYTES:
        return "INVALID_RESPONSE"
    return "NO_RESULTS"


class ExternalSearchProvider:
    """Replaceable external search backend behind the V2 contract.

    fetch_fn(query) -> (status_code:int, body:str); parser(body) -> list of
    {"url", "title", "snippet"}. A frozen per-run query budget and minimum
    interval prevent retry storms. No evasion of any kind.
    """

    def __init__(self, fetch_fn, parser=None, provider_id="external_search",
                 max_queries_per_run=3, min_interval_s=10.0):
        self.fetch_fn = fetch_fn
        self.parser = parser
        self.provider_id = provider_id
        self.max_queries_per_run = max_queries_per_run
        self.min_interval_s = min_interval_s
        self._used = 0
        self._last_call = None
        self.health = ProviderHealth(provider_id)

    def discover(self, query):
        if self._used >= self.max_queries_per_run:
            return ProviderResponse(
                query=query, status="RATE_LIMITED", provider=self.provider_id,
                error="QUERY_BUDGET_EXHAUSTED")
        if self._last_call is not None:
            wait = self.min_interval_s - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
        self._last_call = time.monotonic()
        self._used += 1
        self._last_transport = None
        try:
            transport = self.fetch_fn(query)
            if isinstance(transport, dict):
                status_code = transport.get("http_status") or 0
                body = transport.get("body", "")
                self._last_transport = transport
            else:
                status_code, body = transport
            parsed = self.parser(body) if self.parser else []
        except TimeoutError:
            resp = ProviderResponse(query=query, status="TIMEOUT",
                                    provider=self.provider_id,
                                    error="BACKEND_TIMEOUT")
            self.health.record(resp.status)
            return resp
        except Exception as exc:  # untrusted backend: fail closed
            resp = ProviderResponse(query=query, status="INTERNAL_ERROR",
                                    provider=self.provider_id,
                                    error="BACKEND_ERROR: %s" % exc)
            self.health.record(resp.status)
            return resp
        status = classify_http_response(status_code, body, parsed)
        results = [
            {"url": r.get("url", ""), "title": r.get("title", ""),
             "snippet": r.get("snippet", ""), "provider": self.provider_id,
             "rank": i}
            for i, r in enumerate(parsed or [], start=1)
        ]
        error = None if status in ("SUCCESS", "NO_RESULTS") else status
        resp = ProviderResponse(query=query, status=status, results=results,
                                provider=self.provider_id, error=error)
        if self._last_transport:
            resp.attempts.append(self._last_transport)
        self.health.record(resp.status)
        return resp


NAV_KEYWORDS = ("psykisk", "helse", "rus", "mestring", "ung", "voksen")
MAX_SITE_RESULTS = 20

# Per-municipality URL budget (frozen policy): bounded pages, bounded
# attempts, no retry storms (task 24: bounded fetches).
MAX_SITE_URLS_PER_MUNICIPALITY = 8


def _fold(name):
    s = unicodedata.normalize("NFKD", name.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\u00e6", "ae").replace("\u00f8", "o").replace("\u00e5", "a")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


class SiteDirectProvider:
    """Discover candidates on the municipality's own site, no external
    engine: root -> keyword navigation links -> sitemap (protocol levels 0-3).

    The municipality token is the first word of a frozen query template
    ("<kommune> ..."), so per-query calls share one cached site scan.
    """

    def __init__(self, fetch_fn, roots=None, provider_id="site_direct",
                 sitemap_fetch_fn=None):
        self.fetch_fn = fetch_fn
        self.roots = roots  # optional known municipal roots (Stage A)
        self.provider_id = provider_id
        self.sitemap_fetch_fn = sitemap_fetch_fn or _default_bounded_fetch
        self._url_budget = MAX_SITE_URLS_PER_MUNICIPALITY
        self._cache = {}
        self.health = ProviderHealth(provider_id)

    def discover(self, query):
        municipality = query.split()[0]
        slug = _fold(municipality)
        if slug in self._cache:
            return self._cache[slug]
        attempts = []
        if self.roots:
            candidates = list(self.roots)
        else:
            candidates = ["https://www.%s.kommune.no/" % slug]
        results = []
        final_status = "NO_RESULTS"
        method = None
        for root in candidates:
            status, body = self._get(root)
            attempts.append({"step": "root", "url": root, "status": status})
            if status != "OK":
                final_status = status
                continue
            results = self._nav_links(body, root)
            if results:
                final_status = "SUCCESS"
                method = "NAVIGATION_LINK"
                break
            sitemap_url = urljoin(root, "sitemap.xml")
            sm_status, sm_body = self._get(sitemap_url)
            attempts.append({"step": "sitemap", "url": sitemap_url,
                             "status": sm_status})
            if sm_status == "OK":
                results = self._sitemap_urls(sm_body)
                if results:
                    final_status = "SUCCESS"
                    method = "SITEMAP"
                    break
            final_status = "NO_RESULTS"
        resp = ProviderResponse(
            query=query, status=final_status,
            results=[{"url": r["url"], "title": r["title"], "snippet": "",
                      "provider": self.provider_id, "rank": i}
                     for i, r in enumerate(results, start=1)],
            provider=self.provider_id,
            discovery_method=method,
            error=None if final_status in ("SUCCESS", "NO_RESULTS")
            else final_status,
        )
        resp.attempts = attempts
        self.health.record(final_status)
        self._cache[slug] = resp
        return resp

    def _get(self, url):
        try:
            validate_url(url)
        except InvalidUrlError:
            return ("INVALID_RESPONSE", "")
        if self._url_budget <= 0:
            return ("RATE_LIMITED", "")
        self._url_budget -= 1
        try:
            status_code, body = self.fetch_fn(url)
        except TimeoutError:
            return ("TIMEOUT", "")
        except Exception:
            return ("PROVIDER_UNAVAILABLE", "")
        if status_code == 0:
            return ("PROVIDER_UNAVAILABLE", body)
        if status_code == 429:
            return ("RATE_LIMITED", body)
        if status_code == 401:
            return ("AUTH_REQUIRED", body)
        if status_code == 403:
            return ("BOT_BLOCKED", body)
        if status_code >= 400:
            return ("PROVIDER_UNAVAILABLE", body)
        return ("OK", body or "")

    @staticmethod
    def _nav_links(html, base_url):
        results, seen = [], set()
        for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', html,
                             re.DOTALL | re.IGNORECASE):
            href = m.group(1).strip()
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            absolute = urljoin(base_url, href)
            if not absolute.startswith(("http://", "https://")):
                continue
            try:
                validate_url(absolute)
            except InvalidUrlError:
                continue
            text = re.sub(r"<[^>]+>", " ", m.group(2))
            text = re.sub(r"\s+", " ", text).strip()
            haystack = (text + " " + absolute).lower()
            if not any(k in haystack for k in NAV_KEYWORDS):
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            results.append({"url": absolute, "title": text, "snippet": ""})
            if len(results) >= MAX_SITE_RESULTS:
                break
        return results

    @staticmethod
    def _sitemap_urls(xml):
        results, seen = [], set()
        for m in re.finditer(r"<loc>([^<]+)</loc>", xml):
            url = m.group(1).strip()
            if not url.startswith(("http://", "https://")):
                continue
            try:
                validate_url(url)
            except InvalidUrlError:
                continue
            if not any(k in url.lower() for k in NAV_KEYWORDS):
                continue
            if url in seen:
                continue
            seen.add(url)
            results.append({"url": url, "title": "", "snippet": ""})
            if len(results) >= MAX_SITE_RESULTS:
                break
        return results


class CompositeDiscoveryProvider:
    """Deterministic frozen provider ordering; every switch is logged."""

    def __init__(self, providers):
        self.providers = list(providers)

    def discover(self, query):
        fallback_log = []
        last = None
        for provider in self.providers:
            resp = provider.discover(query)
            if resp.status == "SUCCESS" and resp.results:
                clone = self._clone(resp, fallback_log)
                return clone
            fallback_log.append({
                "provider": getattr(provider, "provider_id", "unknown"),
                "status": resp.status,
                "fallback_authorized": True,
            })
            last = resp
        if last is None:
            last = ProviderResponse(query=query, status="INTERNAL_ERROR",
                                    provider="composite", error="NO_PROVIDERS")
        return self._clone(last, fallback_log)

    def health(self):
        out = []
        for p in self.providers:
            h = getattr(p, "health", None)
            if h is not None:
                out.append(h.to_dict())
        return out

    @staticmethod
    def _clone(resp, fallback_log):
        clone = ProviderResponse(
            query=resp.query, status=resp.status, results=list(resp.results),
            error=resp.error, provider=resp.provider,
            latency_ms=resp.latency_ms,
            discovery_method=resp.discovery_method)
        clone.fallback_log = list(fallback_log)
        clone.attempts = list(getattr(resp, "attempts", []) or [])
        return clone
