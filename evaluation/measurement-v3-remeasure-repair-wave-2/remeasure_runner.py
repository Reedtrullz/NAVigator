#!/usr/bin/env python3
"""Task-local remeasure runner for NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2.

Stage A (default): score the frozen Wave-2 v2 replay predictions with the
FROZEN combined measurement engine, generate fresh semantic review packets
from Wave-2 outputs, run leakage + reviewability audits, and a determinism
re-pass.

--freeze-review-inputs: freeze packet hashes, review order, and astra-config
before any model call.

The burned-baseline runner is imported unmodified; only its path globals are
rebound in memory to this task's frozen inputs. Stdlib only. No model calls.
"""
import hashlib
import importlib.util
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(OUT))
EVAL = os.path.join(REPO, "evaluation")

_spec = importlib.util.spec_from_file_location(
    "frozen_run_baseline",
    os.path.join(EVAL, "measurement-v3-burned-baseline-v1", "run_baseline.py"))
BASE = importlib.util.module_from_spec(_spec)
sys.modules["frozen_run_baseline"] = BASE
_spec.loader.exec_module(BASE)

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2"

# Rebind frozen-runner globals in memory only (originals untouched on disk).
BASE.OUT = OUT
BASE.TASK_ID = TASK_ID
BASE.P3_RUNS = os.path.join(EVAL, "full-sut-repair-wave-2-v1", "runs")
BASE.CORPUS_DIR = os.path.join(EVAL, "dev-corpus-v1-1-repair", "cases")
BASE.AUDIT_META_ARTIFACTS = ("remeasure_runner.py", "security-audit.json")
BASE.FAMILIES = [
    ("safety", "structural-120-replay-v2/safety", "safety_cases.json"),
    ("routing", "structural-120-replay-v2/routing", "routing_cases.json"),
    ("discovery_adversarial",
     "structural-120-replay-v2/discovery_adversarial",
     "discovery_adversarial_cases.json"),
]
BASE.PERF_JSON = os.path.join(OUT, "replay-perf-not-available.json")

SEMANTIC_PACKETS = "semantic-review-packets.jsonl"
SEMANTIC_MANIFEST = "semantic-review-packet-manifest.json"
LEAK_AUDIT = "semantic-review-leakage-audit.json"
REVIEWABILITY = "semantic-reviewability-audit.json"
ASTRA_CONFIG = "astra-config.json"
FREEZE_MANIFEST = "semantic-review-inputs-freeze-manifest.json"

WAVE1_RESULTS = os.path.join(
    EVAL, "measurement-v3-wave1-consensus-comparator-repair-v1",
    "complete-wave1-measurement-results.json")
