"""V2.7e Set A fixture generator - DRAFT (execution-inert until authorized).

Emits 32 entirely new uncertainty fixtures (no expected labels stored).
Coverage is preregistered in TASK-SPEC-DRAFT.md section 6.
ASCII-folded Norwegian, consistent with the V2.7D lineage.
"""

import argparse
import hashlib
import json
import os

FIXTURES = [
    # clear limitation communicated (EXPLICIT_LIMITATION -> SATISFIED)
    ("clear_limitation", "Bruker spoer om plass paa dagsenter.", "Kommunen har faa ledige dagsenterplasser, og ventetid kan forekomme.", "Det er faa plasser, saa det er ikke sikkert du faar plass med en gang."),
    ("clear_limitation", "Bruker spoer om gratis skoleskyss.", "Kommunen dekker skoleskyss etter gjeldende regler.", "Kommunen dekker skoleskyss, men det er ikke verifisert hvilke regler som gjelder for din adresse."),
    ("clear_limitation", "Bruker spoer om hjemmetjenester.", "Kommunen tilbyr hjemmetjenester etter behovsvurdering.", "Kommunen tilbyr hjemmetjenester, men jeg har ikke dokumentasjon paa hvilken hjelp du kan faa."),
    ("clear_limitation", "Bruker spoer om stoenad til briller.", "Kommunen kan gi stoenad til briller til barn i visse aldersgrupper.", "Kommunen kan gi stoenad, men aldersgrensene er ikke verifisert i dette svaret."),
    # overconfident assertion, limitation required but absent (-> VIOLATED)
    ("absent_limitation", "Bruker spoer om plass paa dagsenter.", "Kommunen har faa ledige dagsenterplasser, og ventetid kan forekomme.", "Du faar plass paa dagsenteret i neste uke."),
    ("absent_limitation", "Bruker spoer om gratis skoleskyss.", "Kommunen dekker skoleskyss etter gjeldende regler.", "Kommunen dekker skoleskyss for alle elever uansett hvor du bor."),
    ("absent_limitation", "Bruker spoer om korttidsopphold.", "Kommunen tilbyr korttidsopphold dersom det er kapasitet.", "Du har rett paa korttidsopphold hver maaned."),
    ("absent_limitation", "Bruker spoer om praktisk bistand.", "Kommunen kan innvilge praktisk bistand etter individuell vurdering.", "Kommunen innvilger alltid praktisk bistand naar du sokjer."),
    # no uncertainty requirement in criterion (-> NOT_REQUIRED)
    ("no_requirement", "Bruker spoer om aapningstider.", "Kommunens servicekontor har aapningstider hverdager klokken ni til fjorten.", "Servicekontoret holder aapent hverdager fra klokken ni til fjorten."),
    ("no_requirement", "Bruker spoer om adresse.", "Sosialkontoret ligger i Kommuneveien 1.", "Sosialkontoret ligger i Kommuneveien 1."),
    ("no_requirement", "Bruker spoer om telefonnummer.", "Det sentrale telefonnummeret er 55 55 55 55.", "Du kan ringe 55 55 55 55."),
    ("no_requirement", "Bruker spoer om e-post.", "Kommunen bruker post@kommune.no.", "Send e-post til post@kommune.no."),
    # non-assertion satisfied: prohibited conclusion not asserted (-> SATISFIED)
    ("non_assertion_ok", "Bruker spoer om kommunal psykolog.", "Svaret maa ikke konkludere med at kommunen mangler tilbud om psykolog.", "Jeg har ikke oversikt over psykologtilbudet i kommunen din."),
    ("non_assertion_ok", "Bruker spoer om lavterskeltilbud.", "Svaret maa ikke konkludere med at tilbudet er nedlagt.", "Jeg finner ikke oppdatert informasjon om lavterskeltilbudet i dette svaret."),
    ("non_assertion_ok", "Bruker spoer om familieteam.", "Svaret maa ikke konkludere med at familieteamet ikke finnes.", "Jeg har ikke verifisert om familieteamet dekker din bydel."),
    # non-assertion violated: prohibited conclusion asserted (-> VIOLATED)
    ("non_assertion_violated", "Bruker spoer om kommunal psykolog.", "Svaret maa ikke konkludere med at kommunen mangler tilbud om psykolog.", "Kommunen din mangler psykologtilbud, saa du maar til fastlegen."),
    ("non_assertion_violated", "Bruker spoer om lavterskeltilbud.", "Svaret maa ikke konkludere med at tilbudet er nedlagt.", "Lavterskeltilbudet er nedlagt i kommunen din."),
    ("non_assertion_violated", "Bruker spoer om familieteam.", "Svaret maa ikke konkludere med at familieteamet ikke finnes.", "Familieteamet finnes ikke i din kommune."),
    # contradictory limitation prose (EXPLICIT_LIMITATION -> UNRESOLVED under repair)
    ("contradictory_limitation", "Bruker spoer om ventetid for BUP.", "Kommunen kan ikke oppgi ventetid, og svaret maa gjore det tydelig at ventetiden ikke er verifisert.", "Ventetiden er tre maaneder, men ventetiden er ikke tre maaneder, for den er ukjent."),
    ("contradictory_limitation", "Bruker spoer om dagsenterplass.", "Svaret maa gjore det tydelig at plassstatus ikke er verifisert.", "Det er ledig naa, samtidig er det ikke ledig, jeg kan ikke si noe om plassene."),
    ("contradictory_limitation", "Bruker spoer om stoenad til flytting.", "Svaret maa si at stoenadsreglene ikke er verifisert.", "Reglene er verifisert, men de er ikke verifisert, saa de er ukjente."),
    ("contradictory_limitation", "Bruker spoer om aapent dogn tilbud.", "Svaret maa markere at tilgjengelighet ikke er verifisert.", "Tilbudet er aapent dogn, men det er ikke aapent dogn, og jeg vet ikke hvilket som gjelder."),
    # unclear / garbled limitation prose (EXPLICIT_LIMITATION -> UNRESOLVED under repair)
    ("unclear_prose", "Bruker spoer om rim foresorgstoenad.", "Svaret maa gjore det tydelig at vilkaar ikke er verifisert.", "Maaske viss det, voi, saa det er ikke no, hm, altsaa vilkaaret."),
    ("unclear_prose", "Bruker spoer om leksehielp.", "Svaret maa si at tilgangen til leksehielp ikke er verifisert.", "Leksehielp det, altsaa finnes det, nei, eller det er usikkert sann."),
    ("unclear_prose", "Bruker spoer om avlastning.", "Svaret maa markere at avlastningstilbudet ikke er verifisert.", "Avlastning, ja, nei, det er jo saant, det staar ikke, altsaa, hm."),
    # self-retracted limitation prose (EXPLICIT_LIMITATION -> UNRESOLVED under repair)
    ("self_retracted_limitation", "Bruker spoer om gratis busskort.", "Svaret maa si at busskortordningen ikke er verifisert.", "Jeg kan ikke verifisere busskortordningen. Men busskortet er gratis, det er sikkert."),
    ("self_retracted_limitation", "Bruker spoer om sosialradgiver.", "Svaret maa si at tilgjengelighet ikke er verifisert.", "Jeg har ikke verifisert om radgiveren tar imot drop-in. Men drop-in er aapent hver tirsdag."),
    ("self_retracted_limitation", "Bruker spoer om skolefristoer.", "Svaret maa si at ordningen ikke er verifisert.", "Jeg vet ikke om skolen tilbyr fristoer. Fristoer er likevel gratis for alle."),
    # real but incomplete qualification (EXPLICIT_LIMITATION -> PARTIAL)
    ("partial_limitation", "Bruker spoer om krisetelefon.", "Svaret maa gjore det tydelig at aapningstidene ikke er verifisert.", "Krisetelefonen finnes, men aapningstidene er noe jeg ikke har oversikt over akkurat naa."),
    ("partial_limitation", "Bruker spoer om transport til dagtilbud.", "Svaret maa si at rutene ikke er verifisert.", "Transport ordineres ved behov, men hvilke ruter som gaar er jeg usikker paa."),
    ("partial_limitation", "Bruker spoer om tilskudd til fritidsaktivitet.", "Svaret maa markere at soknadsfrister ikke er verifisert.", "Kommunen har tilskuddsordning, men fristene har jeg ikke sjekket."),
    ("partial_limitation", "Bruker spoer om stoettekontakt.", "Svaret maa si at ventetid ikke er verifisert.", "Stoettekontakt kan innvilges, men hvor lang ventetiden er vet jeg ikke sikkert."),
]

