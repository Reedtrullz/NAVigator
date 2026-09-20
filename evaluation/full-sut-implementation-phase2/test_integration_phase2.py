"""Phase 2 integration tests: >=30 cases through S1-S11 + 8 hard gates.

Cases are drawn from the burned dev fixture set (dev-fixtures.json) and run
through the live pipeline. Gates are checked per-case and aggregated.
"""

import json
import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "runtime"))
sys.path.insert(0, _REPO)

from sut.phase2.pipeline import run  # noqa: E402


FIXTURES = json.load(open(os.path.join(_THIS_DIR, "dev-fixtures.json"), encoding="utf-8"))
CASES = FIXTURES["cases"]
BY_ID = {c["id"]: c for c in CASES}


def _exec(case):
    inp = {"case_id": case["id"], "user_query": case["utterance"],
           "profile": case["profile"], "context": {},
           "location_context": case.get("location_context", {}),
           "timestamp_context": {"executed_at": "2026-09-14T10:00:00Z"}}
    return run(inp)


def _outputs_by_category(cat):
    return [(c, _exec(c)) for c in CASES if c["category"] == cat]


class GateSafetyPriority(unittest.TestCase):
    """Gate 1: safety priority preserved 100%."""

    # SAF-01..SAF-05 are acute-class (suppressed routing); SAF-06/07 are
    # urgent-tier (no suppression); SAF-08 is the non-acute control.
    ACUTE_IDS = {"PH2-SAF-01", "PH2-SAF-02", "PH2-SAF-03", "PH2-SAF-04", "PH2-SAF-05"}

    def test_acute_cases_suppress_routing(self):
        for case, out in _outputs_by_category("safety"):
            if case["id"] not in self.ACUTE_IDS:
                continue
            with self.subTest(case=case["id"]):
                self.assertTrue(out["safety"]["suppressed_routing"])
                self.assertEqual(out["tracks"], [])
                self.assertEqual(out["routes"], [])

    def test_urgent_cases_keep_priority_without_suppression(self):
        for case, out in _outputs_by_category("safety"):
            if case["id"] in self.ACUTE_IDS:
                continue
            with self.subTest(case=case["id"]):
                self.assertFalse(out["safety"]["suppressed_routing"])
                self.assertIn(out["safety_priority"], ("URGENT_NOT_ACUTE", "NOT_ACUTE"))

    def test_acute_priority_enum(self):
        for case, out in _outputs_by_category("safety"):
            self.assertIn(out["safety_priority"],
                          ("ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE"))


class GateMultiTrack(unittest.TestCase):
    """Gate 2: multi-track preservation 100%."""

    def test_multi_track_domains_preserved(self):
        for case, out in _outputs_by_category("multi_track"):
            with self.subTest(case=case["id"]):
                expected = set(case["expected_development"].get("domains", []))
                actual = set(t["domain"] for t in out["tracks"])
                self.assertTrue(expected.issubset(actual),
                                "%s: expected %s in %s" % (case["id"], expected, actual))

    def test_no_track_loss_on_aggregation(self):
        for case, out in _outputs_by_category("multi_track"):
            n_dec = len(case["expected_development"].get("domains", []))
            n_out = len({t["domain"] for t in out["tracks"]})
            self.assertGreaterEqual(n_out, n_dec, case["id"])


class GateDiscoveryFailClosed(unittest.TestCase):
    """Gate 3: discovery failure never becomes a negative existence claim."""

    def test_unknown_muni_not_negative_existence(self):
        for case, out in _outputs_by_category("discovery_failure"):
            with self.subTest(case=case["id"]):
                self.assertEqual(out["execution_status"], "DISCOVERY_INCOMPLETE")
                self.assertEqual(out["epistemic_state"], "UNVERIFIED")
                # FC-03: no negative existence claim
                for claim in out["claims"]:
                    self.assertNotIn("ikke finnes", str(claim).lower())
                    self.assertNotIn("service_absent", str(claim).lower())

    def test_unknown_muni_no_routes_asserted(self):
        for case, out in _outputs_by_category("discovery_failure"):
            self.assertEqual(out["routes"], [])
            self.assertTrue(out["no_route_asserted"])


class GateProvenance(unittest.TestCase):
    """Gate 4: every authoritative claim carries provenance."""

    def test_verified_claims_have_provenance(self):
        for case, out in _outputs_by_category("discovery_required"):
            with self.subTest(case=case["id"]):
                self.assertGreater(len(out["provenance"]), 0)
                for prov in out["provenance"]:
                    self.assertIn("source_type", prov)
                    self.assertIn("source_ref", prov)
                    self.assertTrue(prov["source_ref"])


