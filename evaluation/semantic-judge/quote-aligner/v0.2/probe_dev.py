#!/usr/bin/env python3
"""Dev harness: replays the qa05 misses through an engine module.
Read-only on frozen v0.1 results and v0.4.1 benchmarks.
Usage: python3 probe_dev.py [engine_module]"""
import json
import os
import sys
from importlib import import_module

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
QA05 = os.path.join(os.path.dirname(HERE), "results")
BENCH = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                     "v0.4.1", "benchmarks")
FILES = ["minimal-pairs", "minimal-pairs-supplement", "contra-insuff",
         "modality", "actor-scope", "locality", "diagnostic-20"]


def load_misses():
    texts = {}
    for name in FILES:
        with open(os.path.join(BENCH, name + ".json"), encoding="utf-8") as f:
            for c in json.load(f)["claims"]:
                texts[(name, c["id"])] = c
    misses = []
    for name in FILES:
        with open(os.path.join(QA05, "qa05-results-%s.json" % name),
                  encoding="utf-8") as f:
            for r in json.load(f)["results"]:
                if r.get("status") == "ok" and r["verdict"] != r["expected"]:
                    c = texts[(name, r["id"])]
                    misses.append({"id": r["id"], "expected": r["expected"],
                                   "v01": r["verdict"], "claim": c["claim"],
                                   "source": c["source"]["text"]})
    return misses


def main():
    engine = import_module(sys.argv[1] if len(sys.argv) > 1
                           else "polarity_engine_v02")
    misses = load_misses()
    fixed, still = [], []
    for m in misses:
        got = engine.judge_claim(m["claim"], m["source"])["verdict"]
        if got == m["expected"]:
            fixed.append(m["id"])
        else:
            still.append((m["id"], m["expected"], m["v01"], got))
    print("%d/%d misses fixed" % (len(fixed), len(misses)))
    print("fixed:", " ".join(fixed))
    print("still missing:")
    for i, e, v01, g in still:
        print("  %-8s exp=%-22s v01=%-22s v02=%s" % (i, e, v01, g))


if __name__ == "__main__":
    main()
