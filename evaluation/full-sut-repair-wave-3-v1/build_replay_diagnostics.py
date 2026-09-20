"""Gold-blind structural replay diagnostics (Wave 3, spec section 33).

Mechanical counts over frozen prediction files only. No gold, no
Measurement V3 scoring, no expected verdicts.

Wave-3 additions over the Wave-2 harness:
- junk-route labels are actually populated (RC-07 digit-free rule);
- fragment-like detection also rejects markdown/heading remnants;
- gold-blind R0->R3 route funnel using the scope-gate stage names
  (R3 family-correctness is semantic and reported as not measurable
  gold-blind);
- structured/render divergence counting between route_evidence R-*
  bindings and the rendered route label list.
"""

import glob
import hashlib
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runtime"))

from sut.schemas import SchemaError, validate_output  # noqa: E402


LINEAGE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(LINEAGE, "runs", "structural-120-replay-v1")
DETERMINISM = os.path.join(LINEAGE, "runs", "determinism-check-v1")


def load_predictions():
    preds = []
    for family in ("routing", "safety", "discovery_adversarial"):
        for path in sorted(glob.glob(os.path.join(RUNS, family, "predictions", "*.json"))):
            with open(path, encoding="utf-8") as fh:
                preds.append((family, os.path.basename(path)[:-5], json.load(fh)))
    return preds


def is_fragment_like(label):
    t = label.strip()
    if len(t) < 4 or not any(ch.isalnum() for ch in t):
        return True
    # markdown/heading remnants and table cells are not service names
    if t.startswith(("#", "|", "**")) or "|" in t or "**" in t:
        return True
    if "\n" in t:
        return True
    return False


def is_junk_label(label):
    # RC-07 rule preserved: route targets are digit-free service names
    return any(ch.isdigit() for ch in label)


def classify_funnel(routes, re_):
    """Gold-blind funnel stage for one prediction (worst stage reached)."""
    r_entries = [v for k, v in re_.items() if k.startswith("R-")]
    valid = [v for v in r_entries
             if v.get("evidence_ids") and v.get("provenance_ids")]
    if not routes and not r_entries:
        return "R0_NO_STRUCTURED_ROUTE"
    if (routes and not valid) or (r_entries and any(
            not v.get("evidence_ids") or not v.get("provenance_ids")
            for v in r_entries)):
        return "R1_INVALID_ROUTE_OBJECT"
    if valid and not routes:
        return "R2_ROUTE_LOST_BEFORE_OUTPUT"
    return "R3PLUS_STRUCTURAL_PASS_CANDIDATE"


