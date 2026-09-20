"""Tavily Search API adapter (structured external backend, V2.2).

Thin adapter behind the V2 provider contract: canonical statuses only,
fail-closed classification, frozen per-run query budget and minimum
interval, single attempt per query, no evasion, no retries.

The API key is loaded from the project-local secret config (.env.local)
only. The value is never printed, logged, or persisted in artifacts.

Search output is discovery evidence only: snippets never become route
evidence, include_answer is always false, and final provenance still
comes from fetching the original public page via FetchProvider.
"""

import json
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path

from .providers import (
    BOT_MARKERS,
    MAX_SCAN_BYTES,
    ExternalSearchProvider,
    ProviderResponse,
    classify_http_response,
)

SEARCH_ENDPOINT = "https://api.tavily.com/search"
USER_AGENT = "NAVExploreDiscovery/2.2 (research)"

RESULTS_MAX_BYTES = 2 * 1024 * 1024

EXCLUDED_HOST_PARTS = ("tavily.com",)

ENV_LOCAL_NAME = ".env.local"

# Frozen request defaults (provider config V2.2; see benchmark-freeze.json).
FROZEN_PARAMS = {
    "search_depth": "basic",
    "max_results": 10,
    "include_answer": False,
    "include_raw_content": False,
    "country": "norway",
}


class InvalidResponseError(ValueError):
    """Tavily returned a 2xx body that is not a valid structured payload."""


def load_tavily_api_key(path=None):
    """Load the authorized credential from the project .env.local file.

    Returns the key string or None. Never logs the value; callers must
    not embed it in error messages or artifacts.
    """
    if path is None:
        path = Path(__file__).resolve().parents[2] / ENV_LOCAL_NAME
    p = Path(path)
    if not p.is_file():
        return None
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("TAVILY_API_KEY="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def _transport(url, http_status, body, final_url=None, latency_ms=0,
               body_truncated=False, transport_ok=True):
    """Structured transport result (same shape contract as brave.py)."""
    return {
        "curl_exit": 0 if transport_ok else 1,
        "http_status": http_status,
        "body": body,
        "initial_url": url,
        "final_url": final_url or url,
        "num_redirects": "0",
        "body_truncated": body_truncated,
        "latency_ms": latency_ms,
    }


def tavily_fetch_fn(query, timeout=15, api_key=None, include_domains=None,
                    params=None):
    """POST one structured search request (single attempt, no retries).

    Missing credential maps to HTTP 401 so the classifier produces
    AUTH_REQUIRED (fail closed), never NO_RESULTS.
    """
    if api_key is None:
        api_key = load_tavily_api_key()
    if not api_key:
        return _transport(
            SEARCH_ENDPOINT, 401,
            json.dumps({"detail": "credential missing"}))
    payload = dict(FROZEN_PARAMS)
    if params:
        payload.update(params)
    payload["query"] = query
    if include_domains:
        payload["include_domains"] = list(include_domains)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SEARCH_ENDPOINT, data=data, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
            "User-Agent": USER_AGENT,
        })
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(RESULTS_MAX_BYTES + 1)
            final_url = resp.geturl()
            http_status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read(RESULTS_MAX_BYTES + 1)
        http_status = exc.code
        final_url = SEARCH_ENDPOINT
    except (socket.timeout, TimeoutError) as exc:
        raise TimeoutError("tavily request timed out") from exc
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None),
                      (socket.timeout, TimeoutError)):
            raise TimeoutError("tavily request timed out") from exc
        return _transport(SEARCH_ENDPOINT, 0, "")
    latency_ms = int((time.perf_counter() - started) * 1000)
    text = body.decode("utf-8", errors="replace")
    truncated = len(body) > RESULTS_MAX_BYTES
    if truncated:
        text = text[:RESULTS_MAX_BYTES]
    return _transport(SEARCH_ENDPOINT, http_status, text,
                      final_url=final_url, latency_ms=latency_ms,
                      body_truncated=truncated)


