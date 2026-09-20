#!/usr/bin/env python3
"""DeepSeek-only V3 screening process (separate OUT to allow parallel run)."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v2")
sys.path.insert(0, V2)

rs = importlib.import_module("run_screening_v2")
rs.OUT = os.path.join(HERE, "semantic-screen-results-BAI-DEEPSEEK.json")
rs.CANDIDATES = [
    {"logical_id": "BAI-DEEPSEEK",
     "wire_id": "B.AI/deepseek-v4-flash-vision-exp"},
]
rs.HERE = HERE

if __name__ == "__main__":
    rs.main()

