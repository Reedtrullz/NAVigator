"""Phase 3 S9/S10/S11 unit tests (TDD cycles per spec section 26).

Ctx objects are built through sut.context.make_context plus targeted
injections of structured stage state; component-level synthetic routes
cover states that the replay corpus cannot reach naturally.
"""

import unittest

from sut.context import make_context, mark_stage, StageState

from sut.phase3.planner import plan, sort_routes, s9_answer_planning
from sut.phase3.render import render, s10_answer_rendering, ascii_text
from sut.phase3.finalize import finalize


def base_ctx():
    ctx = make_context({
        "case_id": "UT",
        "user_query": "Jeg trenger psykisk helsehjelp i kommunen",
        "profile": {"age": 19},
        "context": {},
        "location_context": {"municipality": "Drammen"},
        "timestamp_context": {"executed_at": "2026-09-14T10:00:00Z"},
    })
    ctx["safety"] = {"priority": "NOT_ACUTE", "signals": [],
                      "suppressed_routing": False}
    return ctx


def route(rid, name, state="EXISTENCE_ONLY", domain="mental_health",
          scenario="VERIFIED", access="UNRESOLVED"):
    return {
        "route_id": rid,
        "service_type": name,
        "track_domain": domain,
        "route_state": state,
        "scenario_relevant": scenario,
        "access_verified": access,
        "age_eligible": "UNRESOLVED",
        "service_exists": "VERIFIED",
        "contact_verified": "UNRESOLVED",
        "evidence_refs": [],
        "provenance_refs": [],
    }


def inject(ctx, routes=None, records=None, conflicts=None, steps=1,
           incomplete=False):
    ctx["_s6_routes"] = routes or []
    ctx["_s4_records"] = records or []
    ctx["_s7_claims"] = []
    ctx["_s7_conflicts"] = conflicts or []
    ctx["_s5_steps"] = [{"track_id": "T1", "domain": "mental_health",
                         "step": {"state": "COMPLETED", "services": []}}] * steps
    ctx["_s5_incomplete"] = incomplete
    top = "UNVERIFIED"
    if routes:
        top = min((r["route_state"] for r in routes),
                  key=["UNVERIFIED", "EXISTENCE_ONLY", "ACCESS_PARTIAL",
                       "FULLY_VERIFIED"].index)
    ctx["epistemic_states"] = {
        "top_level": top,
        "per_track": {"T1": top},
        "per_route": [],
    }
    return ctx


def discovery_step(name, url):
    return {"track_id": "T1", "domain": "mental_health",
            "step": {"state": "COMPLETED", "services": [
                {"name": name, "source_url": url,
                 "access_methods": ["phone"],
                 "target_group": "voksne"}]}}



class SafetyFirstOrdering(unittest.TestCase):
    """Cycle 1: safety instruction precedes all routing content."""

    def test_acute_suppressed_first_block(self):
        ctx = base_ctx()
        ctx["safety"] = {"priority": "ACUTE_RISK_NOW", "signals": ["vold"],
                          "suppressed_routing": True}
        ctx["tracks"] = []
        inject(ctx)
        p = plan(ctx)
        self.assertEqual(p["blocks"][0]["kind"], "SAFETY_INSTRUCTION")
        ctx["answer_plan"] = p
        answer = render(ctx)
        self.assertTrue(answer.startswith("Ved umiddelbar livsfare"))

    def test_urgent_lead_before_routes(self):
        ctx = base_ctx()
        ctx["safety"]["priority"] = "URGENT_NOT_ACUTE"
        inject(ctx, routes=[route("R-1", "Rask Psykisk Helsehjelp")])
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertLess(answer.index("Dette hoerstes alvorlig"),
                        answer.index("Anbefalt neste steg"))


