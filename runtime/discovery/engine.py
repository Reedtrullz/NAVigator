"""Core discovery engine: planner, link explorer, extractor, ledger,
access classifier, route evaluator, provenance graph, and orchestration.

No municipality-specific logic lives here. All data comes from the frozen
protocol and replay/live providers.
"""

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from .security import validate_url, InvalidUrlError


# ---------------------------------------------------------------------------
# Discovery Planner
# ---------------------------------------------------------------------------

class DiscoveryPlanner:
    """Generate the allowed discovery levels and queries from the protocol."""

    def __init__(self, protocol):
        self.protocol = protocol

    def _levels(self):
        data = self.protocol["levels"] if isinstance(self.protocol, dict) else self.protocol.levels
        return data

    def _templates(self):
        data = (self.protocol["query_family_templates"]
                if isinstance(self.protocol, dict) else self.protocol.query_templates)
        return data

    def plan(self, municipality):
        """Return ordered discovery steps per frozen levels 0-5."""
        steps = []
        for level in self._levels():
            step = {"level": level["id"], "name": level["name"], "queries": [],
                    "known_urls": [], "status": "PENDING"}
            if level["id"] == 1 or level["id"] in (2, 3):
                # Query templates apply to structured/catalog levels
                step["queries"] = [
                    t.replace("<kommune>", municipality)
                    for t in self._templates()
                ]
            steps.append(step)
        return steps


# ---------------------------------------------------------------------------
# Link Explorer
# ---------------------------------------------------------------------------

class LinkExplorer:
    """Follow discovery edges within bounds (recursion depth, max pages)."""

    def __init__(self, fetch_provider, max_depth=2, max_pages=20):
        self.fetch_provider = fetch_provider
        self.max_depth = max_depth
        self.max_pages = max_pages

    def explore(self, start_url, depth=0, visited=None):
        """Yield (url, links, fetch_result) tuples for the page and its links."""
        if visited is None:
            visited = set()
        if depth > self.max_depth or len(visited) >= self.max_pages:
            return
        if start_url in visited:
            return
        try:
            validate_url(start_url)
        except InvalidUrlError:
            return
        visited.add(start_url)
        result = self.fetch_provider.fetch(start_url)
        links = []
        if result.status == "success" and result.content:
            links = self._extract_links(result.content, start_url)
        yield (start_url, links, result)
        for link in links:
            if len(visited) >= self.max_pages:
                return
            yield from self.explore(link, depth + 1, visited)

    @staticmethod
    def _extract_links(html, base_url):
        """Extract absolute URLs from <a href> tags, staying on official domains."""
        from .security import is_official_domain
        links = []
        for m in re.finditer(r'<a[^>]+href="([^"#]+)"', html, re.IGNORECASE):
            href = m.group(1).strip()
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue
            absolute = urljoin(base_url, href)
            try:
                validate_url(absolute)
            except InvalidUrlError:
                continue
            base_domain = is_official_domain(base_url)
            link_domain = is_official_domain(absolute)
            # Stay within official source types for navigation
            if base_domain in ("private", "unknown") and link_domain == "private":
                continue
            if link_domain in ("private", "unknown"):
                continue
            links.append(absolute)
        return list(dict.fromkeys(links))  # dedupe, preserve order


# ---------------------------------------------------------------------------
# Service Extractor
# ---------------------------------------------------------------------------

