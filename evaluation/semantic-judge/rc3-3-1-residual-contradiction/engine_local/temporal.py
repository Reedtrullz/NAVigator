"""TEMPORAL_APPLICABILITY_V1 - RC3.3.1 residual contradiction repair.

Sentence-level temporal applicability: a historical claim is comparable
only when some claim quantity matches a value inside a historical
evidence sentence; a current claim whose quantities match only
historical sentence values is stale. Frozen calibration
CURRENT_YEAR=2026. Deterministic. No case IDs, no label maps.
"""

import re

CURRENT_YEAR = 2026

CUR_MARK_RE = re.compile(
    r"(?i)\b(na|naa|naavaerende|gjeldende|gjeldande|i dag|dette aret|"
    r"per 2026|fra 2026)\b")
HIST_MARK_RE = re.compile(
    r"(?i)\b(gjaldt|tidligere|tidlegare|forrige|forre|erstattet|erstatte|"
    r"opphort|sist endret|gammel|gamal|historisk|var \d+|ble \d+)\b")
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
YEAR_TEMPORAL_PRE_RE = re.compile(
    r"(?i)(?:\bi|\bfra|\bper|\bsiden|\bendret|\bi kraft|\bgjaldt|"
    r"\bvar|\bble|\bden)\s*$")
YEAR_UNIT_POST_RE = re.compile(
    r"(?i)^\s*(?:kroner|kr\b|%|prosent|\s*stk|maneder|maaneder|mnd|"
    r"uker|dager|timer|ar\b|aar\b)")
DAY_OF_MONTH_RE = re.compile(r"\bden\s+(\d{1,2})\.")


def _sentences(text):
    parts = re.split(r"[.;!?]", text or "")
    return [p.strip() for p in parts if p.strip()]


def _is_historical_sentence(sentence):
    return HIST_MARK_RE.search(sentence) is not None


def _temporal_years(text):
    """Bare years in a temporal frame, excluding values inside amounts."""
    years = []
    for m in YEAR_RE.finditer(text):
        pre = text[max(0, m.start() - 14) : m.start()]
        post = text[m.end() : m.end() + 12]
        if YEAR_TEMPORAL_PRE_RE.search(pre) and not YEAR_UNIT_POST_RE.match(
                post):
            years.append(int(m.group(1)))
    return years


def _quantities(text):
    from .numeric import parse_quantities

    return parse_quantities(text)


def _matches(cq, eq):
    """Loose identity for applicability: same type and value; DATE
    matches at year granularity when either side is year-only."""
    if cq["quantity_type"] != eq["quantity_type"]:
        return False
    if cq["quantity_type"] == "DATE":
        if cq["value"] % 10000 == 101 or eq["value"] % 10000 == 101:
            return int(cq["value"] // 10000) == int(eq["value"] // 10000)
        return cq["value"] == eq["value"]
    return cq["value"] == eq["value"]


def _claim_temporal_status(text):
    """HISTORICAL, CURRENT, or None (None treated as comparable)."""
    if CUR_MARK_RE.search(text):
        return "CURRENT"
    if HIST_MARK_RE.search(text):
        return "HISTORICAL"
    years = _temporal_years(text)
    if years and all(y < CURRENT_YEAR for y in years):
        return "HISTORICAL"
    return None


def applicability_mismatch(claim_text, evidence_text):
    """True when claim and deciding evidence disagree in temporal frame.

    Returns False (comparable) or a reason string:
    - FRAME_ONLY: the claim's era is absent from the evidence entirely.
    - VALUE_STALE: the claim's value matches only historical evidence
      while the claim asserts the current frame.
    - PERIOD_MISMATCH: deadline-day or full-date identity failure.

    - claim historical: mismatch when no historical evidence sentence
      exists, or when no claim quantity matches a historical sentence
      value.
    - claim current: mismatch when the claim quantities match only
      historical sentence values.
    - no claim-side temporal signal: comparable.
    """
    claim = claim_text or ""
    evidence = evidence_text or ""
    # Deadline-day mismatch: claim and evidence name different days of
    # the month for the same routine ("den 25." vs "den 20.").
    cdaym = DAY_OF_MONTH_RE.search(claim)
    if cdaym:
        edays = [int(m.group(1))
                 for m in DAY_OF_MONTH_RE.finditer(evidence)]
        if edays and all(int(cdaym.group(1)) != d for d in edays):
            return "PERIOD_MISMATCH"
    cqs = strip_year_phantoms(claim, _quantities(claim))
    # Date-identity claims (law stamps, i-kraft dates, FOR numbers):
    # a full-date claim whose date is absent from the evidence is a
    # period mismatch; year-only date claims stay comparable (the
    # numeric layer resolves them).
    if cqs and all(q["quantity_type"] == "DATE" for q in cqs):
        ev_dates = {
            q["value"]
            for q in _quantities(evidence)
            if q["quantity_type"] == "DATE"
        }
        for q in cqs:
            span = (q.get("provenance") or {}).get("claim_span") or ""
            year_only = bool(
                re.fullmatch(r"\s*(1[89]\d{2}|20\d{2})\s*", span))
            if year_only:
                # Year identity is the numeric layer's job.
                continue
            if q["value"] not in ev_dates:
                return "PERIOD_MISMATCH"
        return False
    cstatus = _claim_temporal_status(claim)
    if cstatus is None:
        return False
    sentences = _sentences(evidence)
    if not sentences:
        return False
    hist_sents = [s for s in sentences if _is_historical_sentence(s)]
    if cstatus == "HISTORICAL":
        if not hist_sents:
            return "FRAME_ONLY"
        if not cqs:
            return False
        hist_qs = [q for s in hist_sents for q in _quantities(s)]
        if any(_matches(cq, eq) for cq in cqs for eq in hist_qs):
            return False
        # Dated claims ("I 2025 var ...") are comparable when a
        # historical evidence clause carries the same year, even when
        # the value differs (that difference is a real conflict, not
        # an applicability gap).
        cyears = set(_temporal_years(claim))
        hist_years = set()
        for s in hist_sents:
            hist_years.update(
                int(m.group(1)) for m in YEAR_RE.finditer(s))
        if cyears and cyears & hist_years:
            return False
        return "FRAME_ONLY"
    # CURRENT
    if not hist_sents or not cqs:
        return False
    nonhist_sents = [s for s in sentences if not _is_historical_sentence(s)]
    nonhist_qs = [q for s in nonhist_sents for q in _quantities(s)]
    if any(_matches(cq, eq) for cq in cqs for eq in nonhist_qs):
        return False
    hist_qs = [q for s in hist_sents for q in _quantities(s)]
    if any(_matches(cq, eq) for cq in cqs for eq in hist_qs):
        return "VALUE_STALE"
    return False


def strip_year_phantoms(text, quantities):
    """Drop non-DATE quantities whose provenance span is a bare year."""
    out = []
    for q in quantities or []:
        if q.get("quantity_type") == "DATE":
            out.append(q)
            continue
        span = (q.get("provenance") or {}).get("claim_span") or ""
        if re.fullmatch(r"\s*(1[89]\d{2}|20\d{2})\s*", span):
            continue
        out.append(q)
    return out
