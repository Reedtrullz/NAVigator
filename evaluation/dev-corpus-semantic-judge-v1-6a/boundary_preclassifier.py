#!/usr/bin/env python3
"""V1.6A deterministic boundary pre-classifier (model-free, precision-first)."""

import re

ROUTE_TERMS = [
    "psykisk helsetjeneste", "psykiske helsetjeneste",
    "rask psykisk helsehjelp", "fastlege",
    "helsestasjon", "skolehelsetjeneste", "familievernkontor",
    "helsesykepleier", "familieteam", "barnevern", "kommunepsykolog",
    "hfu", "bup", "rph", "ppt", "habu", "dps",
]
QUOTE_MARKERS = ["«", "»", "sier:", "sier at", "skriver at",
                 "oppgir:", "oppgir at", "ifølge"]
QUOTE_MARKERS += ["rapporterer at", "opplyser at"]
ADOPTION_MARKERS = ["anbefaler", "anbefale", "riktig sted", "riktig inngang",
                    "bør kontakte", "bør kontaktes"]
RETRACTION_MARKERS = ["trekker tilbake", "korrigere meg",
                      "jeg kan ikke stå inne for",
                      "kan jeg ikke stå inne for",
                      "det stemmer ikke", "nei,"]
NEGATION_MARKERS = ["ikke"]
CONDITIONAL_ROUTE_MARKERS = ["hvis", "dersom", "i tilfeller der",
                             "kunne være", "være en mulighet",
                             "vurderes"]
HEDGE_MARKERS = ["ser ut til", "trolig", "sannsynligvis", "antakelig",
                 "kanskje", "muligens", "kan tenkes"]
HEDGE_MARKERS += ["ser ut som", "det er mulig"]
ASSERTION_MARKERS = ["riktig sted", "riktig inngang", "riktig rute",
                     "riktig første kontakt", "bør kontakte",
                     "bør kontaktes", "kan kontaktes", "kan kontakte",
                     "henvise", "henvis", "anbefaler", "anbefale"]
VAGUE_MARKERS = ["hjelp", "hjelpe", "støtte", "muligheter"]

LIMITATION_MARKERS = ["ikke kunnet verifisere", "ikke verifisert",
                      "mangler informasjon", "mangler fortsatt informasjon",
                      "kunne ikke bekrefte", "uavklart", "ikke sjekket",
                      "ikke har kunnet"]
LIMITATION_MARKERS += ["vet ikke", "mangler oversikt"]
PARTITIVE_MARKERS = ["én av", "en av"]
CERTAINTY_MARKERS = ["helt sikkert", "garanterer", "garantert", "utvetydig"]
CERTAINTY_MARKERS += ["er helt sikker", "er sikker på"]
VERIFIED_PART_MARKERS = ["har verifisert", "kan bekrefte"]
VERIFIED_PART_MARKERS += ["er bekreftet", "er verifisert"]
CONDITIONAL_UNC_MARKERS = ["hvis", "dersom"]

SCOPE_NEGATION_MARKERS = ["kan ikke fastslå", "ikke påvist",
                          "ikke foreligger"]
SCOPE_NEGATION_MARKERS += ["kan ikke bekrefte"]
USER_ATTRIBUTION_MARKERS = ["du sier", "du forteller", "du oppgir"]
USER_ATTRIBUTION_MARKERS += ["du beskriver"]
THIRD_PARTY_ATTRIBUTION_MARKERS = ["sier at", "oppgir at", "skriver at",
                                   "ifølge"]
THIRD_PARTY_ATTRIBUTION_MARKERS += ["rapporterer at", "opplyser at"]
SCOPE_CONDITIONAL_MARKERS = ["hvis", "dersom", "i noen tilfeller",
                             "kan i noen tilfeller", "oppstå",
                             "kunne oppstå"]
SYSTEM_ENDORSEMENT_MARKERS = ["er i akutt fare", "foreligger",
                              "viser tegn på"]


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


def _has_any(text_lower, markers):
    return any(m in text_lower for m in markers)


def _same_sentence(text_lower, a, b):
    lo, hi = sorted((a, b))
    return not any(c in text_lower[lo:hi] for c in ".!?")


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
    quote = _hits(tl, QUOTE_MARKERS)
    adopt = _hits(tl, ADOPTION_MARKERS)
    retraction = _hits(tl, RETRACTION_MARKERS)
    hedge = _hits(tl, HEDGE_MARKERS)
    cond = _hits(tl, CONDITIONAL_ROUTE_MARKERS)
    vague = _hits(tl, VAGUE_MARKERS)
    neg = None
    if route:
        for ni in (m.start() for m in re.finditer("ikke", tl)):
            if any(_same_sentence(tl, rh[1], ni) for rh in route):
                neg = ("ikke", ni, ni + 4)
                break
    fired = []
    if route and quote and adopt:
        fired.append({"rule_id": "BC_ROUTE_QUOTE_CONFLICT_01", "priority": 65,
                      "label": "ABSTAIN_CONFLICT", "span": None, "text": text})
    if route and quote:
        fired.append({"rule_id": "BC_ROUTE_QUOTED_01", "priority": 60,
                      "label": "QUOTED_ONLY", "span": _best(quote), "text": text})
    if route and retraction:
        fired.append({"rule_id": "BC_ROUTE_SELF_RETRACTED_01", "priority": 50,
                      "label": "SELF_RETRACTED", "span": _best(retraction), "text": text})
    if route and neg:
        fired.append({"rule_id": "BC_ROUTE_NEGATED_01", "priority": 40,
                      "label": "NEGATED", "span": neg, "text": text})
    if route and cond:
        fired.append({"rule_id": "BC_ROUTE_HYPOTHETICAL_01", "priority": 30,
                      "label": "HYPOTHETICAL_ONLY", "span": _best(cond), "text": text})
    if route and hedge:
        fired.append({"rule_id": "BC_ROUTE_HEDGED_01", "priority": 20,
                      "label": "HEDGED_ASSERTION", "span": _best(hedge), "text": text})
    if route:
        assertion = _hits(tl, ASSERTION_MARKERS)
        if assertion:
            fired.append({"rule_id": "BC_ROUTE_ASSERTED_01", "priority": 10,
                          "label": "ASSERTED", "span": _best(assertion), "text": text})
    if not route and vague:
        fired.append({"rule_id": "BC_ROUTE_VAGUE_01", "priority": 5,
                      "label": "VAGUE_NONCOMMITTAL", "span": _best(vague), "text": text})
    return _resolve("route_commitment", fired)


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
