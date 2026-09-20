#!/usr/bin/env python3
"""Select CORE 160 + reserve deterministically (spec 38 priorities)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from author_cases_main import quota_report  # noqa: E402

NEG_DEONTIC = {"negation", "deontic", "exception", "modality"}
COND = {"condition", "exception"}


def feature_hits(case):
    f = set(case.get("public_flags", []))
    modality = any(x.startswith("modality") for x in f)
    return {
        "neg_deontic": bool(f & NEG_DEONTIC) or modality,
        "condition": bool(f & COND),
        "multi_span": "multi-span" in f,
        "numeric": "numeric" in f,
        "temporal": "temporal" in f,
        "actor": "actor" in f,
        "scope": "scope" in f,
    }


def select():
    data = json.loads((HERE / "construction-audit" / "cases-pass1.json")
                      .read_text(encoding="utf-8"))
    cases, labels = data["cases"], data["labels"]
    need_sem = {"SUPPORTED": 40, "CONTRADICTED": 40,
                "PARTIALLY_SUPPORTED": 40, "INSUFFICIENT_EVIDENCE": 40}
    quotas = {"compound": 52, "neg_deontic": 34, "condition": 32,
              "multi_span": 32, "numeric": 32, "temporal": 32,
              "actor": 32, "scope": 28, "critical": 22,
              "genuine_i": 32}
    ledger = dict(quotas)
    tracks = {"A": 0, "B": 0}
    core, core_ids = [], set()
    pools = {}
    for c in cases:
        pools.setdefault(labels[c["case_id"]]["semantic_truth"], []).append(c)
    for sem in pools:
        pools[sem].sort(key=lambda c: c["case_id"])
    order = ["SUPPORTED", "CONTRADICTED",
             "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
    progress = True
    while len(core) < 160 and progress:
        progress = False
        for sem in order:
            if need_sem[sem] <= 0:
                continue
            best, best_score = None, -1
            for c in pools[sem]:
                if c["case_id"] in core_ids:
                    continue
                lab = labels[c["case_id"]]
                fh = feature_hits(c)
                score = sum(1 for k, on in fh.items()
                            if on and ledger.get(k, 0) > 0)
                if c["compound"] and ledger["compound"] > 0:
                    score += 2
                if c["critical"] and ledger["critical"] > 0:
                    score += 2
                if lab["genuine_insufficiency"] and ledger["genuine_i"] > 0:
                    score += 1
                if score > best_score:
                    best, best_score = c, score
            if best is None:
                continue
            c = best
            lab = labels[c["case_id"]]
            fh = feature_hits(c)
            core.append(c)
            core_ids.add(c["case_id"])
            need_sem[sem] -= 1
            tracks[c["track"]] += 1
            progress = True
            if c["compound"]:
                ledger["compound"] -= 1
            if c["critical"]:
                ledger["critical"] -= 1
            if lab["genuine_insufficiency"]:
                ledger["genuine_i"] -= 1
            for k, on in fh.items():
                if on and ledger.get(k, 0) > 0:
                    ledger[k] -= 1
    reserve = [c for c in cases if c["case_id"] not in core_ids]
    rep = {
        "core_n": len(core), "reserve_n": len(reserve),
        "tracks": tracks, "ledger_remaining": ledger,
        "quota_report_core": quota_report(core, labels),
    }
    (HERE / "construction-audit" / "selection.json").write_text(
        json.dumps({"core_ids": sorted(core_ids),
                    "reserve_ids": sorted(c["case_id"] for c in reserve),
                    "report": rep}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    select()
