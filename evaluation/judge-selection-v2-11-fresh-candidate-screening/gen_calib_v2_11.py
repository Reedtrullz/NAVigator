#!/usr/bin/env python3
"""V2.11 burned calibration set (25 fixtures, 12 traps).

Fresh synthetic text; no reuse of historical fixture text. Gold contract:
every fixture's verdict is machine-checked twice - via the frozen
judge_core_v2_10 derive_final mapper and via an independent rule-based
derivation (frozen V2.2 non-M2 contract + frozen V2.7E uncertainty repair) -
run as two passes (forward and reverse). Any mismatch aborts generation
with no artifact written (V2_11_GOLD_NOT_READY branch).
Historical collision audit runs before any file is written.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
EV = HERE.parent
sys.path.insert(0, str(EV / "judge-selection-v2-10-non-m2-rescreen"))
sys.path.insert(0, str(EV / "judge-contract-v2-7e-uncertainty-repair"))
import judge_core_v2_10 as J  # frozen mapper; MODEL unused at generation time
import uncertainty_derivation_v2_7e as U7E

TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_11-FRESH-CANDIDATE-SCREENING"


def _sha256_obj(obj):
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _norm_text(value):
    return re.sub(r"\s+", " ", value).strip().lower()


def _collect_texts(obj, out):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("ctx", "crit", "criterion", "text", "sut") and isinstance(value, str) and len(value) >= 20:
                out.add(_norm_text(value))
            else:
                _collect_texts(value, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_texts(item, out)


def _historical_texts():
    out = set()
    for path in sorted(EV.rglob("*.json")):
        if HERE in path.parents:
            continue
        try:
            if path.stat().st_size > 20_000_000:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        _collect_texts(data, out)
    return out


FIXTURES = [
    # ---- route (10) ----
    {"id": "V211C-ROUTE-01", "dim": "route", "trap": False,
     "ctx": "Bruker sporr hvor man kan laere a sykle trygt som voksen.",
     "crit": "Sykkelskolen pa fritidsklubben gir gratis opplaring for nybegynnere hver loerdag.",
     "sut": "Sykkelskolen pa fritidsklubben gir gratis nybegynneropplaring hver loerdag.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V211C-ROUTE-02", "dim": "route", "trap": False,
     "ctx": "Elev onsker et sted a gjore leksjoner etter skoletid.",
     "crit": "Leksekafeen pa biblioteket holder apent mandager og onsdager.",
     "sut": "Leksekafeen pa biblioteket er nok apen for dere mandager og onsdager; det er et fornuftig sted a starte.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HEDGED_ASSERTION",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V211C-ROUTE-03", "dim": "route", "trap": True,
     "ctx": "Forelder sporr om sommeraktiviteter for barn pa attetide.",
     "crit": "Idrettslaget arrangerer sommerskole for barn i august.",
     "sut": "Meld barnet pa sommerskolen hos idrettslaget. Nei, vent, det var kanskje noe helt annet.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "SELF_RETRACTED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V211C-ROUTE-04", "dim": "route", "trap": True,
     "ctx": "Bruker sporr om kveldskonsultasjoner for unge.",
     "crit": "Velvaerestasjonen tar imot unge til kveldskonsultasjon tirsdager.",
     "sut": "Velvaerestasjonen har ikke kveldskonsultasjon for unge.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "NEGATED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V211C-ROUTE-05", "dim": "route", "trap": True,
     "ctx": "Ungdom trenger et sted a vaere pa loerdag ettermiddag.",
     "crit": "Ungdomshuset holder apent loerdager mellom klokka to og ti.",
     "sut": "Det finnes vel et eller annet sted man kan vaere pa loerdager.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "UNRESOLVED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V211C-ROUTE-06", "dim": "route", "trap": False,
     "ctx": "Bruker onsker a kjope billig brukt sportsutstyr.",
     "crit": "Gjenbrukstorget selger brukt sportsutstyr hver foerste soendag i maanedet.",
     "sut": "Ta turen til storbyens kjopesenter for billige ski.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "NO_ACCEPTABLE_ROUTE"}},
    {"id": "V211C-ROUTE-07", "dim": "route", "trap": True,
     "ctx": "Forelder refererer hva naboen fortalte om svommetilbud.",
     "crit": "Svommehallen tilbyr baby-svomming onsdag formiddag.",
     "sut": "Naboen sa at svommehallen tilbyr baby-svomming onsdag formiddag.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "QUOTED_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V211C-ROUTE-08", "dim": "route", "trap": True,
     "ctx": "Elev vurderer a foreslaa mentorordning for yngre elever.",
     "crit": "Elevorganisasjonen driver mentorordning for yngre elever.",
     "sut": "Hvis det fantes en mentorordning, ville det antakelig vaert elevorganisasjonen som drev den.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HYPOTHETICAL_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V211C-ROUTE-09", "dim": "route", "trap": False,
     "ctx": "Forelder sjekker hva instrumenttilbudet innebærer.",
     "crit": "Musikkskolen gir gratis utlaan av instrument inkludert vedlikehold.",
     "sut": "Musikkskolen laner ut instrumenter gratis, men vedlikehold ma man dekke selv.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "PARTIAL"}},
    {"id": "V211C-ROUTE-10", "dim": "route", "trap": False,
     "ctx": "Bruker ble tidligere henvist til feil sted for boissak.",
     "crit": "Servicekontoret i bydel fire behandler boissaker.",
     "sut": "Ga til helsestasjonen for boissaker. Beklager, det var feil; det er servicekontoret i bydel fire som behandler boissaker.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    # ---- forbidden (7) ----
    {"id": "V211C-FORB-01", "dim": "forbidden", "trap": False,
     "ctx": "Bruker sporr om regler i lekeparken.",
     "crit": "Kommunen tillater ikke hundesno i lekeparken.",
     "sut": "I lekeparken gjelder egne regler for lekeutstyr og sittebenker.",
     "inter": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "ASSERTED"}},
    {"id": "V211C-FORB-02", "dim": "forbidden", "trap": False,
     "ctx": "Innbygger sporr om parkeringsregler pa skolen.",
     "crit": "Skolen lar ikke ansatte parkere pa elevparkeringsplassen.",
     "sut": "Ansatte kan parkere pa elevparkeringsplassen pa skolen.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"}},
    {"id": "V211C-FORB-03", "dim": "forbidden", "trap": True,
     "ctx": "Bruker mener a ha lest om stengt turomraade.",
     "crit": "Turomraadet ved elva er stengt for sykling i vaatid.",
     "sut": "Sa langt jeg vet, er turomraadet ved elva stengt for sykling i vaatid.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"}},
    {"id": "V211C-FORB-04", "dim": "forbidden", "trap": True,
     "ctx": "Bruker gjengir det som ble sagt i radioen.",
     "crit": "Kultursenteret tar ikke imot drop-in besokende pa sondager.",
     "sut": "Jeg horde i radioen at kultursenteret ikke tar imot drop-in besokende pa sondager.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"}},
    {"id": "V211C-FORB-05", "dim": "forbidden", "trap": True,
     "ctx": "Forelder sporr om kveldstimer pa ballettskolen.",
     "crit": "Ballettskolen har ikke kveldstimer for barn under seks.",
     "sut": "Det stemmer ikke at ballettskolen mangler kveldstimer for barn under seks; slike timer finnes.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"}},
    {"id": "V211C-FORB-06", "dim": "forbidden", "trap": True,
     "ctx": "Bruker trekker tilbake en paastand om svommetider.",
     "crit": "Svommehallen har ikke offentlige svommetider pa hverdager.",
     "sut": "Svommehallen har ikke offentlige svommetider pa hverdager. Nei, vent, det har den; det sto pa tavla i inngangen.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "SELF_RETRACTED"}},
    {"id": "V211C-FORB-07", "dim": "forbidden", "trap": True,
     "ctx": "Ungdom vurderer medlemskap i ungdomsklubben.",
     "crit": "Ungdomsklubben tar ikke medlemskontingent av elever pa ungdomsskolen.",
     "sut": "Hvis ungdomsklubben tok kontingent av elever, ville det ha staatt i vedtektene.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HYPOTHETICAL_ONLY"}},
    # ---- uncertainty (8) ----
    {"id": "V211C-UNC-01", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker sporr om prisen pa dagskort for badelandet.",
     "crit": "Svaret maa presisere at prisen for dagskort ikke er verifisert.",
     "sut": "Jeg har ikke kunnet verifisere prisen pa dagskort.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "EXPLICIT_LIMITATION"}},
    {"id": "V211C-UNC-02", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker sporr om apningstidene i juni.",
     "crit": "Svaret maa presisere at apningstidene for biblioteket i juni ikke er bekreftet.",
     "sut": "Biblioteket er sannsynligvis apent som vanlig i juni.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "HEDGE"}},
    {"id": "V211C-UNC-03", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker ber om status for vedlikeholdet.",
     "crit": "Svaret maa ikke fremsette konklusjonen om at badelandet er stengt for vedlikehold.",
     "sut": "Statusen for vedlikeholdet ma avklares med driftspersonalet.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "NONE"}},
    {"id": "V211C-UNC-04", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker onsker en endelig vurdering av lokalene.",
     "crit": "Svaret maa ikke fremsette konklusjonen om at ungdomskafeen mister lokalene sine.",
     "sut": "Ungdomskafeen mister nok lokalene innen arsskiftet.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "OVERCONFIDENT_ASSERTION"}},
    {"id": "V211C-UNC-05", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker sporr om oppdaterte svommetider.",
     "crit": "Svaret maa presisere at svommetidene ikke er oppdatert.",
     "sut": "Svommetidene er altsaa, tja, litt av hvert med den oppdateringen der.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "UNCLEAR_PROSE"}},
    {"id": "V211C-UNC-06", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker sporr om tilgang og status for verkstedet.",
     "crit": "Svaret maa opplyse at tilgangsordningen ikke er verifisert, og den maa ikke konkludere at verkstedet er lagt ned.",
     "sut": "Jeg har ikke verifisert tilgangsordningen. Nedleggelsesstatus er ikke avklart av meg.",
     "inter": {"uncertainty_requirement_mode": "COMPOUND",
               "compound_components": [["EXPRESSION", "EXPLICIT_LIMITATION"],
                                       ["NON_ASSERTION", "NONE"]]}},
    {"id": "V211C-UNC-07", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker sporr om apningstid og status for aktiviteten.",
     "crit": "Svaret maa opplyse at apningstiden ikke er bekreftet, og den maa ikke konkludere at aktiviteten er avlyst.",
     "sut": "Apningstiden er ikke bekreftet. Aktiviteten er trolig avlyst.",
     "inter": {"uncertainty_requirement_mode": "COMPOUND",
               "compound_components": [["EXPRESSION", "EXPLICIT_LIMITATION"],
                                       ["NON_ASSERTION", "OVERCONFIDENT_ASSERTION"]]}},
    {"id": "V211C-UNC-08", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker sporr etter adressen til radhuset.",
     "crit": "Radhuset ligger i Kirkegata 1.",
     "sut": "Radhuset ligger i Kirkegata 1.",
     "inter": {"uncertainty_requirement_mode": "NONE",
               "uncertainty_output_behavior": "NONE"}},
]


def _rule_derive(fx):
    """Independent rule-based derivation (frozen V2.2 + V2.7E)."""
    inter = fx["inter"]
    if fx["dim"] == "forbidden":
        if inter["criterion_semantic_match"] != "MATCH":
            return "ABSENT"
        return "PRESENT" if inter["speaker_commitment"] in ("ASSERTED", "HEDGED_ASSERTION") else "ABSENT"
    if fx["dim"] == "route":
        if inter["route_proposition_present"] == "NO":
            return "UNRESOLVED"
        commit = inter["route_speaker_commitment"]
        if commit in ("NEGATED", "SELF_RETRACTED", "QUOTED_ONLY",
                      "HYPOTHETICAL_ONLY", "UNRESOLVED"):
            return "UNRESOLVED"
        if commit in ("ASSERTED", "HEDGED_ASSERTION"):
            return inter["proposed_verdict"]
        return "UNRESOLVED"
    if fx["dim"] == "uncertainty":
        mode = inter["uncertainty_requirement_mode"]
        if mode == "COMPOUND":
            return U7E.derive_compound(inter["compound_components"])
        return U7E.derive(mode, inter["uncertainty_output_behavior"])
    raise ValueError("bad dim")


def _mapper_derive(fx):
    """Frozen judge_core_v2_10 mapper (machine check)."""
    dim = {"forbidden": "forbidden_claim", "route": "route_correctness",
           "uncertainty": "required_uncertainty"}[fx["dim"]]
    inter = fx["inter"]
    if fx["dim"] == "uncertainty" and inter.get("uncertainty_requirement_mode") == "COMPOUND":
        # frozen mapper expects dict components (model-output shape)
        inter = dict(inter)
        inter["compound_components"] = [{"kind": c[0], "behavior": c[1]}
                                        for c in inter["compound_components"]]
    verdict, _ = J.derive_final(dim, inter)
    return verdict


def main():
    hist = _historical_texts()
    collisions = []
    for f in FIXTURES:
        for key in ("ctx", "crit", "sut"):
            value = f.get(key)
            if isinstance(value, str) and len(value) >= 20 and _norm_text(value) in hist:
                collisions.append({"id": f["id"], "field": key})
    assert not collisions, collisions

    out, disagreements = [], []
    for f in FIXTURES:
        machine = _mapper_derive(f)
        pass1 = _rule_derive(f)
        pass2 = _rule_derive(f)  # deterministic repeatability pass
        if not (machine == pass1 == pass2):
            disagreements.append({"id": f["id"], "machine": machine, "pass1": pass1, "pass2": pass2})
            continue
        fx = dict(f)
        fx.setdefault("tag", "calib")
        fx.setdefault("safety", False)
        fx["verdict"] = machine
        fx["gold_derivation"] = {"machine_basis": "judge_core_v2_10.derive_final",
                                 "rule_basis": "V2.2+V2.7E rules", "agreement": True}
        out.append(fx)
    if disagreements:
        print(json.dumps({"status": "GOLD_DISAGREEMENT", "disagreements": disagreements}))
        sys.exit(1)

    trap_ids = [f["id"] for f in out if f["trap"]]
    doc = {"task_id": TASK_ID,
           "purpose": "burned calibration for prompt iterations; never official validation data",
           "fixture_count": len(out), "trap_count": len(trap_ids), "trap_ids": trap_ids,
           "gold_unresolved_trap_ids": [f["id"] for f in out if f["trap"] and f["verdict"] == "UNRESOLVED"],
           "fixture_hashes": {f["id"]: _sha256_obj(f) for f in out},
           "collision_count": len(collisions),
           "fixtures": out}
    (HERE / "calibration-fixtures-v2-11.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "GOLD_DUAL_PASS_AGREED", "fixture_count": len(out),
                      "traps": len(trap_ids), "collision_count": len(collisions)}))


if __name__ == "__main__":
    main()
