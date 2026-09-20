#!/usr/bin/env python3
"""Score frozen V3 B.AI screening outputs with the exact V1 scorer semantics."""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v2")
sys.path.insert(0, V2)

ss = importlib.import_module("score_screening_v2")
ss.SCREEN = json.load(open(os.path.join(HERE, "semantic-screen-results.json"),
                           encoding="utf-8"))["candidates"]

if __name__ == "__main__":
    out = {"scoring_rule": "frozen V1 contract gates; reference = frozen authoritative semantic reference, not human ground truth; schema_valid_rate counts parseable rows (V1 semantics)",
           "candidates": {}}
    for cand_id in ss.SCREEN:
        out["candidates"][cand_id] = {
            lane: ss.score_candidate(cand_id, lane)
            for lane in ("forbidden_claim", "critical_condition")
        }
    with open(os.path.join(HERE, "screening-scored-v3.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({cid: {l: {k: v for k, v in s.items()
                                if not k.endswith("hashes")}
                            for l, s in lanes.items()}
                      for cid, lanes in out["candidates"].items()},
                     ensure_ascii=False, indent=1))