class RouteOrdering(unittest.TestCase):
    """Cycle 2: deterministic route ordering, no weighted scores."""

    def test_domain_priority_beats_state(self):
        routes = [route("R-2", "B", "FULLY_VERIFIED", domain="housing"),
                  route("R-1", "A", "EXISTENCE_ONLY", domain="child_safety")]
        ordered = sort_routes(routes)
        self.assertEqual(ordered[0]["route_id"], "R-1")

    def test_state_priority_within_domain(self):
        routes = [route("R-2", "B", "EXISTENCE_ONLY"),
                  route("R-1", "A", "FULLY_VERIFIED")]
        ordered = sort_routes(routes)
        self.assertEqual(ordered[0]["route_id"], "R-1")

    def test_stable_order_for_equal_keys(self):
        routes = [route("R-1", "Same"), route("R-2", "Same")]
        self.assertEqual([r["route_id"] for r in sort_routes(routes)],
                         ["R-1", "R-2"])


class MultiTrackRendering(unittest.TestCase):
    """Cycle 3: multi-track plans stay separate."""

    def test_two_tracks_two_route_blocks(self):
        ctx = base_ctx()
        inject(ctx, routes=[
            route("R-MH-1", "Rask Psykisk Helsehjelp", domain="mental_health"),
            route("R-HO-1", "Boligtilbud", domain="housing"),
        ], steps=2)
        p = plan(ctx)
        kinds = [b["kind"] for b in p["blocks"]]
        self.assertEqual(kinds.count("PRIMARY_ROUTE"), 1)
        self.assertEqual(kinds.count("SECONDARY_ROUTE"), 1)
        track_ids = {b["track_id"] for b in p["blocks"]
                     if b["kind"] in ("PRIMARY_ROUTE", "SECONDARY_ROUTE")}
        self.assertEqual(track_ids, {"mental_health", "housing"})


class FullWording(unittest.TestCase):
    """Cycle 4: FULLY_VERIFIED wording (synthetic; unreachable in replay)."""

    def test_fully_verified_wording(self):
        ctx = base_ctx()
        r = route("R-1", "Familieteamet", state="FULLY_VERIFIED",
                  access="VERIFIED")
        inject(ctx, routes=[r])
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("er verifisert i oppslaget", answer)
        self.assertNotIn("tilgang er ikke verifisert", answer)


class AccessPartialWording(unittest.TestCase):
    """Cycle 5: ACCESS_PARTIAL qualifies access."""

    def test_access_partial_wording(self):
        ctx = base_ctx()
        inject(ctx, routes=[route("R-1", "Stotte Nar Livet Er Krevende",
                                  state="ACCESS_PARTIAL", access="PARTIAL")])
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("finnes og er relevant, men tilgang er ikke verifisert",
                      answer)


class ExistenceOnlyWording(unittest.TestCase):
    """Cycle 6: EXISTENCE_ONLY never asserts verified access."""

    def test_existence_only_wording(self):
        ctx = base_ctx()
        inject(ctx, routes=[route("R-1", "Helsestasjon For Ungdom")])
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("registrert i oppslaget", answer)
        self.assertIn("Aldersgrense og tilgang er ikke verifisert", answer)
        self.assertNotIn("verifisert i oppslaget", answer)


class DiscoveryIncompleteWording(unittest.TestCase):
    """Cycle 7: DISCOVERY_INCOMPLETE disclaimer."""

    def test_incomplete_disclaimer_present(self):
        ctx = base_ctx()
        inject(ctx, incomplete=True)
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("ble ikke fullfoert", answer)
        self.assertIn("ikke det samme som at kommunen ikke har tilbud", answer)

    def test_negative_existence_absent(self):
        ctx = base_ctx()
        inject(ctx, incomplete=True)
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertNotIn("har ikke tilbud", answer.lower())
        self.assertNotIn("mangler tilbud", answer.lower())


class SourceConflict(unittest.TestCase):
    """Cycle 8: conflict visible, no silent source choice."""

    def test_conflict_rendered(self):
        ctx = base_ctx()
        conflicts = [{"subject": "R-MH-1", "dimension": "access_verified",
                      "claim_ids": ["C-1", "C-2"],
                      "values": ["VERIFIED", "FAILED"]}]
        inject(ctx, conflicts=conflicts)
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("Kildene sier motstridende ting om R-MH-1", answer)
        self.assertIn("ikke lost", answer)


