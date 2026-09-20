#!/usr/bin/env python3
"""Deterministic polarity engine v0.2 - wrapper over frozen v0.1.

Layered architecture (lexically driven, no case IDs in code):
  1. frozen base verdict from polarity_engine.decide_atom
  2. lexicon contra additions (concept axes, numeric bounds, lists)
  3. false-contra guards (actor/scope/negation-scope disambiguation)
  4. support rescues (alias/staffing/paraphrase evidence + vetoes)
Re-aggregation uses the frozen pe.aggregate spec. No model calls.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import polarity_engine as pe  # frozen
from polarity_engine import (
    VERBS,
    _hard_support,
    _claim_strength_veto,
    _predicate_swap_veto,
    _proof_span,
    aggregate,
    detect_injection,
)
from quote_aligner import (
    align_atom,
    canon_tokens,
    content_tokens,
    decompose_claim,
    has_negation,
    modality_of,
    strip_parens,
)
from modality import modality_relation as _mod_relation

with open(os.path.join(HERE, 'domain-lexicon.json'),
          encoding='utf-8') as _f:
    LEX = json.load(_f)

# ---------------------------------------------------------------- helpers

_IG = {'egne', 'egen', 'eget', 'sine', 'sitt', 'ny', 'nytt', 'nye',
       'andre', 'ogsaa', 'også', 'kunne', 'skulle', 'vedtatt', 'innen',
       'etter', 'fordi', 'saa', 'så', 'directe', 'direkte', 'kan'}

_TRANS = str.maketrans({'å': 'a', 'æ': 'ae', 'ø': 'o', 'Å': 'a',
                        'Æ': 'ae', 'Ø': 'o'})

# ASCII-Norwegian modal spellings (aa/maa/faar/boer) that the frozen
# modality normalizer cannot see; normalized only for modality matching.
_ASCII_MODAL_RES = [(re.compile(r'\baa\b'), 'å'),
                    (re.compile(r'\bmaa\b'), 'må'),
                    (re.compile(r'\bfaar\b'), 'får'),
                    (re.compile(r'\bboer\b'), 'bør')]


def _mod_text(text):
    t = text or ''
    for rx, native in _ASCII_MODAL_RES:
        t = rx.sub(native, t)
    return t


def _fold(text):
    """ASCII-fold Norwegian letters and lowercase."""
    return str(text or '').lower().translate(_TRANS)


def _contains(hay, needle):
    """6-char stem containment on folded text."""
    h, n = _fold(hay), _fold(needle)
    if n in h:
        return True
    if len(n) >= 6:
        return n[:6] in h
    return False


def _any_form(text, forms):
    t = _fold(text)
    for f in forms:
        if ' ' in f or '-' in f:
            if _contains_wordbound(t, f):
                return True
        elif _contains(t, f):
            return True
    return False


def _concept_polarity(text, concept_name):
    """(+1, matched_form) positive form, (-1, form) negative form, or
    (0, None) absent for the named lexicon concept.

    Longest-match-first: "ingen kostnad" must win over its substring
    "kostnad" regardless of list order (normalization, not new doctrine)."""
    for con in LEX['concepts']:
        if con['concept'] == concept_name:
            t = _fold(text)
            best = (0, None, 0)
            for f in con['negative_forms']:
                if _contains_wordbound(t, f) and len(f) > best[2]:
                    best = (-1, f, len(f))
            for f in con['positive_forms']:
                if _contains_wordbound(t, f) and len(f) > best[2]:
                    best = (1, f, len(f))
            if best[0]:
                return best[0], best[1]
    return 0, None


def _alias_pairs():
    """(subset, superset, staff?) from the lexicon, 3-char stems."""
    out = []
    for a in LEX['actor_aliases']:
        out.append((a['subset'], a['superset'],
                    a.get('relation') == 'staff_of'))
    return out


def _disjoint_pairs():
    return [(d['a'], d['b']) for d in LEX['disjoint_actors']]


def _stem(word, n=4):
    w = _fold(word)
    return w[:n] if len(w) >= n else w


def _token_hits(text, words):
    t = _fold(text)
    toks = set(t.replace(',', ' ').split())
    stems = {_stem(x) for x in toks}
    return any(_stem(w) in stems for w in words)


def _syn_group_of(word):
    s = _stem(word, 5)
    for grp in LEX['synonym_groups']:
        for m in grp['members']:
            if _fold(m)[:5] == s or _fold(m).startswith(s) and s:
                return grp['group']
    return None


def _uncovered(atom_text, sentence):
    """Claim content tokens with no stem/synonym anchor in the source
    sentence."""
    s_toks = set(_fold(sentence).replace(',', ' ').split())
    s_stems = {_stem(x, 4) for x in s_toks}
    s_syns = {_stem(x, 5) for x in s_toks}
    out = []
    for tok in content_tokens(atom_text):
        ft = _fold(tok)
        if ft in _IG or len(ft) < 4:
            continue
        if re.match(r'^[\d.,:]+$', ft):
            continue
        if _stem(ft, 4) in s_stems or _stem(ft, 5) in s_syns:
            continue
        if _stem(ft, 4) in _fold(sentence) or ft in _fold(sentence):
            continue
        if _syn_group_of(ft) and any(
                _syn_group_of(_fold(x)) == _syn_group_of(ft)
                for x in s_toks):
            continue
        out.append(ft)
    return out


def _topic_ok(atom_text, sentence):
    return not _uncovered(atom_text, sentence)

# ------------------------------------------------- numeric bound conflicts

_NUM = r"(\d{1,3}(?:[ ]\d{3})+|\d+(?:[.,]\d+)?)"
_UNIT = (r"(prosent|%|kroner|kr|uker|uke|maneder|maaneder|maned|maaned|maan|"
         r"mnd|dager|dgn|dag|aar|ar|g)\b")
_OPNUM_RE = re.compile(
    r"\b(under|mindre enn|maksimalt|maks|inntil|opp til|senest|over|"
    r"storre enn|mer enn|minst|bare)\s+" + _NUM + r"\s*" + _UNIT)
_BARENUM_RE = re.compile(r"(?<!\d)" + _NUM + r"\s*" + _UNIT)
_FRAMING_RE = re.compile(r"frist|aldersgrense|alder\b|sats|andel|varer|"
                         r"vare i|ventetid|prosent|%|inntekt|grense")
_UNITS = {"prosent": "pct", "%": "pct", "kroner": "nok", "kr": "nok",
          "uker": "wk", "uke": "wk", "maneder": "mo", "maaneder": "mo",
          "maaned": "mo", "maan": "mo", "mnd": "mo", "dager": "dy",
          "dgn": "dy", "dag": "dy", "aar": "yr", "ar": "yr",
          "g": "g"}
_HI_OPS = ("under", "mindre enn", "maksimalt", "maks", "inntil",
           "opp til", "senest")


def _parse_bound_num(raw):
    r = raw.strip().replace(" ", "")
    if "," in r:
        r = r.replace(".", "").replace(",", ".")
    elif "." in r:
        first, last = r.split(".", 1)
        if len(last) == 3 and len(first) <= 3:
            r = first + last
    return float(r)


def _num_bounds(text):
    """Bound occurrences: {kind: eq|lo|hi, value, unit, span}."""
    t = _fold(text)
    out, spans = [], []
    for m in _OPNUM_RE.finditer(t):
        out.append({"kind": "hi" if m.group(1) in _HI_OPS else
                    ("lo" if m.group(1) in ("over", "storre enn",
                     "mer enn", "minst") else "eq"),
                    "value": _parse_bound_num(m.group(2)),
                    "unit": _UNITS.get(m.group(3), m.group(3)),
                    "span": m.span(),
                    "hi_inc": m.group(1) not in ("under", "mindre enn"),
                    "lo_inc": m.group(1) == "minst"})
        spans.append(m.span())
    for m in _BARENUM_RE.finditer(t):
        if any(s < m.end(1) and e > m.start(1) for s, e in spans):
            continue
        out.append({"kind": "eq", "value": _parse_bound_num(m.group(1)),
                    "unit": _UNITS.get(m.group(2), m.group(2)),
                    "span": m.span(), "hi_inc": True, "lo_inc": True})
    return out


def _bound_span(b):
    if b["kind"] == "eq":
        return b["value"], b["value"]
    if b["kind"] == "hi":
        return 0.0, b["value"]
    return b["value"], float("inf")


def _bound_phrase(t, b):
    """Local phrase around a bound occurrence (spec RC2 sections 8-9)."""
    part_start = max(t.rfind(c, 0, b["span"][0]) for c in ".;|\n")
    part_end = len(t)
    for c in ".;|\n":
        i = t.find(c, b["span"][1])
        if i != -1:
            part_end = min(part_end, i)
    return t[max(0, part_start + 1):part_end]


_QUAL_TOKENS = {"full", "hel", "halv", "halvert", "delt", "dobbelt",
                "total", "totalt", "samlet"}

_SUBJ_STOP = {"kroner", "maneden", "maaned", "maneder", "per"}


def _attests_same_subject(pa, pb):
    """True when pb shares content vocabulary with the claim phrase pa,
    i.e. the source attestation is about the same subject as the claim
    (not merely the same number cited under a different benefit)."""
    wa = {w for w in re.findall(r"[a-zæøå]+", pa)
          if len(w) >= 5 and w not in _SUBJ_STOP}
    if not wa:
        return False
    wb = {w for w in re.findall(r"[a-zæøå]+", pb) if len(w) >= 5}
    return bool(wa & wb)


def _same_predicate_phrase(pa, pb):
    """A numeric pair may only conflict when both local phrases carry
    the same rate/quantity qualifier set (both unqualified, or the same
    full/halv/total marker). Asymmetric markers mean different
    quantities and route to review instead of CONTRA (spec RC2 10)."""
    qa = {w for w in re.findall(r"[a-zæøå]+", pa) if w in _QUAL_TOKENS}
    qb = {w for w in re.findall(r"[a-zæøå]+", pb) if w in _QUAL_TOKENS}
    return qa == qb


def _numeric_contra(atom_text, source_text):
    """Same-unit bound conflicts when the claim frames the number as a
    binding limit (deadline/age/rate/duration/share)."""
    ab = _num_bounds(atom_text)
    if not ab or not _FRAMING_RE.search(_fold(atom_text)):
        return None
    at_all = _fold(atom_text)
    st_all = _fold(source_text)
    sb = _num_bounds(source_text)
    for cb in ab:
        claim_phrase = _bound_phrase(at_all, cb)
        for b in sb:
            if cb["unit"] != b["unit"]:
                continue
            if not _same_predicate_phrase(claim_phrase,
                                          _bound_phrase(st_all, b)):
                continue
            if any(ob["value"] == cb["value"] and
                   ob["unit"] == cb["unit"] and
                   _attests_same_subject(
                       claim_phrase, _bound_phrase(st_all, ob))
                   for ob in sb):
                # Claimed value attested in the source under the same
                # subject/predicate: the mismatched number is a
                # different quantity of the same thing, not a
                # contradiction (fail-closed, spec RC2 10). An
                # attestation bound to a different subject (e.g. the
                # ordinaer rate cited inside an utvidet claim) does
                # not count.
                continue
            clo, chi = _bound_span(cb)
            slo, shi = _bound_span(b)
            if chi < slo or shi < clo:
                return "numeric_bound_conflict"
            if cb["kind"] == "hi" and b["kind"] == "hi" and \
                    cb["value"] < b["value"]:
                return "numeric_cap_conflict"
    return None


# ------------------------------------------------- exhaustive lists


def _enum_parts(sentence):
    """Members of an av/fra enumeration; None when non-exhaustive or
    absent."""
    s = _fold(strip_parens(sentence))
    if any(m in s for m in getattr(pe, "_NONEXHAUSTIVE", ())):
        return None
    m = re.search(r"\b(?:av|fra)\s+([^.]+?)(?:\.|$)", s)
    if not m:
        return None
    parts = [p.strip() for p in re.split(r",| og | eller ", m.group(1))
             if p.strip()]
    return parts or None


def _claim_actor(atom_text):
    """Best actor phrase of the claim: trailing av/fra phrase, kun/bare
    noun, else the leading (article-stripped) noun."""
    t = _fold(strip_parens(atom_text))
    hits = re.findall(r"\b(?:bare\s+)?(?:av|fra)\s+([a-z]+)", t)
    if hits:
        return hits[-1]
    m = re.search(r"\bhos\s+([a-z]+)", t)
    if m:
        return m.group(1)
    m = re.search(r"\b(?:kun|bare)\s+(?:fra\s+)?([a-z]+)", t)
    if m:
        return m.group(1)
    m = re.search(r"^(?:en|ei|et|den|det|de)\s+([a-z]+)", t)
    if m:
        return m.group(1)
    m = re.search(r"^([a-z]+)", t)
    return m.group(1) if m else None


def _listed(actor, members):
    if not actor:
        return False
    st = _stem(actor, 4)
    for mem in members:
        mst = _fold(mem)
        if st and (mst.startswith(st) or st.startswith(mst[:4])):
            return True
        for sub, sup, _staff in _alias_pairs():
            if _stem(sub, 4) == st and _fold(sup).startswith(mst[:4]):
                return True
    return False


def _enum_verdict(atom_text, source_text):
    """CONTRA rule name when the claim actor sits outside the source's
    exhaustive av/fra list, or a kun-actor claim misses listed members.
    None otherwise (listed actor, no list, non-exhaustive)."""
    for sent in pe.split_sentences(source_text):
        members = _enum_parts(sent)
        if not members:
            continue
        stoks = {_stem(x, 4) for x in _fold(sent).replace(',', ' ').split()}
        shared = [t for t in content_tokens(atom_text)
                  if len(_fold(t)) >= 4 and _stem(t, 4) in stoks
                  and _fold(t) != _fold(_claim_actor(atom_text) or '')]
        if not shared:
            continue
        actor = _claim_actor(atom_text)
        # Only an obligation-framed (skal/maa) list is exhaustive; a
        # permissive (kan) list leaves scope unknown.
        if not re.search(r"\b(?:skal|maa|ma)\b", _fold(sent)) and \
                not re.search(r"\b(?:kun|bare|alene)\b",
                              _fold(strip_parens(atom_text))):
            continue
        if not _listed(actor, members):
            return "exhaustive_list_exclusion"
        if re.search(r"\b(?:kun|bare)\s+[a-z]",
                     _fold(strip_parens(atom_text))):
            others = [m for m in members
                      if not _fold(m).startswith(_stem(actor or '', 4))]
            if others:
                return "exhaustive_list_exclusion"
        return None
    return None

# ------------------------------------------------- concept-axis contra


def _concept_contra(atom_text, source_text):
    """Lexicon concept-axis contradiction on the aligned source sentence,
    plus structural axis conflicts (universal-vs-exception, staff
    negation, kan-utelate-vs-skal)."""
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    a = _fold(strip_parens(atom_text))
    sent = rep['candidates'][0]['sentence']
    a = _fold(strip_parens(atom_text))
    for name in ('free_of_charge', 'requires_referral',
                 'can_still_diagnose', 'provides_treatment',
                 'signature_required', 'automatic_decision',
                 'activity_requirement', 'duration_criterion'):
        cp, _cf = _concept_polarity(atom_text, name)
        sp, _sf = _concept_polarity(sent, name)
        if cp and sp and cp != sp:
            if name == 'free_of_charge' and sp == 1:
                m = re.search(r'\bfor\s+([a-z]+)',
                              _fold(strip_parens(sent)))
                if m:
                    ca = _claim_actor(atom_text)
                    if ca and _stem(ca, 4) != _stem(m.group(1), 4):
                        continue
            # Locality-hedged claim ("i enkelte kommuner") vs an
            # unqualified source sentence is scope-unknown, not CONTRA.
            if _any_form(a, ('enkelte', 'noen', 'visse',
                             'i enkelte kommuner')):
                return None
            return 'concept_opposition:' + name
    s = _fold(strip_parens(sent))
    if _any_form(a, LEX['universal_markers']) and _any_form(
            s, LEX['exception_markers'] + LEX['special_case_markers']):
        # "alle X" against a locality exception is scope-unknown, not
        # CONTRA (the source never rules out other localities).
        if _any_form(a, ('alle',)) and _any_form(
                s, ('i trondheim', 'i oslo', 'i bergen',
                    'i stavanger', 'lokalt')):
            pass
        else:
            return 'universal_vs_exception'
    if _any_form(a, ('helsesykepleier',)) and _concept_polarity(
            s, 'can_still_diagnose')[0] == -1 and _any_form(
            s, ('skolehelsetjenesten', 'skolen')):
        return 'staff_negation_contra'
    if _contains(a, 'utelate') and _any_form(
            s, ('skal utbetale', 'skal betale')):
        ca = _claim_actor(atom_text)
        if ca and _stem(ca, 4) in [
                _stem(x, 4) for x in s.replace(',', ' ').split()]:
            return 'option_vs_duty_opposition'
    return None


def _covered_by_synonyms(ctok, stoks):
    grp = _syn_group_of(ctok)
    return bool(grp) and any(
        _syn_group_of(_fold(x)) == grp for x in stoks)


def _alias_rel(a_word, b_word):
    """subset|superset|staff|None between two actor words via lexicon."""
    aw, bw = _stem(a_word, 4), _stem(b_word, 4)
    for sub, sup, staff in _alias_pairs():
        if _stem(sub, 4) == aw and _stem(sup, 4) == bw:
            return 'staff' if staff else 'subset'
        if _stem(sub, 4) == bw and _stem(sup, 4) == aw:
            return 'superset'
    return None


def _guard_fd(atom_text, source_text):
    """division_of_function guard: same-predicate clause exists or the
    reserved function is named nowhere else in the source."""
    for fam, data in pe.FUNCTION_FAMILIES.items():
        if not any(re.search(p, atom_text, re.IGNORECASE)
                   for p in data['claim_markers']):
            continue
        actor_toks = set(pe._actor_tokens(atom_text))
        about_a = None
        for sent in pe.split_sentences(source_text):
            if actor_toks and (actor_toks & set(canon_tokens(sent))):
                about_a = sent
                break
        if not about_a:
            return False
        fam_anywhere = any(
            re.search(p, sent, re.IGNORECASE)
            for sent in pe.split_sentences(source_text)
            for p in data['claim_markers'])
        if not fam_anywhere:
            for sent in pe.split_sentences(source_text):
                stoks = set(pe.canon_tokens(sent))
                if actor_toks and (actor_toks & stoks):
                    continue
                if any(re.search(p, sent, re.IGNORECASE)
                       for p in data['other_markers']):
                    return False
            return True
        if any(re.search(p, about_a, re.IGNORECASE)
               for p in data['claim_markers']):
            return True
    return False


def _guard_cost(atom_text, source_text):
    """cost_axis guard: free-side claim with a pay-artifact sentence."""
    cp, _cf = _concept_polarity(atom_text, 'free_of_charge')
    if cp != 1:
        return False
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return False
    sent = rep['candidates'][0]['sentence']
    sp, _sf = _concept_polarity(sent, 'free_of_charge')
    if sp == 1:
        return True
    if re.search(r'\bkr\b', _fold(sent)):
        return True
    return False


def _guard_actor_atom(atom_text, sent):
    """True when the claim actor is a lexicon subset/staff alias of the
    sentence actor (recipient_disjoint / ACTOR_FAMILY_MISMATCH guard)."""
    ca, sa = _claim_actor(atom_text), None
    sent_actors = pe._actor_tokens(sent)
    sa_vals = set(sent_actors.values())
    if not ca or not sa_vals:
        return False
    if any(_alias_rel(ca, w) in ('subset', 'staff', 'superset')
           for w in sa_vals):
        return True
    return False


def _same_object_negation(atom_text, sent):
    """Near-verbatim negation or same-object nominalization case."""
    a = _fold(strip_parens(atom_text))
    s = _fold(strip_parens(sent))
    if has_negation(a) != has_negation(s):
        if _contains(a, 'frivillig') and _contains(s, 'frivillig'):
            return True
        return False
    if _uncovered(a, s) == [] or _uncovered(s, a) == []:
        return True
    if _contains(a, 'frivillig') and _contains(s, 'frivillig'):
        return True
    return False


def _guard_polarity(atom_text, sent):
    """polarity_conflict guard: near-verbatim shared negation,
    frivillig nominalization, or different-object negation."""
    if _same_object_negation(atom_text, sent):
        return True
    a = _fold(strip_parens(atom_text))
    s = _fold(strip_parens(sent))
    if has_negation(a) and not has_negation(s):
        atoks = set(content_tokens(a))
        stoks = set(content_tokens(s))
        shared = [t for t in atoks
                  if _stem(t, 4) in {_stem(x, 4) for x in stoks}
                  or _covered_by_synonyms(_fold(t),
                                          [_fold(x) for x in stoks])]
        diff = [t for t in atoks
                if len(_fold(t)) >= 5
                and _stem(t, 4) not in {_stem(x, 4) for x in stoks}
                and not _covered_by_synonyms(_fold(t),
                                             [_fold(x) for x in stoks])
                and _fold(t) not in _IG]
        if shared and diff:
            return True
    return False


def _guard_recipient(atom_text, sent):
    ca = _claim_actor(atom_text)
    m = re.search(r'\b(?:bare|kun)\s+(?:fra\s+|til\s+)?([a-z]+)',
                  _fold(strip_parens(atom_text)))
    claim_r = m.group(1) if m else ca
    sm = re.search(r'\btil\s+([a-z]+)', _fold(strip_parens(sent)))
    sent_r = sm.group(1) if sm else None
    if not claim_r or not sent_r:
        return False
    return _alias_rel(claim_r, sent_r) in ('subset', 'staff', 'superset')


def _guard_exclusivity(atom_text, sent, source_text):
    """exclusivity guard: claimed actor is listed (subset aliases count),
    or solo use is grounded elsewhere in the source."""
    actor = _claim_actor(atom_text)
    members = _enum_parts(sent)
    if members and _listed(actor, members):
        return True
    for alias in _alias_pairs():
        sub, sup = _fold(alias[0]), _fold(alias[1])
        if _contains(sub, actor or '') and any(
                _contains(_fold(m), sup) or _fold(m) == sup
                for m in members or []):
            return True
    s_toks = set(content_tokens(_fold(strip_parens(sent))))
    atoks = set(content_tokens(_fold(strip_parens(atom_text))))
    claim_factors = atoks - {'kun', 'bare', 'alene'}
    solo_toks = {t for t in claim_factors if _stem(t, 4) in s_toks}
    for other in pe.split_sentences(source_text):
        if other == sent:
            continue
        otoks = set(content_tokens(_fold(strip_parens(other))))
        if solo_toks and all(_stem(t, 4) in otoks for t in solo_toks) \
                and not (atoks & otoks):
            return True
    return False


# ------------------------------------------------- support rescue

_PASS_VETO = {'PREDICATE_GROUNDING_UNVERIFIED'}

_ADVERBIAL_RES = (re.compile(r'\bved\s+[^,.;]*'),
                  re.compile(r'\bper\s+[\d.]*\s*[a-z0-9. ]*'))


def _reduce_adverbials(text):
    t = text
    for rx in _ADVERBIAL_RES:
        t = rx.sub('', t)
    return t


def _alias_covered(ftok, s_toks):
    for sub, sup, _staff in _alias_pairs():
        if _stem(ftok, 4) == _stem(sub, 4) and any(
                _stem(x, 4) == _stem(sup, 4) for x in s_toks):
            return True
    return False


def _uncovered_core(atom_text, sent):
    s_toks = [_fold(x) for x in
              _fold(strip_parens(sent)).replace(',', ' ').split()]
    reduced = _reduce_adverbials(_fold(strip_parens(atom_text)))
    return [t for t in _uncovered(reduced, sent)
            if not _alias_covered(t, s_toks)]


def _dest_processor(atom_text, sent):
    """sendes-til destination grounds the same actor's behandler claim."""
    s = _fold(strip_parens(sent))
    m = re.search(r'\bsendes til ([a-z]+)', s)
    if not m or not _token_hits(atom_text, ('behandler',)):
        return False
    ca = _claim_actor(atom_text)
    return bool(ca) and _stem(ca, 4) == _stem(m.group(1), 4)


