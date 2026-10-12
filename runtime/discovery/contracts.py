from typing import TypedDict


class Level(TypedDict):
    id: int
    name: str


class ProtocolDefinition(TypedDict):
    protocol_id: str
    levels: list[Level]
    query_family_templates: list[str]
    uncertainty_outputs: dict[str, str]


class PlanStep(TypedDict):
    level: int
    name: str
    queries: list[str]
    known_urls: list[str]
    status: str


class TextSpan(TypedDict):
    label: str
    span: str


class AccessMarkers(TypedDict, total=False):
    phone_numbers: list[str]
    emails: list[str]
    application_form: bool
    dropin: bool
    contact_invitation: bool
    referral_requirement: bool
    referral_negated: bool
    referral_optional: bool
    explicit_self_contact: bool
    phone_connected: bool
    email_connected: bool
    closed_to_patients: bool
    system_targeted: bool


class Extract(TypedDict):
    url: str
    title: str | None
    has_service_content: bool
    access_markers: AccessMarkers
    age_text: str | None
    age_bounds: dict[str, int | None] | None
    age_universal: bool
    target_group: str | None
    text_spans: list[TextSpan]


class Classification(TypedDict):
    methods: list[str]
    self_referral: str


class LedgerEntry(TypedDict):
    field: str
    extracted_value: str
    source_url: str
    source_title: str | None
    supporting_span: str
    retrieved_at: str
    fetch_method: str
    content_hash: str | None
    confidence_state: str


GraphEdge = TypedDict("GraphEdge", {
    "from": str, "to": str, "discovery_method": str,
    "query_family": str | None, "level": int | None,
})
