#!/usr/bin/env python3
"""V2.3 stability stage (only for one-shot qualifiers): 24 fixtures x 5 runs.

Subset: first 8 fixtures per family in frozen file order (V2.1 precedent,
24 total). Frozen section-6 semantics:
  - modal verdict per fixture must agree with the one-shot result on
    >= 0.95 of fixtures overall;
  - per intermediate field (criterion_semantic_match, speaker_commitment,
    critical_evidence_state), modal stability across the 5 runs must be
    >= 0.95 (mean over fixtures of modal-count/run-count).
No majority-vote repair; stability is a gate, not a score source.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
V22 = HERE.parent / "judge-contract-v2-2-two-mechanism"
sys.path.insert(0, str(V22))

import judge_core_v2_2 as J  # noqa: E402

RUNS = 5
PER_FAMILY = 8
MIN = 0.95
FIELDS = ("criterion_semantic_match", "speaker_commitment", "critical_evidence_state")


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + chr(10),
                          encoding="utf-8")


def modal_rate(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return 0.0, None
    c = Counter(vals).most_common(1)[0]
    return c[1] / len(values), c[0]


def main(candidate):
    model = json.loads((HERE / ("screen-" + candidate + ".json")).read_text(encoding="utf-8"))["model"]
    gates = json.loads((HERE / ("gate-extraction-" + candidate + ".json")).read_text(encoding="utf-8"))
    if not gates["gates"]["all_pass"]:
        raise SystemExit("STABILITY_NOT_ELIGIBLE: one-shot gates not passed")

    fixtures = json.loads((V22 / "official-validation-fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    subset = []
    for fam in ("m1", "m2", "control"):
        subset.extend([f for f in fixtures if f["family"] == fam][:PER_FAMILY])
    assert len(subset) == 24

    one_shot = {r["id"]: r for r in json.loads(
        (HERE / ("screen-" + candidate + ".json")).read_text(encoding="utf-8"))["runs"]}

    J.MODEL = model
    ckpt = HERE / ("checkpoint-stability-" + candidate + ".json")
    per_fixture = {}
    if ckpt.exists():
        per_fixture = json.loads(ckpt.read_text(encoding="utf-8"))["per_fixture"]

    for fx in subset:
        if fx["id"] in per_fixture and len(per_fixture[fx["id"]]["runs"]) == RUNS:
            continue
        runs = per_fixture.get(fx["id"], {}).get("runs", [])
        for k in range(len(runs), RUNS):
            result, telemetry = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
            runs.append({"run": k + 1,
                         "valid_result": result is not None,
                         "verdict": result["verdict"] if result else None,
                         "intermediate": result["intermediate"] if result else None,
                         "error": telemetry.get("error") if result is None else None})
            per_fixture[fx["id"]] = {"runs": runs}
            ckpt.write_text(json.dumps({"candidate": candidate, "model": model,
                                        "per_fixture": per_fixture}, ensure_ascii=False) + chr(10),
                            encoding="utf-8")
            print(fx["id"] + " run " + str(k + 1) + "/" + str(RUNS)
                  + " verdict=" + str((result or {}).get("verdict")), flush=True)

    agreement = []
    field_rates = {f: [] for f in FIELDS}
    for fx in subset:
        rs = per_fixture[fx["id"]]["runs"]
        verdicts = [r["verdict"] for r in rs]
        modal, _ = modal_rate(verdicts)
        ok = modal == 1.0 and verdicts[0] is not None and verdicts[0] == one_shot[fx["id"]].get("verdict")
        agreement.append(ok)
        for f in FIELDS:
            vals = [r["intermediate"].get(f) for r in rs
                    if r["valid_result"] and f in (r["intermediate"] or {})]
            if not vals:
                continue
            rate, _ = modal_rate([r["intermediate"][f] for r in rs if r["valid_result"]])
            field_rates[f].append(rate)

    out = {"artifact": "stability-" + candidate + ".json",
           "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN",
           "candidate": candidate, "model": model,
           "runs_per_fixture": RUNS, "fixtures": len(subset),
           "one_shot_agreement": {"n": len(agreement), "agree": sum(agreement),
                                  "rate": round(sum(agreement) / len(agreement), 4), "min": MIN},
           "intermediate_field_modal_stability": {
               f: {"mean_modal_rate": round(sum(v) / len(v), 4), "min": MIN}
               for f, v in field_rates.items() if v},
           "per_fixture": {k: {"verdicts": [r["verdict"] for r in v["runs"]]}
                           for k, v in per_fixture.items()}}
    stability_pass = (out["one_shot_agreement"]["rate"] >= MIN
                      and all(d["mean_modal_rate"] >= MIN
                              for d in out["intermediate_field_modal_stability"].values()))
    out["stability_pass"] = stability_pass
    save(HERE / ("stability-" + candidate + ".json"), out)
    print("STABILITY " + candidate + " agreement=" + str(out["one_shot_agreement"]["rate"])
          + " pass=" + str(stability_pass), flush=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
