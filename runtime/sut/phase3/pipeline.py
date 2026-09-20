"""Phase 3 full SUT pipeline: S1-S11 end to end, deterministic.

S1-S8 are imported unmodified from the frozen Phase 2 pipeline (new lineage,
no edits to phase1/phase2 files). S9-S11 are the Phase 3 answer-planning,
rendering, and finalization stages.
"""

import time

from sut.context import StageState, make_context, mark_stage, normalize_input
from sut.schemas import SchemaError, validate_input

from sut.phase2.pipeline import (
    _default_config,
    _failed_output,
    s1_input_normalization,
    s2_safety_triage,
    s3_decomposition,
    s4_knowledge_retrieval,
    s5_local_discovery,
    s6_route_reasoning,
    s7_evidence_aggregation,
    s8_epistemic_assignment,
)
from sut.phase3.planner import s9_answer_planning
from sut.phase3.render import s10_answer_rendering
from sut.phase3.finalize import s11_output_emission

_STAGE_ORDER = (
    "input_normalization", "safety_triage", "decomposition",
    "knowledge_retrieval", "local_discovery", "route_reasoning",
    "evidence_aggregation", "epistemic_assignment", "answer_planning",
    "answer_rendering", "output_emission",
)

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


def _with_state(stage, fn, ctx):
    start = time.perf_counter()
    try:
        fn(ctx)
    except Exception as exc:  # fail closed: any stage crash becomes RECOVERABLE
        mark_stage(ctx, stage, StageState.RECOVERABLE, "stage error: %s" % exc)
    return {"stage": stage, "latency_ms": round((time.perf_counter() - start) * 1000, 3)}


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
    return ctx.get("_output") or _failed_output("output emission did not run"), trace


def run(input_dict, config=None):
    return run_with_trace(input_dict, config)[0]