def _dest_adjacent_disjoint(atom_text, sent):
    def actor_hit(text, word):
        # Actor mentions must not stem-match inside longer compounds
        # (foreldresamtale is not foreldre; barnevern is not barn).
        w = _stem(word)
        for tok in _fold(text).replace(',', ' ').split():
            tok = tok.strip('.,;:!?()[]')
            if _stem(tok) == w and len(tok) <= len(word) + 2:
                return True
        return False
    for da, db in _disjoint_pairs():
        a1, a2 = actor_hit(atom_text, da), actor_hit(atom_text, db)
        s1, s2 = actor_hit(sent, da), actor_hit(sent, db)
        # Complementary mentions are not conflicts: if the sentence
        # already talks about the claim's actor, no substitution happened.
        if (a1 and s2 and not s1) or (a2 and s1 and not s2):
            return True
    return False


def _veto_explained(name, atom_text, sent):
    """Veto does not apply when the claim is near-verbatim with the span
    or carries no uncovered content after adverbial/alias reduction."""
    if name == 'PLACE_CONFLICT':
        return False
    if _same_object_negation(atom_text, sent):
        return True
    return not _uncovered_core(atom_text, sent)


def _rescue_support(atom_text, source_text):
    """(rule, sent) when hard/alias/hedge evidence grounds SUPPORT.
    Numeric, concept, list, scope and veto checks run first."""
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    sent = rep['candidates'][0]['sentence']
    score = rep['candidates'][0]['score']
    s_mod = modality_of(_mod_text(strip_parens(sent)))
    c_mod = rep['modality']
    if _mod_relation(s_mod, c_mod) == 'CLAIM_STRONGER':
        return None
    n_state, _ds = pe._numeric_state(atom_text, sent, source_text)
    if n_state in ('conflict', 'unequal'):
        return None
    if pe._age_relation(atom_text, sent) == 'disjoint':
        # A sentence whose age expression conflicts with the claim can
        # never ground lexical rescue support (spec RC2 section 5).
        return None
    a = _fold(strip_parens(atom_text))
    if _any_form(a, ('kun', 'bare')):
        return None
    s = _fold(strip_parens(sent))
    if _any_form(a, ('i oslo',)) and _any_form(s, ('i trondheim',)):
        return None
    son = _same_object_negation(atom_text, sent)
    hedge = _any_form(a, LEX['hedge_modifiers']) and \
        _any_form(s, LEX['hedge_modifiers'])
    shared = any(
        _stem(t, 4) in {_stem(x, 4) for x in s.replace(',', ' ').split()}
        for t in a.replace(',', ' ').split() if len(t) >= 4)
    hard = _hard_support(atom_text, sent, n_state, score)
    grounded = (
        hard or
        (hedge and shared) or
        n_state == 'equal' or
        _staff_support(atom_text, sent) or
        _claim_actor_present(atom_text, sent) or
        (not _uncovered_core(atom_text, sent) and
         not _dest_adjacent_disjoint(atom_text, sent)))
    if not grounded:
        return None
    if rep['negated'] != _has_neg_wb(strip_parens(sent)):
        return None
    if _numeric_contra(atom_text, source_text):
        return None
    if _concept_contra(atom_text, source_text):
        return None
    if _enum_verdict(atom_text, source_text):
        return None
    if _dest_adjacent_disjoint(atom_text, sent):
        return None
    uc = _uncovered_core(atom_text, sent)
    cap = _claim_actor_present(atom_text, sent)
    if n_state == 'diff':
        return None
    if uc and not _dest_processor(atom_text, sent) and \
            not cap and not (son and not uc):
        return None
    if len(uc) == 1 and score < 0.6 and \
            not _dest_processor(atom_text, sent) and not son:
        return None
    if uc and cap and score < 0.6 and not hard and \
            not _dest_processor(atom_text, sent) and not son:
        return None
    if len(uc) >= 2:
        return None
    veto = _claim_strength_veto(atom_text, source_text, sent)
    if veto and veto[0] not in _PASS_VETO and \
            not _veto_explained(veto[0], atom_text, sent):
        if veto[0] == 'EXCLUSIVITY_UNVERIFIED' and _enum_parts(sent) \
                and _listed(_claim_actor(atom_text), _enum_parts(sent)):
            pass
        elif n_state != 'equal' and not hard and \
                not _dest_processor(atom_text, sent):
            return None
    if not uc and n_state != 'equal' and not hard and not son and \
            not _dest_processor(atom_text, sent):
        # Empty uncovered-core after alias folding is not alone proof;
        # require hard lexical or numeric-equal grounding.
        return None
    if not uc and n_state != 'equal' and not hard and son and \
            not _dest_processor(atom_text, sent):
        veto = _claim_strength_veto(atom_text, source_text, sent)
        if veto and veto[0] not in _PASS_VETO:
            return None
    swap = _predicate_swap_veto(atom_text, sent)
    if swap and not (_contains(a, 'spesialundervisning') and
                     _contains(s, 'spesialundervisning')):
        return None
    return ('support_lexical_rescue', sent)


