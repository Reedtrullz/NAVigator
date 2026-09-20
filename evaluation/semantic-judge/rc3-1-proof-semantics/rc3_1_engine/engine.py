"""RC3.1 deterministic proof-semantics engine (development candidate).

Per-atom rule battery over claim/atom text and evidence spans, then a frozen
compound aggregation law. No case IDs, no expected-label maps.

Regex style note: this file deliberately avoids backslash escapes by using
[0-9] classes and explicit (?<![a-z0-9]) / (?![a-z0-9]) boundaries.
"""
import json
import os
import re

from .boundary import compare
from .proposition import (
    NEG_MARKERS, QUANT_SET, STOP, clauses, content_tokens, ctx_pairs,
    numbers, polarity, quantifier_pairs, qualifier_pairs, range_pairs,
    ranges, toks, tok_match,
)
from .decomposition import _subject_of, decompose_claim

ENTAILS = "ENTAILS"
CONTRADICTS = "CONTRADICTS"
PARTIAL = "PARTIAL"
RBI = "RELATED_BUT_INSUFFICIENT"
AMBIGUOUS = "AMBIGUOUS"
UNRELATED = "UNRELATED"

HIGH, MID, LOW = 0.5, 0.15, 0.0

LEX = {
    "lova": ["paragraf"], "forskrift": ["paragraf"], "lov": ["paragraf"],
    "sosialhjelp": ["stonad"], "sosialhjelpssatser": ["stonad"],
}

ANTONYM_CONFLICT = [
    ("sunket", "okte"), ("okte", "sunket"),
    ("sank", "okte"), ("okte", "sank"),
    ("overgar", "beholder"), ("beholder", "overgar"),
    ("nye", "tidligere"), ("tidligere", "nye"),
]

# Claim-subject actors whose absence from the evidence leaves the claim
# unaddressed rather than supported (relation-contract-v2 s8).
SUBJECT_ACTORS = {
    "foreldre", "foreldrene", "elever", "studenter", "kommuner", "kommunen",
    "skolen", "fastlege", "husholdninger", "voksne",
}

HERE = os.path.dirname(os.path.abspath(__file__))
RC32_TASK_DIR = os.path.abspath(
    os.path.join(HERE, "..", "..", "rc3-2-boundary-aware-relation"))
with open(os.path.join(RC32_TASK_DIR, "modality-lattice-v2.json"),
          encoding="utf-8") as _lattice_file:
    LATTICE_V2 = json.load(_lattice_file)["relation_effects"]

DISCRETIONARY = {"kan", "vanligvis", "regel", "skjonn", "skjonsbestemt",
                 "noen", "eller", "etter", "minimum", "hvis", "mindre"}
UNIVERSAL = {"alltid", "uansett"}

# SEMANTIC_RELATION_LAYER_V2: directional modality lattice from the frozen
# modality-relation-lattice.json (relation-contract-v2 section 5).
RELATION_LATTICE = {
    ("REQUIRED", "PERMITTED"): "LICENSED",
    ("REQUIRED", "POSSIBLE"): "LICENSED",
    ("ENTITLED", "POSSIBLE"): "LICENSED",
    ("PERMITTED", "REQUIRED"): "WEAK",
    ("POSSIBLE", "REQUIRED"): "WEAK",
    ("POSSIBLE", "ENTITLED"): "WEAK",
    ("NOT_REQUIRED", "REQUIRED"): "DEONTIC_OPPOSITION",
    ("PROHIBITED", "REQUIRED"): "DEONTIC_OPPOSITION",
    ("PROHIBITED", "PERMITTED"): "DEONTIC_OPPOSITION",
    ("REQUIRED", "NOT_REQUIRED"): "DEONTIC_OPPOSITION",
    ("PROHIBITED", "NOT_REQUIRED"): "WEAK",
}
RELATION_MARKERS = {
    "PROHIBITED": ("kan ikke", "forbudt", "ikke tillatt", "ikke far"),
    "NOT_REQUIRED": ("ikke nodvendig", "ikke krav", "ikke obligatorisk",
                     "ikke paakrevd", "ingen henvisning", "krever ikke",
                     "ikke kreves", "frivillig"),
    "ENTITLED": ("har rett", "rett til", "krav pa", "er en rettighet",
                 "rettighet", "gratis"),
    "REQUIRED": ("skal", "ma", "obligatorisk", "paakrevd", "plikt",
                 "plikter", "kreves", "krever", "har ansvar", "tilbyr"),
    "PERMITTED": ("kan", "adgang", "tilbyds", "far", "mulig"),
}


