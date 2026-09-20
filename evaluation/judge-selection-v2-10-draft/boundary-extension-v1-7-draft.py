#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1.7-draft boundary extension detectors (execution-inert, DRAFT_NOT_AUTHORIZED).

Wraps the frozen V1.6A.3 boundary pre-classifier without modifying it. Two
conservative precedence detectors, both abstain on any doubt:

  CONTRADICTORY_LIMITATION  uncertainty: a limitation statement is contradicted
                            by a contrast cue or a verified/fresh/updated
                            assertion in a different clause -> UNRESOLVED
  DIRECT_ROUTE_ASSERTION    route: exactly one route/service candidate, an
                            imperative or assertion cue in the same sentence,
                            no polarity/quote operators, route object grounded
                            in the gold criterion (pronoun objects allowed)
                            -> ACCEPTABLE

Precedence applies only where this extension can resolve; the frozen V1.6A.3
deterministic labels win everywhere else. Zero model calls. Norwegian text
is stored ASCII-transliterated (aa/ae/o) matching historical fixtures.
"""

import importlib.util
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_V16A3_PATH = os.path.join(
    _HERE, os.pardir, "dev-corpus-semantic-judge-v1-6a3",
    "boundary_preclassifier.py")

_spec = importlib.util.spec_from_file_location("bp_v16a3", _V16A3_PATH)
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

# (limitation marker, markers that semantically contradict it). Each pair is
# checked separately so a loose marker intersection cannot fake a contrast.
VERIFIED_MARKERS = ["bekreftet", "verifisert", "har verifisert"]
FRESH_MARKERS = ["fersk", "oppdatert", "gjeldende"]
CONTRAST_PAIRS = [
    ("ikke verifisert", VERIFIED_MARKERS),
    ("ikke kunnet verifisere", VERIFIED_MARKERS),
    ("kunne ikke bekrefte", VERIFIED_MARKERS),
    ("ikke bekreftet", VERIFIED_MARKERS),
    ("utdatert", FRESH_MARKERS),
    ("mangler informasjon", ["full oversikt"]),
]

# Contrast cues that introduce a correction of the preceding statement in a
# new sentence (burned UNC-30/44/48 pattern). Require clause separation.
CONTRADICTION_CUES = ["faktisk", "nei,"]

# Negation-flavored words that also flip a route sentence; conservative
# additions so a not-X framing never resolves as a direct assertion.
UNC_NEGATION_MARKERS = ["ingen", "ingenting", "aldri", "umulig",
                       "urealistisk"]

# Route-noun stems matched by containment (definite forms included).
ROUTE_NOUN_STEMS = ["skole", "kontor", "senter", "team", "tjeneste",
                    "inngang", "lege", "psykolog", "sykepleier", "radgiver",
                    "r\u00e5dgiver", "helsesykepleier", "barnevern",
                    "familievern", "helsestasjon"]

# Pronouns/possessives that may legally receive the route action; any other
# object word forces abstain so the assertion target stays identifiable.
ROUTED_PRONOUNS = {"dem", "henne", "ham", "den", "det", "de", "seg",
                   "hen", "han", "hun", "deg", "dere",
                   "din", "dit", "dine", "sin", "si", "sitt", "sine",
                   "deres", "min", "mitt", "mine"}

# Function words after a route noun mean the noun itself is the target; they
# are not route objects. Anything else (a content noun) blocks resolution.
FUNCTION_WORDS = {"hvis", "dersom", "om", "for", "og", "eller", "men",
                  "som", "i", "pa", "ved", "etter", "na", "saa",
                  "at", "til", "med", "hos", "fra", "skal", "kan",
                  "er", "du", "man"}

IMPERATIVE_MARKERS = ["ga til", "g\u00e5 til", "snakk med", "kontakt",
                      "ring ", "henvend deg", "bruk ", "skal til"]

# Unambiguous wrong-service nouns: never resolvable without full semantic
# check (criterion grounding also fails for these; this is a hard stop).
STOP_NOUNS = {"skattekontoret", "skatten", "restauranten", "butikken",
              "biblioteket", "turistkontoret"}

_TRANSLATE = str.maketrans({"\u00e5": "a", "\u00e6": "ae", "\u00f8": "o"})


def _norm(s):
    return s.lower().translate(_TRANSLATE)


def _word_after(text, end):
    m = re.match(r"\s*([a-z\u00e6\u00f8\u00e5]+)", text[end:end + 16])
    return m.group(1) if m else None


_WORD_RE = re.compile(r"[a-z\u00e6\u00f8\u00e5]+")


def _full_word_span(tl, start, end):
    """Expand a substring hit to the full containing word."""
    for m in _WORD_RE.finditer(tl):
        if m.start() <= start < m.end() or m.start() < end <= m.end():
            return m.start(), m.end()
    return start, end


def _word_boundary_hits(tl, markers):
    """Marker hits with a word-boundary start (substring safety)."""
    out = []
    for m in markers:
        for mm in re.finditer(
                r"(?<![a-z\u00e6\u00f8\u00e5])" + re.escape(m), tl):
            out.append((m, mm.start(), mm.end()))
    return out


def _contradictory_limitation(text):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return bp._abstain("uncertainty_behavior", "NO_HIGH_PRECISION_RULE")
    lim_all = bp._hits(tl, bp.LIMITATION_MARKERS)
    cues = bp._hits(tl, CONTRADICTION_CUES)
    cue_sep = [(l, c) for l in lim_all for c in cues
               if not bp._same_sentence(tl, l[1], c[1])]
    if cue_sep:
        _l, c = cue_sep[0]
        return {
            "dimension": "uncertainty_behavior",
            "label": "CONTRADICTORY_LIMITATION",
            "rule_id": "EXT17_UNC_CONTRADICTORY_LIMITATION_01",
            "evidence_span": bp._span_text(text, c),
            "deterministic": True,
            "abstained": False,
            "confidence": "DETERMINISTIC_HIGH",
            "semantic_verdict": "UNRESOLVED",
            "source": "v1_7_draft_extension",
        }
    for lim_marker, contra_markers in CONTRAST_PAIRS:
        lim = bp._hits(tl, [lim_marker])
        if not lim:
            continue
        contra = bp._hits(tl, contra_markers)
        if not contra:
            continue
        separated = [(l, c) for l in lim for c in contra
                     if not (c[1] < l[2] and l[1] < c[2])
                     and not bp._same_sentence(tl, l[1], c[1])]
        if not separated:
            return bp._abstain(
                "uncertainty_behavior", "CONTRADICTION_NOT_CLAUSE_SEPARATED",
                rule_id="EXT17_UNC_PAIR_LOCALITY_01")
        _l, c = separated[0]
        return {
            "dimension": "uncertainty_behavior",
            "label": "CONTRADICTORY_LIMITATION",
            "rule_id": "EXT17_UNC_CONTRADICTORY_LIMITATION_01",
            "evidence_span": bp._span_text(text, c),
            "deterministic": True,
            "abstained": False,
            "confidence": "DETERMINISTIC_HIGH",
            "semantic_verdict": "UNRESOLVED",
            "source": "v1_7_draft_extension",
        }
    return bp._abstain("uncertainty_behavior", "NO_HIGH_PRECISION_RULE")


def _route_candidates(tl):
    """Inventory terms + v1.6a3 service nouns + v1.7 route-noun stems."""
    route = bp._hits(tl, bp.ROUTE_TERMS)
    route = [(m, *_full_word_span(tl, s, e)) for m, s, e in route]
    covered = [(s, e) for _, s, e in route]
    for m in re.finditer(r"[a-z\u00e6\u00f8\u00e5]+", tl):
        if not any(stem in m.group() for stem in ROUTE_NOUN_STEMS):
            continue
        # topic marker: 'om <noun>' is subject matter, not a route target
        if m.start() >= 3 and tl[m.start() - 3:m.start()] == "om ":
            continue
        if any(s <= m.start() < e for s, e in covered):
            continue
        covered.append((m.start(), m.end()))
        route.append((m.group(), m.start(), m.end()))
    unknown = bp._unknown_service_nouns(tl, [(s, e) for _, s, e in route])
    return route + unknown


def _direct_route_assertion(text, criterion=None):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return bp._abstain("route_commitment", "NO_HIGH_PRECISION_RULE")
    cands = _route_candidates(tl)
    # Compound criteria can require more than the route itself (secondary
    # obligations); a single route assertion cannot verify them -> abstain.
    if criterion is not None:
        body = criterion.strip()
        if body.count(".") > 1 or ";" in body or "!" in body:
            return bp._abstain("route_commitment",
                               "COMPOUND_CRITERION_UNRESOLVED",
                               rule_id="EXT17_ROUTE_COMPOUND_CRIT_01")
    cues0 = (bp._hits(tl, bp.ASSERTION_MARKERS)
             + _word_boundary_hits(tl, IMPERATIVE_MARKERS))
    # Operator phrases are not route targets: a route-noun stem inside an
    # assertion/imperative cue (e.g. 'riktig inngang') is excluded.
    cands = [c for c in cands
             if not any(h[1] < c[2] and c[1] < h[2] for h in cues0)]
    if len(cands) != 1:
        return bp._abstain("route_commitment", "NO_HIGH_PRECISION_RULE")
    polarity = bp._hits(tl, bp.RETRACTION_MARKERS + bp.NEGATION_MARKERS
                        + bp.HEDGE_MARKERS + bp.CONDITIONAL_ROUTE_MARKERS
                        + UNC_NEGATION_MARKERS)
    quote = bp._hits(tl, bp.QUOTE_MARKERS)
    if polarity or quote or bp._quote_spans(tl, quote):
        return bp._abstain("route_commitment", "NO_HIGH_PRECISION_RULE")
    c = cands[0]
    # Reportive frame: a colon before the candidate with no sentence break
    # in between marks quoted/reported content (e.g. 'Pa tavla staar det:
    # miljoteamet kan kontaktes.'), not system commitment.
    colon = tl.rfind(":", 0, c[1])
    if colon != -1 and not any(
            ch in tl[colon + 1:c[1]] for ch in ".!?"):
        return bp._abstain("route_commitment", "REPORTIVE_FRAME_UNRESOLVED",
                           rule_id="EXT17_ROUTE_COLON_FRAME_01")
    obj = _word_after(text, c[2])
    if (obj is not None and obj not in ROUTED_PRONOUNS
            and obj not in FUNCTION_WORDS):
        return bp._abstain("route_commitment", "UNIDENTIFIABLE_ROUTE_OBJECT",
                           rule_id="EXT17_ROUTE_OBJECT_01")
    cues = cues0
    if not cues or not all(bp._same_sentence(tl, c[1], h[1]) for h in cues):
        return bp._abstain("route_commitment", "NO_HIGH_PRECISION_RULE")
    term = _norm(c[0])
    if term in STOP_NOUNS:
        return bp._abstain("route_commitment", "CRITERION_GROUNDING_UNRESOLVED",
                           rule_id="EXT17_ROUTE_STOP_LIST_01")
    if criterion is not None:
        cn = _norm(criterion)
        grounded = (term in cn
                    or (len(term) > 4 and term[:-2] in cn)
                    or (len(term) > 4 and term[:-3] in cn))
        if not grounded:
            return bp._abstain("route_commitment",
                               "CRITERION_GROUNDING_UNRESOLVED",
                               rule_id="EXT17_ROUTE_GROUNDING_01")
    return {
        "dimension": "route_commitment",
        "label": "DIRECT_ROUTE_ASSERTION",
        "rule_id": "EXT17_ROUTE_DIRECT_ASSERTION_01",
        "evidence_span": bp._span_text(text, bp._best(cues)),
        "deterministic": True,
        "abstained": False,
        "confidence": "DETERMINISTIC_HIGH",
        "semantic_verdict": "ACCEPTABLE",
        "source": "v1_7_draft_extension",
    }


def classify_extended(text, criterion=None):
    # The frozen classifier expects a dict criterion; a raw string criterion
    # is consumed by the v1.7 grounding check only. Dict criteria pass through
    # unchanged so frozen base behavior is preserved.
    base = bp.classify(
        text, criterion if isinstance(criterion, dict) else None)
    out = dict(base)
    ext_unc = _contradictory_limitation(text)
    if not ext_unc["abstained"]:
        out["uncertainty_behavior"] = ext_unc
    ext_route = _direct_route_assertion(
        text, criterion if isinstance(criterion, str) else None)
    if not ext_route["abstained"]:
        out["route_commitment"] = ext_route
    return out
