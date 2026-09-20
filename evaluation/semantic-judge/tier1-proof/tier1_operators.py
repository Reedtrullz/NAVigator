# Tier-1 SAFE_FOR_AUTO_PROOF operators (spec sections 11-20).
# Deterministic wrappers over frozen polarity_engine_v02 helpers.
# Preconditions are conjunctive (spec 12): unknown -> abstain (None).
# No case IDs, no model calls, no chaining beyond one bounded proof.
# Fail-closed: callers treat any exception as REVIEW_REQUIRED (spec 15).
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.join(os.path.dirname(HERE), "quote-aligner")
V02 = os.path.join(QA, "v0.2")
sys.path.insert(0, QA)
sys.path.insert(0, V02)

import polarity_engine as pe  # frozen
import polarity_engine_v02 as v02  # frozen

_NEG_RE = re.compile(r"\b(ikke|ingen|aldri|uten|verken|umulig)\b")
_HEDGES = ("normalt", "vanligvis", "vanlig", "normal", "som hovedregel", "ofte")
_UNIVERSAL = ("alle", "alltid", "samtlige", "hver", "enhver")
_DISCRETION = ("individuell vurdering", "skjonn", "skjonnsmessig")
_ARITH_RE = re.compile(r"\b(til sammen|tilsammen|totalt|samlet|i alt|sum)\b")
_DUMMY_RE = re.compile(r"^\s*(det|den)\s+(er|finnes|var|blir)\b")
_EXCL_RE = re.compile(r"\b(ingen|ikke)\b")
_DIR_RE = re.compile(r"\b(over|under)\b")
_THRESH_RE = re.compile(r"\b(etter|foer|innen|senest|inntil|fra og med|fom|fra)\b")
_LOC_RE = re.compile(r"\b(?:i|pa|hele)\s+([a-z]+)")
_DATE_VALUE_RE = re.compile(r"\b(frist|fristen|dato|datoen|utloper|utgaar|startdato|sluttdato|gjelder fra|gjelder til)\b")


def _exclusion_flag(text):
    # "ingen/ikke ... over/under X" asserts the policy cutoff itself.
    f = v02._fold(text)
    return bool(_EXCL_RE.search(f) and _DIR_RE.search(f))


def _conflicting_pair(cbounds, sbounds, claim_excl, sent_excl):
    """First conflicting same-unit bound pair, or None.

    Span-disjoint bounds always conflict. Exclusion thresholds ("ingen
    stonad ved inntekt over X") also conflict when the same bound kind
    and unit carries different values: the cutoff itself is the
    asserted fact, not a value magnitude."""
    for cb in cbounds:
        for sb in sbounds:
            if cb["unit"] != sb["unit"]:
                continue
            clo, chi = v02._bound_span(cb)
            slo, shi = v02._bound_span(sb)
            if chi < slo or shi < clo:
                return cb, sb, "span"
            if (claim_excl and sent_excl and cb["kind"] == sb["kind"]
                    and cb["kind"] in ("lo", "hi")
                    and cb["value"] != sb["value"]):
                return cb, sb, "threshold"
    return None
_QUALIFIER_RE = re.compile(r"\bikke\b[^.]{0,60}?\b(omfattes|omfattet|gjelder|dekkes|inkludert|regnes)\b")


def _proof(operator, premises, sent, claim, result, detail):
    return {"operator": operator, "premises": list(premises),
            "derived_fact": sent.strip()[:160],
            "claim_atom": claim.strip()[:160], "result": result,
            "detail": detail}


def _sentences(source_text):
    sents = [s for s in pe.split_sentences(source_text or "") if s and s.strip()]
    return sents or [source_text or ""]


def _actor_rel(claim_actor, word):
    # equal | subset | staff | superset | None via the frozen lexicon.
    # Generic equality needs full-fold or 6-char stem agreement; 4-char
    # stems collide on distinct nouns (henvendelse/henvisning).
    cf, wf = v02._fold(claim_actor), v02._fold(word)
    if cf == wf:
        return "equal"
    if len(cf) >= 5 and len(wf) >= 5 and v02._stem(cf, 6) == v02._stem(wf, 6):
        return "equal"
    ca, wa = v02._stem(cf, 4), v02._stem(wf, 4)
    for sub, sup, staff in v02._alias_pairs():
        if ca == v02._stem(sub, 4) and wa == v02._stem(sup, 4):
            return "staff" if staff else "subset"
        if wa == v02._stem(sub, 4) and ca == v02._stem(sup, 4):
            return "superset"
    return None


def _disjoint(a, b):
    sa, sb = v02._stem(a, 4), v02._stem(v02._fold(b), 4)
    for pair in v02._disjoint_pairs():
        stems = {v02._stem(x, 4) for x in pair}
        if sa in stems and sb in stems:
            return True
    return False