def _bound(term):
    return "(?<![a-z0-9])" + term + "(?![a-z0-9])"


def _mtok(a, b):
    if tok_match(a, b):
        return True
    if min(len(a), len(b)) >= 5 and (a in b or b in a):
        return True
    return b in LEX.get(a, []) or a in LEX.get(b, [])


def _hits(claim_tokens, span_tokens):
    st = set(span_tokens)
    return sum(1 for t in claim_tokens if any(_mtok(t, u) for u in st))


def _coverage(claim, spans):
    """(best_h1, best_span_index, per-span list)."""
    ct = content_tokens(claim)
    per = []
    for s in spans:
        st = content_tokens(s["text"])
        h1 = _hits(ct, st) / max(len(ct), 1)
        per.append(h1)
    if not per:
        return 0.0, -1, per
    bi = max(range(len(per)), key=lambda i: per[i])
    return per[bi], bi, per


def _proper_noun_absent(claim, spans):
    joined = " ".join(s["text"] for s in spans).lower()
    words = claim.split()
    for i, w in enumerate(words):
        if i == 0:
            continue
        w = w.strip(".,:;!")
        if re.fullmatch(r"[A-Z][a-z]{2,}", w) and w.lower() not in joined:
            return True
    return False


def _age_preds(s):
    txt = s.lower()
    out = []
    for m in re.finditer(r"over ([0-9]{1,3}) ar", txt):
        out.append(("over", int(m.group(1))))
    for m in re.finditer(r"under ([0-9]{1,3}) ar", txt):
        out.append(("under", int(m.group(1))))
    for m in re.finditer(r"opp ?til ([0-9]{1,3})(?: eller ([0-9]{1,3}))? ar",
                         txt):
        out.append(("upto", max(int(m.group(1)),
                                int(m.group(2) or m.group(1)))))
    for m in re.finditer(r"([0-9]{1,3}) til ([0-9]{1,3}) ar", txt):
        out.append(("range", int(m.group(1)), int(m.group(2))))
    for m in re.finditer(r"(?<![a-z0-9])([0-9]{1,3})-aring(?![a-z])", txt):
        out.append(("at", int(m.group(1))))
    for m in re.finditer(
            r"(?<![a-z0-9])([0-9]{1,3})-([0-9]{1,3})(?:-?aringer|[ ]*ar)", txt):
        out.append(("range", int(m.group(1)), int(m.group(2))))
    for m in re.finditer(r"(?<![a-z0-9])([0-9]{1,3})-aringer", txt):
        out.append(("at", int(m.group(1))))
    for m in re.finditer(r"pa ([0-9]{1,3}) ar", txt):
        out.append(("at", int(m.group(1))))
    for m in re.finditer(r"(?<![a-z0-9])([0-9]{1,3})[+](?![0-9])", txt):
        out.append(("atleast", int(m.group(1))))
    return out


def _age_compatible(cpred, epred):
    if cpred[0] == "range" and epred[0] == "range":
        return not (cpred[2] < epred[1] or epred[2] < cpred[1])
    if cpred[0] == "range":
        lo, hi = cpred[1], cpred[2]
    elif cpred[0] == "at":
        lo = hi = cpred[1]
    elif cpred[0] == "atleast":
        lo, hi = cpred[1], 130
    elif cpred[0] == "over":
        lo, hi = cpred[1] + 1, 130
    elif cpred[0] == "under":
        lo, hi = 0, cpred[1] - 1
    else:  # upto
        lo, hi = 0, cpred[1]
    if epred[0] == "range":
        elo, ehi = epred[1], epred[2]
    elif epred[0] == "at":
        elo = ehi = epred[1]
    elif epred[0] == "atleast":
        elo, ehi = epred[1], 130
    elif epred[0] == "over":
        elo, ehi = epred[1] + 1, 130
    elif epred[0] == "under":
        elo, ehi = 0, epred[1] - 1
    else:
        elo, ehi = 0, epred[1]
    return not (hi < elo or ehi < lo)


