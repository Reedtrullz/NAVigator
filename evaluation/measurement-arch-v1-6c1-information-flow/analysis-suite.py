#!/usr/bin/env python3
"""Deterministic V1.6C.1 analysis artifacts.

Inputs (frozen):
  ab-evaluation-set.json
  screening-fixtures.json  (historical V1.6B dir, read-only)
  new-flow-results.json
  dev-corpus-semantic-judge-v1-6b/screening-checkpoint-mimo-v2-5-pro.json
  dev-corpus-semantic-judge-v1-6b/v1_6a3_classifier.py  (imported for packet payload)

Outputs (additive, this dir only):
  old-flow-results.json, failure-cluster-report.json,
  information-attribution.json, token-latency-report.json,
  complexity-report.json
"""
import json, sys, time, importlib.util, hashlib, statistics, os
from pathlib import Path

HERE = Path(__file__).parent
V6B = HERE.parent / "dev-corpus-semantic-judge-v1-6b"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V6B))

CRIT = "critical_condition"; FORB = "forbidden_claim"
ROUTE = "route_correctness"; UNC = "required_uncertainty"
DIMS = (CRIT, FORB, ROUTE, UNC)
SAFETY_CONDITIONS = ("selvmord", "suicid", "selvskading", "livstruende", "akutt")


def load_all():
    ev = json.loads((HERE / "ab-evaluation-set.json").read_text())
    ck = json.loads((V6B / "screening-checkpoint-mimo-v2-5-pro.json").read_text())
    old = {r["id"]: r for r in ck["rows"]}
    new = json.loads((HERE / "new-flow-results.json").read_text())
    new = {r["id"]: r for r in new["rows"]}
    fx = {x["id"]: x for x in
          json.loads((V6B / "screening-fixtures.json").read_text())["fixtures"]}
    return ev, old, new, fx


def old_valid(r):
    return r.get("status") == "OK" and r.get("verdict_correct") is not None


