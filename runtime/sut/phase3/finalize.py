"""Deterministic S11 output finalization (Phase 3).

Consistency-checks the rendered answer against structured state, then
emits canonical sut-output/v1. Any consistency failure or schema failure
is fail-closed: the output becomes a terminal EXECUTION_FAILED result with
a schema-valid shape and no route content.
"""

from sut.schemas import SchemaError, validate_output
from sut.phase3.render import (
    NEGATIVE_EXISTENCE_PHRASES,
    _render_sections,
    ascii_text,
    render,
)
from sut.phase2.pipeline import (
    SAFETY_PRIORITY_OUTPUT_VALUES,
    _claim_evidence,
    _route_evidence,
    _provenance_records,
    _failed_output,
)

_EVALUABLE_STATES = ("FULLY_VERIFIED", "ACCESS_PARTIAL", "EXISTENCE_ONLY")

_CLAIM_ENUMS = {
    "service_exists": ("VERIFIED", "UNRESOLVED", "FAILED", "PARTIAL"),
    "age_eligible": ("VERIFIED", "UNRESOLVED", "FAILED", "PARTIAL"),
    "scenario_relevant": ("VERIFIED", "UNRESOLVED", "FAILED", "PARTIAL"),
    "access_verified": ("VERIFIED", "UNRESOLVED", "FAILED", "PARTIAL"),
    "contact_verified": ("VERIFIED", "UNRESOLVED", "FAILED", "PARTIAL"),
}

_ROUTE_STATE_ENUM = (
    "FULLY_VERIFIED", "ACCESS_PARTIAL", "EXISTENCE_ONLY", "UNVERIFIED",
)

_EPISYSTEM_ENUM = (
    "FULLY_VERIFIED", "ACCESS_PARTIAL", "EXISTENCE_ONLY", "UNVERIFIED",
)

_STAGE_ENUM = (
    "input_normalization", "safety_triage", "decomposition",
    "knowledge_retrieval", "local_discovery", "route_reasoning",
    "evidence_aggregation", "epistemic_assignment", "answer_planning",
    "answer_rendering", "output_emission",
)

_FAILURE_STATE_ENUM = ("SUCCESS", "PARTIAL", "RECOVERABLE", "TERMINAL")



def _evaluable_routes(ctx):
    return [r for r in ctx.get("_s6_routes", [])
            if r.get("route_state") in _EVALUABLE_STATES]


def _known_ref_ids(ctx):
    ids = set()
    for c in ctx.get("_s7_claims", []):
        ids.update(c.get("evidence_ids") or [])
        ids.update(c.get("provenance_ids") or [])
    for rec in ctx.get("_s4_records", []):
        ids.add(rec["evidence_id"])
        ids.add(rec["record_id"])
    for p in ctx.get("_s6_routes", []):
        ids.update(p.get("evidence_refs") or [])
        ids.update(p.get("provenance_refs") or [])
    for p in _provenance_records(ctx):
        ids.add(p["id"])
    ids.add("safety-triage-rules-v2")
    return ids


def _plan_routes_in_structured(ctx, plan_blocks):
    structured = {r["route_id"] for r in ctx.get("_s6_routes", [])}
    for b in plan_blocks:
        if b["kind"] not in ("PRIMARY_ROUTE", "SECONDARY_ROUTE"):
            continue
        for ref in b["span_refs"]:
            if ref.startswith("route:"):
                rid = ref.split("route:", 1)[-1]
                if rid not in structured:
                    return False
    return True


def _plan_span_refs_resolve(ctx, plan_blocks):
    known = _known_ref_ids(ctx)
    for b in plan_blocks:
        for ref in b["span_refs"]:
            if ref in ("discovery_incomplete", "no_route_found"):
                continue
            if ref.startswith("state_") or ref.startswith("top_state_"):
                continue
            if ":" in ref:
                prefix = ref.split(":", 1)[0]
                if prefix in ("terminal", "conflict", "route", "state",
                              "top_state", "discovery_incomplete",
                              "no_route_found"):
                    continue
            if ref in known:
                continue
            return False
    return True