ORIGINAL_BASELINE_RESULTS = os.path.join(
    EVAL, "measurement-v3-final-authority-provenance-repair-v1",
    "combined-measurement-results-complete-provenance-corrected.json")


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_json(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def load_json(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)


def prediction_sha_map():
    out = {}
    for _, run_dir, _ in BASE.FAMILIES:
        pdir = os.path.join(BASE.P3_RUNS, run_dir, "predictions")
        for fn in sorted(os.listdir(pdir)):
            if fn.endswith(".json"):
                out[fn[:-5]] = sha_file(os.path.join(pdir, fn))
    return out


def corpus_binding(case_id):
    for _, _, case_file in BASE.FAMILIES:
        path = os.path.join(BASE.CORPUS_DIR, case_file)
        data = json.load(open(path, encoding="utf-8"))
        for c in data["cases"]:
            if c["id"] == case_id:
                return {"corpus_file": "cases/" + case_file,
                        "corpus_sha256": sha_file(path)}
    raise RuntimeError("case not found in corpus: " + case_id)


def gold_binding(case_id, criterion_id, dimension):
    bind = corpus_binding(case_id)
    path = os.path.join(BASE.CORPUS_DIR,
                        os.path.basename(bind["corpus_file"]))
    data = json.load(open(path, encoding="utf-8"))
    case = next(c for c in data["cases"] if c["id"] == case_id)
    gold = case.get("gold", {})
    if dimension == "forbidden_claim":
        idx = int(criterion_id.split(":")[-1])
        claim = gold["forbidden_claims"][idx - 1]
        return dict(bind, gold_field="gold.forbidden_claims[%d]" % (idx - 1),
                    criterion_source_text=claim)
    return dict(bind, gold_field="gold.critical_error_if",
                criterion_source_text=str(gold.get("critical_error_if") or ""))


def prior_verdict_map():
    prior = {}
    for path in (ORIGINAL_BASELINE_RESULTS, WAVE1_RESULTS):
        data = json.load(open(path, encoding="utf-8"))
        for case in data["cases"]:
            for r in case["criteria"]:
                prior.setdefault(r["criterion_id"], r.get("verdict"))
    return prior


def leakage_audit_extended(packets):
    base = BASE.leak_audit(packets)
    prior = prior_verdict_map()
    hard = {"EXPECTED_VERDICT_VISIBLE": 0,
            "PRIOR_WAVE1_RESULT_VISIBLE": 0,
            "PRIOR_BASELINE_RESULT_VISIBLE": 0,
            "PRIOR_MODEL_RESULT_VISIBLE": 0,
            "EXPECTED_REPAIR_EFFECT_VISIBLE": 0}
    prior_meta = {
        "PRIOR_WAVE1_RESULT_VISIBLE": ("wave-1", "wave1"),
        "PRIOR_BASELINE_RESULT_VISIBLE": ("baseline", "remeasure"),
        "PRIOR_MODEL_RESULT_VISIBLE": ("astra", "sol "),
        "EXPECTED_REPAIR_EFFECT_VISIBLE": ("repair", "rc-01", "rc-02",
                                           "rc-03", "rc-07", "rc-08",
                                           "rc-10", "rc-11")}
    per = []
    for p in packets:
        pkt = p["packet"]
        content = " ".join(str(pkt.get(k, "")) for k in
                           ("criterion", "case_context", "sut_output"))
        low = content.lower()
        ov = prior.get(p["criterion_id"])
        exp_hit = ov is not None and str(ov) in content
        hits = {flag: [t for t in toks if t in low]
                for flag, toks in prior_meta.items()}
        row = {"packet_id": pkt["packet_id"],
               "criterion_id": p["criterion_id"],
               "expected_verdict_hit": exp_hit,
               "prior_meta_hits": {k: v for k, v in hits.items() if v}}
        per.append(row)
        if exp_hit:
            hard["EXPECTED_VERDICT_VISIBLE"] += 1
        for flag in prior_meta:
            if hits[flag]:
                hard[flag] += 1
    return {"artifact": "semantic-review-leakage-audit",
            "task_id": TASK_ID,
            "base_audit": base,
            "hard_flags": hard,
            "hard_flags_pass": all(v == 0 for v in hard.values()),
            "per_packet": per,
            "notes": ["expected-verdict scan compares each packet against "
                      "prior Wave-1 and original-baseline derived verdicts "
                      "for the same criterion",
                      "prior-meta scan is case-insensitive over criterion/"
                      "case_context/sut_output",
                      "contract enum names inside reviewer_instructions are "
                      "legitimate contract context, not prior results"]}


def reviewability_audit(packets):
    rows, bad = [], []
    for p in packets:
        pkt = p["packet"]
        cid, dim = p["case_id"], p["dimension"]
        crit = str(pkt.get("criterion", "")).strip()
        g = gold_binding(cid, p["criterion_id"], dim)
        checks = {
            "criterion_present": bool(crit),
            "criterion_semantically_complete_proxy":
                len(crit) >= 10 and "..." not in crit,
            "criterion_bound_to_gold": crit == g["criterion_source_text"],
            "contract_context_present":
                pkt.get("contract_version") in
                ("semantic-judge-contract-v1-4",
                 "semantic-judge-contract-v2-7e"),
            "sut_answer_present": bool(str(pkt.get("sut_output", "")).strip()),
            "case_context_present":
                bool(str(pkt.get("case_context", "")).strip()),
            "correct_lane": dim in ("critical_condition", "forbidden_claim"),
            "permitted_enum_visible": bool(pkt.get("reviewer_instructions")),
            "packet_schema_valid": BASE.SEM.validate_packet(pkt)[0],
        }
        ok = all(checks.values())
        rows.append({"packet_id": pkt["packet_id"],
                     "criterion_id": p["criterion_id"], "dimension": dim,
                     "checks": checks, "reviewable": ok})
        if not ok:
            bad.append(rows[-1])
    return {"artifact": "semantic-reviewability-audit", "task_id": TASK_ID,
            "packets_total": len(packets),
            "packets_reviewable": sum(1 for r in rows if r["reviewable"]),
            "pass": not bad, "failed": bad, "per_packet": rows,
            "note": "gold binding verified by comparing packet criterion "
                    "verbatim against the repaired corpus gold field"}


def stage_a():
    with open(BASE.PERF_JSON, "w", encoding="utf-8") as f:
        json.dump({"source": "full-sut-repair-wave-2-v1 "
                             "structural-120-replay-v2 replay run; no "
                             "performance-diagnostics artifact exists for "
                             "replay mode",
                   "discovery_invoked_n": None, "latency_ms": None}, f,
                  indent=2)
        f.write("\n")
    pred_sha = prediction_sha_map()
    if len(pred_sha) != 120:
        raise RuntimeError("expected 120 replay predictions, got %d"
                           % len(pred_sha))
    BASE.stage1()

    routing = load_json("measurement-routing-results.json")
    routing["artifact"] = "measurement-routing"
    routing["prediction_source"] = ("evaluation/full-sut-repair-wave-2-v1/"
                                    "runs/structural-120-replay-v2")
    routing["corpus_source"] = "evaluation/dev-corpus-v1-1-repair/cases"
    routing["prediction_sha256_by_case"] = pred_sha
    write_json("measurement-routing.json", routing)

    det = load_json("deterministic-scores.json")
    det["artifact"] = "deterministic-results"
    det["prediction_source"] = ("evaluation/full-sut-repair-wave-2-v1/"
                                "runs/structural-120-replay-v2")
    det["corpus_source"] = "evaluation/dev-corpus-v1-1-repair/cases"
    write_json("deterministic-results.json", det)

    with open(os.path.join(OUT, "human-review-packets.jsonl"),
              encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    batch0 = load_json("human-review-batch-manifest.json")
    meta_by_id = {h["packet_id"]: h for h in batch0["packet_hashes"]}
    packets = []
    for l in lines:
        pkt = json.loads(l)
        h = meta_by_id[pkt["packet_id"]]
        packets.append({"packet": pkt, "criterion_id": h["criterion_id"],
                        "case_id": h["case_id"], "dimension": h["dimension"]})
    with open(os.path.join(OUT, SEMANTIC_PACKETS), "w", encoding="utf-8") as f:
        for l in lines:
            f.write(l + "\n")

    batch = load_json("human-review-batch-manifest.json")
    entries = []
    for h in batch["packet_hashes"]:
        g = gold_binding(h["case_id"], h["criterion_id"], h["dimension"])
        entries.append(dict(h, prediction_sha256=pred_sha[h["case_id"]],
                            gold_provenance=g))
    batch["artifact"] = SEMANTIC_MANIFEST.rsplit(".", 1)[0]
    batch["task_id"] = TASK_ID
    batch["queue_path"] = SEMANTIC_PACKETS
    batch["packet_bindings"] = entries
    batch["prediction_set"] = ("evaluation/full-sut-repair-wave-2-v1/runs/"
                               "structural-120-replay-v2")
    batch["prediction_sha256_by_case"] = pred_sha
    write_json(SEMANTIC_MANIFEST, batch)

    leak = leakage_audit_extended(packets)
    write_json(LEAK_AUDIT, leak)
    rev = reviewability_audit(packets)
    write_json(REVIEWABILITY, rev)

    write_json(ASTRA_CONFIG, {
        "artifact": "astra-review-config",
        "task_id": TASK_ID,
        "model": "gpt-6-astra",
        "reasoning_effort": "LOW",
        "reasoning_effort_enforcement": "hard; MEDIUM/HIGH/MAX forbidden",
        "transport": "local proxy http://127.0.0.1:10100/v1/chat/completions",
        "auth": "bearer token from existing auth store; never printed, "
                "logged, or persisted in artifacts",
        "passes": ["ASTRA-A", "ASTRA-B"],
        "blindness": "B must not see A; neither pass may see historical "
                     "verdicts, Wave-1 results, gold outcomes, or prior "
                     "model results",
        "response_format": {"type": "json_object"},
        "retry_policy": "ONE technical transport retry only; schema-invalid "
                        "or semantically disagreeing output is NOT retried",
        "no_web": True,
        "review_order_source": SEMANTIC_MANIFEST + " packet_bindings order",
    })

    print(json.dumps({
        "stage": "A",
        "deterministic_rows": sum(
            1 for c in det["cases"] for r in c["criteria"]
            if r["authority"] == "DETERMINISTIC"),
        "semantic_pending_rows": sum(
            1 for c in det["cases"] for r in c["criteria"]
            if r["authority"] == "HUMAN_REVIEW"),
        "packets": len(packets),
        "packets_by_dimension": batch["packets_by_dimension"],
        "leakage_pass": leak["hard_flags_pass"],
        "reviewability_pass": rev["pass"],
    }, ensure_ascii=False))


def freeze_review_inputs():
    leak = load_json(LEAK_AUDIT)
    rev = load_json(REVIEWABILITY)
    if not leak["hard_flags_pass"]:
        raise RuntimeError("leakage audit failing; refusing to freeze")
    if not rev["pass"]:
        raise RuntimeError("reviewability audit failing; refusing to freeze")
    names = [SEMANTIC_PACKETS, SEMANTIC_MANIFEST, LEAK_AUDIT, REVIEWABILITY,
             ASTRA_CONFIG]
    files = {}
    for fn in names:
        p = os.path.join(OUT, fn)
        files[fn] = {"sha256": sha_file(p), "bytes": os.path.getsize(p)}
    order = [e["packet_id"] for e in
             load_json(SEMANTIC_MANIFEST)["packet_hashes"]]
    manifest = {"artifact": "semantic-review-inputs-freeze-manifest",
                "task_id": TASK_ID, "status": "FROZEN",
                "frozen_before_model_calls": True,
                "files": files, "review_order": order,
                "note": "packets must not be mutated after this freeze"}
    write_json(FREEZE_MANIFEST, manifest)
    for fn, meta in files.items():
        assert sha_file(os.path.join(OUT, fn)) == meta["sha256"], fn
    print(json.dumps({"stage": "freeze-review-inputs",
                      "frozen": {k: v["sha256"] for k, v in files.items()},
                      "review_order_n": len(order)}))


if __name__ == "__main__":
    if "--freeze-review-inputs" in sys.argv:
        freeze_review_inputs()
    else:
        stage_a()
