#!/usr/bin/env python3
"""Stage A: build minimum-sufficient-reviewer labels on burned evidence.

FROZEN DECISIONS (pre-registered before any router development):

Tier mapping (A.1, fixed; based on Stage 0 routes/costs):
  T1_BASIC          mimo-v2.5-pro, laguna-s-2.1, ling-3.0-flash-sante
  T2_INTERMEDIATE   bai-deepseek, nex-n2.5-pro
  T3_STRONG         luna-high, luna-max
  T4_FRONTIER_RESERVE  (Astra LOW: defined tier, no historical per-row evidence)

Sufficiency (A.2): cell state CORRECT in the Stage 0 inventory already means
valid output + match against frozen gold + no contract violation, and a cell
is CORRECT only if ALL valid runs match gold (stability inherited).

Ladder rule (A.3/A.4, final):
  Walk tiers cheapest-first.
  - Tier state SUFFICIENT: at least one model cell CORRECT.
  - Tier state FAILED: at least one tested (INCORRECT/INVALID) cell and zero
    untested models left in the tier (complete coverage -> tier cannot work).
  - Tier state UNRESOLVED: some tested cells (all failed) but untested models
    remain, or no evaluable evidence.
  - minimum = cheapest tier that is SUFFICIENT, provided every cheaper tier is
    definitively FAILED. If any cheaper tier is UNRESOLVED/NO_EVIDENCE, the
    true minimum could be lower -> label MINIMUM_UNKNOWN (not supervised).
  - If no tier is SUFFICIENT and every tested tier is definitively FAILED
    (complete ladder coverage of T1-T3) -> T4_FRONTIER_RESERVE (supervised):
    the frozen order leaves only the frontier tier, so this is a ladder
    conclusion from exhaustive FAILED coverage, not labeling from absence.
  - If any tested tier is UNRESOLVED -> EVIDENCE_GAP_NO_TIER_CORRECT
    (not supervised).
  Existence semantics: a tier is sufficient if one of its routes works; the
  cascade must therefore order in-tier routes with known-good routes first
  (documented limitation, tested in Stage B).
"""
import json, pathlib, datetime
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
INV = ROOT / "reviewer-evidence-inventory.json"
OUT_JSONL = ROOT / "minimum-sufficient-reviewer-burned.jsonl"
OUT_TAX = ROOT / "stage-a-taxonomy-analysis.json"

TIERS = {
    "T1_BASIC": ["mimo-v2.5-pro", "laguna-s-2.1", "ling-3.0-flash-sante"],
    "T2_INTERMEDIATE": ["bai-deepseek", "nex-n2.5-pro"],
    "T3_STRONG": ["luna-high", "luna-max"],
    "T4_FRONTIER_RESERVE": [],
}
TIER_ORDER = ["T1_BASIC", "T2_INTERMEDIATE", "T3_STRONG", "T4_FRONTIER_RESERVE"]
EVALUABLE = ("CORRECT", "INCORRECT", "INVALID")

def tier_state(cells, models):
    states = [cells[m]["state"] for m in models if m in cells]
    tested = [s for s in states if s in EVALUABLE]
    n_correct = sum(1 for s in tested if s == "CORRECT")
    n_tested_models = len(tested)
    n_tier_models = len(models)
    detail = {
        "correct": n_correct,
        "incorrect": sum(1 for s in tested if s == "INCORRECT"),
        "invalid": sum(1 for s in tested if s == "INVALID"),
        "tested_models": n_tested_models,
        "tier_models": n_tier_models,
    }
    if n_correct > 0:
        detail["state"] = "SUFFICIENT"
    elif n_tested_models > 0 and n_tested_models == n_tier_models:
        detail["state"] = "FAILED"
    else:
        detail["state"] = "UNRESOLVED"
    return detail

