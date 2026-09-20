#!/usr/bin/env python3
"""Deterministic polarity engine (SEMANTIC-JUDGE-DETERMINISTIC-POLARITY-ALIGNER).

Decides SUPPORTED / CONTRADICTED / INSUFFICIENT_EVIDENCE per atom from
deterministic quote signals only. No model calls, no claim-id logic.
Aggregation follows the frozen v0.3 aggregation-spec (PARTIAL only for
mixed compound claims). Luna has no role in this module.
"""
import json
import os
import re

from quote_aligner import (
    MAPS, canon_tokens, content_tokens, decompose_claim, extract_dates,
    extract_numbers, has_exception_marker, has_negation, has_universal,
    micro_spans, modality_of, score_span, split_sentences, strip_parens,
    V041, age_relation, align_atom, extract_ages, _tok_hit)

try:
    import sys as _sys
    if V041 not in _sys.path:
        _sys.path.insert(0, V041)
    from modality import modality_relation as _modality_relation
except Exception:
    _modality_relation = None

FUNCTION_FAMILIES = MAPS.get("function_families", {})
ACTOR_FAMILIES = MAPS.get("actor_families", {})
SYNONYMS = MAPS["synonyms"]

VERBS = {"har", "hadde", "kan", "kunne", "skal", "maa",
         "faar", "blir", "ble", "gir", "gis", "krever", "kreves",
         "gjelder", "dekker", "stiller", "yter", "samtykk", "henvise",
         "henvend", "ring", "fa", "love", "brytes", "utreder",
         "kartlegger", "diagnostiserer", "svarte", "hadde", "fikk",
         "maatte", "mister", "teller", "reduseres", "innvilges",
         "utbetales", "gjennemfores", "gjennomfores", "gjores", "dig", "hor", "samtykke", "samtykk"}

VERBS = VERBS | {"gjeld", "gjelder"}

INJECTION_PATTERNS = [
    r"system-override", r"til dommeren", r"ignore (all )?previous",
    r"ignorer (alle )?tidligere", r"svaret ditt sk(al|ulle) v(æ|ae)re",
    r"uansett innhold", r"disregard (all|any) (previous|above)",
]
APPROX_MARKERS = ["ca.", "ca ", "cirka", "omtrent", "rundt ", " ca.",
                  "≈"]
CONDITION_GUARDS = ["eksempel", "egen beregning", "avrundet", "hvis ",
                    "dersom ", "for soknader", "for søknader", "sendt ",
                    "mottatt ", "per 30.", "per 1.", " - "]
VERBS = VERBS | {"hores"}
OTHER_AGENTS = {"foreldr", "foreldreansvar", "verge", "kommun", "nav",
                "husbank"}

ANTONYM_PAIRS = [
    {"full", "halv"},
    {"permanent", "midlertidig"},
    {"gammel", "nye"},
    {"gamle", "nye"},
]

PARTITIVE_Q = {"flere", "noen", "del", "enkelte", "særlige", "saerlige",
               "varierer"}

OPTIONALITY = {"kunne", "kan", "valgfri", "frivillig", "mulig"}

SUPERLATIVES = {"kortest", "best", "størst", "storst", "høyest", "hoyest",
                "lavest", "raskest", "lengst", "mest"}


def detect_injection(source_text):
    t = str(source_text or "").lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, t):
            return True
    return False


def _stem_set(text):
    return set(canon_tokens(text))


def _verb_overlap(atom_text, sentence):
    a = set(canon_tokens(atom_text))
    s = set(canon_tokens(sentence))
    return bool(a & s & VERBS) or bool(a & s & {"ikke", "ingen", "aldri"}) is False and False


def _shared_verb(atom_text, sentence):
    a = set(canon_tokens(atom_text))
    s = set(canon_tokens(sentence))
    hit = a & s & VERBS
    return sorted(hit)


def _actor_tokens(text):
    t = set(canon_tokens(text))
    found = {}
    for fam, members in ACTOR_FAMILIES.items():
        for m in members:
            if m in t:
                found[m] = fam
    return found


def _actor_conflict(atom_text, sentence):
    """True when atom actor and sentence actor are both identified and
    belong to DIFFERENT families (closed-world guard, spec section 16)."""
    at = _actor_tokens(atom_text)
    st = _actor_tokens(sentence)
    if not at or not st:
        return False
    a_fams = set(at.values())
    s_fams = set(st.values())
    return not (a_fams & s_fams)


def _find_numbers_in(spans_or_text):
    return extract_numbers(spans_or_text)


def _unit_compat(u1, u2):
    if u1 == u2:
        return True
    if {u1, u2} <= {"phone", "plain"}:
        return True
    return False


_UNIT_EQ = {"nok": {"kroner", "kr", "nok"},
            "pct": {"prosent", "%", "pct"},
            "mo": {"maneder", "maaneder", "maned", "maaned", "maan",
                   "mnd", "mo"},
            "yr": {"aar", "ar", "yr"},
            "dy": {"dager", "dgn", "dag", "dy"},
            "wk": {"uker", "uke", "wk"}}


def _unit_eq(u1, u2):
    if u1 == u2:
        return True
    return u2 in _UNIT_EQ.get(u1, {u1})


def _central_number(numbers):
    typed = [n for n in numbers if n["unit"] not in ("plain", "phone")]
    pool = typed or numbers
    return pool[-1] if pool else None


def _numeric_state(atom_text, sentence, source_text):
    """equal / diff / absent. equal: all claim numbers found (same unit)
    in the aligned sentence. diff: central typed number missing but a
    comparable-unit number exists in a subject-overlapping sentence."""
    claim_nums = extract_numbers(atom_text)
    if not claim_nums:
        return "none", None
    sent_nums = extract_numbers(sentence)
    sent_vals = {(n["value"], n["unit"]) for n in sent_nums}
    ok = True
    for n in claim_nums:
        if not any(n["value"] == v and _unit_compat(n["unit"], u)
                   for (v, u) in sent_vals):
            ok = False
            break
    if ok:
        return "equal", None
    central = _central_number(claim_nums)
    if central is None:
        return "absent", None
    if _has_condition_guard(atom_text):
        return "absent", None
    for sent in split_sentences(source_text):
        if score_span(atom_text, sent) < 0.3:
            continue
        for n in extract_numbers(sent):
            if n["value"] == central["value"] and                     _unit_compat(n["unit"], central["unit"]):
                return "absent", None
    for sent in split_sentences(source_text):
        if score_span(atom_text, sent) < 0.4:
            continue
        for n in extract_numbers(sent):
            if n["unit"] == central["unit"] and                     n["unit"] in ("money", "pct", "G", "months", "days",
                                  "years") and                     not _has_condition_guard(sent) and                     not any(c["value"] == central["value"] and
                            _unit_eq(c["unit"], central["unit"])
                            for c in claim_nums):
                return "diff", sent
    return "absent", None


def _proof_span(kind, atom_text, span, source_text, extra=None):
    """Spec section 18/19: no CONTRADICTED/SUPPORTED without proof."""
    s = source_text.find(span[:60]) if span else -1
    return {"proof_type": kind, "claim": atom_text,
            "source_span": span, "span_start": s,
            "span_end": (s + len(span)) if s >= 0 else -1,
            **(extra or {})}


