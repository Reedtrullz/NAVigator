"""Phase 2 S3 track decomposition tests (TDD RED first)."""

import unittest

from sut.phase2.decompose import decompose


class DecomposeTests(unittest.TestCase):
    def test_single_mental_health_track(self):
        tracks = decompose("Jeg har hatt angst i flere maneder og trenger hjelp.")
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["domain"], "mental_health")
        self.assertEqual(tracks[0]["track_id"], "T1")

    def test_multi_track_housing_and_financial(self):
        tracks = decompose(
            "Jeg har mistet boligen min og har ikke okonomi til mat."
        )
        domains = [t["domain"] for t in tracks]
        self.assertIn("housing", domains)
        self.assertIn("financial_support", domains)
        self.assertEqual(len(tracks), 2)

    def test_multi_track_mental_health_and_housing(self):
        tracks = decompose(
            "Jeg sliter psykisk og har faatt varsel om utkastelse fra leiligheten."
        )
        domains = [t["domain"] for t in tracks]
        self.assertIn("mental_health", domains)
        self.assertIn("housing", domains)

    def test_conjunction_without_distinct_domains_stays_single(self):
        tracks = decompose("Jeg er sliten og trot og orker ikke mye for tiden.")
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["domain"], "general")

    def test_same_domain_twice_not_duplicated(self):
        tracks = decompose("Jeg trenger bostotte og boligjobb for min bolig.")
        housing = [t for t in tracks if t["domain"] == "housing"]
        self.assertEqual(len(housing), 1)

    def test_no_match_defaults_general(self):
        tracks = decompose("Hva er klokka?")
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["domain"], "general")

    def test_track_shape(self):
        tracks = decompose("Datteren har alvorlig skolevegring.")
        t = tracks[0]
        self.assertEqual(t["track_id"], "T1")
        self.assertEqual(t["domain"], "education")
        self.assertEqual(t["status"], "PENDING")
        self.assertIsInstance(t["sub_utterance"], str)
        self.assertTrue(t["sub_utterance"])
        self.assertIn("needs_local_discovery", t)

    def test_child_safety_domain(self):
        tracks = decompose("Jeg er bekymret for at barnet blir utsatt for vold, barnevern? ")
        domains = [t["domain"] for t in tracks]
        self.assertIn("child_safety", domains)

    def test_education_domain(self):
        tracks = decompose("Hvem kan hjelpe med PPT vurdering for skolen min?")
        domains = [t["domain"] for t in tracks]
        self.assertIn("education", domains)

    def test_employment_domain(self):
        tracks = decompose("Jeg mistet jobben og trenger hjelp med arbeid og soknad.")
        domains = [t["domain"] for t in tracks]
        self.assertIn("employment", domains)

    def test_legal_rights_domain(self):
        tracks = decompose("Hvilke rettigheter har jeg til samvar med barnet etter samlivsbrudd?")
        domains = [t["domain"] for t in tracks]
        self.assertIn("legal_rights", domains)

    def test_three_track_compound(self):
        tracks = decompose(
            "Jeg har psykiske vansker, truer med utkastelse, og har gjeld."
        )
        domains = [t["domain"] for t in tracks]
        self.assertIn("mental_health", domains)
        self.assertIn("housing", domains)
        self.assertIn("financial_support", domains)

    def test_deterministic_track_order(self):
        a = decompose("Jeg har gjeld og psykiske vansker og boligproblem.")
        b = decompose("Jeg har gjeld og psykiske vansker og boligproblem.")
        self.assertEqual([t["domain"] for t in a], [t["domain"] for t in b])
        self.assertEqual([t["track_id"] for t in a], [t["track_id"] for t in b])

    def test_mental_health_track_needs_local_discovery(self):
        tracks = decompose("Jeg trenger psykisk helsehjelp.")
        self.assertTrue(tracks[0]["needs_local_discovery"])

    def test_general_track_no_local_discovery(self):
        tracks = decompose("Hvordan sender jeg inn skattemelding?")
        self.assertFalse(tracks[0]["needs_local_discovery"])


if __name__ == "__main__":
    unittest.main()
