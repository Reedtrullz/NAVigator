#!/usr/bin/env python3
"""V1.6A.2 deterministic boundary pre-classifier (model-free, precision-first,
clause-local route grounding)."""

import re

ROUTE_TERMS = [
    "psykisk helsetjeneste", "psykiske helsetjeneste",
    "rask psykisk helsehjelp", "fastlege",
    "helsestasjon", "skolehelsetjeneste", "familievernkontor",
    "helsesykepleier", "familieteam", "barnevern", "kommunepsykolog",
    "hfu", "bup", "rph", "ppt", "habu", "dps",
]
QUOTE_MARKERS = ["\u00ab", "\u00bb", "sier:", "sier at", "skriver at",
                 "oppgir:", "oppgir at", "if\u00f8lge"]
QUOTE_MARKERS += ["rapporterer at", "opplyser at"]
ADOPTION_MARKERS = ["anbefaler", "anbefale", "riktig sted", "riktig inngang",
                    "b\u00f8r kontakte", "b\u00f8r kontaktes"]
RETRACTION_MARKERS = ["trekker tilbake", "korrigere meg",
                      "jeg kan ikke st\u00e5 inne for",
                      "kan jeg ikke st\u00e5 inne for",
                      "det stemmer ikke", "nei,"]
NEGATION_MARKERS = ["ikke"]
CONDITIONAL_ROUTE_MARKERS = ["hvis", "dersom", "i tilfeller der",
                             "kunne v\u00e6re", "v\u00e6re en mulighet",
                             "vurderes"]
HEDGE_MARKERS = ["ser ut til", "trolig", "sannsynligvis", "antakelig",
                 "kanskje", "muligens", "kan tenkes"]
HEDGE_MARKERS += ["ser ut som", "det er mulig"]
ASSERTION_MARKERS = ["riktig sted", "riktig inngang", "riktig rute",
                     "riktig f\u00f8rste kontakt", "b\u00f8r kontakte",
                     "b\u00f8r kontaktes", "kan kontaktes", "kan kontakte",
                     "henvise", "henvis", "anbefaler", "anbefale"]
VAGUE_MARKERS = ["hjelp", "hjelpe", "st\u00f8tte", "muligheter"]

LIMITATION_MARKERS = ["ikke kunnet verifisere", "ikke verifisert",
                      "mangler informasjon", "mangler fortsatt informasjon",
                      "kunne ikke bekrefte", "uavklart", "ikke sjekket",
                      "ikke har kunnet"]
LIMITATION_MARKERS += ["vet ikke", "mangler oversikt"]
PARTITIVE_MARKERS = ["\u00e9n av", "en av"]
CERTAINTY_MARKERS = ["helt sikkert", "garanterer", "garantert", "utvetydig"]
CERTAINTY_MARKERS += ["er helt sikker", "er sikker p\u00e5"]
VERIFIED_PART_MARKERS = ["har verifisert", "kan bekrefte"]
VERIFIED_PART_MARKERS += ["er bekreftet", "er verifisert"]
CONDITIONAL_UNC_MARKERS = ["hvis", "dersom"]
SCOPE_NEGATION_MARKERS = ["kan ikke fastsl\u00e5", "ikke p\u00e5vist",
                          "ikke foreligger"]
SCOPE_NEGATION_MARKERS += ["kan ikke bekrefte"]
USER_ATTRIBUTION_MARKERS = ["du sier", "du forteller", "du oppgir"]
USER_ATTRIBUTION_MARKERS += ["du beskriver"]
THIRD_PARTY_ATTRIBUTION_MARKERS = ["sier at", "oppgir at", "skriver at",
                                   "if\u00f8lge"]
THIRD_PARTY_ATTRIBUTION_MARKERS += ["rapporterer at", "opplyser at"]
SCOPE_CONDITIONAL_MARKERS = ["hvis", "dersom", "i noen tilfeller",
                             "kan i noen tilfeller", "oppst\u00e5",
                             "kunne oppst\u00e5"]
