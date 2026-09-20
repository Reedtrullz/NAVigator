"""Generate 40 workflow unit fixtures for the V2.12 uncertainty lane.
Reviewer outputs are fixture data, not model calls. Mirrors V2.6 pattern."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

CTX = "Bruker spor om kommunalt tilbud."
CRIT_REQ = "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert."
CRIT_NA = "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud."
CRIT_COMP = "Kriteriet krever baade usikkerhetsekspresjon og fravaer av overkonklusjon."
SUT = "Jeg har ikke verifisert tilgangen, og det er ikke sikkert du far plass."

F = []
def add(fid, category, crit, sut, case_extra=None, reviews=None, adjudication=None,
        expect=None, expect_after_adjudication=None):
    case = {"case_id": fid, "criterion": crit, "case_context": CTX, "sut_output": sut}
    if case_extra:
        case.update(case_extra)
    fx = {"fixture_id": fid, "category": category, "case": case,
          "reviews": reviews or [], "expect": expect or {}}
    if adjudication is not None:
        fx["adjudication"] = adjudication
    if expect_after_adjudication is not None:
        fx["expect_after_adjudication"] = expect_after_adjudication
    F.append(fx)

def j(mode, behavior, comps=None, spans=None):
    d = {"uncertainty_requirement_mode": mode, "uncertainty_output_behavior": behavior,
         "evidence_spans": spans or []}
    if comps is not None:
        d["compound_components"] = comps
    return d

def rv(rid, judgment):
    return {"reviewer_id": rid, "judgment": judgment}

# wf01-08: single-review derivation happy paths
add("WF12-01", "derivation", "Kriteriet stiller ingen usikkerhetskrav.", "Tilbudet har apning hver tirsdag.",
    reviews=[rv("R1", j("NONE", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "SINGLE_HUMAN_REVIEW", "final_verdict": "NOT_REQUIRED"})
add("WF12-02", "derivation", CRIT_REQ, "Du ma ta kontakt; vi kan ikke love at tilgangen fungerer.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION", spans=["vi kan ikke love at tilgangen fungerer"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF12-03", "derivation", CRIT_REQ, "Det er kanskje ikke tilgang for oeblikket.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE", spans=["kanskje ikke tilgang"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF12-04", "derivation", CRIT_REQ, "Tilgangen er vaerifisert og fullt operativ.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})
add("WF12-05", "derivation_unc_a1", CRIT_REQ, "Det er usikkert. Nei, det er helt sikkert. Kanskje.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "CONTRADICTORY_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF12-06", "derivation", CRIT_NA, "Jeg vet ikke om det finnes tilbud, saa jeg konkluderer ikke.",
    reviews=[rv("R1", j("NON_ASSERTION_CONSTRAINT", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF12-07", "derivation_unc_a2", CRIT_REQ, "Hmm... altsaa... typisk slikt.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "UNCLEAR_PROSE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF12-08", "derivation", CRIT_COMP, "Tilgangen er kanskje ok.",
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "HEDGE"], ["NON_ASSERTION", "NONE"]]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})

# wf09-16: invalid review paths -> HUMAN_REVIEW_INVALID
add("WF12-09", "invalid_span", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION", spans=["ikke en del av teksten"]))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-10", "invalid_field", CRIT_REQ, SUT,
    reviews=[rv("R1", {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION", "evidence_spans": []})],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-11", "invalid_mode_combo", CRIT_REQ, SUT,
    reviews=[rv("R1", j("NONE", "HEDGE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-12", "invalid_compound_empty", CRIT_COMP, SUT,
    reviews=[rv("R1", j("COMPOUND", None, comps=[]))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-13", "invalid_compound_kind", CRIT_COMP, SUT,
    reviews=[rv("R1", j("COMPOUND", None, comps=[["GUESS", "HEDGE"]]))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-14", "invalid_contract_version", CRIT_REQ, SUT,
    reviews=[{"reviewer_id": "R1", "contract_version": "semantic-judge-contract-v1-4",
              "judgment": j("EXPLICIT_LIMITATION", "HEDGE")}],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-15", "invalid_mode_value", CRIT_REQ, SUT,
    reviews=[rv("R1", j("PARTIAL", "NONE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF12-16", "invalid_behavior_value", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "TOTALLY_FINE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})

# wf17-24: state machine
add("WF12-17", "dual_agreement", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION")), rv("R2", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED", "final_verdict": "SATISFIED"})
add("WF12-18", "dual_disagreement", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE")), rv("R2", j("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"))],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "final_is_none": True})
ADJ_OK = {"case_id": "WF12-19", "contract_version": "semantic-judge-contract-v2-7e",
          "adjudicated": True, "model_outputs_visible_to_adjudicator": False,
          "final_judgment": j("EXPLICIT_LIMITATION", "HEDGE"),
          "adjudication_note": "hedge is the defensible reading"}
add("WF12-19", "adjudication", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE")), rv("R2", j("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"))],
    adjudication=ADJ_OK,
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT"},
    expect_after_adjudication={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_WITH_ADJUDICATION", "final_verdict": "PARTIAL"})
ADJ_BAD = {"case_id": "WF12-20", "contract_version": "semantic-judge-contract-v2-7e",
           "adjudicated": True, "model_outputs_visible_to_adjudicator": True,
           "final_judgment": j("EXPLICIT_LIMITATION", "HEDGE"),
           "adjudication_note": "saw model output, forbidden"}
add("WF12-20", "adjudication_invalid", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE")), rv("R2", j("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"))],
    adjudication=ADJ_BAD,
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "adjudication_error": True},
    expect_after_adjudication={"status": "HUMAN_REVIEW_DISAGREEMENT"})
add("WF12-21", "duplicate_review", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE")), rv("R1", j("EXPLICIT_LIMITATION", "HEDGE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "duplicate_rejected": True})
add("WF12-22", "pending_fail_closed", CRIT_REQ, SUT,
    expect={"status": "HUMAN_REVIEW_PENDING", "final_is_none": True})
add("WF12-23", "packet_leakage", CRIT_REQ, SUT,
    case_extra={"gold": "VIOLATED"},
    expect={"packet_error": True})
ADJ_NOSTATE = {"case_id": "WF12-24", "contract_version": "semantic-judge-contract-v2-7e",
               "adjudicated": True, "model_outputs_visible_to_adjudicator": False,
               "final_judgment": j("EXPLICIT_LIMITATION", "HEDGE"),
               "adjudication_note": "no disagreement exists"}
add("WF12-24", "adjudication_wrong_state", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE"))],
    adjudication=ADJ_NOSTATE,
    expect={"status": "HUMAN_REVIEW_RESOLVED", "adjudication_error": True})

# wf25-32: routing / provenance / invariants
add("WF12-25", "routing_flag", CRIT_REQ, SUT,
    reviews=[rv("R1", j("NONE", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "routed_automated_authoritative_false": True})
add("WF12-26", "provenance_sequence", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]})
add("WF12-27", "provenance_sha", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "provenance_has_packet_sha": True})
add("WF12-28", "packet_clean", CRIT_REQ, SUT,
    reviews=[rv("R1", j("NONE", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "packet_has_no_forbidden_keys": True})
add("WF12-29", "compound_dual_agreement", CRIT_COMP, SUT,
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "NONE"]])),
             rv("R2", j("COMPOUND", None, comps=[["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "NONE"]]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED", "final_verdict": "SATISFIED"})
add("WF12-30", "compound_dual_disagreement", CRIT_COMP, SUT,
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "NONE"]])),
             rv("R2", j("COMPOUND", None, comps=[["EXPRESSION", "HEDGE"], ["NON_ASSERTION", "NONE"]]))],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "final_is_none": True})
add("WF12-31", "invalid_then_valid", CRIT_REQ, SUT,
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "NOT_A_BEHAVIOR")),
             rv("R1", j("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "SINGLE_HUMAN_REVIEW"})
add("WF12-32", "buckets", CRIT_REQ, SUT,
    expect={"status": "HUMAN_REVIEW_PENDING", "bucket": "unresolved"})

# wf33-40: mechanical derivation integrity through the frozen V2.7E tables
add("WF12-33", "derivation", CRIT_NA, "Ved ausikkerhet anbefales nav-kontakt.",
    reviews=[rv("R1", j("NON_ASSERTION_CONSTRAINT", "PARTIAL_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF12-34", "derivation_v14_rule", CRIT_COMP, "Tilgang kan ikke bekreftes.",
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "OVERCONFIDENT_ASSERTION"], ["NON_ASSERTION", "NONE"]]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF12-35", "derivation", CRIT_COMP, "Ting er usikre.",
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "UNCLEAR_PROSE"], ["NON_ASSERTION", "UNCLEAR_PROSE"]]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF12-36", "derivation", CRIT_NA, "Det er garantert ikke noe tilbud i kommunen.",
    reviews=[rv("R1", j("NON_ASSERTION_CONSTRAINT", "CONTRADICTORY_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})
add("WF12-37", "derivation_unc_a2", CRIT_REQ, "...",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "UNCLEAR_PROSE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF12-38", "derivation", CRIT_REQ, "Det kan vaere begrenset tilgang naa.",
    reviews=[rv("R1", j("EXPLICIT_LIMITATION", "HEDGE", spans=["kan vaere begrenset tilgang"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF12-39", "derivation", CRIT_COMP, "Jeg har ikke verifisert tilgangen; kommunen kan ha tilbud.",
    reviews=[rv("R1", j("COMPOUND", None, comps=[["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "NONE"]]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF12-40", "derivation", CRIT_NA, "Saa langt kan det konkludererest at kommunen mangler tilbud.",
    reviews=[rv("R1", j("NON_ASSERTION_CONSTRAINT", "OVERCONFIDENT_ASSERTION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})

out = {"artifact": "workflow-test-fixtures-v2-12", "n_fixtures": len(F),
       "provenance": "Synthetic workflow unit fixtures; reviewer outputs are fixture data, no model calls.",
       "fixtures": F}
with open(os.path.join(DIR, "workflow-test-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("wrote", len(F), "workflow fixtures")
