"""Tokenization, normalization, polarity and frame extraction (ASCII-fied Norwegian)."""
import re

STOP = {
    "og", "eller", "en", "et", "ei", "den", "det", "dem", "de", "som", "pa",
    "i", "av", "til", "for", "med", "fra", "om", "at", "a", "er", "var",
    "har", "ha", "kan", "skal", "ma", "vil", "blir", "far", "sa", "ogsa",
    "men", "deres", "sin", "si", "sitt", "sine", "egen", "eget", "egne",
    "seg", "du", "vi", "man", "dette", "disse", "denne", "vaere", "ikke",
    "ja", "nei",
}
NEG_MARKERS = {"ikke", "ingen", "uten"}
QUANT_SET = {"alle", "alltid", "noen", "enhver", "ingen"}
MODAL_SET = {"skal", "ma", "krever", "kreves", "krav", "kravet", "kan",
             "rett", "retten", "plikt", "plikten", "adgang", "mulighet"}
WORD_NUM = {"en": 1, "to": 2, "tre": 3, "fire": 4, "fem": 5, "seks": 6,
            "sju": 7, "syv": 7, "otte": 8, "ni": 9, "ti": 10, "elleve": 11,
            "tolv": 12}
UNIT_WORDS = {"kroner", "kr", "maned", "maneden", "maneder", "maneds", "mnd",
              "ar", "ars", "dager", "dag", "uke", "uker", "g", "prosent",
              "virkedager"}
TOKEN_MAP = {"kr": "kroner", "mnd": "maned"}


def norm(s):
    return s.lower()


def toks(s):
    raw = re.findall(r"[a-zæøå]+|\d+(?:[.,]\d+)*", norm(s))
    out = []
    i = 0
    while i < len(raw):
        t = raw[i]
        if t.isdigit() and i + 1 < len(raw) and raw[i + 1].isdigit() and len(raw[i + 1]) == 3 and len(t) <= 3:
            out.append(t + raw[i + 1])
            i += 2
            continue
        out.append(TOKEN_MAP.get(t, t))
        i += 1
    return out


def content_tokens(s):
    return [t for t in toks(s) if t not in STOP and t not in QUANT_SET]


def tok_match(a, b):
    if a == b:
        return True
    if min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a)):
        return True
    if len(a) >= 6 and len(b) >= 6:
        n = 0
        for x, y in zip(a, b):
            if x != y:
                break
            n += 1
        if n >= 6:
            return True
    return False


def matches(tok, candidates):
    return any(tok_match(tok, c) for c in candidates)


def numbers(s):
    out = []
    for t in toks(s):
        if t.isdigit():
            out.append(int(t))
        elif re.fullmatch(r"\d+[.,]\d+", t):
            out.append(float(t.replace(",", ".")))
        elif t in WORD_NUM:
            out.append(WORD_NUM[t])
    return out


def ranges(s):
    txt = norm(s)
    out = []
    for m in re.finditer(r"(?<![a-z0-9])(\d{1,3})\s*-\s*(\d{1,3})(?!\d)", txt):
        pre = txt[max(0, m.start() - 12):m.start()]
        if "paragraf" in pre or " kap " in pre:
            continue
        out.append((int(m.group(1)), int(m.group(2))))
    return out


def clauses(s):
    parts = re.split(r"[.;:!?()]|,\s+", norm(s))
    return [toks(p) for p in parts if p.strip()]


def polarity(term, s, window=4):
    """True if term appears negated somewhere in s (scoped, clause-local)."""
    for cl in clauses(s):
        for idx, tok in enumerate(cl):
            if tok_match(term, tok):
                lo, hi = max(0, idx - window), min(len(cl), idx + window + 1)
                if any(t in NEG_MARKERS for t in cl[lo:hi]):
                    return True
    return False


def quantifier_pairs(s):
    """(quantifier, bound) pairs like (alle, 25)."""
    out = []
    for m in re.finditer(r"\b(alle|noen)\b[^.;]{0,50}?\b(opptil|opp til|over|under|mer enn|mindre enn)\s*(\d+)", norm(s)):
        out.append((m.group(1), int(m.group(3))))
    return out


def qualifier_pairs(s):
    """(full/delt, number) pairs with adjacency window."""
    out = []
    if re.search(r"[+]", s):
        return out
    tl = toks(s)
    for i, t in enumerate(tl):
        if t in {"full", "delt", "halv"}:
            for j in range(i + 1, min(i + 5, len(tl))):
                u = tl[j]
                if re.fullmatch(r"\d+(?:[.,]\d+)?", u):
                    out.append((t, float(u.replace(",", ".")) if "," in u or "." in u else int(u)))
                    break
    return out


def range_pairs(s):
    """(range, number) pairs like ((11,14), 2078)."""
    out = []
    txt = norm(s)
    for m in re.finditer(r"(?<![a-z0-9])(\d{1,3})\s*-\s*(\d{1,3})(?!\d)", txt):
        pre = txt[max(0, m.start() - 12):m.start()]
        if "paragraf" in pre or " kap " in pre:
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        nm = re.search(r"\d{2,}", txt[m.end():m.end() + 20])
        if nm:
            out.append(((lo, hi), int(nm.group(0))))
    return out


def ctx_pairs(s):
    """(context, number) pairs for condition-bound numbers (akutt etc.)."""
    out = []
    tl = toks(s)
    for i, t in enumerate(tl):
        if t.isdigit() and len(t) >= 3:
            lo, hi = max(0, i - 6), min(len(tl), i + 6)
            window = tl[lo:hi]
            # "ikke-akutt" tokenizes as ikke+akutt; adjacency must win over bare akutt.
            if any(window[j] == "ikke" and window[j + 1] == "akutt"
                   for j in range(len(window) - 1)):
                out.append(("ikke-akutt", int(t)))
            elif "akutt" in window:
                out.append(("akutt", int(t)))
    return out