class NegativeClaimPrevention(unittest.TestCase):
    """Cycle 9: NO_ROUTE_FOUND never becomes NO_SERVICE_EXISTS."""

    def test_no_route_wording_has_disclaimer(self):
        ctx = base_ctx()
        inject(ctx)
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("Fant ingen registrerte kommunale tilbud", answer)
        self.assertIn("Det betyr ikke at tilbudet ikke finnes", answer)


class ProvenanceLinking(unittest.TestCase):
    """Cycle 10: provenance rendered and linked in structured output."""

    def test_provenance_lines_render(self):
        ctx = base_ctx()
        inject(ctx)
        ctx["_s5_steps"] = [discovery_step(
            "Rask Psykisk Helsehjelp", "https://www.drammen.kommune.no/x")]
        ctx["answer_plan"] = plan(ctx)
        answer = render(ctx)
        self.assertIn("Kilde P-D001:", answer)
        self.assertIn("https://www.drammen.kommune.no/x", answer)

    def test_structured_provenance_preserved(self):
        ctx = base_ctx()
        inject(ctx, routes=[route("R-1", "Rask Psykisk Helsehjelp")])
        ctx["_s5_steps"] = [discovery_step(
            "Rask Psykisk Helsehjelp", "https://www.drammen.kommune.no/x")]
        ctx["answer_plan"] = plan(ctx)
        out = finalize(ctx)
        self.assertEqual(out["execution_status"], "SUCCESS")
        self.assertEqual(len(out["provenance"]), 1)
        self.assertEqual(out["provenance"][0]["id"], "P-D001")


class FinalSchemaValidation(unittest.TestCase):
    """Cycle 11: consistency + schema failures fail closed."""

    def _success_ctx(self):
        ctx = base_ctx()
        ctx["_s5_steps"] = [discovery_step(
            "Rask Psykisk Helsehjelp", "https://www.drammen.kommune.no/x")]
        inject(ctx, routes=[route("R-1", "Rask Psykisk Helsehjelp")])
        ctx["answer_plan"] = plan(ctx)
        return ctx

    def test_success_path_valid(self):
        out = finalize(self._success_ctx())
        self.assertEqual(out["execution_status"], "SUCCESS")
        self.assertIn("Rask Psykisk Helsehjelp", out["answer"])

    def test_consistency_failure_fails_closed(self):
        ctx = self._success_ctx()
        # Corrupt the plan: route ref that does not exist in structured state.
        ctx["answer_plan"]["blocks"][0]["span_refs"] = ["route:R-NOPE"]
        out = finalize(ctx)
        self.assertEqual(out["execution_status"], "EXECUTION_FAILED")
        self.assertTrue(any("consistency failed" in f["message"]
                            for f in out["failures"]))

    def test_terminal_failure_marks_tracks_failed(self):
        ctx = base_ctx()
        inject(ctx)
        mark_stage(ctx, "knowledge_retrieval", StageState.TERMINAL, "boom")
        ctx["answer_plan"] = plan(ctx)
        out = finalize(ctx)
        self.assertEqual(out["execution_status"], "EXECUTION_FAILED")


class DeterministicOutput(unittest.TestCase):
    """Cycle 12: same ctx state, byte-identical render."""

    def _rendered(self):
        ctx = base_ctx()
        ctx["_s5_steps"] = [discovery_step(
            "Rask Psykisk Helsehjelp", "https://www.drammen.kommune.no/x")]
        inject(ctx, routes=[route("R-1", "Rask Psykisk Helsehjelp")])
        ctx["answer_plan"] = plan(ctx)
        return render(ctx)

    def test_byte_identical(self):
        self.assertEqual(self._rendered(), self._rendered())

    def test_ascii_transliteration(self):
        self.assertEqual(ascii_text("T\u00e6r\u00f8\u00e5"), "Taeroeaa")


class StageWiring(unittest.TestCase):
    """S9/S10 mark ctx state exactly as the pipeline expects."""

    def test_s9_sets_plan(self):
        ctx = base_ctx()
        inject(ctx)
        s9_answer_planning(ctx)
        self.assertIn("blocks", ctx["answer_plan"])

    def test_s10_sets_answer(self):
        ctx = base_ctx()
        inject(ctx)
        ctx["answer_plan"] = plan(ctx)
        s10_answer_rendering(ctx)
        self.assertTrue(ctx["_answer"])
