"""RC-03 national route candidate tests (generic mechanisms only)."""

import unittest

from sut.context import make_context
from sut.phase2.knowledge import retrieve
from sut.phase2.pipeline import _provenance_records
from sut.phase2.routes import build_national_route_candidates
from sut.phase3.finalize import finalize
from sut.phase2.safety import evaluate_safety, load_rules


RULES = load_rules("data/safety-triage-rules-v2.json")


def _rec(record_id, claim, evidence_id, domain="mental_health",
         source_type="PROJECT_RESEARCH", gap_state=None,
         historical_research=False):
    return {
        "record_id": record_id,
        "source_type": source_type,
        "domain": domain,
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": "docs/x.md"},
        "authority": "INTERNAL_DOC",
        "freshness": "CURRENT",
        "evidence_id": evidence_id,
        "gap_state": gap_state,
        "historical_research": historical_research,
    }


class TestBuildNationalRoutes(unittest.TestCase):
    def test_quoted_claim_becomes_existence_only_route(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        routes = build_national_route_candidates([rec])
        self.assertEqual(len(routes), 1)
        r = routes[0]
        self.assertEqual(r["service_type"], "Fastlegen")
        self.assertEqual(r["route_state"], "EXISTENCE_ONLY")
        self.assertEqual(r["scope"], "NATIONAL")
        self.assertEqual(r["evidence_refs"], ["E-D001"])
        self.assertEqual(r["provenance_refs"], ["P-K001"])
        self.assertEqual(r["service_exists"], "VERIFIED")
        self.assertEqual(r["access_verified"], "UNRESOLVED")

    def test_bold_claim_becomes_route(self):
        rec = _rec("K-D001", "Nasjonal informasjon: **Helsesykepleier** tilbyr samtaler.",
                   "E-D001")
        routes = build_national_route_candidates([rec])
        self.assertEqual(routes[0]["service_type"], "Helsesykepleier")

    def test_rules_and_gap_records_stay_uncertainty_only(self):
        recs = [
            _rec("K-R001", "Prioriteringsforskriftens frister gjelder.",
                 "E-R001", source_type="FROZEN_RULE"),
            _rec("K-D001", "Registrert hull om tilbud.",
                 "E-D001", source_type="GAP", gap_state="REGISTERED_GAP"),
            _rec("K-D002", "Historisk observasjon om tilbud.",
                 "E-D002", historical_research=True),
        ]
        self.assertEqual(build_national_route_candidates(recs), [])

    def test_ungrounded_claim_fails_open_to_no_route(self):
        rec = _rec("K-D001", "Det finnes flere relevante tilbud i kommunen.",
                   "E-D001")
        self.assertEqual(build_national_route_candidates([rec]), [])

    def test_dedup_by_domain_and_service(self):
        recs = [
            _rec("K-D001", "'Fastlegen' kan vurdere behov.", "E-D001"),
            _rec("K-D002", "'Fastlegen' har lang erfaring.", "E-D002"),
        ]
        routes = build_national_route_candidates(recs)
        self.assertEqual(len(routes), 1)

    def test_provenance_offset_follows_discovery_count(self):
        rec = _rec("K-D001", "'Fastlegen' kan vurdere behov.", "E-D001")
        routes = build_national_route_candidates([rec], discovery_service_count=3)
        self.assertEqual(routes[0]["provenance_refs"], ["P-K004"])


class TestNationalRoutesInPipeline(unittest.TestCase):
    def _ctx_with_records(self, records):
        ctx = make_context({
            "case_id": "ROUT-TEST",
            "user_query": "Hvor kan vi fa hjelp?",
            "profile": {"age": 17},
        })
        evaluate_safety(ctx, RULES)
        ctx["_config"] = {
            "knowledge_index_path": "data/knowledge-index-v1.json",
            "rules_registry_path": "data/rules-v1.json",
        }
        ctx["_s4_records"] = records
        ctx["tracks"] = [{
            "track_id": "T1",
            "domain": records[0]["domain"] if records else "general",
            "sub_utterance": ctx["input"]["user_query"],
            "status": "PENDING",
            "needs_local_discovery": False,
        }]
        from sut.phase2.pipeline import s4_knowledge_retrieval, s6_route_reasoning
        s6_route_reasoning(ctx)
        from sut.phase2.pipeline import s7_evidence_aggregation, s8_epistemic_assignment
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        return ctx

    def _finalize(self, records):
        ctx = self._ctx_with_records(records)
        from sut.phase3.planner import s9_answer_planning
        s9_answer_planning(ctx)
        return finalize(ctx)

    def _live_ctx(self, query):
        ctx = make_context({
            "case_id": "ROUT-TEST",
            "user_query": query,
            "profile": {"age": 17},
        })
        evaluate_safety(ctx, RULES)
        ctx["_config"] = {
            "knowledge_index_path": "data/knowledge-index-v1.json",
            "rules_registry_path": "data/rules-v1.json",
        }
        from sut.phase2.pipeline import (
            s4_knowledge_retrieval, s6_route_reasoning,
            s7_evidence_aggregation, s8_epistemic_assignment,
        )
        s4_knowledge_retrieval(ctx)
        s6_route_reasoning(ctx)
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        return ctx

    def test_synthetic_national_route_flows_to_output(self):
        rec = _rec("K-D001",
                   "Nasjonal informasjon: 'Skolehelsetjenesten' kan vurdere behov.",
                   "E-D001")
        out = self._finalize([rec])
        self.assertEqual(out["execution_status"], "SUCCESS")
        self.assertIn("Skolehelsetjenesten", out["routes"])
        self.assertFalse(out["no_route_asserted"])
        prov_ids = {p["id"] for p in out["provenance"]}
        self.assertIn("P-K001", prov_ids)

    def test_provenance_refs_resolve(self):
        recs = [
            _rec("K-D001", "'Fastlegen' kan vurdere behov.", "E-D001"),
            _rec("K-D002", "'Rådgivning for unge' er et lavterskeltilbud.", "E-D002"),
        ]
        ctx = self._ctx_with_records(recs)
        prov_ids = {p["id"] for p in _provenance_records(ctx)}
        for r in ctx["_s6_routes"]:
            for ref in r["provenance_refs"]:
                self.assertIn(ref, prov_ids)

    def test_aeoeaa_label_passes_consistency(self):
        rec = _rec("K-D001", "'Rådgivning for unge' er et lavterskeltilbud.", "E-D001")
        out = self._finalize([rec])
        self.assertEqual(out["execution_status"], "SUCCESS")

    def test_live_index_routes_stay_consistent(self):
        ctx = self._live_ctx("helsesykepleier ungdom")
        prov_ids = {p["id"] for p in _provenance_records(ctx)}
        for r in ctx["_s6_routes"]:
            for ref in r["provenance_refs"]:
                self.assertIn(ref, prov_ids)
            self.assertEqual(r["scope"], "NATIONAL")


if __name__ == "__main__":
    unittest.main()
