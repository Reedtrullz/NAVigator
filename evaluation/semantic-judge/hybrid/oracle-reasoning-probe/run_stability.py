"""Spec 23 stability: hardest probe claims x 3 (max 20 claims x 3).
Hardest = cases where the main probe run produced a non-expected verdict
or failed validation, ranked by ledger difficulty (B first, then A/F).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.dirname(HERE), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from run_proof_probe import call_luna_proof  # noqa: E402
from validate_proof import validate_proof  # noqa: E402


def main():
    ledger = {c["case_id"]: c for c in json.load(
        open(os.path.join(HERE, "oracle-proof-ledger.json")))["cases"]}
    packets = {r["id"]: r for r in json.load(
        open(os.path.join(HERE, "oracle-packets.json"), encoding="utf-8"))}
    probe = json.load(open(os.path.join(HERE, "structured-proof-results.json")))["results"]
    hard = [r["case_id"] for r in probe
            if not r["accepted"] or r["final_verdict"] != r["expected"]]
    hard = [cid for cid in dict.fromkeys(hard)][:5]
    out = []
    for cid in hard:
        packet = packets[cid]["packet"]
        runs = []
        for i in range(3):
            raw = call_luna_proof(packet)
            v = validate_proof(raw or {}, packet)
            runs.append({"run": i + 1, "model_output": raw, "validation": v,
                         "final_verdict": (raw or {}).get("verdict") if v["valid"] else "REVIEW_REQUIRED"})
        ops = {(r["model_output"] or {}).get("inference_operator") for r in runs}
        premises = {tuple(r["model_output"].get("premises_used") or []) if r["model_output"] else () for r in runs}
        verdicts = {r["final_verdict"] for r in runs}
        out.append({"case_id": cid, "runs": runs,
                    "operator_consistent": len(ops) == 1,
                    "premise_consistent": len(premises) == 1,
                    "verdict_consistent": len(verdicts) == 1})
        print(cid, "ops:", ops, "verdicts:", verdicts, flush=True)
    with open(os.path.join(HERE, "stability-results.json"), "w") as f:
        json.dump({"schema": "stability-v1", "n_claims": len(hard), "reps": 3,
                   "results": out}, f, ensure_ascii=False, indent=1)
    print("wrote stability-results.json")


if __name__ == "__main__":
    main()
