from pathlib import Path
import unittest
from typing import Any

from ..context import make_context
from .aggregate import build_claims, derive_track_state
from .knowledge import _doc_record, load_knowledge, retrieve
from .pipeline import _default_config, _provenance_records, s4_knowledge_retrieval
from .synthetic_fixtures import SyntheticCorpus


class SourceAdmissionTests(unittest.TestCase):
    def test_unapproved_metadata_cannot_promote_source_without_changing_bytes(self):
        c = SyntheticCorpus(self)
        entry = c.add_doc(text="bolig old snapshot", freshness="POINT_IN_TIME", verified_date="2026-09-01")
        entry.update(freshness_class="CURRENT", verified_date="2026-10-11")
        c.save_index()
        result = retrieve("bolig", "housing", **c.retrieval_args())
        self.assertEqual(result.records, [])
        self.assertEqual(result.failures, [{"reason": "SOURCE_NOT_ADMITTED"}])

    def test_sha_rejection_propagates(self):
        c = SyntheticCorpus(self)
        c.add_doc()
        (c.root / "public.md").write_text("changed bytes", encoding="utf-8")
        result = retrieve("bolig", "housing", **c.retrieval_args())
        self.assertEqual(result.records, [])
        self.assertEqual(result.failures, [{"reason": "SHA_MISMATCH"}])
        self.assertEqual(result.coverage["state"], "INCOMPLETE")

    def test_missing_differs_from_no_match(self):
        c = SyntheticCorpus(self)
        c.add_doc(text="bolig")
        result = retrieve("unrelated", "housing", **c.retrieval_args())
        self.assertEqual(result.records, [])
        self.assertEqual(result.coverage["state"], "COMPLETE")
        (c.root / "public.md").unlink()
        result = retrieve("unrelated", "housing", **c.retrieval_args())
        self.assertEqual(result.coverage["state"], "INCOMPLETE")
        self.assertEqual(result.failures, [{"reason": "FILE_MISSING"}])

    def test_gap_not_verified_fact(self):
        c = SyntheticCorpus(self)
        c.add_doc("69-kunnskapshullregister", "bolig uncertainty", domain="housing")
        docs, _ = load_knowledge(str(c.index), str(c.root), access_profile=c.profile)
        records = [_doc_record(docs[0], "bolig uncertainty", 1)]
        claims = build_claims([], records)
        self.assertEqual(claims[0]["state"], "UNRESOLVED")
        self.assertEqual(derive_track_state([], records, {"state": "NOT_APPLICABLE"}), "UNVERIFIED")

    def test_gap_class_not_dependent_on_known_document_id(self):
        c = SyntheticCorpus(self)
        c.add_doc("other-gap", "bolig uncertainty", doc_class="GAP_REGISTRY", verified_date="2026-10-01")
        result = retrieve("bolig", "housing", **c.retrieval_args())
        self.assertNotEqual(build_claims([], result.records)[0]["state"], "VERIFIED")


    def test_historical_not_current(self):
        c = SyntheticCorpus(self)
        c.add_doc(text="bolig old snapshot", freshness="POINT_IN_TIME", verified_date="2026-09-01")
        docs, _ = load_knowledge(str(c.index), str(c.root), access_profile=c.profile)
        self.assertNotEqual(build_claims([], [_doc_record(docs[0], "bolig old snapshot", 1)])[0]["state"], "VERIFIED")

    def test_verified_date_is_source_specific(self):
        c = SyntheticCorpus(self)
        c.add_doc("a", "bolig source A", verified_date="2026-10-01")
        c.add_doc("b", "bolig source B")
        docs, _ = load_knowledge(str(c.index), str(c.root), access_profile=c.profile)
        ctx: dict[str, Any] = make_context({"case_id": "SYNTHETIC", "user_query": "bolig", "profile": {}})
        ctx["_s4_records"] = [_doc_record(d, "bolig", i) for i, d in enumerate(docs, 1)]
        prov = _provenance_records(ctx)
        self.assertEqual([p["verified_at"] for p in prov], ["2026-10-01", ""])

    def test_s4_retains_redacted_per_track_failures(self):
        c = SyntheticCorpus(self)
        c.add_doc()
        (c.root / "public.md").unlink()
        ctx: dict[str, Any] = make_context({"case_id": "SYNTHETIC", "user_query": "bolig", "profile": {}})
        ctx["tracks"] = [{"track_id": "T1", "domain": "housing"}]
        cfg = _default_config()
        cfg.update(knowledge_index_path=str(c.index), knowledge_repo_root=str(c.root),
                   rules_registry_path=str(c.rules), knowledge_access_profile=c.profile)
        ctx["_config"] = cfg
        s4_knowledge_retrieval(ctx)
        self.assertEqual(ctx["_s4_admission"]["T1"]["failures"], [{"reason": "FILE_MISSING"}])
        self.assertTrue(any(f["stage"] == "knowledge_retrieval" for f in ctx["failures"]))
        self.assertNotIn(str(Path(c.root)), str(ctx["failures"]))
