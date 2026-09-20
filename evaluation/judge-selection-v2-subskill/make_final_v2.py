#!/usr/bin/env python3
"""V2 finalize: frozen comparison -> preregistered selection -> terminal status.

Selection rule (preregistered in contract): priority order longcat-2-0-free
then mimo-v2-5-pro; a candidate is eligible only if ALL one-shot gates pass;
the top eligible candidate must also pass the stability screen. No
best-of-bad: if no candidate qualifies the terminal status is
JUDGE_SELECTION_V2_NO_JUDGE_QUALIFIES.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2-SUBSKILL-SCREENING"
CANDIDATES = [("longcat-2-0-free", "command-code/meituan/LongCat-2.0:free"),
              ("mimo-v2-5-pro", "command-code/xiaomi/mimo-v2.5-pro")]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def save(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def load_results():
    out = {}
    for key, model in CANDIDATES:
        sp = os.path.join(HERE, "screening-results-" + key + ".json")
        stp = os.path.join(HERE, "stability-results-" + key + ".json")
        entry = {"model": model,
                 "screening": json.load(open(sp)) if os.path.exists(sp) else None,
                 "stability": json.load(open(stp)) if os.path.exists(stp) else None}
        out[key] = entry
    return out


def main():
    results = load_results()
    eligible = [key for key, _ in CANDIDATES
                if results[key]["screening"]
                and results[key]["screening"].get("gates_all_pass")]
    selected = None
    if eligible:
        top = eligible[0]
        stab = results[top]["stability"]
        if stab and stab.get("stability_pass"):
            selected = top

    comparison = {
        "artifact": "JUDGE SELECTION V2 CANDIDATE COMPARISON (FROZEN)",
        "task_id": TASK_ID,
        "selection_priority": [k for k, _ in CANDIDATES],
        "candidates": {k: {
            "model": v["model"],
            "gates_all_pass": bool(v["screening"] and v["screening"].get("gates_all_pass")),
            "stability_pass": bool(v["stability"] and v["stability"].get("stability_pass")),
        } for k, v in results.items()},
        "eligible": eligible,
        "selected": selected,
    }
    save(os.path.join(HERE, "candidate-comparison.json"), comparison)

    if selected:
        status = "JUDGE_SELECTION_V2_QUALIFIED"
        stab = results[selected]["stability"]
        headline = ("Selected judge: " + selected + " ("
                    + results[selected]["model"]
                    + "); stability overall="
                    + str(round(stab["overall_modal_stability"], 4))
                    + " per_family="
                    + json.dumps(stab["per_family_modal_stability"]))
    elif eligible:
        status = "JUDGE_SELECTION_V2_NO_JUDGE_QUALIFIES"
        headline = ("Top candidate " + eligible[0]
                    + " passed one-shot gates but failed the stability screen; "
                    "no best-of-bad selection permitted.")
    else:
        status = "JUDGE_SELECTION_V2_NO_JUDGE_QUALIFIES"
        headline = "No candidate passed all one-shot gates; no best-of-bad selection permitted."

    report = "# Judge Selection V2 - Final Report" + chr(10) + chr(10)
    report += "TASK ID: " + TASK_ID + chr(10) + chr(10)
    report += "## Candidates (one-shot, 72 fixtures, frozen V1.4 pipeline)" + chr(10) + chr(10)
    for key, model in CANDIDATES:
        s = results[key]["screening"]
        report += "- " + key + " (" + model + "): "
        if not s:
            report += "NO SCREENING RESULTS (technically not testable)" + chr(10)
            continue
        cg = s["combined_gates"]
        report += ("family_a=" + str(round(cg["a"]["accuracy"], 4))
                   + " family_b=" + str(round(cg["b"]["accuracy"], 4))
                   + " family_c=" + str(round(cg["c"]["accuracy"], 4))
                   + " crit_fn=" + str(cg["a"]["fn"])
                   + " safety_forbidden_fn=" + str(cg["c"]["fn"])
                   + " evidence_valid=" + str(round(s["evidence_valid_rate"], 4))
                   + " gates_all_pass=" + str(s["gates_all_pass"]) + chr(10))
    report += (chr(10) + "## Selection" + chr(10) + chr(10) + headline + chr(10) + chr(10))
    report += "TERMINAL STATUS: " + status + chr(10) + chr(10)
    report += ("No next stage started: no fresh judge validation, no new evaluator "
               "lineage, no product integration, no full SUT, no product holdout."
               + chr(10))
    with open(os.path.join(HERE, "final-report.md"), "w", encoding="utf-8") as fh:
        fh.write(report)

    lock_path = os.path.join(HERE, "TASK-LOCK.json")
    lock = json.load(open(lock_path))
    lock["status"] = "CLOSED_" + status
    lock["terminal_status"] = status
    lock["terminal_artifacts"] = {
        "candidate-comparison.json": sha(os.path.join(HERE, "candidate-comparison.json")),
        "final-report.md": sha(os.path.join(HERE, "final-report.md")),
    }
    if selected:
        lock["selected_judge"] = {"candidate_key": selected,
                                  "model": results[selected]["model"]}
    save(lock_path, lock)
    print("TERMINAL STATUS:", status, flush=True)
    print(headline, flush=True)


if __name__ == "__main__":
    main()