def extract_old_flow(ev, old):
    rows = []
    for er in ev["rows"]:
        r = old[er["id"]]
        rows.append({
            "id": er["id"], "dimension": er["dimension"],
            "gold_verdict": er["gold_verdict"],
            "verdict": r["result"]["verdict"] if old_valid(r) else None,
            "verdict_correct": r.get("verdict_correct"),
            "evidence_valid": r.get("evidence_valid"),
            "status": r.get("status"),
            "telemetry": {k: r.get("telemetry", {}).get(k)
                          for k in ("usage", "latency_seconds", "retries", "finish_reason")},
        })
    n = len(rows)
    valid = sum(1 for r in rows if r["verdict"] is not None)
    correct = sum(1 for r in rows if r["verdict_correct"] is True)
    doc = {"artifact": "old-flow-results.json (extracted from frozen V1.6B checkpoint)",
           "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
           "source_checkpoint_sha256": hashlib.sha256(
               (V6B / "screening-checkpoint-mimo-v2-5-pro.json").read_bytes()).hexdigest(),
           "n_rows": n, "n_valid": valid, "n_correct": correct,
           "overall_accuracy": round(correct / n, 4),
           "per_dimension": {d: {"n": sum(1 for r in rows if r["dimension"] == d),
                                 "correct": sum(1 for r in rows if r["dimension"] == d and r["verdict_correct"] is True)}
                             for d in DIMS},
           "rows": rows}
    (HERE / "old-flow-results.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc


def a3_payload(fx_row):
    """Re-run classifier to get packet payload identical to NEW arm (deterministic)."""
    from packet_builder import build_packet
    p = build_packet(fx_row["dimension"], fx_row["crit"], fx_row["sut"], fx_row.get("ctx", ""))
    keys = ["clause_spans", "route_candidates", "quote_spans", "negation_spans",
            "retraction_spans", "hedge_spans", "assertion_spans",
            "conditional_spans", "attribution_spans", "vague_spans",
            "deterministic_evidence", "a3"]
    return {k: p[k] for k in keys if p.get(k)}


def cluster_of(dim, fx_row, old_v, new_v, gold):
    """Generalized failure cluster from fixture semantics + verdicts."""
    sut = (fx_row.get("sut", "") or "").lower()
    crit = (fx_row.get("crit", "") or "").lower()
    tags = []
    if new_v != gold and old_v == gold:
        tags.append("NEW_REGRESSION")
    if old_v != gold and new_v == gold:
        tags.append("NEW_REPAIR")
    if old_v != gold and new_v != gold:
        tags.append("UNCHANGED_FAILURE")
    # semantic family markers
    if ("sitert" in crit or "quote" in crit
            or any(q in fx_row.get("crit", "") for q in ('"', "«", "»"))):
        tags.append("QUOTE_CENTERED")
    if any(w in sut for w in ("ikke", "mangler", "finnes ikke", "tilbyr ikke")):
        tags.append("NEGATION_PRESENT_IN_SUT")
    if any(w in sut for w in ("kan", "kanskje", "mulig", "sannsynligvis", "vurder")):
        tags.append("HEDGED_SUT")
    if dim == ROUTE and len(a3_route_candidates(fx_row)) > 1:
        tags.append("MULTI_ROUTE")
    if dim == UNC:
        tags.append("UNCERTAINTY_DIMENSION")
    if dim == CRIT and any(s in crit for s in SAFETY_CONDITIONS):
        tags.append("SAFETY_CRITICAL")
    return tags


def a3_route_candidates(fx_row):
    try:
        p = a3_payload(fx_row)
        return p.get("route_candidates", [])
    except Exception:
        return []


def failure_clusters(ev, old, new, fx):
    clusters = []
    for er in ev["rows"]:
        rid = er["id"]
        ov = old[rid].get("verdict_correct")
        nv = new[rid].get("verdict_correct") if new[rid].get("status") == "OK" else None
        if ov is True and nv is True:
            continue  # cluster report focuses on failures
        clusters.append({
            "id": rid, "dimension": er["dimension"],
            "gold": er["gold_verdict"],
            "old_verdict": old[rid].get("result", {}).get("verdict") if old_valid(old[rid]) else None,
            "new_verdict": new[rid].get("verdict"),
            "clusters": cluster_of(er["dimension"], fx[rid],
                                   old[rid].get("result", {}).get("verdict"),
                                   new[rid].get("verdict"), er["gold_verdict"]),
        })
    # aggregate
    agg = {}
    for c in clusters:
        for tag in c["clusters"]:
            agg.setdefault(tag, []).append(c["id"])
    doc = {"artifact": "failure-cluster-report.json",
           "n_failure_rows": len(clusters),
           "aggregate_clusters": {k: {"n": len(v), "ids": v} for k, v in sorted(agg.items())},
           "rows": clusters}
    (HERE / "failure-cluster-report.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc


def information_attribution(ev, old, new, fx):
    """Which packet fields accompany wrong->right vs right->wrong."""
    attrib = {"wrong_to_right": [], "right_to_wrong": [], "unchanged_wrong": []}
    for er in ev["rows"]:
        rid = er["id"]
        ov = old[rid].get("verdict_correct")
        nv = new[rid].get("verdict_correct") if new[rid].get("status") == "OK" else None
        payload = a3_payload(fx[rid])
        field_presence = {k: bool(v) for k, v in payload.items() if k != "a3"}
        entry = {"id": rid, "dimension": er["dimension"],
                 "packet_field_presence": field_presence,
                 "a3_verdict": payload.get("a3", {}).get("verdict") if isinstance(payload.get("a3"), dict) else payload.get("a3"),
                 "route_candidate_count": len(payload.get("route_candidates", [])),
                 "negation_span_count": len(payload.get("negation_spans", [])),
                 "quote_span_count": len(payload.get("quote_spans", []))}
        if ov is False and nv is True:
            attrib["wrong_to_right"].append(entry)
        elif ov is True and nv is False:
            attrib["right_to_wrong"].append(entry)
        elif ov is False and nv is False:
            attrib["unchanged_wrong"].append(entry)
    # field association rates
    def rate(group, field):
        g = attrib[group]
        return {"n": len(g), "n_with": sum(1 for e in g if e["packet_field_presence"].get(field)),
                "rate": round(sum(1 for e in g if e["packet_field_presence"].get(field)) / len(g), 4) if g else None}
    fields = ["clause_spans", "route_candidates", "quote_spans", "negation_spans",
              "retraction_spans", "hedge_spans", "assertion_spans",
              "conditional_spans", "attribution_spans", "vague_spans",
              "deterministic_evidence"]
    summary = {g: {f: rate(g, f) for f in fields} for g in attrib}
    doc = {"artifact": "information-attribution.json",
           "note": "A3 classifier payload re-run is deterministic (same SHA-bound classifier); field presence only, no payload dump.",
           "summary_field_association": summary,
           "rows": attrib}
    (HERE / "information-attribution.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc


def tokens_of(t):
    u = (t or {}).get("usage") or {}
    return u.get("total_tokens") or u.get("prompt_tokens", 0) + u.get("completion_tokens", 0)


def token_latency(ev, old, new):
    def stats(vals):
        if not vals:
            return {"n": 0}
        s = sorted(vals)
        return {"n": len(vals), "median": round(statistics.median(vals), 2),
                "p95": round(s[min(len(s) - 1, int(0.95 * len(s)))], 2),
                "mean": round(sum(vals) / len(vals), 2)}
    old_lat, new_lat, old_tok, new_tok = [], [], [], []
    for er in ev["rows"]:
        rid = er["id"]
        if old_valid(old[rid]):
            lt = (old[rid].get("telemetry") or {}).get("latency_seconds")
            tt = tokens_of(old[rid].get("telemetry"))
            if lt: old_lat.append(lt)
            if tt: old_tok.append(tt)
        nr = new[rid]
        if nr.get("status") == "OK":
            lt = (nr.get("telemetry") or {}).get("latency_seconds")
            tt = tokens_of(nr.get("telemetry"))
            if lt: new_lat.append(lt)
            if tt: new_tok.append(tt)
    def overhead(o, n):
        if not o or not n:
            return None
        return {"old_median": round(statistics.median(o), 2), "new_median": round(statistics.median(n), 2),
                "median_overhead": round(statistics.median(n) - statistics.median(o), 2),
                "median_overhead_pct": round((statistics.median(n) / statistics.median(o) - 1) * 100, 1) if statistics.median(o) else None}
    doc = {"artifact": "token-latency-report.json",
           "tokens": {"old": stats(old_tok), "new": stats(new_tok),
                      "overhead": overhead(old_tok, new_tok)},
           "latency_seconds": {"old": stats(old_lat), "new": stats(new_lat),
                               "overhead": overhead(old_lat, new_lat)}}
    (HERE / "token-latency-report.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc


def complexity_report():
    """Cyclomatic-ish complexity of packet_builder (branch/function counts)."""
    import ast
    src = (HERE / "packet_builder.py").read_text()
    tree = ast.parse(src)
    n_fn = sum(isinstance(x, ast.FunctionDef) for x in ast.walk(tree))
    n_branch = sum(isinstance(x, (ast.If, ast.For, ast.While, ast.IfExp)) for x in ast.walk(tree))
    n_try = sum(isinstance(x, ast.ExceptHandler) for x in ast.walk(tree))
    loc = len([l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")])
    doc = {"artifact": "complexity-report.json",
           "packet_builder": {"loc": loc, "functions": n_fn, "branches": n_branch,
                              "except_handlers": n_try,
                              "external_dependencies": 0,
                              "notes": "Deterministic stdlib-only builder; single public entry build_packet; a3 SHA drift assert fail-closed."}}
    (HERE / "complexity-report.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc


def main():
    ev, old, new, fx = load_all()
    done = sum(1 for er in ev["rows"] if new[er["id"]].get("status") in ("OK", "ERROR", "TRANSPORT_CAPACITY_FAILURE"))
    if done < len(ev["rows"]):
        print(f"RUN INCOMPLETE: {done}/{len(ev['rows'])} rows terminal; refusing analysis")
        sys.exit(1)
    t0 = time.time()
    old_doc = extract_old_flow(ev, old)
    print("old-flow extracted:", old_doc["n_correct"], "/", old_doc["n_rows"])
    fc = failure_clusters(ev, old, new, fx)
    print("failure clusters:", fc["n_failure_rows"], "rows;", len(fc["aggregate_clusters"]), "tags")
    ia = information_attribution(ev, old, new, fx)
    print("attribution: w2r", len(ia["rows"]["wrong_to_right"]), "r2w", len(ia["rows"]["right_to_wrong"]))
    print("token/latency:", json.dumps(token_latency(ev, old, new)["latency_seconds"]["overhead"]))
    print("complexity:", json.dumps(complexity_report()["packet_builder"]))
    print(f"analysis-suite complete in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
