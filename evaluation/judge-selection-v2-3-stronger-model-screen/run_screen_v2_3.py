#!/usr/bin/env python3
"""V2.3 stronger-model screening: burned V2.2 120-row one-shot, per candidate.

Frozen V2.2 scoring verbatim (imported, not copied). Only the model
identifier and provider label differ per candidate. Checkpoint written
after every row; 429/5xx retried once per judge_core_v2_2 policy.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
V22 = HERE.parent / "judge-contract-v2-2-two-mechanism"
sys.path.insert(0, str(V22))

import judge_core_v2_2 as J  # noqa: E402
from run_official_v2_2 import score  # noqa: E402  frozen scoring verbatim

EXPECTED_PROMPT_SHA = "9a20e9b241b9084be6299fd3ba778c63e41d1a8b35067840675ee443f4f335e5"
FIXTURES_SHA = "23cd24e1d578ed7cd6dbb0b626bcc1a56c740d5f0506d5861590eb7cb60b1f4b"
CORE_SHA = "5d5bbf9db626e43b4a4195e7549b1adcf050bf1aeba1a8bdb6e4d50fab80e0af"

CANDIDATES = {
    "mimo-v2-5": "command-code/xiaomi/mimo-v2.5",
    "ling-3-0-flash-sante-free": "command-code/inclusionai/ling-3.0-flash-sante:free",
    "poolside-laguna-s-2-1-free": "command-code/poolside/laguna-s-2.1-free",
    "deepseek-v4-1-flash": "opencode-go/deepseek-v4.1-flash",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + chr(10),
                          encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, choices=sorted(CANDIDATES))
    args = ap.parse_args()
    model = CANDIDATES[args.candidate]

    assert sha(V22 / "official-validation-fixtures.json") == FIXTURES_SHA
    assert sha(V22 / "judge_core_v2_2.py") == CORE_SHA
    assert J.prompt_hash() == EXPECTED_PROMPT_SHA, "prompt drift"

    fixtures = json.loads((V22 / "official-validation-fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    assert len(fixtures) == 120

    J.MODEL = model
    J.PROVIDER = "commandcode-auth local proxy (V2.3 screen)" if not model.startswith("opencode") else "opencode-go via commandcode local proxy (V2.3 screen)"

    ckpt = HERE / ("checkpoint-screen-" + args.candidate + ".json")
    runs = []
    if ckpt.exists():
        ck = json.loads(ckpt.read_text(encoding="utf-8"))
        if ck.get("model") != model:
            raise SystemExit("checkpoint/model mismatch")
        runs = ck["runs"]
        print("RESUME %s: %d rows loaded" % (args.candidate, len(runs)), flush=True)

    partial = HERE / ("screen-" + args.candidate + ".partial.json")
    done_ids = {r["id"] for r in runs}
    for i, fx in enumerate(fixtures, 1):
        if fx["id"] in done_ids:
            continue
        result, telemetry = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
        entry = {"id": fx["id"], "family": fx["family"], "tag": fx["tag"],
                 "gold_intermediate": fx["gold_intermediate"], "gold_verdict": fx["gold_verdict"],
                 "telemetry": telemetry}
        if result is not None:
            entry.update({"valid_result": True, "intermediate": result["intermediate"],
                          "verdict": result["verdict"], "derivation_basis": result["derivation_basis"],
                          "evidence_spans": result["evidence_spans"], "note": result["note"],
                          "verdict_correct": result["verdict"] == fx["gold_verdict"]})
        else:
            entry.update({"valid_result": False, "verdict_correct": False})
        runs.append(entry)
        ckpt.write_text(json.dumps({"candidate": args.candidate, "model": model, "runs": runs},
                                   ensure_ascii=False) + chr(10), encoding="utf-8")
        partial.write_text(json.dumps({"runs": runs}, ensure_ascii=False) + chr(10), encoding="utf-8")
        print("%d/120 %s ok=%s correct=%s" % (i, entry["id"], entry["valid_result"],
                                              entry.get("verdict_correct")), flush=True)

    summary = score(runs, fixtures)
    out = {"artifact": "screen-" + args.candidate + ".json",
           "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN",
           "run_type": "ONE_SHOT_SCREEN_BURNED_V2_2_120ROW",
           "candidate": args.candidate, "model": model,
           "prompt_sha": J.prompt_hash(), "fixture_count": len(fixtures),
           "runs_completed": len(runs),
           "transport_failures": sum(1 for r in runs if not r.get("valid_result")),
           "summary": summary, "runs": runs}
    save(HERE / ("screen-" + args.candidate + ".json"), out)
    print(json.dumps({k: summary[k] for k in ("overall", "by_family",
                                              "valid_structured_rate",
                                              "derivation_consistency")}, indent=2),
          flush=True)


if __name__ == "__main__":
    main()
