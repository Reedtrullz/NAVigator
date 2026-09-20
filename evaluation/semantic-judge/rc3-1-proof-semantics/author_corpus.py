#!/usr/bin/env python3
"""Author the RC3.1 fresh proof-development corpus (180 cases).

Hand-authored from verified KB anchors (FACTS). Relations are truth
labels for corpus annotation only; the runtime never sees them. Split
is deterministic: sorted by case_id, first 120 -> TRAIN, last 60 ->
VALIDATION (sealed before implementation).
"""
import json
import random
import sys
from pathlib import Path

import corpus_tools as ct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # repo root (validation runs from here)
HOLDOUT = HERE.parent / "rc3-generalization-holdout"

FACTS = {
    "F1": ("25-kommunale-psykiske-tjenester-barn-unge.md", 23,
           "Ikke en ensartet tjeneste. Kommunepsykolog er et hverdagsnavn for psykologer ansatt i kommunal helse- og omsorgstjeneste (eller andre kommunale tjenester). Det finnes ingen nasjonal enhetlig ordning med felles navn, malgruppe, aldersgrenser."),
    "F2": ("25-kommunale-psykiske-tjenester-barn-unge.md", 26,
           "Antall psykologarsverk i kommunal helse- og omsorgstjeneste okte fra 244 (2015) til 531 (2022)."),
    "F3": ("25-kommunale-psykiske-tjenester-barn-unge.md", 27,
           "Ca. 6 av 10 kommuner hadde ansatt egen psykolog i 2022. Andelen faller med lavere sentralitet."),
    "F4": ("25-kommunale-psykiske-tjenester-barn-unge.md", 16,
           "Veilederen sier at kommunens psykiske helsetjeneste til barn og unge skal vaere et lavterskeltilbud: apent for alle barn og unge i kommunen og deres familier, uten henvisning, tilbys digitalt ved behov."),
    "F5": ("25-kommunale-psykiske-tjenester-barn-unge.md", 31,
           "Fastlegen, psykolog i kommunen og barnevernsleder har henvisningsrett til psykisk helsevern for barn og unge."),
    "F6": ("25-kommunale-psykiske-tjenester-barn-unge.md", 34,
           "Barum: Psykisk helse barn og unge med familie er et forebyggende lavterskeltilbud uten henvisning; Begge foreldre skal vaere orientert og samtykke til oppfolging. Personer over 16 er selv helserettslig myndig."),
    "F7": ("25-kommunale-psykiske-tjenester-barn-unge.md", 49,
           "Eksempler pa lokale navn (kommunespesifikke): PHFS i Lillestrom; Psykisk helse barn og unge med familie i Barum; Familieteam helse 0-20 ar i Snasa; Ung Arena i Oslo (moteplass/aktivitetstilbud, ikke terapitjeneste). Andre kommuner har andre navn."),
    "F8": ("25-kommunale-psykiske-tjenester-barn-unge.md", 58,
           "RPH er en kunnskapsbasert modell i den kommunale helsetjenesten for behandling av innbyggere over 16 ar med angst, mild til moderat depresjon, sovnvansker og/eller begynnende rusmiddelproblemer. RPH skal ikke gi tilbud til personer med alvorlige og sammensatte problemer."),
    "F9": ("25-kommunale-psykiske-tjenester-barn-unge.md", 75,
           "Alle kommuner skal ha et gratis HFU-tilbud for ungdom opptil 20 ar. Noen kommuner har tilbud opp til 25 ar."),
    "F10": ("25-kommunale-psykiske-tjenester-barn-unge.md", 109,
            "BUP/PHBU: spesialisthelsetjenesten; henvisning fra fastlege, psykolog i kommunen eller barnevernsleder."),
    "F11": ("28-ppt-i-dybden.md", 12,
            "PPTs oppgaver etter paragraf 11-13: (a) stotte og veilede skolene i a utrede behov for tilrettelegging og sette inn tiltak sa tidlig som mulig, (b) bidra til kompetanseutvikling."),
    "F12": ("28-ppt-i-dybden.md", 13,
            "PPT er sakkyndig instans i saker om spesialpedagogisk hjelp i barnehage."),
    "F13": ("28-ppt-i-dybden.md", 14,
            "PPT kan ikke erstattes ved a bare kjope tilsvarende tjeneste utenfra."),
    "F14": ("28-ppt-i-dybden.md", 46,
            "PPT stiller ikke diagnoser og er ikke behandlingstjeneste: Diagnoser stilles i spesialisthelsetjenesten (BUP/HABU) eller av lege. PPT kan bidra med pedagogisk utredning."),
    "F15": ("28-ppt-i-dybden.md", 101,
            "Statped: nasjonal stottefunksjon; PPT kan soke Statped om radgiving/veiledning/kartlegging. Statped retter seg mot det faglige laget rundt barnet, ikke direkte behandling av barnet."),
    "F16": ("28-ppt-i-dybden.md", 107,
            "Hvem kan soke Statped: PPT (samt u-hoyskoler, helseforetak, og foresatte via Statpeds kontaktform)."),
    "F17": ("28-ppt-i-dybden.md", 108,
            "Statped tilbyr: radgiving og veiledning, spesialpedagogisk kartlegging, kompetanseutvikling, kurs for foresatte."),
    "F18": ("31-skolehelsetjenesten-i-dybden.md", 13,
            "Forskrift paragraf 2 virkeomrade: helsetjeneste i grunnskoler og videregaende skoler; helsestasjonstjeneste for 0-20 ar."),
    "F19": ("31-skolehelsetjenesten-i-dybden.md", 14,
            "Paragraf 3: kommunen skal tilby helsestasjons- og skolehelsetjeneste til barn og ungdom 0-20 ar; kommunen dekker alle utgifter (gratis for brukerne)."),
    "F20": ("31-skolehelsetjenesten-i-dybden.md", 22,
            "Kan (forskrift paragraf 6): helsesamtaler, helseundersokelser, veiing/maling, vaksinering, drop-in, korttidsoppfolging og radgivning, henvisning videre ved behov."),
    "F21": ("31-skolehelsetjenesten-i-dybden.md", 24,
            "Kan ikke (ikke en behandlingstjeneste): Skolehelsetjenesten er ikke et behandlingstilbud for psykiske lidelser; den yter ikke psykoterapi, stiller normalt ikke diagnoser og skriver ikke ut legemidler (skolelegen kan i noen kommuner evaluere foreskrevne legemidler, lokal praksis)."),
    "F22": ("31-skolehelsetjenesten-i-dybden.md", 30,
            "Helsenorge: eleven kan i prinsippet mote pa drop-in/apen dor uten time; læreren kan hjelpe med a ta kontakt; foreldre kan ogsa ta kontakt pa vegne av barnet."),
    "F23": ("31-skolehelsetjenesten-i-dybden.md", 38,
            "Paragraf 4-3: beslutningskompetanse: 18+ (hovedregel); 16-18 ar har rett til a samtykke med mindre annet folger av saerlige bestemmelser; 12-16 ar kan samtykke til helsehjelp i forhold foreldrene ikke er informert om."),
    "F24": ("31-skolehelsetjenesten-i-dybden.md", 39,
            "Paragraf 4-4: foreldre samtykker pa vegne av barn under 16 ar; unntak for 12-16-aringer etter paragraf 4-3 c."),
    "F25": ("31-skolehelsetjenesten-i-dybden.md", 32,
            "Helsestasjon for ungdom (HFU): drop-in, ingen foreldretillatelse kreves."),
    "F26": ("55-bostotte-i-dybden.md", 13,
            "Alder: over 18 ar og ikke i forstegangstjenesten, eller under 18 ar med barn."),
    "F27": ("55-bostotte-i-dybden.md", 14,
            "Boligen ma vaere godkjent til boligformal og ha egen inngang, eget bad og toalett, kjokkenlosning og mulighet for hvile."),
    "F28": ("55-bostotte-i-dybden.md", 25,
            "Soknadsfrist: den 25. i maneden for folgende maneds stonad."),
    "F29": ("55-bostotte-i-dybden.md", 38,
            "Bostotten er godkjente boutgifter minus egenandel, begrenset av inntektsgrensen. Minsteutbetaling er 61 kroner per maned; under det utbetales ingenting."),
    "F30": ("55-bostotte-i-dybden.md", 24,
            "Behandler du okonomisk sosialhjelp til boutgifter, vil kommunen som regel kreve at du sokker bostotte forst."),
    "F31": ("49-samvaersfradrag-og-reisekostnader.md", 20,
            "Samvar pa MER enn 2 dager i gjennomsnitt per maned gir grunnlag for fradrag."),
    "F32": ("49-samvaersfradrag-og-reisekostnader.md", 22,
            "Samvaret ma FAKTISK gjennomfores. Avtalt men ikke gjennomfort samvar gir ikke fradrag."),
    "F33": ("49-samvaersfradrag-og-reisekostnader.md", 59,
            "Klasse 2-tabell: 0-5 dager: 1277; 6-10: 1690; 11-14: 2078; 15+: 2306."),
    "F34": ("54-delt-barnetrygd-ordinar-og-utvidet.md", 14,
            "Ordinar barnetrygd: full 2012 kr/mnd, delt 1006 kr/mnd."),
    "F35": ("54-delt-barnetrygd-ordinar-og-utvidet.md", 15,
            "Utvidet barnetrygd: full 2572 kr/mnd, delt 1286 kr/mnd."),
    "F36": ("54-delt-barnetrygd-ordinar-og-utvidet.md", 24,
            "En forelder med delt fast bosted og innvilget delt utvidet barnetrygd far 1006 + 1286 = 2292 kroner i maneden fra NAV, hvis begge deler er innvilget."),
    "F37": ("56-okonomisk-sosialhjelp-i-dybden.md", 12,
            "Paragraf 17: opplysning, rad og veiledning. Kommunen skal gi slik hjelp, og sa vidt mulig sorge for at andre gor det. Gjelder uavhengig av rett til okonomisk sosialhjelp."),
    "F38": ("56-okonomisk-sosialhjelp-i-dybden.md", 13,
            "Paragraf 18: stonad til livsopphold. De som ikke kan sorge for livsoppholdet gjennom arbeid eller ved a gjore gjeldende okonomiske rettigheter, har krav pa okonomisk stonad."),
    "F39": ("56-okonomisk-sosialhjelp-i-dybden.md", 14,
            "Paragraf 19: stonad i sarlige tilfeller. Kommunen KAN yte okonomisk hjelp selv om vilkarene i paragraf 18 ikke er til stede. Dette er skjonsbestemt, for eksempel okonomisk hjelp til gjeld i boligkrisesituasjoner."),
    "F40": ("56-okonomisk-sosialhjelp-i-dybden.md", 21,
            "Kvalifiseringsprogram: 18-67 ar, normalt inntil to ar. Kvalifiseringsstonad 2,041 G pa arsbasis."),
    "F41": ("56-okonomisk-sosialhjelp-i-dybden.md", 57,
            "BARNETRYGD skal IKKE med ved vurdering av stonad til familier etter paragraf 18 tredje ledd."),
    "F42": ("64-overgangsstonad-nye-regler-i-dybden.md", 39,
            "Arlig full stonad: 307 235 kr (2,25 G)."),
    "F43": ("64-overgangsstonad-nye-regler-i-dybden.md", 40,
            "Manedlig full stonad: 25 603 kr for skatt."),
    "F44": ("64-overgangsstonad-nye-regler-i-dybden.md", 10,
            "Ved fodselse kan det i tillegg ytes inntil 2 maneder for fodselen."),
    "F45": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", 12,
            "Mottakere som star i ordningen per 30. juni 2026 beholder de tidligere reglene, og NAV oppgir en overgangsfase med to parallelle regelverk frem til 30. juni 2031."),
    "F46": ("58-boligtrygghet-depositum-utkastelse.md", 10,
            "Egne midler pa vanlig depositumskonto. Utleier har rett til sikkerhet, men belopet er som utgangspunkt inntil seks maneders leie; kontant sikkerhet skal pa sperret konto."),
    "F47": ("58-boligtrygghet-depositum-utkastelse.md", 12,
            "Nav garanti for depositum: nar du inngar leiekontrakt og ikke kan skaffe penger selv, gir Nav-Kontoret vanligvis en garanti. Dette er paragraf 19-skjonn, ikke en automatisk rett til akkurat garanti."),
    "F48": ("30-skolefravar-og-skolevegring.md", 14,
            "Udir anbefaler skriftlig plan for oppfolging nar fravaeret er bekymringsfullt. Retningslinjen er veiledende, ikke lovfestet."),
    "F49": ("48-barnebidrag-i-dybden.md", 12,
            "Barnebidrag er en betaling fra den ene forelderen til den andre (eller til barnet selv etter fylte 18 ar)."),
    "F50": ("48-barnebidrag-i-dybden.md", 26,
            "Plikten til a betale barnebidrag varer normalt til og med den maneden barnet fyller 18 ar. Etter fylte 18 ar kan barnet ha rett til forsorgelse gjennom videregaende opplaring."),
    "F51": ("07-pensjon/README.md", 9,
            "Alderspensjon fra folketrygden, kan tas ut fra 62 ar."),
    "F52": ("07-pensjon/README.md", 10,
            "Minimum: 5 ars medlemskap, fullt minimum etter 40 ar."),
    "F53": ("03-arbeidsmarkedstjenester/README.md", 11,
            "Adgang: Alle kan registrere seg som jobbsoker."),
    "F54": ("42-vold-trusler-og-sikkerhet.md", 13,
            "Akutt fare: ring 112. Krisesenterlinjen: 116 006 (dognrundt). Politiet: 02800 (ikke-akutt)."),
    "F55": ("24-kildedokumentasjon-bup-og-habu.md", 56,
            "Behandlingsstedet som mottar henvisningen skal vurdere rett til helsehjelp innen 10 virkedager. Svaret skal inneholde vedtak om rett/ikke rett og bindende frist for oppstart."),
    "F56": ("24-kildedokumentasjon-bup-og-habu.md", 57,
            "Bindende frist er juridisk bindende og skal settes ut fra Helsedirektoratets prioriteringsveiledere (individuell vurdering; ikke styrt av kapasitet). Svar med rett til helsehjelp gir ogsa fritt behandlingsvalg."),
}


