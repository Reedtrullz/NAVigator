import copy
import unittest
from unittest.mock import patch
from typing import Any

from ..context import make_context
from .routes import build_route_candidates, build_national_route_candidates
from .aggregate import build_claims
from .pipeline import _default_config, s4_knowledge_retrieval, s8_epistemic_assignment
from .synthetic_fixtures import SyntheticCorpus
from . import discovery_adapter
from .discovery_adapter import run_discovery_step
from runtime.discovery.eligibility import age_in_bounds


def discovery_fixture() -> dict[str, Any]:
    service = {"service_id": "SERVICE_A", "name": "Service A", "state": "SERVICE_VERIFIED",
        "source_url": "https://city.kommune.no/services/a", "domain": "mental_health",
        "content_hash": "a" * 64, "age_bounds": {"min": 18, "max": 25},
        "age_text": "18-25 år", "age_eligible": True, "target_group": "adults",
        "strong_access": True, "access_methods": ["DIRECT_DROPIN"], "self_referral": True}
    rows = [{"service_id": "SERVICE_A", "source_url": service["source_url"],
             "content_hash": "a" * 64, "dimension": dim, "locator": "#service-a",
             "supporting_span": "Service A: 18-25 år. Drop-in for mental health.",
             "value": value}
            for dim, value in [("service_exists", "Service A"),
                               ("age_eligible", {"min": 18, "max": 25}),
                               ("scenario_relevant", "mental_health"),
                               ("access_verified", "DIRECT_DROPIN"),
                               ("contact_verified", "DIRECT_DROPIN")]]
    return {"state": "COMPLETED", "route_state": "ROUTE_ACCESS_PARTIAL",
            "services": [service], "evidence": rows}


