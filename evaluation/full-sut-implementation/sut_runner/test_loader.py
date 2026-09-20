import json
import unittest
import hashlib
import os
import tempfile

from sut_runner.loader import (
    GOLD_FIELDS,
    GoldLeakError,
    iter_inputs,
    load_corpus,
    strip_gold,
)


CORPUS_DIR = "evaluation/dev-corpus-v1"
ROUTING_FILE = CORPUS_DIR + "/cases/routing_cases.json"


def _registry(path):
    manifest = json.load(open(CORPUS_DIR + "/manifest.json", encoding="utf-8"))
    return manifest["files"]


class TestLoadCorpus(unittest.TestCase):
    def test_load_routing_corpus(self):
        cf = load_corpus(ROUTING_FILE, sha_registry=_registry(ROUTING_FILE))
        self.assertEqual(cf["corpus"], "dev-corpus-v1")
        self.assertEqual(cf["family"], "routing_cases")
        self.assertEqual(cf["case_count"], 75)
        self.assertEqual(len(cf["cases"]), 75)

    def test_sha_mismatch_raises(self):
        bad = {"cases/routing_cases.json": "0" * 64}
        with self.assertRaises(GoldLeakError):
            load_corpus(ROUTING_FILE, sha_registry=bad)

    def test_count_mismatch_raises(self):
        broken = {
            "corpus": "dev-corpus-v1",
            "family": "broken",
            "case_count": 99,
            "cases": [{"id": "X-1", "utterance": "q", "profile": {}}],
        }
        raw = json.dumps(broken).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "broken_cases.json")
            with open(path, "wb") as f:
                f.write(raw)
            registry = {
                "cases/broken_cases.json": hashlib.sha256(raw).hexdigest()
            }
            with self.assertRaises(GoldLeakError):
                load_corpus(path, sha_registry=registry)


class TestStripGold(unittest.TestCase):
    def setUp(self):
        cf = load_corpus(ROUTING_FILE, sha_registry=_registry(ROUTING_FILE))
        self.case = cf["cases"][0]

    def test_gold_fields_removed(self):
        inp = strip_gold(self.case, executed_at="2026-09-14T08:00:00Z")
        self.assertEqual(
            sorted(inp.keys()),
            [
                "case_id",
                "context",
                "location_context",
                "profile",
                "timestamp_context",
                "user_query",
            ],
        )
        serialized = json.dumps(inp)
        for field in GOLD_FIELDS:
            self.assertNotIn('"%s"' % field, serialized)
        self.assertNotIn('"gold"', serialized)

    def test_canonical_shape(self):
        inp = strip_gold(self.case, executed_at="2026-09-14T08:00:00Z")
        self.assertEqual(inp["case_id"], self.case["id"])
        self.assertEqual(inp["user_query"], self.case["utterance"])
        self.assertEqual(inp["profile"], self.case["profile"])
        self.assertEqual(inp["context"], {})
        self.assertEqual(inp["location_context"], {})
        self.assertEqual(inp["timestamp_context"]["executed_at"], "2026-09-14T08:00:00Z")

    def test_planted_nested_gold_raises(self):
        planted = json.loads(json.dumps(self.case))
        planted["profile"]["gold"] = {"safety_priority": "NOT_ACUTE"}
        with self.assertRaises(GoldLeakError):
            strip_gold(planted, executed_at="2026-09-14T08:00:00Z")

    def test_planted_hidden_field_raises(self):
        planted = json.loads(json.dumps(self.case))
        planted["utterance"] = self.case["utterance"]
        planted["id"] = self.case["id"]
        planted["profile"] = json.loads(json.dumps(self.case["profile"]))
        planted["profile"]["acceptable_routes"] = ["fastlege"]
        with self.assertRaises(GoldLeakError):
            strip_gold(planted, executed_at="2026-09-14T08:00:00Z")

    def test_iter_inputs_order(self):
        cf = load_corpus(ROUTING_FILE, sha_registry=_registry(ROUTING_FILE))
        inputs = list(iter_inputs(cf, executed_at="2026-09-14T08:00:00Z"))
        self.assertEqual(len(inputs), 75)
        self.assertEqual(inputs[0]["case_id"], cf["cases"][0]["id"])


if __name__ == "__main__":
    unittest.main()
