"""RC-08 track-scoped retrieval tests (spec section 10 scope matrix)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase2.knowledge import retrieve


class KnowledgeScopingTests(unittest.TestCase):
    def test_mental_health_query_excludes_cross_domain_docs(self):
        records = retrieve("bup henvisning fastlege", "mental_health")
        self.assertTrue(records)
        for r in records:
            if r["source_type"] == "FROZEN_RULE":
                self.assertEqual(r["domain"], "mental_health")
            else:
                self.assertIn("mental_health", r["domains"])

    def test_same_track_include_and_cross_track_exclusion(self):
        mh = retrieve("bup henvisning fastlege psykolog", "mental_health")
        self.assertTrue(mh)
        doc_ids_mh = [r["provenance"]["doc_id"] for r in mh
                      if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertIn("25-kommunale-psykiske-tjenester-barn-unge", doc_ids_mh)
        for domain in ("housing", "financial_support", "education"):
            recs = retrieve("bup henvisning fastlege psykolog", domain)
            doc_ids = [r["provenance"]["doc_id"] for r in recs
                       if r["source_type"] == "PROJECT_RESEARCH"]
            self.assertNotIn("25-kommunale-psykiske-tjenester-barn-unge", doc_ids)

    def test_housing_query_scopes_to_housing_docs(self):
        records = retrieve("bostoette depositum utkastelse", "housing")
        doc_records = [r for r in records if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertTrue(doc_records)
        for r in doc_records:
            self.assertIn("housing", r["domains"])

    def test_financial_query_scopes_to_financial_docs(self):
        records = retrieve("barnebidrag samvaersfradrag", "financial_support")
        doc_records = [r for r in records if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertTrue(doc_records)
        for r in doc_records:
            self.assertIn("financial_support", r["domains"])

    def test_child_safety_query_scopes_to_child_safety_docs(self):
        records = retrieve("barnevern bekymringsmelding vold", "child_safety")
        doc_records = [r for r in records if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertTrue(doc_records)
        for r in doc_records:
            self.assertIn("child_safety", r["domains"])

    def test_education_query_scopes_to_education_docs(self):
        records = retrieve("skolevegring tilrettelegging skolemiljoe", "education")
        doc_records = [r for r in records if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertTrue(doc_records)
        for r in doc_records:
            self.assertIn("education", r["domains"])

    def test_multi_domain_doc_reachable_from_every_tagged_domain(self):
        # Doc 31 is tagged mental_health + education in the frozen index.
        for domain in ("mental_health", "education"):
            records = retrieve("skolehelsetjenesten helsesykepleier", domain)
            doc_ids = [r["provenance"]["doc_id"] for r in records
                       if r["source_type"] == "PROJECT_RESEARCH"]
            self.assertIn("31-skolehelsetjenesten-i-dybden", doc_ids)

    def test_general_track_uses_general_fallback_docs(self):
        records = retrieve("hvor henvender jeg meg beslutningstre", "general")
        doc_records = [r for r in records if r["source_type"] == "PROJECT_RESEARCH"]
        self.assertTrue(doc_records)
        for r in doc_records:
            self.assertEqual(r["domains"], ["general"])

    def test_irrelevant_query_still_empty(self):
        self.assertEqual(retrieve("vaskemaskin garantiperiode kjopesvilkår", "general"), [])

    def test_index_without_domains_field_falls_back_to_general(self):
        import hashlib
        import json
        import os
        import shutil
        import tempfile
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        text = "bup henvisning fastlege"
        with open(os.path.join(tmp, "d.md"), "w", encoding="utf-8") as fh:
            fh.write(text)
        index = {"artifact": "t", "docs": [{
            "id": "d", "path": "d.md",
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "class": "DECISION_SUPPORT", "freshness_class": "CURRENT",
        }]}
        with open(os.path.join(tmp, "index.json"), "w", encoding="utf-8") as fh:
            json.dump(index, fh)
        # Scoped domain: no metadata domains -> doc excluded; only frozen
        # rules (domain-bound by registry) may match.
        recs = retrieve("bup henvisning fastlege", "mental_health",
                        index_path=os.path.join(tmp, "index.json"), repo_root=tmp)
        self.assertTrue(all(r["source_type"] == "FROZEN_RULE" for r in recs))
        # General domain: fallback allows it.
        recs = retrieve("bup henvisning fastlege", "general",
                        index_path=os.path.join(tmp, "index.json"), repo_root=tmp)
        self.assertEqual(len(recs), 1)

    def test_gap_scoping_respects_domain(self):
        records = retrieve("bup henvisning fastlege psykolog", "mental_health")
        gaps = [r for r in records if r["gap_state"]]
        self.assertTrue(gaps)
        for r in gaps:
            self.assertIn("mental_health", r["domains"])

    def test_rule_scoping_unchanged(self):
        records = retrieve("65 virkedager psykisk helsehjelp", "mental_health")
        rules = [r for r in records if r["source_type"] == "FROZEN_RULE"]
        self.assertTrue(rules)

    def test_max_records_respected_after_scoping(self):
        records = retrieve("bup henvisning fastlege 65 virkedager rettigheter",
                           "mental_health")
        self.assertLessEqual(len(records), 5)


if __name__ == "__main__":
    unittest.main()
