"""Brave HTML search adapter (external fallback backend).

The adapter is the only Brave-aware code; core runtime never branches on
the backend. Budget and interval are frozen defaults from provider-config.
No evasion: single attempt per query, standard user agent, no retries.

V2.1 transport contract: the curl process exit code and the real HTTP
status are separate facts. Exit 0 means the transfer completed, never
"HTTP 200". HTTP code, final URL, and redirect count are captured
structurally via curl -w write-out metadata, not parsed from prose.
"""

import re
import subprocess
from urllib.parse import quote_plus

from .providers import ExternalSearchProvider

SEARCH_URL = "https://search.brave.com/search?q={q}"
USER_AGENT = "Mozilla/5.0 (compatible; NAVExploreDiscovery/2.0; research)"

EXCLUDED_HOST_PARTS = (
    "brave.com", "bravesoftware", "w3.org", "schema.org",
)

# curl -w metadata is appended behind a sentinel that cannot collide with
# any response body, so transport metadata is never parsed from content.
TRANSPORT_META_SENTINEL = "\n\x1eNAVEXPLORE-TRANSPORT-META\x1e\n"
CURL_TIMEOUT_EXIT = 28

# Bounded response-size policy: external bodies are capped before any
# scanning/classification (truncation is recorded, never silent).
RESULTS_MAX_BYTES = 2 * 1024 * 1024


def brave_parser(html):
    """Extract external result links from Brave search HTML.

    Generic anchor extraction (no brittle result-class dependency):
    external http(s) links only, excluded hosts removed, deduped in order.
    Snippets are intentionally empty: snippets are discovery hints only.
    """
    results, seen = [], set()
    anchor_re = r'<a[^>]+href="(https?://[^"#]+)"[^>]*>(.*?)</a>'
    for m in re.finditer(anchor_re,
                         html or "", re.DOTALL | re.IGNORECASE):
        url = m.group(1).strip()
        low = url.lower()
        if any(part in low for part in EXCLUDED_HOST_PARTS):
            continue
        if url in seen:
            continue
        seen.add(url)
        title = re.sub(r"<[^>]+>", " ", m.group(2) or "")
        title = re.sub(r"\s+", " ", title).strip()
        results.append({"url": url, "title": title[:200], "snippet": ""})
        if len(results) >= 20:
            break
    return results


def _transport(url, curl_exit, http_status, body, final_url=None,
               num_redirects="0", body_truncated=False):
    """Structured transport result (V2.1 richer form)."""
    return {
        "curl_exit": curl_exit,
        "http_status": http_status,
        "body": body,
        "initial_url": url,
        "final_url": final_url or url,
        "num_redirects": num_redirects,
        "body_truncated": body_truncated,
    }


def brave_fetch_fn(query, timeout=15):
    """Fetch the Brave results page as a structured transport result.

    curl exit 0 + HTTP 429 is successful transport + HTTP 429, never
    HTTP 200. On transport failure (exit != 0) no HTTP status is trusted;
    curl exit 28 raises TimeoutError so the provider layer classifies
    TIMEOUT. Bodies are capped at the bounded response-size limit.
    """
    url = SEARCH_URL.format(q=quote_plus(query))
    write_out = "%{http_code} %{url_effective} %{num_redirects}"
    try:
        proc = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-A", USER_AGENT,
             "-w", TRANSPORT_META_SENTINEL + write_out, url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(str(exc)) from exc
    except OSError as exc:
        return _transport(url, 0, 0, str(exc))
    curl_exit = proc.returncode
    stdout = proc.stdout or ""
    body, meta = stdout, ""
    if TRANSPORT_META_SENTINEL in stdout:
        body, meta = stdout.split(TRANSPORT_META_SENTINEL, 1)
    parts = meta.split(None, 2)
    http_code = parts[0] if parts and parts[0].isdigit() else "0"
    final_url = parts[1] if len(parts) > 1 else url
    num_redirects = parts[2] if len(parts) > 2 else "0"
    if curl_exit == CURL_TIMEOUT_EXIT:
        raise TimeoutError("curl exit 28: operation timed out")
    http_status = int(http_code) if curl_exit == 0 else 0
    truncated = len(body) > RESULTS_MAX_BYTES
    if truncated:
        body = body[:RESULTS_MAX_BYTES]
    return _transport(url, curl_exit, http_status, body,
                      final_url=final_url, num_redirects=num_redirects,
                      body_truncated=truncated)


def make_brave_provider(max_queries_per_run=3, min_interval_s=10.0):
    return ExternalSearchProvider(
        fetch_fn=brave_fetch_fn,
        parser=brave_parser,
        provider_id="brave_html",
        max_queries_per_run=max_queries_per_run,
        min_interval_s=min_interval_s,
    )