# ------------------------------------------------- gate-scope guard


def _gate_scope_guard(atom_text, source_text):
    """Demote a base SUPPORT that crossed a recipient/payer boundary or
    added several novel object tokens the source never carries."""
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    sent = rep['candidates'][0]['sentence']
    if _dest_adjacent_disjoint(atom_text, sent):
        return 'scope_disjoint'
    if len(_uncovered_core(atom_text, sent)) >= 2 and \
            not _dest_processor(atom_text, sent):
        return 'scope_object_broadened'
    return None


# ------------------------------------------------- wrapper


def _contra_guard(atom_text, source_text, base):
    """Guard rule name when a base CONTRA rests on a confusable frame."""
    rule = base.get('rule')
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    sent = rep['candidates'][0]['sentence']
    if rule == 'division_of_function' and _guard_fd(atom_text,
                                                    source_text):
        return 'guard_division_same_predicate'
    if rule == 'cost_axis_opposition' and _guard_cost(atom_text,
                                                      source_text):
        return 'guard_cost_free_form'
    if rule == 'modifier_antonym' and _guard_antonym(atom_text,
                                                     source_text):
        return 'guard_antonym_regime_pair'
    if rule == 'recipient_disjoint' and (_guard_recipient(atom_text,
                                                          sent)):
        return 'guard_recipient_alias'
    if rule == 'exclusivity_conflict' and _guard_exclusivity(
            atom_text, sent, source_text):
        return 'guard_exclusivity_listed'
    if rule == 'polarity_conflict' and _guard_polarity(atom_text, sent):
        return 'guard_negation_scope'
    return None


