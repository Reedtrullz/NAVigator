#!/usr/bin/env python3
"""No-tuning analysis of raw Jev responses: exact-match accuracy, confusion,
high-certainty errors, low-confidence counts. No thresholds are optimized."""
import json, pathlib, sys
from collections import Counter, defaultdict

BASE = pathlib.Path(__file__).resolve().parent
src = BASE / (sys.argv[1] if len(sys.argv) > 1 else "raw-responses-run1.jsonl")
rows = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]

report = {"source": src.name, "n": len(rows), "errors": sum(1 for r in rows if r["error"])}

def acc_conf(rows, qkey, field, expected_key):
    ok, conf, errors = 0, [], []
    conf_mat = defaultdict(Counter)
    for r in rows:
        ans = (r.get("answers") or {}).get(qkey) or {}
        pred = ans.get(field)
        gold = r["expected"][expected_key]
        conf_mat[gold][pred] += 1
        c = ans.get("confidence")
        if c is not None:
            conf.append(c)
        if pred == gold:
            ok += 1
        elif c is not None and c >= 0.8:
            errors.append({"case_id": r["case_id"], "gold": gold, "pred": pred,
                           "confidence": c, "probabilities": ans.get("probabilities")})
    n = sum(sum(c.values()) for c in conf_mat.values())
    return {"n": n, "exact": ok, "accuracy": round(ok / n, 4) if n else None,
            "confusion": {g: dict(p) for g, p in conf_mat.items()},
            "high_confidence_errors_ge08": errors,
            "mean_confidence": round(sum(conf) / len(conf), 3) if conf else None}

crit = [r for r in rows if r["lane"] == "critical_condition" and not r["error"]]
fc = [r for r in rows if r["lane"] == "forbidden_claim" and not r["error"]]

report["critical_condition"] = acc_conf(crit, "evidence_state", "choice", "critical_evidence_state")
f_m = acc_conf(fc, "criterion_semantic_match", "choice", "criterion_semantic_match")
f_c = acc_conf(fc, "speaker_commitment", "choice", "speaker_commitment")
pair_ok = sum(
    1 for r in fc
    if ((r["answers"].get("criterion_semantic_match") or {}).get("choice") == r["expected"]["criterion_semantic_match"]
        and (r["answers"].get("speaker_commitment") or {}).get("choice") == r["expected"]["speaker_commitment"]))
f_pair = {"n": len(fc), "pair_exact": pair_ok, "pair_accuracy": round(pair_ok / len(fc), 4) if fc else None}
report["forbidden_claim"] = {"criterion_semantic_match": f_m, "speaker_commitment": f_c, "pair": f_pair}

out = BASE / (src.stem.replace("raw-responses", "analysis") + ".json")
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(report, indent=2, ensure_ascii=False))