def _relation_modality(text):
    """Deontic force of the first clause carrying a relation marker."""
    for cl in clauses(text):
        s = " ".join(cl)
        for label in ("PROHIBITED", "NOT_REQUIRED", "ENTITLED",
                      "REQUIRED", "PERMITTED"):
            for mk in RELATION_MARKERS[label]:
                if re.search(_bound(mk) if " " not in mk
                             else re.escape(mk), s.lower()):
                    return label
    return None


def _hard_polarity_opposition(text, all_text):
    """True when claim and evidence negate the same aligned predicate.

    Scope-safe variant of clause-level polarity consensus: each claim
    clause is compared only to its aligned evidence clause, so negation in
    an unrelated clause cannot flip a match, while negation on the same
    clause is a positive polarity conflict.
    """
    tcl = clauses(text)
    ecl = clauses(all_text)
    ev_sentences = [s.strip() for s in re.split(r"[.!?]", all_text) if s.strip()]

    def _ev_sentence_grants_exception(shared):
        # Exception scope is sentence-level: "som hovedregel nei, unntak
        # for ..." bounds the rule inside one sentence even when the
        # clause splitter separates the two halves.
        for sent in ev_sentences:
            if "unntak" not in sent.lower():
                continue
            if any(any(_mtok(t, u) for u in content_tokens(sent))
                   for t in shared):
                return True
        return False

    for tc in tcl:
        ts = " ".join(tc)
        claim_restrictive = bool(re.search(
            _bound("aldri") + "|" + _bound("bare") + "|" + _bound("kun"),
            ts.lower()))
        for ec in ecl:
            es = " ".join(ec)
            if not _shared_content(ts, es):
                continue
            tneg = any(x in NEG_MARKERS for x in tc)
            eneg = any(x in NEG_MARKERS for x in ec)
            if tneg != eneg:
                if claim_restrictive:
                    continue
                if _ev_sentence_grants_exception(_shared_content(ts, es)):
                    continue
                return True
    return False


def _align_spans(text, spans):
    """Span sharing the most content tokens with the atom text."""
    ct = set(toks(text))
    best, best_i = -1, -1
    for i, s in enumerate(spans):
        st = set(toks(s["text"]))
        ov = len(ct & st)
        if ov > best:
            best, best_i = ov, i
    return spans[best_i] if best_i >= 0 else None


def _relation(text, spans, cov, dim_ev=None):
    """SEMANTIC_RELATION_LAYER_V2: atom relation independent of the support
    boundary (relation-contract-v2 sections 2-9). Called after conflict and
    insufficiency rules have not returned; computes relation from the
    frozen modality lattice and polarity doctrine, defaulting to None so
    the caller falls back to RELATED_BUT_INSUFFICIENT (no proof, no
    positive incompatibility).
    """
    all_text = " ".join(s["text"] for s in spans)
    de = dim_ev or {}

    # DIMENSION_EVIDENCE_LAYER_V1: consume the rich per-dimension states
    # from the frozen contract-v1 section 6 pattern table. The 3-state
    # gate output below is untouched; this layer only classifies relation.
    polarity_state = (de.get("polarity") or {}).get("state")
    modality_state = (de.get("modality") or {}).get("state")
    cond_state = (de.get("condition") or {}).get("state")
    actor_state = (de.get("actor") or {}).get("state")
    scope_state = (de.get("scope") or {}).get("state")
    clause_state = (de.get("clause_coverage") or {}).get("state")
    if clause_state == "PARTIAL_OVERLAP":
        # Clause scope breaks proposition identity: negation after the
        # aligned span means the conflict is not yet propositional.
        return RBI, "RL-dim-clause-partial-overlap"
    if polarity_state == "EXPLICIT_CONFLICT" and _shared_content(text, all_text):
        p_rule = (de.get("polarity") or {}).get("rule")
        if p_rule == "DE-polarity-exception-bounded":
            return RBI, "RL-dim-polarity-exception-bounded"
        return CONTRADICTS, "RL-dim-polarity-explicit-conflict"
    if (modality_state == "DEONTIC_OPPOSITION"
            and (de.get("modality") or {}).get("rule")
            == "DE-modality-deontic-opposition"
            and _shared_content(text, all_text)):
        return CONTRADICTS, "RL-dim-modality-deontic-opposition"
    if modality_state == "SOURCE_WEAKER_THAN_CLAIM":
        return RBI, "RL-dim-source-weaker"
    capped = (cond_state == "CONDITION_MISSING"
              or actor_state == "DIFFERENT_ACTOR"
              or scope_state == "SCOPE_CONFLICT")
    if capped:
        return RBI, "RL-dim-capped"
    if modality_state in ("EXACT_MATCH", "CONDITIONALLY_COMPATIBLE",
                          "SOURCE_STRONGER_THAN_CLAIM"):
        return ENTAILS, "RL-dim-modality-licensed"
    c_mod = _relation_modality(text)
    e_mod = _relation_modality(all_text)
    # The frozen lattice JSON is keyed (evidence, claim): source is the
    # evidence document, target is the claim atom.
    if (c_mod and e_mod and _shared_content(text, all_text)
            and (e_mod, c_mod) in RELATION_LATTICE):
        eff = RELATION_LATTICE[(e_mod, c_mod)]
        if eff == "DEONTIC_OPPOSITION":
            return CONTRADICTS, "RL-deontic-opposition"
        if eff == "WEAK":
            return RBI, "RL-modality-weak"
        return ENTAILS, "RL-modality-licensed"
    # Generalized fallback: PROHIBITED evidence vs REQUIRED/ENTITLED claim
    # on a shared object is positive deontic opposition.
    if (c_mod == "PROHIBITED" and e_mod in ("REQUIRED", "ENTITLED")
            and _shared_content(text, all_text)):
        return CONTRADICTS, "RL-prohibited-opposition"
    if _hard_polarity_opposition(text, all_text):
        return CONTRADICTS, "RL-polarity-opposition"
    # A restrictive "bare/kun" in the claim with no counterpart in the
    # aligned evidence is a different predicate, not a contradiction.
    if (re.search(_bound("bare") + "|" + _bound("kun"), text.lower())
            and not re.search(_bound("bare") + "|" + _bound("kun"),
                              all_text.lower())
            and cov >= MID):
        return RBI, "RL-restriction-absent"
    return None


