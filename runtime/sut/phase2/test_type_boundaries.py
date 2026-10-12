import copy
import json
import unittest
from unittest.mock import patch

from . import discovery_adapter
from .discovery_adapter import run_discovery_step
from .knowledge import load_knowledge
from .safety import TriageError, load_rules
from .synthetic_fixtures import SyntheticCorpus
from .test_evidence_integrity import discovery_fixture
from .test_semantic_normalization import RULES


class TypeBoundaryTests(unittest.TestCase):
    def test_malformed_profile_is_rejected_before_any_source_read(self) -> None:
        corpus = SyntheticCorpus(self)
        profiles: tuple[object, ...] = ([], {"version": "knowledge-access/v1", "documents": []},
                                       {"version": "knowledge-access/v1", "documents": {1: "CANARY"}})
        for profile in profiles:
            with self.subTest(profile=profile), patch("builtins.open", side_effect=AssertionError("UNAUTHORIZED_READ")):
                docs, failures = load_knowledge(str(corpus.index), str(corpus.root), access_profile=profile)
            self.assertEqual(docs, [])
            self.assertEqual(failures, [{"reason": "ACCESS_PROFILE_REQUIRED"}])

    def test_malformed_metadata_is_rejected_before_document_read(self) -> None:
        corpus = SyntheticCorpus(self)
        base = corpus.add_doc(text="PRIVATE_METADATA_CANARY")
        cases: tuple[tuple[str, object], ...] = (("domains", "housing"), ("domains", [False]),
                                                ("path", ["public.md"]), ("freshness_class", ["CURRENT"]))
        for key, value in cases:
            entry = {**base, key: value}
            profile = copy.deepcopy(corpus.profile)
            profile["documents"]["public"][key] = value
            index = json.dumps({"docs": [entry]}).encode()
            with self.subTest(key=key, value=value), patch(
                    "sut.phase2.knowledge._source_bytes",
                    side_effect=[index, AssertionError("UNAUTHORIZED_DOCUMENT_READ")]):
                docs, failures = load_knowledge(str(corpus.index), str(corpus.root), access_profile=profile)
            self.assertEqual(docs, [])
            self.assertEqual(failures, [{"reason": "SOURCE_NOT_ADMITTED"}])
            self.assertNotIn("PRIVATE_METADATA_CANARY", str(failures))

    def test_malformed_safety_fields_raise_triage_error(self) -> None:
        corpus = SyntheticCorpus(self)
        cases: tuple[tuple[str, object], ...] = (
            ("class_precedence", "ACUTE_SOMATIC_MEDICAL"),
            ("class_signals", {"ACUTE_SOMATIC_MEDICAL": "blor mye"}),
            ("class_collapse", {"ACUTE_SOMATIC_MEDICAL":
                               {"priority": "ACUTE_RISK_NOW", "suppressed_routing": "false"}}),
            ("negation_guard", {"negation_patterns": [False]}))
        for key, value in cases:
            _ = corpus.rules.write_text(json.dumps({**RULES, key: value}), encoding="utf-8")
            with self.subTest(key=key), self.assertRaises(TriageError):
                _ = load_rules(str(corpus.rules))

    def test_malformed_replay_payload_returns_redacted_incomplete_result(self) -> None:
        base: dict[str, object] = {**discovery_fixture(), "execution_status": "COMPLETE", "errors": []}
        cases: tuple[tuple[str, object], ...] = (
            ("services", [{"name": ["PRIVATE_REPLAY_CANARY"]}]),
            ("services", [{**discovery_fixture()["services"][0], "age_bounds": {"min": True}}]),
            ("evidence", ["PRIVATE_REPLAY_CANARY"]),
            ("errors", [{"error": ["PRIVATE_REPLAY_CANARY"]}]))
        for key, value in cases:
            with self.subTest(key=key), patch.object(discovery_adapter, "run_discovery", return_value={**base, key: value}), \
                    patch.object(discovery_adapter, "_protocol", return_value={}), \
                    patch.object(discovery_adapter, "_fixtures", return_value={}):
                try:
                    result = run_discovery_step({"domain": "mental_health", "needs_local_discovery": True},
                                                {"municipality": "Synthetic"}, age=19)
                except (ValueError, KeyError, TypeError) as exc:
                    self.fail("Malformed replay escaped the fail-closed boundary: " + type(exc).__name__)
                self.assertEqual(result["state"], "DISCOVERY_INCOMPLETE")
                self.assertEqual(result["services"], [])
                self.assertEqual(result["evidence"], [])
                self.assertNotIn("PRIVATE_REPLAY_CANARY", json.dumps(result))

    def test_valid_nullable_replay_fields_keep_verified_route_evidence(self) -> None:
        step = discovery_fixture()
        step["services"][0]["age_bounds"] = {"min": 18, "max": None}
        step["services"][0]["verified_date"] = None
        raw: dict[str, object] = {**step, "execution_status": "COMPLETE", "errors": []}
        with patch.object(discovery_adapter, "run_discovery", return_value=raw), \
                patch.object(discovery_adapter, "_protocol", return_value={}), \
                patch.object(discovery_adapter, "_fixtures", return_value={}):
            result = run_discovery_step({"domain": "mental_health", "needs_local_discovery": True},
                                        {"municipality": "Synthetic"}, age=19)
        self.assertEqual(result["state"], "COMPLETED")
        self.assertEqual(result["services"][0].get("age_bounds"), {"min": 18, "max": None})
        self.assertIsNone(result["services"][0].get("verified_date"))
        self.assertEqual(result["services"][0]["self_referral"], True)
        self.assertEqual(result["evidence"], discovery_fixture()["evidence"])
