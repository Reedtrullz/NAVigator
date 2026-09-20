"""RC3 proof-bound engine wrapper (PROOF_ENGINE_RC3).

Wraps the frozen RC2 deterministic engine (never modified) and adds a
post-support clause-context guard so that polarity/modality flips living
outside the aligned fragment cannot produce an auto-SUPPORTED proof.
The guard is conservative: it downgrades to ENGINE_UNSAFE and routes to
review. It never flips polarity on absence (no absence-is-contradiction).
"""
import re
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent.parent / "rc2-development" / "engine"
sys.path.insert(0, str(_ENGINE_DIR))
import polarity_engine_v02 as frozen  # noqa: E402

PROOF_STATES = (
    "ENGINE_PROOF_ACCEPTED",
    "ENGINE_NO_PROOF",
    "ENGINE_CONFLICT",
    "ENGINE_UNSAFE",
)

_NEGATION_RE = re.compile(
    r"\b(ikke|ingen|aldri|uten|verken|ikke lenger)\b")
_DEONTIC_MUST_RE = re.compile(r"\b(sk(al|a)l|ma(s|a|atte)|krever|pliktig)\b")
_DEONTIC_MAY_RE = re.compile(r"\b(kan|velge|frivillig|mulig|anbefal)\b")
_EXCEPTION_RE = re.compile(
    r"\b(unntak|bare dersom|kun dersom|sofremt|hvis|dersom|medmindre)\b")
_HOVEDREGEL_RE = re.compile(r"\b(som hovedregel|normalt|vanligvis|usually)\b")

_NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")
_STOP_TOKENS = {
    "og", "eller", "som", "det", "den", "for", "med", "til",
    "fra", "ved", "om", "er", "har", "blir", "kan", "skal",
    "at", "de", "dem", "en", "ei", "et", "paa", "pa", "i", "av",
    "maa", "bor", "the", "ikke", "ingen", "aldri", "uten",
}


def _fold(text):
    return text.lower()


def _subject_overlap(a, b):
    """Loose subject/topic overlap: shared 6-char token stem."""
    stop = {"og", "eller", "som", "det", "den", "for", "med", "til",
            "fra", "ved", "om", "er", "har", "blir", "kan", "skal"}
    ta = {t[:6] for t in re.findall(r"[a-z\xe6\xf8\xe5]{5,}", _fold(a))
          if t not in stop}
    tb = {t[:6] for t in re.findall(r"[a-z\xe6\xf8\xe5]{5,}", _fold(b))
          if t not in stop}
    return bool(ta & tb)


def _polarity_markers(text):
    """Classify generalized polarity/modality markers in text."""
    f = _fold(text)
    markers = []
    if _NEGATION_RE.search(f):
        markers.append("NEGATION")
    if _DEONTIC_MUST_RE.search(f):
        markers.append("DEONTIC_MUST")
    if _DEONTIC_MAY_RE.search(f):
        markers.append("DEONTIC_MAY")
    if _EXCEPTION_RE.search(f):
        markers.append("EXCEPTION_SCOPE")
    if _HOVEDREGEL_RE.search(f):
        markers.append("QUALIFIER_HOVEDREGEL")
    return markers


def _marker_conflict(claim_markers, span_markers):
    """Polarity flip = negation on one side only outside aligned span.
    Deontic flip = must on one side + may on the other. Qualifier or
    exception markers alone trigger review, never contradiction."""
    a, b = set(claim_markers), set(span_markers)
    flip_neg = ("NEGATION" in a) != ("NEGATION" in b)
    flip_must_may = (
        ("DEONTIC_MUST" in a and "DEONTIC_MAY" in b) or
        ("DEONTIC_MAY" in a and "DEONTIC_MUST" in b))
    qualifier_outside = (
        ("EXCEPTION_SCOPE" in b or "QUALIFIER_HOVEDREGEL" in b)
        and "NEGATION" not in b)
    if flip_neg or flip_must_may:
        return "POLARITY_OR_MODALITY_FLIP_OUTSIDE_SPAN"
    if qualifier_outside:
        return "QUALIFIER_OR_EXCEPTION_OUTSIDE_SPAN"
    return None


