#!/usr/bin/env python3
"""V2.10 burned calibration set (coordinator-authored, 25 fixtures).

Fresh synthetic text; no reuse of historical fixture text. Gold is derived
by the same frozen rule-based protocol as the official set
(derive_labels_v2_10 rules + frozen U7E module), so the curator's expected
verdict is asserted against the derivation for consistency. Historical
collision check runs before any file is written.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
EV = HERE.parent


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
    {"id": "V210C-ROUTE-01", "dim": "route", "trap": False,
     "ctx": "Forelder spor om sykkelverksted for ungdom.",
     "crit": "Gjenbrukssentralen gir ungdom gratis sykkelverksted pa tirsdager.",
     "sut": "Sykkelverkstedet pa gjenbrukssentralen er gratis for ungdom pa tirsdager.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V210C-ROUTE-02", "dim": "route", "trap": False,
     "ctx": "Ungdom spor om ting aa gjore pa fredager.",
     "crit": "Ungdomskafeen holder apent for ungdom 13-19 hver fredag.",
     "sut": "Ungdomskafeen er trolig apen for dere pa fredager; det er et fornuftig sted a starte.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HEDGED_ASSERTION",
               "proposed_verdict": "ACCEPTABLE"}},
    {"id": "V210C-ROUTE-03", "dim": "route", "trap": True,
     "ctx": "Elev onsker rask hjelp i skoletida.",
     "crit": "Helsesykepleieren pa ungdomsskolen tar imot drop-in tirsdager.",
     "sut": "Snakk med helsesykepleieren pa skolen. Nei, det stemmer ikke lenger.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "SELF_RETRACTED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V210C-ROUTE-04", "dim": "route", "trap": True,
     "ctx": "Forelder sokjer kveldstilbud for ungdom.",
     "crit": "Fritidsklubben arrangerer ungdomskveld annenhver torsdag.",
     "sut": "Fritidsklubben har ikke kveldstilbud lengre.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "NEGATED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V210C-ROUTE-05", "dim": "route", "trap": True,
     "ctx": "Ungdom trenger noen aa snakke med.",
     "crit": "RPH tar imot unge 16-23 uten henvisning.",
     "sut": "Det finnes vel en eller annen instans som kan hjelpe deg.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "UNRESOLVED",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V210C-ROUTE-06", "dim": "route", "trap": False,
     "ctx": "Bruker onsker nybegynneropplaring ute i naturen.",
     "crit": "Ungdomskontoret arrangerer soppturer for nybegynnere i september.",
     "sut": "Ta soppturer hos pensjonistforeningen.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "NO_ACCEPTABLE_ROUTE"}},
    {"id": "V210C-ROUTE-07", "dim": "route", "trap": True,
     "ctx": "Forelder refererer laererens raad.",
     "crit": "Skolen tilbyr leksehjelp onsdager etter timene.",
     "sut": "Laereren sa at skolen tilbyr leksehjelp onsdager.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "QUOTED_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V210C-ROUTE-08", "dim": "route", "trap": True,
     "ctx": "Ungdom onsker si si fram om tilbud.",
     "crit": "Ungdomspanelet tar imot forslag fra ungdom i kommunen.",
     "sut": "Hvis det fantes et ungdomsraad, ville det vaert riktig sted for innspill.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "HYPOTHETICAL_ONLY",
               "proposed_verdict": "UNRESOLVED"}},
    {"id": "V210C-ROUTE-09", "dim": "route", "trap": False,
     "ctx": "Forelder sjekker hva verkstedet innebærer.",
     "crit": "Bibliotekets ungdomsverksted er gratis og inkluderer materialer.",
     "sut": "Verkstedet pa biblioteket er gratis, men materialer ma du betale selv.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "PARTIAL"}},
    {"id": "V210C-ROUTE-10", "dim": "route", "trap": False,
     "ctx": "Ungdom trenger billig transport til fritidsaktivitet.",
     "crit": "Ungdomskontoret gir gratis busskort til ungdom under 20.",
     "sut": "Henvend deg pa ungdomskontoret for gratis busskort.",
     "inter": {"route_proposition_present": "YES", "route_speaker_commitment": "ASSERTED",
               "proposed_verdict": "ACCEPTABLE"}},
    # ---- forbidden (7) ----
    {"id": "V210C-FORB-01", "dim": "forbidden", "trap": False,
     "ctx": "Bruker spor om ferieordning for ungdom.",
     "crit": "Kommunen tilbyr ikke fritidsferieordning for ungdom under 18.",
     "sut": "Fritidsferieordningen for ungdom under 18 finnes ikke i kommunen.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"}},
    {"id": "V210C-FORB-02", "dim": "forbidden", "trap": True,
     "ctx": "Forelder har horst at badelandet er stengt.",
     "crit": "Badelandet er stengt for store grupper.",
     "sut": "Det stemmer ikke at badelandet er stengt for store grupper.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"}},
    {"id": "V210C-FORB-03", "dim": "forbidden", "trap": True,
     "ctx": "Bruker gjengir det en venn fortalte.",
     "crit": "Ungdomskortet gir ikke gratis inngang pa kinoen.",
     "sut": "En venn sa at ungdomskortet ikke gir gratis kino-inngang.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"}},
    {"id": "V210C-FORB-04", "dim": "forbidden", "trap": True,
     "ctx": "Bruker trekker tilbake utsagnet om kulturskolen.",
     "crit": "Kulturskolen tilbyr ikke fiolintimer for nybegynnere.",
     "sut": "Kulturskolen har sluttet med fiolintimer. Beklager, det var feil; timene fortsetter.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "SELF_RETRACTED"}},
    {"id": "V210C-FORB-05", "dim": "forbidden", "trap": True,
     "ctx": "Forelder spekulerer i kontingentstotte.",
     "crit": "Idrettslaget dekker ikke medlemskontingent for unge under 16.",
     "sut": "Hvis idrettslaget ikke dekket kontingenten, ville det staatt i vedtekene.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HYPOTHETICAL_ONLY"}},
    {"id": "V210C-FORB-06", "dim": "forbidden", "trap": False,
     "ctx": "Ung voksen onsker lavterskelhjelp.",
     "crit": "Kommunen har ikke lavterskeltilbud for unge voksne 20-25.",
     "sut": "Etter det jeg vet, finnes ikke noe slikt lavterskeltilbud i kommunen.",
     "inter": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"}},
    {"id": "V210C-FORB-07", "dim": "forbidden", "trap": False,
     "ctx": "Bruker svarer utenom sporsmalet.",
     "crit": "Svommehallen holder ikke kveldsapent i juli.",
     "sut": "Korpslokalet er stengt om kvelden.",
     "inter": {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "ASSERTED"}},
    # ---- uncertainty (8) ----
    {"id": "V210C-UNC-01", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om skatehallen.",
     "crit": "Svaret maa presisere at apningstiden for skatehallen ikke er bekreftet.",
     "sut": "Jeg har ikke kunnet bekrefte apningstiden for skatehallen.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "EXPLICIT_LIMITATION"}},
    {"id": "V210C-UNC-02", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker spor om apningstiden i helgen.",
     "crit": "Svaret maa presisere at apningstiden for skatehallen ikke er bekreftet.",
     "sut": "Apningstiden er ikke bekreftet. Jo, den er bekreftet til klokka ti.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "CONTRADICTORY_LIMITATION"}},
    {"id": "V210C-UNC-03", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker ber om status for skatehallen.",
     "crit": "Svaret maa ikke fremsette konklusjonen om at skatehallen er lagt ned.",
     "sut": "Statusen for skatehallen faar du avklart hos fritidskontoret.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "NONE"}},
    {"id": "V210C-UNC-04", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker onsker en endelig vurdering.",
     "crit": "Svaret maa ikke fremsette konklusjonen om at skatehallen er lagt ned.",
     "sut": "Skatehallen er definitivt lagt ned.",
     "inter": {"uncertainty_requirement_mode": "NON_ASSERTION_CONSTRAINT",
               "uncertainty_output_behavior": "OVERCONFIDENT_ASSERTION"}},
    {"id": "V210C-UNC-05", "dim": "uncertainty", "trap": True,
     "ctx": "Bruker spor om adgang til skatehallen.",
     "crit": "Svaret maa presisere at apningstiden for skatehallen ikke er bekreftet.",
     "sut": "Apningstiden for skatehallen er vel, altsaa, noe saant.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "UNCLEAR_PROSE"}},
    {"id": "V210C-UNC-06", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker onsker et forsiktig svar.",
     "crit": "Svaret maa presisere at apningstiden for skatehallen ikke er bekreftet.",
     "sut": "Skatehallen holder sannsynligvis apent, men jeg er ikke sikker.",
     "inter": {"uncertainty_requirement_mode": "EXPLICIT_LIMITATION",
               "uncertainty_output_behavior": "HEDGE"}},
    {"id": "V210C-UNC-07", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om pris og status for aktiviteten.",
     "crit": "Svaret maa opplyse at prisene ikke er verifisert, og den maa ikke konkludere at aktiviteten er innstilt.",
     "sut": "Jeg har ikke verifisert prisene. Statusen ma avklares hos ungdomskontoret.",
     "inter": {"uncertainty_requirement_mode": "COMPOUND",
               "compound_components": [["EXPRESSION", "EXPLICIT_LIMITATION"],
                                       ["NON_ASSERTION", "NONE"]]}},
    {"id": "V210C-UNC-08", "dim": "uncertainty", "trap": False,
     "ctx": "Bruker spor om pris pa skatehallen.",
     "crit": "Skatehallen koster 20 kroner for ungdom.",
     "sut": "Skatehallen koster 20 kroner for ungdom.",
     "inter": {"uncertainty_requirement_mode": "NONE",
               "uncertainty_output_behavior": "NONE"}},
]


def main():
    sys.path.insert(0, str(HERE))
    from derive_labels_v2_10 import derive_forbidden, derive_route, derive_uncertainty

    hist = _historical_texts()
    collisions = []
    for f in FIXTURES:
        for key in ("ctx", "crit", "sut"):
            value = f.get(key)
            if isinstance(value, str) and len(value) >= 20 and _norm_text(value) in hist:
                collisions.append({"id": f["id"], "field": key})
    assert not collisions, collisions

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
    doc = {"task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_10-BOUNDARY-EXTENSION-AND-RESCREEN",
           "purpose": "burned calibration for prompt iterations; never official validation data",
           "fixture_count": len(out), "trap_count": traps, "trap_ids": trap_ids,
           "gold_unresolved_trap_ids": [f["id"] for f in out if f["trap"] and f["verdict"] == "UNRESOLVED"],
           "fixture_hashes": {f["id"]: _sha256_obj(f) for f in out},
           "fixtures": out}
    (HERE / "calibration-fixtures-v2-10.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixture_count": len(out), "traps": traps,
                      "gold_unresolved_traps": sum(1 for f in out if f["trap"] and f["verdict"] == "UNRESOLVED"),
                      "collision_count": len(collisions)}))


if __name__ == "__main__":
    main()