SYSTEM_ENDORSEMENT_MARKERS = ["er i akutt fare", "foreligger",
                              "viser tegn p\u00e5"]

SERVICE_NOUN_STEMS = ["tjenest", "kontor", "senter", "sentral", "team"]

_SENT_RE = re.compile(r"[^.!?]+[.!?]?")
_CONJ_RE = re.compile(r"\b(men|eller)\b")


def _hits(text_lower, markers):
    out = []
    for m in markers:
        start = 0
        while True:
            i = text_lower.find(m, start)
            if i == -1:
                break
            out.append((m, i, i + len(m)))
            start = i + 1
    return out


def _best(hits):
    return max(hits, key=lambda h: h[2] - h[1]) if hits else None


def _span_text(text, span):
    return text[span[1]:span[2]] if span else None


def _same_sentence(text_lower, a, b):
    lo, hi = sorted((a, b))
    return not any(c in text_lower[lo:hi] for c in ".!?")


def _clauses(text_lower):
    """Split into clause spans: sentences first, then split on men/eller."""
    spans = []
    for m in _SENT_RE.finditer(text_lower):
        seg = m.group()
        if not seg.strip():
            continue
        base = m.start()
        pieces = []
        pos = 0
        for cm in _CONJ_RE.finditer(seg):
            if cm.start() > pos:
                pieces.append((base + pos, base + cm.start()))
            pos = cm.end()
        pieces.append((base + pos, base + len(seg)))
        spans.extend(pieces)
    return spans


def _span_of(text_lower, offsets):
    return text_lower[offsets[0]:offsets[1]]


def _unknown_service_nouns(text_lower, exclude_spans):
    """Service-noun words not covered by any inventory route-term hit."""
    nouns = []
    for m in re.finditer(r"[a-z\u00e6\u00f8\u00e5]+", text_lower):
        if not any(st in m.group() for st in SERVICE_NOUN_STEMS):
            continue
        if any(s <= m.start() and m.start() < e for s, e in exclude_spans):
            continue
        nouns.append((m.group(), m.start(), m.end()))
    return nouns


def _abstain(dimension, reason, rule_id=None, conflict=None):
    out = {
        "dimension": dimension,
        "label": "ABSTAIN",
        "rule_id": rule_id,
        "evidence_span": None,
        "deterministic": True,
        "abstained": True,
        "reason": reason,
    }
    if conflict is not None:
        out["conflict"] = conflict
    return out


def _resolve(dimension, fired):
    if not fired:
        return _abstain(dimension, "NO_HIGH_PRECISION_RULE")
    top = max(f["priority"] for f in fired)
    group = [f for f in fired if f["priority"] == top]
    labels = {f["label"] for f in group}
    if len(labels) > 1:
        return _abstain(
            dimension, "ABSTAIN_CONFLICT",
            conflict=[{"rule_id": f["rule_id"], "label": f["label"]} for f in group],
        )
    win = group[0]
    if win["label"] == "ABSTAIN_CONFLICT":
        return _abstain(
            dimension, "ABSTAIN_CONFLICT", rule_id=win["rule_id"],
            conflict=[{"rule_id": f["rule_id"], "label": f["label"]}
                      for f in fired if f["priority"] < top],
        )
    return {
        "dimension": dimension,
        "label": win["label"],
        "rule_id": win["rule_id"],
        "evidence_span": _span_text(win["text"], win["span"]),
        "deterministic": True,
        "abstained": False,
        "confidence": "DETERMINISTIC_HIGH",
    }


