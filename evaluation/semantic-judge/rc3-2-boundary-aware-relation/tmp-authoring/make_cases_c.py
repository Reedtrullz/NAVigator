"""Author fresh architecture suite part C: exception-heavy, condition
top-up, and compound top-up cases to meet spec section 23 coverage."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases_c.json")

CASES = []
KB = None


def case(cid, claim, evidence, rel, dims, group, critical=False,
         compound=False, expected_atoms=None):
    row = {
        "case_id": cid,
        "claim": claim,
        "evidence": [{"span_id": "S%d" % (i + 1), "text": t}
                     for i, t in enumerate(evidence)],
        "compound": compound,
        "rel": rel,
        "critical": critical,
        "group": group,
        "kb_ref": KB,
        "expected_dims": dims,
    }
    if expected_atoms:
        row["expected_atoms"] = expected_atoms
    CASES.append(row)


KB = "55-bostotte-i-dybden.md"

# exception bucket top-up (10)
case("BA-128", "Bokollektiv gir aldri bostotte.",
     ["Bokollektiv er som hovedregel nei, unntak for kollektiv av "
      "helsemessige eller sosiale grunner."],
     "CONTRADICTS", {"exception": "EXCEPTION_CONFLICT",
                     "polarity": "EXPLICIT_CONFLICT"}, "exception",
     critical=True)

case("BA-129", "Bokollektiv kan godkjennes av helsemessige grunner.",
     ["Bokollektiv er som hovedregel nei, unntak for kollektiv av "
      "helsemessige eller sosiale grunner."],
     "ENTAILS", {"exception": "EXACT_MATCH"}, "exception")

case("BA-130", "Elever og studenter folger de vanlige bostotte-reglene.",
     ["Studenter, elever og larlinger folger egne regler."],
     "CONTRADICTS", {"exception": "EXCEPTION_CONFLICT",
                     "polarity": "EXPLICIT_CONFLICT"}, "exception")

case("BA-131", "Under 18 ar med barn kan fa bostotte.",
     ["Alder: over 18 ar og ikke i forstegangstjenesten, eller "
      "under 18 ar med barn."],
     "ENTAILS", {"exception": "EXACT_MATCH"}, "exception")

case("BA-132", "Alle boliger kvalifiserer for bostotte.",
     ["Boligen ma vare godkjent til boligformal og ha egen inngang, "
      "eget bad og toalett, kjokkenlosning og mulighet for hvile."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "exception")

case("BA-133", "Ung ufor far gunstigere egenandel i bostotte.",
     ["Ung ufor far gunstigere egenandel; en overgangsordning "
      "gjelder ufore som mottok bostotte i desember 2014."],
     "ENTAILS", {"exception": "EXACT_MATCH",
                 "temporal": "TEMPORAL_COMPATIBLE"}, "exception")

case("BA-134", "Overgangsordningen gjelder alle ufore.",
     ["En overgangsordning gjelder ufore som mottok bostotte i "
      "desember 2014."],
     "CONTRADICTS", {"exception": "EXCEPTION_CONFLICT",
                     "scope": "SCOPE_CONFLICT"}, "exception",
     critical=True)

case("BA-135", "Oppvarmingstillegg gis alltid.",
     ["Det er 613 kroner i maneden til oppvarming hvis oppvarming "
      "ikke er dekket av leien."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "exception")

case("BA-136", "Barnets formue holdes alltid utenfor bostottegrunnlaget.",
     ["Har du hoy formue fordi du skatter for barnets formue, kan "
      "du soke om at barnets formue holdes utenfor, hvis den er "
      "registrert i barnets navn."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING",
      "modality": "SOURCE_WEAKER_THAN_CLAIM"}, "exception",
     critical=True)

case("BA-137", "Manglende flyttemelding er en vanlig avslagsarsak for "
     "bostotte.",
     ["Manglende flyttemelding til Folkeregisteret er en av "
      "Husbankens vanlige avslagsarsaker."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "exception")

# condition bucket top-up (2)
case("BA-138", "Du far bostotte nar inntekten din er lav.",
     ["Bostotte er en stotteordning for husholdninger med lave "
      "inntekter og hoye boutgifter."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_topup")

case("BA-139", "Bostotte beregnes av faktiske boutgifter og inntekt "
     "i soknadsm aneden.",
     ["Bostotte beregnes maned for maned ut fra faktiske "
      "boutgifter og husstandens inntekt i soknadsmaneden."],
     "ENTAILS", {"condition": "EXACT_MATCH"}, "condition_topup")

# compound bucket top-up (8)
case("BA-140", "Bokollektiv gir normalt ikke bostotte, og studenter "
     "folger egne regler.",
     ["Bokollektiv er som hovedregel nei, unntak av helsemessige "
      "eller sosiale grunner.",
      "Studenter, elever og larlinger folger egne regler."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "compound",
     compound=True,
     expected_atoms=["RELATED_BUT_INSUFFICIENT",
                     "RELATED_BUT_INSUFFICIENT"])

case("BA-141", "Full utvidet barnetrygd er 2 572 kroner, og delt "
     "utvidet er 1 286 kroner.",
     ["Full sats utvidet barnetrygd er 2 572 kroner i maneden.",
      "Delt utvidet barnetrygd er 1 286 kroner i maneden."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "compound", compound=True,
     expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-142", "Full utvidet barnetrygd er 2 572 kroner, og delt "
     "utvidet er 2 572 kroner.",
     ["Full sats utvidet barnetrygd er 2 572 kroner i maneden.",
      "Delt utvidet barnetrygd er 1 286 kroner i maneden."],
     "PARTIAL", {"numeric_quantity": "NUMERIC_CONFLICT"},
     "compound", compound=True,
     expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-143", "Ordinær barnetrygd folger barnet, og deles likt ved "
     "delt fast bosted.",
     ["Ordinær barnetrygd folger barnet.",
      "Ved delt fast bosted deles den likt mellom foreldrene."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-144", "Samvaersavtale gir delt barnetrygd, og delingen skjer "
     "automatisk.",
     ["Samvaersavtale gir ikke delt barnetrygd; det kreves delt "
      "fast bosted.",
      "Begge foreldre ma sokke for at delingen skal skje."],
     "PARTIAL", {"polarity": "EXPLICIT_CONFLICT"}, "compound",
     compound=True, expected_atoms=["CONTRADICTS", "CONTRADICTS"])

case("BA-145", "Barn under 18 ar med barn kan fa bostotte, og "
     "forstegangstjenesten gir ikke fritak.",
     ["Alder: over 18 ar og ikke i forstegangstjenesten, eller "
      "under 18 ar med barn."],
     "PARTIAL", {"exception": "EXCEPTION_CONFLICT"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-146", "Elever under 18 ar trenger ikke samtykke fra "
     "foreldre, og 12-16-aringer kan samtykke til helsehjelp "
     "foreldrene ikke er informert om.",
     ["Foreldre samtykker pa vegne av barn under 16 ar.",
      "12-16 ar kan samtykke til helsehjelp i forhold foreldrene "
      "ikke er informert om."],
     "PARTIAL", {"actor": "DIFFERENT_ACTOR",
                 "polarity": "EXPLICIT_CONFLICT"}, "compound",
     compound=True, expected_atoms=["CONTRADICTS", "ENTAILS"])

case("BA-147", "Utbetalingen skjer den 20., og avslag viderefores i "
     "inntil tre maneder.",
     ["Utbetaling skjer den 20. i maneden etter soknadsmaneden.",
      "Avslag viderefores automatisk i inntil tre maneder."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

# Exception top-up to meet section 23 minimum (15 non-NA exception dims).
case("BA-148", "De to ytelsene kan kombineres, men bare hvis utvidet "
     "vilkar er oppfylt for akkurat den forelderen.",
     ["De to ytelsene kan kombineres, men bare hvis utvidet vilkar er "
      "oppfylt for akkurat den forelderen."],
     "ENTAILS", {"exception": "EXACT_MATCH",
                 "clause_coverage": "EXACT_MATCH"}, "exception")

case("BA-149", "En forelder med delt ordinær barnetrygd kan kombinere "
     "den med delt utvidet barnetrygd, men bare hvis utvidet vilkar er "
     "oppfylt for akkurat den andre forelderen.",
     ["De to ytelsene kan kombineres, men bare hvis utvidet vilkar er "
      "oppfylt for akkurat den forelderen."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "ACTOR_UNRESOLVED", "exception": "EXACT_MATCH",
      "clause_coverage": "PARTIAL_OVERLAP"}, "exception",
     critical=True)

case("BA-150", "En ung person under 18 ar kan alltid fa bostotte.",
     ["Alder: over 18 ar og ikke i forstegangstjenesten, eller "
      "under 18 ar med barn."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING", "exception": "EXCEPTION_CONFLICT",
      "clause_coverage": "PARTIAL_OVERLAP"}, "exception",
     critical=True)

case("BA-151", "En person som bor i bokollektiv kan fa bostotte.",
     ["Bokollektiv: som hovedregel nei, unntak for kollektiv av "
      "helsemessige eller sosiale grunner."],
     "PARTIAL", {"exception": "EXCEPTION_CONFLICT",
                 "clause_coverage": "PARTIAL_OVERLAP"}, "exception",
     critical=True)

case("BA-152", "Barn uten delt fast bosted kan foeres pa den andre "
     "forelderens bostottesoknad.",
     ["Barn uten delt fast bosted, bare samvar, kan ikke foeres pa "
      "den andre forelderens soknad."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT",
                     "exception": "EXCEPTION_CONFLICT",
                     "clause_coverage": "PARTIAL_OVERLAP"}, "exception",
     critical=True)

DOC = {
    "suite": "fresh-architecture-cases-v1",
    "part": "C",
    "frozen": False,
    "note": "Part C: exception/condition/compound coverage top-up.",
    "cases": CASES,
}

with open(OUT, "w") as f:
    json.dump(DOC, f, ensure_ascii=False, indent=1)
print("wrote", OUT, len(CASES), "cases")