class ServiceExtractor:
    """Rule-based extraction of service evidence from fetched HTML.

    Fail-closed: extraction returns explicit markers or None. It never
    fabricates a service or access method that is not present in the text.
    """

    # Norwegian access markers
    PHONE_RE = re.compile(r"(?:\+47\s?)?(?:\d{2}\s?){4}\d{2}|\b\d{8}\b|\b\d{3}\s\d{2}\s\d{3}\b")
    EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
    FORM_RE = re.compile(
        r"(søknadsskjema|søk om|elektronisk skjema|digital skjema|selvhenvisning[s]?|fyll ut selvhenvisningsskjema|"
        r"fyll ut skjema|bruk skjema|self[- ]referral|application form)",
        re.IGNORECASE,
    )
    DROPIN_RE = re.compile(r"(drop[- ]?in|kan komme[sr]? uten avtale|uten timebestilling)", re.IGNORECASE)
    CONTACT_RE = re.compile(
        r"(ta kontakt|kontakt oss|du kan kontakte|ring til|ring oss|kontakt(t)? oss på|"
        r"for veiledning.*?kontakt|besøk oss)",
        re.IGNORECASE,
    )
    # selvhenvisning is self-referral, not a referral requirement
    REFERRAL_RE = re.compile(r"(?<!selv)" + (
        r"(henvisning|tilvising|henvises|henvisning fra (fastlege|lege|tannlege|andre)|"
        r"via fastlege|fastlege kan henvise|krever henvisning)"
    ), re.IGNORECASE)
    # Negated referral ("no referral needed") documents self-referral (E3)
    REFERRAL_NEGATED_RE = re.compile(
        r"(trenger (?:ikke|ingen) henvisning|behøver (?:ikke|ingen) henvisning|"
        r"treng (?:ikkje|ingen) tilvising|inga tilvising|utan tilvising|"
        r"ikkje tilvising|ingen henvisning|uten henvisning)",
        re.IGNORECASE,
    )
    # Soft/optional referral: offered as an alternative, not a requirement
    REFERRAL_SOFT_RE = re.compile(
        r"(fortrinnsvis henvisning|ønsker vi fortrinnsvis|eller via fastlege|"
        r"eller du kan henvises|eller henvises av|eller via henvisning)",
        re.IGNORECASE,
    )
    # Capacity closure: page states the service currently cannot accept
    # patients; contact channels may exist but there is no new-user route.
    CLOSED_TO_PATIENTS_RE = re.compile(
        r"(ikke kapasitet til å tilby|ikkje kapasitet til å tilby|"
        r"ingen kapasitet til å tilby|stengt for nye pasienter|"
        r"tar ikke imot nye pasienter)",
        re.IGNORECASE,
    )
    # System-targeted services (guidance to staff, not patient intake)
    SYSTEM_TARGETED_RE = re.compile(
        r"(veiledning av annet helsepersonell|rettleiing og fagstøtte til tilsette)",
        re.IGNORECASE,
    )
    # Service-connected email context (E2 analogue for DIRECT_EMAIL)
    EMAIL_CONNECTED_RE = re.compile(r"(send e-post|e-post\s*:|skriv til)", re.IGNORECASE)

    # Explicit self-contact statements (E1: "ta kontakt" connected to the
    # service; E3: distinguishes unconditional self-referral from a phone
    # number that may route through assessment)
    SELF_CONTACT_RE = re.compile(
        r"(kan ta kontakt (?:selv|direkte)|kan selv ta kontakt|ta kontakt selv|"
        r"alle kan ta kontakt|du kan selv ta kontakt|selv kan ta kontakt|på egen hånd)",
        re.IGNORECASE,
    )
    AGE_RE = re.compile(
        r"((?:over|under) (?:fylte )?(\d{1,3}) år|mellom (\d{1,3}) og (\d{1,3}) år|"
        r"(\d{1,3})-(\d{1,3}) år|fra (\d{1,3}) år|tilbud til barn og unge)",
        re.IGNORECASE,
    )
    AGE_UNIVERSAL_RE = re.compile(r"(gis til alle|tilbud til alle|tilbyr til alle)", re.IGNORECASE)
    TARGET_GROUP_RE = re.compile(
        r"til (?:innbyggere|voksne|barn|unge|ungdom|elever|pårørende|familier|deg som)",
        re.IGNORECASE,
    )
    # Context phrases that connect a phone number to service intake (E2)
    PHONE_INTAKE_CONTEXT_RE = re.compile(
        r"(kontaktinformasjon|telefontid|timebestilling|inntak|ring oss|ring til|ringe|"
        r"kontakt oss på|for veiledning)",
        re.IGNORECASE,
    )
    SERVICE_KEYWORDS = re.compile(
        r"(psykisk helse|psykisk helsehjelp|psykisk helse og rus|rask psykisk helsehjelp|"
        r"psykisk(e)? helsetjeneste|psykisk(e)? helse|helseutfordringer|kommunepsykolog|mestring|lavterskel|helsestasjon|"
        r"ambulant team|barne- og ungdomsteam|"
        r"psykolog|rus|selvhjelp)",
        re.IGNORECASE,
    )

    def extract(self, html, url):
        """Extract candidate services, access markers, and evidence spans."""
        text = self._html_to_text(html)
        if not text or not self.SERVICE_KEYWORDS.search(text):
            # A service page can also be identified by its URL slug when the
            # body text uses formulations the keyword gate does not cover.
            if not self._slug_has_service_terms(url):
                return None
        evidence = []
        result = {
            "url": url,
            "title": None,
            "has_service_content": True,
            "access_markers": {},
            "age_text": None,
            "age_bounds": None,
            "age_universal": False,
            "target_group": None,
            "text_spans": [],
        }
        # Access markers
        phones = self.PHONE_RE.findall(text)
        emails = self.EMAIL_RE.findall(text)
        has_form = bool(self.FORM_RE.search(text))
        has_dropin = bool(self.DROPIN_RE.search(text))
        has_contact = bool(self.CONTACT_RE.search(text))
        # Referral polarity: negated ("no referral needed") and soft/optional
        # ("preferably", "or via GP") referrals are not requirements.
        referral_negated = bool(self.REFERRAL_NEGATED_RE.search(text))
        referral_optional = bool(self.REFERRAL_SOFT_RE.search(text))
        has_referral = (bool(self.REFERRAL_RE.search(text))
                        and not referral_negated and not referral_optional)
        explicit_self_contact = (bool(self.SELF_CONTACT_RE.search(text))
                                 or referral_negated)
        phone_connected = (bool(phones) and bool(self.PHONE_INTAKE_CONTEXT_RE.search(text)))
        email_connected = (bool(emails)
                           and (has_contact or bool(self.EMAIL_CONNECTED_RE.search(text))))
        closed_to_patients = bool(self.CLOSED_TO_PATIENTS_RE.search(text))
        system_targeted = bool(self.SYSTEM_TARGETED_RE.search(text))

        result["access_markers"] = {
            "phone_numbers": list(dict.fromkeys(phones))[:3],
            "emails": list(dict.fromkeys(emails))[:3],
            "application_form": has_form,
            "dropin": has_dropin,
            "contact_invitation": has_contact,
            "referral_requirement": has_referral,
            "referral_negated": referral_negated,
            "referral_optional": referral_optional,
            "explicit_self_contact": explicit_self_contact,
            "phone_connected": phone_connected,
            "email_connected": email_connected,
            "closed_to_patients": closed_to_patients,
            "system_targeted": system_targeted,
        }
        title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
        if title_m:
            result["title"] = title_m.group(1).strip()
        # Age coverage: structured bounds plus universal-offer detection
        age_m = self.AGE_RE.search(text)
        if age_m:
            result["age_text"] = age_m.group(0).strip()
            result["age_bounds"] = self._parse_age_bounds(age_m)
        tg_m = self.TARGET_GROUP_RE.search(text)
        if tg_m:
            result["target_group"] = self._extract_span(text, tg_m.start(), tg_m.end())
        if self.AGE_UNIVERSAL_RE.search(text):
            result["age_universal"] = True
        # Capture supporting spans (short, verbatim)
        for pattern, label in [
            (self.CONTACT_RE, "contact"),
            (self.FORM_RE, "form"),
            (self.DROPIN_RE, "dropin"),
            (self.REFERRAL_RE, "referral"),
        ]:
            m = pattern.search(text)
            if m:
                span = self._extract_span(text, m.start(), m.end())
                result["text_spans"].append({"label": label, "span": span})
        return result

    @staticmethod
    def _html_to_text(html):
        """Strip HTML to text, preserving sentence context."""
        if not html:
            return ""
        text = re.sub(r"<head[^>]*>.*?</head>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        # Add sentence break for block elements
        text = re.sub(r"<(?:p|div|br|h[1-6]|li)[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return text.strip()

    @staticmethod
    def _extract_span(text, start, end):
        """Capture the sentence containing the match for verbatim provenance."""
        sent_start = text.rfind(".", 0, start)
        sent_end = text.find(".", end)
        if sent_start < 0:
            sent_start = max(0, start - 80)
        else:
            sent_start += 1
        if sent_end < 0:
            sent_end = min(len(text), end + 80)
        else:
            sent_end += 1
        return text[sent_start:sent_end].strip()

    @staticmethod
    def _parse_age_bounds(match):
        """Parse an AGE_RE match into inclusive {min, max} bounds."""
        g = match.groups()
        text = match.group(0).lower()
        if g[1] is not None:  # over/under (fylte) N år
            return {"min": None if text.startswith("under") else int(g[1]),
                    "max": int(g[1]) if text.startswith("under") else None}
        if g[2] is not None and g[3] is not None:  # mellom X og Y år
            return {"min": int(g[2]), "max": int(g[3])}
        if g[4] is not None and g[5] is not None:  # X-Y år
            return {"min": int(g[4]), "max": int(g[5])}
        if g[6] is not None:  # fra N år
            return {"min": int(g[6]), "max": None}
        return None

    @staticmethod
    def _slug_has_service_terms(url):
        path = urlparse(url).path.lower()
        terms = ("psykisk-helse", "psykisk-helsetjeneste", "psykisk-helsearbeid",
                 "rask-psykisk", "helse-og-rus", "psykisk-helse-og-rus",
                 "helsestasjon", "kommunepsykolog", "mestring")
        return any(t in path for t in terms)
