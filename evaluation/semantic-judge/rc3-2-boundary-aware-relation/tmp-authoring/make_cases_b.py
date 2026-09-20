"""Author fresh architecture suite part B (actor/scope, negation,
temporal/numeric, compound buckets)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases_b.json")

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


# --- actor_scope: 20 cases ------------------------------------------
KB = "31-skolehelsetjenesten-i-dybden.md"

case("BA-051", "Helsesykepleier og lege jobber i skolehelsetjenesten.",
     ["Tjenesten skal ha helsesykepleier og lege."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "actor_scope")

case("BA-052", "Kommunens bostottekontor fatter vedtak om bostotte.",
     ["Kommunen (eller bydelen i Oslo) er bostottekontor og fatter "
      "vedtak."],
     "ENTAILS", {"actor": "LICENSED_ACTOR_EQUIVALENCE"}, "actor_scope")

case("BA-053", "Pasienten kan henvise seg selv til BUP.",
     ["Henvisning til BUP skjer fra fastlege, psykolog i kommunen "
      "eller barnevernsleder."],
     "RELATED_BUT_INSUFFICIENT", {"actor": "DIFFERENT_ACTOR"},
     "actor_scope")

case("BA-054", "Barn under 16 ar samtykker selv til all helsehjelp.",
     ["Foreldre samtykker pa vegne av barn under 16 ar, med unntak "
      "i pasient- og brukerrettighetsloven."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "DIFFERENT_ACTOR"}, "actor_scope", critical=True)

case("BA-055", "Voksne over 20 ar kan bruke helsestasjonen for ungdom.",
     ["Helsestasjon for ungdom gjelder ungdom opptil 20 ar."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "DIFFERENT_ACTOR"}, "actor_scope")

case("BA-056", "Foreldre kan ta kontakt pa vegne av barnet.",
     ["Foreldre kan ogsa ta kontakt pa vegne av barnet."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "actor_scope")

case("BA-057", "Skolehelsetjenesten er gratis for elevene.",
     ["Kommunen dekker alle utgifter, gratis for brukerne."],
     "ENTAILS", {"actor": "SAME_ACTOR", "polarity": "EXACT_MATCH"},
     "actor_scope")

case("BA-058", "Bostottekontoret er Husbanken.",
     ["Kommunen er bostottekontor; Husbanken eier system, regler og "
      "utbetaling."],
     "CONTRADICTS", {"actor": "DIFFERENT_ACTOR",
                     "polarity": "EXPLICIT_CONFLICT"}, "actor_scope")

case("BA-059", "Alle kommuner har et eget familieteam for helse.",
     ["Flere kommuner bruker navn som familieteam; dette er ikke "
      "standardiserte nasjonale navn."],
     "RELATED_BUT_INSUFFICIENT", {"scope": "SCOPE_CONFLICT"},
     "actor_scope")

case("BA-060", "PHFS finnes i alle kommuner.",
     ["PHFS finnes i Lillestrom som et lokalt tilbud."],
     "RELATED_BUT_INSUFFICIENT", {"scope": "SCOPE_CONFLICT"},
     "actor_scope")

case("BA-061", "HFU gjelder opptil 25 ar i alle kommuner.",
     ["Alle kommuner skal ha HFU-tilbud for ungdom opptil 20 ar; "
      "noen kommuner utvider til 25 ar."],
     "RELATED_BUT_INSUFFICIENT",
     {"scope": "SCOPE_CONFLICT"}, "actor_scope", critical=True)

case("BA-062", "Helsestasjonstjenesten gjelder barn og ungdom 0-20 ar.",
     ["Helsestasjonstjeneste for 0-20 ar reguleres av forskriften."],
     "ENTAILS", {"scope": "SCOPE_COMPATIBLE"}, "actor_scope")

case("BA-063", "Drop-in finnes ved alle skoler.",
     ["Mange kommuner har faste drop-in-tider."],
     "RELATED_BUT_INSUFFICIENT", {"scope": "SCOPE_CONFLICT"},
     "actor_scope")

case("BA-064", "Helsesykepleieren deler ikke opplysninger med "
     "kontaktlæreren uten samtykke.",
     ["Helsesykepleieren kan ikke dele elevens helseting med "
      "kontaktlæreren uten samtykke."],
     "ENTAILS", {"actor": "SAME_ACTOR",
                 "polarity": "EXACT_MATCH"}, "actor_scope")

case("BA-065", "Skolen bestemmer hva helsesykepleieren kan dele om "
     "elever.",
     ["Skolens ansatte er ikke helsepersonell; samtykke kreves for "
      "a dele helseopplysninger."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "DIFFERENT_ACTOR"}, "actor_scope")

case("BA-066", "Ungdom kan møte pa drop-in uten time.",
     ["Eleven kan i prinsippet mote pa drop-in eller apen dor uten "
      "time."],
     "ENTAILS", {"actor": "SAME_ACTOR",
                 "scope": "SCOPE_COMPATIBLE"}, "actor_scope")

case("BA-067", "Kun foresatte kan bestille helsesamtale.",
     ["Faste punkter per trinn inkluderer helsesamtale i 8. trinn; "
      "eleven kan selv ta kontakt."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "DIFFERENT_ACTOR"}, "actor_scope")

case("BA-068", "Fastlegen kan henvise til BUP.",
     ["Fastlegen kan henvise til kommunalt tilbud, privat "
      "spesialist og BUP."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "actor_scope")

case("BA-069", "Barnevernslederen skriver sykemelding.",
     ["Fastlegen er dorapner for helsehjelp og vurderer sykemelding."],
     "RELATED_BUT_INSUFFICIENT",
     {"actor": "DIFFERENT_ACTOR"}, "actor_scope")

case("BA-070", "Elever pa videregaende har vaksinetilbud til og med "
     "20 ar.",
     ["Videregaende skole: vaksineprogram til og med 20 ar."],
     "ENTAILS", {"actor": "SAME_ACTOR",
                 "scope": "SCOPE_COMPATIBLE"}, "actor_scope")

# --- negation_polarity: 20 cases ------------------------------------
KB = "55-bostotte-i-dybden.md"

case("BA-071", "Barns inntekt og formue telles med i "
     "bostottevurderingen.",
     ["Inntekt foer skatt for soeker og alle i husstanden over 20 ar "
      "telles med. Barns inntekt og formue er ikke med."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-072", "Barnetrygd og barnebidrag er ikke med i "
     "inntektsgrunnlaget.",
     ["Barnetrygd og barnebidrag er ikke med i inntekten."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-073", "Kontantstotte reduserer bostotten.",
     ["Kontantstotte er ikke med i inntektsgrunnlaget."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-074", "Foreldrenes inntekt telles med i grunnlaget.",
     ["Barns inntekt er ikke med. Inntekt for soeker og husstanden "
      "over 20 ar telles med."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-075", "Bostotte fortsetter automatisk etter flytting.",
     ["Bostotte fortsetter ikke automatisk; ved flytting ma du "
      "sende inn ny soknad."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-076", "Det finnes ingen nasjonal RPH-telefon.",
     ["Det finnes ingen nasjonal RPH-telefon; tilgangen er lokal."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-077", "Etter tre avslag far du bostotte automatisk videre.",
     ["Etter tre avslag ma du sokke pa nytt."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-078", "Alle kommuner har etablert RPH-tilbud.",
     ["59 prosent svarte at de ikke har RPH."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity")

case("BA-079", "Samtykke kan trekkes tilbake.",
     ["Samtykke kan trekkes tilbake."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-080", "Overgangsstonad teller ikke med i "
     "inntektsgrunnlaget.",
     ["Overgangsstonad er trygd og regnes med i "
      "inntektsgrunnlaget."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-081", "Utleieinntekt fra rom i egen bolig er skattefri og "
     "utover det utenfor grunnlaget.",
     ["Skattefri utleieinntekt, for eksempel rom i egen bolig, "
      "regnes som inntekt."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT",
                     "condition": "CONDITION_MISSING"},
     "negation_polarity", critical=True)

case("BA-082", "Du ma melde fra om endringer i boutgifter.",
     ["Du ma melde fra om endringer, blant annet boutgifter."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-083", "Bostotte beregnes ut fra boutgifter og inntekt.",
     ["Bostotte beregnes maned for maned ut fra faktiske "
      "boutgifter og husstandens inntekt."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-084", "Bostotte gir bothjelp og startlan samtidig.",
     ["Bostotte er en stotteordning for lave inntekter; startlan "
      "har egne vilkar."],
     "RELATED_BUT_INSUFFICIENT",
     {"polarity": "RELEVANT_BUT_UNRESOLVED"}, "negation_polarity")

case("BA-085", "Kommunen kan kreve dokumentasjon uten at du far "
     "epost.",
     ["Kommunen sjekker opplysninger og dokumentasjon; det kan "
      "kreve tilleggsdokumentasjon uten varsel."],
     "AMBIGUOUS", {"polarity": "RELEVANT_BUT_UNRESOLVED"},
     "negation_polarity")

case("BA-086", "Sosialhjelp og skattepenger er ikke med i inntekten.",
     ["Sosialhjelp og skattepenger er ikke med."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-087", "AAP og dagpenger utbetales hver maaned.",
     ["AAP og dagpenger utbetales hver 14. dag."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT",
                     "temporal": "TEMPORAL_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-088", "Skolehelsetjenesten yter psykoterapi.",
     ["Skolehelsetjenesten yter ikke psykoterapi."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT"},
     "negation_polarity", critical=True)

case("BA-089", "Læreren kan hjelpe eleven med a ta kontakt med "
     "skolehelsen.",
     ["Læreren kan hjelpe med a ta kontakt."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

case("BA-090", "Barnebidrag og barnetrygd reduserer ikke bostotten "
     "direkte.",
     ["Barnebidrag og delt barnetrygd oker husstandsinntekten men "
      "reduserer ikke bostotten direkte."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "negation_polarity")

# --- temporal_numeric_locality: 17 cases ----------------------------

case("BA-091", "Utbetalingen skjer den 20. i maneden etter "
     "soknadsmaneden.",
     ["Vedtak og utbetaling: den 20. i maneden etter "
      "soknadsmaneden."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-092", "Utbetalingen skjer den 18. i maneden etter "
     "soknadsmaneden.",
     ["Utbetaling sto oppgitt til 18. september."],
     "RELATED_BUT_INSUFFICIENT",
     {"temporal": "RELEVANT_BUT_UNRESOLVED"},
     "temporal_numeric_locality")

case("BA-093", "Oppvarmingstillegget er 613 kroner i maneden.",
     ["Det er 613 kroner i maneden til oppvarming hvis oppvarming "
      "ikke er dekket av leien."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE",
                 "condition": "EXACT_MATCH"},
     "temporal_numeric_locality")

case("BA-094", "Minsteutbetalingen av bostotte er 613 kroner.",
     ["Minsteutbetaling er 61 kroner per maned."],
     "CONTRADICTS", {"numeric_quantity": "NUMERIC_CONFLICT"},
     "temporal_numeric_locality", critical=True)

case("BA-095", "Fribelopet for kapitalinntekt er 6 672 kroner i "
     "maneden.",
     ["Fribelop 6 672 kroner per ar per person."],
     "CONTRADICTS", {"numeric_quantity": "NUMERIC_CONFLICT",
                     "temporal": "TEMPORAL_CONFLICT"},
     "temporal_numeric_locality", critical=True)

case("BA-096", "Full sats ordinær barnetrygd er 2 012 kroner.",
     ["Full sats for ordinær barnetrygd er 2 012 kroner i maneden."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-097", "Delt sats ordinær barnetrygd er 2 012 kroner per "
     "forelder.",
     ["Delt sats er 1 006 kroner per forelder."],
     "CONTRADICTS", {"numeric_quantity": "NUMERIC_CONFLICT"},
     "temporal_numeric_locality", critical=True)

case("BA-098", "En forelder med delt ordinær og delt utvidet far 2 292 "
     "kroner totalt.",
     ["1 006 + 1 286 = 2 292 kroner i maneden hvis begge deler er "
      "innvilget."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-099", "Inntektsgrensen er 28 241 kroner i alle kommuner.",
     ["Eksempel verifisert: 28 241 kroner i maneden for en "
      "1-persons leietakerhusstand i valgt kommune; grensen "
      "varierer mellom kommuner."],
     "RELATED_BUT_INSUFFICIENT",
     {"scope": "SCOPE_CONFLICT"}, "temporal_numeric_locality",
     critical=True)

case("BA-100", "27 prosent av kommunene hadde eget RPH-tilbud i 2024.",
     ["27 prosent, 94 kommuner og bydeler, hadde etablert eget "
      "RPH-tilbud i 2024."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-101", "RPH-arsverkene okte fra 2023 til 2024.",
     ["368 RPH-arsverk ble rapportert i 2024, en nedgang pa 15 fra "
      "2023."],
     "CONTRADICTS", {"polarity": "EXPLICIT_CONFLICT",
                     "numeric_quantity": "NUMERIC_CONFLICT"},
     "temporal_numeric_locality")

case("BA-102", "Formuestillegget fordeles over 12 maneder.",
     ["65 prosent av overskytende formue legges til inntekten som "
      "formuestillegg, fordelt pa 12 maneder."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE",
                 "temporal": "TEMPORAL_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-103", "Netto formue pa 350 000 kroner gir omtrent 890 kroner "
     "ekstra i maneden.",
     ["Eksempel: netto formue 350 000 kroner i leid bolig gir "
      "tillegg pa omtrent 890 kroner i maneden."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-104", "Klagefristen er tre uker.",
     ["Klage: frist tre uker fra du mottok vedtaket."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"},
     "temporal_numeric_locality")

case("BA-105", "Avslag viderefores automatisk i inntil seks maneder.",
     ["Avslag viderefores automatisk i inntil tre maneder."],
     "CONTRADICTS", {"temporal": "TEMPORAL_CONFLICT",
                     "numeric_quantity": "NUMERIC_CONFLICT"},
     "temporal_numeric_locality", critical=True)

case("BA-106", "Husleie for leiebolig telles som boutgift.",
     ["For leiebolig er det husleie pluss 613 kroner i maneden til "
      "oppvarming."],
     "ENTAILS", {"numeric_quantity": "NOT_APPLICABLE",
                 "polarity": "EXACT_MATCH"},
     "temporal_numeric_locality")

case("BA-107", "Smabarnstillegget er 712 kroner ved full "
     "overgangsstønad.",
     ["Smabarnstillegg 712 kroner i maneden ved full "
      "overgangsstønad for barn 0 til 3 ar."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "temporal_numeric_locality")

# --- compound: 20 cases (multi-atom) ---------------------------------

case("BA-108", "Bostotte utbetales den 20. i maneden etter "
     "soknadsmaneden, og soknadsfristen er den 25. i maneden.",
     ["Utbetaling skjer den 20. i maneden etter soknadsmaneden.",
      "Soknadsfrist er den 25. i maneden."],
     "ENTAILS", {"temporal": "TEMPORAL_COMPATIBLE"},
     "compound", compound=True,
     expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-109", "Delt ordinær barnetrygd er 1 006 kroner, og delt "
     "utvidet er 1 286 kroner.",
     ["Delt sats ordinær barnetrygd er 1 006 kroner per forelder.",
      "Delt utvidet barnetrygd er 1 286 kroner i maneden."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE"},
     "compound", compound=True,
     expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-110", "Full ordinær barnetrygd er 2 012 kroner, og delt sats "
     "er 2 012 kroner.",
     ["Full sats er 2 012 kroner i maneden.",
      "Delt sats er 1 006 kroner per forelder."],
     "PARTIAL", {"numeric_quantity": "NUMERIC_CONFLICT"},
     "compound", compound=True,
     expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-111", "Barnetrygd telles ikke med i grunnlaget, og "
     "barnebidrag telles ikke med.",
     ["Barnetrygd og barnebidrag er ikke med i inntekten."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-112", "Utbetalingen skjer den 20., og klagefristen er tre "
     "maneder.",
     ["Utbetaling skjer den 20. i maneden etter soknadsmaneden.",
      "Klage: frist tre uker fra du mottok vedtaket."],
     "PARTIAL", {"temporal": "TEMPORAL_CONFLICT"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-113", "Helsesykepleier jobber i skolehelsetjenesten, og "
     "tjenesten er gratis.",
     ["Tjenesten skal ha helsesykepleier og lege.",
      "Kommunen dekker alle utgifter, gratis for brukerne."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-114", "Eleven kan mote pa drop-in, og foreldre kan ta "
     "kontakt pa vegne av barnet.",
     ["Eleven kan i prinsippet mote pa drop-in uten time.",
      "Foreldre kan ogsa ta kontakt pa vegne av barnet."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-115", "HFU gjelder opptil 20 ar, og alle kommuner har "
     "tilbud opp til 25 ar.",
     ["Alle kommuner skal ha HFU-tilbud opptil 20 ar.",
      "Noen kommuner har tilbud opp til 25 ar."],
     "PARTIAL", {"scope": "SCOPE_CONFLICT"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-116", "Du ma melde fra om flytting, og ny soknad kreves ved "
     "flytting.",
     ["Ved flytting ma du sende inn ny soknad."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-117", "RPH er for personer over 16 ar, og alle kommuner har "
     "RPH.",
     ["RPH er for innbyggere over 16 ar.",
      "59 prosent svarte at de ikke har RPH."],
     "PARTIAL", {"polarity": "EXPLICIT_CONFLICT"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-118", "Bostotte beregnes ut fra boutgifter og husstandens "
     "inntekt.",
     ["Bostotte beregnes maned for maned ut fra faktiske "
      "boutgifter og husstandens inntekt."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=False)

case("BA-119", "Skolehelsetjenesten skal ha helsesykepleier, og "
     "kommunen skal tilby tjenesten til 0-20 ar.",
     ["Tjenesten skal ha helsesykepleier og lege.",
      "Kommunen skal tilby helsestasjons- og skolehelsetjeneste til "
      "0-20 ar."],
     "ENTAILS", {"modality": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-120", "Skolehelsetjenesten stiller diagnoser, og eleven kan "
     "fa helsesamtale.",
     ["Skolehelsetjenesten stiller normalt ikke diagnoser.",
      "Helsesamtale er et fast tilbud i 8. trinn."],
     "PARTIAL", {"polarity": "EXPLICIT_CONFLICT"}, "compound",
     compound=True, expected_atoms=["CONTRADICTS", "ENTAILS"])

case("BA-121", "Samtykke kan trekkes tilbake, og foreldre samtykker "
     "for barn under 16 ar.",
     ["Samtykke kan trekkes tilbake.",
      "Foreldre samtykker pa vegne av barn under 16 ar."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-122", "Bokollektiv gir som hovedregel ikke bostotte, og "
     "studenter folger egne regler.",
     ["Bokollektiv er som hovedregel nei, unntak av helsemessige "
      "eller sosiale grunner.",
      "Studenter, elever og larlinger folger egne regler."],
     "RELATED_BUT_INSUFFICIENT",
     {"condition": "CONDITION_MISSING"}, "compound",
     compound=True,
     expected_atoms=["RELATED_BUT_INSUFFICIENT",
                     "RELATED_BUT_INSUFFICIENT"])

case("BA-123", "Minsteutbetaling er 61 kroner, og under det "
     "utbetales ingenting.",
     ["Minsteutbetaling er 61 kroner per maned; under det "
      "utbetales ingenting."],
     "ENTAILS", {"numeric_quantity": "NUMERIC_COMPATIBLE",
                 "polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-124", "Inntekt over 20 ar telles med, og barns inntekt "
     "telles med.",
     ["Inntekt for soeker og husstanden over 20 ar telles med.",
      "Barns inntekt og formue er ikke med."],
     "PARTIAL", {"polarity": "EXPLICIT_CONFLICT"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "CONTRADICTS"])

case("BA-125", "Klage sendes kommunen, og Husbanken fatter nytt "
     "vedtak.",
     ["Klagen sendes kommunen, som kompletterer og sender til "
      "Husbanken.",
      "Husbanken fatter nytt vedtak."],
     "ENTAILS", {"actor": "SAME_ACTOR"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-126", "Etterkontroll korrigerer inntekter automatisk, og du "
     "kan fa krav om tilbakebetaling.",
     ["Inntekter korrigeres automatisk nar arbeidsgiver retter "
      "opplysninger til Skatteetaten.",
      "Du kan fa utbetaling etterpa eller krav om tilbakebetaling."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

case("BA-127", "Utvidet barnetrygd deles likt, og Finnmarkstillegget "
     "deles i to.",
     ["Utvidet barnetrygd halveres hvis du mottar full utvidet fra "
      "for.",
      "Finnmark- og Svalbardtillegg deles i to ved delt "
      "barnetrygd."],
     "ENTAILS", {"polarity": "EXACT_MATCH"}, "compound",
     compound=True, expected_atoms=["ENTAILS", "ENTAILS"])

DOC = {
    "suite": "fresh-architecture-cases-v1",
    "part": "B",
    "frozen": False,
    "note": "Fresh dimension-annotated architecture suite, part B.",
    "cases": CASES,
}

with open(OUT, "w") as f:
    json.dump(DOC, f, ensure_ascii=False, indent=1)
print("wrote", OUT, len(CASES), "cases")