def _same_subject(claim, sentence, contra=False):
    # (claim_actor, relation) when the subject axis is established.
    # Directional rule (N-R1 doctrine): contradiction binds only on equal
    # or non-staff subset relations; support may use any documented relation.
    ca = v02._claim_actor(claim)
    if not ca:
        return None
    best = None
    for tok in v02._fold(sentence).replace(",", " ").split():
        rel = _actor_rel(ca, tok)
        if rel == "equal":
            return ca, "equal"
        if rel in ("subset", "staff", "superset") and best is None:
            best = rel
    if best and (not contra or best in ("equal", "subset")):
        return ca, best
    return None


def _hits(text, words):
    return any(v02._contains_wordbound(text, w) for w in words)


def _locale_conflict(claim, sentence):
    cl = [m.group(1) for m in _LOC_RE.finditer(v02._fold(claim))]
    sl = [m.group(1) for m in _LOC_RE.finditer(v02._fold(sentence))]
    for a in cl:
        for b in sl:
            if v02._stem(a, 5) != v02._stem(b, 5):
                return True
    return False


def _scope_conflict(claim, sentence):
    c, s = v02._fold(claim), v02._fold(sentence)
    ch, sh = _hits(c, _HEDGES), _hits(s, _HEDGES)
    cu, su = _hits(c, _UNIVERSAL), _hits(s, _UNIVERSAL)
    cd, sd = _hits(c, _DISCRETION), _hits(s, _DISCRETION)
    if cu and not su and not ch:
        return True
    if ch and su:
        return True
    if cd and su:
        return True
    if cd and not sd and ch and not sh:
        return True
    return _locale_conflict(claim, sentence)


def _time_compatible(claim, sentence):
    # Strict: unknown time axis (one side dated, other not) abstains.
    cd, sd = pe.extract_dates(claim), pe.extract_dates(sentence)
    if not cd and not sd:
        return True
    if cd and sd:
        return (cd[0]["y"], cd[0]["m"], cd[0]["d"]) == (
            sd[0]["y"], sd[0]["m"], sd[0]["d"])
    return False


def _has_hedge(sentence):
    return _hits(v02._fold(sentence), _HEDGES)


def _has_exception(text):
    return _hits(v02._fold(text), v02.LEX.get("exception_markers", []))


def _shared_content(claim, sentence):
    # At least one content-stem or synonym-group overlap (temporal guard).
    stop = {"gjeldende", "gir", "har", "er", "var", "blir"}

    def stems_groups(text):
        st, gr = set(), set()
        for t in v02._fold(text).split():
            if len(t) >= 5 and not t[0].isdigit() and t not in stop:
                st.add(v02._stem(t, 5))
                g = v02._syn_group_of(t)
                if g:
                    gr.add(g)
        return st, gr

    cs, cg = stems_groups(claim)
    ss, sg = stems_groups(sentence)
    return bool((cs & ss) or (cg & sg))


def _qualifier_guard(claim, sent):
    # Negated relative clause scopes the whole sentence; an
    # unqualified claim cannot inherit its assertion (EN-SCOPE).
    return any(_QUALIFIER_RE.search(v02._fold(t)) for t in (claim, sent))

def direct_assertion(claim, source_text):
    # Every concept the claim asserts is asserted (equal polarity) in
    # subject/scope/time-compatible premise sentences (multi-span allowed).
    # A fragment sentence with no own actor (e.g. "Gratis, ingen
    # henvisning.") inherits the subject of the adjacent bound sentence
    # it follows (generic fragment propagation, support-only).
    cands = []
    bound = set()
    for i, sent in enumerate(_sentences(source_text), 1):
        if not _time_compatible(claim, sent) or _scope_conflict(claim, sent):
            continue
        if _qualifier_guard(claim, sent):
            continue
        subj = _same_subject(claim, sent, contra=False)
        if subj:
            if any(_disjoint(subj[0], t)
                   for t in v02._fold(sent).replace(",", " ").split()):
                continue
            bound.add(i)
            cands.append((i, sent))
        elif i - 1 in bound and not _sentence_has_own_actor(sent):
            ca = v02._claim_actor(claim)
            if not (ca and any(_disjoint(ca, t)
                    for t in v02._fold(sent).replace(",", " ").split())):
                bound.add(i)
                cands.append((i, sent))
    if not cands:
        return None
    matched, forms, premises = 0, [], []
    for con in v02.LEX["concepts"]:
        cp, cf = v02._concept_polarity(claim, con["concept"])
        if cp == 0:
            continue
        hit = None
        for i, sent in cands:
            sp, sf = v02._concept_polarity(sent, con["concept"])
            if sp == cp:
                hit = (i, sf)
                break
        if hit is None:
            return None
        i, sf = hit
        if i not in premises:
            premises.append(i)
        matched += 1
        forms.append({"concept": con["concept"], "claim_form": cf,
                      "source_form": sf})
    if not matched:
        return None
    premises.sort()
    fact = " ".join(_sentences(source_text)[i - 1].strip()
                    for i in premises)[:160]
    return _proof("DIRECT_ASSERTION", ["S%d" % i for i in premises], fact,
                  claim, "SUPPORTED",
                  {"concepts": forms, "n_concepts": matched})


