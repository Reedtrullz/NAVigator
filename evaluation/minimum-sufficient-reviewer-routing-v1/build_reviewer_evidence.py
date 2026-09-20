#!/usr/bin/env python3
"""Stage 0: read-only reviewer evidence inventory for router V1."""
import json
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/Users/reidar/Projectos/NAV Explore/evaluation")
OUT = BASE / "minimum-sufficient-reviewer-routing-v1"
CORPUS = BASE / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"

SOURCES = [
    ("mimo-v2.5-pro", "command-code", "cost-qual-v1-screen",
     BASE / "semantic-reviewer-cost-qualification-v1" / "screening-results.json", "candidates"),
    ("nemotron-3-ultra", "openrouter", "cost-qual-v1-screen",
     BASE / "semantic-reviewer-cost-qualification-v1" / "screening-results.json", "candidates"),
    ("nex-n2.5-pro", "openrouter", "cost-qual-v1-screen",
     BASE / "semantic-reviewer-cost-qualification-v1" / "screening-results.json", "candidates"),
    ("gemma-4-31b-it", "openrouter", "cost-qual-v1-screen",
     BASE / "semantic-reviewer-cost-qualification-v1" / "screening-results.json", "candidates"),
    ("laguna-s-2.1", "command-code", "cost-qual-v2-screen",
     BASE / "semantic-reviewer-cost-qualification-v2" / "semantic-screen-results.json", "candidates"),
    ("ling-3.0-flash-sante", "command-code", "cost-qual-v2-screen",
     BASE / "semantic-reviewer-cost-qualification-v2" / "semantic-screen-results.json", "candidates"),
    ("mimo-v2.5-pro", "command-code", "cost-qual-v1-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v1" / "transport-screen-results.json", "candidates"),
    ("nemotron-3-ultra", "openrouter", "cost-qual-v1-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v1" / "transport-screen-results.json", "candidates"),
    ("nex-n2.5-pro", "openrouter", "cost-qual-v1-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v1" / "transport-screen-results.json", "candidates"),
    ("gemma-4-31b-it", "openrouter", "cost-qual-v1-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v1" / "transport-screen-results.json", "candidates"),
    ("inkling-small", "openrouter", "cost-qual-v1-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v1" / "transport-screen-results.json", "candidates"),
    ("gemma-4-26b-a4b-it", "openrouter", "cost-qual-v2-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v2" / "transport-screen-results.json", "candidates"),
    ("laguna-s-2.1", "command-code", "cost-qual-v2-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v2" / "transport-screen-results.json", "candidates"),
    ("ling-3.0-flash-sante", "command-code", "cost-qual-v2-transport-retry",
     BASE / "semantic-reviewer-cost-qualification-v2" / "transport-screen-results.json", "candidates"),
    ("luna-high", "codex-gpt-5-6-luna-reasoning-high", "luna-qual-screen",
     BASE / "semantic-reviewer-luna-qualification-v1" / "screening-results.json", "configs"),
    ("luna-max", "codex-gpt-5-6-luna-reasoning-max", "luna-qual-screen",
     BASE / "semantic-reviewer-luna-qualification-v1" / "screening-results.json", "configs"),
    ("luna-high", "codex-gpt-5-6-luna-reasoning-high", "luna-qual-dualpass-A",
     BASE / "semantic-reviewer-luna-qualification-v1" / "dual-pass-progress-luna-high-A-forbidden_claim.jsonl", "jsonl"),
    ("luna-high", "codex-gpt-5-6-luna-reasoning-high", "luna-qual-dualpass-A",
     BASE / "semantic-reviewer-luna-qualification-v1" / "dual-pass-progress-luna-high-A-critical_condition.jsonl", "jsonl"),
    ("luna-high", "codex-gpt-5-6-luna-reasoning-high", "luna-qual-dualpass-B",
     BASE / "semantic-reviewer-luna-qualification-v1" / "dual-pass-progress-luna-high-B-forbidden_claim.jsonl", "jsonl"),
    ("luna-high", "codex-gpt-5-6-luna-reasoning-high", "luna-qual-dualpass-B",
     BASE / "semantic-reviewer-luna-qualification-v1" / "dual-pass-progress-luna-high-B-critical_condition.jsonl", "jsonl"),
    ("bai-deepseek", "bai-deepseek", "bai-v3-dualpass",
     BASE / "semantic-reviewer-bai-qualification-v3" / "full-qualification-results.json", "bai"),
]