def _claims_substring_of_answer(ctx, answer, claims):
    for c in ctx.get("_s7_claims", []):
        if (c["state"] != "VERIFIED" or c.get("dimension") != "knowledge_fact"
                or not isinstance(c["value"], str)):
            continue
        ascii_val = ascii_text(c["value"])
        if ascii_val not in answer:
            return False
    return True


def _route_labels_substring_of_answer(ctx, answer, routes):
    for label in routes:
        if ascii_text(label) not in answer:
            return False
    return True


def _consistency_errors(ctx, plan, answer, routes, claims,
                        uncertainty, epistemic, failures):
    errors = []
    plan_blocks = plan["blocks"]
    if not _plan_routes_in_structured(ctx, plan_blocks):
        errors.append("plan route not in structured routes")
    if not _plan_span_refs_resolve(ctx, plan_blocks):
        errors.append("plan span_ref unresolved")
    if not _claims_substring_of_answer(ctx, answer, claims):
        errors.append("verified claim value missing from answer")
    if not _route_labels_substring_of_answer(ctx, answer, routes):
        errors.append("route label missing from answer")
    # Non-enum claim values must appear in the answer.
    for c in ctx.get("_s7_claims", []):
        dim = c.get("dimension")
        if dim in _CLAIM_ENUMS and c.get("value") not in _CLAIM_ENUMS[dim]:
            errors.append("claim %s has invalid enum value" % c.get("claim_id"))
    if epistemic not in _EPISYSTEM_ENUM:
        errors.append("epistemic state invalid")
    for f in failures:
        if f["stage"] not in _STAGE_ENUM:
            errors.append("failure stage invalid")
        if f["state"] not in _FAILURE_STATE_ENUM:
            errors.append("failure state invalid")
    # FC-05 guard: complete presentation requires no terminal failure.
    # Frozen presented_as_complete contract (answer-plan-contract.json)
    # admits non-terminal RECOVERABLE/PARTIAL failures; the planner
    # already enforces the other four conditions.
    if plan["presented_as_complete"] and any(
            f["state"] == "TERMINAL" for f in failures):
        errors.append("presented_as_complete with failures")
    # FC-03 guard: negative-existence wording is forbidden in
    # SUT-authored (non-INFO) sections. INFO sections render verbatim,
    # provenance-linked national records; quoting the no-service rule
    # is not asserting local non-existence.
    authored_answer = "\n\n".join(
        text for kind, text in _render_sections(ctx) if kind != "INFO"
    )
    lowered = authored_answer.lower()
    for phrase in NEGATIVE_EXISTENCE_PHRASES:
        if phrase in lowered:
            errors.append("negative existence wording present")
    # Discovery-incomplete wording must appear when discovery is incomplete.
    if ctx.get("_s5_incomplete") and "ikke det samme som at kommunen ikke har tilbud" not in answer:
        errors.append("discovery-incomplete disclaimer missing")
    return errors


def _failed_render_output(message, answer_text=""):
    output = _failed_output(message)
    if answer_text:
        output["answer"] = answer_text
    return output