def E(cid, claim, rel, facts, shapes, atoms=None, critical=False):
    return {"cid": cid, "claim": claim, "rel": rel, "facts": facts,
            "shapes": shapes, "atoms": atoms, "critical": critical}


CASES = [
    E("RC31-0001", "Psykolog i kommunen er en ensartet nasjonal tjeneste med felles navn og malgruppe.", "CONTRADICTS", ["F1"], ["actor", "scope"], None, True),
    E("RC31-0002", "Alle kommuner hadde ansatt egen psykolog i 2022.", "CONTRADICTS", ["F3"], ["numeric", "scope"], None, True),
    E("RC31-0003", "Den kommunale psykiske helsetjenesten for barn og unge skal vaere et lavterskeltilbud.", "ENTAILS", ["F4"], ["modality", "scope"], None, False),
    E("RC31-0004", "Familier ma henvises av fastlegen for a fa hjelp fra det kommunale lavterskeltilbudet for barn og unge.", "CONTRADICTS", ["F4"], ["negation"], None, True),
    E("RC31-0005", "Psykolog i kommunen kan henvise til BUP.", "ENTAILS", ["F5"], ["modality", "actor"], None, False),
    E("RC31-0006", "Kun fastlegen kan henvise til BUP.", "CONTRADICTS", ["F5"], ["actor", "negation"], None, True),
    E("RC31-0007", "Rask psykisk helsehjelp gjelder innbyggere over 16 ar.", "ENTAILS", ["F8"], ["numeric"], None, False),
    E("RC31-0008", "Rask psykisk helsehjelp tar imot barn under 16 ar.", "CONTRADICTS", ["F8"], ["actor", "numeric"], None, True),
    E("RC31-0009", "Rask psykisk helsehjelp skal gi tilbud til personer med alvorlige og sammensatte problemer.", "CONTRADICTS", ["F8"], ["negation", "modality"], None, True),
    E("RC31-0010", "Alle kommuner skal ha et gratis HFU-tilbud for ungdom opptil 20 ar.", "ENTAILS", ["F9"], ["numeric", "modality"], None, False),
    E("RC31-0011", "HFU-tilbudet er gratis.", "ENTAILS", ["F9"], ["modality"], None, False),
    E("RC31-0012", "Ingen kommuner har HFU-tilbud for ungdom over 20 ar.", "CONTRADICTS", ["F9"], ["negation", "numeric"], None, True),
    E("RC31-0013", "Ung Arena i Oslo er en terapitjeneste for ungdom.", "CONTRADICTS", ["F7"], ["negation", "actor"], None, True),
    E("RC31-0014", "Lokale navn pa kommunale psykiske lavterskeltilbud varierer mellom kommunene.", "ENTAILS", ["F7"], ["scope"], None, False),
    E("RC31-0015", "HFU-tilbudet gjelder i alle kommuner ungdom opp til 25 ar.", "CONTRADICTS", ["F9"], ["numeric", "scope"], None, True),
    E("RC31-0016", "HFU-tilbudet er gratis, og alle kommuner har tilbud opp til 25 ar.",
      "PARTIAL", ["F9"],
      ["compound", "numeric"],
      [("A1", "HFU-tilbudet er gratis", ["S1"]), ("A2", "Alle kommuner har HFU-tilbud opp til 25 ar", ["S1"])], False),
    E("RC31-0017", "Kommunepsykologer ma ha godkjent spesialisering i klinisk psykologi.", "RELATED_BUT_INSUFFICIENT", ["F1"], ["modality", "actor"], None, False),
    E("RC31-0018", "Antallet psykologarsverk i kommunene har sunket siden 2015.", "CONTRADICTS", ["F2"], ["numeric", "negation"], None, True),
    E("RC31-0019", "Antall psykologarsverk i kommunal helse- og omsorgstjeneste okte fra 2015 til 2022.",
      "ENTAILS", ["F2"], ["numeric", "negation", "compound"],
      [("A1", "Antall psykologarsverk var 244 i 2015", ["S1"]), ("A2", "Antall psykologarsverk var 531 i 2022", ["S1"])], False),
    E("RC31-0020", "Ca. 6 av 10 kommuner hadde ansatt psykolog i 2021.", "RELATED_BUT_INSUFFICIENT", ["F3"], ["numeric", "temporal", "actor"], None, False),
    E("RC31-0021", "Bostotte sokkes hos Husbanken.", "UNRELATED", ["F1"], ["actor", "scope"], None, False),
    E("RC31-0022", "Kommunens psykiske helsetjeneste for barn og unge kan kreve henvisning fra fastlegen.", "AMBIGUOUS", ["F4"], ["modality", "actor"], None, False),
    E("RC31-0023", "PPT stiller diagnoser.", "CONTRADICTS", ["F14"], ["negation", "actor"], None, True),
    E("RC31-0024", "PPT er ikke en behandlingstjeneste.", "ENTAILS", ["F14"], ["negation"], None, False),
    E("RC31-0025", "Diagnoser stilles i spesialisthelsetjenesten eller av lege.", "ENTAILS", ["F14"], ["actor"], None, False),
    E("RC31-0026", "PPT skal utarbeide sakkyndig vurdering nar lova eller forskrift krever det.", "ENTAILS", ["F11"], ["modality", "actor"], None, False),
    E("RC31-0027", "PPT-tjenesten kan erstattes ved a kjope tilsvarende tjeneste utenfra.", "CONTRADICTS", ["F13"], ["modality", "negation"], None, True),
    E("RC31-0028", "Kommunen skal tilby helsestasjons- og skolehelsetjeneste til barn og ungdom 0-20 ar.", "ENTAILS", ["F19"], ["numeric", "modality", "actor"], None, False),
    E("RC31-0029", "Skolehelsetjenesten er gratis for brukerne.", "ENTAILS", ["F19"], ["numeric", "modality"], None, False),
    E("RC31-0030", "Skolehelsetjenesten yter psykoterapi til elever med depresjon.", "CONTRADICTS", ["F21"], ["negation", "modality"], None, True),
    E("RC31-0031", "Skolehelsetjenesten skriver ut legemidler.", "CONTRADICTS", ["F21"], ["negation"], None, True),
    E("RC31-0032", "Elever pa 14 ar kan samtykke til helsehjelp i forhold foreldrene ikke er informert om.", "ENTAILS", ["F23"], ["numeric", "actor", "modality"], None, False),
    E("RC31-0033", "Foreldre samtykker pa vegne av barn under 16 ar, med unntak for 12-16-aringer etter paragraf 4-3 c.",
      "ENTAILS", ["F24"], ["exception", "compound"],
      [("A1", "Foreldre samtykker pa vegne av barn under 16 ar", ["S1"]), ("A2", "12-16-aringer er et unntak etter paragraf 4-3 c", ["S1"])], False),
    E("RC31-0034", "Barn under 12 ar kan selv samtykke til all helsehjelp uten foreldres samtykke.", "CONTRADICTS", ["F24"], ["exception", "negation"], None, True),
    E("RC31-0035", "Eleven kan i prinsippet mote pa drop-in uten time.", "ENTAILS", ["F22"], ["modality", "actor"], None, False),
    E("RC31-0036", "Ingen kommuner har faste drop-in-tider for ungdomsskoleelever.", "CONTRADICTS", ["F22"], ["negation", "scope"], None, True),
    E("RC31-0037", "PPT kan soke Statped om radgiving og kartlegging.", "ENTAILS", ["F15"], ["modality"], None, False),
    E("RC31-0038", "Statped retter seg mot det faglige laget rundt barnet, ikke direkte behandling av barnet.", "ENTAILS", ["F15"], ["negation", "actor"], None, False),
    E("RC31-0039", "Du kan ha rett til bostotte hvis du er under 18 ar og har barn.", "ENTAILS", ["F26"], ["modality", "condition"], None, False),
    E("RC31-0040", "Alle over 18 ar far bostotte.", "CONTRADICTS", ["F26", "F27", "F29"], ["condition", "modality"], None, True),
    E("RC31-0041", "Boligen ma ha egen inngang og eget bad for a godkjennes til boligformal.", "ENTAILS", ["F27"], ["condition"], None, False),
    E("RC31-0042", "Boliger uten egen inngang kan godkjennes til boligformal for bostotte.", "CONTRADICTS", ["F27"], ["negation", "condition"], None, True),
    E("RC31-0043", "Soknadsfristen for bostotte er den 25. i maneden.", "ENTAILS", ["F28"], ["numeric"], None, False),
    E("RC31-0044", "Bostotte sokkes etter at maneden er utlopt.", "CONTRADICTS", ["F28"], ["numeric", "temporal"], None, True),
    E("RC31-0045", "Minsteutbetalingen av bostotte er 61 kroner per maned.", "ENTAILS", ["F29"], ["numeric"], None, False),
    E("RC31-0046", "Det utbetales alltid minst 100 kroner i bostotte per maned.", "CONTRADICTS", ["F29"], ["numeric"], None, True),
    E("RC31-0047", "Bostotte under 61 kroner per maned utbetales ikke.", "ENTAILS", ["F29"], ["negation", "numeric"], None, False),
    E("RC31-0048", "Kommunen kan kreve at du sokker bostotte forst nar du ber om sosialhjelp til boutgifter.", "ENTAILS", ["F30"], ["modality", "condition"], None, False),
    E("RC31-0049", "Bostotte utbetales alltid den 20. i maneden.", "RELATED_BUT_INSUFFICIENT", ["F28"], ["numeric", "temporal", "actor"], None, False),
    E("RC31-0050", "Bostotte er en rettighet for alle over 18 ar, og soknadsfristen er den 25. i maneden.",
      "PARTIAL", ["F26", "F28"],
      ["compound", "condition", "actor"],
      [("A1", "Bostotte er en rettighet for alle over 18 ar", ["S1"]), ("A2", "Soknadsfristen er den 25. i maneden", ["S2"])], True),
    E("RC31-0051", "Samvar pa mer enn 2 dager i gjennomsnitt per maned gir grunnlag for fradrag i barnebidrag.", "ENTAILS", ["F31"], ["numeric"], None, False),
    E("RC31-0052", "Samvar pa 2 dager i gjennomsnitt per maned gir grunnlag for fradrag.", "CONTRADICTS", ["F31"], ["numeric"], None, True),
    E("RC31-0053", "Avtalt men ikke gjennomfort samvar gir fradrag.", "CONTRADICTS", ["F32"], ["condition", "negation"], None, True),
    E("RC31-0054", "Samvaret ma faktisk gjennomfores for a gi fradrag.", "ENTAILS", ["F32"], ["condition"], None, False),
    E("RC31-0055", "Reisekostnadssatsen for 0-5 dager samvar i klasse 2 er 1277 kroner.", "ENTAILS", ["F33"], ["numeric", "actor"], None, False),
    E("RC31-0056", "Reisekostnadssatsen for 11-14 dager samvar i klasse 2 er 1277 kroner.", "CONTRADICTS", ["F33"], ["numeric", "actor"], None, True),
    E("RC31-0057", "Delt ordinar barnetrygd er 1006 kroner per maned.", "ENTAILS", ["F34"], ["numeric", "actor"], None, False),
    E("RC31-0058", "Full ordinar barnetrygd er 2012 kroner per maned.", "ENTAILS", ["F34"], ["numeric", "actor"], None, False),
    E("RC31-0059", "Delt ordinar barnetrygd er 1286 kroner per maned.", "CONTRADICTS", ["F34", "F35"], ["numeric", "actor"], None, True),
    E("RC31-0060", "Delt utvidet barnetrygd er 2572 kroner i maneden.", "CONTRADICTS", ["F35"], ["numeric", "actor"], None, True),
    E("RC31-0061", "En forelder med delt fast bosted og innvilget delt utvidet barnetrygd far 2292 kroner i maneden fra NAV hvis begge deler er innvilget.", "ENTAILS", ["F36"], ["numeric", "condition", "actor"], None, False),
    E("RC31-0062", "Delt utvidet barnetrygd kommer i tillegg til den ordinarie delte barnetrygden.", "ENTAILS", ["F36"], ["actor"], None, False),
    E("RC31-0063", "Delt ordinar barnetrygd er 1006 kroner, og delt utvidet barnetrygd er 2572 kroner.",
      "PARTIAL", ["F34", "F35"],
      ["compound", "numeric", "actor"],
      [("A1", "Delt ordinar barnetrygd er 1006 kroner", ["S1"]), ("A2", "Delt utvidet barnetrygd er 2572 kroner", ["S2"])], True),
    E("RC31-0064", "Full barnetrygd for ordinar og utvidet til sammen er 4584 kroner per maned.",
      "ENTAILS", ["F34", "F35"], ["numeric", "actor", "compound"],
      [("A1", "Full ordinar barnetrygd er 2012 kroner per maned", ["S1"]), ("A2", "Full utvidet barnetrygd er 2572 kroner per maned", ["S2"])], False),
    E("RC31-0065", "Kommunen skal gi opplysning, rad og veiledning uavhengig av rett til okonomisk sosialhjelp.", "ENTAILS", ["F37"], ["modality", "actor"], None, False),
    E("RC31-0066", "De som ikke kan sorge for livsoppholdet gjennom arbeid, har krav pa okonomisk stonad.", "ENTAILS", ["F38"], ["condition", "actor"], None, False),
    E("RC31-0067", "Alle har krav pa okonomisk stonad til livsopphold.", "CONTRADICTS", ["F38"], ["condition", "actor"], None, True),
    E("RC31-0068", "Kommunen kan yte okonomisk hjelp etter paragraf 19 selv om vilkarene i paragraf 18 ikke er til stede.",
      "ENTAILS", ["F39"], ["modality", "exception", "actor", "compound"],
      [("A1", "Kommunen kan yte okonomisk hjelp etter paragraf 19", ["S1"]), ("A2", "Gjelder selv om vilkarene i paragraf 18 ikke er til stede", ["S1"])], False),
    E("RC31-0069", "Kommunen skal alltid yte okonomisk hjelp etter paragraf 19 nar paragraf 18-vilkarene ikke er oppfylt.", "CONTRADICTS", ["F39"], ["modality", "actor"], None, True),
    E("RC31-0070", "Sosialhjelpssatser fastsettes arlig av Stortinget.", "RELATED_BUT_INSUFFICIENT", ["F38", "F39"], ["actor"], None, False),
    E("RC31-0071", "Kvalifiseringsprogrammet gjelder personer 18-67 ar.", "ENTAILS", ["F40"], ["numeric", "actor"], None, False),
    E("RC31-0072", "Kvalifiseringsstonaden er 2,041 G pa arsbasis.", "ENTAILS", ["F40"], ["numeric", "actor"], None, False),
    E("RC31-0073", "Barnetrygd skal ikke tas hensyn ved vurdering av stonad til familier etter paragraf 18.", "ENTAILS", ["F41"], ["negation"], None, False),
    E("RC31-0074", "Barnetrygd reduserer okonomisk sosialhjelp til familier.", "CONTRADICTS", ["F41"], ["negation"], None, True),
    E("RC31-0075", "Full overgangstonad er 307 235 kroner per ar.", "ENTAILS", ["F42"], ["numeric", "actor"], None, False),
    E("RC31-0076", "Full overgangstonad er 2,25 G.", "ENTAILS", ["F42"], ["numeric", "actor"], None, False),
    E("RC31-0077", "Full overgangstonad er 25 603 kroner for skatt per maned.", "ENTAILS", ["F43"], ["numeric", "actor"], None, False),
    E("RC31-0078", "Full overgangstonad er 25 603 kroner etter skatt.", "CONTRADICTS", ["F43"], ["numeric", "actor"], None, True),
    E("RC31-0079", "Det kan ytes overgangstonad inntil 2 maneder for fodselen.", "ENTAILS", ["F44"], ["modality", "temporal", "actor"], None, False),
    E("RC31-0080", "Overgangstonad ytes alltid fra uke 12 av svangerskapet.", "RELATED_BUT_INSUFFICIENT", ["F44"], ["numeric", "temporal", "actor"], None, False),
    E("RC31-0081", "Mottakere som star i ordningen per 30. juni 2026 beholder de tidligere reglene.", "ENTAILS", ["F45"], ["condition", "actor"], None, False),
    E("RC31-0082", "Alle overgangstonadsmottakere overgar til de nye reglene i juli 2026.", "CONTRADICTS", ["F45"], ["condition", "actor"], None, True),
    E("RC31-0083", "De to regelverkene for overgangstonad loper parallelt frem til 30. juni 2031.", "ENTAILS", ["F45"], ["temporal", "numeric", "actor"], None, False),
    E("RC31-0084", "Belopet for depositumssikkerhet er som utgangspunkt inntil seks maneders leie.", "ENTAILS", ["F46"], ["numeric", "actor"], None, False),
    E("RC31-0085", "Utleier kan kreve opptil seks maneders leie i depositum.", "ENTAILS", ["F46"], ["modality", "numeric", "actor"], None, False),
    E("RC31-0086", "Kontant depositumssikkerhet skal pa sperret konto.", "ENTAILS", ["F46"], ["modality", "actor"], None, False),
    E("RC31-0087", "Nav gir alltid garanti for depositum til alle som sokker.", "CONTRADICTS", ["F47"], ["modality", "negation", "actor"], None, True),
    E("RC31-0088", "Nav-garanti for depositum er en automatisk rettighet.", "CONTRADICTS", ["F47"], ["modality", "actor"], None, True),
    E("RC31-0089", "Nav kan gi garanti for depositum nar du ikke kan skaffe pengene selv.", "ENTAILS", ["F47"], ["modality", "condition", "actor"], None, False),
    E("RC31-0090", "Kommunalt lan for depositum er en nasjonal rettighet.", "RELATED_BUT_INSUFFICIENT", ["F46", "F47"], ["actor"], None, False),
    E("RC31-0091", "Udir anbefaler skriftlig plan for oppfolging nar fravaeret er bekymringsfullt.", "ENTAILS", ["F48"], ["modality", "actor"], None, False),
    E("RC31-0092", "Skolen er lovfestet pliktig til a lage skriftlig fravaersplan i alle tilfeller.", "CONTRADICTS", ["F48"], ["modality", "actor"], None, True),
    E("RC31-0093", "Skoler i Trondheim lager alltid skriftlig fravaersplan.", "RELATED_BUT_INSUFFICIENT", ["F48"], ["scope", "actor"], None, False),
    E("RC31-0094", "Foresatte kan soke Statped via Statpeds kontaktform.", "ENTAILS", ["F16"], ["modality", "actor"], None, False),
    E("RC31-0095", "Kun PPT kan soke Statped.", "CONTRADICTS", ["F16"], ["actor", "negation"], None, True),
    E("RC31-0096", "Statped tilbyr kurs for foresatte.", "ENTAILS", ["F17"], ["actor"], None, False),
    E("RC31-0097", "Statped yter direkte behandling til barnet.", "CONTRADICTS", ["F15"], ["negation", "actor"], None, True),
    E("RC31-0098", "Etter 18-arsdagen kan barnebidrag betales direkte til den unge.", "ENTAILS", ["F49"], ["modality", "numeric", "actor"], None, False),
    E("RC31-0099", "Barnebidrag betales alltid til barnet selv etter fylte 18 ar.", "CONTRADICTS", ["F49"], ["modality", "actor"], None, True),
    E("RC31-0100", "Plikten til a betale barnebidrag varer normalt til og med maneden barnet fyller 18.", "ENTAILS", ["F50"], ["temporal", "actor"], None, False),
    E("RC31-0101", "Barnebidragsplikten opphorer definitivt ved 18-arsdagen i alle tilfeller.", "CONTRADICTS", ["F50"], ["negation", "exception"], None, True),
    E("RC31-0102", "Etter fylte 18 ar kan barnet ha rett til forsorgelse gjennom videregaende opplaring.", "ENTAILS", ["F50"], ["modality"], None, False),
    E("RC31-0103", "Etter fylte 18 ar har barnet alltid rett til forsorgelse gjennom videregaende opplaring.", "CONTRADICTS", ["F50"], ["modality", "actor"], None, True),
    E("RC31-0104", "Den kommunale psykiske helsetjenesten for barn og unge skal vaere apen for alle barn og unge i kommunen.", "ENTAILS", ["F4"], ["modality"], None, False),
    E("RC31-0105", "Kommunens psykiske lavterskeltilbud krever henvisning fra fastlegen.", "CONTRADICTS", ["F4"], ["negation"], None, True),
    E("RC31-0106", "I Barums tilbud skal begge foreldre vaere orientert og samtykke til oppfolging.", "ENTAILS", ["F6"], ["condition", "scope", "actor"], None, False),
    E("RC31-0107", "Personer over 16 ar er selv helserettslig myndig.", "ENTAILS", ["F6"], ["numeric", "actor"], None, False),
    E("RC31-0108", "Begge foreldre ma alltid samtykke for at et barn under 18 ar far psykisk helsehjelp i kommunen.", "AMBIGUOUS", ["F6"], ["scope", "modality"], None, False),
    E("RC31-0109", "Familieteam helse 0-20 ar er navnet pa tilbudet i alle kommuner.", "CONTRADICTS", ["F7"], ["actor", "numeric"], None, True),
    E("RC31-0110", "HFU-tilbudet krever foreldretillatelse for 17-aringer.", "CONTRADICTS", ["F25"], ["negation", "actor"], None, True),
    E("RC31-0111", "Helsestasjon for ungdom tilbyr drop-in uten foreldretillatelse.", "ENTAILS", ["F25"], ["modality", "negation"], None, False),
    E("RC31-0112", "Pensjon kan tas ut fra 62 ar.", "UNRELATED", ["F1"], ["numeric"], None, False),
    E("RC31-0113", "Alderspensjon kan tas ut fra 62 ar.", "ENTAILS", ["F51"], ["modality", "numeric", "actor"], None, False),
    E("RC31-0114", "Full alderspensjon oppnas uansett trygdetid.", "CONTRADICTS", ["F52"], ["condition", "numeric", "actor"], None, True),
    E("RC31-0115", "Minimum 5 ars medlemskap kreves for alderspensjon.", "ENTAILS", ["F52"], ["modality", "numeric", "actor"], None, False),
    E("RC31-0116", "Alle kan registrere seg som jobbsoker hos NAV.", "ENTAILS", ["F53"], ["modality"], None, False),
    E("RC31-0117", "Registrering som jobbsoker er begrenset til personer under 30 ar.", "CONTRADICTS", ["F53"], ["numeric", "negation"], None, True),
    E("RC31-0118", "Krisesenterlinjen er 116 006 og er dognrundt.",
      "ENTAILS", ["F54"], ["numeric", "actor", "compound"],
      [("A1", "Krisesenterlinjen er 116 006", ["S1"]), ("A2", "Krisesenterlinjen er dognrundt", ["S1"])], False),
    E("RC31-0119", "Ved akutt fare skal man ringe 02800.", "CONTRADICTS", ["F54"], ["numeric", "actor"], None, True),
    E("RC31-0120", "Behandlingsstedet skal vurdere rett til nodvendig helsehjelp innen 10 virkedager.", "ENTAILS", ["F55"], ["numeric", "modality", "actor"], None, False),
    E("RC31-0121", "Den bindende fristen skal settes ut fra Helsedirektoratets prioriteringsveiledere.", "ENTAILS", ["F56"], ["modality", "actor"], None, False),
    E("RC31-0122", "Den bindende fristen kan settes ut fra behandlingsstedets kapasitet.", "CONTRADICTS", ["F56"], ["negation", "modality", "actor"], None, True),
    E("RC31-0123", "Svar med rett til helsehjelp gir fritt behandlingsvalg.", "ENTAILS", ["F56"], ["modality", "actor"], None, False),
    E("RC31-0124", "Skolehelsetjenesten stiller normalt ikke diagnoser.", "ENTAILS", ["F21"], ["negation"], None, False),
    E("RC31-0125", "Skolelegen kan i noen kommuner evaluere foreskrevne legemidler.", "ENTAILS", ["F21"], ["modality", "scope", "actor"], None, False),
    E("RC31-0126", "Skolelegen skriver ut legemidler i alle kommuner.", "CONTRADICTS", ["F21"], ["scope", "negation", "actor"], None, True),
    E("RC31-0127", "PPT skal bistar barnehagen i kompetanseutvikling.", "ENTAILS", ["F11"], ["modality", "actor"], None, False),
    E("RC31-0128", "PPT stiller diagnoser ved mistanke om ADHD.", "CONTRADICTS", ["F14"], ["actor", "negation"], None, True),
    E("RC31-0129", "Rask psykisk helsehjelp er for personer over 16 ar, og den tar ikke imot alvorlige og sammensatte problemer.",
      "ENTAILS", ["F8"], ["compound", "negation"],
      [("A1", "Rask psykisk helsehjelp gjelder personer over 16 ar", ["S1"]), ("A2", "Rask psykisk helsehjelp tar ikke imot alvorlige og sammensatte problemer", ["S1"])], False),
    E("RC31-0130", "Rask psykisk helsehjelp tar imot barn under 16 ar, og den er en del av den kommunale helsetjenesten.",
      "CONTRADICTS", ["F8"], ["compound", "actor"],
      [("A1", "Rask psykisk helsehjelp tar imot barn under 16 ar", ["S1"]), ("A2", "Rask psykisk helsehjelp er en del av den kommunale helsetjenesten", ["S1"])], True),
    E("RC31-0131", "Bostotte krever egen inngang, og soknadsfristen er den 20. i maneden.",
      "PARTIAL", ["F27", "F28"], ["compound", "condition", "actor"],
      [("A1", "Bostotte krever egen inngang", ["S1"]), ("A2", "Soknadsfristen er den 20. i maneden", ["S2"])], True),
    E("RC31-0132", "Samvaret ma faktisk gjennomfores for a gi fradrag, og mer enn 2 dager samvar i gjennomsnitt gir grunnlag for fradrag.",
      "ENTAILS", ["F32", "F31"], ["compound", "condition"],
      [("A1", "Samvaret ma faktisk gjennomfores for a gi fradrag", ["S1"]), ("A2", "Mer enn 2 dager samvar i gjennomsnitt per maned gir grunnlag for fradrag", ["S2"])], False),
    E("RC31-0133", "Reisekostnadssatsen i klasse 2 for 0-5 dager er 1277 kroner, og for 6-10 dager er den 1277 kroner.",
      "PARTIAL", ["F33"], ["compound", "numeric", "actor"],
      [("A1", "Satsen for 0-5 dager i klasse 2 er 1277 kroner", ["S1"]), ("A2", "Satsen for 6-10 dager i klasse 2 er 1277 kroner", ["S1"])], True),
    E("RC31-0134", "Delt ordinar barnetrygd er 1006 kroner, og delt utvidet barnetrygd er 1286 kroner.",
      "ENTAILS", ["F34", "F35"], ["compound", "numeric", "actor"],
      [("A1", "Delt ordinar barnetrygd er 1006 kroner", ["S1"]), ("A2", "Delt utvidet barnetrygd er 1286 kroner", ["S2"])], False),
    E("RC31-0135", "Delt ordinar barnetrygd er 2012 kroner, og full utvidet barnetrygd er 2572 kroner.",
      "CONTRADICTS", ["F34", "F35"], ["compound", "numeric", "actor"],
      [("A1", "Delt ordinar barnetrygd er 2012 kroner", ["S1"]), ("A2", "Full utvidet barnetrygd er 2572 kroner", ["S2"])], True),
    E("RC31-0136", "Kommunen skal gi rad og veiledning etter paragraf 17, og kommunen skal alltid yte okonomisk hjelp etter paragraf 19.",
      "PARTIAL", ["F37", "F39"], ["compound", "modality"],
      [("A1", "Kommunen skal gi rad og veiledning etter paragraf 17", ["S1"]), ("A2", "Kommunen skal alltid yte okonomisk hjelp etter paragraf 19", ["S2"])], True),
    E("RC31-0137", "Okonomisk stonad etter paragraf 18 er en rettighet nar vilkarene er oppfylt, og paragraf 19-stonad er skjonsbestemt.",
      "ENTAILS", ["F38", "F39"], ["compound", "condition", "actor"],
      [("A1", "Okonomisk stonad etter paragraf 18 er en rettighet nar vilkarene er oppfylt", ["S1"]), ("A2", "Paragraf 19-stonad er skjonsbestemt", ["S2"])], False),
    E("RC31-0138", "Full overgangstonad er 25 603 kroner per maned, og den utbetales etter skatt.",
      "PARTIAL", ["F43"], ["compound", "numeric", "actor"],
      [("A1", "Full overgangstonad er 25 603 kroner per maned", ["S1"]), ("A2", "Den utbetales etter skatt", ["S1"])], True),
    E("RC31-0139", "Mottakere per 30. juni 2026 beholder tidligere regler, og regelverkene loper parallelt frem til 30. juni 2031.",
      "ENTAILS", ["F45"], ["compound", "temporal", "actor"],
      [("A1", "Mottakere per 30. juni 2026 beholder tidligere regler", ["S1"]), ("A2", "Regelverkene loper parallelt frem til 30. juni 2031", ["S1"])], False),
    E("RC31-0140", "Depositum er som utgangspunkt inntil seks maneders leie, og kontant sikkerhet skal pa sperret konto.",
      "ENTAILS", ["F46"], ["compound", "modality", "actor"],
      [("A1", "Depositum er som utgangspunkt inntil seks maneders leie", ["S1"]), ("A2", "Kontant sikkerhet skal pa sperret konto", ["S1"])], False),
    E("RC31-0141", "Nav gir alltid depositumsgaranti, og depositum kan vaere inntil seks maneders leie.",
      "PARTIAL", ["F47", "F46"], ["compound", "modality", "actor"],
      [("A1", "Nav gir alltid depositumsgaranti", ["S1"]), ("A2", "Depositum kan vaere inntil seks maneders leie", ["S2"])], True),
    E("RC31-0142", "PPT kan soke Statped om kartlegging, og Statped retter seg mot det faglige laget.",
      "ENTAILS", ["F15"], ["compound", "modality", "actor"],
      [("A1", "PPT kan soke Statped om kartlegging", ["S1"]), ("A2", "Statped retter seg mot det faglige laget rundt barnet", ["S1"])], False),
    E("RC31-0143", "Statped tilbyr kurs for foresatte, og Statped behandler barn direkte.",
      "PARTIAL", ["F17", "F15"], ["compound", "negation", "actor"],
      [("A1", "Statped tilbyr kurs for foresatte", ["S1"]), ("A2", "Statped behandler barn direkte", ["S2"])], True),
    E("RC31-0144", "Barnebidragsplikten varer normalt til 18 ar, og etter 18 kan barnet ha rett til forsorgelse gjennom videregaende opplaring.",
      "ENTAILS", ["F50"], ["compound", "temporal", "actor"],
      [("A1", "Barnebidragsplikten varer normalt til og med maneden barnet fyller 18", ["S1"]), ("A2", "Etter 18 kan barnet ha rett til forsorgelse gjennom videregaende opplaring", ["S1"])], False),
    E("RC31-0145", "Barnebidrag betales alltid til barnet selv etter 18 ar, og plikten varer normalt til og med maneden barnet fyller 18.",
      "PARTIAL", ["F49", "F50"], ["compound", "modality", "actor"],
      [("A1", "Barnebidrag betales alltid til barnet selv etter 18 ar", ["S1"]), ("A2", "Plikten varer normalt til og med maneden barnet fyller 18", ["S2"])], True),
    E("RC31-0146", "Udir anbefaler skriftlig plan ved bekymringsfullt fravar, og retningslinjen er veiledende og ikke lovfestet.",
      "ENTAILS", ["F48"], ["compound", "modality", "actor"],
      [("A1", "Udir anbefaler skriftlig plan ved bekymringsfullt fravar", ["S1"]), ("A2", "Retningslinjen er veiledende og ikke lovfestet", ["S1"])], False),
    E("RC31-0147", "Kommunen skal tilby skolehelsetjeneste 0-20 ar, og den skal vaere gratis for brukerne.",
      "ENTAILS", ["F19"], ["compound", "numeric", "actor"],
      [("A1", "Kommunen skal tilby skolehelsetjeneste til barn og ungdom 0-20 ar", ["S1"]), ("A2", "Skolehelsetjenesten er gratis for brukerne", ["S1"])], False),
    E("RC31-0148", "Skolehelsetjenesten tilbyr helseundersokelser, og den yter psykoterapi.",
      "PARTIAL", ["F20", "F21"], ["compound", "negation", "actor"],
      [("A1", "Skolehelsetjenesten tilbyr helseundersokelser", ["S1"]), ("A2", "Skolehelsetjenesten yter psykoterapi", ["S2"])], True),
    E("RC31-0149", "Elever pa 14 ar kan samtykke til helsehjelp i forhold foreldrene ikke er informert om, og foreldre samtykker normalt pa vegne av barn under 16 ar.",
      "ENTAILS", ["F23", "F24"], ["compound", "numeric", "actor"],
      [("A1", "12-16-aringer kan samtykke til helsehjelp i forhold foreldrene ikke er informert om", ["S1"]), ("A2", "Foreldre samtykker pa vegne av barn under 16 ar", ["S2"])], False),
    E("RC31-0150", "Personer over 16 ar er selv helserettslig myndig, og RPH tar imot 12-aringer.",
      "PARTIAL", ["F6", "F8"], ["compound", "actor"],
      [("A1", "Personer over 16 ar er selv helserettslig myndig", ["S1"]), ("A2", "RPH tar imot 12-aringer", ["S2"])], True),
    E("RC31-0151", "Psykolog i kommunen kan henvise til BUP, og barnevernsleder har ogsa henvisningsrett.",
      "ENTAILS", ["F5"], ["compound", "actor"],
      [("A1", "Psykolog i kommunen kan henvise til BUP", ["S1"]), ("A2", "Barnevernsleder har henvisningsrett til BUP", ["S1"])], False),
    E("RC31-0152", "Kommunen kan kreve henvisning til sitt lavterskeltilbud for barn og unge, og BUP krever henvisning.",
      "AMBIGUOUS", ["F4", "F5"], ["compound", "modality", "actor"],
      [("A1", "Kommunen kan kreve henvisning til sitt lavterskeltilbud", ["S1"]), ("A2", "BUP krever henvisning", ["S2"])], False),
    E("RC31-0153", "Barum-tilbudet er uten henvisning, og det passer ikke ved akutt behov.",
      "ENTAILS", ["F6"], ["compound", "condition", "actor"],
      [("A1", "Barum-tilbudet er et lavterskeltilbud uten henvisning", ["S1"]), ("A2", "Tilbudet passer ikke ved akutt behov", ["S1"])], False),
    E("RC31-0154", "Alderspensjon kan tas ut fra 62 ar, og fullt minimum krever 40 ars medlemskap.",
      "ENTAILS", ["F51", "F52"], ["compound", "numeric", "actor"],
      [("A1", "Alderspensjon kan tas ut fra 62 ar", ["S1"]), ("A2", "Fullt minimum krever 40 ars medlemskap", ["S2"])], False),
    E("RC31-0155", "Alle kan registrere seg som jobbsoker, og registrering krever fullfort hoyere utdanning.",
      "PARTIAL", ["F53"], ["compound", "negation", "actor"],
      [("A1", "Alle kan registrere seg som jobbsoker", ["S1"]), ("A2", "Registrering krever fullfort hoyere utdanning", ["S1"])], True),
    E("RC31-0156", "Krisesenterlinjen er 116 006, og ved akutt fare gjelder 112.",
      "ENTAILS", ["F54"], ["compound", "numeric", "actor"],
      [("A1", "Krisesenterlinjen er 116 006", ["S1"]), ("A2", "Ved akutt fare skal man ringe 112", ["S1"])], False),
    E("RC31-0157", "Behandlingsstedet skal vurdere rett til helsehjelp innen 10 virkedager, og svaret skal inneholde bindende frist.",
      "ENTAILS", ["F55"], ["compound", "numeric", "actor"],
      [("A1", "Behandlingsstedet skal vurdere rett til helsehjelp innen 10 virkedager", ["S1"]), ("A2", "Svaret skal inneholde bindende frist for oppstart", ["S1"])], False),
    E("RC31-0158", "Svar med rett til helsehjelp gir fritt behandlingsvalg, og den bindende fristen skal folge prioriteringsveilederne.",
      "ENTAILS", ["F56"], ["compound", "modality", "actor"],
      [("A1", "Svar med rett til helsehjelp gir fritt behandlingsvalg", ["S1"]), ("A2", "Den bindende fristen skal folge prioriteringsveilederne", ["S1"])], False),
    E("RC31-0159", "Boligen ma ha kjokkenlosning og mulighet for hvile.",
      "ENTAILS", ["F27"], ["compound", "actor"],
      [("A1", "Boligen ma ha kjokkenlosning", ["S1"]), ("A2", "Boligen ma ha mulighet for hvile", ["S1"])], False),
    E("RC31-0160", "Boligen ma ha egen inngang og eget bad og toalett.",
      "ENTAILS", ["F27"], ["compound", "actor"],
      [("A1", "Boligen ma ha egen inngang", ["S1"]), ("A2", "Boligen ma ha eget bad og toalett", ["S1"])], False),
    E("RC31-0161", "PPT skal stotte og veilede skolene i a utrede behov for tilrettelegging.",
      "ENTAILS", ["F11"], ["compound", "modality", "actor"],
      [("A1", "PPT skal stotte skolene", ["S1"]), ("A2", "PPT skal veilede skolene i a utrede behov for tilrettelegging", ["S1"])], False),
    E("RC31-0162", "PPT skal utrede behov for tilrettelegging og sette inn tiltak sa tidlig som mulig.",
      "ENTAILS", ["F11"], ["compound", "modality", "actor"],
      [("A1", "PPT skal utrede behov for tilrettelegging", ["S1"]), ("A2", "PPT skal sette inn tiltak sa tidlig som mulig", ["S1"])], False),
    E("RC31-0163", "Sokker du sosialhjelp til boutgifter, vil kommunen som regel kreve at du sokker bostotte forst.",
      "ENTAILS", ["F30"], ["condition", "compound", "actor"],
      [("A1", "Kommunen kan kreve at du sokker bostotte forst", ["S1"]), ("A2", "Kravet gjelder nar du sokker sosialhjelp til boutgifter", ["S1"])], False),
    E("RC31-0164", "Far du innvilget begge deler, far du 2292 kroner i maneden, og satsen gjelder alle foreldre uten vilkar.",
      "PARTIAL", ["F36"], ["compound", "condition", "actor"],
      [("A1", "Med begge deler innvilget far forelderen 2292 kroner i maneden", ["S1"]), ("A2", "Satsen gjelder alle foreldre uten vilkar", ["S1"])], True),
    E("RC31-0165", "Er du over 18 ar og ikke i forstegangstjenesten, kan du kvalifisere for bostotte.", "ENTAILS", ["F26"], ["condition", "modality", "compound", "actor"], None, False),
    E("RC31-0166", "Barn under 18 ar med barn kan kvalifisere for bostotte.", "ENTAILS", ["F26"], ["exception", "modality", "compound", "actor"], None, False),
    E("RC31-0167", "Personer i forstegangstjenesten over 18 ar kvalifiserer for bostotte.", "CONTRADICTS", ["F26"], ["negation", "exception", "compound", "actor"], None, True),
    E("RC31-0168", "Foreldre samtykker pa vegne av barn under 16 ar, men 12-16-aringer kan samtykke i forhold foreldrene ikke er informert om.",
      "ENTAILS", ["F24", "F23"], ["exception", "compound", "actor"],
      [("A1", "Foreldre samtykker pa vegne av barn under 16 ar", ["S1"]), ("A2", "12-16-aringer kan samtykke til helsehjelp i forhold foreldrene ikke er informert om", ["S2"])], False),
    E("RC31-0169", "Samtykke til helsehjelp gis av personer over 18 ar som hovedregel, men 16-18-aringer har rett til a samtykke med mindre annet folger av saerlige bestemmelser.",
      "ENTAILS", ["F23"], ["exception", "compound", "actor"],
      [("A1", "Beslutningskompetanse for samtykke til helsehjelp: 18+ som hovedregel", ["S1"]), ("A2", "16-18-aringer har rett til a samtykke med mindre annet folger av saerlige bestemmelser", ["S1"])], False),
    E("RC31-0170", "Personer over 18 ar samtykker som hovedregel selv, men alle 12-aringer kan samtykke til all helsehjelp.",
      "PARTIAL", ["F23"], ["exception", "compound", "actor"],
      [("A1", "Personer over 18 ar samtykker selv som hovedregel", ["S1"]), ("A2", "Alle 12-aringer kan samtykke til all helsehjelp", ["S1"])], True),
    E("RC31-0171", "Kommunen kan yte okonomisk hjelp etter paragraf 19, men dette er skjonsbestemt og ikke en automatisk rett.",
      "ENTAILS", ["F39"], ["modality", "compound", "actor"],
      [("A1", "Kommunen kan yte okonomisk hjelp etter paragraf 19", ["S1"]), ("A2", "Paragraf 19-hjelpen er skjonsbestemt og ikke en automatisk rett", ["S1"])], False),
    E("RC31-0172", "Skolehelsetjenesten yter ikke psykoterapi og stiller normalt ikke diagnoser.",
      "ENTAILS", ["F21"], ["negation", "compound", "actor"],
      [("A1", "Skolehelsetjenesten yter ikke psykoterapi", ["S1"]), ("A2", "Skolehelsetjenesten stiller normalt ikke diagnoser", ["S1"])], False),
    E("RC31-0173", "PPT stiller ikke diagnoser og er ikke behandlingstjeneste.",
      "ENTAILS", ["F14"], ["negation", "compound", "actor"],
      [("A1", "PPT stiller ikke diagnoser", ["S1"]), ("A2", "PPT er ikke behandlingstjeneste", ["S1"])], False),
    E("RC31-0174", "HFU-tilbudet er gratis og krever foreldretillatelse.",
      "PARTIAL", ["F9", "F25"], ["compound", "negation", "actor"],
      [("A1", "HFU-tilbudet er gratis", ["S1"]), ("A2", "HFU-tilbudet krever foreldretillatelse", ["S2"])], True),
    E("RC31-0175", "BUP/PHBU er spesialisthelsetjenesten, og henvisning kan komme fra fastlege eller psykolog i kommunen.",
      "ENTAILS", ["F10"], ["compound", "actor"],
      [("A1", "BUP/PHBU er spesialisthelsetjenesten", ["S1"]), ("A2", "Henvisning til BUP kan komme fra fastlege eller psykolog i kommunen", ["S1"])], False),
    E("RC31-0176", "Skolehelsetjenesten omfatter grunnskoler og videregaende skoler, og helsestasjonstjenesten gjelder 0-20 ar.",
      "ENTAILS", ["F18"], ["compound", "numeric", "actor"],
      [("A1", "Skolehelsetjenesten omfatter helsetjeneste i grunnskoler og videregaende skoler", ["S1"]), ("A2", "Helsestasjonstjenesten gjelder 0-20 ar", ["S1"])], False),
    E("RC31-0177", "Skolehelsetjenesten yter psykoterapi, og den tilbyr helseundersokelser.",
      "PARTIAL", ["F21", "F20"], ["compound", "negation", "actor"],
      [("A1", "Skolehelsetjenesten yter psykoterapi", ["S1"]), ("A2", "Skolehelsetjenesten tilbyr helseundersokelser", ["S2"])], True),
    E("RC31-0178", "Ung Arena i Oslo er en moteplass og aktivitetstilbud, ikke terapitjeneste.",
      "ENTAILS", ["F7"], ["negation", "compound", "actor"],
      [("A1", "Ung Arena i Oslo er en moteplass og aktivitetstilbud", ["S1"]), ("A2", "Ung Arena er ikke en terapitjeneste", ["S1"])], False),
    E("RC31-0179", "PHFS er det lokale navnet pa det kommunale lavterskeltilbudet i Lillestrom.",
      "ENTAILS", ["F7"], ["actor", "scope", "compound"], None, False),
    E("RC31-0180", "Bostotten er godkjente boutgifter minus egenandel, og minsteutbetalingen er 61 kroner per maned.",
      "ENTAILS", ["F29"], ["compound", "numeric", "actor"],
      [("A1", "Bostotten er godkjente boutgifter minus egenandel, begrenset av inntektsgrensen", ["S1"]), ("A2", "Minsteutbetalingen er 61 kroner per maned", ["S1"])], False),
    E("RC31-0181", "PPT skal veilede skolene om tilrettelegging, og PPT utarbeider den sakkyndige vurderingen nar lova krever det.",
      "ENTAILS", ["F11", "F12"], ["compound", "modality", "condition", "actor"],
      [("A1", "PPT skal veilede skolene i a utrede behov for tilrettelegging", ["S1"]), ("A2", "PPT utarbeider den sakkyndige vurderingen nar lova eller forskrift krever det", ["S2"])], False),
    E("RC31-0182", "Statped gir radgiving og veiledning, og Statped gir direkte behandling til barnet.",
      "PARTIAL", ["F17", "F15"], ["compound", "negation", "actor"],
      [("A1", "Statped gir radgiving og veiledning", ["S1"]), ("A2", "Statped gir direkte behandling til barnet", ["S2"])], True),
    E("RC31-0183", "Skolehelsetjenesten stiller normalt ikke diagnoser, og skolelegen kan i noen kommuner evaluere foreskrevne legemidler.",
      "ENTAILS", ["F21"], ["compound", "negation", "modality", "actor"],
      [("A1", "Skolehelsetjenesten stiller normalt ikke diagnoser", ["S1"]), ("A2", "Skolelegen kan i noen kommuner evaluere foreskrevne legemidler", ["S1"])], False),
    E("RC31-0184", "HFU-tilbudet er gratis i alle kommuner, og HFU-tilbudet gjelder opp til 25 ar.",
      "PARTIAL", ["F9"], ["compound", "numeric", "actor"],
      [("A1", "HFU-tilbudet er gratis", ["S1"]), ("A2", "Alle kommuner har HFU-tilbud opptil 25 ar", ["S1"])], True),
]


