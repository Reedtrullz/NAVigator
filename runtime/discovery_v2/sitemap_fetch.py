from runtime.discovery.security import fetch_public
from runtime.discovery.providers import HttpFetchProvider

USER_AGENT = "Mozilla/5.0 (compatible; NAVExploreDiscovery/2.0; research)"
MAX_SIZE = 2 * 1024 * 1024


def bounded_fetch(url, timeout=15):
    try:
        code, body, _final_url = fetch_public(url, timeout=timeout, max_size=MAX_SIZE, user_agent=USER_AGENT)
    except (OSError, ValueError):
        return (0, "")
    if not 200 <= code < 300:
        return (code, "")
    if HttpFetchProvider._looks_like_spa_shell(body):
        return (200, "")
    return (code, body)