def _age_relation(atom_text, sentence):
    import quote_aligner as _qa
    a_ages = _qa.extract_ages(atom_text)
    s_ages = _qa.extract_ages(sentence)
    if not a_ages or not s_ages:
        return None
    rels = {_qa.age_relation(a, s) for a in a_ages for s in s_ages}
    if "disjoint" in rels:
        return "disjoint"
    if rels == {"subset"}:
        return "subset"
    if "overlap" in rels:
        return "overlap"
    return "overlap"


PREDICATE_WORDS = {"ringe", "ring", "ringte", "ringer", "ringe", "kontakt",
                   "kontakte", "kontaktes", "telefon", "nummer", "via", "man",
                   "ved", "per", "gjelder", "gjelde", "varer", "dreier"}
DEADLINE_RE = re.compile(r"\b(?:innen|frist|senest|begjæring|deadline)\b",
                         re.IGNORECASE)
DURATION_RE = re.compile(r"(?:\bi\s+\d+\s*(?:uke|måned|mnd|år)|varer|gjelder i)",
                         re.IGNORECASE)


def _has_condition_guard(text):


    t = " " + str(text or "").lower() + " "
    if any(m in t for m in CONDITION_GUARDS):
        return True
    if any(m in t for m in APPROX_MARKERS):
        return True
    return False


def _neg_form_match(atom_text, sentence):
    """Spec section 9 scope: 'ingen kostnad/gebyr/pris' grounds a positive
    'gratis' claim (driven by neg_forms in predicate-map.json)."""
    nf = MAPS.get("neg_forms", {})
    atoks = set(canon_tokens(atom_text))
    stoks = set(canon_tokens(sentence))
    for orig, mapped in nf.items():
        if (set(canon_tokens(mapped)) & atoks) and \
                (set(canon_tokens(orig)) & stoks) and \
                has_negation(sentence):
            return True
    return False


def _clause_spans(sentence):
    """Split one source sentence into micro-spans and connector clauses."""
    sps = micro_spans(sentence)
    out = list(sps) if len(sps) > 1 else []
    for sp in re.split(r"\s+eller\s+|\s+og\s+", sentence):
        if sp.strip():
            out.append({"text": sp.strip()})
    return out or [{"text": sentence}]


def _content_hit(atom_text, sentence):
    """Score-0 content token overlap (non-stopword, non-verb)."""
    a = [t for t in content_tokens(atom_text) if t not in VERBS]
    s = set(content_tokens(sentence))
    return bool(a and any(_tok_hit(t, s) for t in a))


def _tok_hit_engine(a, s_set):
    if a in s_set:
        return True
    if len(a) >= 5:
        for b in s_set:
            if len(b) >= 5 and (a.startswith(b) or b.startswith(a)):
                return True
    return False


def _cost_axis_opposition(atom_text, sentence):
    """Claim says free of charge; source says it costs money."""
    a = str(atom_text or "").lower()
    if "gratis" not in a:
        return None
    s = strip_parens(str(sentence or "")).lower()
    if has_negation(s):
        return None
    s_costs = any(m in s for m in ("koster", "kostnad", "gebyr", "pris",
                                   "betaler", "kroner")) or "kr" in s
    if not s_costs:
        return None
    if not _content_hit(atom_text, sentence):
        return None
    return ("COST_AXIS_OPPOSITION", sentence)


def _modifier_antonym(atom_text, sentence):
    """full vs halv, permanent vs midlertidig, gamle vs nye over a shared
    context."""
    a_toks = set(canon_tokens(atom_text))
    s_toks = set(canon_tokens(strip_parens(sentence)))
    for pair in ANTONYM_PAIRS:
        if (pair & a_toks) and ((pair - a_toks) & s_toks):
            ant = pair - a_toks
            shared = (a_toks & s_toks) - pair - ant
            if len(shared) >= 2:
                return ("MODIFIER_ANTONYM", sentence)
    return None


_NONEXHAUSTIVE = ("blant annet", "bl.a", "deriblant", "mellom annet",
                  "for eksempel", "f.eks", "inkludert")


def _exclusivity_conflict(atom_text, sentence):
    """kun/bare/alene X, but the source lists X together with new factors.
    Only fires when the claimed factor is present in the source."""
    a = str(strip_parens(atom_text) or "").lower()
    if not re.search(r"\b(?:kun|bare|alene)\b", a):
        return None
    s = str(strip_parens(sentence) or "").lower()
    if any(m in s for m in _NONEXHAUSTIVE):
        return None
    if " og " not in s and " eller " not in s:
        return None
    claim_factors = set(content_tokens(a)) - {"kun", "bare", "alene"}
    s_content = set(content_tokens(s))
    factor_hit = bool(claim_factors) and all(
        _tok_hit_engine(t, s_content) for t in claim_factors)
    new_factors = [t for t in s_content
                   if not any(_tok_hit_engine(t, ct) for ct in claim_factors)
                   and t not in VERBS and len(t) >= 5]
    if factor_hit and new_factors:
        return ("EXCLUSIVITY_CONFLICT", sentence)
    return None


