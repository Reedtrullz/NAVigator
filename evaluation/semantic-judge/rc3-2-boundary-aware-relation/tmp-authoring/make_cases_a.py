"""Author fresh architecture suite part A (modality + condition buckets).

Case shapes generalize across failure modes; no case IDs, no literal
case->relation maps from burned sets (spec section 21).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases_a.json")

CASES = []
KB = None


def case(cid, claim, evidence, rel, dims, group, critical=False,
         compound=False, expected_atoms=None):
    CASES.append({
        "case_id": cid,
        "claim": claim,
        "evidence": [{"span_id": "S1", "text": t} for t in evidence],
        "compound": compound,
        "rel": rel,
        "critical": critical,
        "group": group,
        "kb_ref": KB,
        "expected_dims": dims,
    })


# --- modality_strength: 30 cases ------------------------------------
KB = "25-kommunale-psykiske-tjenester-barn-unge.md"

case("BA-001", "Rask psykisk helsehjelp er for innbyggere over 16 aar.",
     ["Rask psykisk helsehjelp er for innbyggere over 16 aar."],
     "ENTAILS", {"modality": "EXACT_MATCH", "actor": "SAME_ACTOR",
                 "polarity": "EXACT_MATCH"}, "modality_strength")

case("BA-002", "Kommunen kan tilby helsestasjonstjeneste til barn 0-20 aar.",
     ["Kommunen skal tilby helsestasjons- og skolehelsetjeneste til barn "
      "og ungdom 0-20 aar."],
     "ENTAILS", {"modality": "SOURCE_STRONGER_THAN_CLAIM",
                 "polarity": "EXACT_MATCH"}, "modality_strength")

case("BA-003", "Alle kommuner skal ha Rask psykisk helsehjelp.",
     ["Av kommunene som svarte, hadde 27 prosent etablert eget "
      "RPH-tilbud; tilbudet kan etableres der kapasitet finnes."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-004", "Du ma meldes fra Folkeregisteret for a fa bostotte.",
     ["Manglende flyttemelding til Folkeregisteret er ikke et krav; "
      "det er en vanlig avslagsarsak, men ikke obligatorisk."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-005", "Elever under 18 aar kan fa helsehjelp pa skolen.",
     ["Elever under 18 aar har ikke rett til a samtykke alene til "
      "helsehjelp utenom unntakene i pasient- og brukerrettighetsloven."],
     "RELATED_BUT_INSUFFICIENT", {"modality": "SOURCE_WEAKER_THAN_CLAIM",
                                  "polarity": "EXACT_MATCH"},
     "modality_strength")

case("BA-006", "Foreldre kan ta kontakt med helsestasjonen for ungdom.",
     ["Helsestasjon for ungdom er drop-in; ingen foreldretillatelse "
      "kreves for a kontakte."],
     "ENTAILS", {"modality": "SOURCE_STRONGER_THAN_CLAIM"},
     "modality_strength")

case("BA-007", "Alle ungdomsskoler har faste drop-in-tider.",
     ["Mange kommuner har faste drop-in-tider; enkelte har digital "
      "kontakt."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-008", "Skolehelsetjenesten skal ha helsesykepleier og lege.",
     ["Tjenesten skal ha helsesykepleier og lege som hovedregel; "
      "bemanningen folger forskriften."],
     "ENTAILS", {"modality": "EXACT_MATCH"}, "modality_strength")

case("BA-009", "Elever har rett til psykolog i skolehelsetjenesten.",
     ["Psykolog i skolehelsetjenesten kan vre med der kommunene "
      "organiserer det."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength",
     critical=True)

case("BA-010", "Skolelegen kan evaluere foreskrevne legemidler i noen "
     "kommuner.",
     ["Skolelegen kan i noen kommuner evaluere foreskrevne legemidler; "
      "det er lokal praksis."],
     "ENTAILS", {"modality": "EXACT_MATCH"}, "modality_strength")

case("BA-011", "Du har rett til utvidet barnetrygd nar du bor alene med "
     "barnet.",
     ["For a fa utvidet barnetrygd ma du vre alene med barn, det vil "
      "si ugift, ikke samboer og ikke leve sammen med den andre "
      "forelderen."],
     "ENTAILS", {"modality": "EXACT_MATCH",
                 "condition": "EXACT_MATCH"}, "modality_strength")

case("BA-012", "Delt ordinær barnetrygd er 1 006 kroner i maneden per "
     "forelder.",
     ["Ved delt fast bosted deles ordinær barnetrygd likt: "
      "1 006 kroner per forelder i maneden."],
     "ENTAILS", {"modality": "NOT_APPLICABLE",
                 "numeric_quantity": "NUMERIC_COMPATIBLE"},
     "modality_strength")

case("BA-013", "Ungdom under 20 aar kan bruke helsestasjonen for ungdom.",
     ["Alle kommuner skal ha et gratis HFU-tilbud for ungdom opptil "
      "20 aar."],
     "ENTAILS", {"modality": "SOURCE_STRONGER_THAN_CLAIM"},
     "modality_strength")

case("BA-014", "Barns inntekt er forbudt a regne med i bostottegrunnlaget.",
     ["Barns inntekt og formue er ikke med i inntektsgrunnlaget."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-015", "Barnebidrag er ikke med i bostottens inntektsgrunnlag.",
     ["Barnebidrag er ikke oppfort blant inntekter som telles med."],
     "ENTAILS", {"polarity": "EXACT_MATCH",
                 "modality": "NOT_APPLICABLE"}, "modality_strength")

case("BA-016", "Foreldre kan kontaktes av skolehelsetjenesten.",
     ["Foreldre kan ta kontakt pa vegne av barnet."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-017", "Elever kan dele helseting med læreren via helsesykepleieren.",
     ["Helsesykepleieren kan ikke dele elevens helseting med "
      "kontaktlæreren uten samtykke."],
     "CONTRADICTS", {"modality": "DEONTIC_OPPOSITION",
                     "polarity": "EXPLICIT_CONFLICT"},
     "modality_strength", critical=True)

case("BA-018", "Du kan fa utvidet barnetrygd i tillegg til ordinær.",
     ["Utvidet barnetrygd kommer i tillegg til den ordinære delte "
      "barnetrygden hvis utvidet vilkar er oppfylt for akkurat den "
      "forelderen."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM",
      "condition": "CONDITION_MISSING"}, "modality_strength")

case("BA-019", "Kommunen skal ha psykolog i alle skolehelsetjenester.",
     ["Psykolog kan vre med i skolehelsetjenesten; fysioterapeut bor "
      "vare med."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-020", "Begge foreldre ma sokke for at delingen skal skje.",
     ["Begge foreldre ma sokke for at barnetrygden skal deles."],
     "ENTAILS", {"modality": "EXACT_MATCH"}, "modality_strength")

case("BA-021", "Bokollektiv skal godkjennes for bostotte.",
     ["Bokollektiv er som hovedregel nei, med unntak av helsemessige "
      "eller sosiale grunner."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-022", "Helsestasjonen for ungdom finnes i alle kommuner opp "
     "til 25 aar.",
     ["Alle kommuner skal ha et HFU-tilbud for ungdom opptil 20 aar; "
      "noen kommuner har tilbud opp til 25 aar."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_STRONGER_THAN_CLAIM",
      "scope": "SCOPE_CONFLICT"}, "modality_strength", critical=True)

case("BA-023", "Samtykke kan ikke trekkes tilbake.",
     ["Samtykke kan trekkes tilbake."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "modality_strength", critical=True)

case("BA-024", "Skolehelsetjenesten skal stille diagnoser.",
     ["Skolehelsetjenesten stiller normalt ikke diagnoser og er ikke "
      "et behandlingstilbud for psykiske lidelser."],
     "CONTRADICTS", {"modality": "DEONTIC_OPPOSITION",
                     "polarity": "EXPLICIT_CONFLICT"},
     "modality_strength", critical=True)

case("BA-025", "Noen kommuner har egne tilleggstilbud til gutter i HFU.",
     ["Enkelte HFU-er har egne tilleggstilbud til gutter."],
     "ENTAILS", {"modality": "EXACT_MATCH"}, "modality_strength")

case("BA-026", "Barnet kan fores pa den andre forelderens bostottesoknad "
     "ved delt fast bosted.",
     ["Husbanken godtar at begge foreldre forer barn med delt fast "
      "bosted pa sin bostottesoknad."],
     "ENTAILS", {"modality": "SOURCE_STRONGER_THAN_CLAIM",
                 "actor": "SAME_ACTOR"}, "modality_strength")

case("BA-027", "Du ma ta kontakt med skolehelsetjenesten selv.",
     ["Eleven kan i prinsippet mote pa drop-in uten time; læreren kan "
      "hjelpe med a ta kontakt."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

case("BA-028", "Foreldre kan henvise barnet til BUP direkte.",
     ["Henvisning til BUP skjer fra fastlege, psykolog i kommunen "
      "eller barnevernsleder."],
     "RELATED_BUT_INSUFFICIENT", {"actor": "DIFFERENT_ACTOR"},
     "modality_strength", critical=True)

case("BA-029", "Delt utvidet barnetrygd er 1 286 kroner i maneden.",
     ["Delt utvidet barnetrygd er 1 286 kroner i maneden."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "modality_strength")

case("BA-030", "Kommunen skal dekke alle utgifter til RPH.",
     ["RPH-tilbudet kan etableres av kommunen; finansiering beskrives "
      "ikke i tilbudet."],
     "RELATED_BUT_INSUFFICIENT",
     {"modality": "SOURCE_WEAKER_THAN_CLAIM"}, "modality_strength")

# --- condition_exception: 20 cases ----------------------------------
KB = "54-delt-barnetrygd-ordinar-og-utvidet.md"

case("BA-031", "Du far utvidet barnetrygd delt mellom foreldrene.",
     ["For delt utvidet barnetrygd kreves skriftlig avtale om delt "
      "fast bosted for barn under 18 aar."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_exception")

case("BA-032", "Delt barnetrygd krever skriftlig avtale om delt fast "
     "bosted.",
     ["De har en skriftlig avtale om delt fast bosted som begge har "
      "signert, og da deles barnetrygden."],
     "ENTAILS", {"condition": "EXACT_MATCH"}, "condition_exception")

case("BA-033", "Foreldrene bor ikke sammen og har signert avtale om "
     "delt fast bosted; barnetrygden deles.",
     ["NAV deler barnetrygd nar foreldrene ikke bor sammen, barnet "
      "bor fast hos begge, og de har en signert skriftlig avtale om "
      "delt fast bosted."],
     "ENTAILS", {"condition": "EXACT_MATCH"}, "condition_exception")

case("BA-034", "Bostottesoknaden kan sendes elektronisk.",
     ["Elektronisk soknad er mulig bare via Husbankens eSoknad."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_exception")

case("BA-035", "Bare kommunen kan fatte bostottevedtak.",
     ["Husbanken eier system, regler og utbetaling; kommunen fatter "
      "vedtak som bostottekontor."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_exception")

case("BA-036", "Utvidet barnetrygd deles nar barnet bor hos mor.",
     ["Utvidet barnetrygd deles hvis du mottar full utvidet fra for, "
      "og barnet bor fast hos begge foreldre."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "RELEVANT_BUT_UNRESOLVED"}, "condition_exception")

case("BA-037", "Bostotte krever folkeregistrert adresse i boligen.",
     ["Folkeregistrert adresse er et praktisk vilkar, men manglende "
      "flyttemelding er unntaksvis ikke en avslagsarsak."],
     "RELATED_BUT_INSUFFICIENT",
     {"exception": "EXCEPTION_CONFLICT"}, "condition_exception")

case("BA-038", "Unntak fra bostotte-vilkaret gjelder under 18 aar med "
     "barn.",
     ["Under 18 aar med barn er unntaket fra aldersvilkaret pa 18 aar."],
     "ENTAILS", {"exception": "EXACT_MATCH"}, "condition_exception")

case("BA-039", "Skolehelsetjenesten deler aldri opplysninger med skolen.",
     ["Helsesykepleieren kan ikke dele helseting uten samtykke, men "
      "unntak gjelder ved fare for liv eller alvorlig helse."],
     "RELATED_BUT_INSUFFICIENT",
     {"exception": "EXCEPTION_CONFLICT",
      "polarity": "PARTIAL_OVERLAP"}, "condition_exception",
     critical=True)

case("BA-040", "Soknadsfristen er den 25. i maneden.",
     ["Soknadsfrist: den 25. i maneden for folgende maneds stonad."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"},
     "condition_exception")

case("BA-041", "Du faar meklingsattest automatisk ved samlivsbrudd.",
     ["Ved samlivsbrudd mellom samboere med felles barn under 16 aar "
      "kreves normalt meklingsattest."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_exception")

case("BA-042", "Ved felles barn over 16 aar brukes erklaring om "
     "samlivsbrudd.",
     ["Ved felles barn over 16 aar brukes erklaring om samlivsbrudd "
      "for delt utvidet barnetrygd."],
     "ENTAILS", {"condition": "EXACT_MATCH"}, "condition_exception")

case("BA-043", "Bokollektiv gir ikke bostotte.",
     ["Bokollektiv er som hovedregel nei, unntak for kollektiv av "
      "helsemessige eller sosiale grunner."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING",
      "exception": "EXCEPTION_CONFLICT"}, "condition_exception")

case("BA-044", "Barnetrygd og barnebidrag telles ikke med i "
     "inntektsgrunnlaget.",
     ["Barnetrygd og barnebidrag er ikke med i bostottens "
      "inntektsgrunnlag."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "condition_exception")

case("BA-045", "Ordinær barnetrygd deles likt og utvidet deles likt.",
     ["Ordinær barnetrygd deles likt ved delt fast bosted; utvidet "
      "barnetrygd deles bare hvis du mottar full utvidet fra for."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "condition_exception")

case("BA-046", "Full ordinær barnetrygd er 2 012 kroner og delt sats er "
     "1 006 kroner.",
     ["Full sats for ordinær barnetrygd er 2 012 kroner; delt sats er "
      "1 006 kroner per forelder."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "condition_exception")

case("BA-047", "Utbetaling skjer den 20. og soknadsfristen er den 25.",
     ["Vedtak og utbetaling: den 20. i maneden etter soknadsmaneden. "
      "Soknadsfrist: den 25. i maneden."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"},
     "condition_exception")

case("BA-048", "Bostotte beregnes ut fra boutgifter og inntekt.",
     ["Bostotte beregnes maned for maned ut fra faktiske boutgifter "
      "og husstandens inntekt i soknadsmåneden."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "condition_exception")

case("BA-049", "Unntaksreglene for bostotte avhenger av kommunen.",
     ["Unntak vurderes av kommunen som bostottekontor."],
     "ENTAILS", {"condition": "EXACT_MATCH"}, "condition_exception")

case("BA-050", "Det finnes ikke unntak fra taushetsplikten.",
     ["Taushetsplikten gjelder, men unntak gjelder ved fare for a "
      "skade seg selv eller andre."],
     "CONTRADICTS", {"exception": "EXCEPTION_CONFLICT",
                     "polarity": "EXPLICIT_CONFLICT"},
     "condition_exception", critical=True)

DOC = {
    "suite": "fresh-architecture-cases-v1",
    "part": "A",
    "frozen": False,
    "note": "Fresh dimension-annotated architecture suite, part A. "
            "Authored 2026-09-07 from existing KB files; no burned "
            "case shapes or IDs reused.",
    "cases": CASES,
}

with open(OUT, "w") as f:
    json.dump(DOC, f, ensure_ascii=False, indent=1)
print("wrote", OUT, len(CASES), "cases")
