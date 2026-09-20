#!/usr/bin/env python3
"""DEV-ONLY mechanical novelty checker (spec 20-21).

Reads old benchmark claim texts so the case author never has to.
Prints per-candidate similarity verdicts only; never old claim text.

Pre-registered thresholds (set before candidate authoring):
  EXACT_DUPLICATE        : normalized claim equality (1.0)
  NEAR_DUPLICATE_JACCARD : >= 0.55 (content-token Jaccard)
  NEAR_DUPLICATE_CHAR3   : >= 0.80 (character trigram Dice)
  SKELETON_DUPLICATE     : identical number/date pattern set AND entity-overlap >= 0.50
"""
from __future__ import annotations
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # evaluation/semantic-judge/
CLAIM_KEYS = {"claim", "claims", "claim_text", "claimText", "premise", "statement"}
SKIP_DIRS = {"blind-recertification", "results", "node_modules", "__pycache__"}

THRESH_JACCARD = 0.55
THRESH_CHAR3 = 0.80
THRESH_SKELETON_ENTITY = 0.50

STOP = set("""og eller at som for med til av på i er var har hadde kan skal vil må blir ble ikke ingen uten dersom hvis når man den det dette disse en et ei også bare om fra etter før ved under over mot mellom hos seg sin sine sitt deres vår vår dere du jeg vi han hun de dem dette derfor slik så meget mer mest mindre minst enn noe noen alt alle både hver enten""".split())

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("æ", "ae").replace("ø", "o").replace("å", "aa")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9æøå\s%.,:/-]", " ", s.lower())).strip()

def tokens(s: str):
    return [t for t in re.findall(r"[a-z0-9]+", norm(s)) if t not in STOP]

def char3(s: str):
    s = re.sub(r"\s+", " ", norm(s))
    return {s[i:i+3] for i in range(max(0, len(s)-2))} if len(s) >= 3 else {s}

def numbers(s: str):
    pats = set()
    for m in re.finditer(r"\d+[.,]?\d*\s*%|\d+\s*g(?:\b|(?=[a-zæøå]))|\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d+", s.lower()):
        pats.add(re.sub(r"\s+", "", m.group(0)))
    return pats

def entities(s: str):
    caps = re.findall(r"\b[A-Z][a-zæøå]{2,}\b|\b[A-Z]{2,}\b|\b(?:NAV|Bufetat|Husbanken|Helfo|BUP|HABU|PPT|RPH|HFU|BFT|DPS)\b", s)
    known = ["barnetrygd", "barnebidrag", "bidragsforskudd", "overgangsstonad", "barnetilsyn", "bostotte",
             "sosialhjelp", "depositum", "startlan", "skolehelse", "familievern", "barnevern", "legevakt",
             "trondheimshjelpa", "fastlege", "samtykke", "klage", "frist", "egenandel", "frikort"]
    n = norm(s)
    found = {c.lower() for c in caps} | {k for k in known if k in n}
    return found

def jaccard(a, b):
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if A | B else 0.0

def dice(a, b):
    A, B = set(a), set(b)
    return 2 * len(A & B) / (len(A) + len(B)) if A and B else 0.0

def load_old_claims():
    claims = []
    for p in sorted(ROOT.rglob("*.json")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        stack = [(data, None)]
        seen_ids = set()
        while stack:
            node, hint = stack.pop()
            if isinstance(node, dict):
                cid = node.get("case_id") or node.get("id") or node.get("claim_id") or hint
                for k, v in node.items():
                    if k in CLAIM_KEYS:
                        vals = v if isinstance(v, list) else [v]
                        for v2 in vals:
                            if isinstance(v2, str) and 25 < len(v2) < 1200:
                                key = (str(p), str(cid), v2[:80])
                                if key not in seen_ids:
                                    seen_ids.add(key)
                                    claims.append({"file": str(p.relative_to(ROOT)), "case_id": str(cid), "text": v2})
                    elif isinstance(v, (dict, list)):
                        stack.append((v, cid))
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, (dict, list)):
                        stack.append((item, hint))
    return claims

def main():
    cand_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    candidates = json.loads(cand_path.read_text())
    if isinstance(candidates, dict):
        candidates = candidates.get("candidates", [])
    old = load_old_claims()
    old_norm = [(c, norm(c["text"])) for c in old]
    results = []
    for cand in candidates:
        claim = cand["claim"]
        cn = norm(claim)
        ct = tokens(claim)
        c3 = char3(claim)
        cnum = numbers(claim)
        cent = entities(claim)
        best = {"max_jaccard": 0.0, "max_char3": 0.0, "verdict": "RETAIN", "conflicting_id": None, "reason": None}
        for oc, on in old_norm:
            if cn == on:
                best.update(max_jaccard=1.0, max_char3=1.0, verdict="REJECT_EXACT",
                            conflicting_id=f"{oc['file']}#{oc['case_id']}", reason="exact duplicate")
                break
            j = jaccard(ct, tokens(oc["text"]))
            d = dice(c3, char3(oc["text"]))
            skeleton = bool(cnum and cnum == numbers(oc["text"])) and (jaccard(cent, entities(oc["text"])) >= THRESH_SKELETON_ENTITY)
            if j > best["max_jaccard"]:
                best["max_jaccard"] = j
            if d > best["max_char3"]:
                best["max_char3"] = d
            if best["verdict"] == "RETAIN":
                if j >= THRESH_JACCARD or d >= THRESH_CHAR3:
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
        "max_similarity_retained": max((r["max_jaccard"] for r in results if r["verdict"] == "RETAIN"), default=0.0),
        "thresholds": {"jaccard_near": THRESH_JACCARD, "char3_near": THRESH_CHAR3,
                       "skeleton_entity_overlap": THRESH_SKELETON_ENTITY, "exact": 1.0},
    }
    payload = {"summary": summary, "results": results}
    print(json.dumps(summary, indent=2))
    if out_path:
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
