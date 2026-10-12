"""Deterministic S6 route-candidate construction (Phase 2).

RouteCandidate carries five separate claim dimensions. Each dimension is
evidence-backed or explicitly unresolved; states only ever downgrade.
"""

from .contracts import DiscoveryStep, KnowledgeRecord, Route, Service

import re

from runtime.discovery.eligibility import age_in_bounds
from runtime.discovery.engine import ServiceExtractor
from .text_normalization import normalize_match_text
from .decompose import DOMAIN_SIGNALS


FULLY_VERIFIED = "ROUTE_FULLY_VERIFIED"
ACCESS_PARTIAL = "ROUTE_ACCESS_PARTIAL"
EXISTENCE_ONLY = "ROUTE_EXISTENCE_ONLY"
UNVERIFIED = "ROUTE_UNVERIFIED"

def _service_dimensions(service: Service, track_domain: str, age: int | None) -> tuple[dict[str, str], list[str]]:
    """Map one discovery service to the five claim dimensions."""
    dims = {
        "service_exists": "VERIFIED",
        "age_eligible": "UNRESOLVED",
        "scenario_relevant": "VERIFIED" if service.get("domain") == track_domain else "UNRESOLVED",
        "access_verified": "UNRESOLVED",
        "contact_verified": "UNRESOLVED",
    }
    methods = service.get("access_methods") or []
    # Strong evidence (explicit self-contact, form, drop-in, email) verifies
    # access; a bare contact invitation only supports PARTIAL (runtime
    # doctrine), unclear markers stay unresolved.
    if service.get("strong_access"):
        dims["access_verified"] = "VERIFIED"
        dims["contact_verified"] = "VERIFIED"
    elif methods and methods != ["UNCLEAR"]:
        dims["access_verified"] = "PARTIAL"
        dims["contact_verified"] = "PARTIAL"
    age_ok = age_in_bounds(service.get("age_bounds"), age, service.get("age_text"))
    if age_ok is True:
        dims["age_eligible"] = "VERIFIED"
    elif age_ok is False:
        dims["age_eligible"] = "FAILED"
    return dims, methods


WORST_FIRST = {"FAILED": 0, "UNRESOLVED": 1, "PARTIAL": 2, "VERIFIED": 3}


def _route_state(dims: dict[str, str]) -> str:
    required = ("service_exists", "age_eligible", "scenario_relevant",
                "access_verified", "contact_verified")
    vals = [dims[d] for d in required]
    if all(v == "VERIFIED" for v in vals):
        return "FULLY_VERIFIED"
    if any(v == "FAILED" for v in vals):
        return "UNVERIFIED"
    if dims["service_exists"] == "VERIFIED" and dims["access_verified"] == "PARTIAL":
        return "ACCESS_PARTIAL"
    if dims["service_exists"] == "VERIFIED" and any(v in ("VERIFIED", "PARTIAL") for v in vals):
        return "EXISTENCE_ONLY"
    return "UNVERIFIED"


def build_route_candidates(discovery: DiscoveryStep, track_domain: str, age: int | None = None) -> list[Route]:
    """Build RouteCandidates from one discovery step output."""
    if discovery["state"] != "COMPLETED":
        return []
    routes: list[Route] = []
    for i, service in enumerate(discovery.get("services", []), start=1):
        dims, methods = _service_dimensions(service, track_domain, age)
        dimension_evidence: dict[str, list[str]] = {}
        for dimension in dims:
            bound = _bind_discovery_evidence(service, discovery, track_domain, dimension)
            if not bound:
                dims[dimension] = "UNRESOLVED"
            dimension_evidence[dimension] = bound
        evidence_refs = list(dict.fromkeys(ref for refs in dimension_evidence.values() for ref in refs))
        evidence_records = {"E-DISC-%s-%03d" % (track_domain.upper(), j): {
            key: ev[key] for key in ("service_id", "source_url", "content_hash", "dimension", "locator",
                                    "supporting_span", "value", "verified_date") if key in ev}
            for j, ev in enumerate(discovery.get("evidence", []), 1)
            if "E-DISC-%s-%03d" % (track_domain.upper(), j) in evidence_refs}
        state = _route_state(dims)
        routes.append({
            "route_id": "R-%s-%02d" % (track_domain.upper(), i),
            "service_type": service["name"],
            "service_id": service.get("service_id"),
            "track_domain": track_domain,
            "target_population": service.get("target_group") or "UNRESOLVED",
            "service_exists": dims["service_exists"],
            "age_eligible": dims["age_eligible"],
            "scenario_relevant": dims["scenario_relevant"],
            "access_verified": dims["access_verified"],
            "contact_verified": dims["contact_verified"],
            "access_model": methods if methods else ["UNCLEAR"],
            "self_referral": service.get("self_referral") or "UNCLEAR",
            "scope": "MUNICIPAL",
            "route_state": state,
            "evidence_refs": evidence_refs,
            "dimension_evidence": dimension_evidence,
            "evidence_records": evidence_records,
            "provenance_refs": [service["source_url"]] if evidence_refs else [],
            "failures": [],
        })
    return routes


