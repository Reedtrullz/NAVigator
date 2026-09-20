"""NUMERIC_COVERAGE_V1: numeric semantic quantity layer (RC3.3).

Implements numeric-coverage-contract-v1: quantity parsing, frozen interval
semantics, quantity identity, and directional comparator relations.
Law references are never quantities; no implicit unit or period conversion.
No case IDs, no expected-label maps.
"""
import re

from .proposition import STOP, tok_match, toks

ENTAILS = "ENTAILS"
CONTRADICTS = "CONTRADICTS"
UNRESOLVED = "NUMERIC_RELEVANT_BUT_UNRESOLVED"

NUM = r"(?:\d{1,3}(?:[ .]\d{3})+|\d+)(?:,\d+)?"

MONTHS = {
    "januar": 1, "februar": 2, "mars": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "desember": 12,
}

AGE_CTX = ("aldersgrense", "alder", "aring", "aar", "ar", "fyller",
           "eldre", "yngre", "soker", "elever", "barn", "unge")
PERIOD_CTX = ("etter", "innen", "frist", "ventetid", "svarfrist",
              "behandles", "saksbehandling")

FULL_CTX = re.compile(r"full(?:e|t)?(?: sats)?|hele|heilt", re.IGNORECASE)
DELT_CTX = re.compile(r"delt(?:e|a)?|halv(?:ering|parten)?", re.IGNORECASE)
AAP_CTX = re.compile(r"\baap\b", re.IGNORECASE)


def _value(raw):
    return float(raw.replace(" ", "").replace(".", "").replace(",", "."))


def _comparator(text, start, end):
    before = text[max(0, start - 30):start].lower()
    after = text[end:end + 18].lower()
    if re.search(r"minst", before):
        return ">="
    if re.search(r"mer enn|eldre enn|hoyere enn", before):
        return ">"
    if re.search(r"mindre enn|(?<![a-z])under", before):
        return "<"
    if re.search(r"(?<![a-z])over", before):
        return ">"
    if re.search(r"maksimalt|maks|opp til|opptil|hoyest", before):
        return "<="
    if re.search(r"ca|cirka|omtrent", before):
        return "APPROXIMATE"
    if re.search(r"eller eldre|eller flere|eller mer", after):
        return ">="
    return "="


def _law_spans(text):
    spans = []
    for m in re.finditer(
            r"(?:paragraf|para|kapittel|lov(?:en|a)?|forskrift)\s+"
            r"[0-9]+(?:[-.][0-9]+)*", text, re.IGNORECASE):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r"FOR-\d{4}-\d{2}-\d{2}-\d+", text):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r"\d{4}-\d{2}-\d{2}-\d+", text):
        spans.append((m.start(), m.end()))
    return spans


def _binding(text, start, end):
    pre = text[max(0, start - 40):start]
    post = re.split(r"[;:,.()]", text[end:end + 12])[0]
    window = pre + " " + post
    words = [w for w in toks(window) if w not in STOP and not w.isdigit()]
    return " ".join(words[:8]) if words else None


def _role(text, start, end):
    window = text[max(0, start - 55):min(len(text), end + 55)].lower()
    if re.search(r"totalt|totalen|tilsammen|i alt|summen|pluss", window):
        return "AGGREGATE"
    if re.search(r"komponent(?:e[nr])?\s+(?:pa|paa|av)", window):
        return "COMPONENT"
    if re.search(r"halvering|halvparten|delt pa", window):
        return "COMPONENT"
    return "STANDALONE"


def _qtype_for_year(text, start, end):
    window = text[max(0, start - 55):min(len(text), end + 55)].lower()
    if re.search(r"ventetid|venter|svarfrist|innen \d+|frist", window):
        return "PERIOD"
    if any(w in window for w in PERIOD_CTX):
        return "PERIOD"
    return "AGE"


def _period(text, start, end):
    window = text[max(0, start - 55):min(len(text), end + 55)].lower()
    if re.search(r"per (?:maaned|maned|mnd|moned)|kr/m(?:nd)?|kroner i "
                 r"maneden|kroner per maned", window):
        return "MONTH"
    return None


