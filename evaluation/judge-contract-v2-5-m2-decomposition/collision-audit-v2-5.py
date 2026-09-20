#!/usr/bin/env python3
"""Collision audit: V2.5 human boundary fixtures vs burned fixture sets."""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
V25 = BASE / "m2-fixtures-v2-5.json"
BURNED = [
    BASE.parent / "judge-deepseek-v2-4-m2-validation/calibration-fixtures.json",
    BASE.parent / "judge-contract-v2-2-two-mechanism/official-validation-fixtures.json",
]


def norm(s: str) -> list[str]:
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip().split()


def ngrams(tokens: list[str], n: int = 8) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return data["fixtures"] if isinstance(data, dict) else data


def main() -> int:
    v25 = load(V25)
    burned = []
    for path in BURNED:
        for fx in load(path):
            burned.append({"source": path.parent.name, "id": fx["id"], "fx": fx})

    v25_scen = {fx["id"]: norm(fx["ctx"] + " " + fx["sut"]) for fx in v25}
    burned_scen = {b["id"]: norm(b["fx"]["ctx"] + " " + b["fx"]["sut"]) for b in burned}
    v25_grams = {fid: ngrams(t) for fid, t in v25_scen.items()}
    burned_grams = {fid: ngrams(t) for fid, t in burned_scen.items()}

    substring_hits, gram_hits = [], []
    for vid, vtext in v25_scen.items():
        vstr = " ".join(vtext)
        for bid, btext in burned_scen.items():
            bstr = " ".join(btext)
            if len(vstr) and (vstr in bstr or bstr in vstr):
                substring_hits.append({"v25_id": vid, "burned_id": bid})
                continue
            shared = v25_grams[vid] & burned_grams[bid]
            if shared:
                gram_hits.append(
                    {"v25_id": vid, "burned_id": bid, "shared_8grams": sorted(shared)[:3]}
                )

    report = {
        "audit": "v2-5 human boundary fixture collision audit",
        "v25_fixtures": len(v25),
        "burned_fixtures": len(burned),
        "method": "normalized substring either direction + 8-gram overlap on ctx+sut (crit template frame excluded)",
        "substring_hits": substring_hits,
        "gram_hits": gram_hits,
        "result": "PASS" if not substring_hits and not gram_hits else "FAIL",
    }
    out = BASE / "collision-audit-v2-5.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"v25={len(v25)} burned={len(burned)} substr={len(substring_hits)} grams={len(gram_hits)} result={report['result']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
