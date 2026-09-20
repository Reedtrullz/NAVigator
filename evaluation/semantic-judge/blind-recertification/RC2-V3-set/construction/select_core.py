#!/usr/bin/env python3
# ponytail: greedy-with-rescoring; swap to ILP only if quotas fail.
"""Constraint-based CORE selection (spec 22-24)."""
import json
import sys
from collections import Counter

N_TARGET = 160
SEM_TARGET = {"SUPPORTED": 40, "CONTRADICTED": 40, "PARTIALLY_SUPPORTED": 40, "INSUFFICIENT_EVIDENCE": 40}
SEM_FLOOR = {k: v - 5 for k, v in SEM_TARGET.items()}
SEM_FLOOR["INSUFFICIENT_EVIDENCE"] = max(SEM_FLOOR["INSUFFICIENT_EVIDENCE"], 30)
PRODUCT_MIN = {"AUTO_SUPPORTED": 25, "AUTO_CONTRADICTED": 25, "REVIEW_REQUIRED": 25, "ABSTAIN_INSUFFICIENT": 25}
FLAG_MIN = {
    "cond_exc": 30, "compound": 50, "multi_span": 30, "numeric": 30,
    "temporal": 30, "actor": 30, "modality": 30, "safety": 20,
    "legal": 30, "locality": 20, "age_legal": 20,
}


def pick(cases):
    chosen = []
    sem_count = Counter()
    prod_count = Counter()
    flag_count = Counter()

    def unmet():
        u_sem = {s for s, t in SEM_TARGET.items() if sem_count[s] < t}
        u_prod = {p for p, m in PRODUCT_MIN.items() if prod_count[p] < m}
        u_flag = {f for f, m in FLAG_MIN.items() if flag_count[f] < m}
        return u_sem, u_prod, u_flag

    remaining = list(cases)
    while remaining and len(chosen) < N_TARGET:
        u_sem, u_prod, u_flag = unmet()
        best, best_key = None, None
        for i, c in enumerate(remaining):
            s, p, fl = c["final"]["semantic_truth"], c["final"]["product_action"], set(c["flags"])
            score = 0.0
            if s in u_sem:
                score += 100
            score += 12 * len(u_flag & fl)
            if p in u_prod:
                score += 12
            score += 8 * c["agreement_score"]
            score -= 6 * c["novelty_score"]
            score += 2 * c["fidelity_score"]
            kb = c["primary_kb"]
            score += 1.0 / (1 + sum(1 for x in chosen if x["primary_kb"] == kb))
            key = (score, -i)
            if best_key is None or key > best_key:
                best, best_key = i, key
        c = remaining.pop(best)
        chosen.append(c)
        sem_count[c["final"]["semantic_truth"]] += 1
        prod_count[c["final"]["product_action"]] += 1
        flag_count.update(c["flags"])
    return chosen, sem_count, prod_count, flag_count


def main(pool_path):
    data = json.load(open(pool_path))
    cases = []
    for c in data["cases"]:
        fin = c.get("final")
        if not fin:
            continue
        cases.append({
            "case_id": c["case_id"],
            "final": fin,
            "flags": c["final_flags"],
            "agreement_score": 1.0 if c["labels_agree"] else 0.0,
            "novelty_score": c["novelty_max_jaccard"],
            "fidelity_pass": True,  # placeholder, replaced below from fidelity report if present
            "fidelity_score": c.get("fidelity_score", 1.0),
            "primary_kb": c["primary_kb"],
        })
    core, sem, prod, fl = pick(cases)
    core_ids = [c["case_id"] for c in core]
    core_set = set(core_ids)
    reserve_ids = [c["case_id"] for c in cases if c["case_id"] not in core_set]
    report = {
        "core_n": len(core_ids),
        "reserve_n": len(reserve_ids),
        "semantic": dict(sem),
        "product": dict(prod),
        "flags": {f: fl[f] for f in sorted(FLAG_MIN)},
        "constraint_failures": [],
    }
    for s, t in SEM_TARGET.items():
        if sem[s] < SEM_FLOOR[s]:
            report["constraint_failures"].append(f"semantic {s}: {sem[s]} < floor {SEM_FLOOR[s]}")
    for p, m in PRODUCT_MIN.items():
        if prod[p] < m:
            report["constraint_failures"].append(f"product {p}: {prod[p]} < {m}")
    for f, m in FLAG_MIN.items():
        if fl[f] < m:
            report["constraint_failures"].append(f"flag {f}: {fl[f]} < {m}")
    json.dump({"core": core_ids, "reserve": reserve_ids}, open("construction/selection.json", "w"), indent=1)
    print(json.dumps(report, indent=1))
    return 1 if report["constraint_failures"] or len(core_ids) < 140 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
