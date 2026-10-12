import re
from collections.abc import Callable, Iterable
from typing import Protocol, TypedDict

FetchFn = Callable[[str], tuple[int, str]]

class ResultOptions(TypedDict, total=False):
    title: str
    snippet: str
    provider: str
    rank: int

class Result(ResultOptions):
    url: str

class ResponseData(TypedDict):
    query: str
    status: str
    results: list[Result]
    error: str | None
    provider: str
    latency_ms: float
    discovery_method: str | None
    fallback_log: list[dict[str, object]]
    attempts: list[dict[str, object]]

class ProviderResponse:
    query: str
    status: str
    results: list[Result]
    error: str | None
    provider: str
    latency_ms: float
    discovery_method: str | None
    fallback_log: list[dict[str, object]]
    attempts: list[dict[str, object]]
    def __init__(self, query: str, status: str, results: list[Result] | None = None,
                 error: str | None = None, provider: str = "", latency_ms: float = 0,
                 discovery_method: str | None = None) -> None: ...
    def to_dict(self) -> ResponseData: ...

class ProviderHealth:
    provider: str
    successful_queries: int
    attempted_queries: int
    failure_class: str | None
    def __init__(self, provider: str) -> None: ...
    def record(self, status: str) -> None: ...
    @property
    def healthy(self) -> bool: ...
    def to_dict(self) -> dict[str, object]: ...

class DiscoveryProvider(Protocol):
    def discover(self, query: str) -> ProviderResponse: ...
    def health(self) -> object: ...

class SiteDirectProvider:
    roots: list[str] | None
    provider_id: str
    health: ProviderHealth
    _url_budget: int
    _cache: dict[str, ProviderResponse]
    def __init__(self, fetch_fn: FetchFn, roots: list[str] | None = None,
                 provider_id: str = "site_direct", sitemap_fetch_fn: FetchFn | None = None) -> None: ...
    def discover(self, query: str) -> ProviderResponse: ...
    def _get(self, url: str) -> tuple[str, str]: ...
    @staticmethod
    def _nav_links(html: str, base_url: str) -> list[Result]: ...
    @staticmethod
    def _sitemap_urls(xml: str) -> list[Result]: ...

class ExternalSearchProvider:
    provider_id: str
    health: ProviderHealth
    def __init__(self, fetch_fn: Callable[[str], tuple[int, str] | dict[str, object]],
                 parser: Callable[[str], list[Result]] | None = None,
                 provider_id: str = "external_search", max_queries_per_run: int = 3,
                 min_interval_s: float = 10.0) -> None: ...
    def discover(self, query: str) -> ProviderResponse: ...

class CandidateProvider(Protocol):
    provider_id: str
    health: ProviderHealth
    def discover(self, query: str) -> ProviderResponse: ...

class CompositeDiscoveryProvider:
    def __init__(self, providers: Iterable[CandidateProvider]) -> None: ...
    def discover(self, query: str) -> ProviderResponse: ...
    def health(self) -> list[dict[str, object]]: ...

def classify_http_response(status_code: int, body: str | None,
                           parsed_results: list[Result] | None = None) -> str: ...
CANONICAL_STATUSES: list[str]
BOT_MARKERS: re.Pattern[str]
MIN_VALID_BODY_BYTES: int
MAX_SCAN_BYTES: int
MAX_SITE_RESULTS: int
NAV_KEYWORDS: tuple[str, ...]
__all__ = ["_fold", "MAX_SITE_RESULTS", "NAV_KEYWORDS", "ProviderResponse", "SiteDirectProvider",
           "FetchFn", "Result", "DiscoveryProvider"]
def _fold(name: str) -> str: ...
