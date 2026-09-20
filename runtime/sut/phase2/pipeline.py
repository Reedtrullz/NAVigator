"""Phase 2 full SUT pipeline (S1-S11), deterministic, no product LLM calls.

Same stage signature and ctx contract as Phase 1 (runtime/sut/pipeline.py).
Phase 1 files are byte-identical; this is a new lineage.
"""

import os
import time

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from sut.context import StageState, make_context, mark_stage, normalize_input
from sut.schemas import SchemaError, validate_input, validate_output

from sut.phase2.safety import TriageError, evaluate_safety, load_rules
from sut.phase2.decompose import decompose
from sut.phase2.knowledge import KnowledgeError, retrieve
from sut.phase2.discovery_adapter import run_discovery_step

# RC-02: top-level safety_priority carries the frozen 12-class triage
# vocabulary plus the two collapse priorities. Unknown/failed states are
# coerced fail-closed to ACUTE_RISK_NOW at emission.
SAFETY_PRIORITY_OUTPUT_VALUES = (
    "SYSTEM_SAFETY_PRECEDENCE", "ABUSE_DISCLOSURE_REPORTING", "ACUTE_RISK_NOW", "ACUTE_SOMATIC_MEDICAL", "ACUTE_RISK_HIGH", "ACUTE_RISK_HIGH_THIRD_PARTY", "URGENT_PSYCHOSIS_SUSPECT", "ACUTE_RISK_UNSURE_TRIAGE", "URGENT_CARE_CAPACITY", "SAFETY_CONCERN_NO_ACUTE_VIOLENCE", "SAFETY_CONCERN_REPORTING", "NON_ACUTE_ROUTINE",
    "URGENT_NOT_ACUTE",
    "NOT_ACUTE",
)
from sut.phase2.routes import build_national_route_candidates, build_route_candidates
from sut.phase2.aggregate import build_claims, collapse, derive_track_state, detect_conflicts


_STAGE_ORDER = (
    "input_normalization", "safety_triage", "decomposition",
    "knowledge_retrieval", "local_discovery", "route_reasoning",
    "evidence_aggregation", "epistemic_assignment", "answer_planning",
    "answer_rendering", "output_emission",
)

PHASE_2_ANSWER = (
    "Dette er en strukturert mellomlosning fra beslutningspipelinen "
    "(Phase 2). Endelig svartekst er ikke implementert ennaa. "
    "Ingen rute presentert som fullstendig verifisert; usikkerheter er "
    "listet nedenfor."
)

DEFAULT_VERIFIED_AT = "2026-09-09"


def _default_config():
    # Paths anchored to the repo root so the pipeline is cwd-independent.
    return {
        "mode": "replay",
        "safety_rules_path": os.path.join(_REPO_ROOT, "data", "safety-triage-rules-v2.json"),
        "knowledge_index_path": os.path.join(_REPO_ROOT, "data", "knowledge-index-v1.json"),
        "rules_registry_path": os.path.join(_REPO_ROOT, "data", "rules-v1.json"),
    }


def _with_state(stage, fn, ctx):
    start = time.perf_counter()
    try:
        fn(ctx)
    except Exception as exc:  # fail closed: any stage crash becomes RECOVERABLE
        mark_stage(ctx, stage, StageState.RECOVERABLE, "stage error: %s" % exc)
    return {"stage": stage, "latency_ms": round((time.perf_counter() - start) * 1000, 3)}


def s1_input_normalization(ctx):
    ctx["input"]["user_query"] = ctx["input"]["user_query"].strip()


def s2_safety_triage(ctx):
    try:
        rules = load_rules(ctx["_config"]["safety_rules_path"])
        evaluate_safety(ctx, rules)
    except TriageError as exc:
        mark_stage(ctx, "safety_triage", StageState.TERMINAL, "FC-01: %s" % exc)


def s3_decomposition(ctx):
    if ctx["safety"]["suppressed_routing"]:
        # Safety precedence: acute input never decomposes into service tracks.
        ctx["tracks"] = []
        ctx["_s3_skipped"] = True
        return
    ctx["tracks"] = decompose(ctx["input"]["user_query"])