def tavily_parser(body):
    """Parse a Tavily JSON payload into normalized result dicts.

    Raises InvalidResponseError on any 2xx body that is not a valid
    structured payload, so malformed responses can never degrade into
    NO_RESULTS.
    """
    try:
        data = json.loads(body or "")
    except (ValueError, TypeError) as exc:
        raise InvalidResponseError("not valid JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise InvalidResponseError("missing results list")
    results, seen = [], set()
    for item in data["results"]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            continue
        low = url.lower()
        if any(part in low for part in EXCLUDED_HOST_PARTS):
            continue
        if url in seen:
            continue
        seen.add(url)
        results.append({
            "url": url,
            "title": str(item.get("title") or "")[:200],
            "snippet": str(item.get("content") or "")[:300],
        })
    return results


class TavilySearchProvider(ExternalSearchProvider):
    """ExternalSearchProvider with Tavily-specific fail-closed mapping.

    A 200 body that parses as a valid structured payload maps to
    SUCCESS/NO_RESULTS on real content; any parse failure maps to
    INVALID_RESPONSE. Failure statuses are never folded into NO_RESULTS.
    """

    def discover(self, query):
        if self._used >= self.max_queries_per_run:
            resp = ProviderResponse(
                query=query, status="RATE_LIMITED", provider=self.provider_id,
                error="QUERY_BUDGET_EXHAUSTED")
            self.health.record(resp.status)
            return resp
        if self._last_call is not None:
            wait = self.min_interval_s - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
        self._last_call = time.monotonic()
        self._used += 1
        self._last_transport = None
        try:
            transport = self.fetch_fn(query)
            status_code = transport.get("http_status") or 0
            body = transport.get("body", "")
            self._last_transport = transport
        except TimeoutError:
            resp = ProviderResponse(
                query=query, status="TIMEOUT", provider=self.provider_id,
                error="BACKEND_TIMEOUT")
            self.health.record(resp.status)
            return resp
        except Exception as exc:  # untrusted backend: fail closed
            resp = ProviderResponse(
                query=query, status="INTERNAL_ERROR",
                provider=self.provider_id,
                error="BACKEND_ERROR: %s" % exc)
            self.health.record(resp.status)
            return resp
        # Parse only 2xx JSON payloads; transport/HTTP failures classify
        # first so an unparseable error body can never shadow the true
        # provider status (fail-closed ordering).
        parsed = []
        if status_code == 200:
            try:
                parsed = self.parser(body)
            except InvalidResponseError:
                resp = ProviderResponse(
                    query=query, status="INVALID_RESPONSE",
                    provider=self.provider_id,
                    error="MALFORMED_PROVIDER_PAYLOAD")
                self.health.record(resp.status)
                return resp
            except Exception as exc:  # untrusted payload: fail closed
                resp = ProviderResponse(
                    query=query, status="INTERNAL_ERROR",
                    provider=self.provider_id,
                    error="BACKEND_ERROR: %s" % exc)
                self.health.record(resp.status)
                return resp
            scan = (body or "")[:MAX_SCAN_BYTES]
            if BOT_MARKERS.search(scan):
                status = "BOT_BLOCKED"
            else:
                status = "SUCCESS" if parsed else "NO_RESULTS"
        else:
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


def make_tavily_provider(max_queries_per_run=3, min_interval_s=0.5,
                         include_domains=None, timeout=15, api_key=None):
    """Build a TavilySearchProvider with frozen defaults."""
    def _fetch(query):
        return tavily_fetch_fn(query, timeout=timeout, api_key=api_key,
                               include_domains=include_domains,
                               params=None)
    return TavilySearchProvider(
        fetch_fn=_fetch, parser=tavily_parser, provider_id="tavily_api",
        max_queries_per_run=max_queries_per_run,
        min_interval_s=min_interval_s)
