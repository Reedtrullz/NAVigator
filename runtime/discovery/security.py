"""URL sanitisation and SSRF protection for the discovery runtime.

All URLs entering the fetch path (whether from search results, link
extraction, or fixture manifests) pass through validate_url() first.
"""

import ipaddress
from urllib.parse import urlparse


class InvalidUrlError(ValueError):
    """URL is rejected as unsafe or unsupported."""


ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "[::1]",
    "[0:0:0:0:0:0:0:1]",
}
BLOCKED_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def validate_url(url):
    """Validate a URL for safe fetching. Raises InvalidUrlError on rejection."""
    if not isinstance(url, str) or not url.strip():
        raise InvalidUrlError("URL must be a non-empty string")
    url = url.strip()
    if len(url) > 2048:
        raise InvalidUrlError("URL exceeds maximum length")
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise InvalidUrlError("URL parse failed: %s" % exc) from exc

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise InvalidUrlError("Scheme not allowed: %s" % parsed.scheme)
    if not parsed.hostname:
        raise InvalidUrlError("URL has no hostname")

    host = parsed.hostname.lower()
    if host in BLOCKED_HOSTS:
        raise InvalidUrlError("Host blocked: %s" % host)

    # Check if hostname is an IP literal in a private range.
    # NOTE: InvalidUrlError subclasses ValueError, so the membership check
    # must happen outside the parse try/except.
    ip = None
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        # Not an IP literal; hostname-based blocking above covers localhost.
        # DNS-resolving hostnames to private IPs is out of scope for this
        # prototype; live fetches go to official public domains only.
        ip = None
    if ip is not None:
        for network in BLOCKED_IP_RANGES:
            if ip in network:
                raise InvalidUrlError("Private IP blocked: %s" % host)

    return url


def is_official_domain(url, municipality_domain_hints=None):
    """Classify a URL domain for the DOMAIN CONSTRAINT (spec 31).

    Returns one of: 'municipal', 'intermunicipal', 'helsenorge',
    'health_enterprise', 'private', 'unknown'.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return "unknown"
    host = (parsed.hostname or "").lower()
    if not host:
        return "unknown"
    if municipality_domain_hints:
        for hint in municipality_domain_hints:
            if hint and hint.lower() in host:
                return "municipal"
    if host.endswith(".kommune.no") or host.endswith(".no") and (
        "kommune" in host or host.startswith("www.") and "kommune" in host
    ):
        return "municipal"
    if "helsenorge.no" in host:
        return "helsenorge"
    if any(x in host for x in ("helse-nord", "helse-midt", "helse-vest", "helse-sorost",
                               "sykehuset", "helseforetak")):
        return "health_enterprise"
    if any(x in host for x in ("iks", "samarbeid", "interkommunal", "partner")):
        return "intermunicipal"
    return "private"
