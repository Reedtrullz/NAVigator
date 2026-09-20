"""RC-08 planner INFO-block domain scoping tests."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sut.phase3.planner import plan  # noqa: E402
from sut.context import make_context  # noqa: E402


def rec(eid, domain):
    return {
        "record_id": eid.replace("E-", "K-"),
        "source_type": "PROJECT_RESEARCH",
        "domain": domain,
        "domains": [domain],
        "claim": "x",
        "evidence_id": eid,
        "gap_state": None,
        "historical_research": False,
        "provenance": {},
        "source_reference": {"kind": "REPO_DOC", "path": "x.md"},
        "authority": "INTERNAL_DOC",
        "freshness": "CURRENT",
    }


class PlannerScopingTests(unittest.TestCase):
    def _ctx(self, tracks):
        ctx = make_context({
            "case_id": "UT",
            "user_query": "q",
            "profile": {"age": 19},
            "context": {},
            "location_context": {"municipality": "Drammen"},
            "timestamp_context": {"executed_at": "2026-09-16T10:00:00Z"},
        })
        ctx["safety"] = {"priority": "NOT_ACUTE", "signals": [],
                         "suppressed_routing": False}
        ctx["tracks"] = tracks
        ctx["_s6_routes"] = []
        ctx["_s7_claims"] = []
        ctx["_s7_conflicts"] = []
        ctx["_s5_steps"] = []
        ctx["_s5_incomplete"] = False
        ctx["epistemic_states"] = {"top_level": "UNVERIFIED",
                                   "per_track": {}, "per_route": []}
        return ctx

    def test_info_blocks_scoped_to_track_domain(self):
        ctx = self._ctx([{"track_id": "T1", "domain": "mental_health",
                          "status": "PENDING"}])
        ctx["_s4_records"] = [rec("E-D001", "mental_health"),
                              rec("E-D002", "housing"),
                              rec("E-D003", "education")]
        p = plan(ctx)
        info_eids = [ref for b in p["blocks"] if b["kind"] == "INFO"
                     for ref in b["span_refs"]]
        self.assertEqual(info_eids, ["E-D001"])

    def test_multi_domain_record_reachable_from_second_track(self):
        ctx = self._ctx([
            {"track_id": "T1", "domain": "mental_health", "status": "PENDING"},
            {"track_id": "T2", "domain": "education", "status": "PENDING"},
        ])
        multi = rec("E-D001", "education")
        multi["domains"] = ["mental_health", "education"]
        ctx["_s4_records"] = [multi]
        p = plan(ctx)
        info_eids = [ref for b in p["blocks"] if b["kind"] == "INFO"
                     for ref in b["span_refs"]]
        self.assertEqual(info_eids, ["E-D001"])


if __name__ == "__main__":
    unittest.main()