def _exclusivity_unverified(atom_text, sentence, source_text):
    """kun/bare/alene claim whose aligned span never marks exhaustivity."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(sentence) or "").lower()
    if not re.search(r"\b(?:kun|bare|alene)\b", a):
        return None
    if re.search(r"\b(?:kun|bare|alene|eneste)\b", str(source_text or "").lower()):
        return None
    if re.search(r"\b(?:kun|bare|alene|eneste)\b", s):
        return None
    if not _content_hit(atom_text, sentence):
        return None
    return ("EXCLUSIVITY_UNVERIFIED", sentence)


def _recipient_disjoint(atom_text, sentence):
    """bare til A vs til B with disjoint recipient phrases."""
    a = str(strip_parens(atom_text) or "").lower()
    m = re.search(r"\b(?:bare|kun)\s+(?:til\s+)?(.+)", a)
    if not m:
        return None
    claim_recip = m.group(1).strip()
    s = str(strip_parens(sentence) or "").lower()
    sm = re.search(r"\btil\s+(.+)", s)
    if not sm:
        return None
    cr = set(content_tokens(claim_recip))
    sr = set(content_tokens(sm.group(1)))
    if not cr or not sr:
        return None
    if not any(_tok_hit_engine(t, sr) for t in cr):
        return ("RECIPIENT_DISJOINT", sentence)
    return None


def _not_required_support(atom_text, sentence):
    """uten-X claims need the span to address X as optional/absent."""
    a = str(strip_parens(atom_text) or "").lower()
    m = re.search(r"uten\s+(\w+)", a)
    if not m:
        return True
    x = m.group(1)
    s_toks = set(canon_tokens(strip_parens(sentence)))
    if not _tok_hit_engine(x, s_toks):
        return True
    return bool(s_toks & OPTIONALITY) or "ikke" in s_toks


def _number_pair_misbinding(atom_text, sentence):
    """Claim pairs N1 with N2; the sentence carries both numbers but in
    different eller/og clauses.""" 
    claim_nums = [n["value"] for n in extract_numbers(atom_text)
                  if n["unit"] != "ref"]
    if len(claim_nums) < 2:
        return None
    clauses = [sp["text"] for sp in _clause_spans(sentence)]
    for i, n1 in enumerate(claim_nums):
        for n2 in claim_nums[i + 1:]:
            def has(cl, v):
                return any(n["value"] == v for n in extract_numbers(cl))
            c1 = [cl for cl in clauses if has(cl, n1)]
            c2 = [cl for cl in clauses if has(cl, n2)]
            together = [cl for cl in clauses
                        if has(cl, n1) and has(cl, n2)]
            if c1 and c2 and not together:
                return ("NUMBER_PAIR_MISBINDING", sentence)
    return None


def _misbinding(atom_text, sentence):
    """Claim binds number N to condition C; the source clause carrying N
    lacks C while another clause with a different number has C."""
    spans = micro_spans(sentence)
    if len(spans) < 2:
        return None
    claim_spans = micro_spans(str(atom_text))
    if not claim_spans:
        return None
    best = None
    for cspan in claim_spans:
        c_nums = extract_numbers(cspan["text"])
        if not c_nums:
            continue
        c_toks = set(canon_tokens(cspan["text"]))
        cond_excl = c_toks - PREDICATE_WORDS - VERBS
        cond_excl = {t for t in cond_excl
                     if t not in {str(int(n["value"])) for n in c_nums}}
        if not cond_excl:
            continue
        for c_num in c_nums:
            n_sps = [sp for sp in spans
                     if any(n["unit"] == c_num["unit"] and
                            n["value"] == c_num["value"]
                            for n in extract_numbers(sp["text"]))]
            for nsp in n_sps:
                nsp_toks = set(canon_tokens(nsp["text"]))
                contrast = bool(nsp_toks & {"ellers", "alternativt",
                                            "annet", "annledning"}) or \
                    "ikke" in nsp_toks
                if not contrast:
                    continue
                for sp in spans:
                    if sp is nsp:
                        continue
                    sp_toks = set(canon_tokens(sp["text"]))
                    if (cond_excl & sp_toks) and extract_numbers(sp["text"]):
                        best = {"claim_number": c_num["value"],
                                "condition": sorted(cond_excl & sp_toks)[:4],
                                "span": nsp["text"]}
    return best


def _function_division(atom_text, source_text, best_sent):
    """Bounded division-of-function rule (spec sections 14-15): claim says
    actor A can F; the source sentence about A describes a DIFFERENT
    function, and F is either explicitly reserved elsewhere or the role
    sentence is an exhaustive role enumeration (oppgaver)."""
    fam_hit = None
    for fam, data in FUNCTION_FAMILIES.items():
        for pat in data["claim_markers"]:
            if re.search(pat, atom_text, re.IGNORECASE):
                fam_hit = (fam, data)
                break
    if not fam_hit:
        return None
    fam, data = fam_hit
    actor_toks = set(_actor_tokens(atom_text))
    about_a = None
    for sent in split_sentences(source_text):
        stoks = set(canon_tokens(sent))
        if actor_toks and (actor_toks & stoks):
            about_a = sent
            break
    if not about_a:
        return None
    fam_anywhere = any(
        re.search(p, sent, re.IGNORECASE)
        for sent in split_sentences(source_text)
        for p in data["claim_markers"])
    if not fam_anywhere:
        return about_a
    if any(re.search(p, about_a, re.IGNORECASE)
           for p in data["claim_markers"]):
        return None
    if not any(re.search(p, about_a, re.IGNORECASE)
               for p in data["other_markers"]):
        return None
    if re.search(r"oppgaver", about_a, re.IGNORECASE):
        return about_a
    for sent in split_sentences(source_text):
        if sent is about_a:
            continue
        if any(re.search(p, sent, re.IGNORECASE)
               for p in data["claim_markers"]) and \
                not (set(_actor_tokens(sent).values()) &
                     set(_actor_tokens(atom_text).values())):
            return sent
    return None


def _enumeration_exclusion(atom_text, sentence):
    t = str(sentence or "").lower()
    if not re.search(r"\b(kun|bare|allene)\b", t):
        return False
    if "eller" not in t and "og" not in t:
        return False
    if _age_relation(atom_text, sentence) == "disjoint":
        return False
    at = _actor_tokens(atom_text)
    st = _actor_tokens(sentence)
    if not at or not st:
        return False
    return not (set(at.values()) & set(st.values()))


def _self_agent_mismatch(atom_text, sentence):
    """Claim's main verb is about acting oneself ('selv') and the aligned
    sentence assigns the action to a guardian agent."""
    a = str(atom_text or "").lower()
    if not re.search(r"\bselv\b", a):
        return False
    if re.search(r"selv\s+(?:hvis|om|dersom)|ikke kan skaffe penger selv",
                 a):
        return False
    if not _shared_verb(atom_text, sentence):
        return False
    st = set(canon_tokens(sentence))
    return any(any(tok.startswith(p) for p in OTHER_AGENTS)
               for tok in st)


def _temporal_conflict(atom_rep, sentence):
    claim_dates = atom_rep.get("dates") or []
    sent_dates = extract_dates(sentence)
    if not claim_dates or not sent_dates:
        return False
    for cd in claim_dates:
        for sd in sent_dates:
            if (cd["y"], cd["m"], cd["d"]) != (sd["y"], sd["m"], sd["d"]):
                return True
    return False


def _hard_support(atom_text, best_sent, n_state, best_score):
    """Spec section 19: support needs numeric/predicate/modality grounding,
    not only lexical overlap."""
    if n_state == "equal":
        return True
    rep = align_atom(atom_text, best_sent)
    claim_mod = rep["modality"]
    source_mod = modality_of(strip_parens(best_sent))
    if claim_mod != "UNKNOWN" and claim_mod == source_mod:
        return True
    if claim_mod == "NEVER" and source_mod in ("NEVER", "NOT_REQUIRED"):
        return True
    a = set(canon_tokens(atom_text))
    s = set(canon_tokens(best_sent))
    if a & s & VERBS:
        return True
    if _neg_form_match(atom_text, best_sent):
        return True
    if (claim_mod == "UNKNOWN" and best_score >= 0.5 and
            not [n for n in extract_numbers(atom_text)
                 if n["unit"] not in ("plain", "phone", "ref")] and
            rep["negated"] == has_negation(strip_parens(best_sent))):
        return True
    if (best_score >= 0.4 and
            not [n for n in extract_numbers(atom_text)
                 if n["unit"] not in ("plain", "phone", "ref")] and
            rep["negated"] == has_negation(strip_parens(best_sent))):
        return True
    return False


SCOPE_WORDS = {"nasjonalt", "nasjonal", "sentralt", "sentral", "alle",
               "alltid", "automatisk", "enkelte", "likt", "lik"}

PLACE_RE = re.compile(
    r"\b(oslo|trondheim|bergen|tromso|troms\u00f8|stavanger|drammen|"
    r"kristiansand)\b", re.IGNORECASE)

_ACTOR_SURFACE_RE = re.compile(
    r"\b(lege|psykolog|foreldre|kommune|kommunen|kommuner|bup|ppt|nav|"
    r"habu|barnevern|familier|spesialist|helsesykepleier|"
    r"familievernkontor)\b", re.IGNORECASE)


def _actor_members():
    members = set()
    for fam in ACTOR_FAMILIES.values():
        members.update(fam)
    return members


def _place_unverified(atom_text, source_text):
    """Claim anchors to a place the source never mentions."""
    a = str(strip_parens(atom_text) or "").lower()
    src = str(source_text or "").lower()
    for m in PLACE_RE.finditer(a):
        if m.group(1).lower() not in src:
            sents = split_sentences(source_text)
            return ("PLACE_UNVERIFIED", sents[0] if sents else source_text)
    return None


def _scope_unverified(atom_text, sentence, source_text):
    """Claim carries a scope/coverage word the aligned span never echoes."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(sentence) or "").lower()
    src = str(source_text or "").lower()
    for w in SCOPE_WORDS:
        if w in a and w not in src and _content_hit(atom_text, sentence):
            return ("SCOPE_WORD_UNVERIFIED", sentence)
    return None


