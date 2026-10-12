"""SearchProvider and FetchProvider abstractions with replay-first implementations.

The runtime binds to these interfaces, never to a concrete search engine or
fetch mechanism. Live implementations wrap HTTP; replay implementations read
from a fixture manifest.
"""

import hashlib
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypedDict

from runtime.type_support import override


class SearchHit(TypedDict):
    url: str
    title: str
    snippet: str


class ReplayPage(TypedDict, total=False):
    content: str
    status: int
    captured_at: str
    final_url: str


class SearchResult:
    def __init__(self, query: str, results: list[SearchHit], provider_id: str) -> None:
        self.query: str = query
        self.results: list[SearchHit] = results  # list of {"url", "title", "snippet"}
        self.provider_id: str = provider_id


class FetchResult:
    def __init__(self, url: str, status: str, content: str | None, content_hash: str | None, fetch_method: str,
                 retrieved_at: str | None, error: str | None = None, rendered_fallback: bool = False,
                 final_url: str | None = None) -> None:
        self.url: str = url
        self.status: str = status  # 'success' | 'failed' | 'render_required'
        self.content: str | None = content  # str or None
        self.content_hash: str | None = content_hash
        self.fetch_method: str = fetch_method  # 'http_get' | 'rendered_browser' | 'replay_fixture'
        self.retrieved_at: str | None = retrieved_at
        self.error: str | None = error
        self.rendered_fallback: bool = rendered_fallback
        self.final_url: str = final_url or url


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> SearchResult:
        """Return SearchResult for the query."""


class FetchProvider(ABC):
    @abstractmethod
    def fetch(self, url: str) -> FetchResult:
        """Return FetchResult for the URL."""


class ReplaySearchProvider(SearchProvider):
    """Deterministic search backed by a fixture mapping: query -> results."""

    def __init__(self, fixture_manifest: dict[str, list[SearchHit]]) -> None:
        self.manifest: dict[str, list[SearchHit]] = fixture_manifest

    @override
    def search(self, query: str) -> SearchResult:
        results = self.manifest.get(query, [])
        return SearchResult(query=query, results=results, provider_id="replay_search")


class ReplayFetchProvider(FetchProvider):
    """Deterministic fetch backed by a fixture manifest of captured pages."""

    def __init__(self, fixture_manifest: dict[str, ReplayPage]) -> None:
        self.manifest: dict[str, ReplayPage] = fixture_manifest

    @override
    def fetch(self, url: str) -> FetchResult:
        entry = self.manifest.get(url)
        if entry is None:
            return FetchResult(
                url=url, status="failed", content=None, content_hash=None,
                fetch_method="replay_fixture", retrieved_at="FIXTURE_TIME",
                error="URL not in replay fixtures",
            )
        content = entry.get("content", "")
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return FetchResult(
            url=url, status="success", content=content, content_hash=h,
            fetch_method="replay_fixture", retrieved_at=entry.get("captured_at", "FIXTURE_TIME"),
            final_url=entry.get("final_url", url),
        )


class HttpSearchProvider(SearchProvider):

    SEARCH_URL: str = "https://html.duckduckgo.com/html/?q={q}"

    def __init__(self, user_agent: str = "Mozilla/5.0 (compatible; NAVExploreDiscovery/1.0; research)") -> None:
        self.user_agent: str = user_agent

    @override
    def search(self, query: str) -> SearchResult:
        from .security import fetch_public
        from urllib.parse import quote_plus
        url = self.SEARCH_URL.format(q=quote_plus(query))
        try:
            status, body, _final_url = fetch_public(url, user_agent=self.user_agent)
            if status != 200:
                return SearchResult(query=query, results=[], provider_id="http_search")
            results = self._parse_results(body)
            return SearchResult(query=query, results=results, provider_id="http_search")
        except (OSError, ValueError):
            return SearchResult(query=query, results=[], provider_id="http_search")

    @staticmethod
    def _parse_results(html: str) -> list[SearchHit]:
        import re
        results: list[SearchHit] = []
        # DDG HTML: result links have class result__a
        pattern = re.compile(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        for m in pattern.finditer(html):
            url = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            results.append({"url": url, "title": title, "snippet": ""})
        return results


class HttpFetchProvider(FetchProvider):
    """Live HTTP fetch with timeout, size limit, and redirect tracking."""

    MAX_SIZE: int = 2 * 1024 * 1024  # 2 MiB

    def __init__(self, user_agent: str = "Mozilla/5.0 (compatible; NAVExploreDiscovery/1.0; research)",
                 timeout: float = 15) -> None:
        self.user_agent: str = user_agent
        self.timeout: float = timeout

    @override
    def fetch(self, url: str) -> FetchResult:
        from .security import fetch_public
        try:
            status_code, body, effective_url = fetch_public(
                url, timeout=self.timeout, max_size=self.MAX_SIZE, user_agent=self.user_agent)
        except (OSError, ValueError) as exc:
            return FetchResult(url=url, status="failed", content=None, content_hash=None,
                               fetch_method="http_get", retrieved_at=None,
                               error="FETCH_FAILED: %s" % type(exc).__name__)
        if not 200 <= status_code < 300:
            return FetchResult(url=url, status="failed", content=None, content_hash=None,
                               fetch_method="http_get", retrieved_at=None,
                               error="SOURCE_UNAVAILABLE: HTTP %d" % status_code)

        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        # Heuristic SPA detection: very little body text relative to markup
        if self.looks_like_spa_shell(body):
            return FetchResult(url=url, status="render_required", content=None,
                               content_hash=content_hash, fetch_method="http_get",
                               retrieved_at=None, error="RENDER_REQUIRED",
                               final_url=effective_url)
        return FetchResult(url=url, status="success", content=body,
                           content_hash=content_hash, fetch_method="http_get",
                           retrieved_at=None, final_url=effective_url)

    @staticmethod
    def looks_like_spa_shell(html: str) -> bool:
        """Detect likely JS-rendered shell: minimal text content."""
        import re
        # Strip tags and scripts
        stripped = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        stripped = re.sub(r"<style[^>]*>.*?</style>", " ", stripped, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", stripped)
        # Collapse whitespace and measure
        words = text.split()
        return len(words) < 30

    _looks_like_spa_shell: Callable[[str], bool] = looks_like_spa_shell