def _numeric_conflict(claim_text, span_text):
    """Every number in the claim must appear in the aligned span; a
    mismatched number inside a support span cannot be auto (full-
    clause binding, spec 15)."""
    cn = _NUM_RE.findall(_fold(claim_text))
    sn = set(_NUM_RE.findall(_fold(span_text)))
    if not cn:
        return False
    return any(n not in sn for n in cn)


def _key_token_coverage(claim_text, span_text):
    """Support span must cover most claim content tokens; a fragment
    that drops the claim's key predicate is not the same proposition.
    Conservative threshold 0.6, fail closed to review."""
    # ponytail: stem-less overlap heuristic; upgrade to dependency
    # parsing if review rate gets too high.
    ctoks = {t for t in re.findall(r"[a-z\xe6\xf8\xe5]{5,}",
                                 _fold(claim_text))
             if t not in _STOP_TOKENS}
    stoks = {t[:5] for t in re.findall(r"[a-z\xe6\xf8\xe5]{5,}",
                                      _fold(span_text))}
    if len(ctoks) < 2:
        return True
    covered = sum(1 for t in ctoks if t[:5] in stoks)
    return covered / len(ctoks) >= 0.6


def clause_context_guard(claim_text, source_text, proof):
    """Full-clause binding check (spec 15-16): after the frozen engine
    finds an aligned support span, scan the aligned sentence plus the
    adjacent sentence when subjects overlap. Return None when clean or
    a (reason_code, detail) tuple when a flip lives outside the span."""
    if not proof or proof.get("proof_type") != "SUPPORT":
        return None
    span_text = proof.get("source_span", "")
    if not span_text:
        return None
    claim_markers = _polarity_markers(claim_text)
    sentences = frozen.pe.split_sentences(source_text)
    if not sentences:
        return None
    idx = None
    for i, s in enumerate(sentences):
        if _fold(span_text)[:60] and _fold(span_text)[:60] in _fold(s):
            idx = i
            break
    if idx is None:
        return None
    # Adjacent-sentence extension only with subject overlap (clause
    # boundary preference over raw +/-N token window, spec 16).
    adjacent = []
    if idx + 1 < len(sentences) and _subject_overlap(
            sentences[idx], sentences[idx + 1]):
        adjacent.append(sentences[idx + 1])
    if idx > 0 and _subject_overlap(sentences[idx], sentences[idx - 1]):
        adjacent.append(sentences[idx - 1])
    aligned_markers = _polarity_markers(sentences[idx])
    conflict = _marker_conflict(claim_markers, aligned_markers)
    if conflict:
        return (conflict, "aligned sentence carries flip markers")
    outside = " ".join(adjacent)
    if outside:
        conflict = _marker_conflict(claim_markers,
                                    _polarity_markers(outside))
        if conflict:
            return (conflict,
                    "adjacent clause with subject overlap carries flip "
                    "markers outside aligned span")
    return None


