#!/usr/bin/env python3
"""Lane H interactive adjudication helper: presentation order + blind block display.

Transcription of owner decisions happens in separate append-only JSONL;
this script never invents verdicts.
"""
import json
import sys
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
DATASET = TASK_DIR / "dataset-frozen.jsonl"
ORDER = TASK_DIR / "lane-h-presentation-order.json"
REG = TASK_DIR / "lane-h-registrations.jsonl"


def build_order(rows):
    by_group = {}
    for row in rows:
        if row["safety_critical"]:
            by_group.setdefault(row["scenario_group_id"], []).append(row)
    groups = sorted(by_group)
    assert len(groups) == 30 and all(len(by_group[g]) == 5 for g in groups)
    order = []
    for pos in range(5):
        for group in groups:
            order.append(by_group[group][pos]["row_id"])
    assert len(order) == 150 and len(set(order)) == 150
    lane_ids = {r["row_id"] for r in rows if r["safety_critical"]}
    assert set(order) == lane_ids, "presentation order must cover all safety-critical rows"
    doc = {
        "lane": "H",
        "task_id": "NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1",
        "authorization": "HUMAN GOLD LANE H (attachment e8e2e58c-01d2-44a9-a9c2-ecbba5ecc49c)",
        "rule": ("round-robin: rows grouped by group_id, position 0-4 within group; "
                 "all 30 groups' position-p rows emitted consecutively (groups sorted ascending), "
                 "then position p+1; 15 blocks x 10 rows; "
                 "each group's 5 rows land in 5 different blocks; "
                 "15 blocks x 10 rows covers all 150 Lane H rows"),
        "dataset_sha256": "f3e11e83f03b7ddd9203ffc82be8844dfa32238c39205e08d736c344b6e807a2",
        "blocks": {f"BLOCK-{i + 1}": order[i * 10:(i + 1) * 10]
                   for i in range(15)},
    }
    ORDER.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


def main():
    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    rowmap = {r["row_id"]: r for r in rows}
    doc = json.loads(ORDER.read_text(encoding="utf-8")) if ORDER.exists() else build_order(rows)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    done = set()
    if REG.exists():
        for line in REG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["row_id"])
    if cmd == "status":
        print(json.dumps({"lane_h_rows": 150, "registered": len(done), "pending": 150 - len(done)}))
        return
    if cmd == "block":
        n = int(sys.argv[2])
        block = doc["blocks"][f"BLOCK-{n}"]
        for rid in block:
            r = rowmap[rid]
            print("=====", rid, "|", r["dimension"])
            print("[CASE]", r["packet"]["case_context"])
            print("[CRIT]", r["packet"]["criterion"])
            print("[SUT]", r["packet"]["sut_output"])
        return
    print("unknown command", cmd)


if __name__ == "__main__":
    main()
