import builtins
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from .knowledge import load_knowledge, retrieve
from .synthetic_fixtures import SyntheticCorpus


class PrivacyScopeTests(unittest.TestCase):
    def load(self, corpus, profile=None):
        return load_knowledge(str(corpus.index), str(corpus.root),
                              access_profile=corpus.profile if profile is None else profile)

    def test_no_profile_opens_nothing(self):
        corpus = SyntheticCorpus(self)
        with patch("builtins.open", side_effect=AssertionError("unauthorized open")):
            docs, failures = load_knowledge(str(corpus.index), str(corpus.root))
        self.assertEqual(docs, [])
        self.assertEqual(failures, [{"reason": "ACCESS_PROFILE_REQUIRED"}])

    def test_private_derived_unknown_and_denied_are_never_opened(self):
        corpus = SyntheticCorpus(self)
        for cls, permission in [("PRIVATE", "GENERAL_APPROVED"),
                                ("DERIVED_CASE", "GENERAL_APPROVED"),
                                ("UNKNOWN", "GENERAL_APPROVED"),
                                ("DECISION_SUPPORT", "WITHHELD")]:
            with self.subTest(cls=cls, permission=permission):
                corpus.docs.clear()
                corpus.profile["documents"].clear()
                corpus.add_doc("restricted", "PRIVATE_CANARY", doc_class=cls,
                                    permission=permission)
                opened = []
                real_open = builtins.open

                def observed_open(path, *args, **kwargs):
                    opened.append(Path(path).name)
                    if Path(path).name == "restricted.md":
                        raise AssertionError("private file opened")
                    return real_open(path, *args, **kwargs)

                with patch("builtins.open", observed_open):
                    docs, failures = self.load(corpus)
                self.assertEqual(docs, [])
                self.assertNotIn("restricted.md", opened)
                self.assertNotIn("PRIVATE_CANARY", str(failures))
                self.assertNotIn("restricted", str(failures))

    def test_public_bytes_need_exact_id_path_class_and_hash_permission(self):
        corpus = SyntheticCorpus(self)
        corpus.add_doc()
        docs, failures = self.load(corpus)
        self.assertEqual([d["doc_id"] for d in docs], ["public"])
        self.assertEqual(failures, [])
        profile = copy.deepcopy(corpus.profile)
        profile["documents"]["public"]["path"] = "elsewhere.md"
        with patch("builtins.open", wraps=builtins.open) as opened:
            docs, failures = self.load(corpus, profile)
        self.assertEqual(docs, [])
        self.assertFalse(any(str(c.args[0]).endswith("public.md") for c in opened.call_args_list))

    def test_symlink_and_traversal_are_denied_before_document_open(self):
        corpus = SyntheticCorpus(self)
        corpus.add_doc("hidden", "PRIVATE_CANARY", doc_class="PRIVATE")
        (corpus.root / "link.md").symlink_to(corpus.root / "hidden.md")
        for path in ["link.md", "../outside.md", str(corpus.root / "hidden.md")]:
            corpus.docs = [{"id": "allowed", "path": path, "class": "DECISION_SUPPORT",
                                 "sha256": "0" * 64}]
            corpus.profile["documents"] = {"allowed": {"path": path,
                "class": "DECISION_SUPPORT", "sha256": "0" * 64,
                "permission": "GENERAL_APPROVED"}}
            corpus.save_index()
            with patch("builtins.open", wraps=builtins.open) as opened:
                docs, failures = self.load(corpus)
            self.assertEqual(docs, [])
            self.assertEqual(len(opened.call_args_list), 1)
            self.assertNotIn("PRIVATE_CANARY", str(failures))

    def test_empty_and_wrong_domain_queries_never_open_unapproved_document(self):
        corpus = SyntheticCorpus(self)
        corpus.add_doc("hidden", "PRIVATE_CANARY bolig", doc_class="PRIVATE")
        for query, domain in [("og", "general"), ("bolig", "housing"),
                              ("PRIVATE_CANARY", "mental_health")]:
            with patch("builtins.open", wraps=builtins.open) as opened:
                result = retrieve(query, domain, **corpus.retrieval_args())
            self.assertFalse(any(str(c.args[0]).endswith("hidden.md") for c in opened.call_args_list))
            self.assertNotIn("PRIVATE_CANARY", str(result))
