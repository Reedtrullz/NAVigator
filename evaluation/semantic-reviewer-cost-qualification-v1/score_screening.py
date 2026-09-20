#!/usr/bin/env python3
"""Score frozen Stage-1 screening outputs against the frozen contract gates.

Run only AFTER run_screening.py has frozen all candidate outputs.
Reference fields come from the frozen reference corpus; the reference is the
authoritative frozen semantic reference, not human ground truth.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GATES = json.load(open(os.path.join(HERE, "qualification-contract.json"),
                       encoding="utf-8"))["gates_allowed_error_counts"]
SCREEN = json.load(open(os.path.join(HERE, "screening-results.json"),
                        encoding="utf-8"))["candidates"]
REF = {}
with open(os.path.join(HERE, "reference-corpus.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            # 12 diagnostic rows carry diagnostic_observation; screening
            # partitions never reference them. Guard the lookup here so the
            # scorer does not need to embed lane knowledge.
            if "observation" in r:
                REF[r["canonical_hash"]] = r["observation"]["authoritative_fields"]


def score_candidate(lane):
    cand = SCREEN[cand_id]
    gates = GATES[lane]["screening"]
    rows = [r for r in cand["results"] if r["lane"] == lane]
    parsed_rows = [r for r in rows if "parsed" in r]
    ok_rows = [r for r in rows if r["status"] == "OK"]
    # Spec section 26: compare AUTHORITATIVE semantic fields only. The model
    # response carries extra fields (rationale, evidence_spans); they must not
    # be part of the semantic comparison. Authoritative field set is taken
    # from the frozen reference row for that packet's lane.
    def authoritative_view(parsed, ref):
        return {k: parsed[k] for k in ref if k in parsed}

    agree = [r for r in ok_rows
             if authoritative_view(r["parsed"], REF[r["canonical_hash"]])
             == REF[r["canonical_hash"]]]
    escape = []
    for r in parsed_rows:
        ref = REF[r["canonical_hash"]]
        p = r["parsed"]
        if lane == "critical_condition":
            if (ref.get("critical_evidence_state")
                    == "CLEAR_NON_TRIGGER_SUPPORT"
                    and p.get("critical_evidence_state")
                    == "CLEAR_TRIGGER_SUPPORT"):
                escape.append(r["canonical_hash"])
        else:
            if (ref.get("criterion_semantic_match") == "MATCH"
                    and ref.get("speaker_commitment") == "NEGATED"
                    and p.get("criterion_semantic_match") == "NO_MATCH"):
                escape.append(r["canonical_hash"])
    schema_rate = (len(parsed_rows) / len(rows)) if rows else 0.0
    agreement = (len(agree) / len(ok_rows)) if ok_rows else 0.0
    max_escape = gates["catastrophic_escape_max"]
    passed = (schema_rate >= gates["schema_valid_rate_min"]
              and len(escape) <= max_escape)
    return {
        "rows": len(rows),
        "ok": len(ok_rows),
        "transport_errors": sum(1 for r in rows
                                if r["status"] == "TRANSPORT_ERROR"),
        "invalid_json": sum(1 for r in rows
                            if r["status"] == "INVALID_JSON"),
        "invalid_model_reviews": sum(1 for r in rows
                                     if r["status"] == "INVALID_MODEL_REVIEW"),
        "schema_valid_rate": round(schema_rate, 4),
        "reference_agreement_among_ok": round(agreement, 4),
        "conservative_escape_count": len(escape),
        "conservative_escape_hashes": escape,
        "catastrophic_escape_max": max_escape,
        "screen_pass": passed,
    }


out = {"scoring_rule": "frozen contract gates; reference = frozen authoritative semantic reference, not human ground truth",
       "candidates": {}}
for cand_id in SCREEN:
    out["candidates"][cand_id] = {
        lane: score_candidate(lane) for lane in ("forbidden_claim",
                                                 "critical_condition")
    }
with open(os.path.join(HERE, "screening-scored.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps({cid: {l: {k: v for k, v in s.items()
                            if not k.endswith("hashes")}
                        for l, s in lanes.items()}
                  for cid, lanes in out["candidates"].items()},
                 ensure_ascii=False, indent=1))
