#!/usr/bin/env python3
"""RC2 Phase B: partial-band analysis + labeled development battery.

Band analysis uses the frozen RC1 prediction artifact (reviewer
confidence per routed case) with BURNED_BLIND_V1_DEVELOPMENT_ONLY
labels decrypted in memory (never persisted). The battery reruns the
RC2 candidate engine + auto_gate on the 31 error-anchored cases plus 4
healthy controls and scores semantic/proof-safe/product against the
same labels. No reviewer tuning; results feed fusion-calibration.
"""
import base64
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENGINE = os.path.join(HERE, "engine")
RC1RUN = os.path.join(ROOT, "evaluation", "semantic-judge",
                      "blind-recertification", "RC1-run")
RC1SET = os.path.join(ROOT, "evaluation", "semantic-judge",
                      "blind-recertification", "RC1-set")

BANDS = [("<0.70", 0.0, 0.70), ("0.70-0.77", 0.70, 0.78),
         ("0.78-0.84", 0.78, 0.85), ("0.85-0.89", 0.85, 0.90),
         (">=0.90", 0.90, 1.01)]


def load_labels():
    """Decrypt the sealed burned V1 key in memory. Returns core labels."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    sealed_path = os.environ.get("RC2_KEY_PASSPHRASE")
    secret = None
    if sealed_path and os.path.exists(sealed_path):
        secret = open(sealed_path, encoding="utf-8").read().strip()
    else:
        secret = os.environ.get("RC2_KEY_SECRET")
    if not secret:
        raise SystemExit("RC2 key material missing (env RC2_KEY_SECRET)")
    d = json.loads(open(os.path.join(RC1SET, "answer-key.sealed"),
                        "rb").read())
    nonce = base64.urlsafe_b64decode(d["nonce"] + "==")
    ct = base64.urlsafe_b64decode(d["ciphertext"] + "==")
    key = base64.urlsafe_b64decode(secret + "=" * (-len(secret) % 4))
    ad = hashlib.sha256(open(os.path.join(RC1SET, "blind-cases.json"),
                             "rb").read()).digest()
    data = json.loads(AESGCM(key).decrypt(nonce, ct, ad))
    blind = json.load(open(os.path.join(RC1SET, "blind-cases.json")))
    core_ids = {c["case_id"] for c in blind["core"]}
    return {e["case_id"]: e for e in data
            if e.get("case_id") in core_ids}


def band_of(conf):
    for name, lo, hi in BANDS:
        if lo <= conf < hi:
            return name
    return ">=0.90"


def main():
    labels = load_labels()
    preds = json.load(open(os.path.join(RC1RUN, "RC1-predictions.json")))
    rows = preds.get("rows") or preds.get("predictions")

    # ---------- band analysis on RC1 reviewer-routed rows ----------
    # Counterfactual semantics: for each reviewer-routed row, ask what the
    # outcome would have been if the reviewer verdict were auto-accepted at
    # its confidence. Final RC1 verdicts are kept as the baseline view.
    cf_rows = []
    bands = {name: {"n": 0, "sem_ok": 0, "psafe_ok": 0, "prod_ok": 0,
                    "numeric": 0, "numeric_ok": 0, "critical": 0,
                    "false_support": 0, "false_contra": 0,
                    "cases": []}
             for name, _lo, _hi in BANDS}
    for r in rows:
        ro = r.get("reviewer_output")
        if not isinstance(ro, dict):
            continue
        conf = ro.get("confidence")
        if not isinstance(conf, (int, float)):
            continue
        lab = labels.get(r["case_id"])
        if not lab:
            continue
        cf_rows_entry_marker = None
        b = bands[band_of(conf)]
        b["n"] += 1
        sem_ok = r.get("semantic_verdict") == lab["semantic_truth"]
        psafe_ok = (r.get("proof_safe_verdict") ==
                    lab["proof_safe"])
        prod_ok = (r.get("product_action") ==
                   lab["product_expected_action"])
        rv = ro.get("verdict")
        mapped = {"SUPPORT": "SUPPORTED", "SUPPORTED": "SUPPORTED",
                  "CONTRA": "CONTRADICTED", "CONTRADICTED": "CONTRADICTED",
                  "PARTIAL": "PARTIAL", "PARTIALLY_SUPPORTED": "PARTIAL",
                  "INSUFFICIENT": "PARTIAL"}.get(rv, rv)
        cf_sem_ok = mapped == lab["semantic_truth"]
        cf_prod = ("AUTO_SUPPORTED" if mapped == "SUPPORTED" else
                   "AUTO_CONTRADICTED" if mapped == "CONTRADICTED" else
                   "REVIEW_REQUIRED")
        cf_prod_ok = cf_prod == lab["product_expected_action"]
        eng = r.get("engine_verdict")
        agree_engine = eng == mapped
        b["sem_ok"] += sem_ok
        b["psafe_ok"] += psafe_ok
        b["prod_ok"] += prod_ok
        b["cf_sem_ok"] = b.get("cf_sem_ok", 0) + cf_sem_ok
        b["cf_prod_ok"] = b.get("cf_prod_ok", 0) + cf_prod_ok
        b["agree_engine"] = b.get("agree_engine", 0) + agree_engine
        b["agree_ok"] = b.get("agree_ok", 0) + (agree_engine and cf_sem_ok)
        cf_rows.append({"case_id": r["case_id"], "conf": conf,
                        "reviewer": rv, "mapped": mapped,
                        "engine": eng, "agree": bool(agree_engine),
                        "label": lab["semantic_truth"],
                        "criticality": lab.get("criticality"),
                        "cf_ok": bool(cf_sem_ok),
                        "cf_prod_ok": bool(cf_prod_ok)})
        src = " ".join(s["text"] for s in next(
            c for c in json.load(open(os.path.join(
                RC1SET, "blind-cases.json")))["core"]
            if c["case_id"] == r["case_id"])["sources"])
        import re
        is_num = bool(re.search(
            r"(kr|kroner|prosent|%|maneder|mnd|måned|uker|dager|aar|år)",
            src, re.I))
        b["numeric"] += is_num
        b["numeric_ok"] += (sem_ok and is_num)
        b["critical"] += lab.get("criticality") in ("HIGH", "CRITICAL")
        if r.get("semantic_verdict") == "SUPPORTED" and \
                lab["semantic_truth"] == "CONTRADICTED":
            b["false_support"] += 1
        if r.get("semantic_verdict") == "CONTRADICTED" and \
                lab["semantic_truth"] == "SUPPORTED":
            b["false_contra"] += 1
        if mapped == "SUPPORTED" and lab["semantic_truth"] == "CONTRADICTED":
            b["cf_false_support"] = b.get("cf_false_support", 0) + 1
        if mapped == "CONTRADICTED" and lab["semantic_truth"] == "SUPPORTED":
            b["cf_false_contra"] = b.get("cf_false_contra", 0) + 1
        b["cf_false_support_engine_agree"] = \
            b.get("cf_false_support_engine_agree", 0) + +            (mapped == "SUPPORTED" and lab["semantic_truth"] ==
             "CONTRADICTED" and agree_engine)
        b["cases"].append(r["case_id"])

    # ---------- labeled battery: RC1 baseline vs RC2 candidate ----------
    err_ids = ["RC1B-0001", "RC1B-0004", "RC1B-0005", "RC1B-0009",
               "RC1B-0010", "RC1B-0014", "RC1B-0017", "RC1B-0028",
               "RC1B-0086", "RC1B-0088", "RC1B-0101", "RC1B-0102",
               "RC1B-0111", "RC1B-0112", "RC1B-0117", "RC1B-0120",
               "RC1B-0122", "RC1B-0126", "RC1B-0131", "RC1B-0132",
               "RC1B-0134", "RC1B-0136", "RC1B-0138", "RC1B-0139",
               "RC1B-0140", "RC1B-0143", "RC1B-0144", "RC1B-0145",
               "RC1B-0147", "RC1B-0151", "RC1B-0152", "RC1B-0162",
               "RC1B-0169", "RC1B-0176", "RC1B-0178", "RC1B-0189",
               "RC1B-0192"]
    controls = ["RC1B-0002", "RC1B-0003", "RC1B-0006", "RC1B-0007"]
    battery_ids = err_ids + controls

    # Order matters: ENGINE must win module resolution for quote_aligner,
    # else the frozen RC1 parser shadows the RC2 fix silently.
    sys.path.insert(0, os.path.join(ROOT, "evaluation", "semantic-judge",
                                    "quote-aligner"))
    sys.path.insert(0, os.path.join(ROOT, "evaluation", "semantic-judge",
                                    "hybrid"))
    sys.path.insert(0, ROOT)
    sys.path.insert(0, ENGINE)
    import polarity_engine_v02 as E2
    from auto_gate import auto_gate
    VERDICT_MAP = {"SUPPORTED": "SUPPORTED",
                   "CONTRADICTED": "CONTRADICTED",
                   "PARTIAL": "PARTIALLY_SUPPORTED",
                   "PARTIALLY_SUPPORTED": "PARTIALLY_SUPPORTED",
                   "INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
                   "INSUFFICIENT_EVIDENCE": "INSUFFICIENT_EVIDENCE"}
    blind = json.load(open(os.path.join(RC1SET, "blind-cases.json")))
    by_id = {c["case_id"]: c for c in blind["core"]}
    rc1_by_id = {r["case_id"]: r for r in rows}

    def rc1_scores(cid):
        r = rc1_by_id[cid]
        lab = labels[cid]
        return {"semantic": r.get("semantic_verdict") == lab["semantic_truth"],
                "proof_safe": r.get("proof_safe_verdict") == lab["proof_safe"],
                "product": r.get("product_action") ==
                           lab["product_expected_action"]}

    battery = []
    for cid in battery_ids:
        c = by_id[cid]
        src = "\n\n".join(s["text"] for s in c["sources"])
        lab = labels[cid]
        row = {"case_id": cid, "criticality": lab.get("criticality"),
               "label_semantic": lab["semantic_truth"],
               "label_product": lab["product_expected_action"],
               "rc1": rc1_scores(cid)}
        try:
            res = E2.judge_claim(c["claim"], src)
            reason = auto_gate(c["claim"], src, res)
            if reason is None and res["verdict"] in VERDICT_MAP:
                sem = VERDICT_MAP[res["verdict"]]
                psafe = sem
                prod = ("AUTO_SUPPORTED" if sem == "SUPPORTED" else
                        "AUTO_CONTRADICTED" if sem == "CONTRADICTED"
                        else "REVIEW_REQUIRED")
                route = "auto"
            else:
                sem, psafe, prod, route = ("REVIEW_REQUIRED",
                                           "INSUFFICIENT_EVIDENCE",
                                           "REVIEW_REQUIRED", "review")
            row["rc2"] = {"semantic": sem == lab["semantic_truth"],
                          "proof_safe": psafe == lab["proof_safe"],
                          "product": prod == lab["product_expected_action"],
                          "verdict": res["verdict"], "route": route,
                          "gate_reason": reason}
        except Exception as ex:
            row["rc2"] = {"semantic": False, "proof_safe": False,
                          "product": False, "verdict": "EXCEPTION",
                          "route": "runtime_failure",
                          "error": type(ex).__name__}
        battery.append(row)

    def agg(rows, which):
        return {"n": len(rows),
                "semantic": sum(1 for r in rows if r[which]["semantic"]),
                "proof_safe": sum(1 for r in rows if r[which]["proof_safe"]),
                "product": sum(1 for r in rows if r[which]["product"])}

    out = {"burned_marker": "BURNED_BLIND_V1_DEVELOPMENT_ONLY",
           "bands": bands,
           "battery_ids": battery_ids,
           "battery": battery,
           "cf_rows": cf_rows,
           "rc1_aggregate": agg(battery, "rc1"),
           "rc2_aggregate": agg(battery, "rc2")}
    path = os.path.join(HERE, "phase-b-band-results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("band table:")
    for name, _lo, _hi in BANDS:
        b = bands[name]
        if b["n"]:
            print("  %-8s n=%3d | final sem=%2d prod=%2d | counterfactual "
                  "sem=%2d prod=%2d engAgree=%2d agreeOK=%2d "
                  "cfFSup=%d cfFCon=%d"
                  % (name, b["n"], b["sem_ok"], b["prod_ok"],
                     b.get("cf_sem_ok", 0), b.get("cf_prod_ok", 0),
                     b.get("agree_engine", 0), b.get("agree_ok", 0),
                     b.get("cf_false_support", 0),
                     b.get("cf_false_contra", 0)))
    print("battery RC1:", out["rc1_aggregate"])
    print("battery RC2:", out["rc2_aggregate"])
    fails = [r for r in battery if not all(r["rc2"][k] for k in
                                           ("semantic", "proof_safe",
                                            "product"))]
    print("battery rows not all-correct:", len(fails))
    for r in fails[:12]:
        print("  ", r["case_id"], r["label_product"], "->",
              r["rc2"].get("verdict"), r["rc2"].get("gate_reason"))


if __name__ == "__main__":
    main()
