import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase2.routes import build_route_candidates  # noqa: E402
from sut.phase2.discovery_adapter import run_discovery_step  # noqa: E402


def _disc(muni, age=19):
    return run_discovery_step(
        {"domain": "mental_health", "needs_local_discovery": True},
        location_context={"municipality": muni}, age=age)


class RouteTests(unittest.TestCase):
    def test_no_discovery_no_routes(self):
        disc = run_discovery_step(
            {"domain": "financial_support", "needs_local_discovery": False},
            location_context={"municipality": "Drammen"}, age=19)
        self.assertEqual(build_route_candidates(disc, track_domain="financial_support", age=19), [])

    def test_fully_verified_route(self):
        routes = build_route_candidates(_disc("Drammen"), track_domain="mental_health", age=19)
        self.assertTrue(routes)
        route = next(r for r in routes if r["service_type"] == "Rask Psykisk Helsehjelp")
        self.assertEqual(route["service_exists"], "VERIFIED")
        self.assertEqual(route["age_eligible"], "VERIFIED")
        self.assertEqual(route["access_verified"], "VERIFIED")
        self.assertEqual(route["contact_verified"], "VERIFIED")
        self.assertEqual(route["route_state"], "FULLY_VERIFIED")
        self.assertTrue(route["evidence_refs"])
        self.assertTrue(route["provenance_refs"])

    def test_access_partial_downgrade(self):
        routes = build_route_candidates(_disc("Bjerkreim"), track_domain="mental_health", age=19)
        self.assertEqual(routes[0]["route_state"], "ACCESS_PARTIAL")
        self.assertEqual(routes[0]["access_verified"], "PARTIAL")
        self.assertEqual(routes[0]["service_exists"], "VERIFIED")

    def test_existence_only_has_no_verified_access(self):
        routes = build_route_candidates(_disc("Raelingen"), track_domain="mental_health", age=19)
        self.assertEqual(routes[0]["route_state"], "EXISTENCE_ONLY")
        self.assertNotEqual(routes[0]["access_verified"], "VERIFIED")
        self.assertEqual(routes[0]["contact_verified"], "UNRESOLVED")

    def test_discovery_incomplete_never_positive_claims(self):
        routes = build_route_candidates(_disc("Oz"), track_domain="mental_health", age=19)
        self.assertEqual(routes, [])

    def test_downgrade_only_invariant(self):
        # No route may claim FULLY_VERIFIED without every required dimension.
        for muni in ("Drammen", "Alta", "Bjerkreim", "Raelingen", "Hasvik", "Orland"):
            routes = build_route_candidates(_disc(muni), track_domain="mental_health", age=19)
            for r in routes:
                if r["route_state"] == "FULLY_VERIFIED":
                    for dim in ("service_exists", "age_eligible", "scenario_relevant",
                                "access_verified", "contact_verified"):
                        self.assertEqual(r[dim], "VERIFIED", muni)

    def test_age_mismatch_downgrades_eligibility(self):
        routes = build_route_candidates(_disc("Drammen", age=13), track_domain="mental_health", age=13)
        rph = next(r for r in routes if r["service_type"] == "Rask Psykisk Helsehjelp")
        self.assertEqual(rph["age_eligible"], "FAILED")

    def test_required_fields_present(self):
        routes = build_route_candidates(_disc("Drammen"), track_domain="mental_health", age=19)
        required = {
            "route_id", "service_type", "track_domain", "target_population",
            "service_exists", "age_eligible", "scenario_relevant", "access_verified",
            "contact_verified", "access_model", "self_referral", "scope",
            "route_state", "evidence_refs", "provenance_refs", "failures",
        }
        for r in routes:
            self.assertTrue(required.issubset(r.keys()))


if __name__ == "__main__":
    unittest.main()
