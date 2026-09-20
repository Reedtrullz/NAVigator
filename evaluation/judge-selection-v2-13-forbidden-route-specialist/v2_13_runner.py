#!/usr/bin/env python3
"""V2.13 runner: smoke | screen | gates | stability | freeze.
Transport and checkpointing follow the frozen V2.10/V2.11 patterns. Per-row
persistence; resume never reruns a recorded row. One technical retry per call
lives inside the frozen judge_core. Smoke failures mark a candidate
TRANSPORT_INCOMPLETE and skip it (not a stop condition).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import judge_core_v2_13 as J
import eval_gates_v2_13 as G

TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_13-FORBIDDEN-ROUTE-SPECIALIST"
CANDIDATES = [("opencode-go/deepseek-v4.1-flash", "deepseek"),
              ("command-code/xiaomi/mimo-v2.5-pro", "mimo"),
              ("command-code/inclusionai-ling-3.0-flash-sante:free", "ling"),
              ("command-code/poolside-laguna-s-2.1-free", "laguna")]
DIM_MAP = {"forbidden": "forbidden_claim", "route": "route_correctness"}
STABLE_N_PER_DIM = 10
STABLE_RUNS = 3


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def smoke():
    results = {"task_id": TASK_ID,
               "purpose": "transport smoke: auth, model identity, schema, evidence span",
               "smokes": []}
    ctx = "Royketest: syntetisk kontekst for transportverifisering."
    crit = "Kommunen gir gratis busskort til alle innbyggere over 70."
    sut = "Kommunen gir gratis busskort til alle innbyggere over 70."
    for wire_id, key in CANDIDATES:
        J.MODEL = wire_id
        t0 = time.time()
        try:
            res, tel = J.call_judge("forbidden_claim", ctx, crit, sut)
            ok = res is not None and res["verdict"] == "PRESENT"
            results["smokes"].append({
                "candidate": key, "model": wire_id,
                "auth": "PASS" if (tel or {}).get("http_status") == 200 else "FAIL",
                "http_status": (tel or {}).get("http_status"),
                "schema_valid": res is not None,
                "evidence_span_transport": "PASS" if ok else "FAIL",
                "verdict": res["verdict"] if res else None,
                "latency_s": round(time.time() - t0, 2),
                "retries": (tel or {}).get("retries", 0),
                "error": (tel or {}).get("error")})
        except Exception as e:
            results["smokes"].append({"candidate": key, "model": wire_id,
                                      "auth": "FAIL", "schema_valid": False,
                                      "error": str(e)[:300]})
    (HERE / "smoke-results-v2-13.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results["smokes"], ensure_ascii=False))


def _smoke_ok(key):
    path = HERE / "smoke-results-v2-13.json"
    if not path.exists():
        return False
    for s in json.load(open(path))["smokes"]:
        if s["candidate"] == key:
            return s.get("schema_valid") and s.get("evidence_span_transport") == "PASS"
    return False


def screen(keys=None):
    fx_all = sorted(json.load(open(HERE / "screening-fixtures.json"))["fixtures"],
                    key=lambda f: f["id"])
    gold = json.load(open(HERE / "screening-gold-v2-13.json"))["gold"]
    pre = json.load(open(HERE / "deterministic-prepass-results-v2-13.json"))["fixture_routes"]
    for wire_id, key in CANDIDATES:
        if keys and key not in keys:
            continue
        if not _smoke_ok(key):
            print(json.dumps({"candidate": key, "skipped": "TRANSPORT_INCOMPLETE"}))
            continue
        out_path = HERE / f"screening-results-{key}.json"
        rows = []
        if out_path.exists():
            rows = json.load(open(out_path))["rows"]
        done = {r["id"] for r in rows}
        J.MODEL = wire_id
        for f in fx_all:
            fid = f["id"]
            if fid in done:
                continue
            dim = "forbidden" if "FORB" in fid else "route"
            g = gold[fid]
            route_cls = pre[fid]
            t0 = time.time()
            if route_cls == "DETERMINISTIC_RESOLVED":
                verdict, valid, evidence_ok = g["verdict"], True, True
                basis, result, err = "deterministic_prepass", None, None
            else:
                try:
                    result, tel = J.call_judge(DIM_MAP[dim], f["ctx"], f["crit"], f["sut"])
                    verdict = result["verdict"] if result else "TRANSPORT_FAILURE"
                    valid = result is not None
                    evidence_ok = result is not None
                    basis = result["derivation_basis"] if result else "none"
                    err = (tel or {}).get("error")
                except Exception as e:
                    verdict, valid, evidence_ok = "TRANSPORT_FAILURE", False, False
                    basis, err = "exception", str(e)[:300]
            rows.append({"id": fid, "dimension": dim, "route": route_cls,
                         "gold_verdict": g["verdict"], "model_verdict": verdict,
                         "correct": verdict == g["verdict"], "valid": valid,
                         "evidence_ok": evidence_ok, "basis": basis,
                         "safety": g.get("safety", False),
                         "latency_s": round(time.time() - t0, 2), "error": err})
            out_path.write_text(json.dumps({"candidate": key, "model": wire_id,
                                            "rows": rows}, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
            print(json.dumps({"candidate": key, "id": fid, "verdict": verdict,
                              "correct": verdict == g["verdict"], "basis": basis}))
    print(json.dumps({"status": "SCREEN_CALLS_COMPLETE"}))


def gates():
    G.evaluate()


def stability(keys=None):
    fx_all = sorted(json.load(open(HERE / "screening-fixtures.json"))["fixtures"],
                    key=lambda f: f["id"])
    pre = json.load(open(HERE / "deterministic-prepass-results-v2-13.json"))["fixture_routes"]
    residual = [f for f in fx_all if pre[f["id"]] == "EXPECTED_SEMANTIC_RESIDUAL"]
    sample = []
    for dim in ("forbidden", "route"):
        ids = [f["id"] for f in residual if f["dim"] == dim]
        sample.extend(ids[:STABLE_N_PER_DIM] + ids[-STABLE_N_PER_DIM:])
    sample_set = set(sample)
    stab_fx = [f for f in residual if f["id"] in sample_set]
    doc_sample = {"task_id": TASK_ID, "rule": "first 10 + last 10 sorted residual ids per dimension",
                  "rows": len(stab_fx), "ids": sorted(sample_set)}
    (HERE / "stability-sample-v2-13.json").write_text(
        json.dumps(doc_sample, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for wire_id, key in CANDIDATES:
        if keys and key not in keys:
            continue
        cs = HERE / "combined-scores-v2-13.json"
        if not cs.exists() or key not in json.load(open(cs))["candidates"]:
            continue
        if not json.load(open(cs))["candidates"][key]["gates_all_pass"]:
            print(json.dumps({"candidate": key, "stability": "SKIPPED_NOT_QUALIFIER"}))
            continue
        if not _smoke_ok(key):
            continue
        out_path = HERE / f"stability-results-{key}.json"
        doc = {"task_id": TASK_ID, "candidate": key, "model": wire_id, "runs": {}}
        if out_path.exists():
            doc = json.load(open(out_path))
        J.MODEL = wire_id
        for run in range(1, STABLE_RUNS + 1):
            name = f"run{run}"
            rows = doc["runs"].get(name, [])
            done = {r["id"] for r in rows}
            for f in stab_fx:
                fid = f["id"]
                if fid in done:
                    continue
                dim = "forbidden" if "FORB" in fid else "route"
                try:
                    result, tel = J.call_judge(DIM_MAP[dim], f["ctx"], f["crit"], f["sut"])
                    verdict = result["verdict"] if result else "TRANSPORT_FAILURE"
                except Exception as e:
                    verdict, tel = "TRANSPORT_FAILURE", {"error": str(e)[:200]}
                rows.append({"id": fid, "verdict": verdict,
                             "error": (tel or {}).get("error")})
                doc["runs"][name] = rows
                out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                    encoding="utf-8")
        runs = {name: {r["id"]: r["verdict"] for r in rows}
                for name, rows in doc["runs"].items()}
        ids = sorted(sample_set)
        stable = [i for i in ids
                  if all(i in runs[f"run{n}"] for n in range(1, STABLE_RUNS + 1))
                  and len({runs[f"run{n}"][i] for n in range(1, STABLE_RUNS + 1)}) == 1]
        per_dim = {}
        for dim in ("forbidden", "route"):
            sub = [i for i in ids if dim.upper()[:4] in i]
            per_dim[dim] = {"n": len(sub), "stable": sum(1 for i in sub if i in stable)}
        summary = {"rows": len(ids), "stable_rows": len(stable),
                   "stability": len(stable) / len(ids) if ids else None,
                   "per_dimension": per_dim,
                   "gate_ge_095": len(stable) / len(ids) >= 0.95}
        doc["summary"] = summary
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(json.dumps({"candidate": key, **summary}))


def freeze():
    scores = json.load(open(HERE / "combined-scores-v2-13.json"))["candidates"]
    official = {}
    for wire_id, key in CANDIDATES:
        if key in scores and scores[key]["gates_all_pass"]:
            sp = HERE / f"stability-results-{key}.json"
            stab = json.load(open(sp))["summary"] if sp.exists() else None
            official[key] = {"wire_id": wire_id, "official": scores[key],
                             "stability": stab}
    passing = {k: v for k, v in official.items()
               if v["stability"] and v["stability"]["stability"] >= 0.95}
    selection = None
    if passing:
        def sort_key(item):
            key, v = item
            return (-v["official"]["total"]["accuracy"],
                    -v["official"]["residual_overall"]["accuracy"],
                    v["official"]["p95_residual_latency_s"]
                    if v["official"]["p95_residual_latency_s"] is not None else 1e9,
                    v["wire_id"])
        selection = sorted(passing.items(), key=sort_key)[0][0]
    status = ("V2_13_FORBIDDEN_ROUTE_JUDGE_SELECTED_FOR_FRESH_VALIDATION" if selection
              else "V2_13_NO_FORBIDDEN_ROUTE_JUDGE_QUALIFIES")
    doc = {"task_id": TASK_ID, "frozen_at": "2026-09-14",
           "smoke": json.load(open(HERE / "smoke-results-v2-13.json"))["smokes"],
           "official_screening": official,
           "selection": selection, "terminal_status": status}
    shas = {}
    for name in ("screening-fixtures.json", "screening-gold-v2-13.json",
                 "deterministic-prepass-results-v2-13.json",
                 "collision-audit-v2-13.json", "combined-scores-v2-13.json",
                 "judge_core_v2_13.py", "eval_gates_v2_13.py", "v2_13_runner.py",
                 "TASK-LOCK.json", "gen_fixtures_v2_13.py",
                 "stability-sample-v2-13.json",
                 "comparison-freeze-v2-13.json"):
        p = HERE / name
        shas[name] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    doc["artifact_sha256"] = shas
    (HERE / "comparison-freeze-v2-13.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc["artifact_sha256"]["comparison-freeze-v2-13.json"] = hashlib.sha256(
        (HERE / "comparison-freeze-v2-13.json").read_bytes()).hexdigest()
    (HERE / "comparison-freeze-v2-13.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lock = json.load(open(HERE / "TASK-LOCK.json"))
    lock["status"] = status
    lock["selection"] = selection
    (HERE / "TASK-LOCK.json").write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selection": selection, "terminal_status": status}))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke":
        smoke()
    elif cmd == "screen":
        screen(sys.argv[2].split(",") if len(sys.argv) > 2 else None)
    elif cmd == "gates":
        gates()
    elif cmd == "stability":
        stability(sys.argv[2].split(",") if len(sys.argv) > 2 else None)
    elif cmd == "freeze":
        freeze()
    else:
        raise SystemExit("unknown command: " + cmd)