def _sentence_has_own_actor(sent):
    # A sentence with an explicit known actor sets its own subject and
    # must not inherit a fragment context.
    toks = {v02._fold(x) for x in v02._fold(sent).replace(",", " ").split()}
    for members in pe.ACTOR_FAMILIES.values():
        if toks & {v02._fold(m) for m in members}:
            return True
    return False


def explicit_negation(claim, source_text):
    # Every claim concept is addressed across premise sentences and at
    # least one is polarity-opposite with an explicit, in-scope negation.
    # Exception anywhere in source -> abstain (cross-clause scope risk).
    if _has_exception(source_text):
        return None
    cands = []
    for i, sent in enumerate(_sentences(source_text), 1):
        if not _time_compatible(claim, sent) or _scope_conflict(claim, sent):
            continue
        if _has_hedge(sent):
            continue
        if _qualifier_guard(claim, sent):
            continue
        subj = _same_subject(claim, sent, contra=True)
        if not subj:
            continue
        cands.append((i, sent))
    if not cands:
        return None
    present, opposite, forms = 0, 0, []
    for con in v02.LEX["concepts"]:
        cp, cf = v02._concept_polarity(claim, con["concept"])
        if cp == 0:
            continue
        hit = None
        for i, sent in cands:
            sp, sf = v02._concept_polarity(sent, con["concept"])
            if sp != 0:
                hit = (i, sp, sf)
                break
        if hit is None:
            return None
        i, sp, sf = hit
        forms.append({"concept": con["concept"], "claim_form": cf,
                      "source_form": sf, "claim_pol": cp, "source_pol": sp,
                      "premise": i})
        present += 1
        if sp != cp:
            opposite += 1
    if present == 0 or opposite == 0:
        return None
    scoped = True
    for f in forms:
        if f["claim_pol"] == f["source_pol"]:
            continue
        neg_side = None
        if _NEG_RE.search(v02._fold(f["source_form"])):
            neg_side = "source"
        elif _NEG_RE.search(v02._fold(f["claim_form"])):
            neg_side = "claim"
        if neg_side == "source":
            continue
        text = (claim if neg_side == "claim"
                else _sentences(source_text)[f["premise"] - 1])
        form = f["claim_form"] if neg_side == "claim" else f["source_form"]
        folded = v02._fold(text)
        form_fold = v02._fold(form)
        fi = folded.find(form_fold)
        if fi < 0:
            scoped = False
            break
        window = folded[max(0, fi - 25):fi + len(form_fold) + 15]
        if not _NEG_RE.search(window):
            scoped = False
            break
    if not scoped:
        return None
    result = ("CONTRADICTED" if any(f["claim_pol"] > 0 for f in forms)
              else "SUPPORTED")
    premises = sorted({f["premise"] for f in forms})
    fact = " ".join(_sentences(source_text)[i - 1].strip()
                    for i in premises)[:160]
    return _proof("EXPLICIT_NEGATION", ["S%d" % i for i in premises], fact,
                  claim, result,
                  {"concepts": forms, "n_concepts": present,
                   "n_opposite": opposite})


