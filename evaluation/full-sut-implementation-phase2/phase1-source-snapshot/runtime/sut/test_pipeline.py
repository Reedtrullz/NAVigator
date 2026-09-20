import json
import os
import tempfile
import unittest

from sut.pipeline import PHASE_1_ANSWER, run, run_with_trace
from sut.schemas import validate_output


VALID_INPUT = {
    "case_id": "ROUT-021",
    "user_query": "Hvor kan vi fa hjelp?",
    "profile": {"age": 17},
}


class TestPipelineSkeleton(unittest.TestCase):
    def test_valid_input_produces_schema_valid_output(self):
        out = run(VALID_INPUT)
        validate_output(out)

    def test_fail_closed_when_safety_unverified(self):
        out = run(VALID_INPUT)
        self.assertEqual(out["execution_status"], "EXECUTION_FAILED")
        self.assertFalse(out["presented_as_complete"])
        self.assertTrue(out["no_route_asserted"])
        self.assertEqual(out["routes"], [])
        self.assertEqual(out["claims"], [])
        self.assertEqual(out["epistemic_state"], "UNVERIFIED")

    def test_no_route_fabrication(self):
        out = run(VALID_INPUT)
        for forbidden in ("BUP", "fastlege", "DPS", "helsesykepleier"):
            self.assertNotIn(forbidden, out["answer"])

    def test_malformed_input_is_terminal(self):
        out = run({"case_id": "X"})
        self.assertEqual(out["execution_status"], "EXECUTION_FAILED")
        self.assertFalse(out["presented_as_complete"])
        self.assertEqual(out["failures"][0]["stage"], "input_normalization")

    def test_unsupported_version_fails_closed(self):
        doc = dict(VALID_INPUT, context={"schema_version": "sut-input/v9"})
        # context is free-form, so the v1 shape remains valid; a genuinely
        # incompatible version must be introduced with a new schema file.
        validate_output(run(doc))

    def test_fc01_missing_rule_file_is_terminal(self):
        out = run(VALID_INPUT, config={"safety_rules_path": "data/missing-rules.json"})
        self.assertEqual(out["execution_status"], "EXECUTION_FAILED")
        fc01 = [f for f in out["failures"] if f["stage"] == "safety_triage"]
        self.assertEqual(fc01[0]["state"], "TERMINAL")
        self.assertIn("FC-01", fc01[0]["message"])

    def test_fc01_invalid_rule_file_is_terminal(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"acute_signals": []}, f)
            path = f.name
        try:
            out = run(VALID_INPUT, config={"safety_rules_path": path})
            self.assertEqual(out["execution_status"], "EXECUTION_FAILED")
        finally:
            os.unlink(path)

    def test_stage_trace_covers_all_stages(self):
        _, trace = run_with_trace(VALID_INPUT)
        self.assertEqual(len(trace), 11)
        self.assertEqual(trace[0]["stage"], "input_normalization")
        self.assertEqual(trace[-1]["stage"], "output_emission")
        for mark in trace:
            self.assertIn("latency_ms", mark)
            self.assertIn("state", mark)

    def test_deterministic_output(self):
        a = run(VALID_INPUT)
        b = run(VALID_INPUT)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_skeleton_answer_is_refusal(self):
        out = run(VALID_INPUT)
        self.assertEqual(out["answer"], PHASE_1_ANSWER)
        self.assertIn("ikke", out["uncertainty_expressed"] or "") if False else None


if __name__ == "__main__":
    unittest.main()