def s4_knowledge_retrieval(ctx):
    records = []
    for track in ctx["tracks"]:
        try:
            track_records = retrieve(
                ctx["input"]["user_query"], track["domain"],
                index_path=ctx["_config"]["knowledge_index_path"],
                rules_path=ctx["_config"]["rules_registry_path"])
            # RC-08: retrieval-domain binding, not a claim overwrite.
            # retrieve() already scopes records to the track domain; the
            # per-track copy is evidence binding for S8.
            for rec in track_records:
                rec["track_domain"] = track["domain"]
            records.extend(track_records)
        except KnowledgeError as exc:
            mark_stage(ctx, "knowledge_retrieval", StageState.RECOVERABLE,
                       "knowledge retrieval failed: %s" % exc)
            return
    ctx["_s4_records"] = records
    # Per-domain retrieval restarts evidence-id numbering for each track;
    # ids must be unique across the combined collection or the answer
    # planner's evidence_id dedupe silently drops a later track's records
    # and their claims can no longer render (fail-closed at S11).
    for n, rec in enumerate(records, 1):
        suffix = "R%03d" % n if rec["source_type"] == "FROZEN_RULE" else "D%03d" % n
        rec["record_id"] = "K-" + suffix
        rec["evidence_id"] = "E-" + suffix


def s5_local_discovery(ctx):
    if ctx.get("_s3_skipped"):
        return
    municipality = (ctx["input"].get("location_context") or {}).get("municipality")
    steps = []
    any_incomplete = False
    for track in ctx["tracks"]:
        step = run_discovery_step(
            track,
            location_context=ctx["input"].get("location_context"),
            age=ctx["input"].get("profile", {}).get("age"),
            urgency=ctx["safety"]["priority"])
        steps.append({"track_id": track["track_id"], "domain": track["domain"],
                      "step": step})
        if step["state"] == "DISCOVERY_INCOMPLETE":
            any_incomplete = True
    ctx["_s5_steps"] = steps
    ctx["_s5_incomplete"] = any_incomplete
    if any_incomplete:
        mark_stage(ctx, "local_discovery", StageState.RECOVERABLE,
                   "FC-03: discovery incomplete; never a negative existence claim")
    elif municipality is None:
        mark_stage(ctx, "local_discovery", StageState.RECOVERABLE,
                   "local discovery not applicable: no municipality in location_context")


def s6_route_reasoning(ctx):
    ctx["_s6_routes"] = []
    for entry in ctx.get("_s5_steps", []):
        routes = build_route_candidates(
            entry["step"], track_domain=entry["domain"],
            age=ctx["input"].get("profile", {}).get("age"))
        ctx["_s6_routes"].extend(routes)
    discovery_service_count = sum(
        len(entry["step"].get("services", []))
        for entry in ctx.get("_s5_steps", []))
    ctx["_s6_routes"].extend(build_national_route_candidates(
        ctx.get("_s4_records", []), discovery_service_count))


def s7_evidence_aggregation(ctx):
    claims = build_claims(ctx.get("_s6_routes", []), ctx.get("_s4_records", []))
    result = detect_conflicts(claims)
    ctx["_s7_claims"] = result["claims"]
    ctx["_s7_conflicts"] = result["conflicts"]
    if result["conflicts"]:
        mark_stage(ctx, "evidence_aggregation", StageState.RECOVERABLE,
                   "source conflict detected: %d claim(s) downgraded to UNVERIFIED"
                   % len(result["conflicts"]))


def s8_epistemic_assignment(ctx):
    track_states = []
    per_track = {}
    for entry in ctx.get("_s5_steps", []):
        routes = [r for r in ctx.get("_s6_routes", [])
                  if r["track_domain"] == entry["domain"]]
        knowledge = [k for k in ctx.get("_s4_records", [])
                     if k.get("track_domain", k.get("domain")) == entry["domain"]]
        state = derive_track_state(routes, knowledge, entry["step"])
        track_states.append(state)
        per_track[entry["track_id"]] = state
    if not track_states and ctx.get("_s4_records"):
        track_states = ["EXISTENCE_ONLY"]
    top = collapse(track_states)
    ctx["epistemic_states"] = {
        "top_level": top,
        "per_track": per_track,
        "per_route": [
            {"route_id": r["route_id"], "route_state": r["route_state"]}
            for r in ctx.get("_s6_routes", [])
        ],
    }


def s9_answer_planning(ctx):
    routes = ctx.get("_s6_routes", [])
    evaluable = [r for r in routes
                 if r["route_state"] in ("FULLY_VERIFIED", "ACCESS_PARTIAL",
                                          "EXISTENCE_ONLY")]
    ctx["answer_plan"] = {
        "blocks": [
            {"order": i, "kind": "ROUTE_INFO", "track_id": None,
             "route_label": r["service_type"], "span_refs": r["evidence_refs"]}
            for i, r in enumerate(evaluable, start=1)
        ],
        "no_route_asserted": not evaluable,
        "presented_as_complete": False,
    }


