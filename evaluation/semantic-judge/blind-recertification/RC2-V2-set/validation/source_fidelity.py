#!/usr/bin/env python3
"""Source fidelity validator (spec 23-24): every excerpt must appear verbatim in its kb_ref."""
from __future__ import annotations
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]  # repo root

def canon(s: str) -> str:
    return re.sub(r"\s+", " ", s)

def main():
    cand_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    candidates = json.loads(cand_path.read_text())
    if isinstance(candidates, dict):
        candidates = candidates.get("candidates", [])
    cache = {}
    results, failures = [], 0
    for c in candidates:
        ok_all = True
        detail = []
        for s in c.get("sources", []):
            ref = s["kb_ref"]
            if ref not in cache:
                p = ROOT / ref
                cache[ref] = p.read_text() if p.exists() else None
            body = cache[ref]
            found = body is not None and canon(s["text"]) in canon(body)
            ok_all &= found
            detail.append({"source_id": s.get("source_id"), "kb_ref": ref, "verbatim": found,
                           "file_exists": body is not None})
        if not ok_all:
            failures += 1
        results.append({"case_id": c.get("case_id"), "all_verbatim": ok_all, "sources": detail})
    summary = {"candidates": len(results), "fidelity_failures": failures,
               "all_pass": failures == 0}
    print(json.dumps(summary, indent=2))
    if out_path:
        out_path.write_text(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
