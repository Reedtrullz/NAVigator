#!/usr/bin/env python3
"""V2 candidate screening runner (one-shot per candidate).

Frozen contract: screening-contract-v2.json (d4469ecea0ffaeef...).
Architecture verbatim from V1.6B: deterministic pre-resolve -> frozen A3
boundary pre-classifier -> judge candidate (frozen V1.4 core, MODEL swapped
per candidate). 72 fresh fixtures across 3 families; family A and C go
straight to the judge; family B single EXPLICIT_LIMITATION rows derive
deterministically from A3, all other family B rows go to the judge.
One-shot only; no threshold tuning; no best-of-bad.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3"))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
sys.path.insert(0, A3)
sys.path.insert(0, V14)

from boundary_preclassifier import classify  # noqa: E402
import judge_core_v1_4 as J  # noqa: E402

CONTRACT_SHA = "d4469ecea0ffaeef04bbbf8d5aaf32a920aa2b27ec5aa9402b7903fd531c7bcd"
GOLD_SHA = "2b348e9f12603d9890e6ccb642fc245db24fc850e62db1ab91554cfc5ee2c30d"
A3_SHA = "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b"
FAMILIES = [("a", "family-a-fixtures.json"),
            ("b", "family-b-fixtures.json"),
            ("c", "family-c-fixtures.json")]
EXPL_ROWS = {"EXPLICIT_LIMITATION": "SATISFIED", "PARTIAL_LIMITATION": "PARTIAL",
             "HEDGE": "PARTIAL", "CONTRADICTORY_LIMITATION": "PARTIAL",
             "OVERCONFIDENT_ASSERTION": "VIOLATED", "NONE": "UNRESOLVED",
             "UNRESOLVED": "UNRESOLVED"}


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

    assert sha(os.path.join(HERE, "screening-contract-v2.json")) == CONTRACT_SHA
    gdoc = json.load(open(os.path.join(HERE, "judge-selection-gold.json")))
    gold_canon = json.dumps({k: v for k, v in gdoc.items() if k != "gold_sha256"},
                            sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False).encode("utf-8")
    assert hashlib.sha256(gold_canon).hexdigest() == GOLD_SHA
    assert sha(os.path.join(A3, "boundary_preclassifier.py")) == A3_SHA
    gold = {g["fixture_id"]: {"family": g["family"], "dimension": g["dimension"],
                              "verdict": g["verdict"]}
            for g in gdoc["gold"]}
    assert len(gold) == 72

    fxh = json.load(open(os.path.join(HERE, "fixture-hashes.json")))["fixture_hashes"]
    fixtures = []
    for fam, fname in FAMILIES:
        rows = json.load(open(os.path.join(HERE, fname)))["fixtures"]
        assert len(rows) == 24, fname
        for f in rows:
            canon = json.dumps(f, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")
            assert fxh.get(f["id"]) == hashlib.sha256(canon).hexdigest(), f["id"]
            assert gold[f["id"]]["family"] == fam
            fixtures.append(f)

    smoke_path = os.path.join(HERE, "smoke-" + args.candidate + ".json")
    if not os.path.exists(smoke_path):
        J.MODEL = model
        t = J.call_judge("route_correctness",
                         "TEKNISK SMOKE. Ikke en benchmarksak.",
                         "Akseptabel rute: helsesykepleier paa skolen.",
                         "Du kan kontakte helsesykepleier paa skolen din.")
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
        print("SMOKE already recorded:", smoke_path, flush=True)
        return

    J.MODEL = model

    ckpt_path = os.path.join(HERE, "screening-checkpoint-" + args.candidate + ".json")
    rows = []
    if os.path.exists(ckpt_path):
        ck = json.load(open(ckpt_path))
        if ck.get("model") != model:
            raise RuntimeError("checkpoint/model mismatch")
        rows = ck["rows"]
        blocked = [r for r in rows if r["stage"] == "JUDGE"
                   and r.get("status") == "TRANSPORT_FAILURE"]
        if blocked:
            print("RESUME " + args.candidate + ": retrying "
                  + str(len(blocked)) + " transport-failed rows (no semantic "
                  "label was produced; frozen V1.3 resume protocol)", flush=True)
        rows = [r for r in rows if not (r["stage"] == "JUDGE"
                and r.get("status") == "TRANSPORT_FAILURE")]
        print("RESUME " + args.candidate + ": " + str(len(rows))
              + " valid rows loaded", flush=True)
    done = {r["id"] for r in rows}
    judge_calls = 0

    for i, fx in enumerate(fixtures):
        if fx["id"] in done:
            continue
        g = gold[fx["id"]]
        row = {"id": fx["id"], "family": g["family"], "dimension": g["dimension"]}
        if g["family"] in ("a", "c"):
            judge_calls += 1
            row["stage"] = "JUDGE"
            tj = J.call_judge(g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
            row.update(judge_row(tj, fx))
        else:
            mode = fx["mode"]
            cs = fx.get("criterion_struct") or {}
            single_expl = (mode == "EXPLICIT_LIMITATION"
                           and bool(cs.get("required_limitations"))
                           and not bool(cs.get("prohibited_conclusions")))
            if single_expl:
                out = classify(fx["sut"], cs)
                unc = out["uncertainty_behavior"]
                if not unc["abstained"] and unc.get("label") != "ABSTAIN":
                    verdict = EXPL_ROWS[unc["label"]]
                    row.update(stage="A3_DERIVED", a3_unc_label=unc["label"],
                               verdict=verdict,
                               verdict_correct=(verdict == g["verdict"]),
                               derivation="EXPLICIT-mode frozen derive (V1.6B verbatim)")
                else:
                    judge_calls += 1
                    row.update(stage="JUDGE", a3_unc_label="ABSTAIN")
                    tj = J.call_judge(g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                    row.update(judge_row(tj, fx))
            else:
                judge_calls += 1
                row.update(stage="JUDGE", mode=mode)
                tj = J.call_judge(g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
                row.update(judge_row(tj, fx))
        if row["stage"] == "JUDGE" and "verdict" in row:
            row["verdict_correct"] = row["verdict"] == g["verdict"]
        rows.append(row)
        tag = ("OK" if row.get("verdict_correct") else "WRONG"
               if "verdict_correct" in row else row.get("status", row["stage"]))
        print(str(i + 1) + "/72 " + fx["id"] + " [" + row["stage"] + "] "
              + str(tag), flush=True)
        if len(rows) % 12 == 0:
            save(ckpt_path, {"candidate_key": args.candidate, "model": model,
                             "rows": rows})
    save(ckpt_path, {"candidate_key": args.candidate, "model": model, "rows": rows})
    n_judge = sum(1 for r in rows if r["stage"] == "JUDGE")
    print("DONE rows=" + str(len(rows)) + " judge_rows=" + str(n_judge)
          + " judge_calls=" + str(judge_calls), flush=True)


def judge_row(t, fx):
    row = {"status": t.get("status"),
           "telemetry": {k: t.get(k) for k in (
               "finish_reason", "usage", "latency_seconds", "retries", "error")}}
    if t.get("status") == "OK":
        res = t["result"]
        row["result"] = res
        row["verdict"] = res.get("verdict")
        row["evidence_valid"] = all(J.norm(s) in J.norm(fx["sut"])
                                    for s in res.get("evidence_spans", []))
    return row


if __name__ == "__main__":
    main()