def _route_rules(text, criterion):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return _abstain("route_commitment", "NO_HIGH_PRECISION_RULE")

    route = _hits(tl, ROUTE_TERMS)
    route_spans = [(s, e) for _, s, e in route]
    quote = _hits(tl, QUOTE_MARKERS)
    adopt = _hits(tl, ADOPTION_MARKERS)
    retraction = _hits(tl, RETRACTION_MARKERS)
    hedge = _hits(tl, HEDGE_MARKERS)
    cond = _hits(tl, CONDITIONAL_ROUTE_MARKERS)
    vague = _hits(tl, VAGUE_MARKERS)
    neg_hits = [(m.group(), m.start(), m.end()) for m in re.finditer("ikke", tl)]
    qspans = _quote_spans(tl, quote)

    def in_quote(pos):
        return any(s <= pos < e for s, e in qspans)

    # assertion/adoption cues only license when outside quotation scope
    assertion = [h for h in _hits(tl, ASSERTION_MARKERS) if not in_quote(h[1])]
    adopt = [h for h in adopt if not in_quote(h[1])]

    clauses = _clauses(tl)

    def clause_idx(pos):
        for i, (s, e) in enumerate(clauses):
            if s <= pos < e:
                return i
        return -1

    def op_clauses(hits):
        return {clause_idx(s) for _, s, _e in hits}

    cands = []
    for t, s, e in route:
        cands.append({"term": t, "start": s, "end": e,
                      "clause": clause_idx(s), "inventory": True})
    for n, s, e in _unknown_service_nouns(tl, route_spans):
        cands.append({"term": n, "start": s, "end": e,
                      "clause": clause_idx(s), "inventory": False})

    mixed = len(cands) > 1

    # conservative cross-clause repair: a route/service candidate whose clause
    # carries no licensing operator (assertion, hedge, negation, retraction,
    # quote, conditional - vague is NOT licensing) cannot be grounded.
    retr_c = op_clauses(retraction)

    def locally_grounded(c):
        ci = c["clause"]
        if any(ci in op_clauses(h) for h in
               (assertion, hedge, neg_hits, retraction, quote, cond)):
            return True
        # correction binding: a retraction in the immediately following clause
        # retroactively grounds the commitment it corrects (burned gold
        # VR-R-01..04 / CMT-R-04 pattern).
        return (ci + 1) in retr_c

    ungrounded = [c for c in cands if not locally_grounded(c)]
    if ungrounded:
        return _abstain("route_commitment", "UNGROUNDED_ROUTE_CANDIDATE",
                        rule_id="BC_ROUTE_CLAUSE_LOCALITY_01",
                        conflict=[{"noun": c["term"], "clause": c["clause"],
                                   "inventory": c["inventory"]} for c in ungrounded])

    # ambiguous competition: 2+ candidates share one clause and compete for
    # the same operator - unless the clause is a single hypothetical frame.
    per_clause = {}
    for c in cands:
        per_clause.setdefault(c["clause"], []).append(c)
    cond_c = op_clauses(cond)
    competing = {ci: cs for ci, cs in per_clause.items()
                 if len(cs) > 1 and ci not in cond_c}
    if competing:
        return _abstain("route_commitment", "AMBIGUOUS_GROUNDING_CONFLICT",
                        rule_id="BC_ROUTE_AMBIGUOUS_02",
                        conflict=[{"nouns": [c["term"] for c in cs],
                                   "clause": ci} for ci, cs in competing.items()])

    # V1.6A.1 same-sentence negation preserved for single-proposition outputs.
    neg = None
    if route:
        for ni in (m.start() for m in re.finditer("ikke", tl)):
            if any(_same_sentence(tl, rh[1], ni) for rh in route):
                neg = ("ikke", ni, ni + 4)
                break

    fired = []
    noun_c = {c["clause"] for c in cands}

    if any(not c["inventory"] for c in cands):
        fired.append({"rule_id": "BC_ROUTE_UNKNOWN_SERVICE_01", "priority": 25,
                      "label": "ABSTAIN_CONFLICT", "span": None, "text": text})

    in_quote_cands = [c for c in cands if in_quote(c["start"])]
    if in_quote_cands and assertion:
        fired.append({"rule_id": "BC_ROUTE_QUOTE_CONFLICT_01", "priority": 65,
                      "label": "ABSTAIN_CONFLICT", "span": None, "text": text})
    if cands and quote:
        fired.append({"rule_id": "BC_ROUTE_QUOTED_01", "priority": 60,
                      "label": "QUOTED_ONLY", "span": _best(quote), "text": text})

    # retraction: with one candidate, a correction marker binds to it even
    # across the clause boundary (burned gold VR-R-01..04 pattern); mixed
    # outputs are resolved by the polarity guard below.
    if retraction and any(c["inventory"] for c in cands):
        fired.append({"rule_id": "BC_ROUTE_SELF_RETRACTED_01", "priority": 50,
                      "label": "SELF_RETRACTED", "span": _best(retraction), "text": text})

    if route and neg:
        neg_clause = clause_idx(neg[1])
        if not mixed or neg_clause in noun_c:
            fired.append({"rule_id": "BC_ROUTE_NEGATED_01", "priority": 40,
                          "label": "NEGATED", "span": neg, "text": text})

    if cands and cond:
        fired.append({"rule_id": "BC_ROUTE_HYPOTHETICAL_01", "priority": 30,
                      "label": "HYPOTHETICAL_ONLY", "span": _best(cond), "text": text})

    if cands and hedge:
        if not mixed or (op_clauses(hedge) & noun_c):
            fired.append({"rule_id": "BC_ROUTE_HEDGED_01", "priority": 20,
                          "label": "HEDGED_ASSERTION", "span": _best(hedge), "text": text})

    if cands and assertion:
        if not mixed or (op_clauses(assertion) & noun_c):
            fired.append({"rule_id": "BC_ROUTE_ASSERTED_01", "priority": 10,
                          "label": "ASSERTED", "span": _best(assertion), "text": text})

    if not cands and not fired and vague:
        fired.append({"rule_id": "BC_ROUTE_VAGUE_01", "priority": 5,
                      "label": "VAGUE_NONCOMMITTAL", "span": _best(vague), "text": text})

    if not cands and not fired:
        return _abstain("route_commitment", "NO_HIGH_PRECISION_RULE")

    # mixed-polarity guard: two clause-local commitment labels in one output
    # cannot collapse into a single deterministic polarity.
    if mixed:
        commitment = {f["label"] for f in fired if f["label"] in
                      ("ASSERTED", "HEDGED_ASSERTION", "NEGATED", "SELF_RETRACTED",
                       "HYPOTHETICAL_ONLY")}
        if len(commitment) > 1:
            return _abstain("route_commitment", "MIXED_POLARITY_CONFLICT",
                            rule_id="BC_ROUTE_MIXED_POLARITY_03",
                            conflict=[{"label": l} for l in sorted(commitment)])

    return _resolve("route_commitment", fired)


