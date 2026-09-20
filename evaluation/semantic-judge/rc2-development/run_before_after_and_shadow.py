#!/usr/bin/env python3
"""RC2 before/after metrics + RC2_BURNED_V1_SHADOW (one pass, frozen).

Engine-layer before/after across all 120 core rows, plus the frozen
fusion policy simulation (RC2_BURNED_V1_SHADOW). Labels are decrypted
in memory only. Development-only; never a certification claim.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "engine"))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "semantic-judge",
                                "hybrid"))
from run_phase_b_band_analysis import load_labels, RC1SET, RC1RUN  # noqa
from fusion import fuse  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
import polarity_engine_v02 as E2  # noqa: E402


def main():
    labels = load_labels()
    preds = json.load(open(os.path.join(RC1RUN,
                                        "RC1-predictions.json")))
    rows = preds["predictions"]
    cases = json.load(open(os.path.join(RC1SET, "blind-cases.json")))
    by = {c["case_id"]: c for c in cases["core"]}

    rc1_eng_ok = rc2_eng_ok = 0
    fixed, regressed = [], []
    rc2_verdicts = {}
    for r in rows:
        cid = r["case_id"]
        lab = labels[cid]
        c = by[cid]
        src = "\n\n".join(s["text"] for s in c["sources"])
        try:
            v = E2.judge_claim(c["claim"], src)["verdict"]
        except Exception:
            v = "RUNTIME_FAILURE"
        rc2_verdicts[cid] = v
        rc1v = (r.get("engine_semantic_verdict")
                or r.get("engine_verdict") or "RUNTIME_FAILURE")
        ok1 = rc1v == lab["semantic_truth"]
        ok2 = v == lab["semantic_truth"]
        rc1_eng_ok += ok1
        rc2_eng_ok += ok2
        if ok2 and not ok1:
            fixed.append(cid)
        if ok1 and not ok2:
            regressed.append(cid)

    # ---- fused-policy shadow simulation (same scorer both sides) ----
    def score(which):
        sem = prod = psafe = autos = false_auto = crit_fa = review = 0
        for r in rows:
            cid = r["case_id"]
            lab = labels[cid]
            ro = r.get("reviewer_output") or {}
            if which == "rc1":
                sem += r.get("semantic_verdict") == lab["semantic_truth"]
                prod += (r.get("product_action") ==
                         lab["product_expected_action"])
                psafe += r.get("proof_safe_verdict") == lab["proof_safe"]
                if r.get("product_action") in ("AUTO_SUPPORTED",
                                               "AUTO_CONTRADICTED"):
                    autos += 1
                    if (r.get("product_action") !=
                            lab["product_expected_action"]):
                        false_auto += 1
                        if lab.get("criticality") in ("HIGH", "CRITICAL"):
                            crit_fa += 1
                continue
            if r.get("runtime_status") != "OK" or not ro.get("verdict"):
                review += 1
                continue
            fsem, fprod, route, _ = fuse(ro.get("verdict"),
                                         ro.get("confidence"),
                                         r.get("gate_reason"))
            if route == "auto":
                autos += 1
                sem += fsem == lab["semantic_truth"]
                prod += fprod == lab["product_expected_action"]
                psafe += "SUPPORTED" == lab["proof_safe"]
                if fprod != lab["product_expected_action"]:
                    false_auto += 1
                    if lab.get("criticality") in ("HIGH", "CRITICAL"):
                        crit_fa += 1
            else:
                review += 1
                mv = {"SUPPORT": "SUPPORTED",
                      "SUPPORTED": "SUPPORTED",
                      "CONTRA": "CONTRADICTED",
                      "CONTRADICTED": "CONTRADICTED"}.get(ro.get("verdict"))
                fsv = mv if mv in ("SUPPORTED",
                                   "CONTRADICTED") else "REVIEW_REQUIRED"
                sem += fsv == lab["semantic_truth"]
                prod += "REVIEW_REQUIRED" == lab["product_expected_action"]
                psafe += "INSUFFICIENT_EVIDENCE" == lab["proof_safe"]
        return {"semantic": sem, "product": prod, "proof_safe": psafe,
                "autos": autos, "false_autos": false_auto,
                "critical_false_autos": crit_fa, "review": review}

    rc1_score = score("rc1")
    rc2_score = score("rc2")
    # Deterministic-path rows (RC1 auto-routed without reviewer output)
    # run through the RC2 engine + auto_gate, as the real pipeline would.
    det_extra = {"auto": 0, "auto_ok": 0, "review": 0}
    for r in rows:
        lab = labels[r["case_id"]]
        ro = r.get("reviewer_output") or {}
        if r.get("runtime_status") != "OK" or ro.get("verdict"):
            continue
        c = by[r["case_id"]]
        src = "\n\n".join(s["text"] for s in c["sources"])
        try:
            res = E2.judge_claim(c["claim"], src)
            reason = auto_gate(c["claim"], src, res)
        except Exception:
            det_extra["review"] += 1
            continue
        # Same asymmetry as the reviewer path: only SUPPORT may auto.
        # CONTRA always routes to review (0176/0178 are false-CONTRA
        # autos under a symmetric policy; spec priority: zero critical
        # false autos).
        if reason is None and res["verdict"] == "SUPPORTED":
            det_extra["auto"] += 1
            prod = "AUTO_SUPPORTED"
            det_extra["auto_ok"] += prod == lab["product_expected_action"]
        else:
            det_extra["review"] += 1
    out = {
        "burned_marker": "BURNED_BLIND_V1_DEVELOPMENT_ONLY",
        "engine_layer": {
            "n": 120,
            "rc1_semantic_correct": rc1_eng_ok,
            "rc2_semantic_correct": rc2_eng_ok,
            "fixed": fixed,
            "regressed": regressed,
        },
        "pipeline_layer": {
            "rc1_official": rc1_score,
            "rc2_fused_shadow": rc2_score,
            "note": "RC2 fused shadow = frozen fusion.py over RC1 "
                    "reviewer output; engine verdicts in rc2 engine "
                    "layer; developer-only numbers.",
        },
        "deterministic_path_extra": dict(det_extra,
            note="RC1 auto-routed rows without reviewer output, re-run "
                 "through RC2 engine + auto_gate."),
        "rc2_engine_verdicts": rc2_verdicts,
    }
    with open(os.path.join(HERE, "before-after-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    shadow = {
        "task_id": "NAV-EXPLORE-RC2-ROOT-CAUSE-REPAIR",
        "run_type": "RC2_BURNED_V1_SHADOW",
        "burned_marker": "BURNED_BLIND_V1_DEVELOPMENT_ONLY",
        "not_certification": True,
        "n": 120,
        "rc2_fused": rc2_score,
        "rc1_baseline": rc1_score,
        "engine_layer": out["engine_layer"],
        "potential_label_sensitivity": {
            "cases": ["RC1B-0116", "RC1B-0165"],
            "note": "Strong POTENTIAL_BLIND_LABEL_ERROR per RC1 phase2 "
                    "label-audit; official labels retained. Under "
                    "official labels both are review-routed product "
                    "misses; under audited PARTIAL labels the fused "
                    "REVIEW_REQUIRED product action is correct.",
        },
    }
    with open(os.path.join(HERE, "burned-v1-shadow-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(shadow, f, ensure_ascii=False, indent=1)
    print("deterministic-path extra:", det_extra)
    print("engine:", rc1_eng_ok, "->", rc2_eng_ok,
          "| fixed", len(fixed), "| regressed", regressed)
    print("RC1:", rc1_score)
    print("RC2 fused shadow:", rc2_score)


if __name__ == "__main__":
    main()