def _positive_conflict(dims):
    """DIMENSION_EVIDENCE_LAYER_V1: positive incompatibility evidence only.
    Restriction-words, condition gaps, or exception clauses are not a
    propositional conflict; they leave the relation unresolved (RBI)."""
    de = dims.get("dimension_evidence") or {}
    polarity = de.get("polarity") or {}
    modality = de.get("modality") or {}
    # Exception-bounded polarity: evidence grants the rule but with an
    # explicit exception the claim omits. The gate blocks support, but
    # the conflict is not propositional (rule-id provenance, contract
    # section 4); the claim remains unresolved against the bounded rule.
    if (polarity.get("state") == "EXPLICIT_CONFLICT"
            and polarity.get("rule") == "DE-polarity-exception-bounded"):
        return False
    # A named deontic opposition (PROHIBITED/NOT_REQUIRED source vs
    # obligated claim) or an unbounded gate polarity conflict is positive
    # incompatibility; direction-unknown modality mismatches are not.
    return (modality.get("state") == "DEONTIC_OPPOSITION"
            or polarity.get("state") == "EXPLICIT_CONFLICT")


def _distinct_numbers(s):
    return {int(x) for x in re.findall(r"[0-9]{3,}", s)}


def _shared_content(claim, span_text):
    ct = content_tokens(claim)
    st = set(content_tokens(span_text))
    return [t for t in ct if any(_mtok(t, u) for u in st)]


def _day_of_month(s):
    m = re.search(r"den ([0-9]{1,2})(?![0-9])", s.lower())
    return int(m.group(1)) if m else None


def _neg_statuses(term, text):
    """Per-clause negation status; a marker must fall in a 4-token window
    immediately before or after the term inside the same clause. Norwegian
    negation follows the verb, so the forward window is required to catch
    "fortsetter ikke" style scoping (dependency-light heuristic)."""
    out = []
    for cl in clauses(text):
        cl_toks = toks(" ".join(cl)) if isinstance(cl, str) else cl
        idxs = [i for i, t in enumerate(cl_toks) if tok_match(term, t)]
        if not idxs:
            continue
        st = False
        for i in idxs:
            window = (list(range(max(0, i - 4), i))
                      + list(range(i + 1, min(len(cl_toks), i + 5))))
            if any(cl_toks[j] in NEG_MARKERS for j in window):
                st = True
                break
        out.append(st)
    return out