def _mk(text, m, value, qtype, unit, comparator):
    return {
        "quantity_type": qtype,
        "value": value,
        "range_bounds": None,
        "unit": unit,
        "comparator": comparator,
        "period": _period(text, m.start(), m.end()),
        "object_binding": _binding(text, m.start(), m.end()),
        "role": _role(text, m.start(), m.end()),
        "derivation": "DIRECT",
        "provenance": {"claim_span": m.group(0), "evidence_span": None},
    }


def _with_range(m, text, value, qtype, unit, lo, hi):
    q = _mk(text, m, value, qtype, unit, "BETWEEN")
    q["range_bounds"] = [lo, hi]
    return q


def _date_value(y, mo, d):
    return float(y * 10000 + mo * 100 + d)


def parse_quantities(text):
    """All semantic quantities in text; law references excluded."""
    quantities = []
    taken = _law_spans(text)

    def free(s, e):
        return not any(s < te and e > ts for ts, te in taken)

    date_spans = []

    def free2(s, e):
        return free(s, e) and not any(s < te and e > ts
                                      for ts, te in date_spans)

    def free3(s, e):
        return not any(s < te and e > ts for ts, te in date_spans)

    def add_date(m, value):
        q = _mk(text, m, value, "DATE", None, "=")
        q["object_binding"] = None
        quantities.append(q)
        date_spans.append((m.start(), m.end()))

    # Registry/law date stamps (FOR-YYYY-MM-DD-N, YYYY-MM-DD(-N)) are DATE
    # quantities; their digits are taken before the generic loops so law
    # numbers and stamp fragments never parse as ages or counts.
    for m in re.finditer(r"(?:FOR-)?\d{4}-\d{2}-\d{2}(?:-\d+)?", text):
        if not free3(m.start(), m.end()):
            continue
        stamp = re.sub(r"^FOR-", "", m.group(0))
        add_date(m, _date_value(int(stamp[:4]), int(stamp[5:7]),
                                int(stamp[8:10])))

    # Calendar dates: day.month.year; day month year; month year;
    # year-only with explicit law/date context (FOR-..., fra YYYY,
    # YYYY-MM-DD stamps nearby).
    for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", text):
        if not free2(m.start(), m.end()):
            continue
        add_date(m, _date_value(int(m.group(3)), int(m.group(2)),
                                int(m.group(1))))
    month_alt = "|".join(MONTHS)
    for m in re.finditer(r"\b(\d{1,2})\.?\s+(%s)\s+(\d{4})\b"
                         % month_alt, text):
        if not free2(m.start(), m.end()):
            continue
        add_date(m, _date_value(int(m.group(3)), MONTHS[m.group(2)],
                                int(m.group(1) or 1)))
    for m in re.finditer(r"\b(%s)\s+(\d{4})\b" % month_alt, text):
        if not free2(m.start(), m.end()):
            continue
        add_date(m, _date_value(int(m.group(2)), MONTHS[m.group(1)], 1))
    year_ctx = re.compile(
        r"FOR-\d{4}|\d{4}-\d{2}-\d{2}|\b(?:fra|i kraft|iertak|endret)\b",
        re.IGNORECASE)
    for m in re.finditer(r"\b(1[89]\d{2}|20\d{2})\b", text):
        if not free2(m.start(), m.end()):
            continue
        window = text[max(0, m.start() - 45):min(len(text), m.end() + 45)]
        if year_ctx.search(window):
            add_date(m, float(m.group(1)) * 10000 + 101)

    # Percentages: "50 prosent", "50%", "0,5 G".
    for m in re.finditer(r"(%s)\s*(?:prosent|%%)" % NUM, text):
        if not free2(m.start(1), m.end(1)):
            continue
        quantities.append(_mk(text, m, _value(m.group(1)), "PERCENTAGE",
                              "PERCENT",
                              _comparator(text, m.start(1), m.end(1))))
    for m in re.finditer(r"(\d+(?:,\d+)?)\s*G\b", text):
        quantities.append(_mk(text, m, _value(m.group(1)) * 100.0,
                              "PERCENTAGE", "G", "="))
    # Money: "1 006 kr", "2012 kroner", "kr 1500", "gratis".
    for m in re.finditer(r"(%s)\s*(?:kr\b|kroner)|kr\s*(%s)" % (NUM, NUM),
                         text):
        g = m.group(1) or m.group(2)
        gs, ge = (m.start(1), m.end(1)) if m.group(1) \
            else (m.start(2), m.end(2))
        if not free2(gs, ge):
            continue
        quantities.append(_mk(text, m, _value(g), "MONEY", "NOK",
                              _comparator(text, gs, ge)))
    if re.search(r"\bgratis\b", text, re.IGNORECASE):
        m = re.search(r"\bgratis\b", text, re.IGNORECASE)
        quantities.append(_mk(text, m, 0.0, "MONEY", "NOK", "="))
    # Distinctive multi-digit counts (3+ digits) incl. thousands-split
    # form "1 006" (space groups of 3); law refs and dates excluded.
    for m in re.finditer(r"(?<![\d.,])\d{1,3}[ ]\d{3}(?![\d.,])", text):
        if not free2(m.start(), m.end()):
            continue
        quantities.append(_mk(text, m, _value(m.group(0)), "MONEY", "NOK",
                              _comparator(text, m.start(), m.end())))
    for m in re.finditer(r"(?<![\d.,])\d{1,3}(?:[ ]\d{3})+(?![\d.,])",
                         text):
        if not free2(m.start(), m.end()):
            continue
        quantities.append(_mk(text, m, _value(m.group(0)), "COUNT", None,
                              _comparator(text, m.start(), m.end())))
    for m in re.finditer(r"(?<![\d.,])(\d{3,})(?![\d.,])", text):
        if not free2(m.start(1), m.end(1)):
            continue
        quantities.append(_mk(text, m, float(m.group(1)), "COUNT", None,
                              _comparator(text, m.start(1), m.end(1))))
    # Drop plain-COUNT duplicates that overlap a richer quantity span
    # (e.g. "006" inside "1 006").
    rich = [q for q in quantities
            if q["quantity_type"] != "COUNT"
            or q.get("provenance", {}).get("claim_span", "").find(" ") >= 0]
    rich_spans = []
    for q in rich:
        s = q.get("provenance", {}).get("claim_span") or ""
        if s:
            i = text.find(s)
            if i >= 0:
                rich_spans.append((i, i + len(s)))
    quantities = [q for q in quantities
                  if q["quantity_type"] != "COUNT"
                  or q.get("provenance", {}).get("claim_span", "").find(" ") >= 0
                  or not any(_span_overlap(q, text, s) for s in rich_spans)]
    # Age/period ranges "0-20 ar", "0 til 3 ar".
    for m in re.finditer(
            r"(\d{1,3})\s*(?:-|til)\s*(\d{1,3})\s+(?:aar?|ar)\b", text):
        if not free2(m.start(), m.end()):
            continue
        qtype = _qtype_for_year(text, m.start(), m.end())
        lo, hi = float(m.group(1)), float(m.group(2))
        quantities.append(_with_range(m, text, hi, qtype, "YEAR", lo, hi))
    # Unit periods: "24 timer", "3 uker".
    for pat, unit in [(r"maaneder?|mnd", "MONTH"), (r"uker?", "DAY"),
                      (r"dager?|doegn", "DAY"), (r"timer?", "HOUR")]:
        for m in re.finditer(r"(%s)\s+(?:%s)\b" % (NUM, pat), text):
            if not free2(m.start(1), m.end(1)):
                continue
            quantities.append(_mk(text, m, _value(m.group(1)), "PERIOD",
                                  unit,
                                  _comparator(text, m.start(1), m.end(1))))
    # Ages: "18 ar", "minst 18 ar", "under 18 ar".
    for m in re.finditer(r"(%s)\s+(?:aar?|ar)\b" % NUM, text):
        if not free2(m.start(1), m.end(1)):
            continue
        qtype = _qtype_for_year(text, m.start(1), m.end(1))
        quantities.append(_mk(text, m, _value(m.group(1)), qtype, "YEAR",
                              _comparator(text, m.start(1), m.end(1))))
    # Ordinal grades: enumerate "1. trinn", "2., 6.-7. og 10. trinn".
    for m in re.finditer(r"trinn\b", text):
        window = text[max(0, m.start() - 45):m.start()]
        seen_ranges = False
        for g in re.finditer(
                r"\b(\d{1,2})(?:\s*[-.]\s*(\d{1,2}))?(?=\s*[.,)]|\s*$|\s+og\b)",
                window):
            if not free2(m.start() - 45 + g.start(1),
                         m.start() - 45 + g.end(g.lastindex or 1)):
                continue
            if g.group(2):
                q = _mk(text, m, float(g.group(2)), "GRADE", "GRADE",
                        "BETWEEN")
                q["range_bounds"] = [float(g.group(1)), float(g.group(2))]
                quantities.append(q)
                seen_ranges = True
            else:
                quantities.append(_mk(text, m, float(g.group(1)), "GRADE",
                                      "GRADE", "="))
        if not (seen_ranges or quantities):
            single = re.search(r"\b(\d{1,2})\.?\s*$", window)
            if single and free2(m.start() - 45 + single.start(1),
                                m.start() - 45 + single.end(1)):
                quantities.append(_mk(text, m, float(single.group(1)),
                                      "GRADE", "GRADE", "="))
    return quantities


