"""URL sanitisation and SSRF protection for the discovery runtime.

All URLs entering the fetch path (whether from search results, link
extraction, or fixture manifests) pass through validate_url() first.
"""

import ipaddress
import http.client
import socket
import ssl
import time
from collections.abc import Sequence
from urllib.parse import urljoin, urlparse


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
def _public_ip(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return (address.is_global and not address.is_multicast and not address.is_reserved
            and not address.is_unspecified)


def validate_url(url: object) -> str:
    """Validate a URL for safe fetching. Raises InvalidUrlError on rejection."""
    if not isinstance(url, str) or not url.strip():
        raise InvalidUrlError("URL must be a non-empty string")
    if any(ord(char) <= 32 for char in url) or "\\" in url:
        raise InvalidUrlError("URL contains forbidden characters")
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
    if parsed.username is not None or parsed.password is not None:
        raise InvalidUrlError("URL credentials forbidden")
    try:
        if parsed.port not in (None, 80 if parsed.scheme == "http" else 443):
            raise InvalidUrlError("URL port forbidden")
    except ValueError as exc:
        raise InvalidUrlError("URL port forbidden") from exc

    host = parsed.hostname.lower()
    if host in BLOCKED_HOSTS:
        raise InvalidUrlError("Host blocked: %s" % host)

    ip = None
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and not _public_ip(host):
        raise InvalidUrlError("Nonpublic IP blocked")

    return url


def is_official_domain(url: str, municipality_domain_hints: Sequence[str] | None = None) -> str:
    """Classify a URL domain for the DOMAIN CONSTRAINT (spec 31).

    Returns one of: 'municipal', 'intermunicipal', 'helsenorge',
    'health_enterprise', 'private', 'unknown'.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return "unknown"
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return "unknown"
    if municipality_domain_hints:
        for hint in municipality_domain_hints:
            if hint and (host == hint.lower().rstrip(".") or host.endswith("." + hint.lower().rstrip("."))):
                return "municipal"
    if host.endswith(".kommune.no"):
        return "municipal"
    if host == "helsenorge.no" or host.endswith(".helsenorge.no"):
        return "helsenorge"
    if any(host == root or host.endswith("." + root) for root in (
            "helse-nord.no", "helse-midt.no", "helse-vest.no", "helse-sorost.no")):
        return "health_enterprise"
    return "private"


def fetch_public(url: str, timeout: float = 15, max_size: int = 2 * 1024 * 1024,
                 user_agent: str = "NAVExploreDiscovery/2.0") -> tuple[int, str, str]:
    deadline = time.monotonic() + timeout
    for hop in range(5):
        url = validate_url(url)
        parsed = urlparse(url)
        if not parsed.hostname:
            raise InvalidUrlError("Hostname required")
        host = parsed.hostname.encode("idna").decode("ascii")
        port = 443 if parsed.scheme == "https" else 80
        addresses = [str(ipaddress.ip_address(row[4][0]))
                     for row in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)]
        if not addresses or any(not _public_ip(address) for address in addresses):
            raise InvalidUrlError("DNS target is nonpublic")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("FETCH_TIMEOUT")
        conn = http.client.HTTPConnection(host, port, timeout=remaining)
        conn.auto_open = 0
        try:
            conn.sock = socket.create_connection((addresses[0], port), timeout=remaining)
            if parsed.scheme == "https":
                conn.sock = ssl.create_default_context().wrap_socket(conn.sock, server_hostname=host)
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            _ = conn.request("GET", path, headers={"User-Agent": user_agent, "Accept-Encoding": "identity"})
            response = conn.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                if not location or hop == 4:
                    raise InvalidUrlError("Redirect rejected")
                target = urljoin(url, location)
                if parsed.scheme == "https" and urlparse(target).scheme != "https":
                    raise InvalidUrlError("HTTPS redirect downgrade rejected")
                url = target
                continue
            if not 200 <= response.status <= 599:
                raise InvalidUrlError("HTTP status rejected")
            _ = conn.sock.settimeout(max(0.001, deadline - time.monotonic()))
            body = response.read(max_size + 1)
            if len(body) > max_size:
                raise InvalidUrlError("Response size exceeded")
            return response.status, body.decode("utf-8", errors="replace"), url
        finally:
            conn.close()
    raise InvalidUrlError("Redirect limit exceeded")