_QUOTED_NAME_RE = re.compile(r"'([^']+)'")
_BOLD_NAME_RE = re.compile(r"\*\*([^*]+)\*\*")
_DIGIT_RE = re.compile(r"\d")

# W4-RC-A: heading-context rescue. When quote/bold/table extraction
# fails, the claim nearest enclosing source-doc heading may itself be
# the service name ("### Skolehelsetjenesten"). The heading path is
# fail-closed: verbatim claim location, single match, identity gates,
# generic non-service marker rejection.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# W3-RC-A: table-row route targets are only valid when the governing
# markdown table declares a service-identity column ("Instans",
# "Tjeneste"). Scenario/source-ref tables ("Situasjon", "Paastand",
# "Kommune", '"Jeg ..."' ) must never mint route targets, so the header
# decides, not the cell text.
_SERVICE_IDENTITY_HEADERS = frozenset({"instans", "tjeneste", "service"})
_METADATA_LABELS = frozenset({
    "hensikt", "advarsel", "oppdatering", "revisjon", "status",
    "formal", "formaal", "datostempel", "kort om", "se", "kilder",
    "kilde", "merk",
})

# W4-RC-A (B4): quoted/bold segments that are sentence fragments, not
# service identities. Leading verb/negation markers and trailing
# sentence punctuation are generic fragment signatures.
_SENTENCE_STARTERS = (
    "ikke ", "kan ", "skal ", "er ", "har ", "blir ", "motta ",
    "foreldreansvar ", "akutt ",
)
_SENTENCE_END_RE = re.compile(r"[.!?]$")
# W4-RC-A (B4): [subject noun][finite verb] opener is a clause, not a
# service identity ("Barn kan motta samtaler"). ponytail: small closed
# lists; a wider grammar needs a real parser if fragments ever slip past.
_SUBJECT_VERB_RE = re.compile(
    r"^(barn|foreldre|ungdom|familier|pasienter) " +
    r"(kan|skal|har|er|mottar|far|ma|bor)\b")

# W4-RC-A (B4): all-caps labels are rejected unless they resolve to a
# documented service acronym. Unresolved meta-identifiers (e.g. "NAV",
# "URL") are not service identities and never become route targets.
_SERVICE_ACRONYMS = frozenset({
    "bup", "habu", "rph", "dps", "hfu", "ppt",
})
_ALL_CAPS_RE = re.compile(r"^[A-Z]{2,6}$")

# W4-RC-A: heading text that is document metadata/navigation, never a
# service identity.
_HEADING_MARKERS = (
    "ikke navngitt", "samarbeid", "kryssreferanser", "kunnskapshull",
    "status", "kilder", "metode", "sammendrag", "innledning",
    "gap", "oppdatering", "revisjon", "henvisningsretten",
)
_HEADING_SUFFIX_RE = re.compile(
    r"\s*\((?:verifisert|delvis verifisert)\)\s*$", re.IGNORECASE)
_HEADING_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
_TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|")
_HEADER_ROW_RE = re.compile(r"^\|(.+)\|$")
_SEPARATOR_ROW_RE = re.compile(r"^\|\s*:?-{3,}")
_SELF_CONTACT_RE = re.compile(
    r"uten henvisning|ingen henvisning|ikke nodvendig|direkte kontakt|" +
    r"drop-?in|selv ta kontakt|direkte|soknad", re.IGNORECASE)
_REFERRAL_RE = re.compile(r"henvisning|henvises|henviser", re.IGNORECASE)


def _national_service_name(claim: str) -> str | None:
    """Grounded service-name extraction: quoted or bold segments only.

    RC-07: a route target is a service concept. Numeric/temporal facts,
    table fragments and long evidence sentences are rejected so raw KB
    fragments never become route targets. Ceiling: extraction stays
    lexical; structured national service candidates would need a frozen
    registry (services-index is NAV-only, no mental-health services).
    """
    for pattern in (_QUOTED_NAME_RE, _BOLD_NAME_RE):
        match = pattern.search(claim)
        if match:
            name = match.group(1).strip()
            if _valid_service_name(name):
                return name
    return None


def _valid_service_name(name: str) -> bool:
    """Shared identity gate: meaningful label, no fragments/facts.

    Digits stay rejected on the quoted/bold path (RC-07 numeric-fact
    risk lives there); header-gated table identities may contain them
    because names like 'Helsestasjon 0-5 ar' are legitimate targets.
    """
    return (_valid_label(name) and _DIGIT_RE.search(name) is None
            and not _is_sentence_fragment(name)
            and _resolves_service_acronym(name))


