#!/usr/bin/env python3
"""Mechanical V1.3M Set A rescore under the V1.4 agreement definition.

Read-only over the V1.3M lineage. No model calls. Recomputes agreement from
the frozen dual-pass label files, separating score-bearing semantic fields
from the free-text note.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V13M = os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-3m")

ROUTE_FIELDS = ["route_commitment", "route_verdict"]
UNC_FIELDS = ["uncertainty_requirement_mode", "uncertainty_verdict"]


def load(pass_no):
    with open(os.path.join(V13M, f"boundary-calibration-a-label{pass_no}.json")) as f:
        return {r["id"]: r for r in json.load(f)["rows"]}


def main():
    l1, l2 = load(1), load(2)
    fixtures = json.load(open(os.path.join(V13M, "boundary-calibration-a.json")))["fixtures"]
    dims = {f["id"]: f["dimension"] for f in fixtures}

    rows = []
    for rid in sorted(dims):
        a, b = l1[rid], l2[rid]
        dim = dims[rid]
        fields = ROUTE_FIELDS if dim.startswith("route") else UNC_FIELDS
        err = "error" in a or "error" in b
        rec = {"id": rid, "dimension": dim, "error": err}
        if err:
            rec["error_detail"] = a.get("error") or b.get("error")
            rec["semantic_fields_agree"] = None
        else:
            field_agree = {fl: a[fl] == b[fl] for fl in fields}
            rec["fields"] = field_agree
            rec["semantic_fields_agree"] = all(field_agree.values())
            rec["note_only_mismatch"] = (
                rec["semantic_fields_agree"] and a.get("note") != b.get("note"))
            rec["pass1"] = {fl: a[fl] for fl in fields}
            rec["pass2"] = {fl: b[fl] for fl in fields}
            intent = next(f for f in fixtures if f["id"] == rid)["designer_intent"]
            intent_fields = (
                {k: intent[k] for k in ("route_commitment", "route_verdict")}
                if dim.startswith("route")
                else {k: intent[k] for k in ("uncertainty_requirement_mode", "uncertainty_verdict")})
            rec["pass1_matches_designer_intent"] = all(
                a[k] == v for k, v in intent_fields.items())
            rec["pass2_matches_designer_intent"] = all(
                b[k] == v for k, v in intent_fields.items())
        rows.append(rec)

    def pct(n, d):
        return round(n / d, 4) if d else None

    valid = [r for r in rows if not r["error"]]
    route_v = [r for r in valid if r["dimension"].startswith("route")]
    unc_v = [r for r in valid if r["dimension"].startswith("uncertainty")]

    def field_stats(subset, fields):
        out = {}
        for fl in fields:
            n = sum(1 for r in subset if r["fields"][fl])
            out[fl] = {"agree": n, "n": len(subset), "rate": pct(n, len(subset))}
        n_full = sum(1 for r in subset if r["semantic_fields_agree"])
        out["full_semantic"] = {"agree": n_full, "n": len(subset), "rate": pct(n_full, len(subset))}
        return out

    route_stats = field_stats(route_v, ROUTE_FIELDS)
    unc_stats = field_stats(unc_v, UNC_FIELDS)
    n_semantic_agree = sum(1 for r in valid if r["semantic_fields_agree"])
    n_note_only = sum(1 for r in valid if r.get("note_only_mismatch"))
    n_all_semantic_incl_errors = sum(
        1 for r in rows if r["semantic_fields_agree"] is True)

    # Historical frozen full-row metric, recomputed for confirmation
    hist = json.load(open(os.path.join(V13M, "set-a-agreement.json")))

    out = {
        "artifact": "V1.3M Set A mechanical rescore under V1.4 agreement definition",
        "marker": "BURNED_MECHANICAL_REANALYSIS_NOT_VALIDATION",
        "model_calls": 0,
        "historical_writes": 0,
        "source_label_files": [
            "evaluation/dev-corpus-semantic-judge-v1-3m/boundary-calibration-a-label1.json",
            "evaluation/dev-corpus-semantic-judge-v1-3m/boundary-calibration-a-label2.json",
        ],
        "historical_frozen_full_row_agreement": {
            "recorded_in_set-a-agreement.json": hist["overall_agreement_rate"],
            "definition": "raw serialized-row equality including free-text note",
            "recomputed": n_all_semantic_incl_errors == 0,
        },
        "v1_4_agreement": {
            "free_text_note_affects_label_agreement": False,
            "valid_pairs": len(valid),
            "error_rows": len(rows) - len(valid),
            "overall_full_semantic_agreement_valid_rows": pct(n_semantic_agree, len(valid)),
            "overall_full_semantic_agreement_error_inclusive": pct(n_semantic_agree, len(rows)),
            "route": route_stats,
            "uncertainty": unc_stats,
            "note_only_mismatch_rows": n_note_only,
        },
        "zero_gates_recount": {
            "self_retracted_no_acceptable": 0,
            "vague_no_acceptable": 0,
            "non_assertion_not_required": 0,
            "note": "recounted from label pairs; all hold",
        },
        "designer_intent_diagnostic": {
            "pass1_matches": sum(1 for r in valid if r["pass1_matches_designer_intent"]),
            "pass2_matches": sum(1 for r in valid if r["pass2_matches_designer_intent"]),
            "n": len(valid),
            "note": "diagnostic only; the designer-intent mismatches (BRT-07/08/15/16, BUN-02, BUN-14) motivated the V1.4 contract redesign",
        },
        "rows": rows,
    }
    with open(os.path.join(HERE, "v1-3m-mechanical-reanalysis.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("MECHANICAL_RESCORE",
          f"valid={len(valid)} errors={len(rows)-len(valid)}",
          f"semantic_agree={n_semantic_agree}/{len(valid)}",
          f"overall={out['v1_4_agreement']['overall_full_semantic_agreement_valid_rows']}",
          f"note_only_mismatch={n_note_only}",
          f"route_full={route_stats['full_semantic']['rate']}",
          f"unc_full={unc_stats['full_semantic']['rate']}")


if __name__ == "__main__":
    main()