def _span_overlap(q, text, span):
    s = q.get("provenance", {}).get("claim_span") or ""
    if not s:
        return False
    i = text.find(s)
    if i < 0:
        return False
    return i < span[1] and span[0] < i + len(s)


def derived_quantities(evidence_text):
    """DERIVED results from explicit arithmetic chains only."""
    out = []
    for m in re.finditer(
            r"(%s)\s*\+\s*(%s)\s*=\s*(%s)" % (NUM, NUM, NUM),
            evidence_text):
        a, b, c = (_value(m.group(1)), _value(m.group(2)),
                   _value(m.group(3)))
        if a + b != c:
            continue
        window = evidence_text[max(0, m.start() - 60):m.end() + 60].lower()
        if "kr" in window or "kroner" in window:
            qtype, unit = "MONEY", "NOK"
        elif "prosent" in window or "%" in window:
            qtype, unit = "PERCENTAGE", "PERCENT"
        else:
            qtype, unit = "COUNT", None
        q = {
            "quantity_type": qtype, "value": c, "range_bounds": None,
            "unit": unit, "comparator": "=",
            "period": _period(evidence_text, m.start(), m.end()),
            "object_binding": _binding(evidence_text, m.start(), m.end()),
            "role": "AGGREGATE", "derivation": "DERIVED",
            "provenance": {"claim_span": None,
                           "evidence_span": m.group(0)},
            "components": [a, b],
        }
        out.append(q)
    for m in re.finditer(
            r"(%s)\s*/\s*(\d+)\s*=\s*(%s)" % (NUM, NUM), evidence_text):
        a, d, c = _value(m.group(1)), float(m.group(2)), _value(m.group(3))
        if d == 0 or a / d != c:
            continue
        window = evidence_text[max(0, m.start() - 60):m.end() + 60].lower()
        qtype, unit = ("MONEY", "NOK") if ("kr" in window
                                           or "kroner" in window) \
            else ("COUNT", None)
        out.append({
            "quantity_type": qtype, "value": c, "range_bounds": None,
            "unit": unit, "comparator": "=",
            "period": _period(evidence_text, m.start(), m.end()),
            "object_binding": _binding(evidence_text, m.start(), m.end()),
            "role": "COMPONENT", "derivation": "DERIVED",
            "provenance": {"claim_span": None,
                           "evidence_span": m.group(0)},
            "components": [a, d],
        })
    return out


