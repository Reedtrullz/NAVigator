#!/usr/bin/env python3
"""Expand case lists -> validate -> novelty -> quota report (audit only)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from author_cases import build_case, AUDIT, SEM_MAP  # noqa: E402
from case_list_a import CASES_A, CASES_A2  # noqa: E402
from case_list_b1 import CASES_B1  # noqa: E402
from case_list_b2 import CASES_B2  # noqa: E402
from case_list_b3 import CASES_B3  # noqa: E402
from construction_tools import check_novelty  # noqa: E402

# Critical/safety/legal-rights preregistration rule (spec 30): a case is
# critical when its evidence packet anchors one of these provisions.
CRITICAL_FACTS = {
    "VOLD_112", "KK_KONTROLL", "KK_SAMTYKKE", "KK_MEDLEMMER",
    "SH_18", "SH_20", "DEP_MAX", "DEP_ANDRE", "PPT_LOV",
    "OS_14B", "OS_GAMMEL",
}


def expand():
    cases, labels, problems = [], {}, []
    n = 0

    def add(track, claim, sem, fact_ids, flags, atoms, critical, rationale):
        nonlocal n
        n += 1
        cid = "RC3G-%04d" % n
        case, out = build_case((cid, track, claim, sem, list(fact_ids),
                                list(flags or []), atoms, critical, rationale))
        if case is None:
            problems.append({"id": cid, "missing_facts": out})
            return
        if isinstance(case, tuple):
            problems.append({"id": cid, "invalid": out})
            return
        cases.append(case)
        labels[cid] = out

    for claim, sem, fids, flags, atoms, critical, rationale in CASES_A + CASES_A2:
        add("A", claim, sem, fids, flags, atoms, critical, rationale)
    for claim, sem, fids, flags, critical, rationale in CASES_B1:
        critical = critical or bool(set(fids) & CRITICAL_FACTS)
        add("B", claim, sem, fids, flags, [], critical, rationale)
    for spec in CASES_B2:
        atoms = [(a[0], a[1], a[2], a[3]) for a in spec["atoms"]]
        # Frozen RC3 aggregation convention (routing.aggregate_atoms):
        # uniform atoms keep their class; any mix -> PARTIALLY_SUPPORTED.
        codes = {a[1] for a in spec["atoms"]}
        if len(codes) == 1:
            worst = codes.pop()
        else:
            worst = "P"
        claim = " og ".join(a[0].rstrip(".") for a in spec["atoms"]) + "."
        critical = spec["critical"] or bool(
            {a[2] for a in spec["atoms"]} & CRITICAL_FACTS)
        add("B", claim, worst, [a[2] for a in spec["atoms"]],
            spec["flags"], atoms, critical, spec["rationale"])
    for spec in CASES_B3:
        atoms = [(a[0], a[1], a[2], a[3]) for a in spec["atoms"]]
        worst = next((x for x in ("C", "P", "I", "S")
                      if any(a[1] == x for a in spec["atoms"])), "S")
        claim = " og ".join(a[0].rstrip(".") for a in spec["atoms"]) + "."
        critical = spec["critical"] or bool(
            {a[2] for a in spec["atoms"]} & CRITICAL_FACTS)
        add("B", claim, worst, [a[2] for a in spec["atoms"]],
            spec["flags"], atoms, critical, spec["rationale"])
    return cases, labels, problems


def quota_report(cases, labels):
    sem, prod, tracks, flags_t = {}, {}, {}, {}
    compounds = genuine_i = critical = 0
    for c in cases:
        lab = labels[c["case_id"]]
        sem[lab["semantic_truth"]] = sem.get(lab["semantic_truth"], 0) + 1
        prod[lab["product_action"]] = prod.get(lab["product_action"], 0) + 1
        tracks[c["track"]] = tracks.get(c["track"], 0) + 1
        if c["compound"]:
            compounds += 1
        if lab["genuine_insufficiency"]:
            genuine_i += 1
        if c["critical"]:
            critical += 1
        for f in c["public_flags"]:
            flags_t[f] = flags_t.get(f, 0) + 1
    atoms_total = sum(len(c.get("atoms", [])) for c in cases)
    return {"n": len(cases), "semantic": sem, "product": prod,
            "tracks": tracks, "compound_cases": compounds,
            "genuine_insufficiency": genuine_i, "critical": critical,
            "flags": flags_t, "atoms_total": atoms_total}


if __name__ == "__main__":
    cases, labels, problems = expand()
    print("cases:", len(cases), "problems:", len(problems))
    for p in problems[:30]:
        print(json.dumps(p, ensure_ascii=False))
    novelty = check_novelty([(c["case_id"], c["claim"]) for c in cases])
    rej = [r for r in novelty if r["verdict"] != "OK"]
    print("novelty rejects:", len(rej))
    for r in rej[:20]:
        print(r)
    rep = quota_report(cases, labels)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    AUDIT.mkdir(exist_ok=True)
    (AUDIT / "cases-pass1.json").write_text(
        json.dumps({"cases": cases, "labels": labels}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    (AUDIT / "novelty-pass1.json").write_text(
        json.dumps(novelty, ensure_ascii=False, indent=1), encoding="utf-8")
    (AUDIT / "quota-pass1.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("audit files written")
