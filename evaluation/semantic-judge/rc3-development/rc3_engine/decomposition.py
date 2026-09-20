"""Canonical claim decomposition (DECOMPOSITION_V1).

Claim-logical only: split conjunctions, conditions, and temporal stages
by the claim's own structure, never by evidence availability or expected
labels. Deterministic and stable by construction.
"""
import re

CONDITION_RE = re.compile(
    r"\b(dersom|hvis|sa lenge som|forutsatt at|gitt at|fordi|siden)\b")
TEMPORAL_RE = re.compile(
    r"\b(etter at|innen|foer|f\u00f8r|nar|n\u00e5r|fra og med)\b")
MEN_RE = re.compile(r"\b(men|mens)\b")
OG_SPLIT = " og "

_VERB_MARKERS = {
    "er", "har", "far", "f\u00e5r", "kan", "skal", "ma", "m\u00e5",
    "bor", "b\u00f8r", "gjelder", "krever", "kreves", "gir", "gis",
    "tas", "ta", "sendes", "sokes", "s\u00f8kes", "behandles",
    "vurderes", "regnes", "teller", "finnes", "omfatter", "dekker",
    "heter", "mottes", "m\u00f8tes", "gjennomfores",
    "gjennomf\u00f8res", "gjelder", "plikter", "rett", "krav",
    "plikt", "adgang", "rettighet", "retten", "kravet",
    "henviser", "henvises", "utreder", "utredes", "iverksetter",
    "iverksettes", "kommer", "deltar", "melder", "vurderer",
    "sender", "behandler", "koordinerer", "tilbyr", "skriver",
    "vekter", "mottar", "gransker", "stotter", "opphor", "trenger",
    "skjer", "soke", "vedlegge", "tar", "regnes", "gjes",
    "fornyes", "trekkes", "telles", "avsluttes", "folerer",
    "fastslaar", "fastsl\u00e5r", "folger", "fastsetter", "sier",
    "mener", "viser", "beholder",
}


def _tokens(text):
    return re.findall(r"[a-z\xe6\xf8\xe5]+", text.lower())


def _has_predicate(text):
    """Crude predicate test: a known verb-ish marker or passive -es."""
    for t in _tokens(text):
        if t in _VERB_MARKERS or (len(t) > 4 and t.endswith("es")):
            return True
    return False


def _independent_propositions(left, right):
    """Both halves must be a proposition (verb-ish). 'inntekt og
    formue' is noun coordination, not two propositions."""
    return _has_predicate(left) and _has_predicate(right)


def _split_og(clause):
    """Recursively split on ' og ' between independent propositions."""
    parts = [clause]
    # Try each ' og ' occurrence; longest-first stability: split at the
    # first position where both sides are propositions.
    idx = clause.find(OG_SPLIT)
    while idx != -1:
        left = clause[:idx].strip().rstrip(",")
        right = clause[idx + len(OG_SPLIT):].strip()
        if left and right and _independent_propositions(left, right):
            out = []
            for half in (left, right):
                out.extend(_split_og(half))
            return out
        idx = clause.find(OG_SPLIT, idx + 1)
    return [clause.strip()]


def decompose_claim(claim_text):
    """Return ordered canonical atoms with stable IDs (spec 19-21)."""
    claim_text = claim_text.strip().rstrip(".").strip()
    if not claim_text:
        return [{"atom_id": "A1", "text": "",
                 "relation_to_parent": "CONJUNCT"}]
    # Contrastive 'men' binds two independent propositions.
    men_parts = MEN_RE.split(claim_text, maxsplit=1)
    if len(men_parts) == 2 and all(
            _has_predicate(p) for p in men_parts):
        clauses = men_parts
    else:
        clauses = [claim_text]
    atoms = []
    for clause in clauses:
        # Condition clause: leading condition + main clause.
        m = CONDITION_RE.search(clause)
        if m:
            head = clause[:m.start()].strip().rstrip(",").strip()
            tail = clause[m.end():].strip()
            if head and tail and _has_predicate(head) \
                    and _has_predicate(tail):
                atoms.append(("CONDITION", tail))
                atoms.append(("CONDITION", head))
                continue
        # Temporal clause: leading temporal + main clause.
        m = TEMPORAL_RE.search(clause)
        if m:
            head = clause[:m.start()].strip().rstrip(",").strip()
            tail = clause[m.end():].strip()
            if head and tail and _has_predicate(head) \
                    and _has_predicate(tail):
                atoms.append(("TEMPORAL_STAGE", head))
                atoms.append(("TEMPORAL_STAGE", tail))
                continue
        for piece in _split_og(clause):
            atoms.append(("CONJUNCT", piece))
    if not atoms:
        atoms = [("CONJUNCT", claim_text)]
    return [
        {"atom_id": "A%d" % (i + 1), "text": t,
         "relation_to_parent": rel}
        for i, (rel, t) in enumerate(atoms)
    ]
