"""W3-RC-A route-proposition construction tests (spec sections 18-19).

Generic mechanism coverage only: no case IDs, no corpus strings beyond
project research docs already read at runtime. Table fixtures use real
rows from the frozen source docs so the structured path is exercised
end to end; one fixture is written to a temp file for an access-unclear
identity row the frozen docs do not contain.
"""

import os
import tempfile
import unittest

from sut.context import make_context
from sut.phase2.pipeline import (
    s6_route_reasoning,
    s7_evidence_aggregation,
    s8_epistemic_assignment,
)
from sut.phase2.routes import build_national_route_candidates
from sut.phase3.finalize import finalize
from sut.phase3.planner import s9_answer_planning


_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DOC26 = "26-beslutningsstotte-hvor-henvende-seg.md"

_DOC26_LINES = open(
    os.path.join(_REPO_ROOT, _DOC26), encoding="utf-8").read().splitlines()
_FASTLEGE_ROW = _DOC26_LINES[13]
_SKOLEHELSE_ROW = _DOC26_LINES[15]
_KOMMUNEPSYKOLOG_ROW = _DOC26_LINES[17]
_BUP_ROW = _DOC26_LINES[19]
# Scenario table (Situasjon header): must never mint a route target.
_SCENARIO_ROW = _DOC26_LINES[31]
# Row-prefix claim cut before the access cells: route target still mints,
# but access markers outside the span stay out (documented ceiling).
_KOMMUNEPSYKOLOG_PREFIX = (
    "| Kommunepsykolog/kommunalt lavterskeltilbud | Kartlegging, "
    "korttidsbehandling,")


def _rec(claim, evidence_id="E-D001", domain="mental_health",
         path=_DOC26, source_type="PROJECT_RESEARCH", gap_state=None,
         historical_research=False):
    return {
        "record_id": "K-D001",
        "source_type": source_type,
        "domain": domain,
        "track_domain": domain,
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": path},
        "authority": "INTERNAL_DOC",
        "freshness": "CURRENT",
        "evidence_id": evidence_id,
        "gap_state": gap_state,
        "historical_research": historical_research,
    }


def _discovery_step(domain="mental_health", services=None, state="COMPLETED"):
    return {"track_id": "T1", "domain": domain,
            "step": {"state": state, "evidence": [{"kind": "municipal_page"}],
                     "services": services or []}}


def _service(name, **extra):
    svc = {"name": name, "source_url": "https://kommune.example/tjeneste",
           "access_methods": ["phone"], "target_group": "voksne",
           "strong_access": False, "age_eligible": None}
    svc.update(extra)
    return svc


class RoutePropositionTestBase(unittest.TestCase):
    """Shared full-pipeline harness: S6-S8, plan, finalize."""

    def _ctx(self, records=None, steps=None):
        ctx = make_context({
            "case_id": "W3RCATEST",
            "user_query": "Hvor kan vi fa hjelp?",
            "profile": {"age": 17},
            "context": {},
            "location_context": {"municipality": "Drammen"},
            "timestamp_context": {"executed_at": "2026-09-16T10:00:00Z"},
        })
        ctx["safety"] = {"priority": "NOT_ACUTE", "signals": [],
                         "suppressed_routing": False}
        ctx["_config"] = {
            "knowledge_index_path": "data/knowledge-index-v1.json",
            "rules_registry_path": "data/rules-v1.json",
            "safety_rules_path": "data/safety-triage-rules-v2.json",
        }
        ctx["_s4_records"] = records or []
        ctx["_s5_steps"] = steps or []
        # Mirror s3_decomposition: tracks derive from injected evidence
        # domains so planner INFO scoping matches the real pipeline.
        domains = []
        for rec in (records or []):
            d = rec.get("track_domain") or rec.get("domain")
            if d and d not in domains:
                domains.append(d)
        for entry in (steps or []):
            if entry["domain"] not in domains:
                domains.append(entry["domain"])
        ctx["tracks"] = [
            {"track_id": "T%d" % (i + 1), "domain": d,
             "sub_utterance": ctx["input"]["user_query"],
             "status": "PENDING", "needs_local_discovery": False}
            for i, d in enumerate(domains)]
        ctx["_s5_incomplete"] = any(
            e["step"]["state"] != "COMPLETED" for e in (steps or []))
        s6_route_reasoning(ctx)
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        return ctx

    def _final(self, records=None, steps=None):
        ctx = self._ctx(records, steps)
        s9_answer_planning(ctx)
        return ctx, finalize(ctx)