def s10_answer_rendering(ctx):
    ctx["_answer"] = PHASE_2_ANSWER


def _provenance_records(ctx):
    records = []
    n = 1
    for entry in ctx.get("_s5_steps", []):
        step = entry["step"]
        for service in step["services"]:
            records.append({
                "id": "P-D%03d" % n,
                "source_type": "LOCAL_DISCOVERY",
                "source_ref": service["source_url"],
                "retrieved_at": None,
                "verified_at": DEFAULT_VERIFIED_AT,
                "claim_supported": "service existence and access info",
                "evidence_span": None,
                "authority_level": "MUNICIPAL",
                "freshness_class": "POINT_IN_TIME",
                "conflicts_with": [],
                "chain_parent_id": None,
            })
            n += 1
    for rec in ctx.get("_s4_records", []):
        ref = rec["source_reference"]
        source_ref = ref.get("url") or ref.get("path") or rec["record_id"]
        records.append({
            "id": "P-K%03d" % n,
            "source_type": rec["source_type"],
            "source_ref": source_ref,
            "retrieved_at": None,
            "verified_at": DEFAULT_VERIFIED_AT,
            "claim_supported": rec["claim"][:200],
            "evidence_span": rec["claim"][:200],
            "authority_level": rec["authority"],
            "freshness_class": rec["freshness"],
            "conflicts_with": [],
            "chain_parent_id": None,
        })
        n += 1
    return records


def _route_evidence(ctx, route):
    """RC-10: provenance that supports this specific route.

    A route's own evidence/provenance refs are ownership, not a global
    evidence pool. Local routes carry a service source_url; national routes
    carry a pre-resolved provenance id (P-K...). Only real http(s) URLs from
    structured service discovery are attached as source_url; knowledge
    records keep repo paths and never get fabricated URLs.
    """
    source_url = None
    evidence_ids = list(route.get("evidence_refs") or [])
    prov_records = _provenance_records(ctx)
    prov_by_source = {}
    prov_by_id = {}
    for p in prov_records:
        prov_by_source.setdefault(p.get("source_ref"), p["id"])
        prov_by_id[p["id"]] = p
    prov_ids = []
    for ref in route.get("provenance_refs") or []:
        if not isinstance(ref, str):
            continue
        if ref.startswith(("http://", "https://")):
            if source_url is None:
                source_url = ref
            pid = prov_by_source.get(ref)
        elif ref in prov_by_id:
            pid = ref
        else:
            continue
        if pid and pid not in prov_ids:
            prov_ids.append(pid)
    rec_by_eid = {rec.get("evidence_id"): rec
                  for rec in ctx.get("_s4_records", [])}
    for eid in evidence_ids:
        rec = rec_by_eid.get(eid)
        if not rec:
            continue
        ref = (rec["source_reference"].get("url")
               or rec["source_reference"].get("path"))
        pid = prov_by_source.get(ref)
        if pid and pid not in prov_ids:
            prov_ids.append(pid)
    return source_url, evidence_ids, prov_ids


def _claim_evidence(ctx):
    """RC-10: per-claim provenance resolution keyed by claim_id.

    Only provenance ids that exist in the emitted provenance records are
    attached; unresolved refs are dropped, never fabricated.
    """
    prov_records = _provenance_records(ctx)
    prov_ids_all = {p["id"] for p in prov_records}
    prov_by_source = {}
    for p in prov_records:
        prov_by_source.setdefault(p.get("source_ref"), p["id"])
    rec_by_eid = {rec.get("evidence_id"): rec
                  for rec in ctx.get("_s4_records", [])}
    out = {}
    for c in ctx.get("_s7_claims", []):
        if c.get("state") != "VERIFIED":
            continue
        pids = []
        for pid in c.get("provenance_ids") or []:
            if pid in prov_ids_all and pid not in pids:
                pids.append(pid)
        for eid in c.get("evidence_ids") or []:
            rec = rec_by_eid.get(eid)
            if not rec:
                continue
            ref = (rec["source_reference"].get("url")
                   or rec["source_reference"].get("path"))
            pid = prov_by_source.get(ref)
            if pid and pid not in pids:
                pids.append(pid)
        out[c["claim_id"]] = {
            "evidence_ids": list(c.get("evidence_ids") or []),
            "provenance_ids": pids,
        }
    return out


def _uncertainty_list(ctx):
    items = []
    if ctx.get("_s5_incomplete"):
        items.append("local_availability_unverified")
    elif not ctx.get("_s5_steps"):
        items.append("local_availability_unverified")
    if ctx["epistemic_states"]["top_level"] != "FULLY_VERIFIED":
        items.append("answer_is_structured_placeholder")
    return items


