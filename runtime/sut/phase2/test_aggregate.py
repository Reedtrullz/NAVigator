import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase2.aggregate import (  # noqa: E402
    build_claims, collapse, derive_track_state, detect_conflicts,
)


def _route(state, age="VERIFIED", access="VERIFIED", contact="VERIFIED",
           exists="VERIFIED", relevant="VERIFIED"):
    return {
        "route_id": "R-TEST", "service_type": "Testtjeneste",
        "track_domain": "mental_health",
        "service_exists": exists, "age_eligible": age,
        "scenario_relevant": relevant, "access_verified": access,
        "contact_verified": contact, "route_state": state,
        "evidence_refs": ["E1"], "provenance_refs": ["P1"], "failures": [],
    }


class AggregateTests(unittest.TestCase):
    def test_claims_link_evidence_and_provenance(self):
        claims = build_claims([_route("FULLY_VERIFIED")], [])
        self.assertTrue(claims)
        for c in claims:
            self.assertTrue(c["evidence_ids"])
            self.assertTrue(c["provenance_ids"])

    def test_claim_without_evidence_unresolved(self):
        route = _route("EXISTENCE_ONLY", age="UNRESOLVED", access="UNRESOLVED", contact="UNRESOLVED")
        route["evidence_refs"] = []
        claims = build_claims([route], [])
        access = next(c for c in claims if c["dimension"] == "access_verified")
        self.assertEqual(access["state"], "UNRESOLVED")

    def test_conflict_marks_claim_unverified(self):
        claims = [
            {"claim_id": "C1", "subject": "RPH", "dimension": "age_eligible",
             "value": "over 16", "authority": "LAW", "evidence_ids": ["E1"],
             "provenance_ids": ["P1"]},
            {"claim_id": "C2", "subject": "RPH", "dimension": "age_eligible",
             "value": "under 18", "authority": "LAW", "evidence_ids": ["E2"],
             "provenance_ids": ["P2"]},
        ]
        result = detect_conflicts(claims)
        conflicts = result["conflicts"]
        self.assertEqual(len(conflicts), 1)
        conflicted = next(c for c in result["claims"]
                          if c["claim_id"] in ("C1", "C2") and c.get("conflict"))
        self.assertEqual(conflicted["state"], "UNVERIFIED")

    def test_no_conflict_for_agreeing_claims(self):
        claims = [
            {"claim_id": "C1", "subject": "RPH", "dimension": "age_eligible",
             "value": "over 16", "authority": "LAW", "evidence_ids": ["E1"],
             "provenance_ids": ["P1"]},
            {"claim_id": "C2", "subject": "RPH", "dimension": "age_eligible",
             "value": "over 16", "authority": "LAW", "evidence_ids": ["E2"],
             "provenance_ids": ["P2"]},
        ]
        result = detect_conflicts(claims)
        self.assertEqual(result["conflicts"], [])

    def test_track_state_from_routes(self):
        self.assertEqual(
            derive_track_state([_route("FULLY_VERIFIED")], [], {"state": "COMPLETED"}),
            "FULLY_VERIFIED")
        self.assertEqual(
            derive_track_state([_route("ACCESS_PARTIAL")], [], {"state": "COMPLETED"}),
            "ACCESS_PARTIAL")
        self.assertEqual(
            derive_track_state([_route("EXISTENCE_ONLY")], [], {"state": "COMPLETED"}),
            "EXISTENCE_ONLY")

    def test_knowledge_never_upgrades_track(self):
        # S4 may set EXISTENCE_ONLY at most; it can never push past it alone.
        state = derive_track_state([], [{"record_id": "K1"}], {"state": "NOT_APPLICABLE"})
        self.assertEqual(state, "EXISTENCE_ONLY")

    def test_discovery_incomplete_is_unverified(self):
        state = derive_track_state([], [], {"state": "DISCOVERY_INCOMPLETE"})
        self.assertEqual(state, "UNVERIFIED")

    def test_collapse_min_over_tracks(self):
        self.assertEqual(
            collapse(["FULLY_VERIFIED", "EXISTENCE_ONLY"]), "EXISTENCE_ONLY")
        self.assertEqual(
            collapse(["FULLY_VERIFIED", "UNVERIFIED"]), "UNVERIFIED")
        self.assertEqual(
            collapse(["ACCESS_PARTIAL", "EXISTENCE_ONLY"]), "EXISTENCE_ONLY")
        self.assertEqual(collapse(["FULLY_VERIFIED"]), "FULLY_VERIFIED")

    def test_collapse_empty_tracks_unverified(self):
        self.assertEqual(collapse([]), "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
