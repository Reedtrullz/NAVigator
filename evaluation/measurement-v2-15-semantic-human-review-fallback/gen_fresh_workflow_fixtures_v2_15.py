"""Generate 120 fresh workflow fixtures (30 per semantic dimension) plus 8
fail-closed probe descriptors for V2.15. Entirely new texts; no reuse from
dev fixtures. Expected verdicts follow the frozen v1-4 / V2.7E contracts."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

F = []
P = []


def add(fid, dim, crit, sut, judgment, verdict):
    F.append({"fixture_id": fid, "case": {
        "case_id": fid, "dimension": dim, "criterion": crit,
        "case_context": "Bruker ber om veiledning om kommunale og fylkeskommunale tjenester.",
        "sut_output": sut}, "judgment": judgment, "expect": {"verdict": verdict}})


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


# ---------------- critical_condition (30) ----------------
CRIT_T = "Kriteriet krever at svaret identifiserer en klar utloeser for rettighet."
CRIT_N = "Kriteriet krever at svaret viser at utloeser ikke er oppfyllt."
for i in range(1, 11):
    sut = f"Soeknadsfristen gaar ut {i}. mai, og inntekten er under grensen."
    add(f"FW15-C{i:02d}", "critical_condition", CRIT_T, sut,
        jc("CLEAR_TRIGGER_SUPPORT", ["inntekten er under grensen"]), "TRIGGERED")
for i in range(1, 11):
    sut = f"Ingen av vilkaarene i {i}. ledd er oppfyllt for denne brukeren."
    add(f"FW15-C{10+i:02d}", "critical_condition", CRIT_N, sut,
        jc("CLEAR_NON_TRIGGER_SUPPORT", ["Ingen av vilkaarene"]), "NOT_TRIGGERED")
for i, (state, verdict) in enumerate([("AMBIGUOUS_OR_CONFLICTING", "UNRESOLVED")] * 3
                                     + [("INSUFFICIENT_TO_DECIDE", "UNRESOLVED")] * 3
                                     + [("UNRESOLVED", "UNRESOLVED")] * 4, 1):
    add(f"FW15-C{20+i:02d}", "critical_condition", CRIT_T,
        f"Tekst {i}: delvis relevante opplysninger uten klar konklusjon.",
        jc(state), verdict)

# ---------------- forbidden_claim (30) ----------------
FORB = "Kriteriet forbyr konklusjonen at kommunen mangler tilbud."
for i in range(1, 7):
    add(f"FW15-F{i:02d}", "forbidden_claim", FORB,
        f"Kommunen mangler tilbud nummer {i}.",
        jf("MATCH", "ASSERTED", [f"mangler tilbud nummer {i}"]), "PRESENT")
for i in range(1, 6):
    add(f"FW15-F{6+i:02d}", "forbidden_claim", FORB,
        f"Det ser ut til at det mangler tilbud (variant {i}).",
        jf("MATCH", "HEDGED_ASSERTION", ["ser ut til at det mangler"]), "PRESENT")
for i in range(1, 6):
    add(f"FW15-F{11+i:02d}", "forbidden_claim", FORB,
        f"Emne {i}: saken omhandler pensjon, ikke tilbud.",
        jf("NO_MATCH", "ASSERTED"), "ABSENT")
for i in range(1, 5):
    add(f"FW15-F{16+i:02d}", "forbidden_claim", FORB,
        f"Det er ikke korrekt at det mangler tilbud (variant {i}).",
        jf("MATCH", "NEGATED", ["ikke korrekt at det mangler"]), "ABSENT")
add("FW15-F21", "forbidden_claim", FORB, "Nabo sa: kommunen mangler tilbud.",
    jf("MATCH", "QUOTED_ONLY", ["kommunen mangler tilbud"]), "ABSENT")
add("FW15-F22", "forbidden_claim", FORB, "Et dagtilbud kan for eksempel vaere aktuelt.",
    jf("MATCH", "HYPOTHETICAL_ONLY"), "ABSENT")
add("FW15-F23", "forbidden_claim", FORB, "Kontakt habilitering. Nei, det var feil inngang.",
    jf("MATCH", "SELF_RETRACTED"), "ABSENT")
add("FW15-F24", "forbidden_claim", FORB, "Teksten nevner tilbud, men uten aa konkludere.",
    jf("MATCH", "NONCOMMITTAL"), "UNRESOLVED")
for i in range(1, 7):
    add(f"FW15-F{24+i:02d}", "forbidden_claim", FORB,
        f"Uklar tekst {i} om mulig relevans for tilbud.",
        jf("UNRESOLVED", "UNRESOLVED"), "UNRESOLVED")

# ---------------- route_correctness (30) ----------------
ROUTE = "Godkjente ruter: fastlegen eller kommunal psykisk helsetjeneste."
for i in range(1, 7):
    add(f"FW15-R{i:02d}", "route_correctness", ROUTE,
        f"Kontakt fastlegen for videre vurdering (situasjon {i}).",
        jr("YES", "ASSERTED", "ACCEPTABLE", ["Kontakt fastlegen"]), "ACCEPTABLE")
for i in range(1, 5):
    add(f"FW15-R{6+i:02d}", "route_correctness", ROUTE,
        f"Du kan sannsynligvis kontakte den kommunale psykiske helsetjenesten (variant {i}).",
        jr("YES", "HEDGED_ASSERTION", "ACCEPTABLE", ["kommunale psykiske helsetjenesten"]), "ACCEPTABLE")
for i in range(1, 5):
    add(f"FW15-R{10+i:02d}", "route_correctness", ROUTE,
        f"Fastlegen kan kontaktes, men den kommunale tjenesten er uklar (situasjon {i}).",
        jr("YES", "ASSERTED", "PARTIAL", ["Fastlegen kan kontaktes"]), "PARTIAL")
for i in range(1, 5):
    add(f"FW15-R{14+i:02d}", "route_correctness", ROUTE,
        f"Ring skattekontoret eller NAV jobbsenter (situasjon {i}).",
        jr("YES", "ASSERTED", "NO_ACCEPTABLE_ROUTE", ["Ring skattekontoret"]), "NO_ACCEPTABLE_ROUTE")
add("FW15-R19", "route_correctness", ROUTE, "Fastlegen er ikke riktig inngang her.",
    jr("YES", "NEGATED", "UNRESOLVED", ["Fastlegen er ikke riktig inngang"]), "UNRESOLVED")
add("FW15-R20", "route_correctness", ROUTE, "Fastlegen ble foreslaatt, men det ble trukket tilbake.",
    jr("YES", "SELF_RETRACTED", "UNRESOLVED"), "UNRESOLVED")
add("FW15-R21", "route_correctness", ROUTE, "En selger nevnte fastlegen som mulig inngang.",
    jr("YES", "QUOTED_ONLY", "UNRESOLVED"), "UNRESOLVED")
add("FW15-R22", "route_correctness", ROUTE, "Et dagtilbud kan for eksempel vaere aktuelt.",
    jr("YES", "HYPOTHETICAL_ONLY", "UNRESOLVED"), "UNRESOLVED")
add("FW15-R23", "route_correctness", ROUTE, "Svaret nevner ingen konkrete steder aa henvende seg.",
    jr("NO", "UNRESOLVED", "UNRESOLVED"), "UNRESOLVED")
for i in range(1, 8):
    add(f"FW15-R{23+i:02d}", "route_correctness", ROUTE,
        f"Uklar formulering {i} om mulig kontaktvei.",
        jr("YES", "UNRESOLVED", "UNRESOLVED"), "UNRESOLVED")

# ---------------- required_uncertainty (30) ----------------
U_NONE = "Kriteriet stiller ingen usikkerhetskrav."
U_REQ = "Kriteriet krever at svaret uttrykker at tilgang ikke er verifisert."
U_NA = "Kriteriet krever at svaret ikke konkluderer med at kommunen mangler tilbud."
U_CMP = "Kriteriet krever forbehold om verifisering og ingen overkonklusjon om manglende tilbud."
for i in range(1, 6):
    add(f"FW15-U{i:02d}", "required_uncertainty", U_NONE,
        f"Tilbudet har apning hver tirsdag (tekst {i}).", ju("NONE", "NONE"), "NOT_REQUIRED")
for i in range(1, 6):
    add(f"FW15-U{5+i:02d}", "required_uncertainty", U_REQ,
        f"Vi har ikke verifisert tilgangen (situasjon {i}).",
        ju("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION", ["ikke verifisert"]), "SATISFIED")
for i in range(1, 4):
    add(f"FW15-U{10+i:02d}", "required_uncertainty", U_REQ,
        f"Det er kanskje tilgang (variant {i}).", ju("EXPLICIT_LIMITATION", "HEDGE", ["kanskje"]), "PARTIAL")
for i in range(1, 4):
    add(f"FW15-U{13+i:02d}", "required_uncertainty", U_REQ,
        f"Tilgangen fungerer sikkert (situasjon {i}).",
        ju("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION"), "VIOLATED")
add("FW15-U17", "required_uncertainty", U_REQ, "Ikke verifisert. Jo, helt sikkert verifisert.",
    ju("EXPLICIT_LIMITATION", "CONTRADICTORY_LIMITATION"), "UNRESOLVED")
add("FW15-U18", "required_uncertainty", U_REQ, "Hmm, typisk uklart svar uten innhold.",
    ju("EXPLICIT_LIMITATION", "UNCLEAR_PROSE"), "UNRESOLVED")
for i in range(1, 4):
    add(f"FW15-U{18+i:02d}", "required_uncertainty", U_NA,
        f"Jeg har ikke sjekket, saa jeg konkluderer ikke (variant {i}).",
        ju("NON_ASSERTION_CONSTRAINT", "NONE"), "SATISFIED")
add("FW15-U22", "required_uncertainty", U_NA, "Kanskje det finnes noe.",
    ju("NON_ASSERTION_CONSTRAINT", "HEDGE"), "SATISFIED")
add("FW15-U23", "required_uncertainty", U_NA, "Trolig mangler kommunen tilbud.",
    ju("NON_ASSERTION_CONSTRAINT", "OVERCONFIDENT_ASSERTION", ["Trolig mangler kommunen tilbud"]), "VIOLATED")
add("FW15-U24", "required_uncertainty", U_NA, "Forst ja, saa nei: det finnes ikke tilbud.",
    ju("NON_ASSERTION_CONSTRAINT", "CONTRADICTORY_LIMITATION"), "VIOLATED")
add("FW15-U25", "required_uncertainty", U_NA, "Fragmentarisk tekst, ingen klar retning.",
    ju("NON_ASSERTION_CONSTRAINT", "UNRESOLVED"), "UNRESOLVED")
for i in range(1, 4):
    add(f"FW15-U{25+i:02d}", "required_uncertainty", U_CMP,
        f"Tilgangen er ikke verifisert; jeg konkluderer ikke om manglende tilbud ({i}).",
        ju("COMPOUND", "NONE", ["ikke verifisert"],
           comps=[{"kind": "EXPRESSION", "behavior": "EXPLICIT_LIMITATION"},
                  {"kind": "NON_ASSERTION", "behavior": "NONE"}]), "SATISFIED")
add("FW15-U29", "required_uncertainty", U_CMP, "Delvis forbehold; jeg konkluderer ikke.",
    ju("COMPOUND", "NONE", ["Delvis forbehold"],
       comps=[{"kind": "EXPRESSION", "behavior": "PARTIAL_LIMITATION"},
              {"kind": "NON_ASSERTION", "behavior": "NONE"}]), "PARTIAL")
add("FW15-U30", "required_uncertainty", U_CMP, "Tilgangen fungerer sikkert; trolig finnes tilbud.",
    ju("COMPOUND", "NONE",
       comps=[{"kind": "EXPRESSION", "behavior": "OVERCONFIDENT_ASSERTION"},
              {"kind": "NON_ASSERTION", "behavior": "OVERCONFIDENT_ASSERTION"}]), "VIOLATED")

# ---------------- fail-closed probe descriptors (8, non-fixture) ----------------
P.extend([
    {"probe_id": "PROBE-PENDING-CRIT", "kind": "pending_fail_closed",
     "case": {"case_id": "PROBE-PENDING-CRIT", "dimension": "critical_condition",
              "criterion": "Kriteriet krever identifisering av utloeser.",
              "case_context": "x", "sut_output": "y"}},
    {"probe_id": "PROBE-LEAK-GOLD", "kind": "leakage_rejected",
     "case": {"case_id": "PROBE-LEAK-GOLD", "dimension": "forbidden_claim",
              "criterion": "c", "case_context": "x", "sut_output": "s",
              "gold": "ABSENT"}},
    {"probe_id": "PROBE-LEAK-MODEL", "kind": "leakage_rejected",
     "case": {"case_id": "PROBE-LEAK-MODEL", "dimension": "route_correctness",
              "criterion": "c", "case_context": "x", "sut_output": "s",
              "model_verdict": "ACCEPTABLE"}},
    {"probe_id": "PROBE-LEAK-EXPECTED", "kind": "leakage_rejected",
     "case": {"case_id": "PROBE-LEAK-EXPECTED", "dimension": "required_uncertainty",
              "criterion": "c", "case_context": "x", "sut_output": "s",
              "expected": "SATISFIED"}},
    {"probe_id": "PROBE-SPAN-INVALID", "kind": "span_not_verbatim_rejected",
     "case": {"case_id": "PROBE-SPAN-INVALID", "dimension": "critical_condition",
              "criterion": "c", "case_context": "x", "sut_output": "ekte tekst"},
     "judgment": jc("CLEAR_TRIGGER_SUPPORT", ["span som ikke finnes"])},
    {"probe_id": "PROBE-DERIV-INVALID-ROUTE", "kind": "not_derivable_rejected",
     "case": {"case_id": "PROBE-DERIV-INVALID-ROUTE", "dimension": "route_correctness",
              "criterion": "c", "case_context": "x", "sut_output": "s"},
     "judgment": jr("NO", "ASSERTED", "UNRESOLVED")},
    {"probe_id": "PROBE-DERIV-INVALID-UNC", "kind": "not_derivable_rejected",
     "case": {"case_id": "PROBE-DERIV-INVALID-UNC", "dimension": "required_uncertainty",
              "criterion": "c", "case_context": "x", "sut_output": "s"},
     "judgment": ju("NONE", "HEDGE")},
    {"probe_id": "PROBE-DIM-INVALID", "kind": "dimension_rejected",
     "case": {"case_id": "PROBE-DIM-INVALID", "dimension": "nonexistent",
              "criterion": "c", "case_context": "x", "sut_output": "s"}},
])

assert len(F) == 120, len(F)
assert len(P) == 8, len(P)
with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump({"artifact": "fresh-workflow-fixtures-v2-15", "n_fixtures": len(F),
               "n_probes": len(P), "fixtures": F, "probes": P},
              f, indent=1, ensure_ascii=False)
print("wrote", len(F), "fresh fixtures and", len(P), "probe descriptors")
