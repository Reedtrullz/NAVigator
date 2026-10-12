"""Phase 2 full SUT pipeline (S1-S11), deterministic, no product LLM calls.

Same stage signature and ctx contract as Phase 1 (runtime/sut/pipeline.py).
Phase 1 files are byte-identical; this is a new lineage.
"""

from typing import cast
from .contracts import AttachedEvidence, Config, ConfigOverrides, Context, Evidence, Input, KnowledgeRecord, Output, Provenance, RetrievalEvidence, Route, Stage, StepEntry, Trace

import os
import time

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from ..context import StageState as StageState, make_context, mark_stage as mark_stage, normalize_input
from ..schemas import SchemaError, validate_input, validate_output

from .safety import TriageError, evaluate_safety, load_rules
from .decompose import decompose
from .knowledge import KnowledgeError, retrieve, verified_date
from .discovery_adapter import run_discovery_step

# RC-02: top-level safety_priority carries the frozen 12-class triage
# vocabulary plus the two collapse priorities. Unknown/failed states are
# coerced fail-closed to ACUTE_RISK_NOW at emission.
SAFETY_PRIORITY_OUTPUT_VALUES = (
    "SYSTEM_SAFETY_PRECEDENCE", "ABUSE_DISCLOSURE_REPORTING", "ACUTE_RISK_NOW", "ACUTE_SOMATIC_MEDICAL", "ACUTE_RISK_HIGH", "ACUTE_RISK_HIGH_THIRD_PARTY", "URGENT_PSYCHOSIS_SUSPECT", "ACUTE_RISK_UNSURE_TRIAGE", "URGENT_CARE_CAPACITY", "SAFETY_CONCERN_NO_ACUTE_VIOLENCE", "SAFETY_CONCERN_REPORTING", "NON_ACUTE_ROUTINE",
    "URGENT_NOT_ACUTE",
    "NOT_ACUTE",
)
from .routes import build_national_route_candidates, build_route_candidates
from .aggregate import build_claims, collapse, derive_track_state, detect_conflicts


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

def default_config() -> Config:
    # Paths anchored to the repo root so the pipeline is cwd-independent.
    return {
        "mode": "replay",
        "safety_rules_path": os.path.join(_REPO_ROOT, "data", "safety-triage-rules-v2.json"),
        "knowledge_index_path": os.path.join(_REPO_ROOT, "data", "knowledge-index-v1.json"),
        "rules_registry_path": os.path.join(_REPO_ROOT, "data", "rules-v1.json"),
        "knowledge_access_profile": None,
        "knowledge_repo_root": _REPO_ROOT,
    }


def execute_stage(stage: str, fn: Stage, ctx: Context) -> Trace:
    start = time.perf_counter()
    try:
        fn(ctx)
    except Exception as exc:
        recoverable = stage in ("knowledge_retrieval", "local_discovery")
        mark_stage(ctx, stage, StageState.RECOVERABLE if recoverable else StageState.TERMINAL,
                   "stage error: %s" % type(exc).__name__)
        if not recoverable:
            _ = ctx.pop("_output", None)
        if stage == "knowledge_retrieval":
            ctx["_s4_incomplete"] = True
            ctx["_s4_records"] = []
            ctx["_s4_admission"] = {t["track_id"]: {"coverage": {"state": "INCOMPLETE"},
                "failures": [{"reason": "KNOWLEDGE_STAGE_FAILED"}]} for t in ctx["tracks"]}
        elif stage == "local_discovery":
            ctx["_s5_incomplete"] = True
            ctx["_s5_steps"] = [{"track_id": t["track_id"], "domain": t["domain"],
                                "step": {"state": "DISCOVERY_INCOMPLETE", "services": [], "evidence": []}}
                               for t in ctx["tracks"]]
    return {"stage": stage, "latency_ms": round((time.perf_counter() - start) * 1000, 3)}