class TestMatrix(RoutePropositionTestBase):
    """Spec section 18 cases 1-20."""

    def test_01_single_service_target(self):
        routes = build_national_route_candidates([_rec(_FASTLEGE_ROW)])
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "Fastlege")
        self.assertEqual(routes[0]["route_state"], "EXISTENCE_ONLY")

    def test_02_direct_access_path(self):
        routes = build_national_route_candidates([_rec(_FASTLEGE_ROW)])
        self.assertEqual(routes[0]["self_referral"], True)

    def test_03_referral_path(self):
        routes = build_national_route_candidates([_rec(_BUP_ROW)])
        self.assertEqual(routes[0]["service_type"],
                         "BUP (spesialisthelsetjenesten)")
        self.assertEqual(routes[0]["self_referral"], False)

    def test_04_age_conditioned_route(self):
        step = _discovery_step(services=[
            _service("HFU", strong_access=True, age_eligible=True)])
        ctx = self._ctx(steps=[step])
        routes = [r for r in ctx["_s6_routes"] if r["scope"] == "MUNICIPAL"]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["age_eligible"], "VERIFIED")
        self.assertEqual(routes[0]["route_state"], "FULLY_VERIFIED")

    def test_05_severity_conditioned_candidate(self):
        step = _discovery_step(services=[
            _service("BUP", target_group="alvorlige vansker")])
        ctx = self._ctx(steps=[step])
        routes = [r for r in ctx["_s6_routes"] if r["scope"] == "MUNICIPAL"]
        self.assertEqual(routes[0]["scenario_relevant"], "VERIFIED")
        self.assertEqual(routes[0]["target_population"], "alvorlige vansker")

    def test_06_acute_safety_suppresses_routes(self):
        ctx = self._ctx(records=[_rec(_FASTLEGE_ROW)])
        ctx["safety"] = {"priority": "ACUTE_RISK_NOW", "signals": ["vold"],
                         "suppressed_routing": True}
        ctx["tracks"] = []
        ctx["_s3_skipped"] = True
        ctx["_s5_steps"] = []
        ctx["_s4_records"] = []
        s6_route_reasoning(ctx)
        self.assertEqual(ctx["_s6_routes"], [])
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        s9_answer_planning(ctx)
        self.assertEqual(ctx["answer_plan"]["blocks"][0]["kind"],
                         "SAFETY_INSTRUCTION")

    def test_07_two_parallel_routes(self):
        routes = build_national_route_candidates(
            [_rec(_FASTLEGE_ROW, "E-D001"), _rec(_SKOLEHELSE_ROW, "E-D002")])
        self.assertEqual([r["service_type"] for r in routes],
                         ["Fastlege", "Skolehelsetjeneste"])

    def test_08_local_route(self):
        step = _discovery_step(services=[_service("Kommunal lavterskel")])
        ctx = self._ctx(steps=[step])
        routes = [r for r in ctx["_s6_routes"] if r["scope"] == "MUNICIPAL"]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["evidence_refs"], ["E-DISC-01"])
        self.assertEqual(routes[0]["provenance_refs"],
                         ["https://kommune.example/tjeneste"])

    def test_09_national_route(self):
        routes = build_national_route_candidates([_rec(_FASTLEGE_ROW)])
        self.assertEqual(routes[0]["scope"], "NATIONAL")
        self.assertEqual(routes[0]["provenance_refs"], ["P-K001"])

    def test_10_track_scoped_routes(self):
        recs = [_rec(_FASTLEGE_ROW, "E-D001", domain="mental_health"),
                _rec(_SKOLEHELSE_ROW, "E-D002", domain="education")]
        ctx = self._ctx(recs)
        by_domain = {r["service_type"]: r["track_domain"]
                     for r in ctx["_s6_routes"]}
        self.assertEqual(by_domain.get("Fastlege"), "mental_health")
        self.assertEqual(by_domain.get("Skolehelsetjeneste"), "education")

    def test_11_multi_track_independent_routes(self):
        steps = [
            _discovery_step("mental_health",
                            services=[_service("Kommunal lavterskel")]),
            _discovery_step("housing",
                            services=[_service("Boligsosial radgiver")]),
        ]
        ctx = self._ctx(steps=steps)
        domains = {r["track_domain"] for r in ctx["_s6_routes"]}
        self.assertEqual(domains, {"mental_health", "housing"})

    def test_12_insufficient_evidence_gap_record(self):
        routes = build_national_route_candidates(
            [_rec("Registrert hull om kommunalt tilbud.",
                  gap_state="REGISTERED_GAP")])
        self.assertEqual(routes, [])

    def test_13_no_actionable_service(self):
        routes = build_national_route_candidates(
            [_rec("Det finnes flere relevante tilbud i kommunen.")])
        self.assertEqual(routes, [])

    def test_14_access_path_uncertain_stays_unclear(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".md")
        self.addCleanup(os.remove, tmp_path)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("| Instans | Hovedrolle | Typisk inngang |\n")
            fh.write("|---|---|---|\n")
            fh.write("| Testtilbud | Gir radgivning | Telefon hverdager |\n")
        routes = build_national_route_candidates(
            [_rec("| Testtilbud | Gir radgivning | Telefon hverdager |",
                  path=tmp_path)])
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["self_referral"], "UNCLEAR")
        self.assertEqual(routes[0]["access_verified"], "UNRESOLVED")

    def test_15_retrieval_failure_no_routes(self):
        ctx, out = self._final()
        self.assertEqual(out["routes"], [])
        self.assertTrue(out["no_route_asserted"])

    def test_16_no_supported_route_rules_only(self):
        rec = _rec("Prioriteringsforskriftens frister gjelder.",
                   source_type="FROZEN_RULE")
        ctx, out = self._final([rec])
        self.assertEqual(out["routes"], [])
        self.assertTrue(out["no_route_asserted"])

    def test_17_kb_fragment_not_a_target(self):
        recs = [
            _rec("Fastlege gir grunnvurdering som ikke omfatter "
                 "langtidsbehandling av komplekse vansker.", path=None),
            _rec(_FASTLEGE_ROW, path=None),
        ]
        self.assertEqual(build_national_route_candidates(recs), [])

    def test_18_section_heading_not_a_target(self):
        routes = build_national_route_candidates(
            [_rec("## 1. Trekkplaster per instans (sammendrag)", path=None)])
        self.assertEqual(routes, [])

    def test_19_source_ref_scenario_row_not_a_target(self):
        routes = build_national_route_candidates([_rec(_SCENARIO_ROW)])
        self.assertEqual(routes, [])

    def test_20_route_survives_plan_render_finalize(self):
        ctx, out = self._final([_rec(_FASTLEGE_ROW, "E-D001")])
        self.assertEqual(out["execution_status"], "SUCCESS")
        self.assertIn("Fastlege", out["routes"])
        self.assertFalse(out["no_route_asserted"])
        plan_routes = [b for b in ctx["answer_plan"]["blocks"]
                       if b["kind"] in ("PRIMARY_ROUTE", "SECONDARY_ROUTE")]
        self.assertTrue(plan_routes)
        self.assertIn("Fastlege", out["answer"])

    def test_row_prefix_access_markers_outside_span(self):
        # Documented W3-RC-A ceiling: self_referral only reads markers
        # inside the claim span; a prefix cut before the access cells
        # stays UNCLEAR instead of inventing access semantics.
        routes = build_national_route_candidates(
            [_rec(_KOMMUNEPSYKOLOG_PREFIX)])
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"],
                         "Kommunepsykolog/kommunalt lavterskeltilbud")
        self.assertEqual(routes[0]["self_referral"], "UNCLEAR")