def _interval(q):
    c, v = q["comparator"], q["value"]
    inf = float("inf")
    if c == "UNKNOWN":
        return None
    if c == "=":
        return (True, v, v, True)
    if c == ">":
        return (False, v, inf, False)
    if c == ">=":
        return (True, v, inf, False)
    if c == "<":
        return (False, -inf, v, False)
    if c == "<=":
        return (False, -inf, v, True)
    if c == "BETWEEN" and q.get("range_bounds"):
        lo, hi = q["range_bounds"]
        return (True, lo, hi, True)
    if c == "APPROXIMATE":
        return (True, 0.9 * v, 1.1 * v, True)
    return None


def _subset(s, c):
    s_lo_i, s_lo, s_hi, s_hi_i = s
    c_lo_i, c_lo, c_hi, c_hi_i = c
    if s_lo < c_lo:
        return False
    if s_lo == c_lo and s_lo_i and not c_lo_i:
        return False
    if s_hi > c_hi:
        return False
    if s_hi == c_hi and s_hi_i and not c_hi_i:
        return False
    return True


def _disjoint(s, c):
    if s[2] < c[1]:
        return True
    if s[2] == c[1] and (not s[3] or not c[0]):
        return True
    if c[2] < s[1]:
        return True
    if c[2] == s[1] and (not c[3] or not s[0]):
        return True
    return False


