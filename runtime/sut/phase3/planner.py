"""Deterministic S9 answer planning (Phase 3).

The planner organizes already-approved structured state from the
DecisionContext. It never upgrades route state, invents services,
interprets law, or alters safety state. Blocks are emitted in frozen
order:

  SAFETY_INSTRUCTION -> FAILURE_NOTICE(terminal) -> INFO(knowledge)
  -> FAILURE_NOTICE(conflicts) -> PRIMARY_ROUTE/SECONDARY_ROUTE
  -> UNCERTAINTY -> PROVENANCE_LIST
"""

from sut.phase2.pipeline import _provenance_records

_DOMAIN_PRIORITY = (
    "child_safety", "mental_health", "housing", "financial_support",
    "education", "employment", "legal_rights", "safety", "general",
)

_STATE_RANK = {
    "FULLY_VERIFIED": 0,
    "ACCESS_PARTIAL": 1,
    "EXISTENCE_ONLY": 2,
    "UNVERIFIED": 3,
}

_EVALUABLE_STATES = ("FULLY_VERIFIED", "ACCESS_PARTIAL", "EXISTENCE_ONLY")

# Epistemic wording per route state, rendered verbatim by the renderer.
ROUTE_WORDING = {
    "FULLY_VERIFIED": "verifisert i oppslaget",
    "ACCESS_PARTIAL": "finnes og er relevant, men tilgang er ikke verifisert",
    "EXISTENCE_ONLY": "registrert i oppslaget. Aldersgrense og tilgang er ikke verifisert",
    "UNVERIFIED": "ikke verifisert",
}

DISCOVERY_INCOMPLETE_WORDING = (
    "ble ikke fullfoert. Dette er ikke det samme som at kommunen ikke har tilbud"
)

NO_ROUTE_WORDING = (
    "Fant ingen registrerte kommunale tilbud for denne henvendelsen. "
    "Det betyr ikke at tilbudet ikke finnes; det kan bety at oppslaget ikke "
    "dekker kommunen eller at soeket ikke ga treff."
)

CONFLICT_WORDING = "Kildene sier motstridende ting om %s; konflikten er ikke lost."

URGENCY_LEAD = "Dette hoerstes alvorlig, men ikke akutt pa maaten som krever nodnummer."


def _domain_rank(domain):
    try:
        return _DOMAIN_PRIORITY.index(domain)
    except ValueError:
        return len(_DOMAIN_PRIORITY)


def sort_routes(routes):
    """Deterministic ordering: domain priority, epistemic strength, scenario
    relevance, access verification, name length, input order. No weighted
    scores."""
    indexed = list(enumerate(routes))
    indexed.sort(key=lambda pair: (
        _domain_rank(pair[1].get("track_domain", "")),
        _STATE_RANK.get(pair[1].get("route_state", "UNVERIFIED"), 3),
        0 if pair[1].get("scenario_relevant") == "VERIFIED" else 1,
        0 if pair[1].get("access_verified") == "VERIFIED" else 1,
        len(pair[1].get("service_type", "")),
        pair[0],
    ))
    return [r for _, r in indexed]


def _evaluable_routes(ctx):
    return [r for r in sort_routes(ctx.get("_s6_routes", []))
            if r.get("route_state") in _EVALUABLE_STATES]


def plan(ctx):
    """Build the frozen-block-order AnswerPlan from structured ctx state."""
    blocks = []
    order = 0

    def add(kind, **fields):
        nonlocal order
        order += 1
        block = {"order": order, "kind": kind, "track_id": None,
                 "route_label": None, "span_refs": []}
        block.update(fields)
        blocks.append(block)

    # 1. Safety instruction first whenever the safety lane is active.
    if ctx["safety"]["suppressed_routing"] or ctx["safety"]["priority"] != "NOT_ACUTE":
        add("SAFETY_INSTRUCTION")

    failures = ctx["failures"]
    # 2. Terminal failures show the pipeline could not finish.
    for f in failures:
        if f["state"] == "TERMINAL":
            add("FAILURE_NOTICE", span_refs=["terminal:" + f["stage"]])

    # 3. Knowledge INFO blocks, one per national knowledge record scoped to
    # an active track domain (RC-08). Records without matching scope never
    # render, so cross-domain lexical hits cannot leak into the answer.
    track_domains = {t["domain"] for t in ctx.get("tracks", [])}
    seen_info = set()
    for rec in ctx.get("_s4_records", []):
        if rec.get("track_domain", rec.get("domain")) not in track_domains:
            continue
        if rec["evidence_id"] in seen_info:
            continue
        seen_info.add(rec["evidence_id"])
        add("INFO", span_refs=[rec["evidence_id"]])

    # 4. Source-conflict notices.
    for c in ctx.get("_s7_conflicts", []):
        add("FAILURE_NOTICE",
            span_refs=["conflict:" + c["subject"] + ":" + c["dimension"]])

    # 5. Routes: first evaluable route is PRIMARY, the rest SECONDARY.
    evaluable = _evaluable_routes(ctx)
    for i, route in enumerate(evaluable):
        add("PRIMARY_ROUTE" if i == 0 else "SECONDARY_ROUTE",
            track_id=route["track_domain"], route_label=route["service_type"],
            span_refs=["route:" + route["route_id"]])

    # 6. Uncertainty caveats in fixed precedence.
    uncertainty_refs = []
    if ctx.get("_s5_incomplete"):
        uncertainty_refs.append("discovery_incomplete")
    if not evaluable and not ctx.get("_s5_incomplete"):
        uncertainty_refs.append("no_route_found")
    for route in evaluable:
        if route.get("route_state") in ("ACCESS_PARTIAL", "EXISTENCE_ONLY"):
            uncertainty_refs.append("state_" + route["route_id"])
    top = ctx["epistemic_states"]["top_level"]
    if top != "FULLY_VERIFIED":
        uncertainty_refs.append("top_state_" + top)
    if uncertainty_refs:
        add("UNCERTAINTY", span_refs=uncertainty_refs)

    # 7. Provenance list last.
    prov = _provenance_records(ctx)
    add("PROVENANCE_LIST", span_refs=[p["id"] for p in prov])

    presented_as_complete = (
        not any(f["state"] == "TERMINAL" for f in failures)
        and not ctx.get("_s5_incomplete")
        and not ctx.get("_s3_skipped")
        and bool(ctx.get("_s5_steps"))
        and all(t in _EVALUABLE_STATES
                for t in ctx["epistemic_states"]["per_track"].values())
    )
    return {
        "blocks": blocks,
        "no_route_asserted": not evaluable,
        "presented_as_complete": presented_as_complete,
    }


def s9_answer_planning(ctx):
    ctx["answer_plan"] = plan(ctx)
