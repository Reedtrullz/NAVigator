"""SearchProvider and FetchProvider abstractions with replay-first implementations.

The runtime binds to these interfaces, never to a concrete search engine or
fetch mechanism. Live implementations wrap HTTP; replay implementations read
from a fixture manifest.
"""

import hashlib
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path


class SearchResult:
    def __init__(self, query, results, provider_id):
        self.query = query
        self.results = results  # list of {"url", "title", "snippet"}
        self.provider_id = provider_id


class FetchResult:
    def __init__(self, url, status, content, content_hash, fetch_method,
                 retrieved_at, error=None, rendered_fallback=False,
                 final_url=None):
        self.url = url
        self.status = status  # 'success' | 'failed' | 'render_required'
        self.content = content  # str or None
        self.content_hash = content_hash
        self.fetch_method = fetch_method  # 'http_get' | 'rendered_browser' | 'replay_fixture'
        self.retrieved_at = retrieved_at
        self.error = error
        self.rendered_fallback = rendered_fallback
        self.final_url = final_url or url


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query):
        """Return SearchResult for the query."""


class FetchProvider(ABC):
    @abstractmethod
    def fetch(self, url):
        """Return FetchResult for the URL."""


class ReplaySearchProvider(SearchProvider):
    """Deterministic search backed by a fixture mapping: query -> results."""

    def __init__(self, fixture_manifest):
        self.manifest = fixture_manifest  # dict: query -> [{"url","title","snippet"}]

    def search(self, query):
        results = self.manifest.get(query, [])
        return SearchResult(query=query, results=results, provider_id="replay_search")


class ReplayFetchProvider(FetchProvider):
    """Deterministic fetch backed by a fixture manifest of captured pages."""

    def __init__(self, fixture_manifest):
        self.manifest = fixture_manifest  # dict: url -> {"content": str, "status": int}

    def fetch(self, url):
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
    """Live search using the system 'curl' binary (no extra dependency).

    The search backend is pluggable; this default uses a public HTML endpoint.
    Results are parsed minimally: URLs and titles extracted from HTML.
    """

    SEARCH_URL = "https://html.duckduckgo.com/html/?q={q}"

    def __init__(self, user_agent="Mozilla/5.0 (compatible; NAVExploreDiscovery/1.0; research)"):
        self.user_agent = user_agent

    def search(self, query):
        import shlex
        import subprocess
        from urllib.parse import quote_plus
        url = self.SEARCH_URL.format(q=quote_plus(query))
        try:
            proc = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "15", "-A", self.user_agent, url],
                capture_output=True, text=True, timeout=20,
            )
            if proc.returncode != 0:
                return SearchResult(query=query, results=[], provider_id="http_search")
            results = self._parse_results(proc.stdout)
            return SearchResult(query=query, results=results, provider_id="http_search")
        except (subprocess.TimeoutExpired, OSError):
            return SearchResult(query=query, results=[], provider_id="http_search")

    @staticmethod
    def _parse_results(html):
        import re
        results = []
        # DDG HTML: result links have class result__a
        pattern = re.compile(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        for m in pattern.finditer(html):
            url = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            results.append({"url": url, "title": title, "snippet": ""})
        return results


class HttpFetchProvider(FetchProvider):
    """Live HTTP fetch with timeout, size limit, and redirect tracking."""

    MAX_SIZE = 2 * 1024 * 1024  # 2 MiB

    def __init__(self, user_agent="Mozilla/5.0 (compatible; NAVExploreDiscovery/1.0; research)",
                 timeout=15):
        self.user_agent = user_agent
        self.timeout = timeout

    def fetch(self, url):
        import subprocess
        try:
            proc = subprocess.run(
                ["curl", "-s", "-L", "--max-time", str(self.timeout),
                 "-A", self.user_agent, "-w", "\n%{http_code}\t%{url_effective}",
                 url],
                capture_output=True, text=True, timeout=self.timeout + 5,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            return FetchResult(url=url, status="failed", content=None, content_hash=None,
                               fetch_method="http_get", retrieved_at=None,
                               error="FETCH_FAILED: %s" % exc)

        # The trailing line carries status code + effective URL
        parts = proc.stdout.rsplit("\n", 2)
        body = parts[0] if len(parts) >= 2 else proc.stdout
        trailer = parts[-1] if len(parts) >= 2 else ""
        status_code_str = trailer.split("\t")[0] if "\t" in trailer else ""
        effective_url = trailer.split("\t")[1] if "\t" in trailer else url

        if not status_code_str.isdigit():
            return FetchResult(url=url, status="failed", content=None, content_hash=None,
                               fetch_method="http_get", retrieved_at=None,
                               error="FETCH_FAILED: no status code")
        status_code = int(status_code_str)
        if status_code >= 400:
            return FetchResult(url=url, status="failed", content=None, content_hash=None,
                               fetch_method="http_get", retrieved_at=None,
                               error="SOURCE_UNAVAILABLE: HTTP %d" % status_code)

        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        # Heuristic SPA detection: very little body text relative to markup
        if self._looks_like_spa_shell(body):
            return FetchResult(url=url, status="render_required", content=None,
                               content_hash=content_hash, fetch_method="http_get",
                               retrieved_at=None, error="RENDER_REQUIRED",
                               final_url=effective_url)
        return FetchResult(url=url, status="success", content=body,
                           content_hash=content_hash, fetch_method="http_get",
                           retrieved_at=None, final_url=effective_url)

    @staticmethod
    def _looks_like_spa_shell(html):
        """Detect likely JS-rendered shell: minimal text content."""
        import re
        # Strip tags and scripts
        stripped = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        stripped = re.sub(r"<style[^>]*>.*?</style>", " ", stripped, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", stripped)
        # Collapse whitespace and measure
        words = text.split()
        return len(words) < 30
