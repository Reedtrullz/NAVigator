"""Deterministic S10 answer rendering (Phase 3).

Pure template rendering over the AnswerPlan. No freeform generation, no
randomization, no LLM. Dynamic strings are ASCII-transliterated with the
same function everywhere so claim/route substrings stay exact.
"""

import json

from sut.phase3.planner import (
    CONFLICT_WORDING,
    DISCOVERY_INCOMPLETE_WORDING,
    NO_ROUTE_WORDING,
    ROUTE_WORDING,
    URGENCY_LEAD,
)

# Frozen acute-safety instruction lines. Vocabulary only; no new advice.
SAFETY_INSTRUCTION_LINES = (
    "Ved umiddelbar livsfare: ring 113.",
    "Ved akutt psykisk krise eller selvmordsrisiko: ring 116 123, dognet.",
    "Ved overgrep eller vold: kontakt politiet pa 02800; ring 112 ved akutt fare.",
    "Ved akutt somatisk sykdom eller skade: ring 116 117 (legevakt).",
)

TERMINAL_FAILURE_WORDING = (
    "Svaret er ufullstendig fordi et obligatorisk trinn feilet (%s). "
    "Ingen tjeneste anbefales."
)

NO_PROVENANCE_WORDING = "Ingen kilde kunne verifiseres for dette svaret."

TOP_UNVERIFIED_WORDING = "Ingen del av dette svaret er fullstendig verifisert."

NEGATIVE_EXISTENCE_PHRASES = (
    "har ikke tilbud",
    "mangler tilbud",
    "finnes ikke",
)

_TRANSLIT = {
    "\u00e6": "ae", "\u00f8": "oe", "\u00e5": "aa",
    "\u00c6": "Ae", "\u00d8": "Oe", "\u00c5": "Aa",
    "\u00e9": "e", "\u00c9": "E", "\u00e8": "e", "\u00c8": "E",
    "\u00fc": "u", "\u00dc": "U", "\u00f6": "o", "\u00d6": "O",
    "\u00e4": "a", "\u00c4": "A",
}


def ascii_text(text):
    return "".join(_TRANSLIT.get(ch, ch) for ch in text)


def canonical_json(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _safety_lines(ctx):
    if ctx["safety"]["suppressed_routing"]:
        return list(SAFETY_INSTRUCTION_LINES)
    priority = ctx["safety"]["priority"]
    if priority == "ACUTE_RISK_NOW":
        return list(SAFETY_INSTRUCTION_LINES)
    if priority == "URGENT_NOT_ACUTE":
        return [URGENCY_LEAD]
    return []


def _routes_by_id(ctx):
    return {r["route_id"]: r for r in ctx.get("_s6_routes", [])}


def _route_line(ctx, block):
    ref = block["span_refs"][0] if block["span_refs"] else ""
    route_id = ref.split("route:", 1)[-1]
    route = _routes_by_id(ctx).get(route_id)
    if route is None:
        return []
    state = route.get("route_state", "UNVERIFIED")
    wording = ROUTE_WORDING.get(state)
    if wording is None:
        return []
    name = ascii_text(route.get("service_type", ""))
    if block["kind"] == "PRIMARY_ROUTE":
        lines = ["Anbefalt neste steg:"]
    else:
        lines = ["Andre aktuelle tilbud:"]
    lines.append("'%s' er %s." % (name, wording))
    return lines


def _failure_lines(ctx, block):
    for ref in block["span_refs"]:
        if ref.startswith("terminal:"):
            return [TERMINAL_FAILURE_WORDING % ref.split("terminal:", 1)[-1]]
        if ref.startswith("conflict:"):
            parts = ref.split(":")
            subject = parts[1] if len(parts) > 1 else ref
            return [CONFLICT_WORDING % subject]
    return []


def _info_lines(ctx, block, by_evidence_id):
    lines = []
    for ref in block["span_refs"]:
        rec = by_evidence_id.get(ref)
        if rec is None:
            continue
        lines.append("Nasjonal informasjon: " + ascii_text(rec["claim"]))
    return lines


def _uncertainty_lines(ctx, block):
    refs = block["span_refs"]
    lines = []
    if "discovery_incomplete" in refs:
        lines.append("Lokalt oppslag for minst ett omraade "
                     + DISCOVERY_INCOMPLETE_WORDING + ".")
    if "no_route_found" in refs:
        lines.append(NO_ROUTE_WORDING)
    if "top_state_UNVERIFIED" in refs:
        evaluable = [b for b in ctx["answer_plan"]["blocks"]
                     if b["kind"] in ("PRIMARY_ROUTE", "SECONDARY_ROUTE")]
        if evaluable and "discovery_incomplete" not in refs:
            lines.append(TOP_UNVERIFIED_WORDING)
    return lines


def _provenance_lines(ctx, block):
    from sut.phase2.pipeline import _provenance_records
    records = _provenance_records(ctx)
    by_id = {p["id"]: p for p in records}
    lines = []
    for ref in block["span_refs"]:
        p = by_id.get(ref)
        if p is None:
            continue
        lines.append("Kilde %s: %s (verifisert %s)" % (
            p["id"], ascii_text(p["source_ref"]), p["verified_at"]))
    if not lines:
        lines = [NO_PROVENANCE_WORDING]
    return lines


def _render_sections(ctx):
    """Return [(block_kind, section_text)] for the frozen plan blocks."""
    by_evidence_id = {rec["evidence_id"]: rec for rec in ctx.get("_s4_records", [])}
    sections = []
    for block in ctx["answer_plan"]["blocks"]:
        kind = block["kind"]
        if kind == "SAFETY_INSTRUCTION":
            lines = _safety_lines(ctx)
        elif kind == "FAILURE_NOTICE":
            lines = _failure_lines(ctx, block)
        elif kind == "INFO":
            lines = _info_lines(ctx, block, by_evidence_id)
        elif kind in ("PRIMARY_ROUTE", "SECONDARY_ROUTE"):
            lines = _route_line(ctx, block)
        elif kind == "UNCERTAINTY":
            lines = _uncertainty_lines(ctx, block)
        elif kind == "PROVENANCE_LIST":
            lines = _provenance_lines(ctx, block)
        else:
            lines = []
        if lines:
            sections.append((kind, "\n".join(lines)))
    if not sections:
        sections = [("FALLBACK", NO_ROUTE_WORDING)]
    return sections


def render(ctx):
    """Render the frozen plan blocks into the user-facing answer."""
    return "\n\n".join(text for _kind, text in _render_sections(ctx))


def s10_answer_rendering(ctx):
    ctx["_answer"] = render(ctx)