def _subject_unverified(atom_text, source_text):
    """The claim's subject token appears nowhere in the source while the
    source names a different agent."""
    a_content = [t for t in content_tokens(atom_text) if t not in VERBS]
    if not a_content:
        return None
    subj = a_content[0]
    if subj in _actor_members():
        return None
    s_toks = set(canon_tokens(source_text))
    if _tok_hit_engine(subj, s_toks):
        return None
    if not _ACTOR_SURFACE_RE.search(str(source_text or "")):
        return None
    sents = split_sentences(source_text)
    return ("SUBJECT_UNVERIFIED", sents[0] if sents else source_text)


def _partitive_universal(atom_text, sentence):
    """Universal claim vs partitive source (flere/noen/del/enkelte)."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(sentence) or "").lower()
    if not (has_universal(a) or re.search(r"i alle tilfeller", a)):
        return None
    if not any(p in s for p in PARTITIVE_Q):
        return None
    if not _content_hit(atom_text, sentence):
        return None
    return ("PARTITIVE_VS_UNIVERSAL", sentence)


def _restrictive_partitive_contra(atom_text, sentence):
    """Universal claim vs an explicit restrictor over the same noun."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(sentence) or "").lower()
    if not (has_universal(a) or re.search(r"\balle\b", a)):
        return None
    if not re.search(r"\bi\s+(?:s\u00e6|sae|se)rlige\s+([a-z\u00e6\u00f8\u00e5]+)",
                     s):
        return None
    m = re.search(r"\balle\s+([a-z\u00e6\u00f8\u00e5]+)", a)
    if not m:
        return None
    if not _tok_hit_engine(m.group(1), set(canon_tokens(s))):
        return None
    return ("RESTRICTIVE_PARTITIVE_OPPOSITION", sentence)


