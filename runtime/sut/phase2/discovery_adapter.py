"""Deterministic S5 local-discovery adapter (Phase 2).

Thin wrapper over the frozen V1 discovery runtime (replay mode). Absent
municipality or non-local tracks never trigger discovery. Any discovery
failure maps to DISCOVERY_INCOMPLETE - never a negative existence claim
(FC-03).
"""

import functools
import os
import sys
import json
from collections.abc import Mapping
from typing import cast
from runtime.type_support import object_list, object_mapping, string, strings
from runtime.discovery.contracts import ProtocolDefinition
from .contracts import DiscoveryStep, Location, Service

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from runtime.discovery.orchestrator import run_discovery  # noqa: E402
from runtime.discovery.protocol import ProtocolLoader  # noqa: E402


PROTOCOL_PATH = os.path.join(_REPO_ROOT, "data", "local-service-discovery-protocol-v1.json")
FIXTURES_PATH = os.path.join(
    _REPO_ROOT, "evaluation", "local-discovery-runtime-v1", "fixtures", "fixture-manifest.json")


@functools.lru_cache(maxsize=1)
def _protocol() -> ProtocolDefinition:
    loader = ProtocolLoader(PROTOCOL_PATH)
    return loader.load()


@functools.lru_cache(maxsize=1)
def _fixtures() -> object:
    with open(FIXTURES_PATH, encoding="utf-8") as fh:
        return cast(object, json.load(fh))


def _service(value: object) -> Service:
    fields = object_mapping(value)
    referral = fields.get("self_referral")
    if referral is not None and not isinstance(referral, (str, bool)):
        raise ValueError("Invalid referral")
    markers = object_mapping(fields.get("access_markers") or {})
    result: Service = {
        "name": string(fields["name"]), "source_url": string(fields["source_url"]),
        "state": string(fields["state"]), "access_methods": strings(fields["access_methods"]),
        "self_referral": referral, "age_text": None, "age_eligible": None, "target_group": None,
        "strong_access": bool(markers.get("explicit_self_contact")
                              or "APPLICATION_FORM" in strings(fields.get("access_methods") or [])
                              or "DIRECT_DROPIN" in strings(fields.get("access_methods") or [])
                              or "DIRECT_EMAIL" in strings(fields.get("access_methods") or [])),
    }
    if "service_id" in fields:
        result["service_id"] = string(fields["service_id"])
    if "domain" in fields:
        result["domain"] = string(fields["domain"])
    if "content_hash" in fields:
        result["content_hash"] = string(fields["content_hash"])
    if "verified_date" in fields:
        value = fields["verified_date"]
        result["verified_date"] = None if value is None else string(value)
    if fields.get("age_text") is not None:
        result["age_text"] = string(fields["age_text"])
    if fields.get("target_group") is not None:
        result["target_group"] = string(fields["target_group"])
    eligible = fields.get("age_input_eligible")
    if eligible is not None and not isinstance(eligible, bool):
        raise ValueError("Invalid age eligibility")
    result["age_eligible"] = eligible
    if "age_bounds" in fields:
        bounds = fields["age_bounds"]
        if bounds is None:
            result["age_bounds"] = None
        else:
            parsed: dict[str, int | None] = {}
            for key, bound in object_mapping(bounds).items():
                if bound is not None and (not isinstance(bound, int) or isinstance(bound, bool)):
                    raise ValueError("Invalid age bound")
                parsed[key] = bound
            result["age_bounds"] = parsed
    return result


def run_discovery_step(track: Mapping[str, object], location_context: Location | None = None,
                       age: int | None = None, urgency: str | None = None) -> DiscoveryStep:
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
        domain = track.get("domain")
        if domain is not None:
            domain = string(domain)
        raw = object_mapping(run_discovery(
            _protocol(),
            {"municipality": municipality, "age": age, "need": domain,
             "urgency": urgency},
            fixtures=_fixtures(),
            mode="replay"))
        incomplete = raw.get("execution_status") == "DISCOVERY_INCOMPLETE"
        return {
            "state": "DISCOVERY_INCOMPLETE" if incomplete else "COMPLETED",
            "trigger_reason": "DISCOVERY_TRIGGER_REASON",
            "municipality": municipality,
            "services": [_service(value) for value in object_list(raw.get("services", []))],
            "route_state": None if raw.get("route_state") is None else string(raw["route_state"]),
            "execution_status": None if raw.get("execution_status") is None else string(raw["execution_status"]),
            "access_methods": strings(raw.get("access_methods", [])),
            "self_referral": None if raw.get("self_referral") is None else string(raw["self_referral"]),
            "evidence": [
                {key: value for key, value in object_mapping(item).items()
                 if key in ("field", "value", "source_url", "service_id", "content_hash",
                            "dimension", "locator", "supporting_span", "verified_date")}
                for item in object_list(raw.get("evidence", []))
            ],
            "provenance_states": ["ERROR_STATE"] if (raw.get("errors") or incomplete)
                                 else ["DISCOVERY_RUN"],
            "failures": [
                {"error": string(e["error"]),
                 "url": None if e.get("url") is None else string(e["url"]),
                 "detail": None if e.get("detail") is None else string(e["detail"])}
                for e in (object_mapping(value) for value in object_list(raw.get("errors", [])))
            ],
        }
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
            "failures": [{"error": "DISCOVERY_RUNTIME_ERROR", "detail": type(exc).__name__}],
        }