def _is_sentence_fragment(name: str) -> bool:
    """W4-RC-A (B4): generic sentence-fragment signature gate."""
    low = name.strip().lower()
    return (low.startswith(_SENTENCE_STARTERS)
            or bool(_SUBJECT_VERB_RE.match(low))
            or bool(_SENTENCE_END_RE.search(low)))


def _resolves_service_acronym(name: str) -> bool:
    """W4-RC-A (B4): all-caps labels need resolved service identity."""
    if not _ALL_CAPS_RE.match(name.strip()):
        return True  # not acronym-shaped; other gates decide
    return name.strip().lower() in _SERVICE_ACRONYMS


def _valid_heading_label(name: str) -> bool:
    """Heading path allows digits ('0-5 ar'); sentence fragments stay out."""
    return (_valid_label(name)
            and not _is_sentence_fragment(name)
            and _resolves_service_acronym(name))


def _heading_marker_free(name: str) -> bool:
    return not any(m in name.lower() for m in _HEADING_MARKERS)


def _heading_context_service_name(claim: str, lines: list[str] | None) -> str | None:
    if not isinstance(lines, list):
        return None
    norm = claim.strip()
    if not norm:
        return None
    idxs = [i for i, ln in enumerate(lines) if norm in ln]
    if len(idxs) != 1:
        return None
    for j in range(idxs[0] - 1, -1, -1):
        match = _HEADING_RE.match(lines[j].strip())
        if match is None:
            continue
        name = match.group(2).strip()
        name = _HEADING_SUFFIX_RE.sub("", name).strip()
        name = _HEADING_PREFIX_RE.sub("", name).strip()
        if not _valid_heading_label(name):
            return None
        return name
    return None


def _bind_discovery_evidence(service: Service, discovery: DiscoveryStep, track_domain: str, dimension: str) -> list[str]:
    refs: list[str] = []
    for j, ev in enumerate(discovery.get("evidence", []), 1):
        service_id = service.get("service_id")
        content_hash = service.get("content_hash")
        bounds = service.get("age_bounds")
        span = ev.get("supporting_span")
        locator = ev.get("locator")
        if (not service_id or ev.get("service_id") != service_id
                or not service.get("source_url") or ev.get("source_url") != service["source_url"]
                or not re.fullmatch(r"[0-9a-f]{64}", content_hash or "")
                or ev.get("content_hash") != content_hash
                or ev.get("dimension") != dimension
                or not isinstance(span, str) or not span.strip()
                or not isinstance(locator, str) or not locator.strip()):
            continue
        value = ev.get("value")
        if not re.search(r"(?<!\w)" + re.escape(normalize_match_text(service["name"])) + r"(?!\w)", normalize_match_text(span)):
            continue
        if dimension == "service_exists" and (not isinstance(value, str) or value != service["name"] or value not in span):
            continue
        if dimension == "age_eligible" and (not bounds or value != bounds):
            continue
        if dimension == "age_eligible":
            match = ServiceExtractor.AGE_RE.search(span)
            if (match is None or ServiceExtractor.parse_age_bounds(match) != value
                    or normalize_match_text(match.group(0)) != normalize_match_text(service.get("age_text") or "")):
                continue
        if dimension == "scenario_relevant":
            signals = (*DOMAIN_SIGNALS.get(track_domain, ()), track_domain.replace("_", " "))
            if value != track_domain or not any(normalize_match_text(s) in normalize_match_text(span) for s in signals):
                continue
        if dimension in ("access_verified", "contact_verified"):
            markers = {
                "DIRECT_DROPIN": bool(ServiceExtractor.DROPIN_RE.search(span)),
                "APPLICATION_FORM": bool(ServiceExtractor.FORM_RE.search(span)),
                "DIRECT_DIGITAL": bool(ServiceExtractor.FORM_RE.search(span)),
                "DIRECT_PHONE": bool(ServiceExtractor.SELF_CONTACT_RE.search(span)
                                      or (ServiceExtractor.PHONE_RE.search(span) and ServiceExtractor.PHONE_INTAKE_CONTEXT_RE.search(span))),
                "DIRECT_EMAIL": bool(ServiceExtractor.EMAIL_RE.search(span)
                                      and (ServiceExtractor.EMAIL_CONNECTED_RE.search(span) or ServiceExtractor.CONTACT_RE.search(span))),
                "GP_REFERRAL": bool(ServiceExtractor.REFERRAL_RE.search(span)
                                     and not ServiceExtractor.REFERRAL_NEGATED_RE.search(span)
                                     and not ServiceExtractor.REFERRAL_SOFT_RE.search(span)),
            }
            if not isinstance(value, str) or value not in (service.get("access_methods") or []) or not markers.get(value):
                continue
        refs.append("E-DISC-%s-%03d" % (track_domain.upper(), j))
    return refs