def _quote_spans(tl, quote):
    """Crude quote span detection using guillemets."""
    spans = []
    open_pos = None
    for i, ch in enumerate(tl):
        if ch == "\u00ab":
            open_pos = i
        elif ch == "\u00bb" and open_pos is not None:
            spans.append((open_pos, i + 1))
            open_pos = None
    return spans


def _uncertainty_rules(text, criterion):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return _abstain("uncertainty_behavior", "NO_HIGH_PRECISION_RULE")
    lim = _hits(tl, LIMITATION_MARKERS)
    cert = _hits(tl, CERTAINTY_MARKERS)
    part = _hits(tl, PARTITIVE_MARKERS)
    verified = _hits(tl, VERIFIED_PART_MARKERS)
    hedge = _hits(tl, HEDGE_MARKERS)
    cond = _hits(tl, CONDITIONAL_UNC_MARKERS)
    req = bool(criterion and criterion.get("required_limitations"))
    fired = []
    if lim and cert:
        fired.append({"rule_id": "UNC_CONTRADICTORY_01", "priority": 50,
                      "label": "CONTRADICTORY_LIMITATION", "span": _best(cert), "text": text})
    if lim and (part or ("men" in tl and verified)):
        fired.append({"rule_id": "UNC_PARTIAL_01", "priority": 45,
                      "label": "PARTIAL_LIMITATION", "span": _best(lim), "text": text})
    if lim:
        fired.append({"rule_id": "UNC_EXPLICIT_01", "priority": 40,
                      "label": "EXPLICIT_LIMITATION", "span": _best(lim), "text": text})
    if req and not lim and not hedge and not cond:
        fired.append({"rule_id": "UNC_OVERCONFIDENT_01", "priority": 35,
                      "label": "OVERCONFIDENT_ASSERTION", "span": None, "text": text})
    if hedge:
        fired.append({"rule_id": "UNC_HEDGE_01", "priority": 30,
                      "label": "HEDGE", "span": _best(hedge), "text": text})
    if not lim and not hedge and not cond and not req:
        fired.append({"rule_id": "UNC_NONE_01", "priority": 10,
                      "label": "NONE", "span": None, "text": text})
    out = _resolve("uncertainty_behavior", fired)
    if not out["abstained"] and out["label"] == "OVERCONFIDENT_ASSERTION":
        out["evidence_span"] = text
    if not out["abstained"] and out["label"] == "NONE":
        out["evidence_span"] = text
    return out


