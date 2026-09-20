"""Deterministic S3 problem decomposition (Phase 2).

Conservative keyword-based split over the frozen context schema domain enum.
Conjunctions alone never create tracks; only distinct recognized domains do.
"""


DOMAIN_SIGNALS = {
    "mental_health": (
        "psykisk", "psykiske", "angst", "depresjon", "psykolog",
        "psykisk helse", "mental helse", "sliter psykisk", "psyyke",
        "lavterskel", "dps", "bup", "rph", "hfu",
    ),
    "housing": (
        "bolig", "leilighet", "utkastelse", "husvare", "bostotte",
        "hybel", "varsel om", "botilbud", "hemmelig adresse",
    ),
    "financial_support": (
        "okonomi", "gjeld", "sosialhjelp", "bostotte", "barnetrygd",
        "overgangsstonad", "stonad", "bidrag", "deltid", "okonomisk",
        "raadgivning",
    ),
    "child_safety": (
        "barnevern", "bekymringsmelding", "omsorgssvikt", "overgrep",
        "vold", "krisesenter", "bekymret for",
    ),
    "education": (
        "skole", "ppt", "skolevegring", "skolehelsetjeneste", "laerer",
        "helsesykepleier", "opplaering", "barnehage", "eksamen",
    ),
    "employment": (
        "jobb", "arbeid", "arbeidsgiver", "mistet jobben", "soknad",
        "arbeidsledig", "nav kontor",
    ),
    "legal_rights": (
        "rettighet", "samvar", "foreldreansvar", "samlivsbrudd", "klage",
        "loven", "barnebidrag", "megling",
    ),
}

DOMAIN_ORDER = (
    "mental_health", "housing", "financial_support", "child_safety",
    "education", "employment", "legal_rights",
)

LOCAL_DISCOVERY_DOMAINS = {"mental_health", "housing", "child_safety"}


def _match_domains(text):
    hay = text.lower()
    matched = []
    for domain in DOMAIN_ORDER:
        for signal in DOMAIN_SIGNALS[domain]:
            if signal in hay:
                matched.append((domain, signal))
                break
    return matched


def _split_conjuncts(text):
    # Conservative conjunction split for per-conjunct domain probing only;
    # track identity is domain-based, never conjunct-based.
    parts = []
    current = []
    for token in text.split(" "):
        low = token.lower().strip(",.?!:;")
        if low in ("og", ",", "mens", "samtidig", "plusst", "samt"):
            if current:
                parts.append(" ".join(current))
                current = []
        else:
            current.append(token)
    if current:
        parts.append(" ".join(current))
    return parts


def decompose(user_query):
    """Return ordered canonical tracks for the query."""
    conjuncts = _split_conjuncts(user_query)
    found = {}
    order = [d for d in DOMAIN_ORDER]
    for part in conjuncts:
        for domain, signal in _match_domains(part):
            found.setdefault(domain, signal)
    if not any(d in found for d in order):
        found = {}
        order = ["general"]
    else:
        order = [d for d in order if d in found]
    tracks = []
    for i, domain in enumerate(order, start=1):
        tracks.append({
            "track_id": "T%d" % i,
            "domain": domain,
            "sub_utterance": user_query,
            "status": "PENDING",
            "needs_local_discovery": domain in LOCAL_DISCOVERY_DOMAINS,
            "domain_signal": found.get(domain),
        })
    return tracks