def _valid_label(name: str) -> bool:
    return (3 <= len(name) <= 80
            and "|" not in name
            and "#" not in name
            and name.strip(" :-").lower() not in _METADATA_LABELS)


def _header_cell_service(header: str) -> bool:
    """True when any header cell declares a service-identity column."""
    cells = [c.strip().strip("*").lower() for c in header.split("|")]
    return any(cell in _SERVICE_IDENTITY_HEADERS for cell in cells)


def _structured_service_name(claim: str, lines: list[str] | None) -> str | None:
    row_match = _TABLE_ROW_RE.match(claim.strip())
    if not isinstance(lines, list) or row_match is None:
        return None
    norm = claim.strip()
    row_idxs = [i for i, ln in enumerate(lines) if norm and norm in ln]
    if len(row_idxs) != 1:
        return None
    sep_idx = None
    for j in range(row_idxs[0] - 1, -1, -1):
        line = lines[j].strip()
        if not line:
            break
        if _SEPARATOR_ROW_RE.match(line):
            sep_idx = j
            break
    if not sep_idx:
        return None
    header_match = _HEADER_ROW_RE.match(lines[sep_idx - 1].strip())
    if header_match is None or not _header_cell_service(header_match.group(1)):
        return None
    name = row_match.group(1).strip()
    if not _valid_label(name):
        return None
    return name


def _self_referral_from_row(claim: str) -> bool | None:
    """Lexical access hint from the claim row itself (documented ceiling).

    Negative/positive self-contact markers outrank a bare 'henvisning'
    substring so 'ingen henvisning' is not misread as referral-required.
    Unresolvable rows stay UNCLEAR per spec section 11.
    """
    if _SELF_CONTACT_RE.search(claim):
        return True
    if _REFERRAL_RE.search(claim):
        return False
    return None


def build_national_route_candidates(records: list[KnowledgeRecord], discovery_service_count: int = 0) -> list[Route]:
    """Build EXISTENCE_ONLY national routes from current research docs.

    FROZEN_RULE, GAP and historical records stay uncertainty-only.
    Provenance ids follow provenance_records numbering: P-K ids continue
    after discovery services over the full record-list order.
    """
    routes: list[Route] = []
    seen: set[tuple[str, str]] = set()
    for idx, rec in enumerate(records):
        if rec.get("source_type") != "PROJECT_RESEARCH":
            continue
        if rec.get("gap_state") is not None or rec.get("historical_research"):
            continue
        if rec.get("freshness") != "CURRENT" or not rec.get("provenance", {}).get("verified_date"):
            continue
        domain = rec.get("track_domain") or rec.get("domain")
        if not domain:
            continue
        claim = rec.get("claim", "")
        name = _structured_service_name(
            claim, rec.get("source_lines"))
        self_referral = None
        if name is not None:
            self_referral = _self_referral_from_row(claim)
        else:
            name = _national_service_name(claim)
        # Table rows are exclusively the header-identity-gate's domain
        # (W3-RC-A); heading rescue is for prose claims only.
        if name is None and not _TABLE_ROW_RE.match(claim.strip()):
            heading_name = _heading_context_service_name(
                claim, rec.get("source_lines"))
            if heading_name is not None and _heading_marker_free(heading_name):
                name = heading_name
        if not name:
            continue
        key = (domain, name)
        if key in seen:
            continue
        seen.add(key)
        dims = {
            "service_exists": "VERIFIED",
            "age_eligible": "UNRESOLVED",
            "scenario_relevant": "VERIFIED",
            "access_verified": "UNRESOLVED",
            "contact_verified": "UNRESOLVED",
        }
        routes.append({
            "route_id": "R-%s-K%02d" % (domain.upper(), len(routes) + 1),
            "service_type": name,
            "track_domain": domain,
            "target_population": "UNRESOLVED",
            "service_exists": dims["service_exists"],
            "age_eligible": dims["age_eligible"],
            "scenario_relevant": dims["scenario_relevant"],
            "access_verified": dims["access_verified"],
            "contact_verified": dims["contact_verified"],
            "access_model": ["UNCLEAR"],
            "self_referral": self_referral if self_referral is not None else "UNCLEAR",
            "scope": "NATIONAL",
            "route_state": _route_state(dims),
            "evidence_refs": [rec["evidence_id"]],
            "dimension_evidence": {"service_exists": [rec["evidence_id"]],
                                   "scenario_relevant": [rec["evidence_id"]]},
            "provenance_refs": ["P-K%03d" % (discovery_service_count + idx + 1)],
            "failures": [],
        })
    return routes
