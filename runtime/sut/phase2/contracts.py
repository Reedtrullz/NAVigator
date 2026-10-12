from collections.abc import Callable
from typing import TypedDict


class Profile(TypedDict, total=False):
    age: int | None
    household_children: int | bool
    role: str


class Location(TypedDict, total=False):
    municipality: str
    fylke: str
    kommunenummer: str


class Timestamp(TypedDict, total=False):
    executed_at: str


class InputOptions(TypedDict, total=False):
    location_context: Location
    context: dict[str, object]
    timestamp_context: Timestamp


class Input(InputOptions):
    case_id: str
    user_query: str
    profile: Profile


class Permit(TypedDict, total=False):
    path: str
    permission: str
    sha256: str
    domains: list[str]
    freshness_class: str
    verified_date: str | None


class AccessProfile(TypedDict):
    version: str
    documents: dict[str, dict[str, object]]
    rules: Permit


class ConfigOverrides(TypedDict, total=False):
    mode: str
    safety_rules_path: str
    knowledge_index_path: str
    rules_registry_path: str
    knowledge_access_profile: object
    knowledge_repo_root: str


class Config(TypedDict):
    mode: str
    safety_rules_path: str
    knowledge_index_path: str
    rules_registry_path: str
    knowledge_access_profile: object
    knowledge_repo_root: str


class TrackOptions(TypedDict, total=False):
    domain_signal: str | None


class Track(TrackOptions):
    track_id: str
    domain: str
    sub_utterance: str
    status: str
    needs_local_discovery: bool


class Safety(TypedDict):
    priority: str
    safety_class: str | None
    signals: list[str]
    suppressed_routing: bool
    rule_file_sha256: str | None


class SafetyResult(TypedDict):
    priority: str
    safety_class: str
    signals: list[str]
    suppressed_routing: bool
    guarded_signals: list[str]


class Failure(TypedDict):
    stage: str
    state: str
    message: str


class AdmissionFailure(TypedDict):
    reason: str


class CoverageOptions(TypedDict, total=False):
    scope: str
    admitted_documents: int
    matched_records: int


class Coverage(CoverageOptions):
    state: str


class Admission(TypedDict):
    coverage: Coverage
    failures: list[AdmissionFailure]


class SourceReference(TypedDict, total=False):
    kind: str
    ref: str
    url: str
    path: str


class RecordOptions(TypedDict, total=False):
    domains: list[str]
    source_lines: list[str]
    track_domain: str


class KnowledgeRecord(RecordOptions):
    record_id: str
    source_type: str
    domain: str
    claim: str
    source_reference: SourceReference
    authority: str
    freshness: str
    evidence_id: str
    provenance: dict[str, str | None]
    gap_state: str | None
    historical_research: bool


Document = TypedDict("Document", {
    "doc_id": str, "path": str, "sha256": str, "freshness_class": str,
    "domains": list[str], "verified_date": str | None, "content": str, "class": str,
})


Evidence = dict[str, object]


class ServiceOptions(TypedDict, total=False):
    service_id: str
    domain: str
    content_hash: str
    age_bounds: dict[str, int | None] | None
    verified_date: str | None
    age_text: str | None
    age_eligible: bool | None
    target_group: str | None
    strong_access: bool


class Service(ServiceOptions):
    name: str
    source_url: str
    state: str
    access_methods: list[str]
    self_referral: str | bool | None


class DiscoveryStepOptions(TypedDict, total=False):
    trigger_reason: str | None
    municipality: str | None
    route_state: str | None
    execution_status: str | None
    access_methods: list[str]
    self_referral: str | bool | None
    provenance_states: list[str]
    failures: list[dict[str, str | None]]


class DiscoveryStep(DiscoveryStepOptions):
    state: str
    services: list[Service]
    evidence: list[Evidence]


class StepEntry(TypedDict):
    track_id: str
    domain: str
    step: DiscoveryStep


class RouteOptions(TypedDict, total=False):
    service_id: str | None
    evidence_records: dict[str, Evidence]