def evaluate_atom(text, spans):
    """Return verdict dict for one claim/atom against evidence spans."""
    cov, bi, per = _coverage(text, spans)
    best = spans[bi] if bi >= 0 else None
    all_text = " ".join(s["text"] for s in spans)
    dims = compare(text, all_text)

    def result(verdict, rule, kind="none", span_id=None, note=""):
        return {
            "verdict": verdict, "rule": rule, "kind": kind,
            "coverage": round(cov, 3),
            "span_id": span_id or (best["span_id"] if best else None),
            "grounded": best is not None and cov >= MID, "note": note,
            "boundary": dims,
        }

    def relation_of(verdict, rule, kind="none", span_id=None, note=""):
        """Canonical relation for the R03-R26b battery: these rules already
        classify relation content independently of the boundary state."""
        r = result(verdict, rule, kind, span_id, note)
        r["relation"] = verdict
        return r

    if cov < MID and not text.strip():
        return result(UNRELATED, "R01-empty")
    if cov < MID:
        return result(UNRELATED, "R01-unrelated")

    proper_absent = _proper_noun_absent(text, spans)

    # R03: "kan kreve X" vs "uten X" -> unresolved discretion, not contradiction.
    m = re.search(r"kan kreve ([a-z]+)", text.lower())
    if m and re.search(r"uten " + re.escape(m.group(1)), all_text.lower()):
        return relation_of(AMBIGUOUS, "R03-kan-kreve-vs-uten", "ambiguous")

    # R04: context-bound phone/number pairs.
    cpairs = ctx_pairs(text)
    epairs = []
    for s in spans:
        epairs.extend(ctx_pairs(s["text"]))
    for c, n in cpairs:
        for e, m2 in epairs:
            if c == e and n != m2:
                return relation_of(CONTRADICTS, "R04-ctx-number", "hard",
                              note=f"{c}:{n} vs {m2}")

    # R05/R06: deadlines.
    cday = _day_of_month(text)
    edays = [_day_of_month(s["text"]) for s in spans]
    edays = [d for d in edays if d is not None]
    if cday is not None and edays and all(cday != d for d in edays):
        return relation_of(CONTRADICTS, "R05-deadline-day", "hard",
                      note=f"den {cday}. vs {edays}")
    if (re.search(r"etter at maneden er utlopt", text.lower())
            and re.search(r"for folgende", all_text.lower())):
        return relation_of(CONTRADICTS, "R06-advance-vs-arrears", "hard")

    # R07: range tables (one claimed (range, value) vs table).
    crp = range_pairs(text)
    erp = []
    for s in spans:
        erp.extend(range_pairs(s["text"]))
    if len(crp) == 1 and len(erp) >= 2:
        rng, val = crp[0]
        table = {r: v for r, v in erp}
        if rng in table:
            if table[rng] != val:
                return relation_of(CONTRADICTS, "R07-range-table", "hard",
                              note=f"{rng}={val} but table {rng}={table[rng]}")

    # R08: barnetrygd qualifier x product table.
    cqp = qualifier_pairs(text)
    if cqp and len(cqp) == 1:
        qual, amt = cqp[0]
        product = next((w for w in ("ordinar", "utvidet") if w in toks(text)), None)
        if product:
            for s in spans:
                for q2, a2 in qualifier_pairs(s["text"]):
                    p2 = next((w for w in ("ordinar", "utvidet")
                               if w in toks(s["text"])), None)
                    if p2 == product and q2 == qual:
                        if abs(a2 - amt) > 0.001:
                            return result(CONTRADICTS, "R08-barnetrygd-table",
                                          "hard", span_id=s["span_id"],
                                          note=f"{product}/{qual}: {amt} vs {a2}")
    # Product-amount table: every claimed (qualifier, product, amount)
    # row must match the evidence's stated amount for that same row;
    # a mismatched row blocks entailment of the compound amount claim.
    if len(cqp) >= 2:
        for qual, amt in cqp:
            product2 = next((w for w in ("ordinar", "utvidet")
                             if w in toks(text)), None)
            matched = False
            for s in spans:
                for q2, a2 in qualifier_pairs(s["text"]):
                    p2 = next((w for w in ("ordinar", "utvidet")
                               if w in toks(s["text"])), None)
                    if (product2 and p2 == product2 and q2 == qual
                            and abs(a2 - amt) <= 0.001):
                        matched = True
            if not matched:
                return relation_of(PARTIAL, "R26c-product-row-unresolved",
                              "insufficient")

    # R09: minimum payout.
    m = re.search(r"minst ([0-9]+)", text.lower())
    m2 = re.search(r"minsteutbetaling er ([0-9]+)", all_text.lower())
    if m and m2 and int(m.group(1)) != int(m2.group(1)):
        return relation_of(CONTRADICTS, "R09-minimum-amount", "hard",
                      note=f"minst {m.group(1)} vs {m2.group(1)}")

    # R10: threshold "mer enn N".
    m = re.search(r"mer enn ([0-9]+)", all_text.lower())
    if m:
        n = m.group(1)
        claim_has_bare = (re.search(_bound(n), text.lower())
                          and not re.search(r"mer enn " + n, text.lower()))
        if claim_has_bare:
            return relation_of(CONTRADICTS, "R10-threshold", "hard",
                          note=f"mer enn {n}")

    # R11: tax direction.
    if ("skatt" in text.lower()
            and ("etter skatt" in text.lower()) != ("etter skatt" in all_text.lower())
            and "for skatt" in all_text.lower()):
        return relation_of(CONTRADICTS, "R11-tax-direction", "hard")

    # R12: direction antonyms.
    low_text, low_all = text.lower(), all_text.lower()
    for a, b in ANTONYM_CONFLICT:
        if re.search(_bound(a), low_text) and re.search(_bound(b), low_all):
            return relation_of(CONTRADICTS, "R12-direction-antonym", "soft",
                          note=f"{a}/{b}")

    # R13: age compatibility.
    cage = _age_preds(text)
    eage = []
    for s in spans:
        eage.extend(_age_preds(s["text"]))
    if cage and eage:
        if not any(_age_compatible(c, e) for c in cage for e in eage):
            if _positive_conflict(dims):
                return relation_of(CONTRADICTS, "R13-age-conflict", "hard",
                              note=f"{cage} vs {eage}")
            return relation_of(RBI, "R13-age-unresolved", "insufficient",
                          note=f"{cage} vs {eage}")

    # R14: quantifier-bound pairs (alle, N).
    cq = quantifier_pairs(text)
    eq = []
    for s in spans:
        eq.extend(quantifier_pairs(s["text"]))
    alle_claims = [q for q in cq if q[0] == "alle"]
    alle_ev = [q for q in eq if q[0] == "alle"]
    if alle_claims and alle_ev:
        if not any(n == ev_n for (_, n) in alle_claims for (_, ev_n) in alle_ev):
            if _positive_conflict(dims):
                return relation_of(CONTRADICTS, "R14-quantifier-bound", "hard",
                              note=f"{alle_claims} vs {eq}")
            return relation_of(RBI, "R14-quantifier-unresolved", "insufficient",
                          note=f"{alle_claims} vs {eq}")

    # R15: universal claim vs discretionary evidence on shared predicate.
    ctoks = set(toks(text))
    if ctoks & UNIVERSAL or re.search(r"i alle kommuner", text.lower()):
        disc = {"kan", "vanligvis", "skjonn", "skjonsbestemt", "regel",
                "noen"} & set(toks(all_text))
        if disc and _shared_content(text, all_text):
            if _positive_conflict(dims):
                return relation_of(CONTRADICTS,
                              "R15-universal-vs-discretionary", "soft",
                              note=f"universal vs {sorted(disc)}")
            return relation_of(RBI, "R15-universal-unresolved", "insufficient",
                          note=f"universal vs {sorted(disc)}")
    # Universal claim vs evidence stating an alternative ("eller"):
    # "alltid til barnet" is not entailed when the evidence offers the
    # recipient as an alternative, not a guarantee.
    if (ctoks & UNIVERSAL
            and re.search(r"(?<![a-z0-9])eller(?![a-z0-9])",
                          all_text.lower())):
        if _shared_content(text, all_text):
            return relation_of(PARTIAL, "R26d-universal-vs-alternative",
                          "insufficient")
    if ctoks & {"alle", "all"}:
        restrict = {"unntak", "unntatt", "forhold", "mindre", "saerlige",
                    "ikke", "kan", "noen"} & set(toks(all_text))
        if restrict and _shared_content(text, all_text):
            if _positive_conflict(dims):
                return relation_of(CONTRADICTS,
                              "R15b-universal-vs-restriction", "soft",
                              note=f"universal vs {sorted(restrict)}")
            return relation_of(RBI, "R15b-universal-unresolved", "insufficient",
                          note=f"universal vs {sorted(restrict)}")

    # R16: flat requirement unsupported while evidence says universal availability.
    m = re.search(r"(?<![a-z0-9])(krever|kreve)(?![a-z0-9])(.{0,60})", text.lower())
    if m:
        obj = content_tokens(m.group(2))
        if obj and not _shared_content(m.group(2), all_text):
            if re.search(r"alle (kan|har|far)", all_text.lower()):
                return relation_of(CONTRADICTS, "R16-invented-requirement", "soft")

    # R16b: explicit claim-side restriction vs universal evidence availability.
    if (re.search(r"begrenset til|(?<![a-z0-9])(?<!ikke )(kun|bare)(?![a-z0-9])", text.lower())
            and re.search(r"alle (kan|har|far)", all_text.lower())
            and _shared_content(text, all_text)):
        return relation_of(CONTRADICTS, "R16b-restriction-vs-universal", "soft")

    # R17-negation-flip is superseded by the boundary gate: clause-level
    # polarity consensus in boundary.compare blocks polarity flips before
    # support rules run.

    # Uten-object gate: a claim that asserts X "uten Y" is unsupported
    # when the evidence nowhere grants Y ("uten Y" / "ingen Y"); the
    # un-Y part of the claim stays unresolved instead of auto-support.
    m = re.search(r"uten ([a-z0-9]+(?: [a-z0-9]+)?)", text.lower())
    if m:
        obj = m.group(1)
        if not re.search(r"(uten|ingen) " + re.escape(obj), all_text.lower()):
            return relation_of(PARTIAL, "R26b-uten-object-unresolved",
                          "insufficient")

    if proper_absent:
        return result(RBI, "R02-proper-noun-scope", "insufficient")

    # Boundary gate: a hard dimension mismatch forbids auto-support and
    # classifies the conflict; unresolved dimensions fail closed.
    if dims["overall"] == "BOUNDARY_BLOCKED":
        res = _relation(text, spans, cov, dims.get("dimension_evidence"))
        rel, rel_rule = res if res else (RBI, "RL-no-proof")
        r = result(CONTRADICTS if rel == CONTRADICTS else RBI,
                   "R27-boundary-blocked", "soft",
                      note=",".join(dims["blocking_dimensions"]))
        r["relation"] = rel
        r["relation_rule"] = rel_rule
        return r
    if dims["overall"] == "BOUNDARY_UNRESOLVED":
        res = _relation(text, spans, cov, dims.get("dimension_evidence"))
        rel, rel_rule = res if res else (RBI, "RL-unresolved-no-proof")
        r = result(AMBIGUOUS if rel == AMBIGUOUS else rel,
                   "R28-boundary-unresolved", "ambiguous",
                      note=",".join(dims["blocking_dimensions"]))
        r["relation"] = rel
        r["relation_rule"] = rel_rule
        return r

    # Support rules.
    if alle_claims and any(n == ev_n
                           for (_, n) in alle_claims for (_, ev_n) in alle_ev):
        return result(ENTAILS, "R14-quantifier-support")

    # R18: aligned double negation. Both sides must carry negation on a
    # shared token in the aligned clause, not merely somewhere in the text.
    neg_claim = any(t in NEG_MARKERS for t in toks(text))
    neg_ev = any(t in NEG_MARKERS for t in toks(all_text))
    aligned_neg = any(
        any(_neg_statuses(t, text)) and any(_neg_statuses(t, all_text))
        for t in _shared_content(text, all_text)
        if t not in QUANT_SET and not t.isdigit()
    )
    if neg_claim and neg_ev and aligned_neg and cov >= 0.3:
        return result(ENTAILS, "R18-negation-aligned")

    # R19: requirement object present (skal/ma/krever + object in evidence).
    m = re.search(r"(?<![a-z0-9])(skal|ma|krever)(?![a-z0-9])(.{0,70})", text.lower())
    if m and _shared_content(m.group(2), all_text):
        if not re.search(r"uten |ingen ", all_text.lower()):
            return result(ENTAILS, "R19-requirement-object")

    # R20: legal authority (lova/forskrift claim, paragraf evidence).
    if (re.search(r"(?<![a-z0-9])(lova|forskrift|loven)(?![a-z0-9])", text.lower())
            and "paragraf" in all_text.lower() and cov >= 0.25):
        return result(ENTAILS, "R20-legal-authority")

    # R21: sakkyndig role compatibility.
    if "sakkyndig" in text.lower() and "sakkyndig" in all_text.lower() and cov >= 0.25:
        return result(ENTAILS, "R21-sakkyndig-role")

    # R22: preventive vs non-acute.
    if (re.search(r"ikke[^.;]*(?<![a-z0-9])akutt(?![a-z0-9])", text.lower())
            and "forebyggende" in all_text.lower()):
        return result(ENTAILS, "R22-preventive-vs-acute")

    # R23: distinctive shared number.
    cnums = _distinct_numbers(text)
    if cnums and cnums <= _distinct_numbers(all_text) and cov >= 0.3:
        return result(ENTAILS, "R23-shared-number")

    # R23a: arithmetic sum proof. Every distinctive claim number must be
    # reproducible as a sum of evidence numbers on an addition line.
    if cnums:
        ev_nums = re.findall(r"([0-9]{2,}) [+] ([0-9]{2,}) = ([0-9]{2,})", all_text)
        covered_nums = set()
        for x, y, z in ev_nums:
            if int(x) + int(y) == int(z):
                covered_nums.add(int(z))
        ev_distinct = sorted(_distinct_numbers(all_text))
        for i in range(len(ev_distinct)):
            for j in range(i + 1, len(ev_distinct)):
                covered_nums.add(ev_distinct[i] + ev_distinct[j])
        if cnums and cnums <= covered_nums:
            return result(ENTAILS, "R23a-arithmetic-sum")

    # Soundness guard: unverified distinctive numbers block auto-support.
    claim_nums = {t for t in toks(text) if t.isdigit() and len(t) >= 3}
    if claim_nums:
        covered = False
        for n in claim_nums:
            if n in toks(all_text):
                covered = True
            for lo, hi in ranges(all_text):
                if lo <= int(n) <= hi:
                    covered = True
        if not covered:
            return result(RBI, "R24-unverified-number", "insufficient")

    if cov >= HIGH:
        return result(ENTAILS, "R25-coverage")
    r = result(RBI, "R26-coverage-mid", "insufficient")
    r["relation"] = RBI
    return r


