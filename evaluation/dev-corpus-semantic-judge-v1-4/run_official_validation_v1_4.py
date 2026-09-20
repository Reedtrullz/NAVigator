#!/usr/bin/env python3
"""V1.4 official one-shot mimo validation (spec 43-45)."""
import hashlib
import json
import os
import sys
import time

import judge_core_v1_4 as J

HERE = os.path.dirname(os.path.abspath(__file__))


def matches(result, gold):
    return result.get("verdict") == gold.get("verdict")


def main():
    fxdoc = json.load(open(os.path.join(HERE, "official-validation-fixtures.json")))
    fixtures = fxdoc["fixtures"]
    gold_doc = json.load(open(os.path.join(HERE, "official-validation-gold.json")))
    gold = gold_doc["gold"]
    fixtures_sha = hashlib.sha256(
        open(os.path.join(HERE, "official-validation-fixtures.json"), "rb").read()).hexdigest()
    gold_sha = hashlib.sha256(
        open(os.path.join(HERE, "official-validation-gold.json"), "rb").read()).hexdigest()
    assert fixtures_sha == gold_doc["basis"]["fixtures_sha256"], "fixture hash drift vs gold basis"
    assert gold_doc["status"] == "FROZEN"

    rows = []
    for i, fx in enumerate(fixtures):
        if i:
            time.sleep(2.0)
        g = gold[fx["id"]]
        t = J.call_judge(fx["dimension"], fx["case_context"],
                         fx["gold_criterion"], fx["sut_answer"])
        row = {"id": fx["id"], "dimension": fx["dimension"],
               "status": t.get("status"), "telemetry": {
                   k: t.get(k) for k in
                   ("finish_reason", "usage", "latency_seconds", "retries", "error")}}
        if t.get("status") == "OK":
            row["result"] = t["result"]
            row["gold"] = g
            row["verdict_correct"] = matches(t["result"], g)
            row["payload_exact_match"] = all(
                t["result"].get(k) == g.get(k) for k in g)
            evidence_ok = True
            for s in t["result"].get("evidence_spans", []):
                if J.norm(s) not in J.norm(fx["sut_answer"]):
                    evidence_ok = False
                    break
            row["evidence_valid"] = evidence_ok
        rows.append(row)
        tag = row.get("verdict_correct") if row["status"] == "OK" else row["status"]
        print(f"{i + 1}/{len(fixtures)} {fx['id']}: {tag}", flush=True)

    ok_rows = [r for r in rows if r.get("status") == "OK"]
    dims = ("critical_condition", "forbidden_claim", "route_correctness",
            "required_uncertainty")
    per_dim = {}
    for dim in dims:
        sub = [r for r in ok_rows if r["dimension"] == dim]
        per_dim[dim] = {
            "n": len(sub),
            "verdict_correct": sum(1 for r in sub if r["verdict_correct"]),
            "accuracy": round(sum(1 for r in sub if r["verdict_correct"]) / len(sub), 4)
            if sub else None,
            "payload_exact": sum(1 for r in sub if r["payload_exact_match"]),
        }
    critical_fn = sum(1 for r in ok_rows
                      if r["dimension"] == "critical_condition"
                      and r["gold"]["verdict"] == "TRIGGERED"
                      and r["result"]["verdict"] != "TRIGGERED")
    safety_fn = sum(1 for r in ok_rows
                    if r["dimension"] == "forbidden_claim"
                    and r["gold"]["verdict"] == "PRESENT"
                    and r["result"]["verdict"] != "PRESENT")
    false_acceptable = sum(1 for r in ok_rows
                           if r["dimension"] == "route_correctness"
                           and r["gold"]["verdict"] == "NO_ACCEPTABLE_ROUTE"
                           and r["result"]["verdict"] == "ACCEPTABLE")
    usage = [r["telemetry"]["usage"] for r in ok_rows if r["telemetry"].get("usage")]
    completion = [u.get("completion_tokens") for u in usage
                  if isinstance(u.get("completion_tokens"), int)]
    completion.sort()

    def p95(vals):
        if not vals:
            return None
        k = max(0, min(len(vals) - 1, int(round(0.95 * (len(vals) - 1)))))
        return vals[k]

    summary = {
        "artifact": "V1.4 OFFICIAL ONE-SHOT MIMO VALIDATION",
        "run_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_inputs": {
            "fixtures_sha256": fixtures_sha,
            "gold_sha256": gold_sha,
            "model_config_sha256": hashlib.sha256(
                open(os.path.join(HERE, "model-config-v1-4.json"), "rb").read()).hexdigest(),
            "judge_core_sha256": hashlib.sha256(
                open(os.path.join(HERE, "judge_core_v1_4.py"), "rb").read()).hexdigest(),
            "model": J.MODEL, "provider": J.PROVIDER,
            "temperature": J.TEMPERATURE, "max_tokens": J.MAX_TOKENS,
            "one_shot": True, "substantive_reruns": 0,
        },
        "n": len(rows),
        "status_ok": len(ok_rows),
        "transport_failures": sum(1 for r in rows if r.get("status") == "TRANSPORT_FAILURE"),
        "transport_capacity_failures": sum(
            1 for r in rows if r.get("status") == "TRANSPORT_CAPACITY_FAILURE"),
        "schema_failures": sum(1 for r in rows if r.get("status") == "SCHEMA_FAILURE"),
        "valid_semantic_result_rate": round(len(ok_rows) / len(rows), 4),
        "evidence_span_validity": {
            "checked": len(ok_rows),
            "invalid": sum(1 for r in ok_rows if not r["evidence_valid"]),
        },
        "deterministic_overrides": 0,
        "per_dimension": per_dim,
        "hard_zero": {
            "critical_fn": critical_fn,
            "safety_forbidden_fn": safety_fn,
            "false_acceptable_route": false_acceptable,
        },
        "token_usage": {
            "n_with_usage": len(usage),
            "completion_median": completion[len(completion) // 2] if completion else None,
            "completion_p95": p95(completion),
            "completion_max": completion[-1] if completion else None,
            "max_budget_fraction_used": round(
                (completion[-1] / J.MAX_TOKENS), 4) if completion else None,
            "finish_reason_length_count": sum(
                1 for r in rows if r["telemetry"].get("finish_reason") == "length"),
        },
        "rows": rows,
    }
    overall = round(sum(1 for r in ok_rows if r["verdict_correct"]) / len(ok_rows), 4) if ok_rows else None
    summary["overall_verdict_accuracy"] = overall
    path = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "official-validation-results.json")
    with open(path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in
                      ("n", "status_ok", "transport_failures",
                       "transport_capacity_failures", "schema_failures",
                       "valid_semantic_result_rate", "overall_verdict_accuracy",
                       "per_dimension", "hard_zero", "token_usage")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
