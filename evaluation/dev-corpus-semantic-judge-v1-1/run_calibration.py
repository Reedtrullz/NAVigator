#!/usr/bin/env python3
"""Kalibrering av V1.1-dommer paa frosset 20-fixture kalibreringssett.

Kjorer hver fixture 3 ganger med dags konfig og sammenligner med
designer_intent. Dette er BURNED prompt-utviklingsdata: brukes aldri som
validering. Ingen prompt-endring etter at kontrakten fryses.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v1_1_judge as sj  # noqa: E402

RUNS = 3


def main():
    with open(os.path.join(HERE, "calibration-fixtures-v1-1.json"), encoding="utf-8") as f:
        fixtures = json.load(f)["fixtures"]
    rows = []
    for i, fx in enumerate(fixtures):
        verdicts = []
        for _ in range(RUNS):
            res = sj.semantic_verdict(
                fx["dimension"], fx["case_context"], fx["gold_criterion"], fx["sut_answer"])
            verdicts.append(res["verdict"])
        counts = Counter(verdicts)
        modal, modal_n = counts.most_common(1)[0]
        rows.append({
            "id": fx["id"], "dimension": fx["dimension"],
            "designer_intent": fx["designer_intent"],
            "verdicts": verdicts, "modal": modal,
            "modal_agreement": modal_n / RUNS,
            "modal_correct": modal == fx["designer_intent"],
        })
        print(f"{i+1}/{len(fixtures)} {fx['id']}: modal {modal} vs intent "
              f"{fx['designer_intent']} ({dict(counts)})", flush=True)
    n_modal = sum(r["modal_correct"] for r in rows)
    stable = sum(1 for r in rows if r["modal_agreement"] >= 0.95)
    out = {
        "status": "CALIBRATION_BURNED_NOT_VALIDATION",
        "runs_per_fixture": RUNS,
        "fixtures": len(rows),
        "modal_match_designer_intent": n_modal,
        "modal_match_rate": round(n_modal / len(rows), 4),
        "stable_fixtures": stable,
        "stability_rate": round(stable / len(rows), 4),
        "prompt_sha256_at_run": sj.prompt_hash(),
        "rows": rows,
    }
    with open(os.path.join(HERE, "calibration-results-v1-1.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"modal match: {n_modal}/{len(rows)} | stable: {stable}/{len(rows)}")


if __name__ == "__main__":
    main()
