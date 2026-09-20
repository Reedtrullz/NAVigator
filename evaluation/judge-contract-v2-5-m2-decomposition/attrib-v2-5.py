#!/usr/bin/env python3
"""Offline attribution for V2.5 M2 calibration (no model calls)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
NECESSARY = {
    "clear_trigger": {"trigger_support": "PRESENT"},
    "clear_non_trigger": {"trigger_support": "ABSENT", "non_trigger_support": "PRESENT"},
    "ambiguous_conflicting": {"evidence_conflict": "YES"},
    "insufficient_to_decide": {"evidence_sufficiency": "INSUFFICIENT"},
}


def initials(inter):
    return " ".join(f[0] + ":" + str(inter[f])[0] for f in NECESSARY["clear_trigger"])


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "0"
    path = HERE / ("calibration-results-v2-5-iter%s.partial.json" % suffix)
    runs = json.loads(path.read_text(encoding="utf-8"))["runs"]
    scored = [r for r in runs if r["valid_result"]]
    tags = {}
    for r in scored:
        tags.setdefault(r["tag"], []).append(r)
    print("derived accuracy per tag:")
    for tag in sorted(tags):
        rows = tags[tag]
        ok = sum(r["derived_state_correct"] for r in rows)
        print("  %-22s %2d/%2d" % (tag, ok, len(rows)))
    ok_all = sum(r["derived_state_correct"] for r in scored)
    print("  TOTAL %d/%d = %.4f" % (ok_all, len(scored), ok_all / len(scored)))
    print("field accuracy per necessary field (all scored rows):")
    for f in ("trigger_support", "non_trigger_support", "evidence_conflict", "evidence_sufficiency"):
        gold = {r["id"]: None for r in []}
    # per-field: check necessary field for its tag only, as runner intended
    for tag, need in NECESSARY.items():
        for f, v in need.items():
            rows = [r for r in scored if r["tag"] == tag]
            ok = sum(r["intermediate"][f] == v for r in rows)
            print("  %-22s %s==%s : %2d/%2d" % (tag, f, v, ok, len(rows)))
    print("misses (id | ts/nts/conf/suff | necessary miss | note):")
    for r in scored:
        if r["derived_state_correct"]:
            continue
        i = r["intermediate"]
        sig = " ".join(x[0] + str(i[x])[0] for x in ("trigger_support", "non_trigger_support", "evidence_conflict", "evidence_sufficiency"))
        need = NECESSARY[r["tag"]]
        miss = ",".join(f for f, v in need.items() if i[f] != v)
        print("  %-14s %s | %s | %s" % (r["id"], sig, miss or "-", r["note"]))


if __name__ == "__main__":
    main()
