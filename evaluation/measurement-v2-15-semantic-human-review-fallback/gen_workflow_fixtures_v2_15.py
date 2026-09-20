"""Generate 60 workflow development fixtures for the V2.15 generic lane.
Reviewer outputs are fixture data, not model calls. Mirrors V2.12 pattern.
Expected verdicts are transcribed from the frozen v1-4 / V2.7E contracts."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

CTX = "Bruker spor om kommunalt tilbud."

F = []


def add(fid, category, case, reviews=None, adjudication=None, expect=None,
        expect_after_adjudication=None):
    fx = {"fixture_id": fid, "category": category, "case": case,
          "reviews": reviews or [], "expect": expect or {}}
    if adjudication is not None:
        fx["adjudication"] = adjudication
    if expect_after_adjudication is not None:
        fx["expect_after_adjudication"] = expect_after_adjudication
    F.append(fx)


def case(fid, dim, crit, sut, **extra):
    c = {"case_id": fid, "dimension": dim, "criterion": crit,
         "case_context": CTX, "sut_output": sut}
    c.update(extra)
    return c


def rv(rid, judgment, **over):
    d = {"reviewer_id": rid, "judgment": judgment}
    d.update(over)
    return d


def jc(state, spans=None):
    return {"critical_evidence_state": state, "evidence_spans": spans or []}


def jf(match, comm, spans=None):
    return {"criterion_semantic_match": match, "speaker_commitment": comm,
            "evidence_spans": spans or []}


def jr(prop, comm, verdict, spans=None):
    return {"route_proposition_present": prop, "route_speaker_commitment": comm,
            "proposed_verdict": verdict, "evidence_spans": spans or []}


def ju(mode, behavior, spans=None, comps=None):
    d = {"uncertainty_requirement_mode": mode, "uncertainty_output_behavior": behavior,
         "evidence_spans": spans or []}
    if comps is not None:
        d["compound_components"] = comps
    return d


CRIT_TRIGGER = "Kriteriet krever at svaret identifiserer en klar utloeser."
CRIT_NON = "Kriteriet krever at svaret identifiserer at utloeser mangler."
SUT_TRIG = "Du kvalifiserer fordi inntekten er under grensen."
SUT_NON = "Ingen utloeser er oppfyllt i dette tilfellet."

# --- A: packet-level errors (8) ---
add("WF15-01", "packet_error", case("WF15-01", "forbidden_claim", "c", "s", gold="PRESENT"), expect={"packet_error": True})
add("WF15-02", "packet_error", case("WF15-02", "forbidden_claim", "c", "s", model_verdict="PRESENT"), expect={"packet_error": True})
add("WF15-03", "packet_error", case("WF15-03", "forbidden_claim", "c", "s", automated_verdict="ABSENT"), expect={"packet_error": True})
add("WF15-04", "packet_error", case("WF15-04", "route_correctness", "", "s"), expect={"packet_error": True})
add("WF15-05", "packet_error", case("WF15-05", "critical_condition", "c", ""), expect={"packet_error": True})
add("WF15-06", "packet_error", case("WF15-06", "route", "c", "s"), expect={"packet_error": True})
add("WF15-07", "packet_error", case("", "critical_condition", "c", "s"), expect={"packet_error": True})
add("WF15-08", "packet_error", {"case_id": "WF15-08", "dimension": "critical_condition",
    "criterion": "c", "case_context": 123, "sut_output": "s"}, expect={"packet_error": True})

# --- B: derivation happy paths, single review (20) ---
add("WF15-09", "derivation", case("WF15-09", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT", ["inntekten er under grensen"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "SINGLE_HUMAN_REVIEW",
            "final_verdict": "TRIGGERED",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"],
            "routed_automated_authoritative_false": True})
add("WF15-10", "derivation", case("WF15-10", "critical_condition", CRIT_NON, SUT_NON),
    [rv("R1", jc("CLEAR_NON_TRIGGER_SUPPORT", ["Ingen utloeser er oppfyllt"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "NOT_TRIGGERED"})
add("WF15-11", "derivation", case("WF15-11", "critical_condition", CRIT_TRIGGER, "Delvis relevante opplysninger, motstridende."),
    [rv("R1", jc("AMBIGUOUS_OR_CONFLICTING"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-12", "derivation", case("WF15-12", "critical_condition", CRIT_TRIGGER, "Teksten omhandler annet."),
    [rv("R1", jc("INSUFFICIENT_TO_DECIDE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-13", "derivation", case("WF15-13", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Kommunen mangler familietilbud."),
    [rv("R1", jf("MATCH", "ASSERTED", ["mangler familietilbud"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PRESENT"})
add("WF15-14", "derivation", case("WF15-14", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Det ser ut til aa mangle tilbud."),
    [rv("R1", jf("MATCH", "HEDGED_ASSERTION", ["ser ut til aa mangle"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PRESENT"})
add("WF15-15", "derivation", case("WF15-15", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Saken gjelder barnepensjon."),
    [rv("R1", jf("NO_MATCH", "ASSERTED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ABSENT"})
add("WF15-16", "derivation", case("WF15-16", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Det er ikke riktig at kommunen mangler tilbud."),
    [rv("R1", jf("MATCH", "NEGATED", ["ikke riktig at kommunen mangler"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ABSENT"})
add("WF15-17", "derivation", case("WF15-17", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Nachbar sa: kommunen mangler tilbud."),
    [rv("R1", jf("MATCH", "QUOTED_ONLY", ["kommunen mangler tilbud"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ABSENT"})
add("WF15-18", "derivation", case("WF15-18", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Uklart om teksten gjelder tilbud i det hele tatt."),
    [rv("R1", jf("UNRESOLVED", "UNRESOLVED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-19", "derivation", case("WF15-19", "route_correctness", "Godkjent rute: fastlegen.", "Kontakt fastlegen for vurdering."),
    [rv("R1", jr("YES", "ASSERTED", "ACCEPTABLE", ["Kontakt fastlegen"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ACCEPTABLE",
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS"]})
add("WF15-20", "derivation", case("WF15-20", "route_correctness", "Godkjent rute: fastlege og HFU.", "Du kan kontakte fastlegen, men HFU er ikke nevnt."),
    [rv("R1", jr("YES", "HEDGED_ASSERTION", "PARTIAL", ["kontakte fastlegen"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF15-21", "derivation", case("WF15-21", "route_correctness", "Godkjent rute: fastlegen.", "Ring skattekontoret for hjelp."),
    [rv("R1", jr("YES", "ASSERTED", "NO_ACCEPTABLE_ROUTE", ["Ring skattekontoret"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "NO_ACCEPTABLE_ROUTE"})
add("WF15-22", "derivation", case("WF15-22", "route_correctness", "Godkjent rute: fastlegen.", "Fastlegen er ikke riktig inngang her."),
    [rv("R1", jr("YES", "NEGATED", "UNRESOLVED", ["Fastlegen er ikke riktig inngang"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-23", "derivation", case("WF15-23", "route_correctness", "Godkjent rute: fastlegen.", "Svaret nevner ingen konkrete steder."),
    [rv("R1", jr("NO", "UNRESOLVED", "UNRESOLVED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-24", "derivation", case("WF15-24", "required_uncertainty", "Kriteriet stiller ingen usikkerhetskrav.", "Tilbudet har apning hver tirsdag."),
    [rv("R1", ju("NONE", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "NOT_REQUIRED"})
add("WF15-25", "derivation", case("WF15-25", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Tilgangen er ikke verifisert."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION", ["ikke verifisert"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF15-26", "derivation", case("WF15-26", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Det er kanskje tilgang."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "HEDGE", ["kanskje"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF15-27", "derivation", case("WF15-27", "required_uncertainty", "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud.", "Jeg vet ikke om det finnes tilbud."),
    [rv("R1", ju("NON_ASSERTION_CONSTRAINT", "NONE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF15-28", "derivation", case("WF15-28", "required_uncertainty", "Kriteriet krever forbehold og ingen overkonklusjon.", "Tilgangen er ikke verifisert; jeg konkluderer ikke om manglende tilbud."),
    [rv("R1", ju("COMPOUND", "NONE", ["ikke verifisert"],
                 comps=[{"kind": "EXPRESSION", "behavior": "EXPLICIT_LIMITATION"},
                        {"kind": "NON_ASSERTION", "behavior": "NONE"}]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})

# --- C: review validation errors (8) ---
add("WF15-29", "review_invalid", case("WF15-29", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Kommunen mangler familietilbud."),
    [rv("R1", jf("MATCH", "ASSERTED", ["span som ikke finnes"]))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-30", "review_invalid", case("WF15-30", "forbidden_claim", "c", "s"),
    [rv("R1", jf("MATCH", "SHOUTED"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-31", "review_invalid", case("WF15-31", "critical_condition", "c", "s"),
    [rv("R1", "ikke et objekt")],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-32", "review_invalid", case("WF15-32", "route_correctness", "c", "s"),
    [{"packet_id": "PKT-ANNEN", "case_id": "WF15-32", "reviewer_id": "R1",
      "contract_version": "semantic-judge-contract-v1-4", "reviewed_utc": "2026-09-14T00:00:00Z",
      "judgment": jr("YES", "ASSERTED", "ACCEPTABLE")}],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-33", "review_invalid", case("WF15-33", "critical_condition", "c", "s"),
    [{"packet_id": "PKT-WF15-33", "case_id": "ANNEN", "reviewer_id": "R1",
      "contract_version": "semantic-judge-contract-v1-4", "reviewed_utc": "2026-09-14T00:00:00Z",
      "judgment": jc("UNRESOLVED")}],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-34", "review_invalid", case("WF15-34", "critical_condition", "c", "s"),
    [{"packet_id": "PKT-WF15-34", "case_id": "WF15-34", "reviewer_id": "R1",
      "contract_version": "annen-kontrakt", "reviewed_utc": "2026-09-14T00:00:00Z",
      "judgment": jc("UNRESOLVED")}],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-35", "review_invalid", case("WF15-35", "critical_condition", "c", "s"),
    [rv("R1", {"critical_evidence_state": "UNRESOLVED", "evidence_spans": "ikke-liste"})],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-36", "duplicate_review", case("WF15-36", "critical_condition", "Kriteriet krever identifisering av utloeser.", "Grensen er overskredet."),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT", ["Grensen er overskredet"])),
     rv("R1", jc("CLEAR_NON_TRIGGER_SUPPORT"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "SINGLE_HUMAN_REVIEW",
            "final_verdict": "TRIGGERED", "duplicate_rejected": True,
            "provenance_events": ["PACKET_CREATED", "ROUTED", "STATUS", "REVIEW_ACCEPTED", "STATUS",
                                  "DUPLICATE_REVIEW_REJECTED"]})

# --- D: dual blind (6) ---
add("WF15-37", "dual_blind", case("WF15-37", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT", ["inntekten er under grensen"])),
     rv("R2", jc("CLEAR_TRIGGER_SUPPORT", ["inntekten er under grensen"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED",
            "final_verdict": "TRIGGERED"})
add("WF15-38", "dual_blind", case("WF15-38", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT")), rv("R2", jc("CLEAR_NON_TRIGGER_SUPPORT"))],
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "final_is_none": True, "review_mode": None})
add("WF15-39", "dual_blind", case("WF15-39", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT")), rv("R2", jc("CLEAR_NON_TRIGGER_SUPPORT"))],
    adjudication={"adjudicated": True, "model_outputs_visible_to_adjudicator": False,
                  "case_id": "WF15-39", "contract_version": "semantic-judge-contract-v1-4",
                  "final_judgment": jc("CLEAR_TRIGGER_SUPPORT"), "adjudication_note": "R1 correct"},
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT"},
    expect_after_adjudication={"status": "HUMAN_REVIEW_RESOLVED",
                               "review_mode": "DUAL_BLIND_REVIEW_WITH_ADJUDICATION",
                               "final_verdict": "TRIGGERED"})
add("WF15-40", "dual_blind", case("WF15-40", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT")), rv("R2", jc("CLEAR_NON_TRIGGER_SUPPORT"))],
    adjudication={"adjudicated": False, "model_outputs_visible_to_adjudicator": False,
                  "case_id": "WF15-40", "contract_version": "semantic-judge-contract-v1-4",
                  "final_judgment": jc("CLEAR_TRIGGER_SUPPORT"), "adjudication_note": "x"},
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "adjudication_error": True,
            "final_is_none": True})
add("WF15-41", "dual_blind", case("WF15-41", "critical_condition", CRIT_TRIGGER, SUT_TRIG),
    [rv("R1", jc("CLEAR_TRIGGER_SUPPORT")), rv("R2", jc("CLEAR_NON_TRIGGER_SUPPORT"))],
    adjudication={"adjudicated": True, "model_outputs_visible_to_adjudicator": True,
                  "case_id": "WF15-41", "contract_version": "semantic-judge-contract-v1-4",
                  "final_judgment": jc("CLEAR_TRIGGER_SUPPORT"), "adjudication_note": "x"},
    expect={"status": "HUMAN_REVIEW_DISAGREEMENT", "adjudication_error": True,
            "final_is_none": True})
add("WF15-42", "dual_blind", case("WF15-42", "required_uncertainty", "Kriteriet krever forbehold og ingen overkonklusjon.", "Tilgangen er ikke verifisert."),
    [rv("R1", ju("COMPOUND", "NONE", ["ikke verifisert"],
                 comps=[{"kind": "EXPRESSION", "behavior": "PARTIAL_LIMITATION"},
                        {"kind": "NON_ASSERTION", "behavior": "NONE"}])),
     rv("R2", ju("COMPOUND", "NONE", ["ikke verifisert"],
                 comps=[{"kind": "EXPRESSION", "behavior": "PARTIAL_LIMITATION"},
                        {"kind": "NON_ASSERTION", "behavior": "NONE"}]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "review_mode": "DUAL_BLIND_REVIEW_AGREED",
            "final_verdict": "PARTIAL"})

# --- E: fail-closed derivability probes (6) ---
add("WF15-43", "fail_closed_derivation", case("WF15-43", "route_correctness", "Godkjent rute: fastlegen.", "Ingen rute nevnt."),
    [rv("R1", jr("NO", "ASSERTED", "UNRESOLVED"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-44", "fail_closed_derivation", case("WF15-44", "route_correctness", "Godkjent rute: fastlegen.", "Fastlegen er ikke riktig."),
    [rv("R1", jr("YES", "NEGATED", "ACCEPTABLE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-45", "fail_closed_derivation", case("WF15-45", "route_correctness", "Godkjent rute: fastlegen.", "Det ble sagt: kontakt fastlegen."),
    [rv("R1", jr("YES", "QUOTED_ONLY", "ACCEPTABLE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-46", "fail_closed_derivation", case("WF15-46", "route_correctness", "Godkjent rute: fastlegen.", "Uklart om fastlegen er aktuell."),
    [rv("R1", jr("YES", "UNRESOLVED", "PARTIAL"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-47", "fail_closed_derivation", case("WF15-47", "required_uncertainty", "Kriteriet stiller ingen usikkerhetskrav.", "Tilbud finnes."),
    [rv("R1", ju("NONE", "HEDGE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})
add("WF15-48", "fail_closed_derivation", case("WF15-48", "required_uncertainty", "c", "s"),
    [rv("R1", ju("MAYBE", "NONE"))],
    expect={"status": "HUMAN_REVIEW_INVALID", "final_is_none": True})

# --- F: extra happy paths (12) ---
add("WF15-49", "derivation", case("WF15-49", "critical_condition", CRIT_TRIGGER, "Uklart om utloeser er oppfyllt."),
    [rv("R1", jc("UNRESOLVED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-50", "derivation", case("WF15-50", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Tilgangen fungerer sikkert."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})
add("WF15-51", "derivation", case("WF15-51", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Vi har ikke sjekket alle adresser."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "PARTIAL_LIMITATION", ["ikke sjekket alle adresser"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "PARTIAL"})
add("WF15-52", "derivation", case("WF15-52", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Hmm, altsaa, typisk."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "UNCLEAR_PROSE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-53", "derivation", case("WF15-53", "required_uncertainty", "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert.", "Ikke verifisert. Nei, det er sikkert verifisert."),
    [rv("R1", ju("EXPLICIT_LIMITATION", "CONTRADICTORY_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-54", "derivation", case("WF15-54", "required_uncertainty", "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud.", "Kanskje tilbudet er der."),
    [rv("R1", ju("NON_ASSERTION_CONSTRAINT", "HEDGE"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "SATISFIED"})
add("WF15-55", "derivation", case("WF15-55", "required_uncertainty", "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud.", "Trolig mangler kommunen tilbud."),
    [rv("R1", ju("NON_ASSERTION_CONSTRAINT", "OVERCONFIDENT_ASSERTION", ["Trolig mangler kommunen tilbud"]))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})
add("WF15-56", "derivation", case("WF15-56", "required_uncertainty", "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud.", "Det finnes tilbud. Det finnes ikke tilbud."),
    [rv("R1", ju("NON_ASSERTION_CONSTRAINT", "CONTRADICTORY_LIMITATION"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "VIOLATED"})
add("WF15-57", "derivation", case("WF15-57", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Kontakt habilitering. Nei, det var feil inngang."),
    [rv("R1", jf("MATCH", "SELF_RETRACTED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ABSENT"})
add("WF15-58", "derivation", case("WF15-58", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Dagtilbud kan for eksempel vaere aktuelt."),
    [rv("R1", jf("MATCH", "HYPOTHETICAL_ONLY"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "ABSENT"})
add("WF15-59", "derivation", case("WF15-59", "forbidden_claim", "Kriteriet forbyr konklusjonen at tilbud mangler.", "Teksten nevner tilbud, men holder seg usikker."),
    [rv("R1", jf("MATCH", "NONCOMMITTAL"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})
add("WF15-60", "derivation", case("WF15-60", "route_correctness", "Godkjent rute: fastlegen.", "Uklart om fastlegen er riktig inngang."),
    [rv("R1", jr("YES", "ASSERTED", "UNRESOLVED"))],
    expect={"status": "HUMAN_REVIEW_RESOLVED", "final_verdict": "UNRESOLVED"})


assert len(F) == 60, len(F)
with open(os.path.join(DIR, "workflow-test-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump({"artifact": "workflow-test-fixtures-v2-15", "n_fixtures": len(F),
               "fixtures": F}, f, indent=1, ensure_ascii=False)
print("wrote", len(F), "workflow dev fixtures")
