#!/usr/bin/env python3
"""Mechanical comparison against the AI reference (reading B diagnostic view).

Counts and denominators are always reported. Agreement is reference agreement only;
no accuracy, safety, or minimum-tier claims are derivable from this output.
"""
import json, os, statistics, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)

LABEL = "critical_evidence_state"


def load_rows():
    rows = {}
    for l in open(os.path.join(LANE, "dataset-frozen.jsonl"), encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r["row_id"].startswith("FB1-SCR-"):
                rows[r["row_id"]] = r
    return rows


def load_jsonl(path):
    out = []
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                out.append(json.loads(l))
    return out


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    rows = load_rows()
    props = {json.loads(l)["row_id"]: json.loads(l)
             for l in open(os.path.join(LANE, "lane-h-ai-review-proposals-v1.jsonl"), encoding="utf-8")
             if l.strip()}
    view_b = {rid for rid, p in props.items() if p.get("label_clarification_required") is True}
    results = {}
    for rname in ("MIMO", "DEEPSEEK"):
        recs = load_jsonl(os.path.join(HERE, "results-%s.jsonl" % rname.lower()))
        by_row = {}
        for r in recs:
            cur = by_row.get(r["row_id"])
            if cur is None or (r.get("attempt", 0) >= cur.get("attempt", 0)):
                by_row[r["row_id"]] = r
        results[rname] = by_row

    per_row = []
    for rid in sorted(rows):
        p = props[rid]
        entry = {"row_id": rid,
                 "view": "B" if rid in view_b else "A",
                 "dimension": p.get("dimension"),
                 "review_flags": p.get("review_flags", []),
                 "label_clarification_required": p.get("label_clarification_required", False),
                 "ai_reference": p.get(LABEL),
                 "ai_alternative": (p.get("alternative_critical_evidence_states") or [None])[0],
                 "alternative_status": p.get("alternative_status")}
        for rname in ("MIMO", "DEEPSEEK"):
            rec = results[rname].get(rid)
            if rec is None:
                entry[rname] = {"status": "MISSING"}
            else:
                e = {"status": rec.get("status"),
                     "elapsed_s": rec.get("elapsed_s"),
                     "usage": rec.get("usage", {}),
                     "model_reported": rec.get("model_reported"),
                     "finish_reason": rec.get("finish_reason")}
                if rec.get("status") == "OK":
                    e["label"] = rec["result"].get(LABEL)
                    e["spans"] = rec["result"].get("evidence_spans")
                    e["rationale"] = rec["result"].get("rationale")
                    e["match_reference"] = e["label"] == p.get(LABEL)
                entry[rname] = e
        per_row.append(entry)

    summary = {"artifact": "LANE-H-CHEAP-MODEL-DIAGNOSTIC-V1-COMPARISON",
               "reference_kind": "AI_PROPOSED_REFERENCE (DEVELOPMENT_DIAGNOSTIC_ONLY)",
               "views": {"A": sum(1 for e in per_row if e["view"] == "A"),
                         "B": sum(1 for e in per_row if e["view"] == "B"),
                         "total": len(per_row)}}
    for rname in ("MIMO", "DEEPSEEK"):
        ms = {"planned": len(per_row)}
        ok = [e for e in per_row if e[rname].get("status") == "OK"]
        status_counts = {}
        for e in per_row:
            st = e[rname].get("status", "MISSING")
            status_counts[st] = status_counts.get(st, 0) + 1
        ms["attempted"] = ms["planned"] - status_counts.get("MISSING", 0)
        ms["status_counts"] = status_counts
        ms["completed_valid"] = len(ok)
        ms["evidence_valid_mechanical"] = len(ok)
        match = [e for e in ok if e[rname]["match_reference"]]
        for scope, subset in (("full", per_row), ("A", [e for e in per_row if e["view"] == "A"]),
                              ("B", [e for e in per_row if e["view"] == "B"])):
            n_ok = sum(1 for e in subset if e[rname].get("status") == "OK")
            n_match = sum(1 for e in subset if e[rname].get("status") == "OK" and e[rname]["match_reference"])
            ms.setdefault("views", {})[scope] = {
                "planned": len(subset),
                "completed_valid": n_ok,
                "exact_label_match": n_match,
                "exact_label_match_over_planned": round(n_match / len(subset), 4) if subset else None,
                "exact_label_match_over_completed": round(n_match / n_ok, 4) if n_ok else None}
        conf = {}
        for e in ok:
            ref = e["ai_reference"]
            lab = e[rname]["label"]
            conf.setdefault(ref, {}).setdefault(lab, 0)
            conf[ref][lab] += 1
        ms["confusion_reference_x_model"] = conf
        lat = sorted(e[rname]["elapsed_s"] for e in ok if e[rname].get("elapsed_s") is not None)
        if lat:
            ms["latency"] = {"n": len(lat), "median_s": statistics.median(lat),
                             "p95_s": lat[int(0.95 * (len(lat) - 1))], "max_s": max(lat)}
        usage = {"prompt_tokens": sum(e[rname].get("usage", {}).get("prompt_tokens") or 0 for e in ok),
                 "completion_tokens": sum(e[rname].get("usage", {}).get("completion_tokens") or 0 for e in ok),
                 "total_tokens": sum(e[rname].get("usage", {}).get("total_tokens") or 0 for e in ok)}
        ms["usage_totals_valid_rows"] = usage
        ms["cost_basis"] = "included local-proxy access; observed billing UNKNOWN (not $0)"
        summary[rname] = ms

    both = [e for e in per_row if e["MIMO"].get("status") == "OK" and e["DEEPSEEK"].get("status") == "OK"]
    paired = {"both_eligible": len(both),
              "both_match_reference": sum(1 for e in both if e["MIMO"]["match_reference"] and e["DEEPSEEK"]["match_reference"]),
              "only_mimo_matches": sum(1 for e in both if e["MIMO"]["match_reference"] and not e["DEEPSEEK"]["match_reference"]),
              "only_deepseek_matches": sum(1 for e in both if e["DEEPSEEK"]["match_reference"] and not e["MIMO"]["match_reference"]),
              "both_deviate_same_label": sum(1 for e in both if not e["MIMO"]["match_reference"] and not e["DEEPSEEK"]["match_reference"] and e["MIMO"]["label"] == e["DEEPSEEK"]["label"]),
              "both_deviate_different_labels": sum(1 for e in both if not e["MIMO"]["match_reference"] and not e["DEEPSEEK"]["match_reference"] and e["MIMO"]["label"] != e["DEEPSEEK"]["label"]),
              "missing_or_invalid_any": len(per_row) - len(both)}
    summary["paired"] = paired

    b_view = [e for e in per_row if e["view"] == "B" and e["MIMO"].get("status") == "OK" and e["DEEPSEEK"].get("status") == "OK"]
    summary["view_B_paired_hits"] = {
        "both_eligible": len(b_view),
        "mimo_proposed_hit": sum(1 for e in b_view if e["MIMO"]["label"] == e["ai_reference"]),
        "mimo_alternative_hit": sum(1 for e in b_view if e["MIMO"]["label"] == e["ai_alternative"]),
        "mimo_other": sum(1 for e in b_view if e["MIMO"]["label"] not in (e["ai_reference"], e["ai_alternative"])),
        "deepseek_proposed_hit": sum(1 for e in b_view if e["DEEPSEEK"]["label"] == e["ai_reference"]),
        "deepseek_alternative_hit": sum(1 for e in b_view if e["DEEPSEEK"]["label"] == e["ai_alternative"]),
        "deepseek_other": sum(1 for e in b_view if e["DEEPSEEK"]["label"] not in (e["ai_reference"], e["ai_alternative"])),
        "note": "alternative hit is reported separately and is not counted as extra correct"}

    with open(os.path.join(HERE, "per-row-comparison.jsonl"), "w", encoding="utf-8") as f:
        for e in per_row:
            f.write(json.dumps(e, ensure_ascii=False) + chr(10))
    with open(os.path.join(HERE, "analysis-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    dis = []
    for e in per_row:
        m_ok = e["MIMO"].get("status") == "OK"
        d_ok = e["DEEPSEEK"].get("status") == "OK"
        m_dev = m_ok and not e["MIMO"]["match_reference"]
        d_dev = d_ok and not e["DEEPSEEK"]["match_reference"]
        if m_dev or d_dev:
            dis.append({k: e[k] for k in ("row_id", "view", "dimension", "review_flags",
                                          "label_clarification_required", "ai_reference",
                                          "ai_alternative", "alternative_status",
                                          "MIMO", "DEEPSEEK")})
    with open(os.path.join(HERE, "disagreements-vs-ai-reference.jsonl"), "w", encoding="utf-8") as f:
        for e in dis:
            f.write(json.dumps(e, ensure_ascii=False) + chr(10))

    print("per-row:", len(per_row), "disagreement file rows:", len(dis))
    print("summary:", json.dumps({k: summary[k] for k in ("views", "paired")}, ensure_ascii=False))
    print("sha256 analysis-summary:", sha_file(os.path.join(HERE, "analysis-summary.json")))
    print("sha256 per-row-comparison:", sha_file(os.path.join(HERE, "per-row-comparison.jsonl")))
    print("sha256 disagreements:", sha_file(os.path.join(HERE, "disagreements-vs-ai-reference.jsonl")))


if __name__ == "__main__":
    main()