def build_case(entry):
    facts = entry["facts"]
    sources, evidence = [], []
    for i, fid in enumerate(facts, start=1):
        fname, lineno, text = FACTS[fid]
        sources.append({"kb_ref": "kb/" + fname, "lines": [lineno],
                        "text": text})
        evidence.append({"span_id": "S%d" % i, "text": text})
    case = {
        "case_id": entry["cid"],
        "claim": entry["claim"],
        "track": "B" if entry["atoms"] else "A",
        "sources": sources,
        "evidence": evidence,
        "compound": bool(entry["atoms"]),
        "public_flags": list(entry["shapes"]),
    }
    if entry["atoms"]:
        case["atoms"] = [
            {"atom_id": aid, "text": atext,
             "relation_to_parent": "CONJUNCT",
             "evidence_span_ids": spans}
            for aid, atext, spans in entry["atoms"]
        ]
    return case


def main():
    assert len(CASES) == 184, "expected 184 cases, got %d" % len(CASES)
    cases = [build_case(e) for e in CASES]

    bad = []
    for e, c in zip(CASES, cases):
        errs = ct.validate_case(c, kb_root=ROOT)
        if errs:
            bad.append((e["cid"], errs))
    if bad:
        for cid, errs in bad:
            print(cid, errs)
        sys.exit("validation failed")

    burned = ct.load_burned_claims(HOLDOUT)
    flagged = ct.check_novelty([c["claim"] for c in cases], burned)
    if flagged:
        for f in flagged:
            print("NOVELTY:", f)
        sys.exit("novelty check failed")

    counts, missing = ct.check_quotas(CASES)
    if missing:
        sys.exit("quota shortfall: %r (counts=%r)" % (missing, counts))
    balance = ct.relation_balance(CASES)
    compound_n = sum(1 for c in cases if c["compound"])

    # Deterministic split: seeded shuffle of sorted case IDs (seed is
    # public and recorded in the manifest); first 60 -> VALIDATION.
    ids_sorted = sorted(c["case_id"] for c in cases)
    rng = random.Random(20260904)
    shuffled = list(ids_sorted)
    rng.shuffle(shuffled)
    validation_ids = set(shuffled[:60])
    train = [c for c in cases if c["case_id"] not in validation_ids]
    validation = [c for c in cases if c["case_id"] in validation_ids]
    train_ids = {c["case_id"] for c in train}
    train_labeled = []
    for e in CASES:
        if e["cid"] in train_ids:
            c = build_case(e)
            c["rel"] = e["rel"]
            c["critical"] = e["critical"]
            train_labeled.append(c)
    # Expected atom boundaries are label data: keep them out of the
    # public validation file and seal them with the relation labels.
    validation_pub = []
    val_labels = {}
    for e in CASES:
        if e["cid"] in train_ids:
            continue
        c = build_case(e)
        pub = {k: v for k, v in c.items() if k != "atoms"}
        validation_pub.append(pub)
        lab = {"relation": e["rel"]}
        if e.get("atoms"):
            lab["expected_atoms"] = [
                {"atom_id": aid, "text": atext,
                 "relation_to_parent": "CONJUNCT"}
                for aid, atext, spans in e["atoms"]]
        val_labels[e["cid"]] = lab

    out = HERE / "corpus"
    out.mkdir(exist_ok=True)
    (out / "train-cases.json").write_text(
        json.dumps({"set_id": "RC31-PROOF-DEV-TRAIN",
                    "case_count": len(train_labeled),
                    "cases": train_labeled}, ensure_ascii=False,
                   indent=1) + "\n", encoding="utf-8")
    (out / "validation-cases.json").write_text(
        json.dumps({"set_id": "RC31-PROOF-DEV-VALIDATION",
                    "case_count": len(validation_pub),
                    "cases": validation_pub}, ensure_ascii=False,
                   indent=1) + "\n", encoding="utf-8")

    key_hex, seal_path = ct.seal_validation_key(
        out / "validation-cases.json", val_labels,
        out / "validation-answer-key.sealed")
    print("VALIDATION_KEY_HEX=" + key_hex)

    train_counts, _ = ct.check_quotas(
        [e for e in CASES if e["cid"] in train_ids])
    val_counts, _ = ct.check_quotas(
        [e for e in CASES if e["cid"] not in train_ids])
    manifest = {
        "set_id": "RC31-PROOF-DEV-CORPUS",
        "task_id": "NAV-EXPLORE-RC3_1-PROOF-SEMANTICS-REPAIR",
        "total_cases": 184,
        "train_n": len(train_labeled),
        "validation_n": 60,
        "split_rule": "deterministic: random.Random(20260904).shuffle over case_ids sorted ascending; first 60 -> VALIDATION, rest TRAIN; labels sealed before implementation",
        "split_seed": 20260904,
        "validation_case_ids": sorted(validation_ids),
        "validation_atoms_sealed": True,
        "seal_schema": 2,
        "relation_balance": balance,
        "compound_cases": compound_n,
        "quota_counts_total": counts,
        "quota_counts_train": train_counts,
        "quota_counts_validation": val_counts,
        "novelty_checked_against": "RC3G-HOLDOUT-V1 generalization-cases.json (burned)",
        "novelty_flagged": 0,
        "sha256": {
            "train-cases.json": ct.sha256_file(out / "train-cases.json"),
            "validation-cases.json": ct.sha256_file(
                out / "validation-cases.json"),
            "validation-answer-key.sealed": ct.sha256_file(
                out / "validation-answer-key.sealed"),
        },
    }
    (out / "corpus-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "sha256"},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
