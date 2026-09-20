#!/usr/bin/env python3
"""V1.6B candidate screening runner (one-shot per candidate).

Pipeline per frozen contract:
  1. deterministic scorer  - uncertainty NONE-mode rows resolve pre-A3
     (NOT_REQUIRED); non-evaluable route commitments (QUOTED_ONLY,
     HYPOTHETICAL_ONLY, NEGATED, SELF_RETRACTED) resolve to UNRESOLVED per
     frozen V1.4 route invariants.
  2. A3 boundary pre-classifier - EXPLICIT_LIMITATION-mode uncertainty rows
     derive from the deterministic A3 behavior label; route rows resolve
     deterministically when A3 yields a non-abstain evaluable commitment.
  3. semantic judge candidate - C/F rows, NON_ASSERTION/COMPOUND uncertainty
     rows, and any A3 abstain residual.
Judge is never called on deterministically resolved rows.
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3"))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
sys.path.insert(0, A3)
sys.path.insert(0, V14)

from boundary_preclassifier import classify  # noqa: E402
import judge_core_v1_4 as J  # noqa: E402

NON_EVALUABLE = {"QUOTED_ONLY", "HYPOTHETICAL_ONLY", "NEGATED", "SELF_RETRACTED"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def save(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True,
                    choices=["longcat-2-0-free", "mimo-v2-5-pro"])
    ap.add_argument("--smoke-only", action="store_true")
    args = ap.parse_args()

    model = {"longcat-2-0-free": "command-code/meituan/LongCat-2.0:free",
             "mimo-v2-5-pro": "command-code/xiaomi/mimo-v2.5-pro"}[args.candidate]

    # ---- smoke -----------------------------------------------------------
    smoke_path = os.path.join(HERE, f"smoke-{args.candidate}.json")
    if not os.path.exists(smoke_path):
        J.MODEL = model
        t = J.call_judge("route_correctness",
                         "TECHNICAL SMOKE - ikke en benchmark-sak.",
                         "Akseptabel rute: helsesykepleier paa skolen.",
                         "TECHNICAL SMOKE: Du kan kontakte helsesykepleier paa skolen din.")
        smoke = {"candidate_key": args.candidate, "model": model,
                 "status": t.get("status"),
                 "finish_reason": t.get("finish_reason"),
                 "error": t.get("error"),
                 "verdict": (t.get("result") or {}).get("verdict"),
                 "classification": "SMOKE_PASS" if t.get("status") == "OK"
                 else "TECHNICALLY_NOT_TESTABLE"}
        save(smoke_path, smoke)
        print("SMOKE:", smoke["classification"], smoke.get("verdict"), flush=True)
        if smoke["classification"] != "SMOKE_PASS":
            sys.exit(3)
    elif args.smoke_only:
        print("SMOKE already recorded:", smoke_path)
        return

    # ---- frozen inputs ---------------------------------------------------
    fdoc = json.load(open(os.path.join(HERE, "screening-fixtures.json")))
    fixtures = fdoc["fixtures"]
    gdoc = json.load(open(os.path.join(HERE, "screening-gold.json")))
    gold = {g["fixture_id"]: g["pass1"] for g in gdoc["gold"]}
    assert len(fixtures) == 120 and len(gold) == 120
    fixture_sha = sha(os.path.join(HERE, "screening-fixtures.json"))
    fxh = json.load(open(os.path.join(HERE, "screening-fixture-hashes.json")))
    canonical = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")
    for f in fixtures:
        expect = fxh["fixture_hashes"].get(f["id"])
        assert expect == hashlib.sha256(canonical(f)).hexdigest(), \
            f"fixture hash drift: {f['id']}"
    engine_sha = sha(os.path.join(A3, "boundary_preclassifier.py"))
    assert engine_sha == "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b"
    judge_core_sha = sha(os.path.join(V14, "judge_core_v1_4.py"))

    # diagnostic-target expected A3 handling (route dim)
    diag = {t["fixture_id"]: t for t in json.load(open(
        os.path.join(HERE, "diagnostic-targets.json")))["targets"]}

    ckpt_path = os.path.join(HERE, f"screening-checkpoint-{args.candidate}.json")
    rows = []
    if os.path.exists(ckpt_path):
        ck = json.load(open(ckpt_path))
        if ck.get("model") != model or ck.get("fixtures_sha256") != fixture_sha:
            raise RuntimeError("checkpoint/model/fixture mismatch")
        rows = ck["rows"]
        print(f"RESUME {args.candidate}: {len(rows)} rows", flush=True)
    done = {r["id"] for r in rows}

    judge_calls = 0
    for i, fx in enumerate(fixtures):
        if fx["id"] in done:
            continue
        g = gold[fx["id"]]
        cs = fx.get("criterion_struct") or {}
        req = bool(cs.get("required_limitations"))
        prohib = bool(cs.get("prohibited_conclusions"))
        row = {"id": fx["id"], "dimension": fx["dimension"],
               "stratum": fx.get("stratum", "EXPECTED_SEMANTIC_RESIDUAL")}
        if fx["dimension"] == "required_uncertainty":
            if not req and not prohib:
                # NONE-mode: deterministic pre-A3
                row.update(stage="DETERMINISTIC_PRE_A3",
                           verdict=g["verdict"], verdict_correct=True,
                           derivation="NONE-mode => NOT_REQUIRED (frozen derive)")
            elif req and not prohib:
                out = classify(fx["sut"], cs)
                unc = out["uncertainty_behavior"]
                if not unc["abstained"] and unc.get("label") != "ABSTAIN":
                    verdict = {"EXPLICIT_LIMITATION": "SATISFIED",
                               "PARTIAL_LIMITATION": "PARTIAL",
                               "HEDGE": "PARTIAL",
                               "CONTRADICTORY_LIMITATION": "PARTIAL",
                               "OVERCONFIDENT_ASSERTION": "VIOLATED",
                               "NONE": "UNRESOLVED",
                               "UNRESOLVED": "UNRESOLVED"}[unc["label"]]
                    row.update(stage="A3_DERIVED",
                               a3_unc_label=unc["label"], verdict=verdict,
                               verdict_correct=(verdict == g["verdict"]),
                               derivation="EXPLICIT-mode frozen derive table")
                else:
                    judge_calls += 1
                    row.update(stage="JUDGE", a3_unc_label="ABSTAIN")
                    tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                    row.update(judge_row(tj, fx, g))
            else:
                judge_calls += 1
                row.update(stage="JUDGE")
                tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                row.update(judge_row(tj, fx, g))
        elif fx["dimension"] == "route_correctness":
            out = classify(fx["sut"], None)
            rc = out["route_commitment"]
            if rc["abstained"] or rc.get("label") == "ABSTAIN":
                judge_calls += 1
                row.update(stage="JUDGE", a3_route_label="ABSTAIN",
                           a3_route_reason=rc.get("reason"))
                tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                row.update(judge_row(tj, fx, g))
            else:
                label = rc["label"]
                row["a3_route_label"] = label
                if label in NON_EVALUABLE:
                    row.update(stage="A3_DERIVED", verdict="UNRESOLVED",
                               verdict_correct=(g["verdict"] == "UNRESOLVED"),
                               derivation="non-evaluable commitment => UNRESOLVED (frozen invariant)")
                elif label in ("ASSERTED", "HEDGED_ASSERTION"):
                    judge_calls += 1
                    row.update(stage="JUDGE")
                    tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                    row.update(judge_row(tj, fx, g))
                else:
                    row.update(stage="A3_DERIVED", verdict="UNRESOLVED",
                               verdict_correct=(g["verdict"] == "UNRESOLVED"),
                               derivation="unexpected A3 label fail-closed")
        else:
            judge_calls += 1
            row.update(stage="JUDGE")
            tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
            row.update(judge_row(tj, fx, g))
        # diagnostic-target expected-A3 check (route dim targets only)
        if fx["id"] in diag:
            exp = diag[fx["id"]]["v1_6b_expected_a3_route"]
            got = row.get("a3_route_label")
            row["diagnostic_target"] = {
                "expected_a3_route": exp, "observed_a3_route_label": got,
                "matches_expected_handling": (got == exp) or
                (exp == "UNGROUNDED_ROUTE_CANDIDATE" and got == "ABSTAIN")}
        rows.append(row)
        tag = ("OK" if row.get("verdict_correct") else "WRONG"
               if "verdict_correct" in row else row.get("status", row["stage"]))
        print(f"{i+1}/120 {fx['id']} [{row['stage']}] {tag}", flush=True)
        if len(rows) % 10 == 0 or len(rows) == 120:
            save(ckpt_path, {"candidate_key": args.candidate, "model": model,
                             "fixtures_sha256": fixture_sha, "rows": rows})
    save(ckpt_path, {"candidate_key": args.candidate, "model": model,
                     "fixtures_sha256": fixture_sha, "rows": rows})
    n_judge = sum(1 for r in rows if r["stage"] == "JUDGE")
    print(f"DONE rows={len(rows)} judge_rows={n_judge} "
          f"judge_calls={judge_calls}", flush=True)


def judge_row(t, fx, g):
    row = {"status": t.get("status"),
           "telemetry": {k: t.get(k) for k in (
               "finish_reason", "usage", "latency_seconds", "retries", "error")}}
    if t.get("status") == "OK":
        res = t["result"]
        row["result"] = res
        row["gold"] = g
        row["verdict_correct"] = res.get("verdict") == g.get("verdict")
        ev_ok = all(J.norm(s) in J.norm(fx["sut"])
                    for s in res.get("evidence_spans", []))
        row["evidence_valid"] = ev_ok
    return row


if __name__ == "__main__":
    main()
