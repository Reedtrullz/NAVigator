"""EvidenceLedger, AccessClassifier, RouteEvaluator, and ProvenanceGraph.

These components enforce the frozen protocol rules (ACCESS-E1 through E5,
route states, stop states) and never infer access beyond what evidence shows.
"""


CANONICAL_ACCESS_METHODS = [
    "DIRECT_PHONE", "DIRECT_DIGITAL", "DIRECT_EMAIL", "DIRECT_DROPIN",
    "APPLICATION_FORM", "SELF_REFERRAL_OTHER", "GP_REFERRAL",
    "OTHER_PROFESSIONAL_REFERRAL", "INTERNAL_MUNICIPAL_REFERRAL",
    "INTERMUNICIPAL_GATEWAY", "SPECIALIST_GATEWAY", "UNCLEAR",
]

ROUTE_STATES = [
    "ROUTE_FULLY_VERIFIED", "ROUTE_ACCESS_PARTIAL",
    "ROUTE_EXISTENCE_ONLY", "ROUTE_UNVERIFIED",
]

STOP_STATES = ["ACCESS_VERIFIED", "REFERRAL_VERIFIED", "PUBLIC_DATA_EXHAUSTED"]


class EvidenceLedger:
    """Store evidence assertions with full provenance."""

    def __init__(self):
        self.entries = []

    def add(self, field, value, source_url, source_title, span, retrieved_at,
            fetch_method, content_hash, confidence_state):
        entry = {
            "field": field,
            "extracted_value": value,
            "source_url": source_url,
            "source_title": source_title,
            "supporting_span": span,
            "retrieved_at": retrieved_at,
            "fetch_method": fetch_method,
            "content_hash": content_hash,
            "confidence_state": confidence_state,
        }
        self.entries.append(entry)
        return entry

    def has_evidence_for(self, field):
        return any(e["field"] == field for e in self.entries)

    def get(self, field):
        return [e for e in self.entries if e["field"] == field]


class AccessClassifier:
    """Classify access per the frozen taxonomy and ACCESS-E1..E5 rules.

    Fail-closed: only returns methods that have explicit evidence. A generic
    phone number without service connection does NOT add DIRECT_PHONE (E2).
    """

    def classify(self, page_extract, service_context=None):
        """Return canonical access methods from a ServiceExtractor result."""
        if not page_extract:
            return {"methods": ["UNCLEAR"], "self_referral": "UNCLEAR"}
        markers = page_extract.get("access_markers", {})
        methods = []
        # ACCESS-E1/E2: an application form, drop-in, or explicit statement
        # that the user can contact the service directly is strong access
        # evidence. A bare "ta kontakt"/phone invitation only weakly documents
        # access (E2), and can never establish FULLY_VERIFIED alone.
        if markers.get("application_form"):
            methods.append("APPLICATION_FORM")
            methods.append("DIRECT_DIGITAL")
        if markers.get("dropin"):
            methods.append("DIRECT_DROPIN")
        if markers.get("explicit_self_contact"):
            methods.append("DIRECT_PHONE")
        elif markers.get("phone_connected"):
            # E2: a phone connected to intake/booking supports access, but is
            # weaker than an explicit self-contact statement.
            methods.append("DIRECT_PHONE")
        if markers.get("referral_requirement"):
            methods.append("GP_REFERRAL")
        if markers.get("email_connected"):
            methods.append("DIRECT_EMAIL")
        if not methods:
            methods.append("UNCLEAR")
        methods = [m for m in CANONICAL_ACCESS_METHODS if m in methods]

        # ACCESS-E3: self_referral is its own field. Explicit self-contact or
        # a negated referral ("no referral needed") is YES; a bare contact
        # invitation is CONDITIONAL (direct contact, later assessment); a
        # hard referral requirement is NO.
        self_referral = "UNCLEAR"
        if markers.get("closed_to_patients") or markers.get("system_targeted"):
            # Capacity closure or staff-guidance service: documented contact
            # exists but there is no new-user route (E3/E4).
            self_referral = "NO"
        elif markers.get("application_form") or markers.get("dropin"):
            self_referral = "YES"
        elif markers.get("explicit_self_contact") or markers.get("phone_connected"):
            self_referral = "YES"
        elif markers.get("referral_requirement"):
            self_referral = "NO"
        elif markers.get("contact_invitation"):
            self_referral = "CONDITIONAL"

        return {"methods": methods, "self_referral": self_referral}


class RouteEvaluator:
    """Produce canonical route state from service/eligibility/access evidence."""

    def evaluate(self, service_verified, eligibility_verified, access_methods,
                 access_clear, contact_documented, strong_access=None):
        """Determine route state per the frozen route_confidence_model.

        No probabilistic confidence scores. strong_access marks evidence that
        meets ACCESS-E1 fully (explicit self-contact, application form, or
        drop-in); a bare phone/contact invitation only supports partial."""
        if not service_verified:
            return "ROUTE_UNVERIFIED"
        fully = (eligibility_verified and access_clear and access_methods
                and access_methods != ["UNCLEAR"] and contact_documented)
        if fully:
            if strong_access is None or strong_access:
                return "ROUTE_FULLY_VERIFIED"
            return "ROUTE_ACCESS_PARTIAL"
        if eligibility_verified and (access_methods and access_methods != ["UNCLEAR"]):
            return "ROUTE_ACCESS_PARTIAL"
        return "ROUTE_EXISTENCE_ONLY"


class ProvenanceGraph:
    """Track discovery edges: how each page was found."""

    def __init__(self):
        self.edges = []

    def add_edge(self, from_node, to_node, discovery_method, query_family=None, level=None):
        edge = {
            "from": from_node,
            "to": to_node,
            "discovery_method": discovery_method,
            "query_family": query_family,
            "level": level,
        }
        self.edges.append(edge)
        return edge

    def trace_back(self, target_url):
        """Return the discovery path that led to target_url."""
        path = []
        current = target_url
        visited = set()
        while current and current not in visited:
            visited.add(current)
            parents = [e for e in self.edges if e["to"] == current]
            if not parents:
                break
            edge = parents[0]
            path.append(edge)
            current = edge["from"]
        path.reverse()
        return path
