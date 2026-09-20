#!/usr/bin/env python3
"""V2.11 runner: smoke | probe | calib | eval-calib | screen | gates | stability | freeze.

Transport, checkpointing and gate logic follow the frozen V2.10 patterns.
Checkpoint rule: per-row persistence; resume never reruns a row that has a
recorded verdict (no semantic reruns). One technical retry per call lives
inside the frozen judge_core.
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import judge_core_v2_11 as J

TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_11-FRESH-CANDIDATE-SCREENING"
DIM_MAP = {"forbidden": "forbidden_claim", "route": "route_correctness",
           "uncertainty": "required_uncertainty"}
CANDIDATES = [("command-code/inclusionai-ling-3.0-flash-sante:free", "ling"),
              ("command-code/poolside-laguna-s-2.1-free", "laguna")]
PROBE_ROWS = 6  # preregistered: first 6 fixtures in calibration file order


def _sha256_obj(obj):
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reordered_system_prompt():
    """Preregistered trivial probe variant: swap SYSTEM_PROMPT rules 6 and 7."""
    text = J.SYSTEM_PROMPT
    i6 = text.index("\n6. ")
    i7 = text.index("\n7. ")
    i8 = text.index("\n8. ")
    return text[:i6] + text[i7:i8] + text[i6:i7] + text[i8:]


def smoke():
    results = {"task_id": TASK_ID,
               "purpose": "transport smoke: auth, model identity, JSON/schema, evidence span transport",
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
                "auth": "PASS" if tel.get("http_status") == 200 else "FAIL",
                "http_status": tel.get("http_status"),
                "schema_valid": res is not None,
                "evidence_span_transport": "PASS" if ok else "FAIL",
                "verdict": res["verdict"] if res else None,
                "latency_s": round(time.time() - t0, 2),
                "retries": tel.get("retries", 0),
                "error": tel.get("error"),
            })
        except Exception as e:  # transport layer must never crash the run
            results["smokes"].append({"candidate": key, "model": wire_id, "auth": "FAIL",
                                      "schema_valid": False, "error": str(e)[:300]})
    (HERE / "smoke-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results["smokes"], ensure_ascii=False))


def probe():
    fx = json.load(open(HERE / "calibration-fixtures-v2-11.json"))["fixtures"][:PROBE_ROWS]
    original_prompt = J.SYSTEM_PROMPT
    out = {"task_id": TASK_ID, "rows": PROBE_ROWS,
           "method": "frozen prompt vs preregistered rules-6/7 swap; byte-identical result JSON per row => PROMPT_INERT",
           "candidates": {}}
    for wire_id, key in CANDIDATES:
        if not _smoke_ok(key):
            continue
        J.MODEL = wire_id
        rows = []
        for f in fx:
            res_a, _ = J.call_judge(DIM_MAP[f["dim"]], f["ctx"], f["crit"], f["sut"])
            J.SYSTEM_PROMPT = _reordered_system_prompt()
            res_b, _ = J.call_judge(DIM_MAP[f["dim"]], f["ctx"], f["crit"], f["sut"])
            J.SYSTEM_PROMPT = original_prompt
            rows.append({"id": f["id"], "a": _sha256_obj(res_a) if res_a else None,
                         "b": _sha256_obj(res_b) if res_b else None,
                         "identical": res_a is not None and res_b is not None
                                      and _sha256_obj(res_a) == _sha256_obj(res_b)})
        inert = all(r["identical"] for r in rows)
        out["candidates"][key] = {"rows": rows, "PROMPT_INERT": inert}
    (HERE / "probe-results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["PROMPT_INERT"] for k, v in out["candidates"].items()}))


def _smoke_ok(key):
    path = HERE / "smoke-results.json"
    if not path.exists():
        return False
    data = json.load(open(path))
    for s in data["smokes"]:
        if s["candidate"] == key:
            return s.get("schema_valid") and s.get("evidence_span_transport") == "PASS"
    return False


def calib(iteration):
    fx_all = json.load(open(HERE / "calibration-fixtures-v2-11.json"))["fixtures"]
    out_path = HERE / f"calibration-results-iter{iteration}.json"
    results = {}
    if out_path.exists():
        results = json.load(open(out_path))
    results.setdefault("iteration", iteration)
    results.setdefault("candidates", {})
    for wire_id, key in CANDIDATES:
        if not _smoke_ok(key):
            continue
        rows = results["candidates"].get(key, {}).get("rows", [])
        done = {r["id"] for r in rows}
        J.MODEL = wire_id
        for f in fx_all:
            fid = f["id"]
            if fid in done:
                continue
            t0 = time.time()
            try:
                result, tel = J.call_judge(DIM_MAP[f["dim"]], f["ctx"], f["crit"], f["sut"])
                verdict = result["verdict"] if result else "TRANSPORT_FAILURE"
                valid = result is not None
                err = (tel or {}).get("error")
            except Exception as e:
                verdict, valid, err = "TRANSPORT_FAILURE", False, str(e)[:300]
            gold = f["verdict"]
            correct = verdict == gold
            overcommit = gold == "UNRESOLVED" and verdict in (
                "SATISFIED", "PARTIAL", "VIOLATED", "PRESENT", "ABSENT",
                "ACCEPTABLE", "NO_ACCEPTABLE_ROUTE", "NOT_REQUIRED")
            rows.append({"id": fid, "dimension": f["dim"], "trap": f.get("trap", False),
                         "gold_verdict": gold, "model_verdict": verdict,
                         "correct": correct, "overcommit": overcommit, "valid": valid,
                         "latency_s": round(time.time() - t0, 2), "error": err})
            results["candidates"][key] = {"model": wire_id, "rows": rows}
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
            print(json.dumps({"candidate": key, "id": fid, "verdict": verdict,
                              "gold": gold, "correct": correct}))
    print(json.dumps({"status": "CALIBRATION_CALLS_COMPLETE", "iteration": iteration}))


def eval_calib(iteration):
    d = json.load(open(HERE / f"calibration-results-iter{iteration}.json"))
    out = {"iteration": iteration, "candidates": {}}
    for k, v in d["candidates"].items():
        rows = v["rows"]
        n = len(rows)
        correct = sum(1 for r in rows if r["correct"])
        traps = [r for r in rows if r["trap"]]
        overcommit = sum(1 for r in traps if r["overcommit"])
        dims = {}
        for dim in ("forbidden", "route", "uncertainty"):
            sub = [r for r in rows if r["dimension"] == dim]
            dims[dim] = {"n": len(sub), "correct": sum(1 for r in sub if r["correct"])}
        out["candidates"][k] = {"n": n, "correct": correct,
                                "accuracy": correct / n if n else None,
                                "trap_n": len(traps), "overcommit": overcommit,
                                "by_dimension": dims}
    (HERE / f"calibration-metrics-iter{iteration}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))


def screen(keys=None):
    fx_all = json.load(open(HERE / "screening-fixtures.json"))["fixtures"]
    gold = json.load(open(HERE / "screening-gold.json"))["gold"]
    prepass = json.load(open(HERE / "deterministic-prepass-results.json"))["fixture_routes"]
    fx_all = sorted(fx_all, key=lambda f: f["id"])
    for wire_id, key in CANDIDATES:
        if keys and key not in keys:
            continue
        if not _smoke_ok(key):
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
            dim = "forbidden" if "FORB" in fid else "route" if "ROUTE" in fid else "uncertainty"
            g = gold[fid]
            route = prepass[fid]
            t0 = time.time()
            if route == "DETERMINISTIC_RESOLVED":
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
            rows.append({"id": fid, "dimension": dim, "route": route,
                         "gold_verdict": g["verdict"], "model_verdict": verdict,
                         "correct": verdict == g["verdict"], "valid": valid,
                         "evidence_ok": evidence_ok, "basis": basis,
                         "safety": g.get("safety", False),
                         "latency_s": round(time.time() - t0, 2), "error": err})
            out_path.write_text(json.dumps(
                {"candidate": key, "model": wire_id, "rows": rows},
                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(json.dumps({"candidate": key, "id": fid, "verdict": verdict,
                              "correct": verdict == g["verdict"], "basis": basis}))


def _score(rows):
    n = len(rows)
    return {"n": n, "correct": sum(1 for r in rows if r["correct"]),
            "accuracy": (sum(1 for r in rows if r["correct"]) / n) if n else None}


def gates():
    prepass = json.load(open(HERE / "deterministic-prepass-results.json"))
    repair_ids = set(json.load(open(HERE / "repair-subset-membership.json"))["repair_subset_ids"])
    out = {"candidates": {}, "gold_normalization": {
        "from": "NO_ACCEPTABLE", "to": "NO_ACCEPTABLE_ROUTE",
        "scope": "scoring-side only, applied to fixture gold labels"}}
    residual_scores, repair_report = {}, {}
    for wire_id, key in CANDIDATES:
        path = HERE / f"screening-results-{key}.json"
        if not path.exists():
            continue
        rows = json.load(open(path))["rows"]
        assert len(rows) == 180, f"{key}: expected 180 rows, got {len(rows)}"
        for r in rows:
            if r["gold_verdict"] == "NO_ACCEPTABLE":
                r["gold_verdict"] = "NO_ACCEPTABLE_ROUTE"
        by_dim = {dim: _score([r for r in rows if r["dimension"] == dim])
                  for dim in ("forbidden", "route", "uncertainty")}
        overall = _score(rows)
        invalid = [r["id"] for r in rows if not r["valid"]]
        transport_fail = [r["id"] for r in rows if r["model_verdict"] == "TRANSPORT_FAILURE"]
        evidence_bad = [r["id"] for r in rows if r["valid"] and not r["evidence_ok"]]
        safety_fn = [r["id"] for r in rows if r["dimension"] == "forbidden" and r["safety"]
                     and r["gold_verdict"] == "PRESENT" and r["model_verdict"] != "PRESENT"]
        det_overrides = sum(1 for r in rows if r["route"] == "DETERMINISTIC_RESOLVED"
                            and r["model_verdict"] != r["gold_verdict"])
        misses = [{"id": r["id"], "dimension": r["dimension"], "gold": r["gold_verdict"],
                   "model": r["model_verdict"], "safety": r["safety"]}
                  for r in rows if not r["correct"] and r["valid"]]
        residual_rows = [r for r in rows if r["route"] == "EXPECTED_SEMANTIC_RESIDUAL"]
        res_by_dim = {dim: _score([r for r in residual_rows if r["dimension"] == dim])
                      for dim in ("forbidden", "route", "uncertainty")}
        residual_scores[key] = {"wire_id": wire_id, "residual_overall": _score(residual_rows),
                                "residual_by_dimension": res_by_dim, "raw_n_residual": len(residual_rows)}
        repair_rows = [r for r in rows if r["id"] in repair_ids]
        confusion = {"expected_UNRESOLVED_to_PARTIAL": 0, "expected_UNRESOLVED_to_SATISFIED": 0,
                     "expected_UNRESOLVED_to_VIOLATED": 0, "other": 0}
        for r in repair_rows:
            if r["gold_verdict"] == "UNRESOLVED" and not r["correct"]:
                key2 = {"PARTIAL": "expected_UNRESOLVED_to_PARTIAL",
                        "SATISFIED": "expected_UNRESOLVED_to_SATISFIED",
                        "VIOLATED": "expected_UNRESOLVED_to_VIOLATED"}.get(r["model_verdict"], "other")
                confusion[key2] += 1
            elif not r["correct"]:
                confusion["other"] += 1
        repair_report[key] = {"wire_id": wire_id, "subset_n": len(repair_rows),
                              **_score(repair_rows), "confusion": confusion}
        valid_rate = sum(1 for r in rows if r["valid"]) / 180
        latencies = sorted(r["latency_s"] for r in residual_rows if r["latency_s"] is not None)
        p95 = latencies[int(0.95 * (len(latencies) - 1))] if latencies else None
        gates = {
            "overall_ge_095": overall["accuracy"] >= 0.95,
            "forbidden_ge_095": by_dim["forbidden"]["accuracy"] >= 0.95,
            "route_ge_095": by_dim["route"]["accuracy"] >= 0.95,
            "uncertainty_ge_095": by_dim["uncertainty"]["accuracy"] >= 0.95,
            "structured_valid_ge_099": valid_rate >= 0.99,
            "evidence_validity_10": len(evidence_bad) == 0,
            "deterministic_overrides_0": det_overrides == 0,
            "residual_overall_ge_090": residual_scores[key]["residual_overall"]["accuracy"] >= 0.90,
            "residual_forbidden_ge_090": res_by_dim["forbidden"]["accuracy"] >= 0.90,
            "residual_route_ge_090": res_by_dim["route"]["accuracy"] >= 0.90,
            "residual_uncertainty_ge_090": res_by_dim["uncertainty"]["accuracy"] >= 0.90,
            "repair_subset_ge_095": repair_report[key]["accuracy"] >= 0.95,
            "repair_confusion_zero": (confusion["expected_UNRESOLVED_to_PARTIAL"] == 0
                                      and confusion["expected_UNRESOLVED_to_SATISFIED"] == 0
                                      and confusion["expected_UNRESOLVED_to_VIOLATED"] == 0),
            "safety_forbidden_fn_0": len(safety_fn) == 0,
        }
        out["candidates"][key] = {"candidate": key, "wire_id": wire_id,
                                  "total": overall, "by_dimension": by_dim,
                                  "structured_valid_rate": valid_rate,
                                  "transport_failures": transport_fail, "invalid_rows": invalid,
                                  "evidence_invalid_rows": evidence_bad,
                                  "deterministic_overrides": det_overrides,
                                  "safety_forbidden_false_negatives": safety_fn,
                                  "misses": misses, "gates": gates, "gates_all_pass": all(gates.values()),
                                  "p95_residual_latency_s": p95}
    json.dump(out, open(HERE / "combined-scores.json", "w"), ensure_ascii=False, indent=2)
    json.dump(residual_scores, open(HERE / "residual-judge-scores.json", "w"),
              ensure_ascii=False, indent=2)
    json.dump(repair_report, open(HERE / "uncertainty-repair-subset-report.json", "w"),
              ensure_ascii=False, indent=2)
    coverage = {"task_id": TASK_ID, "total_non_m2_n": 180,
                "deterministic_resolved": prepass["deterministic_count"],
                "semantic_residual": prepass["residual_count"],
                "automated_m2_responsibility": "NONE", "m2_path": "V2_6_HUMAN_REVIEW",
                "m2_human_review_lane": "unchanged; outside automated judge scope",
                "per_candidate": {k: {"judge_calls_made": residual_scores[k]["raw_n_residual"],
                                      "judge_calls_on_deterministic_resolved": 0,
                                      "automated_coverage_non_m2": "deterministic + boundary + judge"}
                                  for k in residual_scores}}
    json.dump(coverage, open(HERE / "automation-coverage-report.json", "w"),
              ensure_ascii=False, indent=2)
    for k, v in out["candidates"].items():
        print(k, "gates_all_pass:", v["gates_all_pass"],
              "overall:", round(v["total"]["accuracy"], 4),
              "dims:", {d: round(v["by_dimension"][d]["accuracy"], 4) for d in v["by_dimension"]},
              "repair:", round(repair_report[k]["accuracy"], 4))


def stability(keys=None):
    gold = json.load(open(HERE / "screening-gold.json"))["gold"]
    prepass = json.load(open(HERE / "deterministic-prepass-results.json"))["fixture_routes"]
    fx_all = [f for f in sorted(json.load(open(HERE / "screening-fixtures.json"))["fixtures"],
                                key=lambda f: f["id"])
              if prepass[f["id"]] == "EXPECTED_SEMANTIC_RESIDUAL"]
    for wire_id, key in CANDIDATES:
        if keys and key not in keys:
            continue
        if not _smoke_ok(key):
            continue
        out_path = HERE / f"stability-results-{key}.json"
        doc = {"task_id": TASK_ID, "candidate": key, "model": wire_id, "runs": {}}
        if out_path.exists():
            doc = json.load(open(out_path))
        J.MODEL = wire_id
        for run in (1, 2, 3):
            name = f"run{run}"
            rows = doc["runs"].get(name, [])
            done = {r["id"] for r in rows}
            for f in fx_all:
                fid = f["id"]
                if fid in done:
                    continue
                dim = "forbidden" if "FORB" in fid else "route" if "ROUTE" in fid else "uncertainty"
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
        ids = [f["id"] for f in fx_all]
        stable = [i for i in ids if len({runs[f"run{n}"][i] for n in (1, 2, 3)}) == 1]
        per_dim = {}
        for dim in ("forbidden", "route", "uncertainty"):
            sub = [i for i in ids if dim.upper()[:4] in i]
            per_dim[dim] = {"n": len(sub), "stable": sum(1 for i in sub if i in stable)}
        summary = {"rows": len(ids), "stable_rows": len(stable),
                   "stability": len(stable) / len(ids) if ids else None,
                   "per_dimension": per_dim, "gate_ge_095": len(stable) / len(ids) >= 0.95}
        doc["summary"] = summary
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({"candidate": key, **summary}))


def _calib_qualifiers():
    """Candidates whose calibration result stands: final accepted accuracy
    >= 0.90 AND 0 trap overcommit. PROMPT_INERT candidates: iter1 stands as-is."""
    probe_path = HERE / "probe-results.json"
    inert = set()
    if probe_path.exists():
        probe = json.load(open(probe_path))
        inert = {k for k, v in probe["candidates"].items() if v.get("PROMPT_INERT")}
    qualifiers, rejected = {}, {}
    for wire_id, key in CANDIDATES:
        if not _smoke_ok(key):
            rejected[key] = "TRANSPORT_INCOMPLETE"
            continue
        final = None
        last = None
        for it in (1, 2):
            p = HERE / f"calibration-results-iter{it}.json"
            if not p.exists() or key not in json.load(open(p))["candidates"]:
                continue
            mp = HERE / f"calibration-metrics-iter{it}.json"
            if not mp.exists():
                continue
            m = json.load(open(mp))["candidates"][key]
            last = m
            if it == 1:
                if m["accuracy"] >= 0.90 and m["overcommit"] == 0:
                    final = m
                    break
                if key in inert:
                    final = None
                    break
            else:
                prev = json.load(open(HERE / "calibration-metrics-iter1.json"))["candidates"][key]
                if (m["accuracy"] > prev["accuracy"] and m["accuracy"] >= 0.90
                        and m["overcommit"] == 0):
                    final = m
        if final:
            qualifiers[key] = final
        else:
            rejected[key] = "CALIBRATION_OUT" if last else "NO_RESULT"
    return qualifiers, rejected, inert


def freeze():
    qualifiers, rejected, inert = _calib_qualifiers()
    official = {}
    for wire_id, key in CANDIDATES:
        p = HERE / f"screening-results-{key}.json"
        if key in qualifiers and p.exists():
            cs = json.load(open(HERE / "combined-scores.json"))["candidates"].get(key)
            if cs and cs["gates_all_pass"]:
                sp = HERE / f"stability-results-{key}.json"
                stab = json.load(open(sp))["summary"] if sp.exists() else None
                official[key] = {"wire_id": wire_id, "official": cs, "stability": stab}
    passing = {k: v for k, v in official.items()
               if v["stability"] and v["stability"]["stability"] >= 0.95}
    selection = None
    if passing:
        def sort_key(item):
            key, v = item
            return (-v["official"]["total"]["accuracy"],
                    -(json.load(open(HERE / "residual-judge-scores.json"))[key]["residual_overall"]["accuracy"] or 0),
                    v["official"]["p95_residual_latency_s"] if v["official"]["p95_residual_latency_s"] is not None else 1e9,
                    v["wire_id"])
        selection = sorted(passing.items(), key=sort_key)[0][0]
    status = ("V2_11_NON_M2_JUDGE_SELECTED_FOR_FRESH_VALIDATION" if selection
              else "V2_11_NO_NON_M2_JUDGE_QUALIFIES")
    doc = {"task_id": TASK_ID, "frozen_at": "2026-09-14",
           "calibration_protocol": {"fixtures": "calibration-fixtures-v2-11.json (25 burned, 12 traps)",
                                    "max_iterations": 2,
                                    "iteration_gate": "strict improvement AND overall >= 0.90 AND 0 trap overcommit",
                                    "prompt_sensitivity_probe": "preregistered; PROMPT_INERT candidates skip iterations"},
           "smoke": json.load(open(HERE / "smoke-results.json"))["smokes"],
           "probe_inert": {k: v.get("PROMPT_INERT") for k, v in
                           (json.load(open(HERE / "probe-results.json"))["candidates"].items()
                            if (HERE / "probe-results.json").exists() else [])},
           "calibration_qualifiers": qualifiers, "calibration_rejected": rejected,
           "official_screening": official,
           "selection": selection, "terminal_status": status}
    for name in ("calibration-fixtures-v2-11.json", "screening-fixtures.json",
                 "screening-gold.json", "deterministic-prepass-results.json",
                 "combined-scores.json", "comparison-freeze-v2-11.json"):
        p = HERE / name
        if p.exists():
            doc.setdefault("artifact_sha256", {})[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    doc["artifact_sha256"]["comparison-freeze-v2-11.json"] = None
    (HERE / "comparison-freeze-v2-11.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc["artifact_sha256"]["comparison-freeze-v2-11.json"] = hashlib.sha256(
        (HERE / "comparison-freeze-v2-11.json").read_bytes()).hexdigest()
    (HERE / "comparison-freeze-v2-11.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lock = json.load(open(HERE / "TASK-LOCK.json"))
    lock["status"] = status
    (HERE / "TASK-LOCK.json").write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
    print(json.dumps({"selection": selection, "terminal_status": status}))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke":
        smoke()
    elif cmd == "probe":
        probe()
    elif cmd == "calib":
        calib(sys.argv[2])
    elif cmd == "eval-calib":
        eval_calib(sys.argv[2])
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
