"""RC-10 evidence attachment tests (spec section 22 matrix).

Invariants:
- routes list stays labels-only; per-route evidence lives under
  evidence.route_evidence keyed by route_id
- per-claim evidence lives under evidence.claim_evidence keyed by claim_id
- only provenance ids that exist in the emitted provenance records are
  attached; unresolved refs are dropped, never fabricated
- conflicting claims are UNVERIFIED and carry no score-bearing evidence
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sut.context import make_context  # noqa: E402
from sut.phase2.pipeline import _provenance_records  # noqa: E402
from sut.phase2.routes import build_national_route_candidates  # noqa: E402
from sut.phase2.safety import evaluate_safety, load_rules  # noqa: E402
from sut.phase3.finalize import finalize  # noqa: E402
from sut.phase3.planner import s9_answer_planning  # noqa: E402


RULES = load_rules("data/safety-triage-rules-v2.json")


def _rec(record_id, claim, evidence_id, domain="mental_health"):
    return {
        "record_id": record_id,
        "source_type": "PROJECT_RESEARCH",
        "domain": domain,
        "domains": [domain],
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": "docs/%s.md" % record_id},
        "authority": "INTERNAL_DOC",
        "freshness": "CURRENT",
        "evidence_id": evidence_id,
        "gap_state": None,
        "historical_research": False,
    }


class EvidenceAttachmentTests(unittest.TestCase):
    def _ctx_with_records(self, records):
        ctx = make_context({
            "case_id": "EV-TEST",
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
        from sut.phase2.pipeline import (
            s5_local_discovery, s6_route_reasoning,
            s7_evidence_aggregation, s8_epistemic_assignment)
        s5_local_discovery(ctx)
        s6_route_reasoning(ctx)
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        s9_answer_planning(ctx)
        return ctx

    def _finalize(self, records):
        return finalize(self._ctx_with_records(records))

    def test_one_claim_one_source(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        out = self._finalize([rec])
        self.assertEqual(out["execution_status"], "SUCCESS")
        ce = out["evidence"]["claim_evidence"]
        verified = [c for c in ce.values() if c["provenance_ids"]]
        self.assertTrue(verified)
        self.assertTrue(all(p.startswith("P-K")
                            for c in ce.values() for p in c["provenance_ids"]))

    def test_one_route_one_source_national(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        out = self._finalize([rec])
        re_ = out["evidence"]["route_evidence"]
        self.assertEqual(len(re_), 1)
        (entry,) = re_.values()
        self.assertEqual(entry["evidence_ids"], ["E-D001"])
        self.assertEqual(entry["provenance_ids"], ["P-K001"])
        self.assertNotIn("source_url", entry)

    def test_one_route_one_source_local(self):
        ctx = self._ctx_with_records([])
        from sut.phase2.pipeline import (
            s6_route_reasoning, s7_evidence_aggregation,
            s8_epistemic_assignment)
        ctx["_s5_steps"] = [{"track_id": "T1", "domain": "mental_health",
                             "step": {"state": "COMPLETED", "services": [
                                 {"name": "Rask Psykisk Helsehjelp",
                                  "source_url": "https://www.drammen.kommune.no/x",
                                  "access_methods": ["phone"],
                                  "target_group": "voksne"}]}}]
        s6_route_reasoning(ctx)
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        s9_answer_planning(ctx)
        out = finalize(ctx)
        (entry,) = out["evidence"]["route_evidence"].values()
        self.assertEqual(entry["source_url"], "https://www.drammen.kommune.no/x")
        self.assertEqual(entry["provenance_ids"], ["P-D001"])

    def test_one_source_supports_multiple_claims(self):
        claim = "Nasjonal informasjon: 'Fastlegen' kan vurdere behov."
        rec = _rec("K-D001", claim, "E-D001")
        ctx = self._ctx_with_records([rec])
        ctx["_s7_claims"].extend([
            {"claim_id": "C-X1", "subject": "K-D001", "dimension": "knowledge_fact",
             "value": claim, "state": "VERIFIED", "authority": "INTERNAL_DOC",
             "evidence_ids": ["E-D001"], "provenance_ids": ["P-K001"]},
            {"claim_id": "C-X2", "subject": "K-D001", "dimension": "knowledge_fact",
             "value": claim + " (detalj)", "state": "VERIFIED",
             "authority": "INTERNAL_DOC",
             "evidence_ids": ["E-D001"], "provenance_ids": ["P-K001"]},
        ])
        from sut.phase3.finalize import _claim_evidence
        ce = _claim_evidence(ctx)
        self.assertEqual(ce["C-X1"]["provenance_ids"], ["P-K001"])
        self.assertEqual(ce["C-X2"]["provenance_ids"], ["P-K001"])

    def test_irrelevant_source_not_attached(self):
        # Irrelevant source in the SAME track: it is rendered as INFO and
        # gets its own claim evidence, but it never attaches to the route.
        from sut.phase2.pipeline import s6_route_reasoning
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        other = _rec("K-H001", "Husleiestotte gis via kommunen.", "E-H001",
                     domain="mental_health")
        out = self._finalize([rec, other])
        re_ = out["evidence"]["route_evidence"]
        (entry,) = re_.values()
        self.assertNotIn("P-K002", entry["provenance_ids"])
        self.assertEqual(entry["provenance_ids"], ["P-K001"])

    def test_conflicting_claims_excluded(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        ctx = self._ctx_with_records([rec])
        ctx["_s7_claims"].append({
            "claim_id": "C-C1", "subject": "K-D001",
            "dimension": "knowledge_fact", "value": "motsigelse",
            "state": "UNVERIFIED", "authority": "INTERNAL_DOC",
            "evidence_ids": ["E-D001"], "provenance_ids": ["P-K001"],
        })
        from sut.phase3.finalize import _claim_evidence
        ce = _claim_evidence(ctx)
        self.assertNotIn("C-C1", ce)

    def test_missing_evidence_never_fabricated(self):
        ctx = self._ctx_with_records([])
        ctx["_s7_claims"].append({
            "claim_id": "C-M1", "subject": "X", "dimension": "knowledge_fact",
            "value": "pasta", "state": "VERIFIED", "authority": "INTERNAL_DOC",
            "evidence_ids": ["E-NOPE"], "provenance_ids": ["P-NOPE"],
        })
        from sut.phase3.finalize import _claim_evidence
        ce = _claim_evidence(ctx)
        self.assertEqual(ce["C-M1"]["evidence_ids"], ["E-NOPE"])
        self.assertEqual(ce["C-M1"]["provenance_ids"], [])

    def test_truncated_evidence_span_still_resolves(self):
        claim = "Lang " * 80 + "'Fastlegen' finnes."
        rec = _rec("K-D001", claim, "E-D001")
        ctx = self._ctx_with_records([rec])
        provs = _provenance_records(ctx)
        self.assertEqual(len(provs[0]["evidence_span"]), 200)
        from sut.phase3.finalize import _claim_evidence
        ce = _claim_evidence(ctx)
        verified = [c for c in ce.values() if c["provenance_ids"]]
        self.assertTrue(verified)

    def test_no_fabricated_route_evidence(self):
        out = self._finalize([])
        self.assertEqual(out["evidence"]["route_evidence"], {})

    def test_unprovenanced_gates(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        out = self._finalize([rec])
        re_ = out["evidence"]["route_evidence"]
        unprov_routes = [rid for rid, e in re_.items() if not e["provenance_ids"]]
        self.assertEqual(unprov_routes, [])
        for c in out["evidence"]["claim_evidence"].values():
            self.assertTrue(c["provenance_ids"])

    def test_provenance_records_cover_attached_ids(self):
        rec = _rec("K-D001", "Nasjonal informasjon: 'Fastlegen' kan vurdere behov.",
                   "E-D001")
        out = self._finalize([rec])
        known = {p["id"] for p in out["provenance"]}
        for e in out["evidence"]["route_evidence"].values():
            self.assertTrue(set(e["provenance_ids"]) <= known)
        for c in out["evidence"]["claim_evidence"].values():
            self.assertTrue(set(c["provenance_ids"]) <= known)


if __name__ == "__main__":
    unittest.main()
