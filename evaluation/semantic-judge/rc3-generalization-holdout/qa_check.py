#!/usr/bin/env python3
"""QA for the RC3 generalization holdout construction task (spec 53)."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
KB = ROOT / "kb"
SNAP = HERE / "runtime-snapshot"
AUDIT = HERE / "construction-audit"
OFFICIAL_SHA = ("e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202"
                "adc969ebaa14b2")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def shasum(path):
    return subprocess.run(["shasum", "-a", "256", str(path)],
                          capture_output=True, text=True).stdout.split()[0]


def main():
    off = (HERE.parent / "blind-recertification" / "RC2-V4-run"
           / "phase2" / "official-score.json")
    check("rc2_official_score_sha", shasum(off) == OFFICIAL_SHA,
          shasum(off))
    r = subprocess.run(["shasum", "-a", "256", "-c", "hashes.txt"],
                       cwd=SNAP, capture_output=True, text=True)
    check("snapshot_hashes", r.returncode == 0,
          "failures: " + str(r.stdout.count(": FAILED")))
    check("contract_files_exist",
          (HERE / "proof-soundness-contract-v2.md").exists()
          and (HERE / "proof-soundness-contract-v2.json").exists())

    pub = json.loads((HERE / "generalization-cases.json")
                     .read_text(encoding="utf-8"))
    cases = pub["cases"]
    sel = json.loads((AUDIT / "selection.json").read_text(encoding="utf-8"))
    rep = sel["report"]["quota_report_core"]
    check("core_size", rep["n"] >= 140, rep["n"])
    sem = rep["semantic"]
    check("semantic_balance",
          all(abs(sem.get(k, 0) - 40) <= 5
              for k in ("SUPPORTED", "CONTRADICTED",
                        "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE")),
          json.dumps(sem))
    prod = rep["product"]
    check("product_quotas",
          prod.get("AUTO_SUPPORTED", 0) >= 25
          and prod.get("AUTO_CONTRADICTED", 0) >= 25
          and prod.get("REVIEW_REQUIRED", 0) >= 25
          and prod.get("ABSTAIN_INSUFFICIENT", 0) >= 25,
          json.dumps(prod))
    check("compound_quota", rep["compound_cases"] >= 50,
          rep["compound_cases"])
    check("critical_quota", rep["critical"] >= 20, rep["critical"])

    by_id = {c["case_id"]: c for c in
             json.loads((AUDIT / "cases-pass1.json")
                        .read_text(encoding="utf-8"))["cases"]}
    core_ids = set(sel["core_ids"])
    core = [by_id[i] for i in core_ids]
    neg_deo = sum(1 for c in core
                  if any(f in ("negation", "deontic")
                         or f.startswith("modality")
                         for f in c["public_flags"]))
    check("negation_deontic_quota", neg_deo >= 30, neg_deo)
    cond = sum(1 for c in core
               if any(f in ("condition", "exception")
                      for f in c["public_flags"]))
    check("condition_quota", cond >= 30, cond)
    for flag, mn in (("multi-span", 30), ("numeric", 30), ("temporal", 30),
                     ("actor", 30), ("scope", 25)):
        n = sum(1 for c in core if flag in c["public_flags"])
        check("flag_" + flag, n >= mn, n)

    p2 = json.loads((AUDIT / "labels-pass2.json").read_text(encoding="utf-8"))
    check("pass2_complete", all(p2.get(i, {}).get("status") == "OK"
                                for i in core_ids))
    agr = json.loads((AUDIT / "agreement.json").read_text(encoding="utf-8"))
    st = agr["stats"]
    for k in ("semantic_agreement", "proof_safe_agreement",
              "product_agreement"):
        check("agreement_" + k, st[k] >= 0.90, st[k])
    check("agreement_atom_count", st["atom_count_agreement"] >= 0.90,
          st["atom_count_agreement"])
    adj = json.loads((AUDIT / "adjudication.json").read_text(
        encoding="utf-8"))
    check("adjudication_rate", adj["adjudication_rate"] <= 0.35,
          adj["adjudication_rate"])
    check("unresolved_zero", adj["unresolved"] == 0)
    fin_path = AUDIT / "labels-final.json"
    fin = json.loads(fin_path.read_text(encoding="utf-8")) \
        if fin_path.exists() else {}
    check("final_labels_complete",
          len(fin) == len(core_ids)
          and all("atoms" in fin[i] for i in core_ids
                  if by_id[i]["compound"]))
    atoms_total = sum(len(fin[i]["atoms"]) for i in core_ids
                      if i in fin and "atoms" in fin[i])
    check("atom_completeness", atoms_total == rep["atoms_total"],
          "%d/%d" % (atoms_total, rep["atoms_total"]))

    kb_cache = {}
    bad = 0
    for c in cases:
        for s in c["sources"]:
            kbfile = ROOT / s["kb_ref"].removeprefix("kb/")
            if kbfile not in kb_cache:
                kb_cache[kbfile] = (kbfile.read_text(encoding="utf-8")
                                    if kbfile.exists() else None)
            txt = kb_cache[kbfile]
            if txt is None or s["text"] not in txt:
                bad += 1
    check("source_fidelity", bad == 0, "%d mismatches" % bad)

    nov = json.loads((AUDIT / "novelty-pass1.json").read_text(
        encoding="utf-8"))
    rej = [n for n in nov if n["verdict"] != "OK"]
    mx = max((n["max_similarity"] for n in nov), default=0)
    check("novelty", len(rej) == 0,
          "rejects=%d max_sim=%.3f" % (len(rej), mx))

    pub_text = (HERE / "generalization-cases.json").read_text(
        encoding="utf-8")
    leaks = [t for t in ("semantic_truth", "proof_safe", "product_action",
                         "genuine_insufficiency", "rationale",
                         "AUTO_SUPPORTED", "AUTO_CONTRADICTED",
                         "ABSTAIN_INSUFFICIENT") if t in pub_text]
    check("public_label_leak", not leaks, str(leaks))
    ids = re.findall(r"RC1B|RC2B|CAL-|ENT-|MOD-|LOC-", pub_text)
    check("public_id_guard", not ids, str(set(ids)))
    snap_ids = []
    for f in SNAP.rglob("*"):
        if f.is_file():
            t = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"RC1B|RC2B", t):
                snap_ids.append(f.name)
    check("snapshot_id_guard", not snap_ids, str(snap_ids))
    preds = [p.name for p in HERE.glob("*prediction*")]
    check("snapshot_not_run", not preds, str(preds))
    try:
        json.loads((HERE / "generalization-cases.json")
                   .read_text(encoding="utf-8"))
        json.loads((HERE / "blind-manifest.json").read_text(encoding="utf-8"))
        ok = True
    except Exception:
        ok = False
    check("json_valid", ok)
    r = subprocess.run(["find", str(KB), "-name", "*.md", "-mmin", "-1440"],
                       capture_output=True, text=True)
    check("kb_read_only", not r.stdout.strip(), r.stdout[:120])

    fails = [x for x in results if not x[1]]
    for name, okv, detail in results:
        print(("PASS " if okv else "FAIL ") + name + " :: " + str(detail))
    print("QA_FAILS=%d/%d" % (len(fails), len(results)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
