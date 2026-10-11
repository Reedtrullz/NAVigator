from typing import Any

from ..context import make_context, normalize_input
from ..schemas import SchemaError, validate_input

from ..phase2.pipeline import (
    _default_config,
    _failed_output,
    _with_state,
    _stage_state,
    s1_input_normalization,
    s2_safety_triage,
    s3_decomposition,
    s4_knowledge_retrieval,
    s5_local_discovery,
    s6_route_reasoning,
    s7_evidence_aggregation,
    s8_epistemic_assignment,
)
from .planner import s9_answer_planning
from .render import s10_answer_rendering
from .finalize import s11_output_emission, _failed_render_output

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


def run_with_trace(input_dict, config=None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Execute S1-S11 once; return (sut_output/v1 dict, stage trace list)."""
    cfg = dict(_default_config())
    if config:
        cfg.update(config)
    if not isinstance(input_dict, dict):
        return _failed_output("INPUT_REJECTED"), [{"stage": "input_normalization", "state": "TERMINAL", "latency_ms": 0.0}]
    normalized = normalize_input(input_dict)
    try:
        validate_input(normalized)
    except SchemaError:
        return _failed_output("INPUT_REJECTED"), [
            {"stage": "input_normalization", "state": "TERMINAL", "latency_ms": 0.0}
        ]

    ctx: dict[str, Any] = make_context(normalized)
    ctx["_config"] = cfg
    trace = []
    for stage in _STAGE_ORDER:
        mark = _with_state(stage, STAGES[stage], ctx)
        mark["state"] = _stage_state(ctx, stage)
        trace.append(mark)
    return ctx.get("_output") or _failed_render_output("output emission did not run"), trace


def run(input_dict, config=None):
    return run_with_trace(input_dict, config)[0]
