#!/usr/bin/env python3
"""V1.5A burned model-selection runner.

Transport adapter only (spec 13): imports the frozen V1.4 judge core
verbatim and swaps only the module-global MODEL per candidate. Prompts,
contract, schema, validation, scoring and the 32768 headroom are unchanged.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
sys.path.insert(0, V14)

import judge_core_v1_4 as J  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


fxdoc = json.load(open(os.path.join(V14, "official-validation-fixtures.json")))
fixtures = fxdoc["fixtures"]
gold_doc = json.load(open(os.path.join(V14, "official-validation-gold.json")))
gold = gold_doc["gold"]
fixtures_sha = sha(os.path.join(V14, "official-validation-fixtures.json"))
gold_sha = sha(os.path.join(V14, "official-validation-gold.json"))
assert fixtures_sha == gold_doc["basis"]["fixtures_sha256"]
assert gold_doc["status"] == "FROZEN"

SMOKE_CASE = {
    "dimension": "route_correctness",
    "case_context": "TECHNICAL SMOKE - ikke en benchmark-sak.",
    "gold_criterion": "Akseptabel rute: helsesykepleier paa skolen.",
    "sut_answer": "TECHNICAL SMOKE: Du kan kontakte helsesykepleier paa skolen din.",
}


def save(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def smoke_call(key, model):
    J.MODEL = model
    t = J.call_judge(**SMOKE_CASE)
    return {
        "candidate_key": key, "model": model,
        "status": t.get("status"),
        "finish_reason": t.get("finish_reason"),
        "error": t.get("error"),
        "http_status": t.get("http_status"),
        "latency_seconds": t.get("latency_seconds"),
        "usage": t.get("usage"),
        "verdict": (t.get("result") or {}).get("verdict"),
        "classification": "SMOKE_PASS" if t.get("status") == "OK"
        else "TECHNICALLY_NOT_TESTABLE",
    }


def summarize(key, model, rows):
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
    completion = sorted(u.get("completion_tokens") for u in usage
                        if isinstance(u.get("completion_tokens"), int))
    latency = sorted(r["telemetry"]["latency_seconds"] for r in ok_rows
                     if isinstance(r["telemetry"].get("latency_seconds"), (int, float)))

    def p95(vals):
        if not vals:
            return None
        return vals[min(len(vals) - 1, int(round(0.95 * (len(vals) - 1))))]

    overall = (round(sum(1 for r in ok_rows if r["verdict_correct"]) / len(ok_rows), 4)
               if ok_rows else None)
    return {
        "candidate_key": key, "model": model,
        "provider": "commandcode-auth local proxy",
        "run_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_inputs": {
            "fixtures_sha256": fixtures_sha, "gold_sha256": gold_sha,
            "prompt_sha256": J.prompt_hash(),
            "judge_core_sha256": sha(os.path.join(V14, "judge_core_v1_4.py")),
            "model_config_sha256": sha(os.path.join(HERE, "model-configs", key + ".json")),
            "model": model, "temperature": J.TEMPERATURE,
            "max_tokens": J.MAX_TOKENS, "one_shot": True,
            "substantive_reruns": 0,
        },
        "n": len(rows), "status_ok": len(ok_rows),
        "transport_failures": sum(1 for r in rows
                                  if r.get("status") == "TRANSPORT_FAILURE"),
        "transport_capacity_failures": sum(
            1 for r in rows if r.get("status") == "TRANSPORT_CAPACITY_FAILURE"),
        "schema_failures": sum(1 for r in rows if r.get("status") == "SCHEMA_FAILURE"),
        "valid_semantic_result_rate": round(len(ok_rows) / len(rows), 4),
        "overall_verdict_accuracy": overall,
        "per_dimension": per_dim,
        "hard_zero": {"critical_fn": critical_fn,
                      "safety_forbidden_fn": safety_fn,
                      "false_acceptable_route": false_acceptable},
        "evidence_span_validity": {
            "checked": len(ok_rows),
            "invalid": sum(1 for r in ok_rows if not r["evidence_valid"])},
        "deterministic_overrides": 0,
        "token_usage": {
            "n_with_usage": len(usage),
            "completion_median": completion[len(completion) // 2] if completion else None,
            "completion_p95": p95(completion),
            "completion_max": completion[-1] if completion else None,
            "input_tokens_total": sum(u.get("prompt_tokens", 0) for u in usage
                                      if isinstance(u.get("prompt_tokens"), int)),
            "completion_tokens_total": sum(completion),
            "max_budget_fraction_used": round(completion[-1] / J.MAX_TOKENS, 4)
            if completion else None,
            "finish_reason_length_count": sum(
                1 for r in rows if r["telemetry"].get("finish_reason") == "length"),
        },
        "latency_seconds": {
            "median": latency[len(latency) // 2] if latency else None,
            "p95": p95(latency), "max": latency[-1] if latency else None,
        },
        "rows": rows,
    }


def run_benchmark(cand):
    key, model = cand["candidate_key"], cand["model"]
    J.MODEL = model
    rows = []
    ckpt_path = os.path.join(HERE, "checkpoint-" + key + ".json")
    ckpt = None
    if os.path.exists(ckpt_path):
        ckpt = json.load(open(ckpt_path))
        if ckpt.get("model") != model or ckpt.get("fixtures_sha256") != fixtures_sha:
            raise RuntimeError("checkpoint/model/fixture mismatch for " + key)
        rows = ckpt["rows"]
        print(f"RESUME {key}: {len(rows)} rows from checkpoint", flush=True)
    done_ids = {r["id"] for r in rows}
    for i, fx in enumerate(fixtures):
        if fx["id"] in done_ids:
            continue
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
            row["verdict_correct"] = t["result"].get("verdict") == g.get("verdict")
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
        print(f"{model} {i + 1}/{len(fixtures)} {fx['id']}: {tag}", flush=True)
        if len(rows) % 10 == 0 or len(rows) == len(fixtures):
            save(ckpt_path, {"candidate_key": key, "model": model,
                             "fixtures_sha256": fixtures_sha,
                             "completed_ids": sorted(done_ids | {fx["id"]}),
                             "rows": rows})
    return summarize(key, model, rows)


def main():
    order = json.load(open(os.path.join(HERE, "execution-order.json")))
    contract = json.load(open(os.path.join(
        HERE, "model-selection-contract-v1-5a.json")))
    lock = json.load(open(os.path.join(HERE, "TASK-LOCK.json")))
    for field in ("semantic_contract_changes_allowed", "gold_changes_allowed",
                  "prompt_tuning_allowed",
                  "candidate_model_silent_escalation_allowed"):
        assert lock[field] is False
    for c in order["candidate_order"]:
        cfg = json.load(open(os.path.join(
            HERE, "model-configs", c["candidate_key"] + ".json")))
        assert cfg["requested_model"] == c["model"]
    assert contract["execution"]["completion_headroom"] == 32768
    assert contract["mimo_baseline"]["rerun"] == "FORBIDDEN"

    smoke_path = os.path.join(HERE, "smoke-results.json")
    smoke_by_key = {}
    if os.path.exists(smoke_path):
        smoke_by_key = {s["candidate_key"]: s
                        for s in json.load(open(smoke_path)).get("results", [])}

    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        results = []
        for c in order["candidate_order"]:
            s = smoke_call(c["candidate_key"], c["model"])
            smoke_by_key[c["candidate_key"]] = s
            results.append(s)
            print("SMOKE", s["candidate_key"], s["status"], s["classification"],
                  flush=True)
        save(smoke_path, {"artifact": "V1.5A TECHNICAL SMOKE",
                          "preregistered": "1 synthetic non-benchmark call per candidate",
                          "results": results})
        print("V1_5A_SMOKE_DONE", flush=True)
        return

    smoke_results, candidate_results = [], []
    for c in order["candidate_order"]:
        key, model = c["candidate_key"], c["model"]
        s = smoke_by_key.get(key)
        if not s or s.get("classification") != "SMOKE_PASS":
            s = smoke_call(key, model)
            smoke_by_key[key] = s
        smoke_results.append(s)
        if s["classification"] != "SMOKE_PASS":
            print("SKIP benchmark (TECHNICALLY_NOT_TESTABLE):", key, flush=True)
            continue
        res = run_benchmark(c)
        candidate_results.append(res)
        save(os.path.join(HERE, "candidate-results-" + key + ".json"), res)
        save(smoke_path, {"artifact": "V1.5A TECHNICAL SMOKE",
                          "preregistered": "1 synthetic non-benchmark call per candidate",
                          "results": list(smoke_by_key.values())})
    save(os.path.join(HERE, "candidate-results.json"),
         {"artifact": "V1.5A CANDIDATE RESULTS",
          "baseline_not_rerun": {"model": "command-code/xiaomi/mimo-v2.5",
                                 "source": "V1.4 official validation results"},
          "candidates": [{k: v for k, v in r.items() if k != "rows"}
                         for r in candidate_results]})
    save(os.path.join(HERE, "token-latency-report.json"),
         {"artifact": "V1.5A TOKEN/LATENCY TELEMETRY",
          "candidates": [{"candidate_key": r["candidate_key"],
                          "token_usage": r["token_usage"],
                          "latency_seconds": r["latency_seconds"]}
                         for r in candidate_results]})
    print("V1_5A_CANDIDATE_EXECUTION_DONE", flush=True)


if __name__ == "__main__":
    main()
