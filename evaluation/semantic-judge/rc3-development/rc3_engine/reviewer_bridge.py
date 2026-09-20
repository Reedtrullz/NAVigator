"""Bridge from frozen RC2 reviewer transport to RC3 REVIEWER_V2.

The frozen transport (gpt-5.6-luna, strict JSON, span-validated) is
reused unchanged. This module only adapts its verdict fields to the RC3
schema. RC3 arbitration treats the result as a proposal, never as an
authoritative final verdict (ARBITRATION_V2).
"""
import importlib
import json
import os
import sys

_RC2_HYBRID = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "..", "hybrid")
sys.path.insert(0, os.path.abspath(_RC2_HYBRID))


def _reviewer_module():
    if "rc2_reviewer" not in sys.modules:
        mod = importlib.import_module("reviewer")
        sys.modules["rc2_reviewer"] = mod
    return sys.modules["rc2_reviewer"]


RELATION_MAP = {
    "SUPPORTED": "SUPPORTED",
    "CONTRADICTED": "CONTRADICTED",
    "PARTIAL": "INSUFFICIENT_EVIDENCE",
    "INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
}


def _rc2_engine_result(claim_text, source_text, atom_result):
    """Adapter: frozen build_packet expects engine_result shape."""
    return {
        "verdict": atom_result.get("frozen_verdict"),
        "atom_results": [{
            "atom_id": "A1",
            "atom_text": claim_text,
            "verdict": atom_result.get("frozen_verdict"),
            "rule": atom_result.get("frozen_rule"),
        }],
    }


def review_atom(claim_text, source_text, atom_result, transport=None):
    """One reviewer call for one atom; returns RC3 schema dict or an
    invalid marker dict. Fidelity failures return requires_human_review
    True with ungrounded spans stripped (fail closed)."""
    rev = _reviewer_module()
    packet = rev.build_packet(
        claim_text, source_text,
        _rc2_engine_result(claim_text, source_text, atom_result),
        "RC3_ARBITRATION_PROPOSAL")
    raw = rev.call_luna(packet, transport=transport)
    out = raw if isinstance(raw, dict) else None
    if out is None:
        # Transport or parse failure: fail closed to human review.
        return {
            "semantic_assessment": "",
            "evidence_sufficiency":
            "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
            "proposed_relation": "INSUFFICIENT_EVIDENCE",
            "supporting_span_ids": [],
            "counter_proof": None,
            "requires_human_review": True,
            "_transport_error": True,
        }
    proposal = {
        "semantic_assessment": str(out.get("verdict", "")).lower(),
        "evidence_sufficiency": "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
        "proposed_relation": RELATION_MAP.get(out.get("verdict"),
                                              "INSUFFICIENT_EVIDENCE"),
        "supporting_span_ids": out.get("support_span_ids") or [],
        "counter_proof": None,
        "requires_human_review": bool(out.get("needs_human_review")),
        "_confidence": out.get("confidence"),
        "_reason_code": out.get("reason_code"),
    }
    # Map span ids (S0..) to character offsets into the source so the
    # RC3 fidelity validator can ground them.
    offsets = []
    for s in packet["candidate_spans"]:
        if s["id"] in proposal["supporting_span_ids"]:
            idx = source_text.find(s["text"])
            if idx >= 0:
                offsets.append(idx)
    proposal["supporting_span_ids"] = offsets
    if out.get("verdict") == "CONTRADICTED":
        contra_idx = []
        for s in packet["candidate_spans"]:
            if s["id"] in (out.get("contradiction_span_ids") or []):
                idx = source_text.find(s["text"])
                if idx >= 0:
                    contra_idx.append(idx)
        if contra_idx:
            proposal["counter_proof"] = {
                "span_ids": contra_idx,
                "target_claim": claim_text,
            }
    return proposal