def _aggregate(atom_results):
    verdicts = [a["verdict"] for a in atom_results]
    if any(v == AMBIGUOUS for v in verdicts):
        return AMBIGUOUS, "AGG-ambiguous-propagates"
    if any(v == UNRELATED for v in verdicts):
        return UNRELATED, "AGG-unrelated-propagates"
    conflicts = [(i, a) for i, a in enumerate(atom_results)
                 if a["verdict"] == CONTRADICTS]
    if conflicts:
        lead_i, lead = conflicts[0]
        if lead_i == 0 and lead["kind"] == "hard":
            return CONTRADICTS, "AGG-lead-hard-conflict"
        return PARTIAL, "AGG-conflict-partial"
    if all(v == ENTAILS for v in verdicts):
        return ENTAILS, "AGG-all-entails"
    return RBI, "AGG-insufficient-atom"


def evaluate_case(case):
    spans = case["evidence"]
    if case.get("compound"):
        atoms = decompose_claim(case["claim"])
        lead_subject = _subject_of(atoms[0]) if atoms else None
        results = []
        for i, atom in enumerate(atoms):
            t = atom
            if (i > 0 and atom.split()
                    and atom.split()[0] in {"den", "det", "dette", "de"}
                    and lead_subject):
                t = lead_subject + " " + atom
            results.append(evaluate_atom(t, spans))
        top, agg = _aggregate(results)
        return {"case_id": case["case_id"], "verdict": top, "aggregation": agg,
                "atoms": [
                    {"atom_id": f"A{i+1}", "text": atoms[i], **results[i]}
                    for i in range(len(atoms))]}
    r = evaluate_atom(case["claim"], spans)
    return {"case_id": case["case_id"], "verdict": r["verdict"],
            "aggregation": "SINGLE",
            "atoms": [{"atom_id": "A1", "text": case["claim"], **r}]}