def _scope_rules(text, criterion):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return _abstain("assertion_scope", "NO_HIGH_PRECISION_RULE")
    retraction = _hits(tl, RETRACTION_MARKERS)
    negcond = _hits(tl, SCOPE_NEGATION_MARKERS)
    userattr = _hits(tl, USER_ATTRIBUTION_MARKERS)
    thirdattr = _hits(tl, THIRD_PARTY_ATTRIBUTION_MARKERS)
    condscope = _hits(tl, SCOPE_CONDITIONAL_MARKERS)
    endorse = _hits(tl, SYSTEM_ENDORSEMENT_MARKERS)
    fired = []
    if retraction:
        fired.append({"rule_id": "BC_SCOPE_RETRACTED_01", "priority": 55,
                      "label": "RETRACTED", "span": _best(retraction), "text": text})
    if negcond:
        fired.append({"rule_id": "BC_SCOPE_NEGATED_01", "priority": 50,
                      "label": "NEGATED", "span": _best(negcond), "text": text})
    if userattr:
        fired.append({"rule_id": "BC_SCOPE_USER_REPORTED_01", "priority": 41,
                      "label": "USER_REPORTED", "span": _best(userattr), "text": text})
    if thirdattr:
        fired.append({"rule_id": "BC_SCOPE_THIRD_PARTY_01", "priority": 40,
                      "label": "THIRD_PARTY_QUOTED", "span": _best(thirdattr), "text": text})
    if condscope:
        fired.append({"rule_id": "BC_SCOPE_HYPOTHETICAL_01", "priority": 30,
                      "label": "HYPOTHETICAL", "span": _best(condscope), "text": text})
    if endorse:
        neg_hits = [(m.group(), m.start(), m.end()) for m in re.finditer("ikke", tl)]
        endorsed_negated = False
        for m, s, e in endorse:
            hit = next((h for h in neg_hits
                        if not any(c in tl[min(h[1], s):max(h[2], e)] for c in ".!?")), None)
            if hit:
                fired.append({"rule_id": "BC_SCOPE_NEGATED_02", "priority": 50,
                              "label": "NEGATED", "span": hit, "text": text})
                endorsed_negated = True
                break
        if not endorsed_negated:
            fired.append({"rule_id": "BC_SCOPE_SYSTEM_ENDORSED_01", "priority": 20,
                          "label": "SYSTEM_ENDORSED", "span": _best(endorse), "text": text})
    return _resolve("assertion_scope", fired)


def classify(text, criterion=None):
    return {
        "route_commitment": _route_rules(text, criterion),
        "uncertainty_behavior": _uncertainty_rules(text, criterion),
        "assertion_scope": _scope_rules(text, criterion),
    }
