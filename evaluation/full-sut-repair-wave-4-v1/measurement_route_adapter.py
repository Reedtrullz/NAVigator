"""Measurement V3.1 route object adapter (Wave 4 Phase B).

Pure observation layer over serialized SUT route semantics. Reads the
structured route object when present; falls back to labels only through
the explicitly separated legacy function. Never scores, never compares
against gold, never mutates the answer. Stdlib only.
"""

STRUCTURED = "STRUCTURED_V2_2"
LEGACY = "LEGACY_LABELS_ONLY"

_EVALUABLE_STATES = frozenset({
    "FULLY_VERIFIED", "EXISTENCE_ONLY", "ACCESS_PARTIAL", "PARTIAL",
})


def _obs_from_structured(entry):
    return {
        "route_id": entry.get("route_id"),
        "identity": entry.get("service_identity"),
        "display_label": entry.get("display_label"),
        "target": entry.get("target_population"),
        "access_model": entry.get("access_model"),
        "conditions": entry.get("dims") or {},
        "track_domain": entry.get("track_domain"),
        "route_state": entry.get("route_state"),
        "evidence_refs": entry.get("evidence_refs") or [],
        "provenance_refs": entry.get("provenance_refs") or [],
        "evaluable": bool(entry.get("service_identity"))
                     and entry.get("route_state") != "UNVERIFIED",
    }


def _obs_from_label(label):
    return {
        "route_id": None,
        "identity": None,
        "display_label": label,
        "target": None,
        "access_model": None,
        "conditions": {},
        "track_domain": None,
        "route_state": None,
        "evidence_refs": [],
        "provenance_refs": [],
        "evaluable": None,
    }


def observe_routes(answer):
    """Observe routes from a serialized SUT answer dict.

    Returns {"mode": ..., "routes": [...], "no_route_asserted": ...}.
    Structured mode requires evidence.structured_routes to be a non-empty
    list; anything else fail-closes to the legacy observation path.
    """
    if not isinstance(answer, dict):
        return observe_routes_legacy(answer)
    evidence = answer.get("evidence") or {}
    structured = evidence.get("structured_routes")
    if isinstance(structured, list) and structured:
        return {
            "mode": STRUCTURED,
            "routes": [_obs_from_structured(e) for e in structured],
            "no_route_asserted": bool(answer.get("no_route_asserted")),
        }
    return observe_routes_legacy(answer)


def observe_routes_legacy(answer):
    """Labels-only observation for historical predictions (explicitly
    separated; preserves pre-Wave-4 behavior)."""
    labels = answer.get("routes") if isinstance(answer, dict) else None
    if not isinstance(labels, list):
        labels = []
    return {
        "mode": LEGACY,
        "routes": [_obs_from_label(lab) for lab in labels if lab],
        "no_route_asserted": bool(answer.get("no_route_asserted"))
                             if isinstance(answer, dict) else True,
    }
