#!/usr/bin/env python3
"""Freeze primary A/B review artifacts and build audited residual inputs (sec 16-17)."""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")

_spec = importlib.util.spec_from_file_location(
    "frozen_run_baseline",
    os.path.join(EVAL, "measurement-v3-burned-baseline-v1", "run_baseline.py"))
BASE = importlib.util.module_from_spec(_spec)
sys.modules["frozen_run_baseline"] = BASE
_spec.loader.exec_module(BASE)

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1"
FREEZE_FILES = ["astra-pass-a.jsonl", "astra-pass-b.jsonl",
                "primary-review-validation.json", "primary-consensus.json",
                "residual-inputs.json", "astra-config.json"]


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    consensus = json.load(open(os.path.join(HERE, "primary-consensus.json"),
                               encoding="utf-8"))
    residual_ids = consensus["residual_ids"]

    packets = [json.loads(l) for l in
               open(os.path.join(HERE, "semantic-review-packets.jsonl"),
                    encoding="utf-8") if l.strip()]
    by_id = {p["packet_id"]: p for p in packets}
    batch0 = json.load(open(os.path.join(HERE, "human-review-batch-manifest.json"),
                            encoding="utf-8"))
    meta_by_id = {h["packet_id"]: h for h in batch0["packet_hashes"]}
    residual_packets = [{"packet": by_id[pid],
                         "criterion_id": meta_by_id[pid]["criterion_id"],
                         "case_id": meta_by_id[pid]["case_id"],
                         "dimension": meta_by_id[pid]["dimension"]}
                        for pid in residual_ids]
    base_audit = BASE.leak_audit(residual_packets)

    # Prior-result meta scan over the same three fields as the primary audit.
    prior_meta = ("baseline", "remeasure", "wave-1", "wave1", "astra",
                  "adjudicat", "repair", "rc-01", "rc-02", "rc-03")
    meta_rows, meta_hits = [], 0
    for pid in residual_ids:
        p = by_id[pid]
        content = " ".join(str(p.get(k, "")) for k in
                           ("criterion", "case_context", "sut_output")).lower()
        hits = [t for t in prior_meta if t in content]
        meta_rows.append({"packet_id": pid, "prior_meta_hits": hits})
        meta_hits += bool(hits)

    audit = {
        "artifact": "residual-input-leakage-audit",
        "task_id": TASK_ID,
        "residual_count": len(residual_ids),
        "inputs_source": "frozen semantic-review-packets.jsonl packet bodies only",
        "excluded": ["primary A/B results", "disagreement reasons",
                     "prior Phase-3 Astra results", "old baseline results",
                     "gold outcomes"],
        "base_audit": {"packets_total": base_audit["packets_total"],
                       "packets_valid": base_audit["packets_valid"],
                       "verdict_token_content_hits": base_audit["verdict_token_content_hits"],
                       "forbidden_keys_present": [b for b in base_audit["bad"]]},
        "prior_meta_hits_total": meta_hits,
        "per_packet_meta": meta_rows,
        "pass": (base_audit["packets_valid"] == len(residual_ids)
                 and not base_audit["verdict_token_content_hits"] and meta_hits == 0),
    }

    for name, obj in (("residual-leakage-audit.json", audit),):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")
    if not audit["pass"]:
        raise SystemExit("RESIDUAL_INPUT_LEAKAGE_AUDIT_FAILED")

    files = list(FREEZE_FILES)
    if os.path.exists(os.path.join(HERE, "astra-transport-log.jsonl")):
        files.append("astra-transport-log.jsonl")
    else:
        with open(os.path.join(HERE, "astra-transport-log.jsonl"), "w") as f:
            f.write("")  # explicit empty log: zero transport failures
        files.append("astra-transport-log.jsonl")
    manifest = {
        "artifact": "primary-review-freeze-manifest",
        "task_id": TASK_ID,
        "frozen_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                                  __import__("time").gmtime()),
        "freeze_order": "PRIMARY_REVIEW_FROZEN_BEFORE_RESIDUAL_ADJUDICATION",
        "files": [{"path": fn, "sha256": sha_file(os.path.join(HERE, fn))}
                  for fn in files],
        "residual_ids": residual_ids,
        "counts_at_freeze": {
            "primary_packets": consensus["summary"]["packets_total"],
            "llm_reviewed_consensus": consensus["summary"]["llm_consensus"],
            "residual": len(residual_ids)},
    }
    with open(os.path.join(HERE, "primary-review-freeze-manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"residual": len(residual_ids), "audit_pass": audit["pass"],
                      "frozen_files": len(files)}, indent=1))


if __name__ == "__main__":
    main()
