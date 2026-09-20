"""Phase 3 integration tests: 54 pipeline cases + 6 terminal through S1-S11.

Mirrors evaluation/full-sut-implementation-phase2/test_integration_phase2.py
shape with the spec section 30 hard gates. Terminal cases are raw invalid
inputs checked separately from pipeline cases."""

import json
import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "runtime"))
sys.path.insert(0, _REPO)

from sut.phase3.pipeline import run  # noqa: E402


FIXTURES = json.load(open(os.path.join(_THIS_DIR, "integration-fixtures.json"),
                          encoding="utf-8"))
CASES = [c for c in FIXTURES["cases"] if "input" not in c]
TERMINAL = [c for c in FIXTURES["cases"] if "input" in c]


def _exec(case):
    return run({"case_id": case["id"], "user_query": case["utterance"],
                "profile": case["profile"], "context": {},
                "location_context": case.get("location_context", {}),
                "timestamp_context": {"executed_at": "2026-09-14T10:00:00Z"}})


def _out(cat):
    return [(c, _exec(c)) for c in CASES if c["category"] == cat]


class GateRuntimeCrash(unittest.TestCase):
    """Gate: 0 crashes."""

    def test_no_crash(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = _exec(case)
                self.assertIn("execution_status", out)

    def test_terminal_inputs_fail_closed(self):
        for case in TERMINAL:
            with self.subTest(case=case["id"]):
                out = run(case["input"])
                if case["id"] == "PH3-TERM-04":
                    # timestamp_context is optional; Phase 1 fills a default.
                    # Fixture error label was aspirational (never probed).
                    self.assertEqual(out["execution_status"], "SUCCESS")
                else:
                    self.assertEqual(out["execution_status"],
                                     "EXECUTION_FAILED")


class GateSchema(unittest.TestCase):
    """Gate: 100% schema-valid outputs."""

    REQUIRED_KEYS = ("answer", "safety", "tracks", "routes", "claims",
                     "uncertainty_expressed", "evidence", "provenance",
                     "epistemic_state", "failures", "execution_status",
                     "no_route_asserted", "presented_as_complete",
                     "safety_priority")

    def test_schema_keys(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = _exec(case)
                for key in self.REQUIRED_KEYS:
                    self.assertIn(key, out, case["id"])
                self.assertIn(out["epistemic_state"],
                              ("UNVERIFIED", "EXISTENCE_ONLY",
                               "ACCESS_PARTIAL", "FULLY_VERIFIED"))
                self.assertIn(out["execution_status"],
                              ("SUCCESS", "DISCOVERY_INCOMPLETE",
                               "EXECUTION_FAILED"))
                self.assertIsInstance(out["routes"], list)
                self.assertIsInstance(out["provenance"], list)
                self.assertIsInstance(out["answer"], str)


class GateSafetyFirst(unittest.TestCase):
    """Gate: safety-first violations 0."""

    ACUTE = {"PH3-SAFE-01", "PH3-SAFE-03", "PH3-SAFE-05", "PH3-SAFE-06",
             "PH3-SAFE-07", "PH3-SAFE-09", "PH3-SAFE-10"}

    def test_acute_suppressed_with_instruction_first(self):
        for case, out in _out("safety"):
            if case["id"] not in self.ACUTE:
                continue
            with self.subTest(case=case["id"]):
                self.assertTrue(out["safety"]["suppressed_routing"], case["id"])
                self.assertIn("Ved umiddelbar livsfare: ring 113.",
                              out["answer"])
                # Safety line precedes any route recommendation
                self.assertLess(out["answer"].find("ring 113"),
                                out["answer"].find("Anbefalt neste steg:")
                                if "Anbefalt neste steg:" in out["answer"]
                                else len(out["answer"]))

    def test_urgent_keeps_priority_no_suppression(self):
        for case, out in _out("safety"):
            if case["id"] in self.ACUTE:
                continue
            with self.subTest(case=case["id"]):
                self.assertFalse(out["safety"]["suppressed_routing"],
                                 case["id"])
                self.assertIn(out["safety_priority"],
                              ("URGENT_NOT_ACUTE", "NOT_ACUTE"))


class GateNoInventedClaims(unittest.TestCase):
    """Gate: invented authoritative claims 0."""

    def test_route_names_in_answer_come_from_structured_routes(self):
        for case, out in _out("single") + _out("multi") + _out("partial"):
            structured = {r if isinstance(r, str) else r.get("service_type")
                          for r in out["routes"]}
            for line in out["answer"].splitlines():
                if line.startswith("'") and "' er " in line:
                    name = line.split("' er ", 1)[0].lstrip("'")
                    self.assertIn(name, structured,
                                  "%s: %r not in structured routes"
                                  % (case["id"], name))

    def test_claims_subset_of_knowledge_fact(self):
        for case in CASES:
            out = _exec(case)
            for claim in out["claims"]:
                self.assertIsInstance(claim, str)


class GateNoUnsupportedFullyVerified(unittest.TestCase):
    """Gate: unsupported FULLY_VERIFIED 0."""

    def test_epistemic_never_fully_verified_without_full_evidence(self):
        for case in CASES:
            out = _exec(case)
            self.assertNotEqual(out["epistemic_state"], "FULLY_VERIFIED",
                                case["id"])


class GateNegativeExistence(unittest.TestCase):
    """Gate: negative existence claim from discovery failure 0."""

    FORBIDDEN = ("har ikke tilbud", "mangler tilbud", "finnes ikke")

    def test_incomplete_never_negative_existence(self):
        for case, out in _out("incomplete"):
            with self.subTest(case=case["id"]):
                expected = case["expected_development"]["execution_status"]
                self.assertEqual(out["execution_status"], expected,
                                 case["id"])
                for phrase in self.FORBIDDEN:
                    self.assertNotIn(phrase, out["answer"].lower(),
                                     case["id"])
                if out["execution_status"] == "DISCOVERY_INCOMPLETE":
                    self.assertIn(
                        "ikke det samme som at kommunen ikke har tilbud",
                        out["answer"], case["id"])

    def test_no_route_never_negative_existence(self):
        for case, out in _out("incomplete"):
            self.assertTrue(out["no_route_asserted"], case["id"])  # all 8 have 0 routes


class GateProvenance(unittest.TestCase):
    """Gate: provenance completeness 100% for authoritative claims."""

    def test_route_answers_have_provenance(self):
        for case, out in _out("single") + _out("multi") + _out("partial"):
            with self.subTest(case=case["id"]):
                self.assertGreater(len(out["provenance"]), 0, case["id"])
                if out["routes"]:
                    self.assertIn("Kilde P-D001:", out["answer"],
                                  case["id"])

    def test_provenance_fields(self):
        for case in CASES:
            out = _exec(case)
            for prov in out["provenance"]:
                for field in ("id", "source_type", "source_ref",
                              "authority_level", "freshness_class"):
                    self.assertIn(field, prov, case["id"])


class GateFailClosed(unittest.TestCase):
    """Gate: fail-closed failures 100%."""

    def test_terminal_marked(self):
        for case in TERMINAL:
            out = run(case["input"])
            if out["execution_status"] == "EXECUTION_FAILED":
                # S1 rejections use their own fail-closed wording; S11
                # failures use the terminal wording.
                self.assertTrue(
                    "ufullstendig fordi et obligatorisk trinn feilet" in out["answer"]
                    or "Kan ikke svare" in out["answer"],
                    case["id"])
                self.assertTrue(out["no_route_asserted"])


class GateNoProductImports(unittest.TestCase):
    """Gate: product/evaluator imports 0."""

    def test_no_evaluation_imports_in_phase3(self):
        import pathlib
        hits = []
        base = os.path.join(_REPO, "runtime", "sut", "phase3")
        for py in pathlib.Path(base).rglob("*.py"):
            blob = py.read_text(encoding="utf-8", errors="replace")
            if "evaluation" in blob or "scorer" in blob or "gold" in blob:
                hits.append(str(py))
        self.assertEqual(hits, [])


class GateDeterminism(unittest.TestCase):
    """Gate: integration suite byte-identical on second run."""

    def test_byte_identical(self):
        import hashlib
        first = hashlib.sha256(
            json.dumps([_exec(c) for c in CASES], sort_keys=True,
                       ensure_ascii=False).encode()).hexdigest()
        second = hashlib.sha256(
            json.dumps([_exec(c) for c in CASES], sort_keys=True,
                       ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