class EvidenceIntegrityTests(unittest.TestCase):
    def test_strict_and_invalid_age_bounds(self):
        self.assertFalse(age_in_bounds({"min": 18, "max": None}, 18, "over 18 år"))
        self.assertFalse(age_in_bounds({"min": None, "max": 18}, 18, "under 18 år"))
        self.assertIsNone(age_in_bounds({"min": 30, "max": 18}, 19))
        self.assertIsNone(age_in_bounds({"min": 18, "max": 25}, True))

    def test_adapter_retains_explicit_evidence_without_inventing_missing_fields(self):
        d = discovery_fixture()
        raw = {**d, "execution_status": "COMPLETE", "errors": []}
        with patch.object(discovery_adapter, "run_discovery", return_value=raw), \
                patch.object(discovery_adapter, "_protocol", return_value={}), \
                patch.object(discovery_adapter, "_fixtures", return_value={}):
            result = run_discovery_step({"domain": "mental_health", "needs_local_discovery": True},
                                        {"municipality": "Synthetic"}, age=19)
        self.assertEqual(result["evidence"], d["evidence"])
        self.assertEqual(build_route_candidates(result, "mental_health", 19)[0]["route_state"], "FULLY_VERIFIED")

    def test_other_service_evidence_rejected_even_on_same_page(self):
        d = discovery_fixture()
        for row in d["evidence"]:
            row["service_id"] = "SERVICE_B"
        route = build_route_candidates(d, "mental_health", age=19)[0]
        self.assertEqual(route["route_state"], "UNVERIFIED")
        self.assertEqual(route["evidence_refs"], [])

    def test_identity_or_marker_mismatch_in_excerpt_cannot_verify_dimension(self):
        for span in ("Service B: Drop-in for mental health.", "Service A: mental health. No access evidence here."):
            d = discovery_fixture()
            d["evidence"][3]["supporting_span"] = span
            route = build_route_candidates(d, "mental_health", 19)[0]
            self.assertEqual(route["access_verified"], "UNRESOLVED")

    def test_run_access_not_inherited(self):
        d = discovery_fixture()
        d["services"][0]["strong_access"] = False
        d["services"][0]["access_methods"] = ["UNCLEAR"]
        route = build_route_candidates(d, "mental_health", age=19)[0]
        self.assertEqual(route["access_verified"], "UNRESOLVED")

    def test_age_presence_not_eligibility_and_actual_bounds_compared(self):
        d = discovery_fixture()
        for age, expected in [(13, "FAILED"), (19, "VERIFIED"), (None, "UNRESOLVED")]:
            self.assertEqual(build_route_candidates(d, "mental_health", age)[0]["age_eligible"], expected)
        self.assertEqual(build_route_candidates(d, "mental_health", 13)[0]["route_state"], "UNVERIFIED")
        d["services"][0].pop("age_bounds")
        self.assertEqual(build_route_candidates(d, "mental_health", 19)[0]["age_eligible"], "UNRESOLVED")

    def test_age_metadata_must_match_actual_excerpt(self):
        d = discovery_fixture()
        d["evidence"][1]["supporting_span"] = "Service A: for 30-40 år."
        self.assertEqual(build_route_candidates(d, "mental_health", 19)[0]["age_eligible"], "UNRESOLVED")

    def test_each_dimension_needs_its_own_excerpt_locator_hash_and_value(self):
        for mutation in ["locator", "supporting_span", "content_hash", "value"]:
            d = discovery_fixture()
            row = d["evidence"][3]
            row[mutation] = "" if mutation != "value" else "OTHER_ACCESS"
            route = build_route_candidates(d, "mental_health", 19)[0]
            self.assertEqual(route["access_verified"], "UNRESOLVED", mutation)
        d = discovery_fixture()
        route = build_route_candidates(d, "mental_health", 19)[0]
        claims = build_claims([route], [])
        existence = next(c for c in claims if c["dimension"] == "service_exists")
        access = next(c for c in claims if c["dimension"] == "access_verified")
        self.assertTrue(existence["evidence_ids"])
        self.assertTrue(access["evidence_ids"])
        self.assertTrue(set(existence["evidence_ids"]).isdisjoint(access["evidence_ids"]))

    def test_independent_track_uncertainty(self):
        d = discovery_fixture()
        mh = build_route_candidates(d, "mental_health", 19)[0]
        ctx: dict[str, Any] = make_context({"case_id": "SYNTHETIC", "user_query": "bolig og angst", "profile": {}})
        ctx["_s6_routes"] = [mh]
        ctx["_s4_records"] = []
        ctx["_s4_admission"] = {"T1": {"failures": []}, "T2": {"failures": [{"reason": "FILE_MISSING"}]}}
        ctx["_s5_steps"] = [{"track_id": "T1", "domain": "mental_health", "step": d},
                            {"track_id": "T2", "domain": "housing", "step": {"state": "COMPLETED"}}]
        s8_epistemic_assignment(ctx)
        self.assertEqual(ctx["epistemic_states"]["per_track"], {"T1": "FULLY_VERIFIED", "T2": "UNVERIFIED"})

    def test_evidence_ids_unique_across_tracks(self):
        c = SyntheticCorpus(self)
        c.add_doc("a", "angst support", domain="mental_health")
        c.add_doc("b", "bolig support", domain="housing")
        ctx: dict[str, Any] = make_context({"case_id": "SYNTHETIC", "user_query": "angst bolig", "profile": {}})
        ctx["tracks"] = [{"track_id": "T1", "domain": "mental_health"}, {"track_id": "T2", "domain": "housing"}]
        cfg = _default_config()
        cfg.update(knowledge_index_path=str(c.index), knowledge_repo_root=str(c.root),
                   rules_registry_path=str(c.rules), knowledge_access_profile=c.profile)
        ctx["_config"] = cfg
        s4_knowledge_retrieval(ctx)
        ids = [r["evidence_id"] for r in ctx["_s4_records"]]
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(set(ids)), 2)
        other = copy.deepcopy(discovery_fixture())
        other["services"][0]["domain"] = "housing"
        other["evidence"][2]["value"] = "housing"
        routes = build_route_candidates(discovery_fixture(), "mental_health", 19) + build_route_candidates(other, "housing", 19)
        self.assertTrue(set(routes[0]["evidence_refs"]).isdisjoint(routes[1]["evidence_refs"]))

    def test_national_reasoning_uses_only_admitted_context_and_never_reopens_a_path(self):
        record = {"source_type": "PROJECT_RESEARCH", "domain": "housing", "gap_state": None,
                  "historical_research": False, "freshness": "CURRENT",
                  "claim": "bolig support", "evidence_id": "E-D001", "record_id": "K-D001",
                  "provenance": {"verified_date": "2026-10-01"},
                  "source_reference": {"path": "PRIVATE_CANARY.md"},
                  "source_lines": ["### Public Service", "bolig support"]}
        with patch("builtins.open", side_effect=AssertionError("unauthorized secondary read")):
            routes = build_national_route_candidates([record])
        self.assertEqual(routes[0]["service_type"], "Public Service")
