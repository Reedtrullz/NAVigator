#!/usr/bin/env python3
"""Offline test of deterministic aggregation over compound-set.json (no LLM calls)."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import semantic_judge as sj

def main():
    with open(os.path.join(HERE, "compound-set.json"), encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    failures = []
    for c in cases:
        atom_results = [{"atom_id": a["id"], "verdict": a["verdict"],
                         "near_miss": a.get("near_miss", False),
                         "confidence": a.get("confidence", 0.95)} for a in c["atoms"]]
        got = sj.aggregate({"type": c.get("claim_type", "compound"),
                            "atoms": [{**a, "text": ""} for a in c["atoms"]]},
                           atom_results, c.get("flags"))
        checks = [
            ("verdict", got["verdict"], c["expected_verdict"]),
            ("review_flag", got["review_flag"], c["expected_review_flag"]),
            ("safety_block", got["safety_block"], c["expected_safety_block"]),
        ]
        bad = [(k, g, e) for k, g, e in checks if e is not None and g != e]
        if bad:
            failures.append({"id": c["id"], "desc": c.get("description"), "mismatches": bad})
    print(f"COMPOUND AGGREGATION: {len(cases) - len(failures)}/{len(cases)} pass")
    for f_ in failures:
        print(json.dumps(f_, ensure_ascii=False))
    out = {"n": len(cases), "failures": failures,
           "pass": len(cases) - len(failures)}
    with open(os.path.join(HERE, "results", "compound-run.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    sys.exit(0 if not failures else 1)

if __name__ == "__main__":
    main()
