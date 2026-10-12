from collections.abc import Callable
from typing import TypedDict
from runtime.discovery.contracts import GraphEdge, LedgerEntry, TextSpan

FetchFn = Callable[[str], tuple[int, str]]


class ResultOptions(TypedDict, total=False):
    title: str
    snippet: str
    provider: str
    rank: int


class Result(ResultOptions):
    url: str


class RunInputOptions(TypedDict, total=False):
    age: int | None
    need: str | None
    urgency: str | None


class RunInput(RunInputOptions):
    municipality: str


class QueryReport(TypedDict):
    query: str
    status: str
    result_count: int
    provider: str
    discovery_method: str | None
    fallback_log: list[dict[str, object]]
    attempts: list[dict[str, object]]


class DiscoveredService(TypedDict):
    url: str
    title: str | None
    access_methods: list[str]
    self_referral: str
    route_state: str
    age_text: str | None
    age_bounds: dict[str, int | None] | None
    age_input_eligible: bool | None
    target_group: str | None
    evidence_spans: list[TextSpan]


class Execution(TypedDict):
    revision: str
    attempted_fetches: int
    successful_fetches: int
    protocol_completed: bool
    services_found: int
    unsupported_levels: list[int]
    unfetched_candidates: int


class RunResult(TypedDict):
    run_id: str
    runtime: str
    mode: str
    input: RunInput
    protocol_id: str
    protocol_sha256: str
    executed_at: str
    query_families_used: list[str]
    queries: list[QueryReport]
    provider_chain: object
    fallback_log: list[dict[str, object]]
    selected_candidates: list[str]
    pages_fetched: int
    execution: Execution
    render_fallbacks: int
    services: list[DiscoveredService]
    route_state: str
    terminal_state: str
    execution_status: str
    provider_failures: list[QueryReport]
    fetch_errors: list[dict[str, str | None]]
    uncertainty_output: str
    evidence: list[LedgerEntry]
    provenance_graph: list[GraphEdge]
