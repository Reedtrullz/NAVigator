"""RC-01 input-boundary normalization tests (generic mechanisms only).

Covers supported legacy caller shapes (unknown age, household children,
nested context alias), normalization determinism/idempotency, and
fail-closed rejection of malformed input. No corpus strings or case IDs.
"""

import json
import unittest

from sut.context import make_context, normalize_input
from sut.schemas import SchemaError, validate_input, validate_output


BASE = {"case_id": "NRM-1", "user_query": "Hvor kan vi fa hjelp?"}


def with_profile(profile):
    doc = dict(BASE)
    doc["profile"] = profile
    return doc


class TestNormalizeInput(unittest.TestCase):
    def test_null_age_dropped(self):
        n = normalize_input(with_profile({"age": None, "role": "parent"}))
        self.assertNotIn("age", n["profile"])
        self.assertEqual(n["profile"]["role"], "parent")
        validate_input(n)

    def test_household_children_boolean_normalized(self):
        n = normalize_input(with_profile({"household_children": True}))
        self.assertEqual(n["profile"]["household_children"], 1)
        validate_input(n)
        n = normalize_input(with_profile({"household_children": False}))
        self.assertEqual(n["profile"]["household_children"], 0)
        validate_input(n)

    def test_household_children_int_kept(self):
        n = normalize_input(with_profile({"household_children": 3}))
        self.assertEqual(n["profile"]["household_children"], 3)
        validate_input(n)

    def test_nested_context_moved_and_top_level_wins(self):
        doc = with_profile({"context": {"a": 1, "b": 1}})
        doc["context"] = {"b": 2}
        n = normalize_input(doc)
        self.assertNotIn("context", n["profile"])
        self.assertEqual(n["context"], {"a": 1, "b": 2})
        validate_input(n)

    def test_nested_context_created_when_top_level_absent(self):
        n = normalize_input(with_profile({"context": {"k": "v"}}))
        self.assertEqual(n["context"], {"k": "v"})
        validate_input(n)

    def test_normalization_deterministic(self):
        doc = with_profile({"age": None, "household_children": True,
                            "context": {"k": "v"}})
        self.assertEqual(
            json.dumps(normalize_input(doc), sort_keys=True),
            json.dumps(normalize_input(doc), sort_keys=True))

    def test_normalization_idempotent(self):
        doc = with_profile({"age": None, "household_children": True,
                            "context": {"k": "v"}})
        once = normalize_input(doc)
        self.assertEqual(
            json.dumps(once, sort_keys=True),
            json.dumps(normalize_input(once), sort_keys=True))

    def test_malformed_household_children_fails_closed(self):
        n = normalize_input(with_profile({"household_children": "many"}))
        with self.assertRaises(SchemaError):
            validate_input(n)

    def test_scalar_profile_context_wrapped(self):
        n = normalize_input(with_profile({"context": "situasjon"}))
        self.assertNotIn("context", n["profile"])
        self.assertEqual(n["context"], {"situational_context": "situasjon"})
        validate_input(n)
        again = normalize_input(n)
        self.assertEqual(
            json.dumps(again, sort_keys=True),
            json.dumps(n, sort_keys=True))

    def test_scalar_profile_context_top_level_wins(self):
        doc = with_profile({"context": "situasjon"})
        doc["context"] = {"situational_context": "overordnet"}
        n = normalize_input(doc)
        self.assertEqual(n["context"], {"situational_context": "overordnet"})
        validate_input(n)

    def test_unsupported_context_shapes_fail_closed(self):
        n = normalize_input(with_profile({"context": ["x"]}))
        with self.assertRaises(SchemaError):
            validate_input(n)
        doc = with_profile({"context": "situasjon"})
        doc["context"] = "ikke objekt"
        n = normalize_input(doc)
        with self.assertRaises(SchemaError):
            validate_input(n)

    def test_age_out_of_range_still_rejected(self):
        n = normalize_input(with_profile({"age": 150}))
        with self.assertRaises(SchemaError):
            validate_input(n)

    def test_unknown_profile_key_still_rejected(self):
        n = normalize_input(with_profile({"forbidden_key": 1}))
        with self.assertRaises(SchemaError):
            validate_input(n)


class TestLegacyShapesEndToEnd(unittest.TestCase):
    def test_phase1_run_accepts_supported_legacy_shapes(self):
        from sut.pipeline import run
        doc = with_profile({"age": None, "household_children": True,
                            "context": {"situasjon": "x"}})
        out = run(doc)
        validate_output(out)
        self.assertFalse(
            [f for f in out["failures"] if f["stage"] == "input_normalization"])

    def test_full_sut_accepts_supported_legacy_shapes(self):
        from sut.phase3.pipeline import run_with_trace as run_full
        doc = with_profile({"age": None, "household_children": 2,
                            "context": {"situasjon": "x"}})
        out, trace = run_full(doc)
        stages = {m["stage"]: m["state"] for m in trace}
        self.assertNotEqual(stages.get("input_normalization"), "TERMINAL")
        validate_output(out)

    def test_full_sut_accepts_scalar_profile_context(self):
        from sut.phase3.pipeline import run_with_trace as run_full
        doc = with_profile({"age": 9, "role": "third_party",
                            "context": "annen voksen til stede"})
        out, trace = run_full(doc)
        stages = {m["stage"]: m["state"] for m in trace}
        self.assertNotEqual(stages.get("input_normalization"), "TERMINAL")
        self.assertEqual(out["execution_status"], "SUCCESS")
        validate_output(out)

    def test_make_context_carries_normalized_input(self):
        ctx = make_context(with_profile({"age": None,
                                         "household_children": True,
                                         "context": {"k": "v"}}))
        self.assertNotIn("age", ctx["input"]["profile"])
        self.assertEqual(ctx["input"]["profile"]["household_children"], 1)
        self.assertEqual(ctx["input"]["context"], {"k": "v"})


if __name__ == "__main__":
    unittest.main()
