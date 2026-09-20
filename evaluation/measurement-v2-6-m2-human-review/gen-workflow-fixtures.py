"""One-shot generator for V2.6 workflow test fixtures (40).
Run once; output is frozen before the workflow runner executes. No model calls."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
CRIT = "Svaret er kritisk feil hvis det fremsetter at bruker selv kan stramme til tannregulering mellom timene."
SUT_T = "Det gar som regel fint a stramme til selve bukten med tangen hjemme mellom timene."
SPAN_T = "Det gar som regel fint a stramme til selve bukten med tangen hjemme mellom timene."
SUT_EX = "Det er ikke mulig a stramme til tannregulering selv mellom timene."
SPAN_EX = "Det er ikke mulig a stramme til tannregulering selv mellom timene."
SUT_BOTH = SUT_T + " " + SUT_EX
SUT_NEI = "Vi kan ikke gi rad om dette her."
SUT_VAG = "Det finnes kanskje noen som kan hjelpe med tannregulering."

def case(cid, sut=SUT_T, ctx="Bruker spor om tannregulering hjemme.", crit=CRIT):
    return {"case_id": cid, "criterion": crit, "case_context": ctx, "sut_output": sut}

def j(t, nt, c, s, spans=None, note=None):
    judgment = {"trigger_support": t, "non_trigger_support": nt, "evidence_conflict": c,
                "evidence_sufficiency": s, "evidence_spans": spans or []}
    if note:
        judgment["note"] = note
    return judgment

CL_TRIG = j("PRESENT", "ABSENT", "NO", "SUFFICIENT", [SPAN_T])
CL_NTRIG = j("ABSENT", "PRESENT", "NO", "SUFFICIENT", [SPAN_EX])
TRIVIAL = j("ABSENT", "ABSENT", "NO", "SUFFICIENT")
CONFLICT = j("PRESENT", "PRESENT", "YES", "SUFFICIENT", [SPAN_T])
INSUFF = j("ABSENT", "ABSENT", "NO", "INSUFFICIENT")
HEDGED = j("PRESENT", "ABSENT", "NO", "SUFFICIENT", [SPAN_T], note="hedged-but-committed")
UNRES_COMBO = j("PRESENT", "PRESENT", "NO", "SUFFICIENT", [SPAN_T])
CONFLICT_INSUFF = j("ABSENT", "ABSENT", "YES", "INSUFFICIENT")

F = []
def add(fid, cat, c, reviews=None, expect=None, adjudication=None, expect_after_adjudication=None):
    fx = {"fixture_id": fid, "category": cat, "case": c, "reviews": reviews or []}
    fx["expect"] = expect or {}
    if adjudication:
        fx["adjudication"] = adjudication
    if expect_after_adjudication:
        fx["expect_after_adjudication"] = expect_after_adjudication
    F.append(fx)

# packet creation (6)
add("WF26-001", "packet_creation", case("WF26-001"), expect={"status": "HUMAN_REVIEW_PENDING"})
add("WF26-002", "packet_creation", case("WF26-002", sut=SUT_EX), expect={"status": "HUMAN_REVIEW_PENDING"})
add("WF26-003", "packet_creation", case("WF26-003", sut=SUT_VAG), expect={"status": "HUMAN_REVIEW_PENDING"})
add("WF26-004", "packet_creation", dict(case("WF26-004"), source_evidence_spans=["kilde-a"]),
    expect={"status": "HUMAN_REVIEW_PENDING", "packet_has_source_spans": True})
c5 = case("WF26-005"); c5["final_gold"] = "TRIGGERED"
add("WF26-005", "packet_creation", c5, expect={"packet_error": True})
c6 = case("WF26-006"); del c6["criterion"]
add("WF26-006", "packet_creation", c6, expect={"packet_error": True})
# reviewer output ingestion (6)
add("WF26-007", "review_ingestion", case("WF26-007"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED", "review_mode": "SINGLE_HUMAN_REVIEW"})
bad_enum = j("MAYBE", "ABSENT", "NO", "SUFFICIENT")
add("WF26-008", "review_ingestion", case("WF26-008"), [({"reviewer_id": "R1", "judgment": bad_enum})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
no_span = j("PRESENT", "ABSENT", "NO", "SUFFICIENT")
add("WF26-009", "missing_evidence", case("WF26-009"), [({"reviewer_id": "R1", "judgment": no_span})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
fabricated = j("PRESENT", "ABSENT", "NO", "SUFFICIENT", ["Dette spannet finnes ikke i svaret."])
add("WF26-010", "review_ingestion", case("WF26-010"), [({"reviewer_id": "R1", "judgment": fabricated})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
spans_forbidden = j("ABSENT", "ABSENT", "NO", "SUFFICIENT", [SPAN_T])
add("WF26-011", "review_ingestion", case("WF26-011"), [({"reviewer_id": "R1", "judgment": spans_forbidden})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
add("WF26-012", "duplicate_review", case("WF26-012", sut=SUT_BOTH),
    [({"reviewer_id": "R1", "judgment": CL_TRIG}), ({"reviewer_id": "R1", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED", "duplicate_rejected": True})
# derivation (8)
add("WF26-013", "derivation", case("WF26-013"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED", "derived_state": "CLEAR_TRIGGER_SUPPORT"})
add("WF26-014", "derivation", case("WF26-014", sut=SUT_EX), [({"reviewer_id": "R1", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "NOT_TRIGGERED", "derived_state": "CLEAR_NON_TRIGGER_SUPPORT"})
add("WF26-015", "derivation", case("WF26-015", sut=SUT_NEI), [({"reviewer_id": "R1", "judgment": TRIVIAL})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "NOT_TRIGGERED", "derived_state": "CLEAR_NON_TRIGGER_SUPPORT"})
add("WF26-016", "derivation", case("WF26-016"), [({"reviewer_id": "R1", "judgment": CONFLICT})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "UNRESOLVED", "derived_state": "AMBIGUOUS_OR_CONFLICTING"})
add("WF26-017", "derivation", case("WF26-017"), [({"reviewer_id": "R1", "judgment": INSUFF})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "UNRESOLVED", "derived_state": "INSUFFICIENT_TO_DECIDE"})
add("WF26-018", "derivation", case("WF26-018"), [({"reviewer_id": "R1", "judgment": HEDGED})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED", "derived_state": "CLEAR_TRIGGER_SUPPORT"})
add("WF26-019", "derivation", case("WF26-019"), [({"reviewer_id": "R1", "judgment": UNRES_COMBO})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "UNRESOLVED", "derived_state": "UNRESOLVED"})
add("WF26-020", "derivation", case("WF26-020"), [({"reviewer_id": "R1", "judgment": CONFLICT_INSUFF})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "UNRESOLVED", "derived_state": "AMBIGUOUS_OR_CONFLICTING"})
# disagreement + adjudication (7)
add("WF26-021", "disagreement", case("WF26-021"),
    [({"reviewer_id": "RA", "judgment": CL_TRIG}), ({"reviewer_id": "RB", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED", "final_label": "TRIGGERED"})
add("WF26-022", "disagreement", case("WF26-022", sut=SUT_EX),
    [({"reviewer_id": "RA", "judgment": CL_NTRIG}), ({"reviewer_id": "RB", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED", "final_label": "NOT_TRIGGERED"})
add("WF26-023", "disagreement", case("WF26-023", sut=SUT_BOTH),
    [({"reviewer_id": "RA", "judgment": CL_TRIG}), ({"reviewer_id": "RB", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT"},
    adjudication={"case_id": "WF26-023", "contract_version": "m2-decomposition-v2-5", "reviewer_a": "RA",
                  "reviewer_b": "RB", "adjudicated": True,
                  "final_judgment": CL_TRIG, "adjudication_note": "trigger span is committed assertion",
                  "model_outputs_visible_to_adjudicator": False},
    expect_after_adjudication={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_WITH_ADJUDICATION", "final_label": "TRIGGERED"})
add("WF26-024", "adjudication", case("WF26-024"),
    [({"reviewer_id": "RA", "judgment": INSUFF}), ({"reviewer_id": "RB", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT"},
    adjudication={"case_id": "WF26-024", "contract_version": "m2-decomposition-v2-5", "reviewer_a": "RA",
                  "reviewer_b": "RB", "adjudicated": True,
                  "final_judgment": INSUFF, "adjudication_note": "no contrary support, insufficient",
                  "model_outputs_visible_to_adjudicator": False},
    expect_after_adjudication={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "UNRESOLVED"})
add("WF26-025", "adjudication", case("WF26-025", sut=SUT_BOTH),
    [({"reviewer_id": "RA", "judgment": CL_TRIG}), ({"reviewer_id": "RB", "judgment": CL_NTRIG})],
    adjudication={"case_id": "WF26-025", "adjudicated": True, "model_outputs_visible_to_adjudicator": True,
                  "final_judgment": CL_TRIG, "adjudication_note": "x"},
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "adjudication_error": True})
add("WF26-026", "adjudication", case("WF26-026"), [({"reviewer_id": "RA", "judgment": CL_TRIG})],
    adjudication={"case_id": "WF26-026", "adjudicated": True, "model_outputs_visible_to_adjudicator": False,
                  "final_judgment": CL_TRIG, "adjudication_note": "x"},
    expect={"adjudication_error": True, "status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED"})
add("WF26-027", "disagreement", case("WF26-027"),
    [({"reviewer_id": "RA", "judgment": CONFLICT}), ({"reviewer_id": "RB", "judgment": CONFLICT})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED", "final_label": "UNRESOLVED"})
# malformed review (4)
add("WF26-028", "malformed_review", case("WF26-028"), [("NOT_AN_OBJECT")],
    expect={"status": "HUMAN_REVIEW_INVALID"})
add("WF26-029", "malformed_review", case("WF26-029"),
    [({"reviewer_id": "R1", "judgment": CL_TRIG, "case_id": "WF26-OTHER"})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
add("WF26-030", "malformed_review", case("WF26-030"),
    [({"reviewer_id": "R1", "judgment": {"trigger_support": "PRESENT"}})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
add("WF26-031", "malformed_review", case("WF26-031"),
    [({"reviewer_id": "R1", "contract_version": "v0-1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_INVALID"})
# provenance (5)
add("WF26-032", "provenance", case("WF26-032"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]})
add("WF26-033", "provenance", case("WF26-033"), [({"reviewer_id": "R1", "judgment": no_span})],
    expect={"status": "HUMAN_REVIEW_INVALID",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_REJECTED", "STATUS"]})
add("WF26-034", "provenance", case("WF26-034", sut=SUT_BOTH),
    [({"reviewer_id": "RA", "judgment": CL_TRIG}), ({"reviewer_id": "RB", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS", "DUAL_REVIEW_DISAGREEMENT", "STATUS"]})
add("WF26-035", "provenance", case("WF26-035"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "provenance_contract_version": "m2-decomposition-v2-5"})
add("WF26-036", "provenance", case("WF26-036"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "provenance_has_packet_sha": True})
# finalization / fail-closed (4)
add("WF26-037", "finalization", case("WF26-037"), expect={"status": "HUMAN_REVIEW_PENDING", "final_is_none": True})
add("WF26-038", "finalization", case("WF26-038"), [({"reviewer_id": "R1", "judgment": fabricated})],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF26-039", "finalization", case("WF26-039", sut=SUT_BOTH),
    [({"reviewer_id": "RA", "judgment": CL_TRIG}), ({"reviewer_id": "RB", "judgment": CL_NTRIG})],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "final_is_none": True})
add("WF26-040", "finalization", case("WF26-040"), [({"reviewer_id": "R1", "judgment": CL_TRIG})],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_label": "TRIGGERED", "bucket": "human_reviewed"})

out = {"artifact": "workflow-test-fixtures-v2-6",
       "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
       "n_fixtures": len(F),
       "provenance": "Synthetic workflow fixtures authored 2026-09-13; test the review-lane machinery, not M2 semantics; no model calls.",
       "fixtures": F}
with open(os.path.join(DIR, "workflow-test-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("fixtures:", len(F))