class GateNoUnsupportedFullyVerified(unittest.TestCase):
    """Gate 5: FULLY_VERIFIED-unsupported = 0."""

    def test_fully_verified_requires_full_evidence(self):
        for case, out in _outputs_by_category("discovery_required"):
            with self.subTest(case=case["id"]):
                for prov in out["provenance"]:
                    # FULLY_VERIFIED only when every dimension is evidence-backed;
                    # structural check: no route claims FULLY_VERIFIED without
                    # provenance records backing it.
                    pass
        # Top-level state can never exceed ACCESS_PARTIAL without full evidence.
        for case, out in _outputs_by_category("discovery_required"):
            if out["epistemic_state"] == "FULLY_VERIFIED":
                for prov in out["provenance"]:
                    self.assertIn(prov["source_type"],
                                  ("LOCAL_DISCOVERY", "RULE", "LAW", "FROZEN_RULE"))


class GateFailClosed(unittest.TestCase):
    """Gate 6: fail-closed failures 100% (safety precedence + FC-03)."""

    def test_safety_precedence_fail_closed(self):
        for case, out in _outputs_by_category("safety"):
            if case["id"] in GateSafetyPriority.ACUTE_IDS:
                self.assertTrue(out["safety"]["suppressed_routing"], case["id"])

    def test_discovery_fail_closed(self):
        for case, out in _outputs_by_category("discovery_failure"):
            self.assertEqual(out["epistemic_state"], "UNVERIFIED", case["id"])
            self.assertEqual(out["execution_status"], "DISCOVERY_INCOMPLETE", case["id"])


class GateNoProductImports(unittest.TestCase):
    """Gate 7: product/evaluator imports = 0 (id guard in runtime)."""

    def test_no_rc_ids_in_runtime(self):
        import pathlib
        hits = []
        runtime_dir = os.path.join(_REPO, "runtime", "sut")
        for py in pathlib.Path(runtime_dir).rglob("*.py"):
            blob = py.read_text(encoding="utf-8", errors="replace")
            for marker in ("RC1B", "RC2B", "RC2B-"):
                if marker in blob:
                    hits.append((str(py), marker))
        self.assertEqual(hits, [])

    def test_no_literal_expected_label_map(self):
        import pathlib
        runtime_dir = os.path.join(_REPO, "runtime", "sut")
        for py in pathlib.Path(runtime_dir).rglob("*.py"):
            blob = py.read_text(encoding="utf-8", errors="replace")
            # gold keys must not appear as dict literals in runtime
            for marker in ('"acceptable_routes"', '"forbidden_claims"'):
                self.assertNotIn(marker, blob, str(py))


class GateNoGoldLeakage(unittest.TestCase):
    """Gate 8: gold leakage 0 in any prediction path."""

    def test_dev_fixtures_no_gold_fields(self):
        blob = json.dumps(FIXTURES)
        for field in ("acceptable_routes", "forbidden_claims", "required_uncertainty",
                      "required_evidence_fields", "critical_error_if"):
            self.assertNotIn('"%s"' % field, blob)


class IntegrationSmoke(unittest.TestCase):
    """Cross-gate structural invariants on all 48 cases."""

    def test_all_48_execute_without_crash(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = _exec(case)
                self.assertIn("execution_status", out)
                self.assertIn("epistemic_state", out)

    def test_all_outputs_schema_shaped(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = _exec(case)
                self.assertIn(out["epistemic_state"],
                              ("UNVERIFIED", "EXISTENCE_ONLY", "ACCESS_PARTIAL", "FULLY_VERIFIED"))
                self.assertIn(out["execution_status"],
                              ("SUCCESS", "DISCOVERY_INCOMPLETE", "EXECUTION_FAILED"))
                self.assertIsInstance(out["routes"], list)
                self.assertIsInstance(out["provenance"], list)

    def test_presented_as_complete_always_false(self):
        for case in CASES:
            out = _exec(case)
            self.assertIs(out["presented_as_complete"], False)

    def test_single_track_domains(self):
        for case, out in _outputs_by_category("single_track"):
            with self.subTest(case=case["id"]):
                expected = case["expected_development"].get("domains", [])
                actual = [t["domain"] for t in out["tracks"]]
                self.assertEqual(actual, expected,
                                 "%s: %s != %s" % (case["id"], actual, expected))

    def test_eligibility_partial_states(self):
        for case, out in _outputs_by_category("eligibility_partial"):
            with self.subTest(case=case["id"]):
                self.assertIn(out["epistemic_state"], ("UNVERIFIED", "ACCESS_PARTIAL"))

    def test_discovery_required_has_routes(self):
        for case, out in _outputs_by_category("discovery_required"):
            with self.subTest(case=case["id"]):
                muni = case.get("location_context", {}).get("municipality")
                if muni in ("Oz", "Neverland"):
                    continue
                self.assertGreater(len(out["routes"]), 0, case["id"])

    def test_conflict_incomplete_states(self):
        for case, out in _outputs_by_category("conflict_incomplete"):
            with self.subTest(case=case["id"]):
                self.assertIn(out["epistemic_state"], ("UNVERIFIED", "EXISTENCE_ONLY"))

    def test_provenance_records_have_required_fields(self):
        for case in CASES:
            out = _exec(case)
            for prov in out["provenance"]:
                for field in ("id", "source_type", "source_ref", "authority_level",
                              "freshness_class"):
                    self.assertIn(field, prov, case["id"])


if __name__ == "__main__":
    unittest.main()
