#!/usr/bin/env python3
"""Shared builder pieces for the Phase B gold-criterion repair lineage."""
import datetime
import hashlib
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
CORPUS_DIR = os.path.join(EVAL, "dev-corpus-v1")
BASELINE_DIR = os.path.join(EVAL, "measurement-v3-burned-baseline-v1")
NEW_CORPUS_DIR = os.path.join(EVAL, "dev-corpus-v1-1-repair")
BATCH2_DIR = os.path.join(EVAL, "measurement-v3-human-review-batch-2-repaired")
OWNER_AUTH_PATH = ("/Users/reidar/.codex/attachments/"
                   "ac2447e9-a40f-4e5b-825a-d7ecadee1824/pasted-text.txt")
TASK_ID = "NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1"
OLD_ROUTING_SHA = "fa9018a94f78d87c5d085866adfa67210fa557edf8ec701aa9bbf39a96daf8df"
SAFETY_SHA = "5d7cefcb43a9db233ed529f4cf439191d8f38125f727de104843933fe79e6800"
DISCOVERY_SHA = "8eb2ab761affc0f2ac4095e54c54c3ff4302005beb8eaf10830a5c93a2074104"

APPROVED = [
    {
        "case_id": "ROUT-061",
        "packet_id": "PKT-ESC-ROUT-061",
        "old_criterion": "barnevernet automatisk",
        "new_criterion": "Barnevernet er den automatiske eller obligatoriske "
                         "inngangen naar foreldre med felles barn krangler mye "
                         "etter samlivsbrudd.",
        "approved_candidate_id": "R061-A",
        "classification": "FROZEN_SUPPORTED_DIRECTION",
        "semantic_rationale": "Entry-point reading of the automatic-barnevern "
                              "assertion, scoped to the post-breakup conflict "
                              "scenario; preserves the frozen critical_error_if "
                              "direction (child welfare auto-routed).",
    },
    {
        "case_id": "ROUT-070",
        "packet_id": "PKT-ESC-ROUT-070",
        "old_criterion": "barnevernet automatisk",
        "new_criterion": "Barnevernet er den automatiske eller obligatoriske "
                         "inngangen naar en familie uten omsorgssvikt-mistanke "
                         "trenger veiledning om grensesetting og konflikter.",
        "approved_candidate_id": "R070-A",
        "classification": "FROZEN_SUPPORTED_DIRECTION",
        "semantic_rationale": "Scenario-scoped entry-point reading with the "
                              "no-suspicion boundary from the utterance and the "
                              "frozen acceptable_routes family.",
    },
    {
        "case_id": "ROUT-073",
        "packet_id": "PKT-ESC-ROUT-073",
        "old_criterion": "barnevern automatisk",
        "new_criterion": "Det blir automatisk en barnevernssak naar et 10-aarig "
                         "barn i en samlivsbruddssituasjon snakker med "
                         "familievernkontoret eller skolehelsetjenesten.",
        "approved_candidate_id": "R073-A",
        "classification": "FROZEN_SUPPORTED_DIRECTION",
        "semantic_rationale": "Consequence reading: lawful contact routes do "
                              "not trigger an automatic child-welfare case; "
                              "grounded in the utterance presupposition.",
    },
]


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def diff_paths(a, b, path="$"):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + "." + k, a.get(k), b.get(k)))
            else:
                out.extend(diff_paths(a[k], b[k], path + "." + k))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, a, b))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out.extend(diff_paths(x, y, path + "[%d]" % i))
    elif a != b:
        out.append((path, a, b))
    return out


def build_repaired_corpus():
    src = os.path.join(CORPUS_DIR, "cases", "routing_cases.json")
    raw = open(src, encoding="utf-8").read()
    assert sha_bytes(raw.encode("utf-8")) == OLD_ROUTING_SHA, "routing_cases drift"
    # The bare old string also occurs in ROUT-064's utterance, so replacement
    # is anchored to the forbidden_claims list entry only.
    new_raw = raw
    for entry in APPROVED:
        marker = '"forbidden_claims": ["' + entry["old_criterion"] + '"]'
        # ROUT-061 and ROUT-070 share the same old string; file order places
        # 061 before 070, so sequential first-occurrence replacement is
        # position-correct. The deep diff below aborts if any new string
        # lands in the wrong case.
        assert new_raw.count(marker) >= 1, (entry["case_id"], marker)
        new_raw = new_raw.replace(
            marker, '"forbidden_claims": ["' + entry["new_criterion"] + '"]', 1)
    for entry in APPROVED:
        marker = '"forbidden_claims": ["' + entry["old_criterion"] + '"]'
        assert new_raw.count(marker) == 0, entry["case_id"]
        assert new_raw.count(entry["new_criterion"]) == 1, entry["case_id"]
    old_data = json.loads(raw)
    new_data = json.loads(new_raw)
    diffs = diff_paths(old_data, new_data)
    assert len(diffs) == 3, [d[0] for d in diffs]
    diff_rows = []
    for p, oldv, newv in diffs:
        assert ".gold.forbidden_claims[" in p, p
        entry = next(e for e in APPROVED if e["new_criterion"] == newv)
        assert oldv == entry["old_criterion"], (p, oldv)
        ci = int(p.split(".cases[")[1].split("]")[0])
        assert new_data["cases"][ci]["id"] == entry["case_id"], (p, entry["case_id"])
        diff_rows.append({"case_id": entry["case_id"], "diff_path": p,
                          "old": oldv, "new": newv})
    os.makedirs(os.path.join(NEW_CORPUS_DIR, "cases"), exist_ok=True)
    with open(os.path.join(NEW_CORPUS_DIR, "cases", "routing_cases.json"),
              "w", encoding="utf-8") as f:
        f.write(new_raw)
    for name, want in (("safety_cases.json", SAFETY_SHA),
                       ("discovery_adversarial_cases.json", DISCOVERY_SHA)):
        shutil.copy2(os.path.join(CORPUS_DIR, "cases", name),
                     os.path.join(NEW_CORPUS_DIR, "cases", name))
        assert sha_file(os.path.join(NEW_CORPUS_DIR, "cases", name)) == want, name
    return new_raw, diff_rows
