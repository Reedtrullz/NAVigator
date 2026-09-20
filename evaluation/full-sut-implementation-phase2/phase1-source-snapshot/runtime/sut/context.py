"""Typed DecisionContext factory and fail-closed stage-state marking."""

import enum

from sut.schemas import validate_context, validate_input


class StageState(enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    RECOVERABLE = "RECOVERABLE"
    TERMINAL = "TERMINAL"


STAGE_NAMES = (
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


def make_context(sut_input):
    validate_input(sut_input)
    return {
        "input": sut_input,
        "safety": {
            "priority": "TRIAGE_FAILED",
            "signals": [],
            "suppressed_routing": True,
            "rule_file_sha256": None,
        },
        "tracks": [
            {
                "track_id": "T1",
                "domain": "general",
                "sub_utterance": sut_input["user_query"],
                "status": "PENDING",
                "needs_local_discovery": False,
            }
        ],
        "candidate_routes": [],
        "evidence": {},
        "provenance": [],
        "claim_states": [],
        "epistemic_states": {"top_level": "UNVERIFIED", "per_route": []},
        "failures": [],
        "answer_plan": {
            "blocks": [],
            "no_route_asserted": True,
            "presented_as_complete": False,
        },
    }


def mark_stage(ctx, stage, state, message=""):
    if stage not in STAGE_NAMES:
        raise ValueError("unknown stage: %r" % (stage,))
    if isinstance(state, str):
        state = StageState(state)
    if state is StageState.SUCCESS:
        return
    record = {"stage": stage, "state": state.value, "message": message}
    ctx["failures"].append(record)
