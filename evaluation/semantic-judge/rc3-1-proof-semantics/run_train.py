"""First train evaluation for the RC3.1 proof-semantics engine.

Read-only over corpus/train-cases.json; reports gates from the task spec.
"""
import json
import sys

from rc3_1_engine.proposition import content_tokens
from rc3_1_engine.engine import evaluate_case


def _match_frac(expected_text, produced_text):
    e = content_tokens(expected_text)
    p = set(content_tokens(produced_text))
    if not e:
        return 1.0
    hits = sum(1 for t in e if t in p)
    return hits / len(e)


def _boundary_match(expected_atoms, produced_atoms):
    """Greedy containment matcher; separate used sets for both sides."""
    pairs = []
    for i, ea in enumerate(expected_atoms):
        for j, pa in enumerate(produced_atoms):
            frac = _match_frac(ea, pa)
            if frac >= 0.6:
                pairs.append((frac, i, j))
    pairs.sort(reverse=True)
    used_i, used_j = set(), set()
    matched = 0
    for frac, i, j in pairs:
        if i not in used_i and j not in used_j:
            used_i.add(i)
            used_j.add(j)
            matched += 1
    return matched


def main():
    data = json.load(open("corpus/train-cases.json", encoding="utf-8"))
    cases = data["cases"]

    run1 = [evaluate_case(c) for c in cases]
    run2 = [evaluate_case(c) for c in cases]
    stable = all(
        json.dumps(a["verdict"], sort_keys=True) == json.dumps(b["verdict"], sort_keys=True)
        for a, b in zip(run1, run2)
    ) and all(
        [a["atoms"][k]["verdict"] for k in range(len(a["atoms"]))]
        == [b["atoms"][k]["verdict"] for k in range(len(b["atoms"]))]
        for a, b in zip(run1, run2)
    )

    per_class = {}
    preds = {}
    correct = 0
    wrong = []
    for c, r in zip(cases, run1):
        exp = c["rel"]
        got = r["verdict"]
        preds.setdefault(exp, {})
        preds[exp][got] = preds[exp].get(got, 0) + 1
        per_class.setdefault(exp, [0, 0])
        per_class[exp][1] += 1
        if exp == got:
            correct += 1
            per_class[exp][0] += 1
        else:
            wrong.append((c["case_id"], exp, got,
                          [a["verdict"] + ":" + a["rule"] for a in r["atoms"]]))

    flags = {}
    for c, r in zip(cases, run1):
        for f in c.get("public_flags", []):
            flags.setdefault(f, [0, 0])
            flags[f][1] += 1
            if c["rel"] == r["verdict"]:
                flags[f][0] += 1

    comp = [(c, r) for c, r in zip(cases, run1) if c.get("compound")]
    count_exact = 0
    boundary_exact = 0
    missing_atoms = 0
    extra_atoms = 0
    comp_details = []
    for c, r in comp:
        exp_atoms = [a["text"] for a in c.get("atoms", [])]
        got_atoms = [a["text"] for a in r["atoms"]]
        ce = len(exp_atoms) == len(got_atoms)
        bm = _boundary_match(exp_atoms, got_atoms)
        count_exact += ce
        boundary_exact += bm == len(exp_atoms) == len(got_atoms)
        if len(got_atoms) < len(exp_atoms):
            missing_atoms += len(exp_atoms) - len(got_atoms)
        if len(got_atoms) > len(exp_atoms):
            extra_atoms += len(got_atoms) - len(exp_atoms)
        if not ce or bm != len(exp_atoms):
            comp_details.append((c["case_id"], len(exp_atoms), len(got_atoms), bm))

    # Soundness accounting: auto verdicts = ENTAILS / CONTRADICTS.
    unsound = []
    invalid_auto = 0
    false_entails = 0
    false_contradicts = 0
    for c, r in zip(cases, run1):
        for a in r["atoms"]:
            if a["verdict"] in ("ENTAILS", "CONTRADICTS"):
                if not a.get("grounded"):
                    invalid_auto += 1
                if a["verdict"] == "ENTAILS":
                    ok = c["rel"] == "ENTAILS"
                else:
                    ok = c["rel"] == "CONTRADICTS"
                if not ok:
                    unsound.append((c["case_id"], a["atom_id"], a["verdict"], a["rule"]))
        if r["verdict"] == "ENTAILS" and c["rel"] != "ENTAILS":
            false_entails += 1
        if r["verdict"] == "CONTRADICTS" and c["rel"] != "CONTRADICTS":
            false_contradicts += 1

    n = len(cases)
    print(f"cases={n} correct={correct} accuracy={correct / n:.4f}")
    print("per-class (correct/total):")
    for k in sorted(per_class):
        c0, t0 = per_class[k]
        print(f"  {k}: {c0}/{t0} = {c0 / t0:.3f}")
    print("confusion (expected -> predicted):")
    for k in sorted(preds):
        print(f"  {k}: {preds[k]}")
    print("per-flag:")
    for f in sorted(flags):
        c0, t0 = flags[f]
        print(f"  {f}: {c0}/{t0} = {c0 / t0:.3f}")
    print(f"compounds={len(comp)} count_exact={count_exact}/{len(comp)} "
          f"boundary_exact={boundary_exact}/{len(comp)}")
    print(f"missing_atoms={missing_atoms} extra_atoms={extra_atoms}")
    if comp_details:
        print("decomposition misses:")
        for d in comp_details:
            print(f"  {d[0]}: expected {d[1]} got {d[2]} matched {d[3]}")
    print(f"stability_100={stable}")
    print(f"unsound_auto={len(unsound)} invalid_auto_ungrounded={invalid_auto}")
    print(f"false_entails_top={false_entails} false_contradicts_top={false_contradicts}")
    for u in unsound[:20]:
        print(f"  unsound {u}")
    if wrong:
        print("wrong cases:")
        for w in wrong:
            print(f"  {w[0]} exp={w[1]} got={w[2]} atoms={w[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