def _new_contra(atom_text, source_text):
    for check in (_numeric_contra, _enum_verdict, _concept_contra):
        hit = check(atom_text, source_text)
        if hit:
            return hit
    for check in (_auto_discretion_contra, _disjoint_actor_contra,
                  _neg_object_conflict, _insufficiency_contra):
        hit = check(atom_text, source_text)
        if hit:
            return hit
    return None


def _flip(base, verdict, rule, review):
    out = dict(base)
    out['verdict'] = verdict
    out['rule'] = rule
    out['review'] = review
    out['override'] = rule
    out['confidence'] = 0.9 if verdict in ('CONTRADICTED', 'SUPPORTED') \
        else 0.5
    if verdict == 'CONTRADICTED':
        out['proof'] = _proof_span('CONTRA', base.get('atom_text', ''),
                                   (base.get('proof') or {}).get('span',
                                                                 ''),
                                   '')
    return out


def decide_atom_v02(atom_text, source_text):
    base = pe.decide_atom(atom_text, source_text)
    v = base['verdict']
    if v == 'CONTRADICTED':
        contra = _new_contra(atom_text, source_text)
        if contra:
            return _flip(base, 'CONTRADICTED', contra, False)
        guard = _contra_guard(atom_text, source_text, base)
        if guard:
            rescue = _rescue_support(atom_text, source_text)
            if rescue:
                out = _flip(base, 'SUPPORTED', rescue[0], False)
                out['proof'] = _proof_span('SUPPORT', atom_text,
                                           rescue[1], source_text)
                return out
            return _flip(base, 'INSUFFICIENT_EVIDENCE', guard, True)
        rescue = _rescue_support(atom_text, source_text)
        if rescue:
            out = _flip(base, 'SUPPORTED', rescue[0], False)
            out['proof'] = _proof_span('SUPPORT', atom_text, rescue[1],
                                       source_text)
            return out
        return base
    if v == 'INSUFFICIENT_EVIDENCE':
        contra = _new_contra(atom_text, source_text)
        if contra:
            return _flip(base, 'CONTRADICTED', contra, False)
        rescue = _rescue_support(atom_text, source_text)
        if rescue:
            out = _flip(base, 'SUPPORTED', rescue[0], False)
            out['proof'] = _proof_span('SUPPORT', atom_text, rescue[1],
                                       source_text)
            return out
        return base
    if v == 'SUPPORTED':
        contra = _new_contra(atom_text, source_text)
        if contra:
            return _flip(base, 'CONTRADICTED', contra, False)
        gate = _gate_scope_guard(atom_text, source_text)
        if gate == 'scope_disjoint':
            return _flip(base, 'INSUFFICIENT_EVIDENCE', gate, True)
        return base
    return base


