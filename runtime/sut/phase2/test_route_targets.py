"""RC-07 structured route-target tests (spec section 17 matrix)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase2.routes import (  # noqa: E402
    build_national_route_candidates,
    _national_service_name,
)


def record(eid, claim, domain="mental_health", track=None, freshness="CURRENT"):
    rec = {
        "record_id": "K-" + eid,
        "source_type": "PROJECT_RESEARCH",
        "domain": domain,
        "domains": [domain],
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": "x.md"},
        "authority": "INTERNAL_DOC",
        "freshness": freshness,
        "evidence_id": eid,
        "provenance": {},
        "gap_state": None,
        "historical_research": False,
    }
    if track:
        rec["track_domain"] = track
    return rec


class NationalServiceNameTests(unittest.TestCase):
    def test_bold_service_name_accepted(self):
        name = _national_service_name("- **Rask psykisk helsehjelp**: Gratis tilbud.")
        self.assertEqual(name, "Rask psykisk helsehjelp")

    def test_numeric_fact_rejected(self):
        self.assertIsNone(_national_service_name('HFU er dokumentert "opptil 20 ar" i fil 25.'))

    def test_table_fragment_rejected(self):
        self.assertIsNone(_national_service_name(
            "| Helsestasjon for ungdom (HFU) | Rådgivning opptil 20 år |"))

    def test_heading_rejected(self):
        self.assertIsNone(_national_service_name("## 4. Rask psykisk helsehjelp (RPH)"))


class NationalRouteCandidateTests(unittest.TestCase):
    def test_structured_route_from_current_record(self):
        routes = build_national_route_candidates(
            [record("E-D001", "- **Rask psykisk helsehjelp**: Gratis tilbud.")])
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "Rask psykisk helsehjelp")
        self.assertEqual(routes[0]["track_domain"], "mental_health")
        self.assertEqual(routes[0]["scope"], "NATIONAL")
        self.assertEqual(routes[0]["route_state"], "EXISTENCE_ONLY")

    def test_track_binding_uses_retrieval_stamp(self):
        routes = build_national_route_candidates(
            [record("E-D001", "- **Fastlege**: First contact.",
                    domain="legal_rights", track="housing")])
        self.assertEqual(routes[0]["track_domain"], "housing")

    def test_gap_and_historical_records_excluded(self):
        gap = record("E-D001", "- **Noe**: x")
        gap["gap_state"] = "REGISTERED_GAP"
        hist = record("E-D002", "- **Noe annet**: x")
        hist["historical_research"] = True
        self.assertEqual(build_national_route_candidates([gap, hist]), [])

    def test_unsupported_claims_produce_no_route(self):
        routes = build_national_route_candidates(
            [record("E-D001", "Kommunen skal vurdere behovet for hjelp.")])
        self.assertEqual(routes, [])

    def test_multi_track_routes_bind_independently(self):
        routes = build_national_route_candidates([
            record("E-D001", "- **Tjeneste A**: x", track="mental_health"),
            record("E-D002", "- **Tjeneste B**: x", track="housing"),
        ])
        self.assertEqual([r["track_domain"] for r in routes],
                         ["mental_health", "housing"])

    def test_no_raw_kb_fragment_gate(self):
        import re
        routes = build_national_route_candidates([
            record("E-D001", 'HFU er dokumentert "opptil 20 ar" i fil 25.'),
            record("E-D002", "| Tabellrad | mer tekst |"),
        ])
        self.assertEqual(routes, [])
        for r in routes:
            self.assertIsNone(re.search(r"\d", r["service_type"]))


if __name__ == "__main__":
    unittest.main()