def s1_input_normalization(ctx: Context) -> None:
    ctx["input"]["user_query"] = ctx["input"]["user_query"].strip()


def s2_safety_triage(ctx: Context) -> None:
    cfg = ctx.get("_config")
    if cfg is None:
        raise KeyError("_config")
    try:
        rules = load_rules(cfg["safety_rules_path"])
        evaluate_safety(ctx, rules)
    except TriageError as exc:
        mark_stage(ctx, "safety_triage", StageState.TERMINAL, "FC-01: %s" % exc)


def s3_decomposition(ctx: Context) -> None:
    if ctx["safety"]["suppressed_routing"]:
        # Safety precedence: acute input never decomposes into service tracks.
        ctx["tracks"] = []
        ctx["_s3_skipped"] = True
        return
    ctx["tracks"] = decompose(ctx["input"]["user_query"])


def s4_knowledge_retrieval(ctx: Context) -> None:
    cfg = ctx.get("_config")
    if cfg is None:
        raise KeyError("_config")
    records: list[KnowledgeRecord] = []
    ctx["_s4_admission"] = {}
    ctx["_s4_incomplete"] = False
    for track in ctx["tracks"]:
        try:
            result = retrieve(
                ctx["input"]["user_query"], track["domain"],
                index_path=cfg["knowledge_index_path"],
                rules_path=cfg["rules_registry_path"],
                repo_root=cfg["knowledge_repo_root"],
                access_profile=cfg["knowledge_access_profile"])
            track_records = result.records
            ctx["_s4_admission"][track["track_id"]] = {
                "coverage": result.coverage, "failures": result.failures}
            if result.failures:
                ctx["_s4_incomplete"] = True
                mark_stage(ctx, "knowledge_retrieval", StageState.RECOVERABLE,
                           "source admission incomplete: " + ",".join(f["reason"] for f in result.failures))
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


def s5_local_discovery(ctx: Context) -> None:
    if ctx.get("_s3_skipped"):
        return
    municipality = (ctx["input"].get("location_context") or {}).get("municipality")
    steps: list[StepEntry] = []
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


def s6_route_reasoning(ctx: Context) -> None:
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


def s7_evidence_aggregation(ctx: Context) -> None:
    claims = build_claims(ctx.get("_s6_routes", []), ctx.get("_s4_records", []))
    result = detect_conflicts(claims)
    ctx["_s7_claims"] = result["claims"]
    ctx["_s7_conflicts"] = result["conflicts"]
    if result["conflicts"]:
        mark_stage(ctx, "evidence_aggregation", StageState.RECOVERABLE,
                   "source conflict detected: %d claim(s) downgraded to UNVERIFIED"
                   % len(result["conflicts"]))


def s8_epistemic_assignment(ctx: Context) -> None:
    track_states: list[str] = []
    per_track = {}
    for entry in ctx.get("_s5_steps", []):
        routes = [r for r in ctx.get("_s6_routes", [])
                  if r["track_domain"] == entry["domain"]]
        knowledge = [k for k in ctx.get("_s4_records", [])
                     if k.get("track_domain", k.get("domain")) == entry["domain"]]
        state = derive_track_state(routes, knowledge, entry["step"])
        if ctx.get("_s4_admission", {}).get(entry["track_id"], {}).get("failures"):
            state = "UNVERIFIED"
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


def s9_answer_planning(ctx: Context) -> None:
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


def s10_answer_rendering(ctx: Context) -> None:
    ctx["_answer"] = PHASE_2_ANSWER


def provenance_records(ctx: Context) -> list[Provenance]:
    records: list[Provenance] = []
    n = 1
    for entry in ctx.get("_s5_steps", []):
        step = entry["step"]
        for service in step.get("services", []):
            records.append({
                "id": "P-D%03d" % n,
                "source_type": "LOCAL_DISCOVERY",
                "source_ref": service["source_url"],
                "retrieved_at": None,
                "verified_at": verified_date(service.get("verified_date")) or "",
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
            "verified_at": verified_date(rec.get("provenance", {}).get("verified_date")) or "",
            "claim_supported": rec["claim"][:200],
            "evidence_span": rec["claim"][:200],
            "authority_level": rec["authority"],
            "freshness_class": rec["freshness"],
            "conflicts_with": [],
            "chain_parent_id": None,
        })
        n += 1
    return records


