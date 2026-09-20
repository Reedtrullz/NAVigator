#!/usr/bin/env python3
"""Curation pass 2: independent re-derivation of gold from frozen semantics.

Pass 1 gold lives in official-validation-fixtures.json. This script re-labels
every fixture from its tag taxonomy via rule tables written independently of
pass 1's gold_intermediate fields, then compares.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from judge_core_v2_2 import derive_final  # noqa: E402

HERE = Path(__file__).parent

TAG_RULES_M1 = {
    "clear_assertion": {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"},
    "hedged_positive": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"},
    "strongly_hedged_asserted": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"},
    "hypothetical": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HYPOTHETICAL_ONLY"},
    "quoted": {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"},
    "negated": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"},
    "self_retracted": {"criterion_semantic_match": "MATCH", "speaker_commitment": "SELF_RETRACTED"},
    "noncommittal": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NONCOMMITTAL"},
    "near_match": {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"},
    "near_match_no_match": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "UNRESOLVED"},
    "no_match": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "UNRESOLVED"},
}
TAG_RULES_M2 = {
    "clear_trigger": {"critical_evidence_state": "CLEAR_TRIGGER_SUPPORT"},
    "clear_non_trigger": {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"},
    "ambiguous": {"critical_evidence_state": "AMBIGUOUS_OR_CONFLICTING"},
    "conflicting": {"critical_evidence_state": "AMBIGUOUS_OR_CONFLICTING"},
    "insufficient": {"critical_evidence_state": "INSUFFICIENT_TO_DECIDE"},
    "hedged_triggered": {"critical_evidence_state": "CLEAR_TRIGGER_SUPPORT"},
    "quoted": {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"},
    "hypothetical": {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"},
    "adversarial": {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"},
    "control_ordinary": {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"},
}
TAG_RULES_ROUTE = {
    "acceptable_route": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED", "proposed_verdict": "ACCEPTABLE"},
    "wrong_route": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED", "proposed_verdict": "NO_ACCEPTABLE_ROUTE"},
    "partial_route": {"route_proposition_present": "YES", "route_speaker_commitment": "HEDGED_ASSERTION", "proposed_verdict": "PARTIAL"},
    "no_acceptable": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED", "proposed_verdict": "NO_ACCEPTABLE_ROUTE"},
    "self_retracted_route": {"route_proposition_present": "YES", "route_speaker_commitment": "SELF_RETRACTED", "proposed_verdict": "UNRESOLVED"},
    "vague_route": {"route_proposition_present": "NO", "route_speaker_commitment": "UNRESOLVED", "proposed_verdict": "UNRESOLVED"},
    "negated_route": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED", "proposed_verdict": "ACCEPTABLE"},
    "multiple_routes": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED", "proposed_verdict": "ACCEPTABLE"},
    "hypothetical_route": {"route_proposition_present": "YES", "route_speaker_commitment": "HYPOTHETICAL_ONLY", "proposed_verdict": "UNRESOLVED"},
    "quoted_route": {"route_proposition_present": "YES", "route_speaker_commitment": "QUOTED_ONLY", "proposed_verdict": "UNRESOLVED"},
}
TAG_RULES_UNC = {
    "none": {"uncertainty_requirement_mode": "NONE"},
    "explicit_limitation_satisfied": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION", "uncertainty_output_behavior": "EXPLICIT_LIMITATION"},
    "explicit_limitation_violated": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION", "uncertainty_output_behavior": "OVERCONFIDENT_ASSERTION"},
    "non_assertion_satisfied": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT", "uncertainty_output_behavior": "EXPLICIT_LIMITATION"},
    "non_assertion_violated": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT", "uncertainty_output_behavior": "OVERCONFIDENT_ASSERTION"},
    "non_assertion_ambiguous": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT", "uncertainty_output_behavior": "UNRESOLVED"},
    "compound_satisfied": {"uncertainty_requirement_mode": "COMPOUND",
                           "compound_components": [{"kind": "EXPRESSION", "behavior": "EXPLICIT_LIMITATION"},
                                                   {"kind": "NON_ASSERTION", "behavior": "NONE"}]},
    "compound_partial": {"uncertainty_requirement_mode": "COMPOUND",
                         "compound_components": [{"kind": "EXPRESSION", "behavior": "EXPLICIT_LIMITATION"},
                                                 {"kind": "NON_ASSERTION", "behavior": "NONE"}]},
    "compound_violated": {"uncertainty_requirement_mode": "COMPOUND",
                          "compound_components": [{"kind": "EXPRESSION", "behavior": "OVERCONFIDENT_ASSERTION"},
                                                  {"kind": "NON_ASSERTION", "behavior": "OVERCONFIDENT_ASSERTION"}]},
    "hedged_partial": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION", "uncertainty_output_behavior": "PARTIAL_LIMITATION"},
}
TAG_RULES_FORBIDDEN_CTRL = {
    "control_straightforward": {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"},
    "control_negated": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"},
    "control_hedged": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"},
    "control_noncommittal": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NONCOMMITTAL"},
    "control_quoted": {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"},
    "control_no_match": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "UNRESOLVED"},
}


def rules_for(f):
    if f["family"] == "m1":
        return TAG_RULES_M1[f["tag"]]
    if f["family"] == "m2":
        return TAG_RULES_M2[f["tag"]]
    if f["dimension"] == "critical_condition":
        return TAG_RULES_M2[f["tag"]]
    if f["dimension"] == "route_correctness":
        return TAG_RULES_ROUTE[f["tag"]]
    if f["dimension"] == "required_uncertainty":
        return TAG_RULES_UNC[f["tag"]]
    if f["dimension"] == "forbidden_claim":
        return TAG_RULES_FORBIDDEN_CTRL[f["tag"]]
    raise KeyError(f["id"])


def main():
    data = json.loads((HERE / "official-validation-fixtures.json").read_text(encoding="utf-8"))
    disputes = []
    shape_disputes = []
    n = len(data["fixtures"])
    for f in data["fixtures"]:
        inter2 = rules_for(f)
        verdict2, _ = derive_final(f["dimension"], inter2)
        verdict1 = f["gold_verdict"]
        if verdict2 != verdict1:
            disputes.append({"id": f["id"], "pass1_inter": f["gold_intermediate"], "pass1_verdict": verdict1, "pass2_inter": inter2, "pass2_verdict": verdict2})
        elif inter2 != f["gold_intermediate"]:
            shape_disputes.append({"id": f["id"], "pass1_inter": f["gold_intermediate"], "pass2_inter": inter2,
                                   "note": "verdict identical; pass-1 hand-authored evidence fields not re-derived by rule tables"})
    agree_n = n - len(disputes)
    prefix = {"m1": "V22-M1-", "m2": "V22-M2-", "control": "V22-C-"}
    by_family = {}
    for fam, p in prefix.items():
        fl = [f for f in data["fixtures"] if f["id"].startswith(p)]
        d = [x for x in disputes if x["id"].startswith(p)]
        by_family[fam] = {"n": len(fl), "agreement": round((len(fl) - len(d)) / len(fl), 4)}
    out = {
        "artifact": "curator-pass2.json",
        "mode": "independent_rederivation_from_tag_taxonomy",
        "n": n,
        "agreement": round(agree_n / n, 4),
        "verdict_level_agreement": round((n - len(disputes)) / n, 4),
        "by_family": by_family,
        "disputes": disputes,
        "shape_only_differences": shape_disputes,
        "note": "disputes require fixture burn/replace per spec section 31 before freeze",
    }
    (HERE / "curator-pass2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n", "agreement", "by_family")}, indent=2))
    for x in disputes:
        print("DISPUTE", x["id"], "pass1:", x["pass1_verdict"], "pass2:", x["pass2_verdict"])


if __name__ == "__main__":
    main()
