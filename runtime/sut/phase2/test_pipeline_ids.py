"""RC-08 residual: evidence ids must be unique across combined tracks."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase2.pipeline import _default_config, s4_knowledge_retrieval


class CombinedTrackIdTests(unittest.TestCase):
    def test_ids_unique_across_tracks(self):
        ctx = {
            "tracks": [
                {"track_id": "T1", "domain": "mental_health"},
                {"track_id": "T2", "domain": "education"},
            ],
            "_config": _default_config(),
            "input": {"user_query": "skolevegring PPT fastlege BUP"},
            "failures": [],
        }
        s4_knowledge_retrieval(ctx)
        recs = ctx["_s4_records"]
        self.assertEqual(len(recs), 10)
        eids = [r["evidence_id"] for r in recs]
        rids = [r["record_id"] for r in recs]
        self.assertEqual(len(set(eids)), len(eids))
        self.assertEqual(len(set(rids)), len(rids))


if __name__ == "__main__":
    unittest.main()
