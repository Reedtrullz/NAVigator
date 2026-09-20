#!/usr/bin/env python3
"""Deterministic quote aligner for SEMANTIC-JUDGE-DETERMINISTIC-POLARITY-ALIGNER.

Tokenisation, normalisation, span candidate generation and claim
representation. No model calls, no randomness, no claim-id logic.
Luna has no role in this module.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
V041 = os.path.join(os.path.dirname(HERE), "v0.4.1")

with open(os.path.join(HERE, "predicate-map.json"), encoding="utf-8") as f:
    MAPS = json.load(f)

# Frozen v0.4.1 modality normalizer, read-only reuse (spec sections 10-12).
import sys
if V041 not in sys.path:
    sys.path.insert(0, V041)
import modality as _mod


def modality_of(text):
    return _mod.normalize_modality(text or "")


# ---------------------------------------------------------------- tokens
SYNONYMS = MAPS["synonyms"]

_SUFFIXES = ("er", "ar", "en", "et", "ene", "ane", "or", "es")


def tokenize(text):
    t = str(text or "")
    # acronyms with suffixes: PPTs -> ppt, NAV -> nav
    t = re.sub(r"\b([A-Z\u00c6\u00d8\u00c5]{2,})[a-z\u00e6\u00f8\u00e5]*\b",
               lambda m: m.group(1).lower(), t)
    return re.findall(r"[\w\u00e6\u00f8\u00e5\u00c6\u00d8\u00c5]+",
                      t.lower(), re.UNICODE)


def _stem(tok):
    if len(tok) > 5:
        for suf in ("ene", "ane", "nes", "ets", "ens"):
            if tok.endswith(suf):
                return tok[:-len(suf)]
    if len(tok) > 4:
        for suf in ("er", "ar", "en", "et"):
            if tok.endswith(suf):
                return tok[:-len(suf)]
    if len(tok) > 4 and tok.endswith("es"):
        return tok[:-2]
    return tok


def _canon(t):
    if t.startswith("helsesykepl"):
        return "skolehelsetjeneste"
    return SYNONYMS.get(t, t)


def canon_tokens(text):
    # synonyms first, then stemming, so inflected forms converge
    return [_stem(_canon(t)) for t in tokenize(text)]


def content_tokens(text):
    STOP = {"og", "eller", "til", "for", "den", "det", "dem", "som",
            "paa", "i", "med", "er", "var", "har", "kan", "skal",
            "av", "en", "et", "ei", "de", "du", "ved", "fra", "om",
            "att", "ikke", "men", "at", "blir", "ble", "ha", "faa",
            "kunne", "ville", "maa", "vaer"}
    return [t for t in canon_tokens(text) if t not in STOP and len(t) > 2]


def strip_parens(text):
    return re.sub(r"\([^)]*\)", " ", str(text or ""))


# ---------------------------------------------------------------- numbers
_NUM_CLASS_PATTERNS = [
    # unit-bound numbers (highest priority)
    (0, "money", r"(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(?:kr|kroner)\b"),
    (0, "pct", r"(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(?:prosent|%|prosentpoeng)\b"),
    (0, "G", r"\b(\d+(?:[.,]\d+)?)\s*G\b"),
    (0, "months", r"(\d+)\s*m[å¥]*neder\b"),
    (0, "days", r"(\d+)\s*virkedager\b"),
    (0, "weeks", r"(\d+)\s*uke(?:r|ne)?\b"),
    (0, "years", r"(\d+)\s*(?:år|ars)\b"),
    # phone-like numbers
    (1, "phone", r"(?<!\d)(\d{8})(?!\d)"),
    (1, "phone", r"(?<!\d)(\d{3}\s\d{2}\s\d{3})(?!\d)"),
    # space-grouped thousands without unit
    (2, "plain", r"(?<!\d)(\d{1,3}(?:\s\d{3})+)(?!\d)"),
]


def _parse_num(raw):
    raw = raw.strip().replace(" ", "")
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "." in raw:
        first, last = raw.split(".", 1)
        if len(last) == 3 and len(first) <= 3:
            raw = first + last  # Norwegian thousands dot: 1.286
    return float(raw)


def _iter_numbers(text):
    """Priority-class extraction; overlapping lower-priority matches are
    dropped so '1 286 kr' yields exactly one money number."""
    t = str(text or "")
    found = []
    for cls, unit, pat in _NUM_CLASS_PATTERNS:
        for m in re.finditer(pat, t, re.IGNORECASE):
            found.append((cls, m.start(1), m.end(1), unit,
                          _parse_num(m.group(1))))
    # bare numbers last: reject any that overlap an accepted span
    def _is_ref(idx):
        j = idx - 1
        while j >= 0 and t[j] == " ":
            j -= 1
        return j >= 0 and t[j] == "§"
    for m in re.finditer(r"(?<!\d)(\d+(?:[.,]\d+)?)(?!\d)", t):
        unit = "ref" if _is_ref(m.start(1)) else "plain"
        found.append((3, m.start(1), m.end(1), unit,
                      _parse_num(m.group(1))))
    accepted = []
    for cls, s, e, unit, val in sorted(found, key=lambda x: (x[0], x[1])):
        if any(s < ae and as_ < e for (as_, ae) in accepted):
            continue
        accepted.append((s, e))
        yield {"value": val, "unit": unit, "start": s, "end": e}


def extract_numbers(text):
    return list(_iter_numbers(text))


# ---------------------------------------------------------------- ages
_MONTHS = {"januar": 1, "februar": 2, "mars": 3, "april": 4, "mai": 5,
           "juni": 6, "juli": 7, "august": 8, "september": 9,
           "oktober": 10, "november": 11, "desember": 12}


def extract_ages(text):
    """Return list of {op,interval,text} age expressions.
    under X -> [0, X-1]; over X -> [X+1, 200]; fra X -> [X, 200];
    X-Y -> [X, Y]; bare number before 'ar' handled as interval [X, X] when
    tokenised next to a context word (kept simple by spec)."""
    out = []
    t = str(text or "")
    for m in re.finditer(r"under\s+(\d{1,3})\s*(?:\u00e5r|ars|aar|ar)?", t,
                         re.IGNORECASE):
        x = int(m.group(1))
        out.append({"op": "under", "interval": [0, x - 1],
                    "text": m.group(0), "start": m.start(), "end": m.end()})
    for m in re.finditer(r"(?:over|eldre enn)\s+(\d{1,3})\s*"
                         r"(?:\u00e5r|ars|aar|ar)?", t, re.IGNORECASE):
        x = int(m.group(1))
        out.append({"op": "over", "interval": [x + 1, 200],
                    "text": m.group(0), "start": m.start(), "end": m.end()})
    for m in re.finditer(r"(?:fra|fylle?|fylt)\s+(\d{1,3})\s*"
                         r"(?:\u00e5r|ars|aar|ar)?", t, re.IGNORECASE):
        x = int(m.group(1)
                )
        out.append({"op": "fra", "interval": [x, 200],
                    "text": m.group(0), "start": m.start(), "end": m.end()})
    for m in re.finditer(r"(\d{1,3})\s*[-\u2013]\s*(\d{1,3})\s*(?:\u00e5r|ars)?", t,
                         re.IGNORECASE):
        x, y = int(m.group(1)), int(m.group(2))
        out.append({"op": "range", "interval": [x, y],
                    "text": m.group(0), "start": m.start(), "end": m.end()})
    for m in re.finditer(r"(?<![\w\u00e6\u00f8\u00e5.])(\d{1,3})\s*"
                         r"(?:\u00e5r|ars|aar|ar)\b", t, re.IGNORECASE):
        txt = m.group(0)
        # skip spans already captured by fra/fylt/under/over/range above
        if any(m.start() >= o["start"] and m.end() <= o["end"]
               for o in out):
            continue
        rest = t[m.end():m.end() + 8]
        if re.match(r"\s*(?:sidan|siden)\b", rest):
            continue
        x = int(m.group(1))
        out.append({"op": "bare", "interval": [x, x],
                    "text": txt, "start": m.start(), "end": m.end()})
    return out


def age_relation(a, b):
    """disjoint | overlap | subset (claim within source) | superset."""
    ia, ib = a["interval"], b["interval"]
    if ia[1] < ib[0] or ib[1] < ia[0]:
        return "disjoint"
    if ia[0] >= ib[0] and ia[1] <= ib[1]:
        return "subset"
    if ib[0] >= ia[0] and ib[1] <= ia[1]:
        return "superset"
    return "overlap"


# ---------------------------------------------------------------- dates

def extract_dates(text):
    """Return list of {y,m,d,text}. Handles DD.MM.YYYY and 'D. month YYYY'."""
    out = []
    t = str(text or "")
    for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", t):
        out.append({"y": int(m.group(3)), "m": int(m.group(2)),
                    "d": int(m.group(1)), "text": m.group(0)})
    month_names = "|".join(_MONTHS.keys())
    pat = (r"\b(\d{1,2})\.?\s+(%s)\s+(\d{4})\b") % month_names
    for m in re.finditer(pat, t, re.IGNORECASE):
        mo = _MONTHS[m.group(2).lower()]
        out.append({"y": int(m.group(3)), "m": mo, "d": int(m.group(1)),
                    "text": m.group(0)})
    return out


# ---------------------------------------------------------------- negation
_NEGATORS = ("ikke", "ingen", "aldri", "uten", "verken")


def has_negation(text):
    t = str(strip_parens(text) or "").lower()
    if any(w in t for w in _NEGATORS):
        return True
    return bool(re.search(r"\b(?:trenger|kreves|krever|kan|skal|m\u00e5)\s+ikke\b",
                          t))


def has_universal(text):
    t = str(strip_parens(text) or "").lower()
    return any(w in t for w in ("alle", "uansett", "hver", "full taushet",
                                "samtlige", "enhver"))


def has_exception_marker(text):
    t = str(strip_parens(text) or "").lower()
    return any(w in t for w in ("unntak", "kun", "bare", "unntatt"))


# ---------------------------------------------------------------- spans

def split_sentences(text):
    parts, start = [], 0
    t = str(text or "")
    for m in re.finditer(r"[.!?;]", t):
        if m.group() == ".":
            seg = t[start:m.end()]
            nxt = t[m.end():m.end() + 1]
            if re.search(r"\b(?:ca|osv|dvs|evt|eks|f\.eks|bl\.a|inkl|maks|jf|nr)\.$",
                         seg, re.IGNORECASE):
                continue
            if re.search(r"\d\.$", seg) and (
                    nxt.isdigit() or
                    (nxt == " " and t[m.end() + 1:m.end() + 2].islower())):
                continue
        part = t[start:m.end()].strip()
        if part:
            parts.append(part)
        start = m.end()
    tail = t[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def micro_spans(text):
    """Split on , : ; ( ) with offsets into the original string."""
    out = []
    t = str(text or "")
    start = 0
    for m in re.finditer(r"(?<!\d),(?!\d)|[;:()]", t):
        seg = t[start:m.start()].strip()
        if seg:
            out.append({"text": seg, "start": start, "end": m.start()})
        start = m.start() + 1
    tail = t[start:].strip()
    if tail:
        out.append({"text": tail, "start": start, "end": len(t)})
    return out


def _tok_hit(a, s_set):
    if a in s_set:
        return True
    if len(a) >= 5:
        for b in s_set:
            if len(b) >= 5 and (a.startswith(b) or b.startswith(a)):
                return True
    return False


def score_span(atom_text, span_text):
    """Lexical overlap score 0-1 with a small exact-number bonus."""
    a = content_tokens(atom_text)
    s = content_tokens(span_text)
    if not a or not s:
        return 0.0
    sa = set(a)
    ss = set(s)
    ov = sum(1 for tok in sa if _tok_hit(tok, ss)) / len(sa)
    if extract_numbers(atom_text) and extract_numbers(span_text):
        a_nums = {n["value"] for n in extract_numbers(atom_text)}
        s_nums = {n["value"] for n in extract_numbers(span_text)}
        if a_nums & s_nums:
            ov += 0.5
    return min(ov, 1.0)


def candidates(atom_text, source_text, top_n=4):
    """Top micro-spans/sentences overlapping the atom, score > 0.15."""
    cands = []
    for sent in split_sentences(source_text):
        spans = micro_spans(sent)
        pool = spans if len(spans) > 1 else [{"text": sent,
                                             "start": 0, "end": len(sent)}]
        pool.append({"text": sent, "start": 0, "end": len(sent)})
        for sp in pool:
            sc = score_span(atom_text, sp["text"])
            if sc > 0.10:
                cands.append({"sentence": sent, "text": sp["text"],
                              "score": round(min(sc, 1.0), 3),
                              "start": sp["start"], "end": sp["end"]})
    cands.sort(key=lambda x: -x["score"])
    return cands[:top_n]


# ---------------------------------------------------------------- claim rep

def decompose_claim(claim_text):
    """Split claim into atomic parts: sentences, 'men'-clauses and
    comma+og clause joins."""
    parts = []
    for sent in split_sentences(claim_text):
        chunks = re.split(r"\s+men\s+|,\s+og\s+", sent)
        parts.extend([c.strip() for c in chunks if c.strip()])
    return parts or [str(claim_text or "").strip()]


def align_atom(atom_text, source_text):
    rep = {
        "atom": atom_text,
        "candidates": candidates(atom_text, source_text),
        "negated": has_negation(atom_text),
        "universal": has_universal(atom_text),
        "exception": has_exception_marker(atom_text),
        "modality": modality_of(atom_text),
        "numbers": extract_numbers(atom_text),
        "ages": extract_ages(atom_text),
        "dates": extract_dates(atom_text),
        "canon": canon_tokens(atom_text),
    }
    return rep


def align(claim_text, source_text):
    """Full claim alignment: one representation per atom."""
    return {"claim": claim_text,
            "atoms": [align_atom(a, source_text)
                      for a in decompose_claim(claim_text)]}
