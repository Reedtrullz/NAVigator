#!/usr/bin/env python3
"""Deterministic routing simulation over raw Jev outputs (Phase 9-10).

Variants differ only in Choice-confidence gates. All thresholds were fixed as
variant definitions before scoring; no variant is tuned to labels afterwards.

Critical lane:
  AUTO-REJECT  evidence_state == CLEAR_TRIGGER_SUPPORT and conf >= T
  AUTO-ACCEPT  evidence_state == CLEAR_NON_TRIGGER_SUPPORT and conf >= T
  ESCALATE     otherwise
Forbidden lane:
  AUTO-REJECT  match == MATCH and commitment == ASSERTED and both conf >= T
  AUTO-ACCEPT  (match == NO_MATCH and conf >= T)
               or (match == MATCH and commitment == NEGATED and both conf >= T)
  ESCALATE     otherwise
False PASS  = AUTO-ACCEPT while frozen gold says the case is wrong/violating.
False FAIL  = AUTO-REJECT while frozen gold says the case is fine/non-violating.
"""
import json, pathlib
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parent

VIOLATING_MATCH = {"MATCH/ASSERTED"}

def gold_violating(exp):
    if exp["lane"] == "critical_condition":
        return exp["critical_evidence_state"] == "CLEAR_TRIGGER_SUPPORT"
    if exp["criterion_semantic_match"] == "UNRESOLVED":
        return False
    if exp["criterion_semantic_match"] == "NO_MATCH":
        return False
    return exp["speaker_commitment"] == "ASSERTED"

def gold_fine(exp):
    if exp["lane"] == "critical_condition":
        return exp["critical_evidence_state"] == "CLEAR_NON_TRIGGER_SUPPORT"
    return not gold_violating(exp) and exp["criterion_semantic_match"] != "UNRESOLVED"

def route(row, t):
    lane, ans, exp = row["lane"], row["answers"], row["expected"]
    def conf(k):
        return (ans.get(k) or {}).get("confidence") or 0.0
    def choice(k):
        return (ans.get(k) or {}).get("choice")
    if lane == "critical_condition":
        c, q = conf("evidence_state"), choice("evidence_state")
        if q == "CLEAR_TRIGGER_SUPPORT" and c >= t:
            return "AUTO_REJECT"
        if q == "CLEAR_NON_TRIGGER_SUPPORT" and c >= t:
            return "AUTO_ACCEPT"
        return "ESCALATE"
    m, mc, s, sc = (choice("criterion_semantic_match"), conf("criterion_semantic_match"),
                    choice("speaker_commitment"), conf("speaker_commitment"))
    if m == "MATCH" and s == "ASSERTED" and min(mc, sc) >= t:
        return "AUTO_REJECT"
    if m == "NO_MATCH" and mc >= t:
        return "AUTO_ACCEPT"
    if m == "MATCH" and s == "NEGATED" and min(mc, sc) >= t:
        return "AUTO_ACCEPT"
    return "ESCALATE"

def evaluate(rows, t):
    out = Counter()
    details = []
    for r in rows:
        if r["error"]:
            out["ERROR"] += 1
            continue
        d = route(r, t)
        out[d] += 1
        if d == "AUTO_ACCEPT" and gold_violating(r["expected"]):
            out["FALSE_PASS"] += 1
            details.append({"case_id": r["case_id"], "kind": "FALSE_PASS"})
        if d == "AUTO_REJECT" and gold_fine(r["expected"]):
            out["FALSE_FAIL"] += 1
            details.append({"case_id": r["case_id"], "kind": "FALSE_FAIL"})
    return {"threshold": t, **dict(out), "events": details}

def main():
    report = {}
    for tag in ("run", "run-v2"):
        for run in (1, 2, 3):
            name = f"raw-responses-run{run}.jsonl" if tag == "run" else f"raw-responses-run{run}-v2.jsonl"
            rows = [json.loads(l) for l in (BASE / name).read_text().splitlines() if l.strip()]
            report[f"{tag}{run}"] = {f"T={t}": evaluate(rows, t) for t in (0.7, 0.8, 0.9)}
    (BASE / "routing-simulation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    for run, variants in report.items():
        print(f"== {run} ==")
        for name, r in variants.items():
            print(name, {k: v for k, v in r.items() if k != "events"})
            for e in r["events"]:
                print("   ", e)

if __name__ == "__main__":
    main()
