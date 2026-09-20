#!/usr/bin/env python3
"""Stabilitetstest: 22 fixtures x 5 kjoeringer, modal agreement paa primitives."""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantic_judge as sj

RUNS = 5
MIN_FIXTURES = 20


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "judge-validation-fixtures.json"), encoding="utf-8") as f:
        fixtures = json.load(f)["fixtures"]

    # Deterministic sample: first 6 per dimension (22-24 fixtures), stability-relevant mix
    by_dim = {}
    for fx in fixtures:
        by_dim.setdefault(fx["dimension"], []).append(fx)
    sample = []
    for d, fxs in sorted(by_dim.items()):
        sample.extend(fxs[:6])

    rows = []
    for i, fx in enumerate(sample):
        verdicts = []
        for run in range(RUNS):
            res = sj.semantic_verdict(
                fx["dimension"], fx["case_context"], fx["gold_criterion"], fx["sut_answer"])
            verdicts.append(res["verdict"])
        counts = Counter(verdicts)
        modal, modal_n = counts.most_common(1)[0]
        agree = modal_n / RUNS
        rows.append({
            "id": fx["id"], "dimension": fx["dimension"],
            "verdicts": verdicts, "modal": modal,
            "modal_agreement": agree,
        })
        print(f"{i+1}/{len(sample)} {fx['id']}: modal {modal} ({modal_n}/{RUNS}) {dict(counts)}", flush=True)

    stable = sum(1 for r in rows if r["modal_agreement"] >= 0.95)
    result = {
        "runs_per_fixture": RUNS,
        "fixtures": len(rows),
        "stable_fixtures": stable,
        "stability_rate": round(stable / len(rows), 4),
        "rows": rows,
    }
    with open(os.path.join(here, "stability-results.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"stability: {stable}/{len(rows)} fixtures with modal agreement >= 95%")


if __name__ == "__main__":
    main()