INCOMPATIBLE_REGISTERED = [
    {"source": "evaluation/judge-deepseek-v2-4-m2-validation", "model": "deepseek-v4.1-flash",
     "reason": "different judge contract and calibration-fixture format; not row-level comparable against shared frozen gold",
     "classification": "INCOMPATIBLE_CONTRACT"},
    {"source": "evaluation/native-jev-qualification-v2 + native-jev-fresh-qualification-v3", "model": "jev-1.13.0",
     "reason": "Jev is the router candidate under evaluation in this task, not a reviewer tier with comparable correctness evidence",
     "classification": "OUT_OF_SCOPE_ROUTER_CANDIDATE"},
]

CANON = {
    "nemotron-3-ultra": "nemotron-3-ultra",
    "nex-n2.5-pro": "nex-n2.5-pro",
    "gemma-4-31b-it": "gemma-4-31b-it",
    "mimo-v2.5-pro": "mimo-v2.5-pro",
    "R2-laguna-s-2.1": "laguna-s-2.1",
    "R3-ling-3.0-flash-sante": "ling-3.0-flash-sante",
    "R4-gemma-4-26b-a4b-it": "gemma-4-26b-a4b-it",
    "R5-inkling-small": "inkling-small",
    "luna-high": "luna-high",
    "luna-max": "luna-max",
    "bai-deepseek": "bai-deepseek",
    "luna-high-A": "luna-high",
    "luna-high-B": "luna-high",
    "BAI-DEEPSEEK-forbidden_claim-A": "bai-deepseek",
    "BAI-DEEPSEEK-forbidden_claim-B": "bai-deepseek",
    "BAI-DEEPSEEK-critical_condition-A": "bai-deepseek",
    "BAI-DEEPSEEK-critical_condition-B": "bai-deepseek",
}


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_results(path, kind):
    if kind == "jsonl":
        stem = path.stem
        name = stem.replace("dual-pass-progress-", "").rsplit("-", 1)[0]
        yield name, [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        return
    d = json.loads(path.read_text())
    if kind == "candidates":
        for name, c in d["candidates"].items():
            yield name, c.get("results", [])
    elif kind == "configs":
        for name, c in d["configs"].items():
            yield name.lower(), c.get("results", [])
    elif kind == "jsonl":
        stem = path.stem
        name = stem.replace("dual-pass-progress-", "").rsplit("-", 1)[0]
        yield name, [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    elif kind == "bai":
        for name, c in d["candidates"].items():
            for lane, passes in c.items():
                if isinstance(passes, dict):
                    for p_label in ("A", "B"):
                        if p_label in passes:
                            yield name + "-" + lane + "-" + p_label, passes[p_label]


def evaluate(parsed, lane, gold):
    if parsed is None:
        return "UNKNOWN", "no parsed output"
    try:
        if lane == "forbidden_claim":
            g = gold["authoritative_fields"]
            pm = parsed.get("criterion_semantic_match")
            pc = parsed.get("speaker_commitment")
            if pm is None or pc is None:
                return "UNKNOWN", "missing forbidden fields"
            ok = pm == g.get("criterion_semantic_match") and pc == g.get("speaker_commitment")
            detail = "pred=(%s,%s) gold=(%s,%s)" % (pm, pc, g.get("criterion_semantic_match"), g.get("speaker_commitment"))
            return ("CORRECT" if ok else "INCORRECT"), detail
        if lane == "critical_condition":
            g = gold["authoritative_fields"].get("critical_evidence_state")
            pred = parsed.get("critical_evidence_state")
            if pred is None:
                return "UNKNOWN", "missing critical_evidence_state"
            return ("CORRECT" if pred == g else "INCORRECT"), "pred=%s gold=%s" % (pred, g)
    except Exception as exc:
        return "UNKNOWN", "evaluation error: %s" % exc
    return "INCOMPATIBLE_CONTRACT", "lane not comparable"


def state_from_result(r):
    st = r.get("status")
    if st == "OK":
        checks = [r.get(k) for k in ("schema_valid", "enum_valid", "evidence_valid") if k in r]
        if checks and not all(checks):
            return "INVALID"
        return "VALID"
    if st in ("TRANSPORT_ERROR", "ERROR"):
        return "TRANSPORT_ERROR"
    return "INVALID"


def family_of(gold_fields, lane):
    if lane == "critical_condition":
        s = gold_fields.get("critical_evidence_state")
        return {"CLEAR_TRIGGER_SUPPORT": "trigger_support",
                "CLEAR_NON_TRIGGER_SUPPORT": "non_trigger_support",
                "AMBIGUOUS_TO_DECIDE": "ambiguous",
                "INSUFFICIENT_TO_DECIDE": "unresolved"}.get(s, "critical:" + str(s))
    m = gold_fields.get("criterion_semantic_match")
    c = gold_fields.get("speaker_commitment")
    if m == "MATCH" and c == "ASSERTED":
        return "forbidden_match_asserted"
    if m == "MATCH" and c == "NEGATED":
        return "forbidden_match_negated"
    if m == "NO_MATCH" and c == "UNRESOLVED":
        return "forbidden_no_match_unresolved"
    return "forbidden:" + str(m) + ":" + str(c)


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    corpus_rows = [json.loads(x) for x in CORPUS.read_text().splitlines() if x.strip()]
    gold_by_hash = {r["canonical_hash"]: r for r in corpus_rows}
    corpus_sha = sha256_file(CORPUS)

    cells = defaultdict(list)
    source_counts = []
    for model_id, provider, task, path, kind in SOURCES:
        if not path.exists():
            source_counts.append({"source": task, "file": str(path), "error": "missing"})
            continue
        n_rows = 0
        for key, results in load_results(path, kind):
            model = CANON.get(key, key)
            if model != model_id:
                continue
            for r in results:
                h = r.get("canonical_hash")
                if not h:
                    continue
                n_rows += 1
                st = state_from_result(r)
                run = {"source": task, "state": st, "status": r.get("status")}
                if st == "VALID":
                    row = gold_by_hash.get(h)
                    lane = r.get("lane")
                    if row is None or lane != row.get("lane"):
                        run["eval"] = ("INCOMPATIBLE_CONTRACT", "row missing from gold corpus or lane mismatch")
                    else:
                        run["eval"] = evaluate(r.get("parsed"), lane, row["observation"])
                cells[(h, model)].append(run)
        source_counts.append({"source": task, "file": str(path), "rows_loaded": n_rows})

    all_hashes = set(gold_by_hash) | {h for (h, _m) in cells}

    def classify_runs(runs):
        valid = [r for r in runs if r["state"] == "VALID"]
        if valid:
            evals = [r.get("eval") for r in valid]
            if any(e is None or e[0] in ("UNKNOWN", "INCOMPATIBLE_CONTRACT") for e in evals):
                return "UNKNOWN", len(valid)
            if all(e[0] == "CORRECT" for e in evals):
                return "CORRECT", len(valid)
            return "INCORRECT", len(valid)
        if any(r["state"] == "TRANSPORT_ERROR" for r in runs):
            return "TRANSPORT_ERROR", 0
        return "INVALID", 0

    rows_out = []
    models_present = sorted({m for (_h, m) in cells})
    for h in sorted(all_hashes):
        row = gold_by_hash.get(h)
        lane = row["lane"] if row else None
        obs = row.get("observation") if row else None
        gold = obs.get("authoritative_fields") if isinstance(obs, dict) else None
        case_id = row.get("case_id") if row else None
        safety = bool(row and lane == "critical_condition" and isinstance(gold, dict) and gold.get("critical_evidence_state") == "CLEAR_TRIGGER_SUPPORT")
        cell_states = {}
        for model in models_present:
            runs = cells.get((h, model))
            if not runs:
                cell_states[model] = {"state": "NOT_RUN", "n_valid_runs": 0, "n_runs": 0}
            else:
                state, n_valid = classify_runs(runs)
                cell_states[model] = {"state": state, "n_valid_runs": n_valid, "n_runs": len(runs)}
        rows_out.append({
            "canonical_hash": h,
            "case_id": case_id,
            "lane": lane,
            "gold": gold,
            "safety_critical_trigger": safety,
            "in_gold_corpus": row is not None,
            "cells": cell_states,
        })

    models = models_present
    model_stats = {}
    for m in models:
        c = Counter(row["cells"][m]["state"] for row in rows_out)
        model_stats[m] = dict(c)

    fam_counts = Counter()
    for row in rows_out:
        if row["gold"]:
            fam_counts[family_of(row["gold"], row["lane"])] += 1

    inventory = {
        "artifact": "reviewer-evidence-inventory",
        "task_id": "NAV-EXPLORE-MINIMUM-SUFFICIENT-REVIEWER-ROUTING-V1",
        "stage": "STAGE_0_READ_ONLY",
        "generated_utc": now,
        "gold_corpus": {"path": str(CORPUS), "sha256": corpus_sha, "rows": len(corpus_rows),
                        "note": "frozen authoritative semantic reference (LLM-consensus lineage), not human ground truth"},
        "sources_loaded": source_counts,
        "incompatible_registered": INCOMPATIBLE_REGISTERED,
        "models": models,
        "cell_states_enum": ["CORRECT", "INCORRECT", "INVALID", "TRANSPORT_ERROR", "NOT_RUN", "INCOMPATIBLE_CONTRACT", "UNKNOWN"],
        "cell_state_rule": "cell is CORRECT only if ALL valid runs on that row match frozen gold (strict stability); NOT_RUN is not an error",
        "model_summary": model_stats,
        "family_counts": dict(fam_counts),
        "rows": rows_out,
    }
    (OUT / "reviewer-evidence-inventory.json").write_text(json.dumps(inventory, indent=1, ensure_ascii=False))

    gaps = {"artifact": "reviewer-evidence-gaps", "task_id": inventory["task_id"], "generated_utc": now,
            "model_gaps": {}, "family_gaps": []}
    for m in models:
        st = model_stats[m]
        evaluable = st.get("CORRECT", 0) + st.get("INCORRECT", 0)
        gaps["model_gaps"][m] = {
            "rows_with_any_run": sum(v for k, v in st.items() if k != "NOT_RUN"),
            "evaluable_rows": evaluable,
            "coverage_share_of_corpus": round(evaluable / len(corpus_rows), 4),
            "missing_on_corpus_rows": len(corpus_rows) - evaluable,
        }
    for f in fam_counts:
        per_model = {}
        for m in models:
            per_model[m] = sum(1 for row in rows_out if row["gold"] and family_of(row["gold"], row["lane"]) == f
                               and row["cells"].get(m, {}).get("state") == "CORRECT")
        if fam_counts[f] > 0 and max(per_model.values()) < fam_counts[f]:
            gaps["family_gaps"].append({"family": f, "family_rows": fam_counts[f], "correct_per_model": per_model})
    (OUT / "reviewer-evidence-gaps.json").write_text(json.dumps(gaps, indent=1, ensure_ascii=False))

    lines = ["# Reviewer Evidence Coverage - Stage 0 (read-only)", "",
             "Generated: " + now, "Gold corpus rows: " + str(len(corpus_rows)) + "  sha256 prefix: " + corpus_sha[:16], "",
             "## Sources", ""]
    for s in source_counts:
        lines.append("- " + s.get("source") + ": " + str(s.get("rows_loaded", s.get("error"))) + " rows")
    lines += ["", "## Registered incompatible / out-of-scope", ""]
    for inc in INCOMPATIBLE_REGISTERED:
        lines.append("- " + inc["source"] + " (" + inc["model"] + "): " + inc["classification"] + " - " + inc["reason"])
    lines += ["", "## Per-model cell states (union universe " + str(len(all_hashes)) + " rows)", "",
              "Model | CORRECT | INCORRECT | INVALID | TRANSPORT_ERROR | UNKNOWN"]
    for m in models:
        st = model_stats[m]
        lines.append("- " + m + ": " + str(st.get("CORRECT", 0)) + " / " + str(st.get("INCORRECT", 0)) + " / "
                     + str(st.get("INVALID", 0)) + " / " + str(st.get("TRANSPORT_ERROR", 0)) + " / " + str(st.get("UNKNOWN", 0)))
    lines += ["", "## Gold family coverage (corpus rows)", ""]
    for f, n in fam_counts.most_common():
        lines.append("- " + f + ": " + str(n))
    lines += ["", "## Family gaps", ""]
    for g in gaps["family_gaps"]:
        lines.append("- " + g["family"] + ": " + str(g["family_rows"]) + " rows; correct per model: " + json.dumps(g["correct_per_model"]))
    lines += ["", "## Key reading", "",
              "- Only the 90-row screening core has broad multi-model coverage; Luna dual-pass extends Luna to the full labeled corpus.",
              "- Forbidden MATCH/ASSERTED gold rows are the rarest family and historically under-covered by cheap tiers.",
              "- NOT_RUN cells are coverage gaps, not model failures, and must not be read as stronger-model-required.", ""]
    (OUT / "reviewer-evidence-coverage.md").write_text("\n".join(lines))

    print(json.dumps({"universe_rows": len(all_hashes), "corpus_rows": len(corpus_rows),
                      "models": models, "model_summary": model_stats, "family_counts": dict(fam_counts)}, indent=1))


if __name__ == "__main__":
    main()