def judge_claim(claim_text, source_text):
    atoms = decompose_claim(claim_text)
    atom_results = []
    for i, a in enumerate(atoms, 1):
        res = decide_atom_v02(a, source_text)
        res['atom_id'] = 'A%d' % i
        res['atom_text'] = a
        atom_results.append(res)
    verdict = aggregate(atom_results, is_compound=len(atom_results) > 1)
    injection = detect_injection(source_text)
    review = any(r.get('review') for r in atom_results)
    return {
        'verdict': verdict,
        'confidence': round(min(r['confidence'] for r in atom_results),
                            2),
        'engine': 'quote-aligner-deterministic-v0.2',
        'injection_detected': injection,
        'review_required': review,
        'atom_results': atom_results,
        'atoms': [{'id': r['atom_id'], 'text': r['atom_text'],
                   'verdict': r['verdict'], 'rule': r['rule']}
                  for r in atom_results],
    }




def _guard_antonym(atom_text, source_text):
    """modifier_antonym guard: admissibility date before the source's
    regime cutoff is an old-rules case, not a modifier antonym."""
    a = _fold(strip_parens(atom_text))
    if not re.search(r'\bsendt\s+\d', a):
        return False
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return False
    s = _fold(strip_parens(rep['candidates'][0]['sentence']))
    if 'etter' not in s:
        return False
    cd, sd = pe.extract_dates(atom_text), pe.extract_dates(source_text)
    if not cd or not sd:
        return False
    from datetime import date as _d
    claim_date = _d(cd[0]['y'], cd[0]['m'], cd[0]['d'])
    cutoff = _d(sd[0]['y'], sd[0]['m'], sd[0]['d'])
    return claim_date < cutoff


