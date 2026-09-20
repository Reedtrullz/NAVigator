#!/usr/bin/env python3
"""A.7 burned router development: run frozen-candidate Jev schema on supervised
rows, then evaluate routing policies. No gold or reviewer outcomes enter the
Jev state. Raw responses are stored; analysis is a separate step.

Usage:
  python3 run_router_dev.py run      # Jev calls (resumable)
  python3 run_router_dev.py analyze  # policy metrics vs burned labels
"""
import hashlib, json, pathlib, sys, time
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "native-jev-qualification-v2"))
import jev_client
import router_schema

CORPUS = HERE.parent / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"
LABELS = HERE / "minimum-sufficient-reviewer-burned.jsonl"
RAW = HERE / "router-dev-raw-jev.jsonl"
SCHEMA_FROZEN = HERE / "router-schema-frozen.json"
MODEL = "jev-latest"
TIER_INDEX = {"T1_BASIC": 0, "T2_INTERMEDIATE": 1, "T3_STRONG": 2, "T4_FRONTIER_RESERVE": 3}

def sha256_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def freeze_schema():
    schema = {
        "model": MODEL,
        "reasoning_complexity_levels": router_schema.REASONING_COMPLEXITY_LEVELS,
        "tier_choices": router_schema.TIER_CHOICES,
        "tier_instructions": router_schema.TIER_INSTRUCTIONS,
        "complexity_instructions": router_schema.COMPLEXITY_INSTRUCTIONS,
        "noul_signals": router_schema.NOUL_SIGNALS,
        "noul_instructions": router_schema.NOUL_INSTRUCTIONS,
        "state_fields": ["criterion", "case_context", "sut_output", "lane"],
    }
    blob = json.dumps(schema, ensure_ascii=False, sort_keys=True)
    SCHEMA_FROZEN.write_text(json.dumps({
        "candidate": "JEV_ROUTER_V1_DEV_CANDIDATE",
        "schema": schema,
        "schema_sha256": hashlib.sha256(blob.encode()).hexdigest(),
        "router_schema_py_sha256": sha256_file(HERE / "router_schema.py"),
    }, indent=2, ensure_ascii=False))
    print("frozen:", SCHEMA_FROZEN.name)

def load_rows():
    corpus = {}
    for line in CORPUS.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            corpus[r["canonical_hash"]] = r
    rows = []
    for line in LABELS.read_text().splitlines():
        if line.strip():
            lab = json.loads(line)
            if lab["supervised"]:
                lab["corpus_row"] = corpus[lab["row_id"]]
                rows.append(lab)
    rows.sort(key=lambda x: x["row_id"])
    return rows

def cmd_run():
    done = set()
    if RAW.exists():
        for line in RAW.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["row_id"])
    rows = load_rows()
    todo = [r for r in rows if r["row_id"] not in done]
    print(f"supervised={len(rows)} done={len(done)} todo={len(todo)}")
    with RAW.open("a") as f:
        for i, r in enumerate(todo):
            state = router_schema.router_state(r["corpus_row"])
            resp, dt = jev_client.system_one(state, router_schema.router_questions(), model=MODEL)
            rec = {
                "row_id": r["row_id"],
                "case_id": r["case_id"],
                "lane": r["lane"],
                "minimum_sufficient_tier": r["minimum_sufficient_tier"],
                "safety_critical": r["safety_critical"],
                "model": MODEL,
                "latency_s": round(dt, 3),
                "response": resp,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            tag = "OK" if "http_error" not in resp and "transport_error" not in resp else "ERR"
            print(f"[{i+1}/{len(todo)}] {tag} {r[chr(39)+chr(39)] if False else r["case_id"]} {dt:.1f}s", flush=True)
            time.sleep(0.2)

def extract(resp):
    if not isinstance(resp, dict):
        return {}
    return resp.get("answers") or {}

def choice_value(a):
    if not isinstance(a, dict):
        return None
    return a.get("choice") or a.get("answer") or a.get("selected") or a.get("value")

def prob(a):
    if not isinstance(a, dict):
        return None
    if "noul" in a:
        return a.get("noul")
    return a.get("confidence")

def cmd_analyze():
    recs = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    out = []
    for rec in recs:
        answers = extract(rec["response"])
        tier = None
        complexity = None
        signals = {}
        for k, a in answers.items():
            if k == "predicted_starting_tier":
                tier = choice_value(a)
            elif k == "reasoning_complexity":
                complexity = choice_value(a) if choice_value(a) is not None else a.get("score")
            elif k.startswith("signal_"):
                signals[k[7:]] = prob(a)
        out.append({**{k: rec[k] for k in ("row_id", "case_id", "lane", "minimum_sufficient_tier", "safety_critical")},
                    "predicted_tier": tier, "complexity": complexity, "signals": signals,
                    "transport_ok": "http_error" not in rec["response"] and "transport_error" not in rec["response"]})
    valid = [r for r in out if r["transport_ok"] and r["predicted_tier"] in TIER_INDEX]
    print(f"records={len(out)} valid={len(valid)}")
    print("predicted distribution:", dict(Counter(r["predicted_tier"] for r in valid)))
    print("complexity distribution:", dict(Counter(str(r["complexity"]) for r in valid)))
    (HERE / "router-dev-parsed.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "run":
        if not SCHEMA_FROZEN.exists():
            freeze_schema()
        cmd_run()
    elif sys.argv[1:] and sys.argv[1] == "analyze":
        cmd_analyze()
    elif sys.argv[1:] and sys.argv[1] == "freeze":
        freeze_schema()
    else:
        print("usage: run_router_dev.py run|analyze|freeze")
