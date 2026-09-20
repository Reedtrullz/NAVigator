"""Service-specific provenance gate for V2.5 FULLY_VERIFIED (pure rule,
no imports from frozen runtime modules). Shared by RouteEvaluatorV25 and
the V2.5 unit tests so runtime and tests cannot drift.

Rule: a URL names a concrete service when its path has >= 2 segments or its
last slug contains a service term. Root/section pages (0-1 segments without
a service slug) may evidence existence and contacts, but not a verified
route. No case IDs, no municipality names, no gold URLs.
"""

from urllib.parse import urlparse

SERVICE_SLUG_TERMS = (
    "psykisk-helse", "psykisk-helsetjeneste", "psykisk-helsearbeid",
    "rask-psykisk", "helse-og-rus", "psykisk-helse-og-rus",
    "helsestasjon", "helsestasjonen", "kommunepsykolog", "mestring",
)

# Words that mark umbrella/section pages regardless of path depth: they
# aggregate many services, so a hit on them alone never proves that a
# specific service exists on this page.
SECTION_GENERIC_SLUGS = (
    "tjenester", "alle-tjenester", "aktuelt", "nyheter", "kommunen",
    "organisasjon", "site", "sider", "innhold",
    # Municipal taxonomy category names: a page whose last path segment is
    # one of these is a section/landing page even at path depth >= 2.
    "barnehage-skole-og-familie", "helse-og-velferd", "helse-og-sosial",
    "helse-omsorg-og-mestring", "barn-unge-og-familier", "helse-og-omsorg",
)


def is_service_specific_url(url):
    path = urlparse(url).path.strip("/")
    segments = [s for s in path.split("/") if s]
    if not segments:
        return False
    last = segments[-1].lower()
    if last in SECTION_GENERIC_SLUGS:
        return False
    if any(term in last for term in SERVICE_SLUG_TERMS):
        return True
    return len(segments) >= 2
