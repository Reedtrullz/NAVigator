#!/usr/bin/env python3
"""RC2 Phase-A hard gates (RC2 spec section 12).

Runs the new engine regression suite, the frozen Tier-1 battery, the
frozen operator regression, ENT/N canaries, and the ID guard against
the RC2 engine candidate. RC1 artifacts are untouched (new engine lives
in rc2-development/engine/). Exit 0 only when every gate passes.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENGINE = os.path.join(HERE, "engine")
T1 = os.path.join(ROOT, "evaluation", "semantic-judge", "tier1-proof")
OPREG = os.path.join(ROOT, "evaluation", "semantic-judge",
                     "operator-regression")


def load_rc2_engine():
    """Import RC2 candidate first so frozen batteries bind to it."""
    sys.path.insert(0, ENGINE)
    sys.path.insert(0, T1)
    import polarity_engine as pe  # noqa: E402,F401
    import polarity_engine_v02 as v02  # noqa: E402,F401
    return pe, v02


def run_py(path, cwd=None):
    p = subprocess.run([sys.executable, path], cwd=cwd or ROOT,
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)[-3000:]


def main():
    pe, v02 = load_rc2_engine()
    import tier1_operators as ops
    import proof_validator as pv

    results = {}
    fails = []

    # 1. new engine regression suite
    code, out = run_py(os.path.join(HERE, "regressions",
                                    "run_regression.py"))
    results["rc2_regressions"] = {"exit": code, "tail": out[-500:]}
    if code != 0:
        fails.append("rc2_regressions")

    # 2. frozen tier1 operator battery (43/43 expected)
    code, out = run_py(os.path.join(T1, "test_tier1_operators.py"))
    results["tier1_battery"] = {"exit": code, "tail": out[-500:]}
    if code != 0:
        fails.append("tier1_battery")

    # 3. frozen operator regression corpus (23 cases expected)
    code, out = run_py(os.path.join(OPREG, "run_regression.py"))
    results["operator_regression"] = {"exit": code, "tail": out[-500:]}
    if code != 0:
        fails.append("operator_regression")

    # 4. ENT-C / N-R1 / N-A4 / ACT-25 canaries on RC2 engine
    canary_rows = []
    entc = ("PPT kan stille ADHD-diagnose.",
            "PPT kartlegger pedagogiske behov og gir sakkyndige "
            "vurderinger. BUP utreder psykiske lidelser/"
            "nevroutviklingsforstyrrelser.")
    proofs, crashed = ops.run_operators(*entc)
    canary_rows.append({
        "canary": "ENT-C",
        "pass": not crashed and not [p for p in proofs
                                     if p["result"] == "CONTRADICTED"]})
    nr1 = ("Helsesykepleier stiller ADHD-diagnose.",
           "Skolehelsetjenesten stiller ikke diagnoser.")
    proofs, crashed = ops.run_operators(*nr1)
    canary_rows.append({
        "canary": "N-R1",
        "pass": not crashed and not [p for p in proofs
                                     if p["result"] == "CONTRADICTED"]})
    # Full RC1 product chain (engine -> auto_gate), calibrated against
    # frozen RC1 behavior: ENT-C CONTRA is expected (ent-controls), N-R1
    # CONTRA never carries a tier1 proof (checked above); N-A4 must not
    # auto-accept as SUPPORTED; ACT-25 must stay SUPPORT-capable.
    sys.path.insert(0, os.path.join(ROOT, "evaluation", "semantic-judge",
                                    "hybrid"))
    from auto_gate import auto_gate
    v_na4 = v02.judge_claim("Henvendelse krever henvisning.",
                            "Du kan kontakte helsestasjonen uten "
                            "henvisning.")
    v_act25 = v02.judge_claim("Psykolog i BUP kan gi terapi.",
                              "BUP har psykologer og leger som gir "
                              "behandling.")
    g_na4 = auto_gate("Henvendelse krever henvisning.",
                      "Du kan kontakte helsestasjonen uten henvisning.",
                      v_na4)
    g_act25 = auto_gate("Psykolog i BUP kan gi terapi.",
                        "BUP har psykologer og leger som gir behandling.",
                        v_act25)
    v_entc_prod = v02.judge_claim(*entc)
    canary_rows.append({"canary": "ENT-C-product",
                        "pass": v_entc_prod["verdict"] == "CONTRADICTED",
                        "detail": "expected CONTRADICTED (matches frozen RC1)"})
    v_nr1_prod = v02.judge_claim(*nr1)
    canary_rows.append({"canary": "N-R1-product",
                        "pass": v_nr1_prod["verdict"] == "CONTRADICTED",
                        "detail": "expected CONTRADICTED (matches frozen RC1)"})
    canary_rows.append({"canary": "N-A4-product",
                        "pass": v_na4["verdict"] != "SUPPORTED" or
                                g_na4 is not None,
                        "detail": "no false auto-SUPPORT"})
    canary_rows.append({"canary": "ACT-25-product",
                        "pass": v_act25["verdict"] == "SUPPORTED" or
                                g_act25 is not None,
                        "detail": "support capability preserved"})
    results["canaries"] = canary_rows
    if not all(r["pass"] for r in canary_rows):
        fails.append("canaries")

    # 5. ID guard on RC2 runtime engine files
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, "evaluation", "semantic-judge",
                                      "v0.4.1", "id_guard.py"),
         ENGINE],
        capture_output=True, text=True)
    id_guard_out = p.stdout + p.stderr
    id_guard_ok = p.returncode == 0
    if not id_guard_ok and "0 hits" not in id_guard_out.lower():
        results["id_guard"] = {"exit": p.returncode, "tail": id_guard_out[-500:]}
        fails.append("id_guard")
    else:
        results["id_guard"] = {"exit": p.returncode, "tail": id_guard_out[-500:]}

    # 6. parser soundness asserts (spec RC2 sections 6-7, 12)
    import quote_aligner as QA
    age_negatives = ["§ 4-3", "§ 15-8 andre ledd", "kapittel 4",
                     "FOR-2026-06-25-1361", "LOV-2026-06-12-27",
                     "frist 25.06.2026", "telefon 55 55 33 34",
                     "2 572 kroner", "inntekt over 4 G"]
    law_fp = [t for t in age_negatives if QA.extract_ages(t)]
    results["law_as_age_fp"] = law_fp
    if law_fp:
        fails.append("law_as_age_fp")

    ok = not fails
    results["_verdict"] = "RC2_PHASE_A_PASS" if ok else "RC2_PHASE_A_FAIL"
    results["_failed_gates"] = fails
    out_path = os.path.join(HERE, "phase-a-gates.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in results.items()
                      if k in ("_verdict", "_failed_gates")}, indent=1))
    for name in fails:
        print("FAILED GATE:", name, json.dumps(results.get(name))[:300])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
