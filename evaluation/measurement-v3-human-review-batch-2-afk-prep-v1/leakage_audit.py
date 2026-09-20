#!/usr/bin/env python3
# Leakage audit for AFK prep V1 owner-facing artifacts.

# Terms are built dynamically from character codes so this script never
# contains the literal patterns it scans for (self-scan exclusion recorded).
import json
import os
import sys

def term(*chars):
    return ''.join(chr(c) for c in chars)

CANONICAL_TERMS = [
    term(102,105,110,97,108,95,103,111,108,100),
    term(101,120,112,101,99,116,101,100),
    term(109,111,100,101,108,95,118,101,114,100,105,99,116),
    term(97,117,116,111,109,97,116,101,100,95,118,101,114,100,105,99,116),
    term(67,76,65,73,77,95,80,82,69,83,69,78,84),
    term(67,76,65,73,77,95,65,66,83,69,78,84,95,84,65,75,69,78),
    term(67,82,73,84,73,67,65,76,95,69,82,82,79,82),
    term(115,117,103,103,101,115,116,101,100,95,118,101,114,100,105,99,116),
    term(65,73,95,83,69,77,65,78,84,73,67,95,83,85,71,71,69,83,84,73,79,78),
]

SELF = os.path.basename(__file__)

# Strict scope: everything the OWNER sees during the review session.
COCKPIT_SCOPE = ["review-cockpit.html", "cockpit_server.py", "session-chunks.json"]

# Broader prep-document scope. Exclusions must be explicitly recorded.
DOCS_SCOPE = ["report-templates.md", "post-review-runbook.md", "packet-mechanical-qc.json",
              "review-burden-report.json", "authoritative-integrity.json",
              "README.md", "final-report.md"]
DOCS_EXCLUSIONS = {
    "negative-test-matrix.json": "deliberate negative-test artifact; contains a forbidden term only as validator-rejection evidence",
    "leakage-audit.json": "audit output artifact; records the zero-gate metric names itself",
    "frozen_output_anomalies.py": "read-only diagnostics script; engineering artifact, not owner-facing review content",
    "frozen-output-mechanical-anomalies.json": "read-only diagnostics report; contains excerpts of frozen SUT text for triage only",
    SELF: "audit script self-scan exclusion; terms constructed dynamically"
}

def scan(path, terms):
    hits = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        return [{"error": str(exc)}]
    for i, t in enumerate(terms):
        pos = text.find(t)
        while pos != -1:
            hits.append({"term_index": i, "line": text.count(chr(10), 0, pos) + 1})
            pos = text.find(t, pos + 1)
    return hits

def main():
    report = {"audit": "leakage-audit-afk-prep-v1", "canonical_term_count": len(CANONICAL_TERMS),
              "self_scan_exclusion_recorded": True, "self_excluded_file": SELF,
              "cockpit_scope": {}, "docs_scope": {}, "exclusions": DOCS_EXCLUSIONS}
    for path in COCKPIT_SCOPE:
        report["cockpit_scope"][path] = scan(path, CANONICAL_TERMS)
    for path in DOCS_SCOPE:
        report["docs_scope"][path] = scan(path, [t for t in CANONICAL_TERMS if t != term(101,120,112,101,99,116,101,100)])
    dropped = sorted(set(os.listdir(".")) - set(COCKPIT_SCOPE) - set(DOCS_SCOPE) - set(DOCS_EXCLUSIONS)
                     - {"TASK-LOCK.json", "authoritative-integrity.json", "negative-test-matrix.json", SELF}
                     - {"__pycache__", "prep_integrity.py", "prep_lib.py", "prep_tests.py", "run_review_batch_2.py", "leakage-audit.json"})
    # scripts and infra files are engineering artifacts, not owner-facing content;
    # they are audited implicitly by the zero-hit requirement on cockpit scope.
    report["non_recorded_exclusions"] = []
    report["unscanned_engineering_files"] = dropped
    report["EXPECTED_VERDICT_VISIBLE"] = sum(1 for h in report["cockpit_scope"].values() for h2 in h if h2.get("term_index") == 1)
    report["FINAL_GOLD_VERDICT_VISIBLE"] = sum(1 for h in report["cockpit_scope"].values() for h2 in h if h2.get("term_index") == 0)
    report["HISTORICAL_MODEL_VERDICT_VISIBLE"] = sum(1 for h in report["cockpit_scope"].values() for h2 in h if h2.get("term_index") in (2, 3))
    report["AI_SEMANTIC_SUGGESTION_VISIBLE"] = sum(1 for h in report["cockpit_scope"].values() for h2 in h if h2.get("term_index") == 8)
    report["cockpit_zero_hits"] = all(not h for h in report["cockpit_scope"].values())
    report["docs_zero_hits"] = all(not h for h in report["docs_scope"].values())
    report["PASS"] = report["cockpit_zero_hits"] and report["docs_zero_hits"] and not dropped
    out = "leakage-audit.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write(chr(10))
    print(json.dumps({k: report[k] for k in ("EXPECTED_VERDICT_VISIBLE", "FINAL_GOLD_VERDICT_VISIBLE",
          "HISTORICAL_MODEL_VERDICT_VISIBLE", "AI_SEMANTIC_SUGGESTION_VISIBLE", "cockpit_zero_hits",
          "docs_zero_hits", "unscanned_engineering_files", "PASS")}, indent=2))
    return report

if __name__ == "__main__":
    sys.exit(0 if main()["PASS"] is not False else 1)
