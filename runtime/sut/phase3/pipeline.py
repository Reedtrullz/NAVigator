from typing import cast
from ..phase2.contracts import ConfigOverrides, Context, Input, Output, Trace

from ..context import make_context, normalize_input
from ..schemas import SchemaError, validate_input

from ..phase2.pipeline import (
    default_config,
    failed_output,
    execute_stage,
    stage_state,
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
from .finalize import s11_output_emission, failed_render_output

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

    ctx: Context = make_context(cast(Input, normalized))
    ctx["_config"] = cfg
    trace: list[Trace] = []
    for stage in _STAGE_ORDER:
        mark = execute_stage(stage, STAGES[stage], ctx)
        mark["state"] = stage_state(ctx, stage)
        trace.append(mark)
    return ctx.get("_output") or failed_render_output("output emission did not run"), trace


def run(input_dict: object, config: ConfigOverrides | None = None) -> Output:
    return run_with_trace(input_dict, config)[0]
