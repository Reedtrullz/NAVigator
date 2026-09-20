#!/usr/bin/env python3
"""Build consensus, validation and coverage artifacts from stored ASTRA results."""
import json, hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACKETS = os.path.join(ROOT, "evaluation/measurement-v3-human-review-batch-2-repaired/human-review-packets.jsonl")

CRIT_STATES = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT", "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED"}
MATCH_ENUM = {"MATCH", "NO_MATCH", "UNRESOLVED"}
COMMIT_ENUM = {"ASSERTED", "HEDGED_ASSERTION", "QUOTED_ONLY", "HYPOTHETICAL_ONLY", "NEGATED", "SELF_RETRACTED", "NONCOMMITTAL", "UNRESOLVED"}
REQ_CRIT = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}

def load(f):
    return {json.loads(l)["packet_id"]: json.loads(l) for l in open(os.path.join(HERE, f)) if l.strip()}

def main():
    packets = {json.loads(l)["packet_id"]: json.loads(l) for l in open(PACKETS) if l.strip()}
    order = json.load(open(os.path.join(ROOT, "evaluation/measurement-v3-human-review-batch-2-repaired/review-order.json")))
    A, B = load("astra-pass-a.jsonl"), load("astra-pass-b.jsonl")
    assert set(A) == set(B) == set(packets) == set(order["packet_ids"]), "coverage mismatch"

    evidence = {"artifact": "evidence-validation", "passes_checked": 148, "violations": [], "empty_span_legal_cases": 0, "empty_span_required_missing": 0}
    consensus, disagreements, human_burden = [], [], []
    counts = {"packets_total": 74, "valid_astra_a": 0, "valid_astra_b": 0, "exact_semantic_agreement": 0,
              "disagreement": 0, "invalid_pass_packets": 0}
    by_lane = {"critical_condition": {"agreement": 0, "disagreement": 0, "invalid": 0},
               "forbidden_claim": {"agreement": 0, "disagreement": 0, "invalid": 0}}
    labels = {"critical_evidence_state": {}, "criterion_semantic_match": {}, "speaker_commitment": {}}

    def validate(pid, rec):
        if rec["status"] == "TRANSPORT_ERROR":
            return "TRANSPORT_ERROR"
        res = rec.get("result", {})
        sut = packets[pid]["sut_output"]
        spans = res.get("evidence_spans", [])
        if "critical_evidence_state" in res:
            if res.get("critical_evidence_state") not in CRIT_STATES:
                return "INVALID_ENUM"
            need = res["critical_evidence_state"] in REQ_CRIT
        elif "criterion_semantic_match" in res:
            if res.get("criterion_semantic_match") not in MATCH_ENUM or res.get("speaker_commitment") not in COMMIT_ENUM:
                return "INVALID_ENUM"
            need = res["criterion_semantic_match"] == "MATCH" and res.get("speaker_commitment") != "UNRESOLVED"
        else:
            return "INVALID_SCHEMA"
        if not isinstance(spans, list) or not all(isinstance(s, str) for s in spans):
            return "INVALID_SPANS_TYPE"
        nonverb = [s for s in spans if s not in sut]
        if nonverb:
            evidence["violations"].append({"packet_id": pid, "pass": rec["pass"], "non_verbatim_spans": nonverb})
            return "INVALID_MODEL_REVIEW"
        if need and not spans:
            evidence["empty_span_required_missing"] += 1
            return "INVALID_MODEL_REVIEW"
        if not need and not spans:
            evidence["empty_span_legal_cases"] += 1
        return "OK"

    for pid in order["packet_ids"]:
        p = packets[pid]
        dim = p["dimension"]
        ra, rb = A[pid], B[pid]
        va, vb = validate(pid, ra), validate(pid, rb)
        if va == "OK":
            counts["valid_astra_a"] += 1
        if vb == "OK":
            counts["valid_astra_b"] += 1

        def auth_fields(res):
            if "critical_evidence_state" in res:
                return {"critical_evidence_state": res.get("critical_evidence_state")}
            return {"criterion_semantic_match": res.get("criterion_semantic_match"),
                    "speaker_commitment": res.get("speaker_commitment")}

        fa, fb = auth_fields(ra.get("result", {})), auth_fields(rb.get("result", {}))
        entry = {"packet_id": pid, "dimension": dim, "packet_sha256": p["packet_sha256"],
                 "astra_a": {"validity": va, "authoritative_fields": fa,
                             "evidence_spans": ra.get("result", {}).get("evidence_spans", [])},
                 "astra_b": {"validity": vb, "authoritative_fields": fb,
                             "evidence_spans": rb.get("result", {}).get("evidence_spans", [])}}

        if va != "OK" or vb != "OK":
            status = "INVALID_MODEL_REVIEW"
            entry["consensus_status"] = status
            entry["invalid_passes"] = [s for s, v in (("ASTRA_A", va), ("ASTRA_B", vb)) if v != "OK"]
            counts["invalid_pass_packets"] += 1
            by_lane[dim]["invalid"] += 1
            human_burden.append({"packet_id": pid, "reason": status, "detail": entry["invalid_passes"]})
        elif fa == fb:
            status = "LLM_CONSENSUS"
            entry["consensus_status"] = status
            entry["final_label"] = "LLM_REVIEWED"
            counts["exact_semantic_agreement"] += 1
            by_lane[dim]["agreement"] += 1
            for k, v in fa.items():
                labels[k][v] = labels[k].get(v, 0) + 1
        else:
            status = "LLM_REVIEW_DISAGREEMENT"
            entry["consensus_status"] = status
            entry["final_label"] = status
            counts["disagreement"] += 1
            by_lane[dim]["disagreement"] += 1
            diff = [k for k in fa if fa[k] != fb.get(k)]
            entry["differing_fields"] = diff
            disagreements.append(entry)
            human_burden.append({"packet_id": pid, "reason": status, "differing_fields": diff,
                                 "astra_a": fa, "astra_b": fb})
        consensus.append(entry)

    counts["agreement_by_lane"] = by_lane
    counts["label_distributions_consensus_packets"] = labels

    def dump(name, obj):
        with open(os.path.join(HERE, name), "w") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")

    dump("consensus-results.json", {"artifact": "astra-consensus-results", "summary": counts, "packets": consensus})
    dump("disagreements.json", {"artifact": "astra-disagreements", "count": len(disagreements), "packets": disagreements})
    dump("evidence-validation.json", evidence)
    dump("review-coverage.json", counts)
    dump("human-adjudication-packet.json", {"artifact": "optional-human-adjudication-set",
        "note": "LLM_REVIEW_DISAGREEMENT and INVALID_MODEL_REVIEW cases only; no AI decisions populate verdicts",
        "count": len(human_burden), "cases": human_burden})
    print(json.dumps(counts, indent=1))
    print("evidence violations:", len(evidence["violations"]), "empty_span_legal:", evidence["empty_span_legal_cases"])

if __name__ == "__main__":
    main()
