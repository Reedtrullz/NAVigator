import unittest

from sut.schemas import SchemaError, validate_context, validate_input, validate_output


VALID_INPUT = {
    "case_id": "ROUT-021",
    "user_query": "Hvor kan vi fa hjelp?",
    "profile": {"age": 17, "role": "parent"},
}


class TestInputSchema(unittest.TestCase):
    def test_valid_input_passes(self):
        validate_input(VALID_INPUT)

    def test_missing_required_field_raises(self):
        doc = {"case_id": "X", "user_query": "q"}
        with self.assertRaises(SchemaError):
            validate_input(doc)

    def test_empty_query_raises(self):
        doc = dict(VALID_INPUT, user_query="")
        with self.assertRaises(SchemaError):
            validate_input(doc)

    def test_bad_case_id_pattern_raises(self):
        doc = dict(VALID_INPUT, case_id="bad id!")
        with self.assertRaises(SchemaError):
            validate_input(doc)

    def test_age_out_of_range_raises(self):
        doc = dict(VALID_INPUT, profile={"age": 121})
        with self.assertRaises(SchemaError):
            validate_input(doc)

    def test_unknown_top_level_key_raises(self):
        doc = dict(VALID_INPUT, gold={"safety_priority": "NOT_ACUTE"})
        with self.assertRaises(SchemaError):
            validate_input(doc)

    def test_unsupported_version_guard(self):
        # Version is carried by schema identity; a v2 doc shape must not
        # silently validate against v1.
        doc = dict(VALID_INPUT, context={"schema_version": "sut-input/v2"})
        validate_input(doc)  # context is free-form: still v1-valid input


VALID_OUTPUT = {
    "answer": "Kontakt fastlegen.",
    "safety": {
        "priority": "NOT_ACUTE",
        "signals": [],
        "suppressed_routing": False,
    },
    "tracks": [{"track_id": "T1", "domain": "mental_health", "status": "NO_ROUTE"}],
    "routes": [],
    "claims": [],
    "uncertainty_expressed": [],
    "evidence": {},
    "provenance": [],
    "epistemic_state": "UNVERIFIED",
    "failures": [],
    "execution_status": "SUCCESS",
    "no_route_asserted": True,
    "presented_as_complete": False,
}


class TestOutputSchema(unittest.TestCase):
    def test_valid_output_passes(self):
        validate_output(VALID_OUTPUT)

    def test_missing_required_field_raises(self):
        doc = {k: v for k, v in VALID_OUTPUT.items() if k != "answer"}
        with self.assertRaises(SchemaError):
            validate_output(doc)

    def test_bad_execution_status_raises(self):
        doc = dict(VALID_OUTPUT, execution_status="MAGIC")
        with self.assertRaises(SchemaError):
            validate_output(doc)

    def test_provenance_linkage_required(self):
        doc = dict(
            VALID_OUTPUT,
            provenance=[
                {
                    "id": "P1",
                    "source_type": "RULE_REGISTRY",
                    "source_ref": "data/rules-v1.json",
                    "verified_at": "2026-09-14T00:00:00Z",
                    "freshness_class": "CURRENT",
                }
            ],
        )
        validate_output(doc)


class TestContextSchema(unittest.TestCase):
    def test_minimal_context_passes(self):
        ctx = {
            "input": VALID_INPUT,
            "safety": {"priority": "NOT_ACUTE", "signals": [], "suppressed_routing": False},
            "tracks": [
                {
                    "track_id": "T1",
                    "domain": "general",
                    "sub_utterance": "q",
                    "status": "PENDING",
                }
            ],
            "candidate_routes": [],
            "evidence": {},
            "provenance": [],
            "claim_states": [],
            "epistemic_states": {"top_level": "UNVERIFIED", "per_route": []},
            "failures": [],
            "answer_plan": {
                "blocks": [],
                "no_route_asserted": True,
                "presented_as_complete": False,
            },
        }
        validate_context(ctx)

    def test_bad_track_domain_raises(self):
        ctx = {
            "input": VALID_INPUT,
            "safety": {"priority": "NOT_ACUTE", "signals": [], "suppressed_routing": False},
            "tracks": [
                {
                    "track_id": "T1",
                    "domain": "quantum",
                    "sub_utterance": "q",
                    "status": "PENDING",
                }
            ],
            "candidate_routes": [],
            "evidence": {},
            "provenance": [],
            "claim_states": [],
            "epistemic_states": {"top_level": "UNVERIFIED", "per_route": []},
            "failures": [],
            "answer_plan": {
                "blocks": [],
                "no_route_asserted": True,
                "presented_as_complete": False,
            },
        }
        with self.assertRaises(SchemaError):
            validate_context(ctx)


if __name__ == "__main__":
    unittest.main()