def resolve_route_evidence(ctx: Context, route: Route) -> tuple[str | None, list[str], list[str]]:
    """RC-10: provenance that supports this specific route.

    A route's own evidence/provenance refs are ownership, not a global
    evidence pool. Local routes carry a service source_url; national routes
    carry a pre-resolved provenance id (P-K...). Only real http(s) URLs from
    structured service discovery are attached as source_url; knowledge
    records keep repo paths and never get fabricated URLs.
    """
    source_url = None
    evidence_ids = list(route.get("evidence_refs") or [])
    prov_records = provenance_records(ctx)
    prov_by_source: dict[str | None, str] = {}
    prov_by_id: dict[str, Provenance] = {}
    for p in prov_records:
        _ = prov_by_source.setdefault(p.get("source_ref"), p["id"])
        prov_by_id[p["id"]] = p
    prov_ids: list[str] = []
    for ref in route.get("provenance_refs") or []:
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


def claim_evidence(ctx: Context) -> dict[str, AttachedEvidence]:
    """RC-10: per-claim provenance resolution keyed by claim_id.

    Only provenance ids that exist in the emitted provenance records are
    attached; unresolved refs are dropped, never fabricated.
    """
    prov_records = provenance_records(ctx)
    prov_ids_all = {p["id"] for p in prov_records}
    prov_by_source: dict[str | None, str] = {}
    for p in prov_records:
        _ = prov_by_source.setdefault(p.get("source_ref"), p["id"])
    rec_by_eid = {rec.get("evidence_id"): rec
                  for rec in ctx.get("_s4_records", [])}
    out: dict[str, AttachedEvidence] = {}
    for c in ctx.get("_s7_claims", []):
        if c.get("state") != "VERIFIED":
            continue
        pids: list[str] = []
        for pid in c.get("provenance_ids") or []:
            resolved = pid if pid in prov_ids_all else prov_by_source.get(pid)
            if resolved and resolved not in pids:
                pids.append(resolved)
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


def retrieval_evidence(ctx: Context) -> RetrievalEvidence:
    return {"revision": "source-admission/v2", "per_track": ctx.get("_s4_admission", {}),
            "source_dates": {p["id"]: p["verified_at"] or None for p in provenance_records(ctx)},
            "safety_assessment": "LEXICAL_MATCH_ONLY" if ctx["safety"]["signals"] else "NO_SIGNAL_UNKNOWN"}


def dimension_sources(ctx: Context) -> dict[str, Evidence]:
    return {eid: source for route in ctx.get("_s6_routes", [])
            for eid, source in route.get("evidence_records", {}).items()}


def _uncertainty_list(ctx: Context) -> list[str]:
    items: list[str] = []
    if ctx.get("_s4_incomplete"):
        items.append("source_admission_incomplete")
    if ctx.get("_s5_incomplete"):
        items.append("local_availability_unverified")
    elif not ctx.get("_s5_steps"):
        items.append("local_availability_unverified")
    if ctx["epistemic_states"]["top_level"] != "FULLY_VERIFIED":
        items.append("answer_is_structured_placeholder")
    return items