def _compare(cq, eq):
    """Directional relation: evidence interval vs claim interval."""
    if cq["comparator"] == ">" and eq["comparator"] == "=" \
            and eq["value"] == cq["value"]:
        # A strict claim threshold at exactly the evidence amount is not
        # proven by the amount itself ("more than X" needs > X).
        return UNRESOLVED
    if cq["quantity_type"] == "DATE":
        if cq["value"] == eq["value"]:
            return ENTAILS
        return CONTRADICTS
    s, c = _interval(eq), _interval(cq)
    if s is None or c is None:
        return UNRESOLVED
    if cq["comparator"] == "=" and not cq.get("range_bounds"):
        v = cq["value"]
        lo_i, lo, hi, hi_i = s
        if ((lo < v < hi) or (v == lo and lo_i)
                or (v == hi and hi_i)):
            return ENTAILS
    if _subset(s, c):
        return ENTAILS
    if _disjoint(s, c):
        return CONTRADICTS
    return UNRESOLVED


def _compare_coverage(cq, eq, claim_text):
    """Coverage-style relation for bounded age/scope quantities: the
    evidence range covers the claim interval; a claim reaching beyond a
    finite evidence upper bound is a conflict (not entailment)."""
    if cq["quantity_type"] not in ("AGE", "PERIOD"):
        return None
    if cq.get("range_bounds") and eq.get("range_bounds"):
        c_lo, c_hi = cq["range_bounds"]
        e_lo, e_hi = eq["range_bounds"]
        if e_lo <= c_lo and c_hi <= e_hi:
            return ENTAILS
        if c_hi > e_hi or c_lo < e_lo:
            return CONTRADICTS
        return UNRESOLVED
    if not cq.get("range_bounds") and eq.get("range_bounds"):
        e_lo, e_hi = eq["range_bounds"]
        c = _interval(cq)
        if c is None:
            return None
        lo_i, lo, hi, hi_i = c
        lo_eff = e_lo if lo == float("-inf") else lo
        covered = lo_eff >= e_lo and hi <= e_hi
        if covered:
            if re.search(r"(?<![a-z])(?:bare|kun|utelukkende)(?![a-z])",
                         claim_text.lower()):
                return CONTRADICTS
            return ENTAILS
        if hi > e_hi:
            return CONTRADICTS
        return UNRESOLVED
    return None


def _compatible(cq, eq):
    ct, et = cq["quantity_type"], eq["quantity_type"]
    if ct != et:
        return False
    if (cq["unit"] or None) != (eq["unit"] or None):
        return False
    return True


def _identity(cq, eq):
    if not _compatible(cq, eq):
        return False
    cp = cq.get("period") or None
    ep = eq.get("period") or None
    if (cp or ep) and cq["quantity_type"] == "AGE":
        # AGE quantities have no period dimension; a nearby "kr/mnd" must
        # not leak a MONTH period onto an age range (e.g. "712 kr/mnd ...
        # 0 til 3 ar" in the same sentence).
        cp = ep = None
    if cp and ep:
        return cp == ep
    if cp != ep:
        # One-sided period context: only identical values (or an
        # aggregate role that resolves elsewhere) share identity.
        return cq["value"] == eq["value"] or cq["role"] == "AGGREGATE"
    return True