def finalize(ctx):
    """S11: render, consistency-check, validate, emit canonical output."""
    failures = ctx["failures"]
    try:
        answer_text = render(ctx)
    except Exception as exc:
        return _failed_render_output(
            "render failed: %s" % type(exc).__name__)

    evaluable = _evaluable_routes(ctx)
    routes = [r["service_type"] for r in evaluable]
    claims = [c["value"] for c in ctx.get("_s7_claims", [])
              if c["state"] == "VERIFIED" and c.get("dimension") == "knowledge_fact"
              and isinstance(c["value"], str)]
    uncertainty = []
    for b in ctx["answer_plan"]["blocks"]:
        if b["kind"] == "UNCERTAINTY":
            uncertainty.extend(b["span_refs"])
    top = ctx["epistemic_states"]["top_level"]

    errors = _consistency_errors(
        ctx, ctx["answer_plan"], answer_text, routes, claims,
        uncertainty, top, failures)
    if errors:
        return _failed_render_output(
            "output consistency failed: " + "; ".join(errors),
            answer_text=answer_text)

    if any(f["state"] == "TERMINAL" for f in failures):
        execution_status = "EXECUTION_FAILED"
    elif ctx.get("_s5_incomplete"):
        execution_status = "DISCOVERY_INCOMPLETE"
    else:
        execution_status = "SUCCESS"

    priority = ctx["safety"]["priority"]
    safety_class = ctx["safety"].get("safety_class")
    if priority not in SAFETY_PRIORITY_OUTPUT_VALUES:
        priority = "ACUTE_RISK_NOW"
        safety_class = None
        top_priority = "ACUTE_RISK_NOW"
    else:
        # RC-11: fine triage class survives at top level; the collapsed
        # priority stays in safety.priority for the frozen 3-level contract.
        top_priority = safety_class if (
            isinstance(safety_class, str)
            and safety_class in SAFETY_PRIORITY_OUTPUT_VALUES) else priority

    # RC-10: per-route/per-claim evidence attachment under the additive
    # evidence map; the routes list stays labels-only for the frozen
    # scorer contract.
    route_evidence = {}
    for r in evaluable:
        source_url, evidence_ids, prov_ids = _route_evidence(ctx, r)
        entry = {"evidence_ids": evidence_ids, "provenance_ids": prov_ids}
        if source_url:
            entry["source_url"] = source_url
        route_evidence[r["route_id"]] = entry

    # W4-RC-A (B5): route objects survive serialization in the additive
    # evidence map (additionalProperties: true, no schema change); the
    # labels-only routes list keeps the frozen scorer contract intact.
    structured_routes = []
    for r in evaluable:
        entry = route_evidence.get(r["route_id"], {})
        structured_routes.append({
            "route_id": r["route_id"],
            "service_identity": r["service_type"],
            "display_label": r["service_type"],
            "track_domain": r.get("track_domain"),
            "route_state": r.get("route_state"),
            "access_model": r.get("access_model"),
            "self_referral": r.get("self_referral"),
            "target_population": r.get("target_population"),
            "scope": r.get("scope"),
            "evidence_refs": entry.get("evidence_ids", []),
            "provenance_refs": entry.get("provenance_ids", []),
            "dims": {k: r.get(k) for k in (
                "service_exists", "age_eligible", "scenario_relevant",
                "access_verified", "contact_verified")},
        })

    track_status = {}
    for t in ctx["epistemic_states"]["per_track"].items():
        track_status[t[0]] = "RESOLVED" if t[1] in _EVALUABLE_STATES else "NO_ROUTE"
    tracks = []
    for t in ctx["tracks"]:
        tracks.append({
            "track_id": t["track_id"],
            "domain": t["domain"],
            "status": track_status.get(t["track_id"], "NO_ROUTE"),
        })

    output = {
        "answer": answer_text,
        "safety": {
            "priority": priority,
            "safety_class": safety_class,
            "signals": ctx["safety"]["signals"],
            "suppressed_routing": ctx["safety"]["suppressed_routing"],
        },
        "tracks": tracks,
        "routes": routes,
        "claims": claims,
        "uncertainty_expressed": uncertainty,
        "evidence": {
            "conflicts": [c["subject"] for c in ctx.get("_s7_conflicts", [])],
            "per_track_epistemic": ctx["epistemic_states"]["per_track"],
            "route_evidence": route_evidence,
            "structured_routes": structured_routes,
            "claim_evidence": _claim_evidence(ctx),
            "safety_priority": top_priority,
        },
        "provenance": _provenance_records(ctx),
        "epistemic_state": top,
        "failures": failures,
        "execution_status": execution_status,
        "no_route_asserted": not evaluable,
        "presented_as_complete": ctx["answer_plan"]["presented_as_complete"],
    }
    output["safety_priority"] = top_priority

    try:
        validate_output(output)
    except SchemaError as exc:
        return _failed_render_output("schema validation failed: %s" % exc,
                                     answer_text=answer_text)
    return output


def s11_output_emission(ctx):
    ctx["_output"] = finalize(ctx)
