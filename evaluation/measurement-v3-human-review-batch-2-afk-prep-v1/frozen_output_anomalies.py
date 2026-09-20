#!/usr/bin/env python3
# Mechanical diagnostics on frozen Phase 3 outputs. Read-only, deterministic,
# presentation-layer only: no semantic judgment, no scoring, no mutations.
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "full-sut-implementation-phase3", "runs")
REPLAY = ["replay-discovery", "replay-routing", "replay-safety"]
MOJIBAKE = ("\u00c3", "\u00e2\u20ac", "\u00ef\u00bf\u00bd")


def paragraphs(text):
    return [p.strip() for p in text.split(chr(10) + chr(10)) if p.strip()]


def norm(s):
    return " ".join(s.split())


def main():
    cases = []
    para_map = {}
    national_blocks = Counter()
    encoding_cases = []
    no_route_complete = []
    for replay in REPLAY:
        pred_dir = os.path.join(ROOT, replay, "predictions")
        for fn in sorted(os.listdir(pred_dir)):
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(pred_dir, fn), encoding="utf-8") as f:
                d = json.load(f)
            cid = fn[:-5]
            cases.append(cid)
            ans = d.get("answer") or ""
            enc_hits = [m for m in MOJIBAKE if m in ans]
            if enc_hits or "\\n" in ans:
                encoding_cases.append({"case_id": cid, "mojibake": enc_hits,
                                       "literal_backslash_n": "\\n" in ans})
            if bool(d.get("no_route_asserted")) and bool(d.get("presented_as_complete")):
                no_route_complete.append(cid)
            for p in paragraphs(ans):
                key = norm(p)
                para_map.setdefault(key, []).append(cid)
                if key.startswith("Nasjonal informasjon:"):
                    national_blocks[key] += 1
    dup = {k: sorted(set(v)) for k, v in para_map.items() if len(set(v)) > 1}
    dup_pairs = sum(len(v) * (len(v) - 1) // 2 for v in dup.values())
    top_dup = sorted(dup.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]
    top_national = sorted(national_blocks.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    report = {
        "artifact": "frozen-output-mechanical-anomalies",
        "read_only": True,
        "mechanical_only": True,
        "semantic_judgment": "NONE",
        "cases_scanned": len(cases),
        "duplicate_paragraph_groups_across_cases": len(dup),
        "duplicate_paragraph_case_pairs": dup_pairs,
        "top_duplicate_paragraphs": [
            {"cases": v, "preview": k[:120]} for k, v in top_dup
        ],
        "repeated_national_blocks": [
            {"occurrences": n, "preview": k[:120]} for k, n in top_national
        ],
        "encoding_artifact_cases": encoding_cases,
        "no_route_but_presented_complete_cases": no_route_complete,
        "interpretation": "diagnostic presentation-layer observations only; any scoring or repair decision belongs to an authorized downstream task"
    }
    out = os.path.join(HERE, "frozen-output-mechanical-anomalies.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write(chr(10))
    summary = {k: report[k] for k in ("cases_scanned", "duplicate_paragraph_groups_across_cases",
               "duplicate_paragraph_case_pairs", "encoding_artifact_cases",
               "no_route_but_presented_complete_cases")}
    summary["top_repeated_national_blocks"] = [{"occurrences": n} for _, n in top_national[:5]]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
