#!/usr/bin/env python3
"""Deterministic human-review workbook + scenario-group manifest for Fresh Batch V1.

Blindness: per-row sections contain case_context, criterion and sut_output only.
No family tags, source ids, gold or model metadata in row sections.
"""
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
DATASET = TASK_DIR / "dataset-frozen.jsonl"
CONTRACT = TASK_DIR.parent / "semantic-reviewer-cost-qualification-v1" / "qualification-contract.json"


def main():
    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    si = contract["semantic_instructions"]

    groups = OrderedDict()
    for row in rows:
        gid = row["scenario_group_id"]
        g = groups.setdefault(gid, {
            "scenario_group_id": gid,
            "primary_family": row["primary_family"],
            "safety_critical": bool(row["safety_critical"]),
            "row_ids": [],
        })
        g["row_ids"].append(row["row_id"])
    manifest = {
        "task_id": "NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1",
        "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
        "group_count": len(groups),
        "row_count": len(rows),
        "groups": list(groups.values()),
    }
    (TASK_DIR / "scenario-group-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = []
    w = out.append
    w("# HUMAN REVIEW WORKBOOK - REVIEWER MINIMUM TIER FRESH BATCH V1")
    w("")
    w("Formal: Preparationsartefakt for blind human adjudication av 350 frosne rader (100 scenario-grupper).")
    w("")
    w("Policy: SINGLE_HUMAN_REVIEW. Kun Reidar (eller eksplisitt utpekt menneske) fyller inn verdier.")
    w("AI skal aldri fungere som human reviewer og skal aldri forfylle verdict-feltene.")
    w("")
    w("Arbeidsregel: Les packet -> gjor vurderingen -> velg evidence span -> lagre -> ga videre.")
    w("Ikke sammenlign med tidligere cases. Paastandens sannhet er irrelevant der kontrakten sier det.")
    w("")
    w("Dataset (frozen): dataset-frozen.jsonl sha256 " + manifest["dataset_sha256"])
    w("")
    w("## FROZEN CONTRACT DEFINITIONS (verbatim from qualification-contract.json, semantic_instructions)")
    w("")
    for key in ("forbidden_contract", "critical_contract", "evidence_rule", "enum_domains", "schemas", "system_prompt"):
        w("### " + key)
        w("")
        w("~~~")
        value = si[key]
        w(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2))
        w("~~~")
        w("")
    w("EVIDENCE SPAN RULE: " + si["evidence_rule"])
    w("")
    w("UNRESOLVED er en korrekt terminaltilstand naar kontrakten ikke kan skille trygt; gjett aldri.")
    w("")
    w("---")
    w("")
    for index, row in enumerate(rows, 1):
        pkt = row["packet"]
        w(f"## {index}/{len(rows)} {row['row_id']} [{row['dimension']}]")
        w("")
        w("### A. Case")
        w("")
        w(pkt["case_context"])
        w("")
        w("### B. Criterion")
        w("")
        criterion = pkt["criterion"]
        w(criterion if isinstance(criterion, str) else json.dumps(criterion, ensure_ascii=False))
        w("")
        w("### C. Candidate text (SUT output)")
        w("")
        w("~~~")
        w(pkt["sut_output"])
        w("~~~")
        w("")
        w("verdict:")
        w("")
        w("evidence_spans:")
        w("")
        w("rationale_unclear:")
        w("")
        w("---")
        w("")
    (TASK_DIR / "human-review-workbook.md").write_text("\n".join(out), encoding="utf-8")
    print("groups:", len(groups), "rows:", len(rows))
    print("workbook bytes:", (TASK_DIR / "human-review-workbook.md").stat().st_size)


if __name__ == "__main__":
    main()
