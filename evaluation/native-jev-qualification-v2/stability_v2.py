#!/usr/bin/env python3
"""Phase 14: cross-run stability of Jev primitives and routing decisions."""
import json, pathlib, sys
from routing_v2 import route

BASE = pathlib.Path(__file__).resolve().parent
suffix = sys.argv[1] if len(sys.argv) > 1 else ""
runs = {n: [json.loads(l) for l in (BASE / f"raw-responses-run{n}{suffix}.jsonl").read_text().splitlines() if l.strip()]
        for n in (1, 2, 3)}

def q(n, cid, key):
    return (runs[n][cid]["answers"].get(key) or {})

out = {"runs_compared": "1v2 (choice/conf) and 1v2v3 (routing)", "n": len(runs[1])}
for key in ("evidence_state", "criterion_semantic_match", "speaker_commitment"):
    same_choice, same_full, probs_l1 = 0, 0, []
    for i in range(len(runs[1])):
        a, b = q(1, i, key), q(2, i, key)
        if a.get("choice") == b.get("choice"):
            same_choice += 1
        if a.get("choice") == b.get("choice") and a.get("confidence") == b.get("confidence"):
            same_full += 1
        for lvl, p in (a.get("probabilities") or {}).items():
            probs_l1.append(abs(p - (b.get("probabilities") or {}).get(lvl, 0.0)))
    out[key] = {"identical_choice_1v2": f"{same_choice}/{len(runs[1])}",
                "identical_choice_and_conf_1v2": f"{same_full}/{len(runs[1])}",
                "mean_prob_l1_delta_1v2": round(sum(probs_l1) / len(probs_l1), 4)}

route_stable = {t: 0 for t in (0.7, 0.8, 0.9)}
route_flips = {t: [] for t in (0.7, 0.8, 0.9)}
for i, row in enumerate(runs[1]):
    for t in route_stable:
        r1, r2, r3 = route(runs[1][i], t), route(runs[2][i], t), route(runs[3][i], t)
        if r1 == r2 == r3:
            route_stable[t] += 1
        else:
            route_flips[t].append({"row": i, "case_id": row["case_id"], "run1": r1, "run2": r2, "run3": r3})
out["routing_stability"] = {f"T={t}": f"{v}/57" for t, v in route_stable.items()}
out["routing_flip_examples"] = {f"T={t}": v[:5] for t, v in route_flips.items() if v}

(BASE / f"stability-results{suffix}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(out, indent=2, ensure_ascii=False))