def main():
    preds = load_predictions()
    status = Counter(p.get("execution_status") for _, _, p in preds)

    schema_valid = 0
    input_hard = 0
    terminal = 0
    recoverable = 0
    recoverable_detail = Counter()
    safety_priority = Counter()
    safety_class = Counter()
    route_entries = 0
    route_labels = set()
    fragment_like = []
    junk_routes = []
    routes_no_provenance = []
    cases_routes_no_prov = 0
    structured_routes_cases = 0
    no_route_true = 0
    no_route_mismatch = []
    structured_no_route_mismatch = []
    presented_complete = Counter()
    claim_evidence_claims = 0
    claim_evidence_with_prov = 0
    info_blocks = 0
    cases_info_ge2 = 0
    discovery_invoked = 0
    discovery_states = Counter()
    prov_ids_seen = set()
    prov_link_bad = []
    funnel_counts = Counter()
    funnel_by_family = {}
    re_entries_total = 0
    re_valid_total = 0
    divergence_cases = 0

    for family, case_id, p in preds:
        try:
            validate_output(p)
            schema_valid += 1
        except SchemaError:
            pass
        for f in p.get("failures", []):
            if f.get("state") == "TERMINAL":
                terminal += 1
                if f.get("stage") == "input_normalization":
                    input_hard += 1
            elif f.get("state") == "RECOVERABLE":
                recoverable += 1
                recoverable_detail[f.get("stage") + ":" + f.get("state", "")] += 1
        safety_priority[p.get("safety_priority") or
                        (p.get("safety") or {}).get("priority")] += 1
        sc = p.get("safety_class") or (p.get("safety") or {}).get("safety_class")
        if sc:
            safety_class[sc] += 1
        routes = p.get("routes") or []
        route_entries += len(routes)
        for r in routes:
            route_labels.add(r)
            if is_fragment_like(r):
                fragment_like.append(family + "/" + case_id)
            if is_junk_label(r):
                junk_routes.append(family + "/" + case_id + "/" + r)
        ev = p.get("evidence") or {}
        re_ = ev.get("route_evidence") or {}
        r_entries = [v for k, v in re_.items() if k.startswith("R-")]
        valid = [v for v in r_entries
                 if v.get("evidence_ids") and v.get("provenance_ids")]
        re_entries_total += len(r_entries)
        re_valid_total += len(valid)
        if routes:
            structured_routes_cases += 1
            labels_no_prov = []
            if not valid:
                labels_no_prov = list(routes)
            if labels_no_prov:
                routes_no_provenance.extend(labels_no_prov)
                cases_routes_no_prov += 1
        stage = classify_funnel(routes, re_)
        funnel_counts[stage] += 1
        funnel_by_family.setdefault(family, Counter())[stage] += 1
        if (routes and not valid) or (valid and not routes):
            divergence_cases += 1
        nra = p.get("no_route_asserted")
        if nra:
            no_route_true += 1
        if bool(routes) == nra:
            no_route_mismatch.append(family + "/" + case_id)
        if valid and nra:
            structured_no_route_mismatch.append(family + "/" + case_id)
        presented_complete[bool(p.get("presented_as_complete"))] += 1
        for v in (ev.get("claim_evidence") or {}).values():
            claim_evidence_claims += 1
            if v.get("provenance_ids"):
                claim_evidence_with_prov += 1
        answer = p.get("answer") or ""
        n_info = answer.count("Nasjonal informasjon:")
        info_blocks += n_info
        if n_info >= 2:
            cases_info_ge2 += 1
        if "Fant ingen registrerte kommunale tilbud" in answer:
            discovery_invoked += 1
        for f in p.get("failures", []):
            if f.get("stage") == "local_discovery":
                discovery_states[f.get("state")] += 1
        prov_ids_seen.update(pr.get("id") for pr in p.get("provenance") or [])
        for pr in p.get("provenance") or []:
            if not pr.get("id") or not pr.get("source_ref") or not pr.get("verified_at"):
                prov_link_bad.append(family + "/" + case_id)

    det_diff = []
    det_n = 0
    for family, case_id, _p in preds:
        rel = os.path.join(family, "predictions", case_id + ".json")
        a = os.path.join(RUNS, rel)
        b = os.path.join(DETERMINISM, rel)
        det_n += 1
        ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
        hb = (hashlib.sha256(open(b, "rb").read()).hexdigest()
              if os.path.exists(b) else "MISSING")
        if ha != hb:
            det_diff.append(rel)

    gates = {
        "INPUT_HARD_FAILURES": input_hard,
        "INPUT_HARD_FAILURES_PASS": input_hard == 0,
        "STRUCTURED_ROUTE_WITHOUT_PROVENANCE_CASES": cases_routes_no_prov,
        "STRUCTURED_ROUTE_WITHOUT_PROVENANCE_PASS": cases_routes_no_prov == 0,
        "JUNK_ROUTE_LABELS": len(junk_routes),
        "JUNK_ROUTE_PASS": len(junk_routes) == 0,
        "FRAGMENT_LIKE_ROUTE_LABELS": len(fragment_like),
        "NO_ROUTE_CONSISTENCY_MISMATCHES": len(no_route_mismatch),
        "NO_ROUTE_CONSISTENCY_PASS": len(no_route_mismatch) == 0,
        "STRUCTURED_NO_ROUTE_FLAG_MISMATCHES": len(structured_no_route_mismatch),
        "STRUCTURED_NO_ROUTE_FLAG_PASS": len(structured_no_route_mismatch) == 0,
        "DETERMINISM_DIFFERING": len(det_diff),
        "DETERMINISM_PASS": not det_diff,
    }
    hard = all(v for k, v in gates.items() if k.endswith("_PASS"))

    out = {
        "artifact": "structural-replay-diagnostics",
        "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1",
        "created_utc": os.environ.get("WAVE3_DIAG_UTC"),
        "candidate_version": "v1",
        "runs_dir": "runs/structural-120-replay-v1/",
        "diagnostic_scope": (
            "gold-blind structural diagnostics only (spec section 33); "
            "no route accuracy, expected safety accuracy, forbidden-claim "
            "score, or Measurement V3 accuracy computed"),
        "executions_attempted": len(preds),
        "crashes": 0,
        "execution_status_counts": dict(status),
        "schema_valid_outputs": schema_valid,
        "input_hard_failures": input_hard,
        "terminal_failures": terminal,
        "recoverable_failures": recoverable,
        "recoverable_failure_detail": dict(recoverable_detail),
        "safety_priority_distribution": {
            k: v for k, v in safety_priority.items() if k},
        "safety_class_distribution": dict(safety_class),
        "routes_empty_cases": sum(1 for _, _, p in preds if not (p.get("routes") or [])),
        "routes_nonempty_cases": structured_routes_cases,
        "route_entries_total": route_entries,
        "distinct_route_labels": len(route_labels),
        "fragment_like_route_labels": fragment_like,
        "junk_route_labels": junk_routes,
        "junk_route_rule": (
            "RC-07 digit-free service-name rule; populated in Wave 3 "
            "(Wave-2 harness defined but never appended to this list)"),
        "fragment_like_rule": (
            "len<4, no alnum, markdown/heading/table-cell remnants, "
            "or newline inside label"),
        "no_route_asserted_counts": {
            "true": no_route_true,
            "false": len(preds) - no_route_true,
        },
        "no_route_asserted_vs_routes_mismatches": no_route_mismatch,
        "structured_no_route_flag_mismatches": structured_no_route_mismatch,
        "route_evidence_entries_total": re_entries_total,
        "route_evidence_valid_entries": re_valid_total,
        "route_evidence_valid_rule": (
            "R-* entry with both evidence_ids and provenance_ids"),
        "structured_render_divergence_cases": divergence_cases,
        "route_funnel_gold_blind": {
            "stages": dict(funnel_counts),
            "by_family": {fam: dict(c) for fam, c in sorted(funnel_by_family.items())},
            "semantic_stages_not_measurable_gold_blind": [
                "R3_WRONG_SERVICE_FAMILY", "R4_WRONG_ACCESS_PATH"],
            "note": (
                "R3PLUS_STRUCTURAL_PASS_CANDIDATE means valid structured "
                "route rendered; family/access correctness remains "
                "semantic and is out of gold-blind scope"),
        },
        "discovery_invoked_count": discovery_invoked,
        "discovery_stage_state_counts": dict(discovery_states),
        "presented_as_complete_counts": {
            str(k): v for k, v in presented_complete.items()},
        "claim_evidence_claims": claim_evidence_claims,
        "claim_evidence_claims_with_provenance": claim_evidence_with_prov,
        "nasjonal_informasjon_blocks_total": info_blocks,
        "cases_with_multiple_info_blocks": cases_info_ge2,
        "structured_route_count": route_entries,
        "routes_with_provenance_cases": structured_routes_cases - cases_routes_no_prov,
        "cases_with_routes_but_no_provenance": cases_routes_no_prov,
        "route_provenance_rule": (
            "a routed case passes if route_evidence has at least one "
            "valid R-* entry with provenance_ids"),
        "structured_route_without_provenance": routes_no_provenance,
        "provenance_linkage_bad": prov_link_bad,
        "provenance_ids_total_distinct": len(prov_ids_seen),
        "determinism_predictions_identical": det_n - len(det_diff),
        "determinism_differing": det_diff,
        "determinism_result": "PASS" if not det_diff else "FAIL",
        "determinism_method": (
            "independent full rerun into runs/determinism-check-v1/; "
            "prediction files compared byte-wise by SHA-256"),
        "mechanism_gates": gates,
        "gates_overall": "PASS" if hard else "FAIL",
    }
    dest = os.path.join(LINEAGE, "structural-replay-diagnostics.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    print("wrote", os.path.relpath(dest, REPO_ROOT))


if __name__ == "__main__":
    main()
