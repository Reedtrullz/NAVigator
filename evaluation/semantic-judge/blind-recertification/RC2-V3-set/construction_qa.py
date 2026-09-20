#!/usr/bin/env python3
"""Fail-closed construction QA for RC2 Blind V3.

Every hard gate is evaluated against the selected CORE only. Pool-wide counts
are reported but can never satisfy a gate. Exit 0 only if all hard gates pass.

Input JSON shape:
{
  "candidates": [ {case_id, claim, sources, flags: [...],
                   "pass1": {semantic_truth, proof_safe, product_action},
                   "pass2": {...}, "final": {...} (only if adjudicated)} ],
  "selection": {"core": [ids], "reserve": [ids]},
  "fidelity": {"failures": 0},
  "novelty": {"pass": true}
}
"""
import json
import sys

SEMANTIC = {"SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"}
PROOF = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"}
PRODUCT = {"AUTO_SUPPORTED", "AUTO_CONTRADICTED", "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"}
VALID_FLAGS = {
    "multi_span", "compound", "numeric", "temporal", "actor", "modality",
    "cond_exc", "safety", "legal", "locality", "age_legal",
}

FLAG_MINIMA = {
    "cond_exc": 30, "compound": 50, "multi_span": 30, "numeric": 30,
    "temporal": 30, "actor": 30, "modality": 30, "safety": 20,
    "legal": 30, "locality": 20, "age_legal": 20,
}
PRODUCT_MINIMA = {
    "AUTO_SUPPORTED": 25, "AUTO_CONTRADICTED": 25,
    "REVIEW_REQUIRED": 25, "ABSTAIN_INSUFFICIENT": 25,
}
AGREEMENT_MIN = 0.90
ADJUDICATION_RATE_MAX = 0.35
SLOTS = ("semantic_truth", "proof_safe", "product_action")
SLOT_ENUMS = {"semantic_truth": SEMANTIC, "proof_safe": PROOF, "product_action": PRODUCT}


def final_of(case):
    """Final labels: explicit final block, else pass1 when both passes agree."""
    fin = case.get("final")
    if fin:
        return fin
    p1, p2 = case.get("pass1"), case.get("pass2")
    if not p1 or not p2:
        return None
    return dict(p1) if all(p1[s] == p2[s] for s in SLOTS) else None


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def quota_failures(core, n):
    fails = []
    finals = [final_of(c) for c in core]
    if any(f is None for f in finals):
        return ["CORE quota check blocked: some cases lack final labels (single-pass or unresolved)"]
    sem = [f["semantic_truth"] for f in finals]
    per_class = {s: sem.count(s) for s in SEMANTIC}
    target = n / 4.0
    for s, cnt in per_class.items():
        if cnt < target - 5:
            fails.append(f"semantic class {s}: {cnt} < floor {target - 5:.0f}")
    insuf_min = 30 if n >= 160 else 25
    if per_class["INSUFFICIENT_EVIDENCE"] < insuf_min:
        fails.append(f"genuine insufficiency: {per_class['INSUFFICIENT_EVIDENCE']} < {insuf_min}")
    prod = [f["product_action"] for f in finals]
    for cls, minimum in PRODUCT_MINIMA.items():
        cnt = prod.count(cls)
        if cnt < minimum:
            fails.append(f"product class {cls}: {cnt} < {minimum}")
    flagsets = [set(c.get("flags", [])) for c in core]
    for flag, minimum in FLAG_MINIMA.items():
        cnt = sum(1 for fs in flagsets if flag in fs)
        if cnt < minimum:
            fails.append(f"flag {flag}: {cnt} < {minimum}")
    return fails


def agreement(core):
    """Pre-adjudication exact-match agreement per slot on CORE."""
    out = {}
    for slot in SLOTS:
        same = sum(1 for c in core if c.get("pass1", {}).get(slot) == c.get("pass2", {}).get(slot))
        out[slot] = same / len(core) if core else 0.0
    return out


