import json
import unittest
from unittest.mock import patch
from typing import Any

from ..context import make_context
from ..schemas import SchemaError, validate_output
from . import finalize as finalizer


class RejectionTests(unittest.TestCase):
    def context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = make_context({"case_id": "SYNTHETIC", "user_query": "bolig", "profile": {}})
        ctx["safety"].update(priority="NOT_ACUTE", suppressed_routing=False)
        ctx["tracks"] = []
        ctx["epistemic_states"]["per_track"] = {}
        return ctx

    def assert_rejected(self, output):
        self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
        self.assertFalse(output["presented_as_complete"])
        self.assertEqual(output["routes"], [])
        self.assertEqual(output["claims"], [])
        self.assertIn("safety_class", output["safety"])
        self.assertIsNone(output["safety"]["safety_class"])
        self.assertNotIn("REJECTED_RECOMMENDATION_CANARY", json.dumps(output))
        self.assertEqual(output["failures"][0]["stage"], "output_emission")
        validate_output(output)

    def test_consistency_rejection_removes_answer_for_answer_only_consumers(self):
        ctx = self.context()
        ctx["_s7_claims"] = [{"claim_id": "C1", "state": "VERIFIED", "dimension": "knowledge_fact",
                              "value": "required fact", "evidence_ids": [], "provenance_ids": []}]
        with patch.object(finalizer, "render", return_value="REJECTED_RECOMMENDATION_CANARY"):
            output = finalizer.finalize(ctx)
        self.assert_rejected(output)

    def test_renderer_exception_does_not_expose_exception_text(self):
        with patch.object(finalizer, "render", side_effect=ValueError("REJECTED_RECOMMENDATION_CANARY")):
            output = finalizer.finalize(self.context())
        self.assert_rejected(output)

    def test_schema_rejection_does_not_expose_answer_or_schema_value(self):
        with patch.object(finalizer, "render", return_value="REJECTED_RECOMMENDATION_CANARY"), \
                patch.object(finalizer, "validate_output", side_effect=SchemaError("REJECTED_RECOMMENDATION_CANARY")):
            output = finalizer.finalize(self.context())
        self.assert_rejected(output)