def s11_output_emission(ctx):
    failures = ctx["failures"]
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

    routes = ctx.get("_s6_routes", [])
    evaluable = [r for r in routes
                 if r["route_state"] in ("FULLY_VERIFIED", "ACCESS_PARTIAL",
                                          "EXISTENCE_ONLY")]
    route_evidence = {}
    for r in evaluable:
        source_url, evidence_ids, prov_ids = _route_evidence(ctx, r)
        entry = {"evidence_ids": evidence_ids, "provenance_ids": prov_ids}
        if source_url:
            entry["source_url"] = source_url
        route_evidence[r["route_id"]] = entry
    claims = [c["value"] for c in ctx.get("_s7_claims", [])
              if c["state"] == "VERIFIED" and isinstance(c["value"], str)]
    top = ctx["epistemic_states"]["top_level"]
    output = {
        "answer": ctx.get("_answer", PHASE_2_ANSWER),
        "safety": {
            "priority": priority,
            "safety_class": safety_class,
            "signals": ctx["safety"]["signals"],
            "suppressed_routing": ctx["safety"]["suppressed_routing"],
        },
        "tracks": [
            {"track_id": t["track_id"], "domain": t["domain"],
             "status": "RESOLVED" if evaluable else "NO_ROUTE"}
            for t in ctx["tracks"]
        ],
        "routes": [r["service_type"] for r in evaluable],
        "claims": claims,
        "uncertainty_expressed": _uncertainty_list(ctx),
        "evidence": {
            "conflicts": [c["subject"] for c in ctx.get("_s7_conflicts", [])],
            "per_track_epistemic": ctx["epistemic_states"]["per_track"],
            "route_evidence": route_evidence,
            "claim_evidence": _claim_evidence(ctx),
            "safety_priority": top_priority,
        },
        "provenance": _provenance_records(ctx),
        "epistemic_state": top,
        "failures": failures,
        "execution_status": execution_status,
        "no_route_asserted": not evaluable,
        "presented_as_complete": False,
    }
    output["safety_priority"] = top_priority
    validate_output(output)
    ctx["_output"] = output


def _failed_output(message):
    priority = "ACUTE_RISK_NOW"  # fail-closed placeholder, see INTERFACE_GAP-001
    output = {
        "answer": "Kan ikke svare: input ble avvist av S1-valideringen.",
        "safety": {"priority": priority, "signals": [], "suppressed_routing": True},
        "tracks": [],
        "routes": [],
        "claims": [],
        "uncertainty_expressed": [],
        "evidence": {},
        "provenance": [],
        "epistemic_state": "UNVERIFIED",
        "failures": [
            {"stage": "input_normalization", "state": "TERMINAL", "message": message}
        ],
        "execution_status": "EXECUTION_FAILED",
        "no_route_asserted": True,
        "presented_as_complete": False,
    }
    output["safety_priority"] = priority
    validate_output(output)
    return output


STAGES = {
    "input_normalization": s1_input_normalization,
    "safety_triage": s2_safety_triage,
    "decomposition": s3_decomposition,
    "knowledge_retrieval": s4_knowledge_retrieval,
    "local_discovery": s5_local_discovery,
    "route_reasoning": s6_route_reasoning,
    "evidence_aggregation": s7_evidence_aggregation,
    "epistemic_assignment": s8_epistemic_assignment,
    "answer_planning": s9_answer_planning,
    "answer_rendering": s10_answer_rendering,
    "output_emission": s11_output_emission,
}


def _stage_state(ctx, stage):
    for failure in ctx["failures"]:
        if failure["stage"] == stage:
            return failure["state"]
    return "SUCCESS"


def run_with_trace(input_dict, config=None):
    """Execute S1-S11 once; return (sut_output/v1 dict, stage trace list)."""
    cfg = dict(_default_config())
    if config:
        cfg.update(config)
    normalized = normalize_input(input_dict)
    try:
        validate_input(normalized)
    except SchemaError as exc:
        return _failed_output(str(exc)), [
            {"stage": "input_normalization", "state": "TERMINAL", "latency_ms": 0.0}
        ]

    ctx = make_context(normalized)
    ctx["_config"] = cfg
    trace = []
    for stage in _STAGE_ORDER:
        mark = _with_state(stage, STAGES[stage], ctx)
        mark["state"] = _stage_state(ctx, stage)
        trace.append(mark)
    return ctx["_output"], trace


def run(input_dict, config=None):
    return run_with_trace(input_dict, config)[0]
