#!/usr/bin/env python3
"""V2.9 burned calibration set (coordinator-authored, 25 fixtures).

Fresh synthetic text; no reuse of V2.8/V2.9 official fixture text. Gold is
derived by the same frozen rule-based protocol as the official set
(derive_labels_v2_9 rules + frozen U7E module); the curator's expected
verdict is asserted against the derivation for consistency.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent

FIXTURES = [
    # ---- route (10) ----
    {"id": "V29C-ROUTE-01", "dim": "route", "trap": False,
     "ctx": "Forelder spor om kreativt verksted for barn pa biblioteket.",
     "crit": "Biblioteket tilbyr kreativt verksted for barn pa onsdager.",
     "sut": "Ta med barnet pa verkstedet pa biblioteket pa onsdager.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V29C-ROUTE-02", "dim": "route", "trap": False,
     "ctx": "Ungdom spor om aktivitetstilbud i helgen.",
     "crit": "Fritidsklubben arrangerer apent verksted for ungdom losrdager.",
     "sut": "Fritidsklubben har trolig apent verksted i helgen; det er et fornuftig sted a starte.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HEDGED_ASSERTION",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V29C-ROUTE-03", "dim": "route", "trap": True,
     "ctx": "Bruker ber om raad om hvor eleven kan fa leksehjelp.",
     "crit": "Fritidsklubben tilbyr leksehjelp for ungdomsskoleelever hver tirsdag.",
     "sut": "Biblioteket passer bra for leksehjelp. Nei, vent - leksehjelpen for ungdomsskoleelever er ikke pa biblioteket.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "SELF_RETRACTED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V29C-ROUTE-04", "dim": "route", "trap": True,
     "ctx": "Forelder spor om barnesvomming.",
     "crit": "Svommehallen holder barnesvommetimer pa loerdager.",
     "sut": "Biblioteket er ikke riktig sted for barnesvomming.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "NEGATED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V29C-ROUTE-05", "dim": "route", "trap": True,
     "ctx": "Bruker spor om stotte for unge med engstelser.",
     "crit": "Ungdom kan ta direkte kontakt med ungdomshelsestasjonen for samtale.",
     "sut": "Det finnes kanskje et tilbud et sted i kommunen for slike ting.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "UNRESOLVED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V29C-ROUTE-06", "dim": "route", "trap": False,
     "ctx": "Elev spor om leksehjelp.",
     "crit": "Fritidsklubben tilbyr leksehjelp for ungdomsskoleelever hver tirsdag.",
     "sut": "Ta kontakt med pensjonistforeningen for leksehjelp.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "NO_ACCEPTABLE_ROUTE"}},
    {"id": "V29C-ROUTE-07", "dim": "route", "trap": True,
     "ctx": "Forelder refererer hva laereren sa.",
     "crit": "Helsesykepleieren pa skolen tar imot elever for samtale uten timebestilling.",
     "sut": "Laereren foreslo at eleven kan ga til helsesykepleieren.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "QUOTED_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V29C-ROUTE-08", "dim": "route", "trap": True,
     "ctx": "Ungdom vurderer medbestemmelse.",
     "crit": "Ungdomsraadet tar imot innspill fra ungdom i kommunen.",
     "sut": "Om kommunen skulle hatt et ungdomsraad, ville det vaert et sted for slikt.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HYPOTHETICAL_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V29C-ROUTE-09", "dim": "route", "trap": False,
     "ctx": "Ung spor om psykologisk veiledning.",
     "crit": "RPH tar imot unge 16-23 uten henvisning, eller fastlegen kan henvise.",
     "sut": "Fastlegen er riktig forste kontakt for henvisning til samtalehjelp.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V29C-ROUTE-10", "dim": "route", "trap": False,
     "ctx": "Forelder spor om verkstedtilbudet.",
     "crit": "Verkstedet tilbyr baade veiledning og materialer inkludert i prisen.",
     "sut": "Verkstedet gir veiledning, men materialene ma du betale selv.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "PARTIAL"}},
    # ---- forbidden (7) ----
    {"id": "V29C-FORB-01", "dim": "forbidden", "trap": False,
     "ctx": "Bruker spor om stottekontakt.",
     "crit": "Kommunen har ikke stottekontakt for unge under 20.",
     "sut": "Kommunen tilbyr ikke stottekontakt for unge under 20.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"}},
    {"id": "V29C-FORB-02", "dim": "forbidden", "trap": True,
     "ctx": "Forelder har horst rykter om svommetimen.",
     "crit": "Barnesvommetimen pa loerdager er avviklet.",
     "sut": "Det stemmer ikke at timen er avviklet; barnesvommetimen fortsetter pa loerdager.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"}},
    {"id": "V29C-FORB-03", "dim": "forbidden", "trap": True,
     "ctx": "Bruker refererer samtale med nabo.",
     "crit": "Barnehageplassen faller automatisk bort ved fire ukers ferie.",
     "sut": "En nabo sa at barnehageplassen faller automatisk bort ved fire ukers ferie.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"}},
    {"id": "V29C-FORB-04", "dim": "forbidden", "trap": True,
     "ctx": "Bruker korrigerer seg selv om kulturskolen.",
     "crit": "Kulturskolen har avviklet teatertimer for barn.",
     "sut": "Kulturskolen har sluttet med teatertimer. Beklager, det var feil - timene fortsetter som normalt.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "SELF_RETRACTED"}},
    {"id": "V29C-FORB-05", "dim": "forbidden", "trap": True,
     "ctx": "Bruker spekulerer i vilkarsendringer.",
     "crit": "Biblioteket har fjernet leseappen for ungdomskort-brukere.",
     "sut": "Hvis biblioteket hadde fjernet leseappen, ville det staatt i brukervilarene.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HYPOTHETICAL_ONLY"}},
    {"id": "V29C-FORB-06", "dim": "forbidden", "trap": False,
     "ctx": "Bruker er usikker på klubbens status.",
     "crit": "Ungdomsklubben pa torget er nedlagt.",
     "sut": "Etter det jeg vet, er ungdomsklubben pa torget lagt ned.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"}},
    {"id": "V29C-FORB-07", "dim": "forbidden", "trap": False,
     "ctx": "Bruker spor om ulike tilbud pa tvers.",
     "crit": "Dusjterminene pa svommehallen er redusert til to timer.",
     "sut": "Korpsmedlemmer ma selv betale for uniformen.",
     "inter": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "ASSERTED"}},
    # ---- uncertainty (8) ----
    {"id": "V29C-UNC-01", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om verkstedet fortsatt gar.",
     "crit": "Svaret ma gjoere tydelig at tilgangen ikke er verifisert.",
     "sut": "Jeg har ikke kunnet verifisere om verkstedet fortsatt gar; sjekk med biblioteket.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "EXPLICIT_LIMITATION"}},
    {"id": "V29C-UNC-02", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker spor om verkstedtilbudet denne uken.",
     "crit": "Svaret ma gjoere tydelig at tilgangen ikke er verifisert.",
     "sut": "Tilgangen er ikke verifisert, og vi kan ikke si noe sikkert - men verkstedet gar garantert som normalt.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "CONTRADICTORY_LIMITATION"}},
    {"id": "V29C-UNC-03", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om ungdomsklubbens status.",
     "crit": "Svaret ma ikke konkludere med at ungdomsklubben er nedlagt.",
     "sut": "Statusen for ungdomsklubben faar du bekreftet hos fritidskontoret.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "NONE"}},
    {"id": "V29C-UNC-04", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om ungdomsklubbens apningstider.",
     "crit": "Svaret ma ikke konkludere med at ungdomsklubben er nedlagt.",
     "sut": "Ungdomsklubben er definitivt nedlagt, sa det er bortkastet a ga dit.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "OVERCONFIDENT_ASSERTION"}},
    {"id": "V29C-UNC-05", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker spor om tilgang til verkstedet.",
     "crit": "Svaret ma gjoere tydelig at tilgangen ikke er verifisert.",
     "sut": "Tilgang verksted kanskje ikke usikker men helt sikker uvisst onsdag kanskje.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "UNCLEAR_PROSE"}},
    {"id": "V29C-UNC-06", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om verkstedet gar videre.",
     "crit": "Svaret ma gjoere tydelig at tilgangen ikke er verifisert.",
     "sut": "Verkstedet gar nok som normalt, men jeg er litt usikker.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "HEDGE"}},
    {"id": "V29C-UNC-07", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om tilgang og konklusjon pa gang.",
     "crit": "Svaret ma si at tilgangen ikke er verifisert og ikke konkludere at tilbudet mangler.",
     "sut": "Jeg har ikke verifisert tilgangen. Statusen ma bekreftes hos fritidskontoret.",
     "inter": {"uncertainty_requirement_mode": "COMPOUND",
               "compound_components": [["EXPRESSION", "EXPLICIT_LIMITATION"],
                                       ["NON_ASSERTION", "NONE"]]}},
    {"id": "V29C-UNC-08", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om pris pa svommetimen.",
     "crit": "Barnesvommetimen koster 40 kroner per gang.",
     "sut": "Barnesvommetimen koster 40 kroner per gang.",
     "inter": {"uncertainty_requirement_mode": "NONE",
               "uncertainty_output_behavior": "NONE"}},
]


def _sha256_obj(obj):
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main():
    import sys
    sys.path.insert(0, str(HERE))
    from derive_labels_v2_9 import derive_forbidden, derive_route, derive_uncertainty
    sys.path.insert(0, str(HERE.parent / "judge-contract-v2-7e-uncertainty-repair"))

    out = []
    for f in FIXTURES:
        fx = dict(f)
        fx.setdefault("tag", "calib")
        fx.setdefault("safety", False)
        if f["dim"] == "forbidden":
            verdict = derive_forbidden(fx)
        elif f["dim"] == "route":
            verdict = derive_route(fx)
        else:
            verdict = derive_uncertainty(fx)
        fx["verdict"] = verdict
        out.append(fx)
    traps = sum(1 for f in out if f["trap"])
    trap_ids = [f["id"] for f in out if f["trap"]]
    gold_unresolved_traps = [f["id"] for f in out if f["trap"] and f["verdict"] == "UNRESOLVED"]
    doc = {"task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_9-NON-M2-POST-DIAGNOSTIC-SCREENING",
           "purpose": "burned calibration for prompt iterations; never official validation data",
           "fixture_count": len(out), "trap_count": traps, "trap_ids": trap_ids,
           "gold_unresolved_trap_ids": gold_unresolved_traps,
           "fixture_hashes": {f["id"]: _sha256_obj(f) for f in out},
           "fixtures": out}
    (HERE / "calibration-fixtures-v2-9.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixture_count": len(out), "traps": traps,
                      "gold_unresolved_traps": len(gold_unresolved_traps)}))


if __name__ == "__main__":
    main()
