import copy
import json
import unittest
from unittest.mock import patch
from functools import cached_property
from collections.abc import Callable
from pathlib import Path
from typing import cast
from ..phase2.contracts import ConfigOverrides, Context, DiscoveryStep, Input, Output, Trace

from ..phase2 import pipeline as engine
from ..phase2.synthetic_fixtures import SyntheticCorpus
from ..phase2.test_evidence_integrity import discovery_fixture
from ..schemas import validate_output
from . import finalize as finalizer
from .pipeline import run_with_trace, STAGES


class RuntimeSyntheticTests(unittest.TestCase):
    @cached_property
    def corpus(self) -> SyntheticCorpus:
        corpus = SyntheticCorpus(self)
        _ = corpus.add_doc("public", "angst support fact", domain="mental_health", verified_date="2026-10-01")
        return corpus

    @property
    def cfg(self) -> ConfigOverrides:
        return {"knowledge_index_path": str(self.corpus.index), "knowledge_repo_root": str(self.corpus.root),
                    "knowledge_access_profile": self.corpus.profile, "rules_registry_path": str(self.corpus.rules)}

    @property
    def input(self) -> Input:
        return {"case_id": "SYNTHETIC", "user_query": "angst", "profile": {"age": 19},
                      "location_context": {"municipality": "Synthetic"}}

    def execute(self, discovery: DiscoveryStep | None = None,
                input_data: Input | None = None) -> tuple[Output, list[Trace]]:
        step = copy.deepcopy(discovery if discovery is not None else discovery_fixture())
        with patch.object(engine, "run_discovery_step", return_value=step), \
                patch("socket.create_connection", side_effect=AssertionError("NO_NETWORK")), \
                patch("subprocess.run", side_effect=AssertionError("NO_SUBPROCESS")):
            output, trace = run_with_trace(input_data or self.input, self.cfg)
        validate_output(output)
        self.assertEqual(len(trace), 11)
        return output, trace

    def test_happy_path_through_real_s1_to_s11(self) -> None:
        output, trace = self.execute()
        self.assertEqual(output["execution_status"], "SUCCESS")
        self.assertEqual(output["epistemic_state"], "FULLY_VERIFIED")
        self.assertIn("Service A", output["routes"])
        self.assertIn("angst support fact", output["claims"])
        self.assertTrue(all(t.get("state") == "SUCCESS" for t in trace))
        assert "source_admission" in output["evidence"]
        self.assertEqual(output["evidence"]["source_admission"]["source_dates"]["P-K002"], "2026-10-01")

    def test_actual_dimension_evidence_survives_serialization(self) -> None:
        output, _ = self.execute()
        proofs = output["evidence"].get("dimension_sources", {})
        self.assertTrue(proofs)
        assert "claim_evidence" in output["evidence"]
        for claim in output["evidence"]["claim_evidence"].values():
            assert "evidence_ids" in claim
            for eid in claim["evidence_ids"]:
                if eid.startswith("E-DISC-"):
                    self.assertIn(eid, proofs)
                    self.assertTrue(proofs[eid]["supporting_span"])
                    self.assertTrue(proofs[eid]["locator"])
                    content_hash = proofs[eid]["content_hash"]
                    assert isinstance(content_hash, str)
                    self.assertEqual(len(content_hash), 64)

    def test_norwegian_verified_fact_survives_real_rendering(self) -> None:
        fact = "angst: blåbær, støtte og øvelse"
        _ = self.corpus.add_doc("norwegian", fact, domain="mental_health", verified_date="2026-10-01")
        output, _ = self.execute()
        self.assertEqual(output["execution_status"], "SUCCESS")
        self.assertIn(fact, output["claims"])
        self.assertIn("angst: blaabaer, stoette og oevelse", output["answer"])

    def test_gap_information_is_qualified_in_user_answer(self) -> None:
        self.corpus.docs[0]["class"] = "GAP_REGISTRY"
        self.corpus.profile["documents"]["public"]["class"] = "GAP_REGISTRY"
        self.corpus.save_index()
        output, _ = self.execute()
        self.assertNotIn("angst support fact", output["claims"])
        self.assertIn("Registrert kunnskapshull", output["answer"])

    def test_private_marker_never_opened_or_returned_in_final_output(self) -> None:
        _ = self.corpus.add_doc("private", "PRIVATE_CASE_CANARY", doc_class="PRIVATE_CASE", domain="mental_health")
        private = str(self.corpus.root / "private.md")
        opened: list[str] = []
        original = open
        def observe(path: str | Path, mode: str = "r", buffering: int = -1,
                    encoding: str | None = None, errors: str | None = None,
                    newline: str | None = None, closefd: bool = True,
                    opener: Callable[[str, int], int] | None = None) -> object:
            opened.append(str(path))
            return original(path, mode, buffering, encoding, errors, newline, closefd, opener)
        with patch("builtins.open", side_effect=observe):
            output, _ = self.execute()
        self.assertNotIn(private, opened)
        self.assertNotIn("PRIVATE_CASE_CANARY", json.dumps(output))
        self.assertEqual(output["epistemic_state"], "UNVERIFIED")
        self.assertFalse(output["presented_as_complete"])

    def test_sha_and_unavailable_index_survive_to_last_output(self) -> None:
        _ = (self.corpus.root / "public.md").write_text("MODIFIED_SOURCE_CANARY", encoding="utf-8")
        output, _ = self.execute()
        assert "source_admission" in output["evidence"]
        self.assertEqual(output["evidence"]["source_admission"]["per_track"]["T1"]["failures"], [{"reason": "SHA_MISMATCH"}])
        self.assertNotIn("MODIFIED_SOURCE_CANARY", json.dumps(output))
        self.corpus.index.unlink()
        output, _ = self.execute()
        assert "source_admission" in output["evidence"]
        self.assertEqual(output["evidence"]["source_admission"]["per_track"]["T1"]["coverage"]["state"], "INCOMPLETE")
        self.assertFalse(output["presented_as_complete"])

    def test_unknown_age_is_not_a_positive_suitability_claim(self) -> None:
        data = copy.deepcopy(self.input)
        data["profile"] = {}
        output, _ = self.execute(input_data=data)
        self.assertNotEqual(output["epistemic_state"], "FULLY_VERIFIED")
        assert "structured_routes" in output["evidence"]
        route = output["evidence"]["structured_routes"][0]
        self.assertEqual(route["dims"]["age_eligible"], "UNRESOLVED")
        self.assertFalse(output["presented_as_complete"])

    def test_technical_discovery_failure_stays_incomplete(self) -> None:
        output, _ = self.execute({"state": "DISCOVERY_INCOMPLETE", "services": [], "evidence": []})
        self.assertEqual(output["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertEqual(output["epistemic_state"], "UNVERIFIED")
        self.assertIn("discovery_incomplete", output["uncertainty_expressed"])
        self.assertNotIn("no_route_found", output["uncertainty_expressed"])

    def test_discovery_crash_and_render_crash_cannot_look_complete(self) -> None:
        def crash(_ctx: Context) -> None:
            raise RuntimeError("PRIVATE_EXCEPTION_CANARY")
        with patch.dict(STAGES, {"local_discovery": crash}):
            output, _ = self.execute()
        self.assertEqual(output["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertNotIn("PRIVATE_EXCEPTION_CANARY", json.dumps(output))
        with patch.object(finalizer, "render", side_effect=ValueError("REJECTED_RECOMMENDATION_CANARY")):
            output, _ = self.execute()
        self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
        self.assertEqual(output["routes"], [])
        self.assertNotIn("REJECTED_RECOMMENDATION_CANARY", json.dumps(output))

    def test_rejection_is_terminal_in_stage_trace_as_well_as_output(self) -> None:
        with patch.object(finalizer, "render", return_value="REJECTED_RECOMMENDATION_CANARY"):
            output, trace = self.execute()
        self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
        self.assertEqual(trace[-1]["stage"], "output_emission")
        self.assertEqual(trace[-1].get("state"), "TERMINAL")

    def test_bad_input_is_rejected_before_sources_or_discovery(self) -> None:
        original = open
        def public_schema_only(path: str | Path, mode: str = "r", buffering: int = -1,
                    encoding: str | None = None, errors: str | None = None,
                    newline: str | None = None, closefd: bool = True,
                    opener: Callable[[str, int], int] | None = None) -> object:
            self.assertNotIn(str(self.corpus.root), str(path))
            return original(path, mode, buffering, encoding, errors, newline, closefd, opener)
        with patch.object(engine, "run_discovery_step", side_effect=AssertionError("MUST_NOT_DISCOVER")), \
                patch("builtins.open", side_effect=public_schema_only):
            output, trace = run_with_trace({"case_id": "SYNTHETIC", "user_query": "", "profile": {}}, self.cfg)
        self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
        self.assertEqual(len(trace), 1)

    def test_nonobject_and_invalid_sensitive_input_fail_without_echo(self) -> None:
        values: tuple[object, ...] = (None, [], {"case_id": "SYNTHETIC", "user_query": "bolig", "profile": {"urgency": "PRIVATE_INPUT_CANARY"}})
        for value in values:
            with self.subTest(value=value):
                output, trace = run_with_trace(value, self.cfg)
                self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
                self.assertNotIn("PRIVATE_INPUT_CANARY", json.dumps(output))
                self.assertEqual(len(trace), 1)

    def test_phase2_terminal_crashes_emit_safe_output(self) -> None:
        stages = [stage for stage in engine.STAGES if stage not in ("knowledge_retrieval", "local_discovery")]
        cases = [(stage, False) for stage in stages] + [("output_emission", True)]
        for stage, partial_output in cases:
            with self.subTest(stage=stage, partial_output=partial_output):
                def crash(raw_context: object) -> None:
                    assert isinstance(raw_context, dict)
                    ctx = cast(dict[str, object], raw_context)
                    ctx["_answer"] = "REJECTED_RECOMMENDATION_CANARY"
                    if partial_output:
                        ctx["_output"] = {"answer": "REJECTED_RECOMMENDATION_CANARY"}
                    raise RuntimeError("PRIVATE_EXCEPTION_CANARY")
                with patch.dict(engine.STAGES, {stage: crash}), \
                        patch.object(engine, "run_discovery_step", return_value=discovery_fixture()):
                    output, trace = engine.run_with_trace(self.input, self.cfg)
                validate_output(output)
                self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
                self.assertEqual(output["routes"], [])
                self.assertEqual(output["claims"], [])
                self.assertNotIn("CANARY", json.dumps(output))
                self.assertEqual(next(t.get("state") for t in trace if t["stage"] == stage), "TERMINAL")
                self.assertEqual(trace[-1].get("state"), "TERMINAL")

    def test_phase2_recoverable_crashes_keep_explicit_incomplete_receipts(self) -> None:
        def crash(_ctx: Context) -> None:
            raise RuntimeError("PRIVATE_EXCEPTION_CANARY")
        for stage in ("knowledge_retrieval", "local_discovery"):
            with self.subTest(stage=stage), patch.dict(engine.STAGES, {stage: crash}), \
                    patch.object(engine, "run_discovery_step", return_value=discovery_fixture()):
                output, trace = engine.run_with_trace(self.input, self.cfg)
                validate_output(output)
                self.assertEqual(output["epistemic_state"], "UNVERIFIED")
                self.assertNotIn("PRIVATE_EXCEPTION_CANARY", json.dumps(output))
                self.assertEqual(next(t.get("state") for t in trace if t["stage"] == stage), "RECOVERABLE")
                if stage == "knowledge_retrieval":
                    assert "source_admission" in output["evidence"]
                    receipt = output["evidence"]["source_admission"]["per_track"]["T1"]
                    self.assertEqual(receipt["coverage"]["state"], "INCOMPLETE")
                    self.assertIn("source_admission_incomplete", output["uncertainty_expressed"])
                else:
                    self.assertEqual(output["execution_status"], "DISCOVERY_INCOMPLETE")
                    self.assertIn("local_availability_unverified", output["uncertainty_expressed"])

    def test_phase2_invalid_input_is_rejected_without_echo_or_discovery(self) -> None:
        values: tuple[object, ...] = (None, [], "PRIVATE_INPUT_CANARY", {"case_id": "SYNTHETIC", "user_query": "angst", "profile": {"age": "PRIVATE_INPUT_CANARY"}})
        for value in values:
            with self.subTest(value=value), patch.object(engine, "run_discovery_step", side_effect=AssertionError("MUST_NOT_DISCOVER")):
                output, trace = engine.run_with_trace(value, self.cfg)
                validate_output(output)
                self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
                self.assertNotIn("PRIVATE_INPUT_CANARY", json.dumps(output))
                self.assertEqual(len(trace), 1)

    def test_terminal_trace_overrides_earlier_recoverable_marker_in_both_phases(self) -> None:
        def crash(ctx: Context) -> None:
            engine.mark_stage(ctx, "answer_planning", engine.StageState.RECOVERABLE, "synthetic partial stage")
            raise RuntimeError("PRIVATE_EXCEPTION_CANARY")
        for runner, stages in ((engine.run_with_trace, engine.STAGES), (run_with_trace, STAGES)):
            with self.subTest(runner=runner.__module__), patch.dict(stages, {"answer_planning": crash}), \
                    patch.object(engine, "run_discovery_step", return_value=discovery_fixture()):
                output, trace = runner(self.input, self.cfg)
                validate_output(output)
                self.assertEqual(output["execution_status"], "EXECUTION_FAILED")
                self.assertEqual(next(t.get("state") for t in trace if t["stage"] == "answer_planning"), "TERMINAL")
