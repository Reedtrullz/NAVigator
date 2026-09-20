#!/usr/bin/env python3
"""RC2 compound audit on burned V1 failures (BURNED_BLIND_V1_DEVELOPMENT_ONLY).

Classifies each RC1 semantic failure by comparing the frozen answer-key
atom labels against the RC2 engine's atom_results. Labels are decrypted
in memory and never persisted. Output: compound-audit.md + JSON counts.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RC1SET = os.path.join(ROOT, "evaluation", "semantic-judge",
                      "blind-recertification", "RC1-set")
RC1RUN = os.path.join(ROOT, "evaluation", "semantic-judge",
                      "blind-recertification", "RC1-run")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "engine"))
from run_phase_b_band_analysis import load_labels  # noqa: E402
import polarity_engine_v02 as E2  # noqa: E402


def norm(v):
    return {"INSUFFICIENT_EVIDENCE": "INSUFFICIENT",
            "PARTIALLY_SUPPORTED": "PARTIAL"}.get(v, v)


def classify(lab_atoms, eng_atoms):
    nl, ne = len(lab_atoms), len(eng_atoms)
    if ne == 0:
        return "MISSING_ATOM", "engine produced no atoms"
    if ne < nl:
        return "BAD_DECOMPOSITION", "engine merged %d label atoms into %d" % (
            nl, ne)
    if ne > nl:
        return "WRONG_ATOM_BOUNDARY", "engine split into %d vs %d label atoms" % (
            ne, nl)
    lv = [norm(a["semantic_truth"]) for a in lab_atoms]
    ev = [norm(a["verdict"]) for a in eng_atoms]
    if lv == ev:
        return "AGGREGATION_OR_FUSION", "atoms fully correct, overall wrong"
    # A contradicted engine atom whose label is SUPPORTED is the worst case.
    for l, e in zip(lv, ev):
        if e == "CONTRADICTED" and l in ("SUPPORTED", "INSUFFICIENT"):
            return "ATOM_VERDICT_ERROR", "false-CONTRA atom (label %s)" % l
    if ev.count("SUPPORTED") > lv.count("SUPPORTED"):
        return "ATOM_VERDICT_ERROR", "over-support vs labels"
    return "ATOM_VERDICT_ERROR", "verdict mismatch %s vs %s" % (ev, lv)


def main():
    labels = load_labels()
    preds = json.load(open(os.path.join(RC1RUN, "RC1-predictions.json")))
    rows = preds["predictions"]
    cases = json.load(open(os.path.join(RC1SET, "blind-cases.json")))
    by_id = {c["case_id"]: c for c in cases["core"]}
    counts = Counter()
    detail = []
    for r in rows:
        lab = labels.get(r["case_id"])
        if not lab:
            continue
        if r.get("semantic_verdict") == lab["semantic_truth"]:
            continue  # audit scope: failures only
        lab_atoms = lab.get("atom_labels") or []
        c = by_id[r["case_id"]]
        src = "\n\n".join(s["text"] for s in c["sources"])
        try:
            res = E2.judge_claim(c["claim"], src)
            eng_atoms = [{"verdict": a["verdict"],
                          "text": a.get("atom_text", "")}
                         for a in res.get("atom_results", [])]
        except Exception as ex:
            counts["RUNTIME_ERROR"] += 1
            detail.append({"case_id": r["case_id"], "class": "RUNTIME_ERROR",
                           "error": type(ex).__name__})
            continue
        cls, why = classify(lab_atoms, eng_atoms)
        counts[cls] += 1
        detail.append({"case_id": r["case_id"], "class": cls, "why": why,
                       "label_atoms": lab_atoms, "engine_atoms": eng_atoms})
    out = {"burned_marker": "BURNED_BLIND_V1_DEVELOPMENT_ONLY",
           "failures_audited": len(detail), "counts": dict(counts),
           "detail": detail}
    with open(os.path.join(HERE, "compound-audit.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("failures audited:", len(detail))
    for k, v in counts.most_common():
        print("  %-22s %d" % (k, v))
    for d in detail:
        if d["class"] in ("BAD_DECOMPOSITION", "MISSING_ATOM",
                          "RUNTIME_ERROR"):
            print("  ", d["case_id"], d["class"],
                  d.get("why", d.get("error", "")))


if __name__ == "__main__":
    main()