def completeness_failures(all_cases, core_ids, reserve_ids):
    fails = []
    by_id = {c["case_id"]: c for c in all_cases}
    for cid in core_ids + reserve_ids:
        c = by_id.get(cid)
        if c is None:
            fails.append(f"{cid}: missing from candidates")
            continue
        if not c.get("pass1") or not c.get("pass2"):
            fails.append(f"{cid}: single-pass (double annotation required)")
    return fails


def dispute_failures(core):
    fails = []
    for c in core:
        if not c.get("pass1") or not c.get("pass2"):
            continue
        differs = any(c["pass1"][s] != c["pass2"][s] for s in SLOTS)
        if differs:
            fin = final_of(c)
            if not fin:
                fails.append(f"{c['case_id']}: unresolved dispute (no final labels)")
            else:
                for s in SLOTS:
                    if fin.get(s) not in SLOT_ENUMS[s]:
                        fails.append(f"{c['case_id']}: final {s} missing/invalid")
    return fails


def label_vocabulary_failures(core):
    fails = []
    for c in core:
        for p in ("pass1", "pass2"):
            if p not in c:
                continue
            for s in SLOTS:
                if c[p][s] not in SLOT_ENUMS[s]:
                    fails.append(f"{c['case_id']}: {p}.{s} invalid label {c[p][s]!r}")
    return fails


def run_qa(data):
    fails, info = [], []
    candidates = data["candidates"]
    sel = data["selection"]
    core_ids, reserve_ids = sel["core"], sel["reserve"]
    by_id = {c["case_id"]: c for c in candidates}
    missing = [i for i in core_ids if i not in by_id]
    if missing:
        fails.append(f"core ids missing from candidates: {missing[:5]}")
        return fails, info
    core = [by_id[i] for i in core_ids]
    n = len(core)
    info.append(f"CORE n={n} reserve n={len(reserve_ids)} pool n={len(candidates)}")

    if n < 140:
        fails.append(f"CORE size {n} < 140")
    if n > 0:
        fails += quota_failures(core, n)
        fails += label_vocabulary_failures(core)
        fails += dispute_failures(core)
        agr = agreement(core)
        info.append("pre-adjudication CORE agreement: " + ", ".join(
            f"{s}={agr[s]:.4f}" for s in SLOTS))
        for s in SLOTS:
            if agr[s] < AGREEMENT_MIN:
                fails.append(f"CORE agreement {s}: {agr[s]:.4f} < {AGREEMENT_MIN}")
        adj = sum(1 for c in core
                  if any(c.get("pass1", {}).get(s) != c.get("pass2", {}).get(s) for s in SLOTS))
        rate = adj / n
        info.append(f"adjudication rate: {adj}/{n} = {rate:.4f}")
        if rate > ADJUDICATION_RATE_MAX:
            fails.append(f"adjudication rate {rate:.4f} > {ADJUDICATION_RATE_MAX}")
        for c in core:
            bad = set(c.get("flags", [])) - VALID_FLAGS
            if bad:
                fails.append(f"{c['case_id']}: unknown flags {sorted(bad)}")
    fails += completeness_failures(candidates, core_ids, reserve_ids)
    fid = data.get("fidelity", {})
    if fid.get("failures", 0) != 0:
        fails.append(f"source fidelity failures: {fid['failures']}")
    nov = data.get("novelty", {})
    if not nov.get("pass", False):
        fails.append("novelty check not passed")
    return fails, info


def main():
    if len(sys.argv) != 2:
        print("usage: construction_qa.py <construction.json>", file=sys.stderr)
        return 2
    data = load(sys.argv[1])
    fails, info = run_qa(data)
    for line in info:
        print("INFO ", line)
    pool_sem = {}
    for c in data["candidates"]:
        f = c.get("final")
        if f:
            pool_sem[f["semantic_truth"]] = pool_sem.get(f["semantic_truth"], 0) + 1
    if pool_sem:
        print("INFO  pool semantic distribution (informational, not gate-satisfying):", pool_sem)
    ok = True
    for f in fails:
        print("FAIL ", f)
        ok = False
    if ok:
        print("ALL_HARD_GATES_PASS (CORE-only enforcement)")
        return 0
    print(f"QA_FAILED: {len(fails)} hard gate failure(s); refusing construction completion")
    return 1


if __name__ == "__main__":
    sys.exit(main())