def s11_output_emission(ctx: Context) -> None:
    failures = ctx["failures"]
    if any(f["state"] == "TERMINAL" for f in failures):
        ctx["_output"] = failed_output("terminal stage failure", stage="output_emission")
        mark_stage(ctx, "output_emission", StageState.TERMINAL, "terminal stage failure")
        return
    if ctx.get("_s5_incomplete"):
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
    route_evidence: dict[str, AttachedEvidence] = {}
    for r in evaluable:
        source_url, evidence_ids, prov_ids = resolve_route_evidence(ctx, r)
        entry: AttachedEvidence = {"evidence_ids": evidence_ids, "provenance_ids": prov_ids}
        if source_url:
            entry["source_url"] = source_url
        route_evidence[r["route_id"]] = entry
    claims = [c["value"] for c in ctx.get("_s7_claims", [])
              if c["state"] == "VERIFIED" ]
    top = ctx["epistemic_states"]["top_level"]
    output: Output = {
        "safety_priority": top_priority,
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
            "dimension_sources": dimension_sources(ctx),
            "source_admission": retrieval_evidence(ctx),
            "conflicts": [c["subject"] for c in ctx.get("_s7_conflicts", [])],
            "per_track_epistemic": ctx["epistemic_states"].get("per_track", {}),
            "route_evidence": route_evidence,
            "claim_evidence": claim_evidence(ctx),
            "safety_priority": top_priority,
        },
        "provenance": provenance_records(ctx),
        "epistemic_state": top,
        "failures": failures,
        "execution_status": execution_status,
        "no_route_asserted": not evaluable,
        "presented_as_complete": False,
    }
    output["safety_priority"] = top_priority
    validate_output(output)
    ctx["_output"] = output


def failed_output(message: str, stage: str = "input_normalization") -> Output:
    priority = "ACUTE_RISK_NOW"  # fail-closed placeholder, see INTERFACE_GAP-001
    output: Output = {
        "safety_priority": priority,
        "answer": ("Kan ikke svare: input ble avvist av S1-valideringen." if stage == "input_normalization"
                   else "Svaret kunne ikke fullfores. Ingen anbefaling vises."),
        "safety": {"priority": priority, "safety_class": None, "signals": [], "suppressed_routing": True},
        "tracks": [],
        "routes": [],
        "claims": [],
        "uncertainty_expressed": [],
        "evidence": {},
        "provenance": [],
        "epistemic_state": "UNVERIFIED",
        "failures": [
            {"stage": stage, "state": "TERMINAL", "message": message}
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


def stage_state(ctx: Context, stage: str) -> str:
    states = {failure["state"] for failure in ctx["failures"] if failure["stage"] == stage}
    for state in ("TERMINAL", "RECOVERABLE", "PARTIAL"):
        if state in states:
            return state
    return "SUCCESS"


def run_with_trace(input_dict: object, config: ConfigOverrides | None = None) -> tuple[Output, list[Trace]]:
    """Execute S1-S11 once; return (sut_output/v1 dict, stage trace list)."""
    cfg = default_config()
    if config:
        cfg.update(config)
    if not isinstance(input_dict, dict):
        return failed_output("INPUT_REJECTED"), [{"stage": "input_normalization", "state": "TERMINAL", "latency_ms": 0.0}]
    normalized = normalize_input(cast(object, input_dict))
    try:
        validate_input(normalized)
    except SchemaError:
        return failed_output("INPUT_REJECTED"), [
            {"stage": "input_normalization", "state": "TERMINAL", "latency_ms": 0.0}
        ]

    ctx = make_context(cast(Input, normalized))
    ctx["_config"] = cfg
    trace: list[Trace] = []
    for stage in _STAGE_ORDER:
        mark = execute_stage(stage, STAGES[stage], ctx)
        mark["state"] = stage_state(ctx, stage)
        trace.append(mark)
    return ctx.get("_output") or failed_output("output emission did not run", stage="output_emission"), trace


def run(input_dict: object, config: ConfigOverrides | None = None) -> Output:
    return run_with_trace(input_dict, config)[0]

_default_config = default_config
_with_state = execute_stage
_failed_output = failed_output
_stage_state = stage_state
_provenance_records = provenance_records
_route_evidence = resolve_route_evidence
_claim_evidence = claim_evidence
_retrieval_evidence = retrieval_evidence
_dimension_sources = dimension_sources