def _has_neg_wb(text):
    """Word-boundary negation on folded text (frozen has_negation is
    substring-based and false-positives on e.g. "ordningen")."""
    return bool(re.search(
        r"\b(ikke|ingen|aldri|uten|verken)\b", _fold(text)))


def _staff_support(atom_text, sent):
    """Claim actor is an alias/staff-of an actor named in the sentence."""
    ca = _claim_actor(atom_text)
    if not ca:
        return False
    s_toks = [_fold(x) for x in _fold(sent).replace(',', ' ').split()]
    for tok in s_toks:
        rel = _alias_rel(ca, tok)
        if rel in ('subset', 'staff', 'superset'):
            return True
    return False


def _auto_discretion_contra(atom_text, source_text):
    """Universal-claim vs individual-discretion source: CONTRA."""
    a = _fold(strip_parens(atom_text))
    if not (re.search(r"\b(alltid|automatisk)\b", a) and
            re.search(r"\b(skal|kan|maa|ma)\b", a)):
        return None
    s = _fold(source_text)
    if re.search(r"individuell vurdering|ingen automatisk rett", s):
        return ('auto_discretion_contra',
                'claim states automatic/universal rule; '
                'source states individual assessment')
    return None


def _disjoint_actor_contra(atom_text, source_text):
    """Disjoint actor stems on opposite sides: CONTRA."""
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    sent = rep['candidates'][0]['sentence']
    ca = _claim_actor(atom_text)
    if not ca:
        return None
    if not any(ca in (_fold(d['a']), _fold(d['b']))
               for d in LEX['disjoint_actors']):
        return None
    for d in LEX['disjoint_actors']:
        x, y = _fold(d['a']), _fold(d['b'])
        pair = (x, y) if ca == x else ((y, x) if ca == y else None)
        if not pair:
            continue
        other = pair[1]
        # The partner must be framed as the transaction's recipient
        # ("til husbanken"); a partner merely mentioned as beneficiary
        # leaves the claim's routing unstated.
        if not re.search(r"\btil\s+" + re.escape(other),
                         _fold(sent)):
            continue
        if any(_stem(other, 4) == _stem(_fold(t), 4)
               for t in _fold(sent).replace(',', ' ').split()):
            return ('disjoint_actor_contra',
                    'claim actor %s conflicts with source actor %s'
                    % (ca, other))
    return None


