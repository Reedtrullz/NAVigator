#!/usr/bin/env python3
"""V1.6C.1 semantic residual packet builder.

Structure-only. Source of truth: frozen A3 engine (boundary_preclassifier.py
sha 21047fda...) and its own frozen marker lists. No new semantic
classification. Never receives gold, fixture ids, or strata.

ponytail: marker-span location is substring-based exactly like A3's own rule
matching; if A3 ever upgrades to dependency parsing, swap _hits for it here.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3_DIR = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3"))
sys.path.insert(0, A3_DIR)

import boundary_preclassifier as B  # noqa: E402

A3_ENGINE_SHA = "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b"
PACKET_VERSION = "semantic-residual-packet-v1"


def _a3_sha():
    path = os.path.join(A3_DIR, "boundary_preclassifier.py")
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _strip_inventory(obj):
    """Deep-redact lexical inventory flags from embedded A3 output."""
    if isinstance(obj, dict):
        return {k: _strip_inventory(v) for k, v in obj.items() if k != "inventory"}
    if isinstance(obj, list):
        return [_strip_inventory(v) for v in obj]
    return obj


def _clause_index_of(clauses, pos):
    for i, (s, e) in enumerate(clauses):
        if s <= pos < e:
            return i
    return None


def _dedup(spans):
    seen = set()
    out = []
    for s in spans:
        key = (s["start"], s["end"], s["text"])
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def build_packet(dimension, criterion, source_text, case_context=""):
    if _a3_sha() != A3_ENGINE_SHA:
        raise RuntimeError("A3 engine SHA drift: refusing to build packet")
    tl = source_text.lower()
    a3_raw = B.classify(source_text, None)
    a3 = _strip_inventory(json.loads(json.dumps(a3_raw)))
    clauses = B._clauses(tl)

    clause_spans = [
        {"start": s, "end": e, "text": tl[s:e],
         "provenance": "a3_clause_segmentation"}
        for s, e in clauses
    ]

    def located(markers, provenance):
        spans = []
        for _m, s, e in B._hits(tl, markers):
            sp = {"start": s, "end": e, "text": tl[s:e], "provenance": provenance}
            ci = _clause_index_of(clauses, s)
            if ci is not None:
                sp["clause_index"] = ci
            spans.append(sp)
        return _dedup(spans)

    route_candidates = located(B.ROUTE_TERMS, "a3_route_terms_hits")
    quote_spans = located(B.QUOTE_MARKERS, "a3_quote_marker_hits")
    negation_spans = located(B.NEGATION_MARKERS, "a3_negation_marker_hits")
    retraction_spans = located(B.RETRACTION_MARKERS, "a3_retraction_marker_hits")
    hedge_spans = located(B.HEDGE_MARKERS, "a3_hedge_marker_hits")
    assertion_spans = located(B.ASSERTION_MARKERS, "a3_assertion_marker_hits")
    conditional_spans = located(
        sorted(set(B.CONDITIONAL_ROUTE_MARKERS + B.CONDITIONAL_UNC_MARKERS)),
        "a3_conditional_marker_hits")
    attribution_spans = located(
        sorted(set(B.USER_ATTRIBUTION_MARKERS + B.THIRD_PARTY_ATTRIBUTION_MARKERS)),
        "a3_attribution_marker_hits")
    vague_spans = located(B.VAGUE_MARKERS, "a3_vague_marker_hits")

    deterministic_evidence = []
    for dim in ("route_commitment", "uncertainty_behavior", "assertion_scope"):
        span_text = (a3.get(dim) or {}).get("evidence_span")
        if span_text and span_text.lower() in tl and span_text not in deterministic_evidence:
            deterministic_evidence.append(span_text)

    return {
        "packet_version": PACKET_VERSION,
        "dimension": dimension,
        "source_text": source_text,
        "criterion": criterion,
        "case_context": case_context,
        "clause_spans": clause_spans,
        "route_candidates": route_candidates,
        "quote_spans": quote_spans,
        "negation_spans": negation_spans,
        "retraction_spans": retraction_spans,
        "hedge_spans": hedge_spans,
        "assertion_spans": assertion_spans,
        "conditional_spans": conditional_spans,
        "attribution_spans": attribution_spans,
        "vague_spans": vague_spans,
        "a3": a3,
        "deterministic_evidence": deterministic_evidence,
    }