def _superlative_unverified(atom_text, sentence, source_text):
    """Superlative claim grounded only by a non-comparative source."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(sentence) or "").lower()
    sup = next((w for w in SUPERLATIVES if w in a), None)
    if not sup:
        return None
    if sup in s or sup in str(source_text or "").lower():
        return None
    if not _content_hit(atom_text, sentence):
        return None
    return ("SUPERLATIVE_UNVERIFIED", sentence)


def _conditional_grant_source(atom_text, sentence):
    """Source grants the right conditionally ('som ... rett'); an
    unconditional claim is stronger than the source."""
    s = str(strip_parens(sentence) or "")
    a = str(strip_parens(atom_text) or "").lower()
    if " som " in a:
        return None
    if re.search(r"\bsom\b[^.;]*(?:rett|plikt|krav)", s, re.IGNORECASE) and \
            re.search(r"\b(?:rett|plikt)\b", a, re.IGNORECASE):
        return ("CONDITIONAL_GRANT_SOURCE", sentence)
    return None


def _substitution_unverified(atom_text, sentence):
    """Exactly one substantive claim token missing while the source
    introduces a replacement token."""
    a_content = [t for t in content_tokens(atom_text) if t not in VERBS]
    if len(a_content) < 2:
        return None
    s_toks = set(canon_tokens(strip_parens(sentence)))
    s_content = set(content_tokens(sentence))
    missing = [t for t in a_content if not _tok_hit_engine(t, s_toks)]
    if len(missing) != 1 or len(missing[0]) < 6:
        return None
    if missing[0] in _actor_members():
        return None
    s_extra = [t for t in s_content
               if not any(_tok_hit_engine(t, ct) for ct in a_content)]
    shared = [t for t in a_content if _tok_hit_engine(t, s_toks)]
    if s_extra and len(shared) >= 2:
        return ("TOPIC_TOKEN_UNVERIFIED", sentence)
    return None


def _hits_deficit(atom_text, sentence):
    """Fewer than half of the claim's content tokens grounded and at least
    two missing outright."""
    a_content = [t for t in content_tokens(atom_text) if t not in VERBS]
    if len(a_content) < 3:
        return None
    s_toks = set(canon_tokens(strip_parens(sentence)))
    hits = [t for t in a_content if _tok_hit_engine(t, s_toks)]
    missing = [t for t in a_content if not _tok_hit_engine(t, s_toks)]
    if len(missing) >= 2 and len(hits) < len(missing):
        return ("TOPIC_TOKENS_UNVERIFIED", sentence)
    return None


def _conjunction_unverified(atom_text, sentence):
    """Compound 'A og B': one side grounded, the other missing tokens."""
    a = str(strip_parens(atom_text) or "")
    if not re.search(r"\s+og\s+", a):
        return None
    sides = re.split(r"\s+og\s+", a)
    if len(sides) != 2:
        return None
    s_toks = set(canon_tokens(strip_parens(sentence)))
    side_state = []
    for side in sides:
        toks = [t for t in content_tokens(side) if t not in VERBS]
        if not toks:
            return None
        side_state.append(all(_tok_hit_engine(t, s_toks) for t in toks))
    if side_state[0] != side_state[1]:
        return ("CONJUNCTION_UNVERIFIED", sentence)
    return None


_REQ_VERBS = {"krever", "kreves", "krav", "plikt", "plikter",
              "obligatorisk", "skal", "maa", "m\u00e5"}


def _requirement_opposition(atom_text, sentence):
    """Claim exempts X ('uten X'); source makes X a requirement."""
    a = str(strip_parens(atom_text) or "").lower()
    m = re.search(r"uten\s+([a-z\u00e6\u00f8\u00e5]+)", a)
    if not m:
        return None
    x_toks = canon_tokens(m.group(1))
    s = str(strip_parens(sentence) or "").lower()
    if not any(_tok_hit_engine(t, set(canon_tokens(s))) for t in x_toks):
        return None
    s_toks = set(canon_tokens(s))
    req_stems = set(canon_tokens(" ".join(_REQ_VERBS)))
    if s_toks & req_stems:
        return ("REQUIREMENT_OPPOSITION", sentence)
    return ("EXEMPTION_UNVERIFIED", sentence)


def _age_limit_opposition(atom_text, sentence):
    """Claim says no age limit; source states an age boundary."""
    a = str(strip_parens(atom_text) or "").lower()
    if "uten aldersgrense" not in a:
        return None
    s = str(strip_parens(sentence) or "").lower()
    if re.search(r"\b(?:til|inntil|opptil|over|under)\s+\d+\s*(?:\u00e5r|aa?r)\b",
                 s) or extract_ages(s) or \
            re.search(r"\b\d{1,3}\s*(?:\u00e5r|aa?r)\b", s):
        return ("AGE_LIMIT_UNVERIFIED", sentence)
    return None


_MONTH_DAY_RE = re.compile(
    r"\b(\d{1,2})\.?\s+(januar|februar|mars|april|mai|juni|juli|august|"
    r"september|oktober|november|desember)\b", re.IGNORECASE)


def _month_day_conflict(atom_text, source_text, sentence):
    """Year-less dates: claim month/day differs from source month/day in a
    shared deadline context."""
    cm = [(int(m.group(1)), m.group(2).lower())
          for m in _MONTH_DAY_RE.finditer(str(atom_text or ""))]
    sm = [(int(m.group(1)), m.group(2).lower())
          for m in _MONTH_DAY_RE.finditer(str(source_text or ""))]
    if not cm or not sm:
        return None
    if _has_condition_guard(str(atom_text)):
        return None
    if (cm[0][1] == sm[0][1] and cm[0][0] == sm[0][0]):
        return None
    deadline_word = re.compile(r"(?:innen|frist|senest|deadline)",
                               re.IGNORECASE)
    if deadline_word.search(str(atom_text)) and \
            deadline_word.search(str(source_text)):
        return ("DATE_ANCHOR_CONFLICT", sentence)
    return None


def _date_gate(atom_text, source_text):
    """Claim is anchored to a date before the source's 'etter D'
    transition; old-regime wording is then consistent, not opposed."""
    c_dates = extract_dates(atom_text)
    if not c_dates:
        return False
    m = re.search(r"\b(?:etter|fra)\s+(\d{1,2}\.\d{1,2}\.\d{4})",
                  str(source_text or ""))
    if not m:
        return False
    anchor = extract_dates(m.group(1))
    if not anchor:
        return False
    a = (anchor[0]["y"], anchor[0]["m"], anchor[0]["d"])
    return all((d["y"], d["m"], d["d"]) < a for d in c_dates)


_OBLIGATION_WORDS = re.compile(
    r"\b(p\u00e5budt|pliktig|obligatorisk|skal|m\u00e5|maa)\b",
    re.IGNORECASE)


def _recommendation_block(atom_text, sentence):
    """Source only recommends ('anbefaler'); an obligation-worded claim is
    not grounded by it."""
    s = str(strip_parens(sentence) or "").lower()
    if "anbefaler" not in s and "anbefales" not in s:
        return False
    return bool(_OBLIGATION_WORDS.search(str(strip_parens(atom_text) or "")))


_EXCLUSIVE_WORDS = {"kun", "bare", "alene"}


def _claim_strength_veto(atom_text, source_text, best_sent):
    """Iteration B: veto support when the claim asserts more than the
    source documents. Returns (rule, span) or None."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(best_sent) or "").lower()
    src = str(source_text or "").lower()
    a_toks = set(canon_tokens(atom_text))
    if any(w in a_toks for w in _EXCLUSIVE_WORDS):
        return ("EXCLUSIVITY_UNVERIFIED", best_sent)
    if any(w in a_toks for w in SUPERLATIVES):
        return ("SUPERLATIVE_UNVERIFIED", best_sent)
    if has_universal(a) and any(p in src for p in PARTITIVE_Q):
        return ("PARTITIVE_VS_UNIVERSAL", best_sent)
    if has_universal(a) and not any(w in src for w in
                                    ("alle", "samtlige", "hver", "enhver")) \
            and (PLACE_RE.search(s) or any(p in s for p in PARTITIVE_Q)):
        return ("UNIVERSAL_SCOPE_UNVERIFIED", best_sent)
    for w in ("nasjonalt", "nasjonal", "sentralt", "sentral", "likt",
              "lik", "alltid"):
        if w in a_toks and w not in src and \
                (PLACE_RE.search(s) or "kommun" in s or "kommun" in src):
            return ("SCOPE_INFLATION_UNVERIFIED", best_sent)
    places_c = {m.group(1).lower() for m in PLACE_RE.finditer(a)}
    places_s = {m.group(1).lower() for m in PLACE_RE.finditer(s)}
    if places_c:
        src_lower_places = {p.lower() for p in PLACE_RE.findall(src)}
        if places_s and not (places_c & places_s):
            return ("PLACE_CONFLICT", best_sent)
        if places_s and places_c.issubset(places_s) and \
                not (places_c & src_lower_places):
            return ("PLACE_UNVERIFIED", best_sent)
    if any(m in a for m in ("koster", "kostnad", "gebyr", "pris",
                            "betaler")) and "gratis" in s and \
            not has_negation(s):
        return ("REVERSE_COST_AXIS", best_sent)
    claim_actors = _actor_tokens(atom_text)
    sent_actors = _actor_tokens(best_sent)
    if claim_actors and sent_actors and \
            not (set(claim_actors.values()) & set(sent_actors.values())):
        return ("ACTOR_FAMILY_MISMATCH", best_sent)
    # absent professional role: claim's actor token is a professional
    # role that appears nowhere in the source while the source names
    # different providers for the same service
    _PROF_ROLES = {"ergoterapeut", "tannlege", "l\u00e6r",
                   "arbeidsgiver", "fosterforeld", "barn"}
    for at in set(canon_tokens(atom_text)):
        if at in _PROF_ROLES and not _tok_hit_engine(at, set(canon_tokens(src))) \
                and sent_actors:
            return ("ACTOR_ROLE_UNVERIFIED", best_sent)
    for fam, data in FUNCTION_FAMILIES.items():
        claim_hit = any(re.search(p, a, re.IGNORECASE)
                        for p in data["claim_markers"])
        src_hit = any(re.search(p, src, re.IGNORECASE)
                      for p in data["claim_markers"])
        if claim_hit and not src_hit:
            return ("FUNCTION_UNVERIFIED", best_sent)
    if not re.search(r"\b(?:med|som|uten|ved|etter)\s+\w", a):
        cgr = _conditional_grant_source(atom_text, best_sent)
        if cgr:
            return ("CONDITIONAL_GRANT_SOURCE", best_sent)
    req = _requirement_opposition(atom_text, best_sent)
    if req and req[0] == "EXEMPTION_UNVERIFIED" and \
            not _not_required_support(atom_text, best_sent):
        return ("EXEMPTION_UNVERIFIED", best_sent)
    age_opp = _age_limit_opposition(atom_text, best_sent)
    if age_opp:
        return ("AGE_LIMIT_UNVERIFIED", best_sent)
    if "automatisk" in a_toks and not has_negation(s) and \
            any(m in s for m in ("kan ", "valgfri", "vurderes")):
        return ("AUTOMATIC_UNVERIFIED", best_sent)
    # 'all' inside a claim ('all helsehjelp') is a universal over objects
    if re.search(r"\ball(e)?\s+\w+", a) and not has_universal(a) and \
            not any(w in src for w in ("alle", "alt", "all")):
        return ("UNIVERSAL_SCOPE_UNVERIFIED", best_sent)
    # claim names a specific beneficiary/actor absent from source
    claim_actors = _actor_tokens(atom_text)
    if claim_actors and sent_actors and \
            not (set(claim_actors.values()) & set(sent_actors.values())):
        return ("ACTOR_FAMILY_MISMATCH", best_sent)
    for at in set(canon_tokens(atom_text)):
        if at in ("foreldre", "forelder") and not _tok_hit_engine(
                at, set(canon_tokens(src))) and sent_actors:
            return ("ACTOR_ROLE_UNVERIFIED", best_sent)
    # claim adds a specific expense/service type absent from source
    a_content = [t for t in content_tokens(a) if t not in VERBS]
    src_toks_all = set(canon_tokens(src))
    s_content = set(content_tokens(s))
    for t in a_content:
        if len(t) < 6 or t in s_content or _tok_hit_engine(t, src_toks_all):
            continue
        if t in ("totalt", "samlet", "tilsammen") or \
                any(suf in t for suf in ("st\u00f8nad", "ordning", "trygd",
                                         "ytelse", "penger", "bidrag",
                                         "sats")):
            continue
        if t in ("trondheim", "oslo", "bergen"):
            continue
        rest = [x for x in a_content if x != t]
        if len(rest) >= 1 and all(_tok_hit_engine(x, src_toks_all)
                                  for x in rest):
            return ("PREDICATE_GROUNDING_UNVERIFIED", best_sent)
    # obligation-verb claim grounded by weaker source verb
    if re.search(r"\bskal\b", a) and \
            re.search(r"\bb(?:\u00f8|oe)r\b", s):
        return ("OBLIGATION_WEAKENED", best_sent)
    # predicate grounding: the claim's distinctive non-verb content token
    # is absent from the whole source while the source carries its own
    # differing grounded predicate for the shared topic
    a_content = [t for t in content_tokens(a) if t not in VERBS]
    src_toks_all = set(canon_tokens(src))
    s_content = set(content_tokens(s))
    for t in a_content:
        if len(t) < 6 or t in s_content or _tok_hit_engine(t, src_toks_all):
            continue
        if t in ("totalt", "samlet", "tilsammen") or \
                any(suf in t for suf in ("st\u00f8nad", "ordning", "trygd",
                                         "ytelse", "penger", "bidrag",
                                         "sats")):
            continue
        if t in ("trondheim", "oslo", "bergen"):
            continue
        rest = [x for x in a_content if x != t]
        if len(rest) >= 1 and all(_tok_hit_engine(x, src_toks_all)
                                  for x in rest):
            return ("PREDICATE_GROUNDING_UNVERIFIED", best_sent)
    if re.search(r"\s+og\s+", a):
        sides = re.split(r"\s+og\s+", a)
        if len(sides) == 2:
            s_toks = set(canon_tokens(best_sent))
            def grounded(side):
                toks = [t for t in content_tokens(side) if t not in VERBS]
                return all(_tok_hit_engine(t, s_toks) for t in toks)
            if (not grounded(sides[0]) or not grounded(sides[1])) and \
                    re.search(r"\w+es\b", s):
                return ("PASSIVE_CONJUNCTION_UNVERIFIED", best_sent)
    return None