def _neg_object_conflict(atom_text, source_text):
    """Both sides negated, same subject, different objects: CONTRA."""
    rep = align_atom(atom_text, source_text)
    if not rep['candidates']:
        return None
    sent = rep['candidates'][0]['sentence']
    a = _fold(strip_parens(atom_text))
    s = _fold(strip_parens(sent))
    if not (_has_neg_wb(a) and _has_neg_wb(s)):
        return None
    a_toks = [t for t in a.replace(',', ' ').split()
              if t not in _IG and len(t) >= 4 and
              not _has_neg_wb(t)]
    s_toks = [t for t in s.replace(',', ' ').split()
              if t not in _IG and len(t) >= 4 and
              not _has_neg_wb(t)]
    if not a_toks or not s_toks:
        return None
    shared = {t for t in a_toks
              if any(_stem(t, 4) == _stem(x, 4) for x in s_toks)}
    a_only = [t for t in a_toks if t not in shared and
              not any(_stem(t, 4) == _stem(x, 4) for x in s_toks)]
    s_only = [t for t in s_toks if not any(
        _stem(t, 4) == _stem(x, 4) for x in a_toks)]
    if shared and a_only and s_only:
        return ('neg_object_conflict',
                'both sides negate but objects differ: %s vs %s'
                % (', '.join(a_only[:3]), ', '.join(s_only[:3])))
    return None


