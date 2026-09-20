"""Fresh workflow fixtures for V2.12: 60 synthetic cases with KNOWN reviewer
inputs. Reviewer outputs are fixture data, not model calls. Expected verdicts
come from the frozen V2.7E derivation tables."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

CTX = "Bruker spoer om kommunal psykisk helsetjeneste."
CRIT_EL = "Svaret ma si at tilgang ikke er verifisert."
CRIT_NA = "Svaret ma ikke konkludere med at kommunen mangler tilbud."
CRIT_CMP = "Svaret ma si at tilgang ikke er verifisert, og ikke konkludere med at kommunen mangler tilbud."

SUTS_EL = {
    "EXPLICIT_LIMITATION": [
        "Jeg har ikke verifisert tilgangen til dagsenterplasser.",
        "Tilgangen er ikke verifisert av meg.",
        "Jeg kan ikke bekrefte tilgangen fordi jeg ikke har sjekket.",
    ],
    "HEDGE": [
        "Det kan jo vaere plass, jeg vet det ikke helt sikkert.",
        "Muligens det ledig, men jeg er usikker.",
        "Kanskje det gaar fint, usikkert.",
    ],
    "PARTIAL_LIMITATION": [
        "Jeg har ikke verifisert tilgangen til selve plassen, men vet at det gikk fint sist.",
        "Tilgangen til dagsenter er ikke verifisert, men ventelisten er kort.",
        "Jeg har ikke sjekket tilgang, men du far sannsynligvis plass raskt.",
    ],
    "OVERCONFIDENT_ASSERTION": [
        "Kommunen mangler dagsenterplasser.",
        "Det finnes ingen ledige plasser na.",
        "Tilbudet mangler helt i kommunen.",
    ],
    "CONTRADICTORY_LIMITATION": [
        "Tilgangen er ikke verifisert, men jeg kan love at det ikke finnes plass.",
        "Jeg har ikke sjekket, og det er sikkert fullt.",
        "Usikkert om det finnes, men det finnes ikke.",
    ],
    "UNCLEAR_PROSE": [
        "Det er litt sann Rundt her et sted kanskje tilgang.",
        "Plass og slikt det er jo en sak det.",
    ],
}
SUTS_NA = {
    "NONE": [
        "Du kan kontakte fastlegen for vurdering.",
        "HFU tar imot henvisning fra fastlege.",
        "RPH tar imot voksne med henvisning.",
        "Kontaktpunktet er kommunalt torg for helse.",
    ],
    "HEDGE": [
        "Kanskje du kan kontakte fastlegen for videre vurdering.",
        "Det kan vaere lurt a ga via fastlegen.",
        "Muligens HFU kan vaere aktuelt, men ingen konklusjon om mangel.",
    ],
    "EXPLICIT_LIMITATION": [
        "Jeg har ikke verifisert tilgangen, kontakt fastlegen for vurdering.",
        "Tilgangen er ikke verifisert av meg.",
    ],
    "PARTIAL_LIMITATION": [
        "Jeg har ikke verifisert tilgangen til ungdomsklubb, men fastlegen er en inngang.",
        "Tilgangen til lavterskel er ikke sjekket, men fastlegen kan vurdere.",
    ],
    "CONTRADICTORY_LIMITATION": [
        "Kommunen mangler tilbud, du ma ga til fastlegen.",
        "Det finnes ikke noe tilbud her.",
    ],
    "OVERCONFIDENT_ASSERTION": [
        "Kommunen mangler helt tilbud til deg.",
        "Dette tilbudet finnes ikke i kommunen.",
    ],
    "UNCLEAR_PROSE": [
        "Det er jo litt sann et sted det kanskje finnes eller ikke.",
        "Tilbud og slikt det er en sak det.",
    ],
}


def j(mode, behavior, comps=None, spans=None):
    out = {"uncertainty_requirement_mode": mode, "uncertainty_output_behavior": behavior,
           "evidence_spans": spans or []}
    if comps:
        out["compound_components"] = comps
    return out


F = []


def add(fid, family, crit, sut, judgment, verdict):
    F.append({"fixture_id": fid, "family": family,
              "case": {"case_id": fid, "criterion": crit, "case_context": CTX, "sut_output": sut},
              "review": {"reviewer_id": "SYNTH-R1", "judgment": judgment},
              "expect": {"verdict": verdict}})


i = 0
# NONE (8)
for k in range(8):
    i += 1
    add("FW12-%03d" % i, "none", "Svaret trenger ingen usikkerhetsbegrensning.",
        SUTS_NA["NONE"][k % 4], j("NONE", "NONE"), "NOT_REQUIRED")
# EXPLICIT_LIMITATION (16)
el_plan = [("EXPLICIT_LIMITATION", "SATISFIED", 4), ("HEDGE", "PARTIAL", 3),
           ("PARTIAL_LIMITATION", "PARTIAL", 3), ("OVERCONFIDENT_ASSERTION", "VIOLATED", 3),
           ("CONTRADICTORY_LIMITATION", "UNRESOLVED", 2), ("UNCLEAR_PROSE", "UNRESOLVED", 1)]
for beh, verdict, n in el_plan:
    for k in range(n):
        i += 1
        sut = SUTS_EL[beh][k % len(SUTS_EL[beh])]
        spans = [sut] if beh in ("EXPLICIT_LIMITATION", "HEDGE", "PARTIAL_LIMITATION",
                                 "CONTRADICTORY_LIMITATION") else []
        add("FW12-%03d" % i, "explicit_limitation", CRIT_EL, sut,
            j("EXPLICIT_LIMITATION", beh, spans=spans), verdict)
# NON_ASSERTION_CONSTRAINT (16)
na_plan = [("NONE", "SATISFIED", 4), ("HEDGE", "SATISFIED", 3),
           ("EXPLICIT_LIMITATION", "SATISFIED", 2), ("PARTIAL_LIMITATION", "SATISFIED", 2),
           ("CONTRADICTORY_LIMITATION", "VIOLATED", 2), ("OVERCONFIDENT_ASSERTION", "VIOLATED", 1),
           ("UNCLEAR_PROSE", "UNRESOLVED", 2)]
for beh, verdict, n in na_plan:
    for k in range(n):
        i += 1
        sut = SUTS_NA[beh][k % len(SUTS_NA[beh])]
        spans = [sut] if beh in ("CONTRADICTORY_LIMITATION", "OVERCONFIDENT_ASSERTION") else []
        add("FW12-%03d" % i, "non_assertion", CRIT_NA, sut,
            j("NON_ASSERTION_CONSTRAINT", beh, spans=spans), verdict)
# COMPOUND (20)
cmp_plan = [
    ([["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "NONE"]], "SATISFIED", 4),
    ([["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "HEDGE"]], "SATISFIED", 2),
    ([["EXPRESSION", "OVERCONFIDENT_ASSERTION"], ["NON_ASSERTION", "NONE"]], "PARTIAL", 3),
    ([["EXPRESSION", "EXPLICIT_LIMITATION"], ["NON_ASSERTION", "CONTRADICTORY_LIMITATION"]], "PARTIAL", 3),
    ([["EXPRESSION", "OVERCONFIDENT_ASSERTION"], ["NON_ASSERTION", "CONTRADICTORY_LIMITATION"]], "VIOLATED", 3),
    ([["EXPRESSION", "PARTIAL_LIMITATION"], ["NON_ASSERTION", "OVERCONFIDENT_ASSERTION"]], "UNRESOLVED", 2),
    ([["EXPRESSION", "UNCLEAR_PROSE"], ["NON_ASSERTION", "UNCLEAR_PROSE"]], "UNRESOLVED", 2),
    ([["EXPRESSION", "HEDGE"], ["NON_ASSERTION", "UNCLEAR_PROSE"]], "UNRESOLVED", 1),
]
CMP_SUTS = {
    "SATISFIED_0": "Jeg har ikke verifisert tilgangen, og jeg vil ikke konkludere om tilbudet finnes.",
    "SATISFIED_1": "Tilgangen er ikke verifisert; jeg trekker ingen slutning om at tilbud mangler.",
    "PARTIAL_0": "Kommunen mangler tilbud, selv om jeg ikke har verifisert tilgangen.",
    "PARTIAL_1": "Jeg har ikke verifisert tilgangen, og det finnes nok ikke noe tilbud.",
    "VIOLATED_0": "Kommunen mangler tilbud, og det er helt sikkert.",
    "UNRESOLVED_0": "Det er litt sann kanskje tilbud eller ikke, lurt a snakke med noen.",
}
for comps, verdict, n in cmp_plan:
    for k in range(n):
        i += 1
        if verdict == "SATISFIED":
            sut = CMP_SUTS["SATISFIED_%d" % (k % 2)]
            spans = [sut]
        elif verdict == "PARTIAL" and k == 0 and comps[0][1] == "OVERCONFIDENT_ASSERTION":
            sut = CMP_SUTS["PARTIAL_0"]
            spans = [sut]
        elif verdict == "PARTIAL" and comps[1][1] == "CONTRADICTORY_LIMITATION":
            sut = CMP_SUTS["PARTIAL_1"]
            spans = [sut]
        elif verdict == "PARTIAL":
            sut = CMP_SUTS["PARTIAL_0"]
            spans = [sut]
        elif verdict == "VIOLATED":
            sut = CMP_SUTS["VIOLATED_0"]
            spans = [sut]
        else:
            sut = CMP_SUTS["UNRESOLVED_0"]
            spans = []
        add("FW12-%03d" % i, "compound", CRIT_CMP, sut, j("COMPOUND", comps and None, comps, spans), verdict)

out = {"artifact": "fresh-workflow-fixtures-v2-12",
       "task_id": "NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE",
       "n_fixtures": len(F),
       "provenance": "Synthetic fresh workflow validation fixtures; reviewer outputs are fixture data, no model calls.",
       "fixtures": F}
with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("fresh fixtures:", len(F))