class TestHardGates(RoutePropositionTestBase):
    """Spec section 19 zero-gates over accumulated fixtures."""

    def _all_routes(self):
        fixtures = [
            ([_rec(_FASTLEGE_ROW, "E-D001")], []),
            ([_rec(_BUP_ROW, "E-D002")], []),
            ([_rec(_SKOLEHELSE_ROW, "E-D003")], []),
            ([], [_discovery_step(services=[
                _service("Kommunal lavterskel"),
                _service("HFU", age_eligible=True)])]),
        ]
        routes = []
        for records, steps in fixtures:
            ctx = self._ctx(records, steps)
            routes.extend(ctx["_s6_routes"])
        return routes

    def test_route_without_track_binding_zero(self):
        for r in self._all_routes():
            self.assertTrue(r["track_domain"])

    def test_structured_route_without_provenance_zero(self):
        for r in self._all_routes():
            self.assertTrue(r["evidence_refs"])
            self.assertTrue(r["provenance_refs"])

    def test_rendered_route_without_structured_route_zero(self):
        ctx, out = self._final([_rec(_FASTLEGE_ROW, "E-D001")])
        structured = {r["service_type"] for r in ctx["_s6_routes"]}
        for label in out["routes"]:
            self.assertIn(label, structured)

    def test_supported_route_lost_zero(self):
        ctx, out = self._final([_rec(_FASTLEGE_ROW, "E-D001")])
        structured = {r["service_type"] for r in ctx["_s6_routes"]
                      if r["route_state"] != "UNVERIFIED"}
        for label in structured:
            self.assertIn(label, out["routes"])

    def test_fragment_heading_sourceref_never_targets(self):
        rejects = [
            _rec("Fastlege gir grunnvurdering som ikke omfatter "
                 "langtidsbehandling av komplekse vansker.", path=None),
            _rec("## 1. Trekkplaster per instans (sammendrag)", path=None),
            _rec(_SCENARIO_ROW),
        ]
        self.assertEqual(build_national_route_candidates(rejects), [])


if __name__ == "__main__":
    unittest.main()