def _aggregate_ok(cq, eq, eqs):
    """Component/aggregate role mismatch is not a contradiction when role
    labels resolve elsewhere in the evidence (contract: aggregate vs
    component section)."""
    if cq["role"] == eq["role"]:
        return True
    pair = {cq["role"], eq["role"]}
    if pair == {"COMPONENT", "STANDALONE"}:
        return True
    if pair == {"AGGREGATE", "STANDALONE"}:
        return True
    if pair == {"AGGREGATE", "COMPONENT"}:
        return any(q.get("derivation") == "DERIVED"
                   and q["quantity_type"] == cq["quantity_type"]
                   for q in eqs)
    return False


def _has_ctx(cq, want):
    return want.search(cq.get("object_binding") or "")


def _best_binding(cq, cands):
    """Prefer evidence whose binding context matches the claim's
    (full sats vs delt sats vs AAP)."""
    want_full = bool(_has_ctx(cq, FULL_CTX))
    want_delt = bool(_has_ctx(cq, DELT_CTX))
    want_aap = bool(_has_ctx(cq, AAP_CTX))

    def key(eq):
        k = 0
        if cq.get("object_binding") and eq.get("object_binding"):
            c_binds = [t for t in cq["object_binding"].split()
                       if t not in STOP]
            k += 3 * sum(1 for t in c_binds
                         if any(tok_match(t, e) for e in
                                eq["object_binding"].split()))
        e_full = _has_ctx(eq, FULL_CTX)
        e_delt = _has_ctx(eq, DELT_CTX)
        if want_aap and _has_ctx(eq, AAP_CTX):
            k += 3
        if want_full == want_delt:
            # Both or neither context on the claim side: value and
            # comparator decide; context cannot conflict.
            if cq["value"] == eq["value"]:
                k += 2
            if cq["comparator"] == eq["comparator"]:
                k += 1
            return k
        if want_full:
            if e_full:
                k += 2
            elif e_delt:
                k -= 4
            else:
                if cq["value"] == eq["value"]:
                    k += 2
                if cq["comparator"] == eq["comparator"]:
                    k += 1
        if want_delt:
            if e_delt:
                k += 2
            elif e_full:
                k -= 4
            else:
                if cq["value"] == eq["value"]:
                    k += 2
                if cq["comparator"] == eq["comparator"]:
                    k += 1
        return k
    return max(cands, key=key)