_SWAP_DOMAINS = [("medisinsk", "pedagogisk"), ("pedagogisk", "medisinsk")]


def _predicate_swap_veto(atom_text, best_sent):
    """Claim names one professional domain; the grounded span names the
    opposed domain for the same function noun."""
    a = str(strip_parens(atom_text) or "").lower()
    s = str(strip_parens(best_sent) or "").lower()
    for dom, opp in _SWAP_DOMAINS:
        if dom in a and opp in s and "utredning" in s:
            return ("PREDICATE_DOMAIN_SWAP", best_sent)
    return None


def _exhaustive_eller_exclusion(atom_text, sentence):
    """Source lists exhaustive signers/referrers with eller; an actor
    outside the list cannot perform the function."""
    s = str(strip_parens(sentence) or "").lower()
    if " eller " not in s or "skal" not in s:
        return False
    claim_actors = _actor_tokens(atom_text)
    sent_actors = _actor_tokens(sentence)
    if not claim_actors or not sent_actors:
        return False
    return not (set(claim_actors.values()) & set(sent_actors.values()))



def decide_atom(atom_text, source_text):
    """One atom verdict from deterministic signals. Hard evidence beats
    soft evidence; mixed soft signals are ambiguous (spec section 21)."""
    rep = align_atom(atom_text, source_text)
    cands = rep["candidates"]
    signals = {"numeric": None, "negation_opposition": False,
               "misbinding": None, "enumeration": False,
               "universal_exception": False, "function_division": None,
               "age_disjoint": False, "self_agent_mismatch": False,
               "discretion_vs_right": False,
               "temporal": False, "modality_relation": None,
               "contra_blocks": [], "soft_blocks": []}
    if not cands:
        return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.5,
                "rule": "no_candidate_span", "signals": signals,
                "proof": None, "review": True}

    support_sents = []
    contra_hits = []  # (kind, span, rule, hard)
    soft_blocks = []  # (kind, span, rule) - support veto only
    n_state, diff_sent = "none", None

    atom_toks = set(canon_tokens(atom_text))
    for c in cands:
        sent, clean = c["sentence"], strip_parens(c["sentence"])
        sent_toks = set(canon_tokens(sent))
        topic_ok = bool(atom_toks & sent_toks)
        if c is not cands[0]:
            n_state, diff_sent = _numeric_state(atom_text, sent,
                                                source_text)
            if n_state == "equal":
                support_sents.append((sent, "numeric_equal"))
            elif n_state == "diff" and diff_sent is not None:
                contra_hits.append(("MUTUALLY_EXCLUSIVE_VALUE", diff_sent,
                                    "numeric_conflict", True))
        if _age_relation(atom_text, sent) == "disjoint" and \
                _shared_verb(atom_text, sent):
            signals["age_disjoint"] = True
            contra_hits.append(("AGE_INTERVAL_OPPOSITION", sent,
                                "age_disjoint", True))
        cost = _cost_axis_opposition(atom_text, sent)
        if cost:
            signals["contra_blocks"].append(cost[0])
            contra_hits.append((cost[0], cost[1], "cost_axis_opposition",
                                True))
        ant = _modifier_antonym(atom_text, sent)
        if ant:
            signals["contra_blocks"].append(ant[0])
            contra_hits.append((ant[0], ant[1], "modifier_antonym", True))
        np_mis = _number_pair_misbinding(atom_text, sent)
        if np_mis:
            signals["contra_blocks"].append(np_mis[0])
            contra_hits.append((np_mis[0], np_mis[1],
                                "number_pair_misbinding", True))
        excl = _exclusivity_conflict(atom_text, sent)
        if excl:
            signals["contra_blocks"].append(excl[0])
            contra_hits.append((excl[0], excl[1], "exclusivity_conflict",
                                True))
        recip = _recipient_disjoint(atom_text, sent)
        if recip:
            signals["contra_blocks"].append(recip[0])
            contra_hits.append((recip[0], recip[1], "recipient_disjoint",
                                True))
        req = _requirement_opposition(atom_text, sent)
        if req:
            signals["contra_blocks"].append(req[0])
            if req[0] == "REQUIREMENT_OPPOSITION":
                contra_hits.append((req[0], req[1],
                                    "requirement_opposition", True))
            else:
                signals["soft_blocks"].append(req[0])
                soft_blocks.append((req[0], req[1],
                                    "exemption_unverified"))
        restr = _restrictive_partitive_contra(atom_text, sent)
        if restr:
            signals["contra_blocks"].append(restr[0])
            contra_hits.append((restr[0], restr[1],
                                "restrictive_partitive", True))
        if _month_day_conflict(atom_text, source_text, sent):
            md = _month_day_conflict(atom_text, source_text, sent)
            signals["contra_blocks"].append(md[0])
            contra_hits.append((md[0], md[1], "date_anchor_conflict", True))
        for fn, rule, arg3 in (
                (_exclusivity_unverified, "exclusivity_unverified", True),
                (_scope_unverified, "scope_unverified", True),
                (_superlative_unverified, "superlative_unverified", True),
                (_substitution_unverified, "topic_token_unverified", False),
                (_hits_deficit, "topic_tokens_unverified", False),
                (_conjunction_unverified, "conjunction_unverified", False),
                (_partitive_universal, "partitive_vs_universal", False),
                (_conditional_grant_source,
                 "conditional_grant_source", False)):
            hit = fn(atom_text, sent, source_text) if arg3 else \
                fn(atom_text, sent)
            if hit:
                signals["soft_blocks"].append(hit[0])
                soft_blocks.append((hit[0], hit[1], rule))
        if _recommendation_block(atom_text, sent):
            signals["soft_blocks"].append("RECOMMENDATION_NOT_OBLIGATION")
            contra_hits.append(("RECOMMENDATION_NOT_OBLIGATION", sent,
                                "recommendation_not_obligation", False))
        if rep["universal"] and topic_ok and has_negation(clean) and \
                _shared_verb(atom_text, sent):
            signals["universal_exception"] = True
            contra_hits.append(("UNIVERSAL_CLAIM_NEGATED", sent,
                                "universal_claim_negated_by_source", True))
        elif rep["universal"] and topic_ok and \
                has_exception_marker(clean) and not rep["negated"]:
            signals["universal_exception"] = True
            contra_hits.append(("UNIVERSAL_VS_EXCEPTION", sent,
                                "universal_claim_vs_exception_bound_source",
                                True))

    claim_neg = rep["negated"] and rep["modality"] not in (
        "NOT_REQUIRED",)
    best = cands[0]
    best_sent = best["sentence"]
    if claim_neg:
        atom_toks2 = atom_toks
        neg_hits = [c for c in cands
                    if has_negation(strip_parens(c["sentence"])) and
                    (atom_toks2 & set(canon_tokens(c["sentence"])))]
        if neg_hits:
            best = neg_hits[0]
            best_sent = best["sentence"]
    clean_sent = strip_parens(best_sent)

    n_state, diff_sent = _numeric_state(atom_text, best_sent, source_text)
    signals["numeric"] = n_state
    if n_state == "equal":
        if _misbinding(atom_text, best_sent):
            mb = _misbinding(atom_text, best_sent)
            signals["misbinding"] = mb
            contra_hits.append(("MUTUALLY_EXCLUSIVE_VALUE", best_sent,
                                "number_condition_misbinding", True))
        else:
            support_sents.append((best_sent, "numeric_equal"))
    elif n_state == "diff" and diff_sent is not None:
        contra_hits.append(("MUTUALLY_EXCLUSIVE_VALUE", diff_sent,
                            "numeric_conflict", True))

    src_neg = has_negation(clean_sent)
    if src_neg:
        claim_effective_neg = claim_neg or \
            rep["modality"] == "NOT_REQUIRED"
        neg_topics = set()
        for nm in re.finditer(r"\b(?:ingen|ikke|aldri|verken)\s+"
                              r"(\w+)", clean_sent, re.IGNORECASE):
            mapped = MAPS.get("neg_forms", {}).get(nm.group(1).lower())
            if mapped:
                neg_topics.update(canon_tokens(mapped))
        if not claim_effective_neg and neg_topics and \
                (neg_topics & set(canon_tokens(atom_text))):
            src_neg = False
    topic_ok = bool(set(canon_tokens(atom_text)) &
                    set(canon_tokens(best_sent)))
    claim_effective_neg = claim_neg or rep["modality"] == "NOT_REQUIRED"
    exemption_shaped = bool(re.search(r"\buten\s+\w", atom_text,
                                      re.IGNORECASE))
    if not exemption_shaped and claim_effective_neg != src_neg and \
            topic_ok:
        shared = _shared_verb(atom_text, best_sent)
        if shared or best["score"] >= 0.45:
            signals["negation_opposition"] = True
            contra_hits.append(("EXPLICIT_NEGATION", best_sent,
                                "polarity_conflict", False))
    elif (exemption_shaped or claim_effective_neg == src_neg) and \
            (best["score"] >= 0.45 or
                                   rep["modality"] == "NOT_REQUIRED"):
        support_sents.append((best_sent, "polarity_agreement"))

    if _enumeration_exclusion(atom_text, best_sent):
        signals["enumeration"] = True
        contra_hits.append(("EXHAUSTIVE_SET_EXCLUSION", best_sent,
                            "actor_outside_exhaustive_list", False))

    fd = _function_division(atom_text, source_text, best_sent)
    if fd:
        signals["function_division"] = fd
        contra_hits.append(("FUNCTION_RESERVED_TO_OTHER_ACTOR", fd,
                            "division_of_function", True))

    if (re.search(r"\b(?:individrett|rettighet|rett)\b", atom_text,
                  re.IGNORECASE) and
            re.search(r"skj[øo]nnsbestemt|ikke automatisk|"
                      r"ikke en automatisk", strip_parens(best_sent),
                      re.IGNORECASE)):
        signals["discretion_vs_right"] = True
        contra_hits.append(("DISCRETION_VS_ENTITLEMENT", best_sent,
                            "discretion_vs_entitlement", True))

    if _self_agent_mismatch(atom_text, best_sent):
        signals["self_agent_mismatch"] = True
        if _age_relation(atom_text, best_sent) == "disjoint":
            contra_hits.append(("GUARDIAN_AGE_EXCLUSION", best_sent,
                                "guardian_opposes_self_action", True))
    plc = _place_unverified(atom_text, source_text)
    if plc:
        signals["soft_blocks"].append(plc[0])
        soft_blocks.append((plc[0], plc[1], "place_unverified"))
    sub = _subject_unverified(atom_text, source_text)
    if sub:
        signals["soft_blocks"].append(sub[0])
        soft_blocks.append((sub[0], sub[1], "subject_unverified"))
    age_opp = _age_limit_opposition(atom_text, best_sent)
    if age_opp:
        signals["soft_blocks"].append(age_opp[0])
        soft_blocks.append((age_opp[0], age_opp[1],
                            "age_limit_unverified"))
    if not _not_required_support(atom_text, best_sent):
        signals["soft_blocks"].append("EXEMPTION_NOT_GROUNDED")
        soft_blocks.append(("EXEMPTION_NOT_GROUNDED", best_sent,
                            "exemption_not_grounded"))
    if _date_gate(atom_text, source_text):
        signals["soft_blocks"].append("DATE_GATE_OLD_REGIME")
        soft_blocks.append(("DATE_GATE_OLD_REGIME", best_sent,
                            "date_gate_old_regime"))

    c_is_deadline = bool(DEADLINE_RE.search(atom_text))
    s_is_deadline = bool(DEADLINE_RE.search(best_sent))
    compatible_frames = (c_is_deadline == s_is_deadline) or \
        (DURATION_RE.search(atom_text) and s_is_deadline)
    if _temporal_conflict(rep, best_sent) and \
            not _has_condition_guard(best_sent) and compatible_frames:
        signals["temporal"] = True
        contra_hits.append(("TEMPORAL_CONFLICT", best_sent,
                            "incompatible_dates", True))

    if _modality_relation is not None:
        c_mod = rep["modality"]
        s_mod = modality_of(clean_sent)
        try:
            m_rel = _modality_relation(s_mod, c_mod)
        except Exception:
            m_rel = None
        signals["modality_relation"] = m_rel
        if m_rel == "CONFLICT" and c_mod != "NOT_REQUIRED":
            contra_hits.append(("MODALITY_CONFLICT", best_sent,
                                "modality_matrix_conflict", True))

    if contra_hits and support_sents:
        if any(h for *_x, h in contra_hits):
            support_sents = []
        else:
            return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.5,
                    "rule": "ambiguous_evidence", "signals": signals,
                    "proof": None, "review": True}
    if contra_hits:
        kind, span, rule, _hard = sorted(contra_hits,
                                         key=lambda x: 0 if x[3] else 1)[0]
        return {"verdict": "CONTRADICTED", "confidence": 0.9,
                "rule": rule, "signals": signals,
                "proof": _proof_span(kind, atom_text, span, source_text),
                "review": False}
    if signals["self_agent_mismatch"]:
        return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.5,
                "rule": "self_agent_not_established", "signals": signals,
                "proof": None, "review": False}
    if signals["modality_relation"] == "CLAIM_STRONGER":
        return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.6,
                "rule": "claim_stronger_than_source", "signals": signals,
                "proof": None, "review": False}
    claim_nums = [n for n in extract_numbers(atom_text)
                  if n["unit"] != "ref"]
    typed = [n for n in claim_nums
             if n["unit"] not in ("plain", "phone")]
    best_nums = {n["value"] for n in extract_numbers(best_sent)}
    numeric_ok = (not claim_nums or n_state == "equal" or
                  bool(typed and all(n["value"] in best_nums
                                     for n in typed)) or
                  _has_condition_guard(atom_text))
    strong_lex = best["score"] >= 0.5 and claim_neg == src_neg and \
        bool(set(canon_tokens(atom_text)) & set(canon_tokens(best_sent)) &
             VERBS)
    if support_sents and numeric_ok and \
            (_hard_support(atom_text, best_sent, n_state, best["score"]) or
             strong_lex):
        veto = _claim_strength_veto(atom_text, source_text, best_sent)
        if veto:
            signals["soft_blocks"].append(veto[0])
            soft_blocks.append((veto[0], veto[1],
                                veto[0].lower()))
            return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.5,
                    "rule": veto[0].lower(), "signals": signals,
                    "proof": None, "review": True}
        swap = _predicate_swap_veto(atom_text, best_sent)
        if swap:
            signals["soft_blocks"].append(swap[0])
            return {"verdict": "INSUFFICIENT_EVIDENCE",
                    "confidence": 0.5, "rule": "predicate_domain_swap",
                    "signals": signals, "proof": None, "review": True}
        if _exhaustive_eller_exclusion(atom_text, best_sent):
            return {"verdict": "CONTRADICTED", "confidence": 0.85,
                    "rule": "exhaustive_eller_exclusion", "signals": signals,
                    "proof": _proof_span("EXHAUSTIVE_SET_EXCLUSION",
                                         atom_text, best_sent, source_text),
                    "review": False}
        signals["support_evidence"] = "hard" if \
            _hard_support(atom_text, best_sent, n_state, best["score"]) \
            else "lex"
        return {"verdict": "SUPPORTED", "confidence": 0.9,
                "rule": "support_from_quote_alignment", "signals": signals,
                "proof": _proof_span("SUPPORT", atom_text, best_sent,
                                     source_text),
                "review": False}
    return {"verdict": "INSUFFICIENT_EVIDENCE", "confidence": 0.5,
            "rule": "no_deterministic_signal", "signals": signals,
            "proof": None, "review": True}