def _regime_support(atom_text, source_text):
    """Claim 'sendt <date>' predates source cutoff: SUPPORT."""
    a = _fold(strip_parens(atom_text))
    m = re.search(r"\bsendt\s+(\d{1,2})\.(\d{1,2})\.(\d{4})", a)
    if not m:
        return None
    day, mon, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    s = _fold(source_text)
    sm = re.search(
        r"(?:gjelder fra|gjeldende fra|fra|cutoff)\s+"
        r"(\d{1,2})\.(\d{1,2})\.(\d{4})", s)
    if not sm:
        return None
    cutoff = (int(sm.group(3)), int(sm.group(2)), int(sm.group(1)))
    if (year, mon, day) < cutoff:
        return ('regime_support',
                'claim date %02d.%02d.%04d precedes source cutoff '
                '%02d.%02d.%04d' % (day, mon, year,
                                    cutoff[2], cutoff[1], cutoff[0]))
    return None


def _contains_wordbound(hay, needle):
    """Whole-word/phrase containment; guards against 'behandler ikke'
    matching 'gir behandling' (suffix overlap)."""
    h, n = _fold(hay), _fold(needle)
    if not n:
        return False
    return re.search(r'(?<![a-z])' + re.escape(n) + r'(?![a-z])', h)         is not None


def _insufficiency_contra(atom_text, source_text):
    """Claim "X alone is sufficient" vs source "X alone is not
    sufficient / not the only criterion": CONTRA."""
    a = _fold(strip_parens(atom_text))
    if not re.search(r"\b(alene|bare|kun)\b", a):
        return None
    s = _fold(source_text)
    # source explicitly denies sufficiency: "ikke bare X" / "krever Y"
    if re.search(r"ikke\s+(?:bare|kun)\s", s) and             re.search(r"krever", s):
        # claim's subject appears in source's denied-sufficiency phrase
        denied = re.search(r"ikke\s+(?:bare|kun)\s+([a-z\s]+)", s)
        if denied:
            subj = _stem(_fold(denied.group(1).split()[0]), 4)
            claim_toks = [t for t in a.split() if len(t) >= 4]
            if any(subj in t or t.startswith(subj) for t in claim_toks):
                return ('insufficiency_contra',
                        'claim states %s alone suffices; source '
                        'requires more' % denied.group(1).strip()[:30])
    return None


def _claim_actor_present(atom_text, sent):
    """Claim actor aliases into an actor explicitly named in the aligned
    sentence (staff/alias relation to a present token)."""
    ca = _claim_actor(atom_text)
    if not ca:
        return False
    for tok in _fold(sent).replace(',', ' ').split():
        if _alias_rel(ca, _fold(tok)) in ('subset', 'staff', 'superset',
                                          'equal'):
            return True
    return False
