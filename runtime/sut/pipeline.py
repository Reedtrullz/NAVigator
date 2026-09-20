"""S1-S11 pass-through skeleton for the full SUT.

Each stage has signature stage(ctx) -> ctx. Phase 1 implements structure and
fail-closed state accounting only: S2 verifies the safety rule file (FC-01)
but performs no triage evaluation, S4/S5/S6 are explicitly not implemented,
and no stage fabricates routes, claims, or provenance.
"""

import hashlib
import json
import time

from sut.context import StageState, mark_stage
from sut.schemas import SchemaError, validate_input, validate_output
from sut.context import normalize_input


PHASE_1_ANSWER = (
    "Kan ikke svare: sikkerhetsvurdering (S2) og kunnskapshenting (S4/S5/S6) "
    "er ikke aktivert i Phase 1-skjelettet. Ingen rute er verifisert."
)

_STAGE_ORDER = (
    "input_normalization",
    "safety_triage",
    "decomposition",
    "knowledge_retrieval",
    "local_discovery",
    "route_reasoning",
    "evidence_aggregation",
    "epistemic_assignment",
    "answer_planning",
    "answer_rendering",
    "output_emission",
)


def _default_config():
    return {
        "mode": "replay",
        "safety_rules_path": "data/safety-triage-rules-v1.json",
        "rules_registry_path": "data/rules-v1.json",
    }


def _with_state(stage, fn, ctx):
    start = time.perf_counter()
    try:
        fn(ctx)
    except Exception as exc:  # fail closed: any stage crash becomes RECOVERABLE
        mark_stage(ctx, stage, StageState.RECOVERABLE, "stage error: %s" % exc)
    return {"stage": stage, "latency_ms": round((time.perf_counter() - start) * 1000, 3)}


def s1_input_normalization(ctx):
    # Validation already happened in make_context via validate_input;
    # normalization: trim query whitespace.
    ctx["input"]["user_query"] = ctx["input"]["user_query"].strip()


def s2_safety_triage(ctx):
    path = ctx["_config"]["safety_rules_path"]
    try:
        with open(path, "rb") as f:
            raw = f.read()
        rules = json.loads(raw.decode("utf-8"))
        if not isinstance(rules.get("acute_signals"), list) or not rules["acute_signals"]:
            raise ValueError("acute_signals missing or empty")
        ctx["safety"]["rule_file_sha256"] = hashlib.sha256(raw).hexdigest()
    except Exception as exc:
        mark_stage(ctx, "safety_triage", StageState.TERMINAL, "FC-01: safety rules unavailable: %s" % exc)
        return
    # Phase 1: rules verified, evaluation not implemented. The skeleton
    # cannot answer honestly without a verifiable safety layer (FC-01),
    # so this is TERMINAL: execution fails closed, nothing is presented.
    mark_stage(
        ctx,
        "safety_triage",
        StageState.TERMINAL,
        "FC-01: safety triage evaluation not implemented in Phase 1; "
        "unverifiable safety layer must not answer (rules file sha recorded)",
    )


def s3_decomposition(ctx):
    # Conservative single-track fallback is the minimal correct behavior.
    pass


def s4_knowledge_retrieval(ctx):
    mark_stage(
        ctx,
        "knowledge_retrieval",
        StageState.RECOVERABLE,
        "knowledge retrieval not implemented in Phase 1",
    )


def s5_local_discovery(ctx):
    mark_stage(
        ctx,
        "local_discovery",
        StageState.RECOVERABLE,
        "local discovery not run in Phase 1 skeleton (mode: %s)" % ctx["_config"]["mode"],
    )


def s6_route_reasoning(ctx):
    mark_stage(
        ctx,
        "route_reasoning",
        StageState.RECOVERABLE,
        "route reasoning not implemented in Phase 1; no routes fabricated",
    )


def s7_evidence_aggregation(ctx):
    # Pass-through of empty maps cannot fail (fail-closed contract).
    pass


def s8_epistemic_assignment(ctx):
    # Defaults to UNVERIFIED on unresolvable input: already UNVERIFIED.
    pass


def s9_answer_planning(ctx):
    ctx["answer_plan"] = {
        "blocks": [
            {"order": 1, "kind": "FAILURE_NOTICE", "track_id": None, "route_label": None, "span_refs": []},
            {"order": 2, "kind": "INFO", "track_id": "T1", "route_label": None, "span_refs": []},
        ],
        "no_route_asserted": True,
        "presented_as_complete": False,
    }


def s10_answer_rendering(ctx):
    ctx["_answer"] = PHASE_1_ANSWER


def s11_output_emission(ctx):
    failures = ctx["failures"]
    if any(f["state"] == "TERMINAL" for f in failures):
        execution_status = "EXECUTION_FAILED"
    elif any(f["stage"] == "local_discovery" and f["state"] == "RECOVERABLE" for f in failures):
        execution_status = "DISCOVERY_INCOMPLETE"
    else:
        execution_status = "SUCCESS"

    # INTERFACE_GAP-001: decision-context-v1 allows safety.priority
    # TRIAGE_FAILED, sut-output-v1 does not. Unverified/failed triage maps
    # to the worst-case enum value as a fail-closed placeholder; the
    # accompanying failure record and presented_as_complete=false carry the
    # honesty. A placeholder is never emitted when a verified verdict exists.
    priority = ctx["safety"]["priority"]
    if priority not in ("ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE"):
        priority = "ACUTE_RISK_NOW"
    output = {
        "answer": ctx.get("_answer", PHASE_1_ANSWER),
        "safety": {
            "priority": priority,
            "signals": ctx["safety"]["signals"],
            "suppressed_routing": ctx["safety"]["suppressed_routing"],
        },
        "tracks": [
            {"track_id": t["track_id"], "domain": t["domain"], "status": "FAILED"}
            for t in ctx["tracks"]
        ],
        "routes": [],
        "claims": [],
        "uncertainty_expressed": [
            "safety_priority_unverified",
            "knowledge_unverified",
            "local_availability_unverified",
        ],
        "evidence": ctx["evidence"],
        "provenance": ctx["provenance"],
        "epistemic_state": ctx["epistemic_states"]["top_level"],
        "failures": failures,
        "execution_status": execution_status,
        "no_route_asserted": True,
        "presented_as_complete": False,
    }
    # safety_priority mirror: always present for scorer compatibility; in the
    # placeholder case it mirrors the worst-case mapping, not a verdict.
    output["safety_priority"] = priority
    validate_output(output)
    ctx["_output"] = output


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

    from sut.context import make_context

    ctx = make_context(normalized)
    ctx["_config"] = cfg
    trace = []
    for stage in _STAGE_ORDER:
        mark = _with_state(stage, STAGES[stage], ctx)
        mark["state"] = _stage_state(ctx, stage)
        trace.append(mark)
    return ctx["_output"], trace


def _stage_state(ctx, stage):
    for failure in ctx["failures"]:
        if failure["stage"] == stage:
            return failure["state"]
    return "SUCCESS"


def run(input_dict, config=None):
    return run_with_trace(input_dict, config)[0]
