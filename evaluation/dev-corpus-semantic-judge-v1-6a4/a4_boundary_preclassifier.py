#!/usr/bin/env python3
"""V1.6A.4 assertion-strength layer on top of the frozen V1.6A.3 engine.

Adds ONLY the forbidden_claim dimension. A1/A2/A3 behavior is inherited
untouched. Precision-first: ambiguous commitment binding -> ABSTAIN.
"""

import re

import boundary_preclassifier as a3

FIRST_PERSON_BELIEF_MARKERS = ["jeg mener", "vi mener", "jeg tror",
                               "jeg antar", "jeg regner med",
                               "vi antar", "er overbevist"]
BELIEF_STEM_RE = re.compile(r"\b(mener|tror|antar|regner med)\b")
CONSEQUENT_MARKERS = ["vil det si at", "det vil si", "betyr at", "bety at"]
META_NEG_NEXT = " om "

CLAIM_PRIORITY = {"NEGATED": 50, "HYPOTHETICAL_ONLY": 40,
                  "REPORTED_ATTRIBUTED": 30, "HEDGED_ASSERTION": 20,
                  "ASSERTED": 10}


def _overlap(a, b):
    return a[1] < b[2] and b[1] < a[2]


def _forbidden_rules(text, criterion):
    tl = text.lower()
    if text.rstrip().endswith("?"):
        return a3._abstain("forbidden_claim", "NO_HIGH_PRECISION_RULE")

    terms = [t.lower() for t in (criterion or {}).get("prohibited_claim_terms") or []]
    claims = a3._hits(tl, terms) if terms else []

    if not claims:
        out = {
            "dimension": "forbidden_claim", "label": "NOT_PRESENT",
            "rule_id": "BC_CLAIM_ABSENCE_01",
            "evidence_span": None, "evidence_basis":
                "ABSENCE_OF_PROHIBITED_ASSERTION",
            "deterministic": True, "abstained": False,
            "confidence": "DETERMINISTIC_HIGH",
        }
        vague = a3._hits(tl, a3.VAGUE_MARKERS)
        if vague:
            out["label"] = "VAGUE_NONCOMMITTAL"
            out["rule_id"] = "BC_CLAIM_VAGUE_02"
            out["evidence_span"] = a3._span_text(text, a3._best(vague))
            out["evidence_basis"] = "TEXT_SPAN"
        return out

    clauses = a3._clauses(tl)

    def clause_idx(pos):
        for i, (s, e) in enumerate(clauses):
            if s <= pos < e:
                return i
        return -1

    qspans = a3._quote_spans(tl, a3._hits(tl, a3.QUOTE_MARKERS))

    def in_quote(pos):
        return any(s <= pos < e for s, e in qspans)

    quote_end = max((e for _, e in qspans), default=None)

    retraction = a3._hits(tl, a3.RETRACTION_MARKERS)
    if retraction:
        return {
            "dimension": "forbidden_claim", "label": "SELF_RETRACTED",
            "rule_id": "BC_CLAIM_SELF_RETRACTED_01",
            "evidence_span": a3._span_text(text, a3._best(retraction)),
            "evidence_basis": "TEXT_SPAN", "deterministic": True,
            "abstained": False, "confidence": "DETERMINISTIC_HIGH",
        }

    # quoted claim surface: QUOTED_ONLY unless an out-of-quote adoption
    # operator follows the quote end (then scope cannot be adjudicated).
    if any(in_quote(c[1]) for c in claims):
        after = [h for h in (a3._hits(tl, FIRST_PERSON_BELIEF_MARKERS)
                             + a3._hits(tl, a3.ADOPTION_MARKERS))
                 if quote_end is not None and h[1] >= quote_end]
        if after:
            return a3._abstain("forbidden_claim", "QUOTE_SCOPE_AMBIGUITY",
                               rule_id="BC_CLAIM_QUOTE_SCOPE_03")
        return {
            "dimension": "forbidden_claim", "label": "QUOTED_ONLY",
            "rule_id": "BC_CLAIM_QUOTED_04",
            "evidence_span": a3._span_text(text, a3._best(claims)),
            "evidence_basis": "TEXT_SPAN", "deterministic": True,
            "abstained": False, "confidence": "DETERMINISTIC_HIGH",
        }

    neg_hits = [(m.group(), m.start(), m.end()) for m in re.finditer("ikke", tl)]
    hedge = a3._hits(tl, a3.HEDGE_MARKERS)
    cond = a3._hits(tl, a3.CONDITIONAL_ROUTE_MARKERS)
    consequent = a3._hits(tl, CONSEQUENT_MARKERS)
    third = a3._hits(tl, a3.THIRD_PARTY_ATTRIBUTION_MARKERS)
    fp_belief = a3._hits(tl, FIRST_PERSON_BELIEF_MARKERS)

    frames = set()
    for term, cs, ce in claims:
        ci = clause_idx(cs)
        # meta-linguistic negation ("ikke om X"): the claim is mentioned,
        # not asserted -> mechanically unresolvable here.
        for _, ns, ne in neg_hits:
            if clause_idx(ns) == ci and tl[ne:ne + 4] == META_NEG_NEXT:
                return a3._abstain("forbidden_claim",
                                   "META_NEGATION_SCOPE_AMBIGUITY",
                                   rule_id="BC_CLAIM_META_SCOPE_05")
        frame = None
        # A4-N1: negation inside a first-person belief clause flips polarity.
        if any(clause_idx(h[1]) == ci for h in fp_belief) \
                and any(clause_idx(h[1]) == ci for h in neg_hits):
            frame = "NEGATED"
        else:
            for _, ns, _ne in neg_hits:
                if clause_idx(ns) != ci:
                    continue
                if any(_overlap((_, ns, _ne), (t, s, e))
                       for t, s, e in claims):
                    continue  # negation is part of the claim surface itself
                if any(clause_idx(h[1]) == ci and h[1] < ns
                       for h in cond):
                    continue  # A3-G5: conditional-scoped antecedent negation
                frame = "NEGATED"
                break
        if frame is None:
            if any(clause_idx(h[1]) == ci for h in hedge):
                frame = "HEDGED_ASSERTION"
            elif any(clause_idx(h[1]) == ci for h in third):
                frame = "REPORTED_ATTRIBUTED"
            elif any(clause_idx(h[1]) == ci for h in fp_belief):
                frame = "ASSERTED"
            elif BELIEF_STEM_RE.search(tl) and not fp_belief:
                frame = "REPORTED_ATTRIBUTED"  # bare belief verb = attributed
            elif any(clause_idx(h[1]) == ci for h in cond):
                # F-23 consequent assertion: claim after a consequent marker
                # that itself follows the conditional is an assertion.
                cpos = next((h[1] for h in cond if clause_idx(h[1]) == ci), None)
                bpos = next((h[1] for h in consequent
                             if cpos is not None and h[1] > cpos), None)
                if bpos is not None and cs > bpos:
                    frame = "ASSERTED"
                else:
                    frame = "HYPOTHETICAL_ONLY"
            else:
                frame = "ASSERTED"
        frames.add(frame)

    if len(frames) > 1:
        return a3._abstain("forbidden_claim", "MIXED_CLAIM_FRAMES",
                           rule_id="BC_CLAIM_MIXED_FRAMES_06",
                           conflict=[{"label": f} for f in sorted(frames)])

    frame = frames.pop()
    best = a3._best(claims)
    return {
        "dimension": "forbidden_claim", "label": frame,
        "rule_id": "BC_CLAIM_FRAME_07",
        "evidence_span": a3._span_text(text, best),
        "evidence_basis": "TEXT_SPAN", "deterministic": True,
        "abstained": False, "confidence": "DETERMINISTIC_HIGH",
        "priority": CLAIM_PRIORITY[frame],
    }


def classify(text, criterion=None):
    out = a3.classify(text, criterion)
    out["forbidden_claim"] = _forbidden_rules(text, criterion)
    return out