def judge_atom(claim_text, source_text):
    """Judge one atom through the frozen engine, then the RC3 guard.
    Returns a proof-state object (spec 7 authority model)."""
    base = frozen.decide_atom_v02(claim_text, source_text)
    out = {
        "claim": claim_text,
        "frozen_verdict": base["verdict"],
        "frozen_rule": base["rule"],
        "frozen_confidence": base["confidence"],
        "frozen_review": base.get("review", False),
        "proof": base.get("proof"),
        "guard": None,
    }
    if base["verdict"] == "SUPPORTED" and base.get("rule") == \
            "support_from_quote_alignment":
        conflict = clause_context_guard(claim_text, source_text,
                                        base.get("proof"))
        if conflict:
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": conflict[0],
                "reason_detail": conflict[1],
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out

    # Proof-bound guards for ALL SUPPORT verdicts regardless of the
    # frozen rule that produced them (spec 35: same atom, correct
    # scope, correct polarity).
    if base["verdict"] == "SUPPORTED":
        span_text = (base.get("proof") or {}).get("source_span", "")
        if _numeric_conflict(claim_text, span_text):
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": "NUMERIC_MISMATCH_IN_SPAN",
                "reason_detail": "claim number missing from aligned "
                                 "support span",
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out
        if not _key_token_coverage(claim_text, span_text):
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": "KEY_TOKEN_COVERAGE_LOW",
                "reason_detail": "aligned span misses claim key "
                                 "tokens",
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out
    # Positive proof obligation for contradiction (spec 13): a rule-
    # derived exclusion contradiction needs an explicit exhaustivity
    # marker in the source; absence from a list is not exclusion.
    if base["verdict"] == "CONTRADICTED" and base.get("rule") in (
            "exhaustive_list_exclusion", "exhaustive_eller_exclusion"):
        if not re.search(
                r"\b(bare|kun|enten|eller ingen|ikke andre|kunne)\b",
                _fold(source_text)):
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": "EXHAUSTIVITY_NOT_STATED",
                "reason_detail": "exclusion contradiction without "
                                 "explicit exhaustivity marker",
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out
    # Every accepted contradiction needs a positive proof object with
    # a concrete span or a deterministic comparator rule (spec 13).
    if base["verdict"] == "CONTRADICTED":
        p = base.get("proof") or {}
        if not p.get("source_span") and base.get("rule") not in (
                "numeric_conflict", "incompatible_dates",
                "neg_object_conflict", "exhaustive_list_exclusion",
                "exhaustive_eller_exclusion"):
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": "NO_POSITIVE_CONTRA_SPAN",
                "reason_detail": "contradiction without span or "
                                 "deterministic comparator",
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out
    if base["verdict"] == "CONTRADICTED":
        # A contradiction whose span carries 'som hovedregel'/exception
        # markers is not an absolute negation (spec 17): fail closed
        # to review instead of auto-flipping modality to polarity.
        span_text = (base.get("proof") or {}).get("source_span", "")
        span_markers = _polarity_markers(span_text)
        if ("QUALIFIER_HOVEDREGEL" in span_markers
                or "EXCEPTION_SCOPE" in span_markers):
            out.update({
                "proof_state": "ENGINE_UNSAFE",
                "reason_code": "QUALIFIER_IN_CONTRA_SPAN",
                "reason_detail": "contradiction span carries "
                                 "hovedregel/exception qualifier",
                "final_verdict": "REVIEW_REQUIRED",
                "review_required": True,
            })
            return out
    if base["verdict"] == "SUPPORTED":
        out.update({
            "proof_state": "ENGINE_PROOF_ACCEPTED",
            "final_verdict": "AUTO_SUPPORTED",
            "review_required": False,
        })
    elif base["verdict"] == "CONTRADICTED":
        out.update({
            "proof_state": "ENGINE_PROOF_ACCEPTED",
            "final_verdict": "AUTO_CONTRADICTED",
            "review_required": False,
        })
    else:
        out.update({
            "proof_state": "ENGINE_NO_PROOF",
            "final_verdict": "PENDING_ROUTE",
            "review_required": True,
        })
    return out


def judge_claim(claim_text, source_text):
    """Compound-aware judge: canonical decomposition, atom pipeline,
    deterministic top-level aggregation (DECOMPOSITION_V1)."""
    from decomposition import decompose_claim as canon_decompose
    from routing import aggregate_atoms
    atoms = canon_decompose(claim_text)
    atom_results = []
    for i, atom in enumerate(atoms):
        res = judge_atom(atom["text"], source_text)
        res["atom_id"] = atom["atom_id"]
        res["relation_to_parent"] = atom["relation_to_parent"]
        atom_results.append(res)
    top = aggregate_atoms(atom_results)
    return {
        "engine": "PROOF_ENGINE_RC3",
        "decomposition_version": "DECOMPOSITION_V1",
        "atoms": atom_results,
        "atom_count": len(atom_results),
        "final_verdict": top["product_action"],
        "review_required": top["product_action"] in
        ("REVIEW_REQUIRED", "PENDING_ROUTE"),
        "abstain_insufficient": top["product_action"] ==
        "ABSTAIN_INSUFFICIENT",
    }
