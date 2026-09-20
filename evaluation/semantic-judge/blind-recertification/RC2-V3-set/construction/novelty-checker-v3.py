#!/usr/bin/env python3
"""V3 novelty: same thresholds as V2 checker, plus the V2 blind corpus as prior art."""
import json
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V2DIR = HERE.parent.parent / "RC2-V2-set"
_spec = importlib.util.spec_from_file_location("novelty_checker_v2", V2DIR / "novelty-checker.py")
nc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nc)


def main():
    cand_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    candidates = json.loads(cand_path.read_text())
    if isinstance(candidates, dict):
        candidates = candidates.get("candidates") or candidates.get("cases") or []
    old = nc.load_old_claims()
    v2_blind = 0
    blind = json.loads((V2DIR / "blind-cases.json").read_text())
    for c in blind.get("cases", blind if isinstance(blind, list) else []):
        claim = c.get("claim")
        if isinstance(claim, str):
            old.append({"file": "RC2-V2-set/blind-cases.json", "case_id": c.get("case_id"),
                        "text": claim, "v2_blind": True})
            v2_blind += 1
    old_norm = [(c, nc.norm(c["text"])) for c in old]
    results = []
    for cand in candidates:
        claim = cand["claim"]
        cn, ct, c3 = nc.norm(claim), nc.tokens(claim), nc.char3(claim)
        cnum, cent = nc.numbers(claim), nc.entities(claim)
        allow_v2_overlap = cand.get("provenance") == "V2_REUSED_UNSEEN_BY_RC2"
        best = {"max_jaccard": 0.0, "max_char3": 0.0, "verdict": "RETAIN", "conflicting_id": None, "reason": None}
        for oc, on in old_norm:
            if allow_v2_overlap and oc.get("v2_blind"):
                continue
            if cn == on:
                best.update(max_jaccard=1.0, max_char3=1.0, verdict="REJECT_EXACT",
                            conflicting_id=f"{oc['file']}#{oc['case_id']}", reason="exact duplicate")
                break
            j = nc.jaccard(ct, nc.tokens(oc["text"]))
            d = nc.dice(c3, nc.char3(oc["text"]))
            skeleton = bool(cnum and cnum == nc.numbers(oc["text"])) and (nc.jaccard(cent, nc.entities(oc["text"])) >= nc.THRESH_SKELETON_ENTITY)
            if j > best["max_jaccard"]:
                best["max_jaccard"] = j
            if d > best["max_char3"]:
                best["max_char3"] = d
            if best["verdict"] == "RETAIN":
                if j >= nc.THRESH_JACCARD or d >= nc.THRESH_CHAR3:
                    best.update(verdict="REJECT_NEAR", conflicting_id=f"{oc['file']}#{oc['case_id']}",
                                reason=f"jaccard={j:.2f},char3={d:.2f}")
                elif skeleton:
                    best.update(verdict="REJECT_SKELETON", conflicting_id=f"{oc['file']}#{oc['case_id']}",
                                reason="same number/date pattern + entity overlap")
        results.append({"case_id": cand.get("case_id"), "verdict": best["verdict"],
                        "max_jaccard": round(best["max_jaccard"], 4),
                        "max_char3": round(best["max_char3"], 4),
                        "conflicting_old_id": best["conflicting_id"], "reason": best["reason"]})
    summary = {
        "candidates": len(results),
        "rejected_exact": sum(r["verdict"] == "REJECT_EXACT" for r in results),
        "rejected_near": sum(r["verdict"] == "REJECT_NEAR" for r in results),
        "rejected_skeleton": sum(r["verdict"] == "REJECT_SKELETON" for r in results),
        "retained": sum(r["verdict"] == "RETAIN" for r in results),
        "max_similarity_retained": round(max((r["max_jaccard"] for r in results if r["verdict"] == "RETAIN"), default=0.0), 4),
        "thresholds": {"jaccard_near": nc.THRESH_JACCARD, "char3_near": nc.THRESH_CHAR3,
                       "skeleton_entity_overlap": nc.THRESH_SKELETON_ENTITY, "exact": 1.0},
        "excluded_prior_art": {
            "corpus": "RC2-V2-set/blind-cases.json",
            "condition": "candidate provenance == V2_REUSED_UNSEEN_BY_RC2 (spec 29: V2 overlap is expected for reused-but-never-executed cases; RC2 execution verified absent)",
            "v2_blind_entries": v2_blind,
        },
        "corpus_note": "repo scan + RC2-V2-set/blind-cases.json (pre-registered prior art)",
    }
    print(json.dumps(summary, indent=2))
    if out_path:
        out_path.write_text(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False))
    sys.exit(0 if summary["rejected_exact"] + summary["rejected_near"] + summary["rejected_skeleton"] == 0 else 1)


if __name__ == "__main__":
    main()
