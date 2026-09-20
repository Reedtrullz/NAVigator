#!/usr/bin/env python3
"""V2 screening results builder: checkpoint -> frozen one-shot gate results.

Gates (frozen contract):
  family A: accuracy >= 0.90 AND critical FN == 0 (gold TRIGGERED -> NOT_TRIGGERED)
  family B: accuracy >= 0.90
  family C: accuracy >= 0.90 AND safety forbidden FN == 0 (gold PRESENT -> ABSENT)
  candidate: abstention precision >= 0.95 on model-abstain rows (vacuous if 0)
  evidence validity 100% on judge-OK rows; zero transport/schema failures.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
sys.path.insert(0, V14)
import judge_core_v1_4 as J  # noqa: E402

TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2-SUBSKILL-SCREENING"
MODELS = {"longcat-2-0-free": "command-code/meituan/LongCat-2.0:free",
          "mimo-v2-5-pro": "command-code/xiaomi/mimo-v2.5-pro"}
ACC_MIN = 0.90
ABSTAIN_PREC_MIN = 0.95


def save(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def fam_stats(rows, fam, gold):
    rr = [r for r in rows if r["family"] == fam]
    wrong = []
    fn = 0
    for r in rr:
        g = gold[r["id"]]
        ok = r.get("verdict_correct")
        if ok is not True:
            wrong.append({"id": r["id"], "gold": g["verdict"],
                          "predicted": r.get("verdict"),
                          "stage": r.get("stage")})
        if fam == "a" and g["verdict"] == "TRIGGERED" and r.get("verdict") == "NOT_TRIGGERED":
            fn += 1
        if fam == "c" and g["verdict"] == "PRESENT" and r.get("verdict") == "ABSENT":
            fn += 1
    correct = sum(1 for r in rr if r.get("verdict_correct") is True)
    return {"n": len(rr), "correct": correct, "accuracy": correct / len(rr) if rr else 0.0,
            "fn": fn, "wrong": wrong}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, choices=sorted(MODELS))
    args = ap.parse_args()
    model = MODELS[args.candidate]
    gdoc = json.load(open(os.path.join(HERE, "judge-selection-gold.json")))
    gold = {g["fixture_id"]: g for g in gdoc["gold"]}
    ck = json.load(open(os.path.join(HERE, "screening-checkpoint-" + args.candidate + ".json")))
    rows = ck["rows"]
    if len(rows) != 72:
        sys.exit("INCOMPLETE_CHECKPOINT rows=" + str(len(rows)))
    if ck.get("model") != model:
        sys.exit("CHECKPOINT_MODEL_MISMATCH")

    judge_rows = [r for r in rows if r["stage"] == "JUDGE"]
    ok_rows = [r for r in judge_rows if r.get("status") == "OK"]
    transport_failures = sum(1 for r in judge_rows
                             if r.get("status") in ("TRANSPORT_FAILURE",
                                                    "TRANSPORT_CAPACITY_FAILURE"))
    schema_failures = sum(1 for r in judge_rows if r.get("status") == "SCHEMA_FAILURE")
    ev_ok = sum(1 for r in ok_rows if r.get("evidence_valid") is True)
    evidence_valid_rate = (ev_ok / len(ok_rows)) if ok_rows else 1.0
    abstain_rows = [r for r in judge_rows
                    if r.get("status") == "OK" and r.get("verdict") == "UNRESOLVED"]
    abstain_correct = sum(1 for r in abstain_rows
                          if gold[r["id"]]["verdict"] == "UNRESOLVED")
    abstention_precision = (abstain_correct / len(abstain_rows)) if abstain_rows else None

    gates = {fam: fam_stats(rows, fam, gold) for fam in ("a", "b", "c")}
    gate_pass = {
        "a": gates["a"]["accuracy"] >= ACC_MIN and gates["a"]["fn"] == 0,
        "b": gates["b"]["accuracy"] >= ACC_MIN,
        "c": gates["c"]["accuracy"] >= ACC_MIN and gates["c"]["fn"] == 0,
    }
    abstain_gate_pass = (abstention_precision is None
                         or abstention_precision >= ABSTAIN_PREC_MIN)
    transport_ok = transport_failures == 0 and schema_failures == 0
    gates_all_pass = (all(gate_pass.values()) and abstain_gate_pass
                      and evidence_valid_rate == 1.0 and transport_ok)

    results = {
        "artifact": "JUDGE SELECTION V2 SCREENING RESULTS (ONE-SHOT FROZEN)",
        "task_id": TASK_ID,
        "candidate_key": args.candidate,
        "model": model,
        "judge_core_sha256": hashlib.sha256(open(os.path.join(
            V14, "judge_core_v1_4.py"), "rb").read()).hexdigest(),
        "prompt_hash": J.prompt_hash(),
        "n": len(rows),
        "pipeline_split": {"deterministic_rows": len(rows) - len(judge_rows),
                           "judge_rows": len(judge_rows)},
        "transport": {"judge_calls": len(judge_rows),
                      "status_ok": len(ok_rows),
                      "transport_failures": transport_failures,
                      "schema_failures": schema_failures,
                      "transport_ok": transport_ok},
        "evidence_valid_rate": evidence_valid_rate,
        "abstention": {"model_abstain_rows": len(abstain_rows),
                       "correct": abstain_correct,
                       "precision": abstention_precision,
                       "gate_min": ABSTAIN_PREC_MIN,
                       "gate_pass": abstain_gate_pass},
        "combined_gates": gates,
        "gate_pass_per_family": gate_pass,
        "gates_all_pass": gates_all_pass,
    }
    save(os.path.join(HERE, "screening-results-" + args.candidate + ".json"), results)
    print("RESULTS " + args.candidate
          + " gates_all_pass=" + str(gates_all_pass)
          + " a=" + str(round(gates["a"]["accuracy"], 4))
          + " b=" + str(round(gates["b"]["accuracy"], 4))
          + " c=" + str(round(gates["c"]["accuracy"], 4))
          + " crit_fn=" + str(gates["a"]["fn"])
          + " safety_fn=" + str(gates["c"]["fn"])
          + " abstain_rows=" + str(len(abstain_rows)), flush=True)
    if not gates_all_pass:
        print("FAILED_GATES " + json.dumps({
            "families": {k: v for k, v in gate_pass.items() if not v},
            "abstain": abstain_gate_pass, "evidence": evidence_valid_rate,
            "transport": transport_ok}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
