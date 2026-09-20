import unittest

from sut.context import STAGE_NAMES, StageState, make_context, mark_stage
from sut.schemas import SchemaError, validate_context


VALID_INPUT = {
    "case_id": "ROUT-021",
    "user_query": "Hvor kan vi fa hjelp?",
    "profile": {"age": 17, "role": "parent"},
}


class TestMakeContext(unittest.TestCase):
    def test_minimal_context_valid(self):
        ctx = make_context(VALID_INPUT)
        validate_context(ctx)

    def test_invalid_input_rejected(self):
        with self.assertRaises(SchemaError):
            make_context({"case_id": "X"})

    def test_pre_triage_default_is_fail_closed(self):
        ctx = make_context(VALID_INPUT)
        self.assertEqual(ctx["safety"]["priority"], "TRIAGE_FAILED")
        self.assertTrue(ctx["safety"]["suppressed_routing"])

    def test_conservative_single_track(self):
        ctx = make_context(VALID_INPUT)
        self.assertEqual(len(ctx["tracks"]), 1)
        track = ctx["tracks"][0]
        self.assertEqual(track["track_id"], "T1")
        self.assertEqual(track["domain"], "general")
        self.assertEqual(track["status"], "PENDING")
        self.assertEqual(track["sub_utterance"], VALID_INPUT["user_query"])

    def test_closed_defaults(self):
        ctx = make_context(VALID_INPUT)
        self.assertEqual(ctx["candidate_routes"], [])
        self.assertEqual(ctx["claim_states"], [])
        self.assertEqual(ctx["epistemic_states"]["top_level"], "UNVERIFIED")
        self.assertEqual(ctx["failures"], [])
        self.assertTrue(ctx["answer_plan"]["no_route_asserted"])
        self.assertFalse(ctx["answer_plan"]["presented_as_complete"])


class TestMarkStage(unittest.TestCase):
    def test_success_not_recorded_as_failure(self):
        ctx = make_context(VALID_INPUT)
        mark_stage(ctx, "input_normalization", StageState.SUCCESS)
        self.assertEqual(ctx["failures"], [])

    def test_recoverable_recorded(self):
        ctx = make_context(VALID_INPUT)
        mark_stage(ctx, "local_discovery", StageState.RECOVERABLE, "provider failed")
        self.assertEqual(len(ctx["failures"]), 1)
        rec = ctx["failures"][0]
        self.assertEqual(rec["stage"], "local_discovery")
        self.assertEqual(rec["state"], "RECOVERABLE")
        self.assertEqual(rec["message"], "provider failed")

    def test_unknown_stage_rejected(self):
        ctx = make_context(VALID_INPUT)
        with self.assertRaises(ValueError):
            mark_stage(ctx, "stage_x", StageState.SUCCESS)

    def test_unknown_state_rejected(self):
        ctx = make_context(VALID_INPUT)
        with self.assertRaises(ValueError):
            mark_stage(ctx, "decomposition", "MAGIC")

    def test_eight_stages_in_order(self):
        self.assertEqual(
            STAGE_NAMES,
            (
                "input_normalization",
                "safety_triage",
                "decomposition",
                "knowledge_retrieval",
                "local_discovery",
                "route_reasoning",
                "evidence_aggregation",
                "epistemic_assignment",
                "answer_planning",
                "answer_rendering",
                "output_emission",
            ),
        )

    def test_stage_state_members(self):
        self.assertEqual(
            {s.value for s in StageState},
            {"SUCCESS", "PARTIAL", "RECOVERABLE", "TERMINAL"},
        )


if __name__ == "__main__":
    unittest.main()