def compute_min_tier(cells):
    detail = {}
    saw_evaluable = False
    blocked_lower = True  # true while every cheaper tier is definitively FAILED
    for tier in TIER_ORDER:
        d = tier_state(cells, TIERS[tier])
        detail[tier] = d
        st = d["state"]
        if d["tested_models"] > 0:
            saw_evaluable = True
        if st == "SUFFICIENT":
            if blocked_lower:
                return tier, detail, ("CHEAPEST_TIER_CORRECT" if tier == "T1_BASIC"
                                      else "CHEAPER_TIERS_DEFINITIVELY_FAILED")
            return "MINIMUM_UNKNOWN", detail, "CHEAPER_TIER_UNRESOLVED"
        if st == "FAILED":
            continue
        # UNRESOLVED (incl. no evidence): a cheaper-or-equal untested route may work
        blocked_lower = False
    if not saw_evaluable:
        return "NO_EVIDENCE_ANY_TIER", detail, "NEVER_RUN_ON_ANY_TIER"
    return "EVIDENCE_GAP_NO_TIER_CORRECT", detail, "ALL_TESTED_TIERS_FAILED"

def main():
    inv = json.loads(INV.read_text())
    rows = inv["rows"]
    out, dist, strength_dist = [], Counter(), Counter()
    fam_tier = defaultdict(Counter)
    for r in rows:
        if r["gold"] is None:
            continue
        tier, detail, strength = compute_min_tier(r["cells"])
        supervised = tier in TIER_ORDER
        rec = {
            "row_id": r["canonical_hash"],
            "case_id": r["case_id"],
            "lane": r["lane"],
            "frozen_gold": r["gold"],
            "available_model_evidence": detail,
            "minimum_sufficient_tier": tier,
            "supervised": supervised,
            "evidence_strength": strength,
            "safety_critical": r["safety_critical_trigger"],
            "source_corpus": "evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl",
            "burned": True,
        }
        out.append(rec)
        dist[tier] += 1
        strength_dist[strength] += 1
        fam_tier[r["lane"]][tier] += 1
    with OUT_JSONL.open("w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    safety = [x for x in out if x["safety_critical"]]
    tax = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "frozen_tier_mapping": TIERS,
        "tier_order": TIER_ORDER,
        "frozen_sufficiency_rule": {
            "cell_state": "Stage 0 CORRECT = valid output + frozen-gold match + no contract violation, all runs",
            "ladder": "cheapest SUFFICIENT tier with all cheaper tiers definitively FAILED; otherwise MINIMUM_UNKNOWN",
            "tier_FAILED": "all tier models tested (INCORRECT/INVALID), zero correct",
            "tier_UNRESOLVED": "no evaluable evidence, or tested failures with untested models remaining",
            "existence_note": "tier sufficient if one route works; cascade must order in-tier routes accordingly",
            "frontier": "T4 supervised only when T1-T3 all definitively FAILED (ladder exhaustion, not absence)",
        },
        "total_gold_rows": len(out),
        "label_distribution": dict(dist),
        "supervised_rows": sum(v for k, v in dist.items() if k in TIER_ORDER),
        "min_unknown_rows": dist.get("MINIMUM_UNKNOWN", 0),
        "evidence_gap_rows": dist.get("EVIDENCE_GAP_NO_TIER_CORRECT", 0),
        "evidence_strength_distribution": dict(strength_dist),
        "safety_critical_rows": len(safety),
        "safety_critical_supervised": sum(1 for x in safety if x["supervised"]),
        "safety_critical_min_tier_distribution": dict(Counter(x["minimum_sufficient_tier"] for x in safety)),
        "family_x_tier": {k: dict(v) for k, v in fam_tier.items()},
    }
    OUT_TAX.write_text(json.dumps(tax, indent=2, ensure_ascii=False))
    keys = ("total_gold_rows", "label_distribution", "supervised_rows",
            "min_unknown_rows", "evidence_gap_rows", "safety_critical_rows",
            "safety_critical_supervised", "safety_critical_min_tier_distribution")
    print(json.dumps({k: tax[k] for k in keys}, indent=1))

if __name__ == "__main__":
    main()
