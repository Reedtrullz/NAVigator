"""Deterministic S5 local-discovery adapter (Phase 2).

Thin wrapper over the frozen V1 discovery runtime (replay mode). Absent
municipality or non-local tracks never trigger discovery. Any discovery
failure maps to DISCOVERY_INCOMPLETE - never a negative existence claim
(FC-03).
"""

import functools
import os
import sys

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from runtime.discovery.orchestrator import run_discovery  # noqa: E402
from runtime.discovery.protocol import ProtocolLoader  # noqa: E402


PROTOCOL_PATH = os.path.join(_REPO_ROOT, "data", "local-service-discovery-protocol-v1.json")
FIXTURES_PATH = os.path.join(
    _REPO_ROOT, "evaluation", "local-discovery-runtime-v1", "fixtures", "fixture-manifest.json")


@functools.lru_cache(maxsize=1)
def _protocol():
    loader = ProtocolLoader(PROTOCOL_PATH)
    return loader.load()


@functools.lru_cache(maxsize=1)
def _fixtures():
    import json
    with open(FIXTURES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def run_discovery_step(track, location_context=None, age=None, urgency=None):
    """Run one conditional discovery step for a track. Deterministic."""
    municipality = (location_context or {}).get("municipality")
    if not (track.get("needs_local_discovery") and municipality):
        return {
            "state": "NOT_APPLICABLE",
            "trigger_reason": None,
            "municipality": municipality,
            "services": [],
            "route_state": None,
            "execution_status": None,
            "access_methods": [],
            "self_referral": None,
            "evidence": [],
            "provenance_states": [],
            "failures": [],
        }
    try:
        raw = run_discovery(
            _protocol(),
            {"municipality": municipality, "age": age, "need": track.get("domain"),
             "urgency": urgency},
            fixtures=_fixtures(),
            mode="replay")
    except Exception as exc:  # fail-closed: runtime/loader errors
        return {
            "state": "DISCOVERY_INCOMPLETE",
            "trigger_reason": "DISCOVERY_TRIGGER_REASON",
            "municipality": municipality,
            "services": [],
            "route_state": "ROUTE_UNVERIFIED",
            "execution_status": "DISCOVERY_INCOMPLETE",
            "access_methods": [],
            "self_referral": None,
            "evidence": [],
            "provenance_states": ["ERROR_STATE"],
            "failures": [{"error": "DISCOVERY_RUNTIME_ERROR", "detail": str(exc)}],
        }
    incomplete = raw.get("execution_status") == "DISCOVERY_INCOMPLETE"
    return {
        "state": "DISCOVERY_INCOMPLETE" if incomplete else "COMPLETED",
        "trigger_reason": "DISCOVERY_TRIGGER_REASON",
        "municipality": municipality,
        "services": [
            {
                "name": s["name"],
                "source_url": s["source_url"],
                "state": s["state"],
                "access_methods": s["access_methods"],
                "self_referral": s["self_referral"],
                "age_text": s.get("age_text"),
                "age_eligible": s.get("age_input_eligible"),
                "target_group": s.get("target_group"),
                "strong_access": bool(
                    (s.get("access_markers") or {}).get("explicit_self_contact")
                    or "APPLICATION_FORM" in (s.get("access_methods") or [])
                    or "DIRECT_DROPIN" in (s.get("access_methods") or [])
                    or "DIRECT_EMAIL" in (s.get("access_methods") or [])
                ),
            }
            for s in raw.get("services", [])
        ],
        "route_state": raw.get("route_state"),
        "execution_status": raw.get("execution_status"),
        "access_methods": raw.get("access_methods", []),
        "self_referral": raw.get("self_referral"),
        "evidence": [
            {"field": e.get("field"), "value": e.get("value"), "source_url": e.get("source_url")}
            for e in raw.get("evidence", [])
        ],
        "provenance_states": ["ERROR_STATE"] if (raw.get("errors") or incomplete)
                             else ["DISCOVERY_RUN"],
        "failures": [
            {"error": e["error"], "url": e.get("url"), "detail": e.get("detail")}
            for e in raw.get("errors", [])
        ],
    }
