"""Frozen RC3 routing table (PRODUCT_ROUTING_V2) and deterministic
review-vs-abstain classifier (spec 10-12, 28).

Routing is proof-bounded: reviewer confidence alone can never produce an
auto action. Absence of support is never contradiction (spec 13).
"""
import re

SUFFICIENCY_CLASSES = (
    "EVIDENCE_SUFFICIENT_FOR_PROOF",
    "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
    "EVIDENCE_GENUINELY_INSUFFICIENT",
)

PRODUCT_ACTIONS = (
    "AUTO_SUPPORTED",
    "AUTO_CONTRADICTED",
    "PARTIALLY_SUPPORTED",
    "REVIEW_REQUIRED",
    "ABSTAIN_INSUFFICIENT",
)

# FROZEN ROUTING TABLE (spec 10). No confidence thresholds.
ROUTING_TABLE = {
    ("ENGINE_PROOF_ACCEPTED", "SUPPORTED"): "AUTO_SUPPORTED",
    ("ENGINE_PROOF_ACCEPTED", "CONTRADICTED"): "AUTO_CONTRADICTED",
    ("ENGINE_UNSAFE",): "REVIEW_REQUIRED",
    ("ENGINE_CONFLICT",): "REVIEW_REQUIRED",
    ("ENGINE_NO_PROOF",): "CLASSIFY_SUFFICIENCY",
}

_STOP = {
    "og", "eller", "som", "det", "den", "for", "med", "til", "fra",
    "ved", "om", "er", "har", "blir", "kan", "skal", "maa", "at",
    "de", "dem", "en", "ei", "et", "paa", "pa", "i", "av", "til",
}


def _content_tokens(text):
    # 3-char minimum keeps short acronyms (PPT, BUP) usable; higher
    # relevance sensitivity is fail-closed (REVIEW, never auto).
    return [t for t in re.findall(r"[a-z\xe6\xf8\xe5]{3,}", text.lower())
            if t not in _STOP]


def classify_sufficiency(claim_text, source_text):
    """Deterministic evidence-sufficiency classifier (spec 28).
    Relevance = shared claim/source content token. Relevant evidence
    that fails to yield a proof routes to review; no relevant evidence
    routes to abstain. Never produces auto without a proof object."""
    claim_toks = set(_content_tokens(claim_text))
    source_toks = set(_content_tokens(source_text))
    shared = claim_toks & source_toks
    if shared:
        return ("EVIDENCE_RELEVANT_BUT_UNRESOLVED", sorted(shared)[:3])
    return ("EVIDENCE_GENUINELY_INSUFFICIENT", [])


def route_atom(atom_result, claim_text="", source_text=""):
    """Frozen routing table application for one atom."""
    state = atom_result.get("proof_state")
    if state == "ENGINE_NO_PROOF":
        cls, _ = classify_sufficiency(claim_text, source_text)
        if cls == "EVIDENCE_GENUINELY_INSUFFICIENT":
            return "ABSTAIN_INSUFFICIENT"
        return "REVIEW_REQUIRED"
    return ROUTING_TABLE[(state,)] if (state,) in ROUTING_TABLE \
        else ROUTING_TABLE[(state, atom_result["frozen_verdict"])]


def aggregate_atoms(atom_results):
    """Deterministic top-level aggregation from atom product routes.
    Review dominates; abstain only when every unresolved atom is
    genuinely insufficient; mixed auto is PARTIALLY_SUPPORTED."""
    routes = []
    for a in atom_results:
        if "route" not in a:
            a = dict(a)
        routes.append(a)
    # Route each atom if not already routed.
    routed = []
    for a in atom_results:
        if a.get("route"):
            routed.append(a["route"])
        else:
            r = a.get("final_verdict")
            routed.append(r)
    if any(r in ("REVIEW_REQUIRED", "PENDING_ROUTE") for r in routed):
        return {"product_action": "REVIEW_REQUIRED"}
    if all(r == "ABSTAIN_INSUFFICIENT" for r in routed):
        return {"product_action": "ABSTAIN_INSUFFICIENT"}
    n_sup = routed.count("AUTO_SUPPORTED")
    n_con = routed.count("AUTO_CONTRADICTED")
    # Any auto plus any abstain: claim only partially determined,
    # consistent with frozen RC2 aggregation contract.
    if (n_sup or n_con) and "ABSTAIN_INSUFFICIENT" in routed:
        return {"product_action": "PARTIALLY_SUPPORTED"}
    if n_sup and n_con:
        return {"product_action": "PARTIALLY_SUPPORTED"}
    if n_con:
        return {"product_action": "AUTO_CONTRADICTED"}
    if n_sup:
        return {"product_action": "AUTO_SUPPORTED"}
    # Unreachable with current routes, kept fail-closed.
    return {"product_action": "REVIEW_REQUIRED"}
