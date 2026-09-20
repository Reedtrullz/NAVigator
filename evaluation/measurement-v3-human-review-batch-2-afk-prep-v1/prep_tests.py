#!/usr/bin/env python3
"""AFK prep V1: synthetic E2E (F) + negative test matrix (G).

All tests run on SYN-* packets only. Real packet IDs are asserted absent.
Every negative case must fail closed (>=1 validator error).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_lib as P

REAL_IDS = {p["packet_id"] for p in P.load_packets()}


def check_real_id_leak(rows):
    bad = [r.get("packet_id") for r in rows if isinstance(r, dict) and r.get("packet_id") in REAL_IDS]
    assert not bad, "REAL PACKET ID IN SYNTHETIC DATA: " + str(bad)
    bad2 = [pid for pid in REAL_IDS if "SYN" in pid]
    assert not bad2


def parse_jsonl(text):
    rows, parse_errors = [], []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception as e:
            parse_errors.append({"line": i, "error": "malformed JSONL: " + str(e)[:80],
                                 "truncated_row_suspected": not line.rstrip().endswith("}")})
    return rows, parse_errors


def main():
    packets = P.make_synthetic_packets()
    for p in packets:
        assert p["packet_id"].startswith("PKT-SYN-"), p["packet_id"]
    by_id = {p["packet_id"]: p for p in packets}
    order = [p["packet_id"] for p in packets]

    e2e = P.run_synthetic_e2e()
    check_real_id_leak(e2e.get("steps", []) and [] or [])
    results = []

    def case(cid, rows, parse_errors=(), packet_map=None, order_list=None):
        errs = []
        seen = set()
        for r in rows:
            errs.extend(P.validate_review_row(r, packet_map or by_id, seen))
        if order_list is not None and order_list != order:
            errs.append("review order corruption: sequence differs from frozen order")
        if len((packet_map or by_id)) != len(packets):
            errs.append("missing packet in packet set")
        failed = bool(errs)
        results.append({"case": cid, "injected": cid, "failed_closed": failed,
                        "first_error": errs[0] if errs else None,
                        "parse_errors": list(parse_errors)})

    base_crit = {"critical_evidence_state": "CLEAR_TRIGGER_SUPPORT", "evidence_spans": [], "note": ""}
    base_forb = {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED", "evidence_spans": [], "note": ""}
    def row(pid, j, **over):
        r = {"packet_id": pid, "case_id": by_id[pid]["case_id"], "reviewer_id": "SYNTHETIC-REVIEWER",
             "contract_version": "semantic-judge-contract-v1-4", "reviewed_utc": "2026-09-15T00:00:00Z", "judgment": j}
        r.update(over)
        return r

    unknown_row = {"packet_id": "PKT-SYN-NOPE", "case_id": "SYN-NOPE", "reviewer_id": "SYNTHETIC-REVIEWER",
                   "contract_version": "semantic-judge-contract-v1-4", "reviewed_utc": "2026-09-15T00:00:00Z",
                   "judgment": base_crit}
    case("unknown_packet_id", [unknown_row]);
    case("wrong_packet_sha", [row("PKT-SYN-CRIT-1", base_crit, packet_sha256="0" * 64)]);
    case("invalid_enum", [row("PKT-SYN-CRIT-1", {"critical_evidence_state": "MAYBE", "evidence_spans": [], "note": ""})]);
    case("missing_required_enum", [row("PKT-SYN-CRIT-1", {"critical_evidence_state": "", "evidence_spans": [], "note": ""})]);
    case("evidence_span_not_present", [row("PKT-SYN-FORB-1", dict(base_forb, evidence_spans=["this sentence is nowhere in the SUT output"]))]);
    case("evidence_span_from_forbidden_location",
         [row("PKT-SYN-FORB-1", dict(base_forb, evidence_spans=[by_id["PKT-SYN-FORB-1"]["criterion"]]))],
         );
    case("duplicate_review", [row("PKT-SYN-CRIT-1", base_crit), row("PKT-SYN-CRIT-1", base_crit)]);
    case("wrong_reviewer", [row("PKT-SYN-CRIT-1", base_crit, reviewer_id="REVIEWER-02")]);
    case("wrong_contract_version", [row("PKT-SYN-CRIT-1", base_crit, contract_version="semantic-judge-contract-v9")]);
    case("unexpected_field", [row("PKT-SYN-CRIT-1", base_crit, model_verdict="LEAK")]);
    case("missing_packet_in_set", [row("PKT-SYN-CRIT-1", base_crit)], packet_map={k: v for k, v in by_id.items() if k != "PKT-SYN-CRIT-2"});
    dup_set = [dict(p) for p in packets] + [dict(p) for p in packets if p["packet_id"] == "PKT-SYN-CRIT-1"]
    case("duplicate_packet_in_set", [], packet_map={p["packet_id"]: p for p in dup_set},
         order_list=order + ["PKT-SYN-CRIT-1"]);
    case("review_order_corruption", [], order_list=["PKT-SYN-FORB-1"] + order[:-1]);
    # same set, different sequence must also fail closed
    case("review_order_transposition", [], order_list=order[::-1]);
    case("attempt_bind_to_batch1_packet", [row("PKT-SYN-CRIT-1", base_crit, packet_sha256="batch1-packet-sha")]
         );
    case("attempt_bind_to_superseded_criterion_packet", [row("PKT-SYN-CRIT-1", base_crit, packet_sha256="superseded-sha")]
         );

    rows, parse_errors = parse_jsonl('{"packet_id": "PKT-SYN-CRIT-1", "judg')
    results.append({"case": "malformed_jsonl", "failed_closed": bool(parse_errors),
                    "first_error": parse_errors[0]["error"] if parse_errors else None, "parse_errors": parse_errors})
    rows2, pe2 = parse_jsonl('{"packet_id": "PKT-SYN-CRIT-1", "reviewer_id": "SYNTHETIC-REVIEWER"}'[:-3])
    results.append({"case": "truncated_last_row", "failed_closed": bool(pe2),
                    "first_error": pe2[0]["error"] if pe2 else None, "parse_errors": pe2})

    all_fail = all(r["failed_closed"] for r in results)
    out = {"artifact": "negative-test-matrix", "task_id": "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1",
           "synthetic_only": True, "real_packet_ids_used": 0,
           "cases": results, "cases_total": len(results), "all_failed_closed": all_fail,
           "verdict": "PASS" if all_fail and e2e["verdict"] == "PASS" else "FAIL",
           "synthetic_e2e": e2e}
    with open(os.path.join(HERE, "negative-test-matrix.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("NEGATIVE MATRIX:", out["verdict"], "| cases:", len(results), "| e2e:", e2e["verdict"])
    for r in results:
        if not r["failed_closed"]:
            print("  NOT FAIL-CLOSED:", r["case"])
    sys.exit(0 if out["verdict"] == "PASS" else 1)

if __name__ == "__main__":
    main()