def numeric_conflict(claim, source_text):
    # Same-unit numeric bounds conflict under binding framing.
    if not v02._FRAMING_RE.search(v02._fold(claim)):
        return None
    # Aggregate claim values recompute across premises; they are not
    # comparable to a single component bound (ARI-POS/ARI-AMBIG).
    if _ARITH_RE.search(v02._fold(claim)):
        return None
    cbounds = v02._num_bounds(claim)
    if not cbounds:
        return None
    # Exclusion thresholds ("ingen ... ved inntekt over X") assert the
    # policy cutoff itself, so two cutoffs of the same kind and unit
    # with different values conflict even though the spans overlap.
    claim_excl = _exclusion_flag(claim)
    # Mixed conjuncts: every claim bound must conflict on the same
    # sentence axis before the operator is eligible (partial conflicts
    # are reviewer work, not unsafe auto-CONTRADICTED).
    for i, sent in enumerate(_sentences(source_text), 1):
        sent_excl = _exclusion_flag(sent)
        if all(any(cb["unit"] == sb["unit"] and (
                v02._bound_span(cb)[1] < v02._bound_span(sb)[0] or
                v02._bound_span(sb)[1] < v02._bound_span(cb)[0])
                or _conflicting_pair([cb], [sb], claim_excl, sent_excl)
                for sb in v02._num_bounds(sent))
                for cb in cbounds):
            break
    else:
        return None
    for i, sent in enumerate(_sentences(source_text), 1):
        if not _time_compatible(claim, sent) or _scope_conflict(claim, sent):
            continue
        # "Det er ingen ... over 4 G" has no lexical subject; the claim
        # asserts the bound itself, so same-subject binding is vacuous.
        if not _DUMMY_RE.match(v02._fold(claim)) and not _same_subject(
                claim, sent, contra=True):
            continue
        for cb in cbounds:
            for sb in v02._num_bounds(sent):
                if cb["unit"] != sb["unit"]:
                    continue
                pair = _conflicting_pair([cb], [sb], claim_excl,
                                         _exclusion_flag(sent))
                if pair:
                    detail = {"claim_bound": list(v02._bound_span(pair[0])),
                              "source_bound": list(v02._bound_span(pair[1])),
                              "unit": cb["unit"], "conflict": pair[2]}
                    return _proof("NUMERIC_CONFLICT", ["S%d" % i], sent,
                                  claim, "CONTRADICTED", detail)
    return None


def temporal_conflict(claim, source_text):
    # Explicit, shared-topic date anchors that disagree on the same axis.
    # A threshold/effective-date anchor on one side only is an axis
    # mismatch (date-of-event vs validity period) -> abstain.
    cdates = pe.extract_dates(claim)
    if not cdates:
        return None
    # Date-as-value only: a bare dated statement is not a
    # deadline anchor and must not fire TEMPORAL_CONFLICT.
    if not _DATE_VALUE_RE.search(v02._fold(claim)):
        return None
    c0 = cdates[0]
    c_thresh = bool(_THRESH_RE.search(v02._fold(claim)))
    for i, sent in enumerate(_sentences(source_text), 1):
        sdates = pe.extract_dates(sent)
        if not sdates:
            continue
        s0 = sdates[0]
        if (c0["y"], c0["m"], c0["d"]) == (s0["y"], s0["m"], s0["d"]):
            continue
        if bool(_THRESH_RE.search(v02._fold(sent))) != c_thresh:
            continue
        if not _shared_content(claim, sent):
            continue
        detail = {"claim_date": [c0["y"], c0["m"], c0["d"]],
                  "source_date": [s0["y"], s0["m"], s0["d"]]}
        return _proof("TEMPORAL_CONFLICT", ["S%d" % i], sent, claim,
                      "CONTRADICTED", detail)
    return None


def simple_arithmetic(claim, source_text):
    # One documented sum/difference recomputes to the claim value.
    if not _ARITH_RE.search(v02._fold(claim)):
        return None
    cb = v02._num_bounds(claim)
    if not cb or len(cb) != 1 or cb[0]["unit"] == "pct":
        return None
    target, unit = cb[0]["value"], cb[0]["unit"]
    found = []
    for i, sent in enumerate(_sentences(source_text), 1):
        if not _time_compatible(claim, sent) or _scope_conflict(claim, sent):
            continue
        if not _same_subject(claim, sent, contra=False):
            continue
        for b in v02._num_bounds(sent):
            if b["unit"] == unit and b["value"] != target:
                found.append((i, b["value"]))
    matches = []
    for x in range(len(found)):
        for y in range(x + 1, len(found)):
            (ia, va), (ib, vb) = found[x], found[y]
            if va + vb == target:
                matches.append(("sum", [ia, ib], [va, vb]))
            if abs(va - vb) == target:
                matches.append(("difference", [ia, ib], [va, vb]))
    # ponytail: exactly-one-relation gate; ambiguity -> abstain (spec 12)
    if len(matches) != 1:
        return None
    rel, premises, values = matches[0]
    fact = "%s of %s = %s %s" % (rel, values, target, unit)
    return _proof("SIMPLE_ARITHMETIC", ["S%d" % p for p in premises], fact,
                  claim, "SUPPORTED",
                  {"relation": rel, "values": values})


OPERATORS = (direct_assertion, explicit_negation, numeric_conflict,
             temporal_conflict, simple_arithmetic)


def run_operators(claim, source_text):
    # Fire all five; never raises. Returns (proofs, crash_flag).
    proofs, crashed = [], False
    for fn in OPERATORS:
        try:
            p = fn(claim, source_text)
        except Exception:
            crashed = True
            continue
        if p:
            proofs.append(p)
    return proofs, crashed
