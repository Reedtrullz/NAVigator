"""Deterministic auto-accept gates for the hybrid layer.

Decides which quote-aligner v0.2 verdicts are strong enough to
auto-accept and which must route to semantic review.  Generic signals
only (atom count, rule family, alignment coverage) - no claim IDs.

Design evidence (results/auto-coverage.json, strict policy):
  - multi-atom auto decisions: 8 correct / 8 wrong -> gate all
  - support_lexical_rescue: 24 ok / 3 wrong -> gate (weakest support rule)
  - support proofs with >=2 uncovered content tokens: most SUP errors
  - exhaustive_list_exclusion + incompatible_dates contra: 8 ok / 6 wrong
  - neg_object_conflict / cost_axis contra misfires on paraphrase
  - numeric/temporal/age values inside SUPPORT claims: binding class
  - first-person locality + causal "fordi" claims: unsupported shapes
Hard-fact rules (numeric/temporal/safety/negation) stay auto per spec 8
when they fire as CONTRA with strong rules; weak contra rules route.
"""

import re

WEAK_CONTRA_RULES = {
    "exhaustive_list_exclusion", "incompatible_dates",
    "neg_object_conflict", "cost_axis_opposition",
}
WEAK_SUPPORT_RULES = {"support_lexical_rescue"}

FIRST_PERSON_LOCAL = re.compile(
    r"\b(min|mitt|v\u00e5r|vart)\s+kommun", re.IGNORECASE)
FIRST_PERSON_ANY = re.compile(r"\b(min|mitt|v\u00e5r|vart)\b", re.IGNORECASE)
CAUSAL = re.compile(r"\bfordi\b", re.IGNORECASE)
UNIVERSAL_RE = re.compile(r"\b(alltid|alle|ethvert|hver)\b", re.IGNORECASE)


def _rule_base(raw):
    m = re.search(r"[a-z_]{4,}", str(raw or ""))
    return m.group(0) if m else ""


def _best_candidate(atom_text, source_text):
    from quote_aligner import align_atom
    rep = align_atom(atom_text, source_text)
    if not rep["candidates"]:
        return None
    return rep["candidates"][0]


def gate_atom(atom, source_text):
    """Return review reason for one atom result, or None if auto-eligible."""
    rule = _rule_base(atom.get("rule"))
    verdict = atom.get("verdict")
    if verdict == "SUPPORTED":
        if rule in WEAK_SUPPORT_RULES:
            return "weak_support_rule:" + rule
        if UNIVERSAL_RE.search(atom.get("atom_text", "")):
            return "universal_quantifier_support"
        cand = _best_candidate(atom.get("atom_text", ""), source_text)
        if cand is None:
            return "support_without_candidate"
        from polarity_engine_v02 import _uncovered_core, strip_parens
        unc = len(_uncovered_core(atom.get("atom_text", ""),
                                  strip_parens(cand["sentence"])))
        if unc >= 2:
            return "support_undercovered:%d" % unc
        if unc == 1 and cand["score"] < 0.6:
            return "support_weak_span:score=%.2f" % cand["score"]
        return None
    if verdict == "CONTRADICTED" and rule in WEAK_CONTRA_RULES:
        return "weak_contra_rule:" + rule
    if verdict == "CONTRADICTED" and rule == "numeric_bound_conflict":
        from quote_aligner import extract_numbers
        if len(extract_numbers(atom.get("atom_text", ""))) >= 2:
            return "compound_numeric_conflict"
    if verdict == "CONTRADICTED" and str(atom.get("rule") or "").endswith(
            ":free_of_charge"):
        return "weak_contra_rule:concept_opposition:free_of_charge"
    return None


def auto_gate(claim_text, source_text, result):
    """Return review reason for the claim, or None to auto-accept.

    Only clean SUPPORTED/CONTRADICTED verdicts without review_required
    can pass; anything else already routes to review by policy.
    """
    if result.get("verdict") not in ("SUPPORTED", "CONTRADICTED"):
        return "not_a_proof:" + str(result.get("verdict"))
    if result.get("review_required"):
        return "engine_review_flag"
    atoms = result.get("atom_results") or result.get("atoms") or []
    if len(atoms) > 1:
        return "compound_claim"
    if result["verdict"] == "SUPPORTED":
        atom_texts = " ".join(str(a.get("atom_text") or a.get("text") or "")
                              for a in atoms)
        from quote_aligner import extract_numbers, extract_dates, extract_ages
        if (extract_numbers(atom_texts) or extract_dates(atom_texts)
                or extract_ages(atom_texts)):
            return "numeric_support_binding"
        if FIRST_PERSON_LOCAL.search(atom_texts) and not FIRST_PERSON_ANY.search(
                source_text or ""):
            return "first_person_locality_unverified"
        if CAUSAL.search(atom_texts):
            return "causal_claim"
    for atom in atoms:
        reason = gate_atom(atom, source_text)
        if reason:
            return reason
    return None


if __name__ == "__main__":
    # Self-check: a clean near-verbatim support passes; compound and
    # weak-rule shapes must route to review.
    import os
    import sys
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "quote-aligner", "v0.2"))
    sys.path.insert(0, os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    import polarity_engine_v02 as E
    src = "Lavterskel psykisk helsehjelp i kommunen krever henvisning fra fastlege."
    clean = E.judge_claim(
        "Kommunen krever henvisning til lavterskel psykisk helsehjelp.", src)
    assert auto_gate("x", src, clean) is None, auto_gate("x", src, clean)
    multi = E.judge_claim(
        "Kommunen krever henvisning fra fastlege. "
        "Henvisning er nodvendig.", src)
    assert auto_gate("x", src, multi) == "compound_claim"
    print("gates self-check OK")
