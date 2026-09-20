"""Typed DecisionContext factory and fail-closed stage-state marking."""

import enum
import copy

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


def normalize_input(sut_input):
    """Canonicalize supported caller shapes at the S1 input boundary.

    - profile.age: null -> key removed (unknown age is legitimate)
    - profile.household_children: true/false -> 1/0 (int kept)
    - profile.context: legacy alias for top-level context; dict values
      merge with the top-level value (top level wins on key conflicts),
      scalar values are wrapped as context.situational_context
    Malformed values are kept in place and fail closed in the strict
    post-normalization schema validation. Idempotent.
    """
    normalized = copy.deepcopy(sut_input)
    profile = normalized.get("profile")
    if isinstance(profile, dict):
        if "age" in profile and profile["age"] is None:
            del profile["age"]
        children = profile.get("household_children")
        if children is True:
            profile["household_children"] = 1
        elif children is False:
            profile["household_children"] = 0
        nested_context = profile.pop("context", None)
        if isinstance(nested_context, dict):
            merged = dict(nested_context)
            if isinstance(normalized.get("context"), dict):
                merged.update(normalized["context"])
            normalized["context"] = merged
        elif isinstance(nested_context, (str, int, float)):
            top = normalized.get("context")
            if isinstance(top, dict):
                top.setdefault("situational_context", nested_context)
            elif "context" not in normalized:
                normalized["context"] = {"situational_context": nested_context}
            else:
                # Unrepresentable combination: keep in profile so strict
                # post-normalization validation fails closed.
                profile["context"] = nested_context
        elif nested_context is not None:
            profile["context"] = nested_context
    return normalized


def make_context(sut_input):
    normalized = normalize_input(sut_input)
    validate_input(normalized)
    return {
        "input": normalized,
        "safety": {
            "priority": "TRIAGE_FAILED",
            "safety_class": None,
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