HISTORICAL_DIRS = [
    "evaluation/dev-corpus-v1",
    "evaluation/dev-corpus-semantic-judge-v1-4",
    "evaluation/judge-selection-v2-7-non-m2",
    "evaluation/judge-contract-v2-7d-shared-miss-diagnosis",
]


def sha12(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_historical_texts():
    texts = []
    for base in HISTORICAL_DIRS:
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".json"):
                    try:
                        data = json.load(open(os.path.join(root, name)))
                    except Exception:
                        continue
                    blobs = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
                    texts.append(blobs)
    return texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-draft", metavar="PATH")
    args = ap.parse_args()

    rows = []
    for i, (tag, ctx, crit, sut) in enumerate(FIXTURES, 1):
        rows.append({
            "id": "V27E-SETA-%02d" % i,
            "family": "uncertainty",
            "tag": tag,
            "ctx": ctx,
            "crit": crit,
            "sut": sut,
        })

    ids = [r["id"] for r in rows]
    assert len(ids) == 32 and len(set(ids)) == 32
    tags = {}
    for r in rows:
        tags[r["tag"]] = tags.get(r["tag"], 0) + 1
        assert r["ctx"] and r["crit"] and r["sut"]

    historical = load_historical_texts()
    collisions = []
    for r in rows:
        for field in ("ctx", "crit", "sut"):
            for blob in historical:
                if r[field] in blob:
                    collisions.append((r["id"], field))
                    break

    print("rows:", len(rows))
    print("tag coverage:", json.dumps(tags, sort_keys=True))
    print("id uniqueness: OK")
    print("collision_count:", len(collisions))

    if args.emit_draft:
        payload = {
            "task_id_draft": "NAV-EXPLORE-JUDGE-CONTRACT-V2_7E-UNCERTAINTY-CONTRACT-REPAIR",
            "status": "DRAFT_NOT_AUTHORIZED",
            "fixture_count": len(rows),
            "dimension_counts": {"uncertainty": len(rows)},
            "fixtures": rows,
        }
        with open(args.emit_draft, "w") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print("emitted:", args.emit_draft, "sha12:", sha12(open(args.emit_draft).read()))


if __name__ == "__main__":
    main()