def aggregate(atom_results, is_compound):
    """Frozen v0.3 aggregation-spec rules 1-5 (deterministic)."""
    vs = [a["verdict"] for a in atom_results]
    n_sup = vs.count("SUPPORTED")
    n_con = vs.count("CONTRADICTED")
    n_ins = vs.count("INSUFFICIENT_EVIDENCE")
    if n_con and n_sup == 0:
        return "CONTRADICTED"
    if n_con > n_sup:
        return "CONTRADICTED"
    if n_con and n_sup and n_con == n_sup:
        return "PARTIALLY_SUPPORTED"
    if n_con and n_sup:
        return "PARTIALLY_SUPPORTED"
    if n_ins == len(vs):
        return "INSUFFICIENT_EVIDENCE"
    if n_sup and n_ins:
        return "PARTIALLY_SUPPORTED" if is_compound else "INSUFFICIENT_EVIDENCE"
    return "SUPPORTED"


def judge_claim(claim_text, source_text):
    atoms = decompose_claim(claim_text)
    atom_results = []
    for i, a in enumerate(atoms, 1):
        res = decide_atom(a, source_text)
        res["atom_id"] = "A%d" % i
        res["atom_text"] = a
        atom_results.append(res)
    verdict = aggregate(atom_results, is_compound=len(atom_results) > 1)
    injection = detect_injection(source_text)
    review = any(a.get("review") for a in atom_results)
    return {
        "verdict": verdict,
        "confidence": round(min(a["confidence"] for a in atom_results), 2),
        "engine": "quote-aligner-deterministic",
        "injection_detected": injection,
        "review_required": review,
        "atom_results": atom_results,
        "atoms": [{"id": a["atom_id"], "text": a["atom_text"],
                   "verdict": a["verdict"], "rule": a["rule"]}
                  for a in atom_results],
    }
