"""V2.3 canonical municipality-root rule (task section 20).

Generalizable, pattern-based root resolution without web search and without
any municipality->service URL table: try the canonical
www.<slug>.kommune.no pattern first, then the bare-domain pattern (live
verification: Hasvik serves on the bare domain, Raelingen on www).
The pattern is corroborated by Brreg Enhetsregisteret, the official
Norwegian registry of municipalities and their registered homepages
(e.g. Raelingen kommune, org 952540556, hjemmeside www.ralingen.kommune.no).
The registry is an identity/canonical-root source, never a service-URL
lookup; no service-page knowledge enters this module.

Secondary platform pattern: some municipalities publish their child/youth
service content on the national program platform <slug>.bedreinnsats.no.
It is tried only after every kommune.no variant fails, and a hit still has
to pass the provider's nav-link keyword test and the orchestrator's
official-domain check; otherwise it is discarded. Pattern rule, not a
municipality lookup table.
"""

import re
import unicodedata


def slug_fold(municipality):
    s = unicodedata.normalize("NFKD", municipality.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\u00e6", "ae").replace("\u00f8", "o").replace("\u00e5", "a")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def canonical_roots(municipality):
    # ponytail: bounded transliteration variants (NFKD ae/o/a plus the
    # compressed ae->a variant some registered domains use, e.g.
    # Raellingen -> ralingen.kommune.no). If a future municipality deviates
    # from both variants, registry lookup (Brreg hjemmeside) is the upgrade
    # path; NO_RESULTS stays the honest fail-closed outcome.
    slug = slug_fold(municipality)
    compressed = slug.replace("ae", "a")
    variants = [slug]
    if compressed != slug:
        variants.append(compressed)
    roots = []
    for v in variants:
        roots.append("https://www.%s.kommune.no/" % v)
        roots.append("https://%s.kommune.no/" % v)
    roots.append("https://%s.bedinnsats.no/" % compressed)
    return roots