class Route(RouteOptions):
    route_id: str
    service_type: str
    track_domain: str
    target_population: str
    service_exists: str
    age_eligible: str
    scenario_relevant: str
    access_verified: str
    contact_verified: str
    access_model: list[str]
    self_referral: str | bool
    scope: str
    route_state: str
    evidence_refs: list[str]
    dimension_evidence: dict[str, list[str]]
    provenance_refs: list[str]
    failures: list[Failure]


class ClaimOptions(TypedDict, total=False):
    conflict: bool


class Claim(ClaimOptions):
    claim_id: str
    subject: str
    dimension: str
    value: str
    state: str
    authority: str
    evidence_ids: list[str]
    provenance_ids: list[str]


class Conflict(TypedDict):
    subject: str
    dimension: str
    claim_ids: list[str]
    values: list[str]


class Aggregate(TypedDict):
    claims: list[Claim]
    conflicts: list[Conflict]


class Block(TypedDict):
    order: int
    kind: str
    track_id: str | None
    route_label: str | None
    span_refs: list[str]


class AnswerPlan(TypedDict):
    blocks: list[Block]
    no_route_asserted: bool
    presented_as_complete: bool


class EpistemicOptions(TypedDict, total=False):
    per_track: dict[str, str]


class Epistemic(EpistemicOptions):
    top_level: str
    per_route: list[dict[str, str]]


class Provenance(TypedDict):
    id: str
    source_type: str
    source_ref: str
    retrieved_at: str | None
    verified_at: str
    claim_supported: str
    evidence_span: str | None
    authority_level: str
    freshness_class: str
    conflicts_with: list[str]
    chain_parent_id: str | None


class AttachedEvidence(TypedDict, total=False):
    evidence_ids: list[str]
    provenance_ids: list[str]
    source_url: str


class OutputSafety(TypedDict):
    priority: str
    safety_class: str | None
    signals: list[str]
    suppressed_routing: bool


class StructuredRoute(TypedDict):
    route_id: str
    service_identity: str
    display_label: str
    track_domain: str
    route_state: str
    access_model: list[str]
    self_referral: str | bool
    target_population: str
    scope: str
    evidence_refs: list[str]
    provenance_refs: list[str]
    dims: dict[str, str | None]


class RetrievalEvidence(TypedDict):
    revision: str
    per_track: dict[str, Admission]
    source_dates: dict[str, str | None]
    safety_assessment: str


class OutputEvidence(TypedDict, total=False):
    dimension_sources: dict[str, Evidence]
    source_admission: RetrievalEvidence
    conflicts: list[str]
    per_track_epistemic: dict[str, str]
    route_evidence: dict[str, AttachedEvidence]
    structured_routes: list[StructuredRoute]
    claim_evidence: dict[str, AttachedEvidence]
    safety_priority: str


class Output(TypedDict):
    answer: str
    safety: OutputSafety
    tracks: list[dict[str, str]]
    routes: list[str]
    claims: list[str]
    uncertainty_expressed: list[str]
    evidence: OutputEvidence
    provenance: list[Provenance]
    epistemic_state: str
    failures: list[Failure]
    execution_status: str
    no_route_asserted: bool
    presented_as_complete: bool
    safety_priority: str


class TraceOptions(TypedDict, total=False):
    state: str


class Trace(TraceOptions):
    stage: str
    latency_ms: float


class ContextOptions(TypedDict, total=False):
    _config: Config
    _s2: SafetyResult
    _s3_skipped: bool
    _s4_records: list[KnowledgeRecord]
    _s4_admission: dict[str, Admission]
    _s4_incomplete: bool
    _s5_steps: list[StepEntry]
    _s5_incomplete: bool
    _s6_routes: list[Route]
    _s7_claims: list[Claim]
    _s7_conflicts: list[Conflict]
    _answer: str
    _output: Output


class Context(ContextOptions):
    input: Input
    safety: Safety
    tracks: list[Track]
    candidate_routes: list[Route]
    evidence: dict[str, object]
    provenance: list[Provenance]
    claim_states: list[Claim]
    epistemic_states: Epistemic
    failures: list[Failure]
    answer_plan: AnswerPlan


Stage = Callable[[Context], None]
