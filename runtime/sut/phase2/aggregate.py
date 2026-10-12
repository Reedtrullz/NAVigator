"""Deterministic S7 evidence aggregation + S8 epistemic collapse (Phase 2).

Canonical wiring: claim -> evidence IDs -> provenance IDs. Two authoritative
sources in conflict -> conflict record + claim downgraded to UNVERIFIED.
Epistemic collapse follows the frozen epistemic-state contract: top-level
state = min over tracks (FULLY_VERIFIED > ACCESS_PARTIAL > EXISTENCE_ONLY >
UNVERIFIED).
"""

from typing import Literal
from .contracts import Aggregate, Claim, Conflict, DiscoveryStep, KnowledgeRecord, Route


STATE_ORDER = ("UNVERIFIED", "EXISTENCE_ONLY", "ACCESS_PARTIAL", "FULLY_VERIFIED")


def _dimension_claims() -> tuple[Literal["service_exists", "age_eligible", "scenario_relevant", "access_verified", "contact_verified"], ...]:
    dims = ("service_exists", "age_eligible", "scenario_relevant",
            "access_verified", "contact_verified")
    return dims


def build_claims(routes: list[Route], knowledge_records: list[KnowledgeRecord]) -> list[Claim]:
    """Materialize per-dimension claims for each route."""
    claims: list[Claim] = []
    n = 1
    for route in routes:
        for dim in _dimension_claims():
            value = route[dim]
            refs = route.get("dimension_evidence", {}).get(dim, [])
            if value in ("VERIFIED", "PARTIAL") and not refs:
                value = "UNRESOLVED"
            state = "VERIFIED" if value == "VERIFIED" else (
                "FAILED" if value == "FAILED" else "UNRESOLVED")
            claims.append({
                "claim_id": "C-%03d" % n,
                "subject": route["route_id"],
                "dimension": dim,
                "value": value,
                "state": state,
                "authority": "DISCOVERY" if route["evidence_refs"] else "NONE",
                "evidence_ids": list(refs) if state == "VERIFIED" else [],
                "provenance_ids": list(route["provenance_refs"]) if state == "VERIFIED" else [],
            })
            n += 1
    for rec in knowledge_records:
        factual = (not rec.get("gap_state") and rec.get("source_type") != "GAP"
                   and not rec.get("historical_research") and rec.get("freshness") == "CURRENT"
                   and bool(rec.get("provenance", {}).get("verified_date")))
        claims.append({
            "claim_id": "C-%03d" % n,
            "subject": rec["record_id"],
            "dimension": "knowledge_fact",
            "value": rec["claim"],
            "state": "VERIFIED" if factual else "UNRESOLVED",
            "authority": rec["authority"],
            "evidence_ids": [rec["evidence_id"]] if factual else [],
            "provenance_ids": [rec["record_id"]] if factual else [],
        })
        n += 1
    return claims


def detect_conflicts(claims: list[Claim]) -> Aggregate:
    """Detect same subject+dimension with disagreeing authoritative values."""
    groups: dict[tuple[str, str], list[Claim]] = {}
    for c in claims:
        key = (c["subject"], c["dimension"])
        groups.setdefault(key, []).append(c)
    conflicts: list[Conflict] = []
    for (subject, dim), group in groups.items():
        values = {c["value"] for c in group if c["authority"] in ("LAW", "DISCOVERY")}
        if len(values) > 1:
            conflicts.append({
                "subject": subject,
                "dimension": dim,
                "claim_ids": [c["claim_id"] for c in group],
                "values": sorted(str(v) for v in values),
            })
            for c in group:
                c["conflict"] = True
                c["state"] = "UNVERIFIED"
    return {"claims": claims, "conflicts": conflicts}


def derive_track_state(routes: list[Route], knowledge_records: list[KnowledgeRecord], discovery: DiscoveryStep | None) -> str:
    """S8 per-track epistemic state; downgrades only."""
    discovery_state = discovery.get("state") if discovery else None
    if discovery_state == "DISCOVERY_INCOMPLETE":
        return "UNVERIFIED"
    states: list[str] = []
    for route in routes:
        rs = route.get("route_state")
        if rs == "FULLY_VERIFIED" and all(
                route[d] == "VERIFIED" for d in _dimension_claims()):
            states.append("FULLY_VERIFIED")
        elif rs in ("FULLY_VERIFIED", "ACCESS_PARTIAL"):
            states.append("ACCESS_PARTIAL")
        elif rs == "EXISTENCE_ONLY":
            states.append("EXISTENCE_ONLY")
        else:
            states.append("UNVERIFIED")
    if not states and any(c["state"] == "VERIFIED" for c in build_claims([], knowledge_records)):
        # S4 alone can only ever justify EXISTENCE_ONLY.
        return "EXISTENCE_ONLY"
    if not states:
        return "UNVERIFIED"
    return states[0] if len(set(states)) == 1 else min(states, key=STATE_ORDER.index)


def collapse(track_states: list[str]) -> str:
    """Frozen S8 doctrine: top-level = min over tracks."""
    if not track_states:
        return "UNVERIFIED"
    return min(track_states, key=STATE_ORDER.index)
