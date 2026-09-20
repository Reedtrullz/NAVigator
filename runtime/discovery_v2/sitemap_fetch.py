"""Bounded sitemap fetch for SiteDirectProvider (V2 provider layer).

Mirrors the HTTP behavior of runtime.discovery.providers.HttpFetchProvider
(curl, size cap, SPA-shell detection) but returns (status_code, body) for
the provider-layer fetch_fn contract. Robot-relevant conventions: GET of a
well-known discovery document (sitemap.xml), standard user agent, single
attempt, no retries. This is protocol level 3 (SITEMAP) execution.
"""

import hashlib
import re
import subprocess

USER_AGENT = "Mozilla/5.0 (compatible; NAVExploreDiscovery/2.0; research)"
MAX_SIZE = 2 * 1024 * 1024


def _looks_like_spa_shell(html):
    stripped = re.sub(r"<script[^>]*>.*?</script>", " ", html,
                      flags=re.DOTALL | re.IGNORECASE)
    stripped = re.sub(r"<style[^>]*>.*?</style>", " ", stripped,
                      flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", stripped)
    return len(text.split()) < 30


def bounded_fetch(url, timeout=15):
    """Return (status_code, body). SPA shells map to (200, '')."""
    try:
        proc = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-A",
             USER_AGENT, "-w", "\n%{http_code}\t%{url_effective}", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
    except (subprocess.TimeoutExpired, OSError):
        return (0, "")
    parts = proc.stdout.rsplit("\n", 2)
    body = parts[0] if len(parts) >= 2 else proc.stdout
    trailer = parts[-1] if len(parts) >= 2 else ""
    code_str = trailer.split("\t")[0] if "\t" in trailer else ""
    if len(body) > MAX_SIZE:
        body = body[:MAX_SIZE]
    if not code_str.isdigit():
        return (0, "")
    code = int(code_str)
    if code >= 400:
        return (code, "")
    if _looks_like_spa_shell(body):
        return (200, "")
    return (code, body)