def numeric_relation(claim_text, evidence_text):
    """Aggregate directional numeric relation; None when claim carries no
    semantic quantity."""
    cqs = parse_quantities(claim_text)
    if not cqs:
        return None
    eqs = parse_quantities(evidence_text) + derived_quantities(evidence_text)
    if not eqs:
        return None
    if any(q["quantity_type"] == "MONEY" for q in eqs):
        for q in eqs:
            if q["quantity_type"] == "COUNT" and q["value"] > 500:
                q["quantity_type"] = "MONEY"
                q["unit"] = "NOK"
    if any(q["quantity_type"] == "MONEY" for q in cqs):
        for q in cqs:
            if q["quantity_type"] == "COUNT" and q["value"] > 500:
                q["quantity_type"] = "MONEY"
                q["unit"] = "NOK"

    # Full-date stamps resolve against full dates; year-only values
    # (*/101 suffix) match at year granularity and stay unresolved when
    # the evidence offers no year at all.
    date_full = {q["value"] for q in eqs
                 if q["quantity_type"] == "DATE" and q["value"] % 10000 != 101}
    date_years = {int(q["value"]) // 10000 for q in eqs
                  if q["quantity_type"] == "DATE"}
    date_results = []
    date_cq_indexes = []
    for i, cq in enumerate(cqs):
        if cq["quantity_type"] != "DATE":
            continue
        date_cq_indexes.append(i)
        if cq["value"] % 10000 == 101:
            year = int(cq["value"]) // 10000
            date_results.append(ENTAILS if year in date_years else UNRESOLVED)
        else:
            date_results.append(ENTAILS if cq["value"] in date_full
                                else CONTRADICTS)
    if len(date_cq_indexes) == len(cqs):
        if CONTRADICTS in date_results:
            return CONTRADICTS
        if UNRESOLVED in date_results:
            return UNRESOLVED
        return ENTAILS

    # Grade claims compare as sets; a restrictive qualifier ("bare/kun/
    # utelukkende") demands the exact set, otherwise subset coverage.
    if (cqs and all(q["quantity_type"] == "GRADE" for q in cqs)
            and eqs and all(q["quantity_type"] == "GRADE" for q in eqs)):

        def grade_set(qs):
            out = set()
            for q in qs:
                if q.get("range_bounds"):
                    lo, hi = q["range_bounds"]
                    out.update(int(v) for v in range(int(lo), int(hi) + 1))
                else:
                    out.add(int(q["value"]))
            return out

        cset, eset = grade_set(cqs), grade_set(eqs)
        restrictive = re.search(
            r"(?<![a-z])(utelukkende|bare|kun)(?![a-z])",
            claim_text.lower())
        if cset <= eset and (not restrictive or cset == eset):
            return ENTAILS
        if restrictive and cset != eset:
            return CONTRADICTS
        if not cset <= eset and all(
                q["comparator"] == "=" and not q.get("range_bounds")
                for q in cqs):
            # Closed-world enumeration: a point grade claim whose grade is
            # absent from the evidence's explicit list is a positive
            # conflict about the same listed activity, not a gap.
            return CONTRADICTS
        return UNRESOLVED

    # Fraction-of-evidence claims ("halvparten av X", "dobbelt av X"):
    # when the evidence states the base amount and a fraction relation,
    # the derived product is entailed even though the base itself is
    # never restated as the claim's amount.
    frac = re.search(r"halvparten(?:\s+av)?\s+(?:full\s+sats\s+pa\s+)?"
                     r"(%s)" % NUM, claim_text, re.IGNORECASE)
    if frac:
        base = _value(frac.group(1))
        if any(eq["value"] == base for eq in eqs) and any(
                re.search(r"halveres|halvparten", evidence_text.lower())
                for _ in (0,)):
            return ENTAILS

    # Claim-side explicit arithmetic "a + b = c" resolves before any
    # per-quantity binding.
    ar = re.search("(" + NUM + r")\s*(?:\+|pluss|og)\s*(" + NUM
                   + r")\s*(?:=|er)\s*(" + NUM + r")",
                   claim_text, re.IGNORECASE)
    arithmetic_result = None
    if ar:
        a, b, c = (_value(ar.group(1)), _value(ar.group(2)),
                   _value(ar.group(3)))
        arithmetic_result = ENTAILS if a + b == c else CONTRADICTS

    # A lone aggregate value with no matching evidence quantity is a
    # positive conflict, not a neutral unresolved.
    non_date = [q for q in cqs if q["quantity_type"] != "DATE"]
    aggregate_result = None
    if (len(non_date) == 1 and not arithmetic_result
            and not non_date[0].get("range_bounds")
            and non_date[0]["role"] == "AGGREGATE"
            and non_date[0]["comparator"] == "="
            and not any(eq["value"] == non_date[0]["value"]
                        and eq["quantity_type"] == non_date[0]["quantity_type"]
                        for eq in eqs)):
        aggregate_result = CONTRADICTS

    results = []
    for i, cq in enumerate(cqs):
        if i in date_cq_indexes:
            results.append(date_results[date_cq_indexes.index(i)])
            continue
        cands = [eq for eq in eqs
                 if _identity(cq, eq) and _aggregate_ok(cq, eq, eqs)]
        if not cands:
            results.append(UNRESOLVED)
            continue
        if _has_ctx(cq, AAP_CTX):
            aap = [eq for eq in cands if _has_ctx(eq, AAP_CTX)]
            if any(_compare(cq, eq) == ENTAILS for eq in aap):
                results.append(ENTAILS)
            else:
                results.append(UNRESOLVED)
            continue
        eq = _best_binding(cq, cands)
        cov = _compare_coverage(cq, eq, claim_text)
        results.append(cov if cov is not None else _compare(cq, eq))
    if arithmetic_result is not None:
        results.append(arithmetic_result)
    if aggregate_result is not None:
        results.append(aggregate_result)
    if CONTRADICTS in results:
        return CONTRADICTS
    if UNRESOLVED in results:
        return UNRESOLVED
    return ENTAILS


def numeric_gate(claim_text, evidence_text):
    """True when the numeric layer blocks lexical support rules."""
    rel = numeric_relation(claim_text, evidence_text)
    return rel in (CONTRADICTS, UNRESOLVED)
