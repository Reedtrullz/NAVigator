#!/usr/bin/env python3
"""Author wave 3 blind-set candidates (RC1B-0144..0167) from verbatim KB excerpts."""
import json
import pathlib

ROOT = pathlib.Path("/Users/reidar/Projectos/NAV Explore")
OUT = ROOT / "evaluation/semantic-judge/blind-recertification/RC1-set/candidates/RC1B-candidates-w3-bolig-skole-hull.json"


def line(fname, n):
    lines = (ROOT / fname).read_text(encoding="utf-8").splitlines()
    return lines[n - 1]


def lines(fname, a, b):
    ls = (ROOT / fname).read_text(encoding="utf-8").splitlines()
    return "\n".join(ls[a - 1 : b])


def s(kb_ref, text):
    return {"kb_ref": kb_ref, "source_id": "SRC1", "text": text}


KB = {
    "dep_konto": line("58-boligtrygghet-depositum-utkastelse.md", 10),
    "dep_komm": line("58-boligtrygghet-depositum-utkastelse.md", 12),
    "dep_garanti": line("58-boligtrygghet-depositum-utkastelse.md", 14),
    "dep_beslutter": line("58-boligtrygghet-depositum-utkastelse.md", 16),
    "startlan_egenkapital": line("60-radgivning-startlan-og-gjeld.md", 21),
    "startlan_soknad": line("60-radgivning-startlan-og-gjeld.md", 25),
    "startlan_ikke_akutt": line("60-radgivning-startlan-og-gjeld.md", 26),
    "gjeld_hull": line("60-radgivning-startlan-og-gjeld.md", 38),
    "botilbud_plikt": line("59-midlertidig-botilbud-og-kommunal-bolig.md", 12),
    "botilbud_venner": line("59-midlertidig-botilbud-og-kommunal-bolig.md", 14),
    "botilbud_forsvarlig": line("59-midlertidig-botilbud-og-kommunal-bolig.md", 15),
    "botilbud_klage": line("59-midlertidig-botilbud-og-kommunal-bolig.md", 18),
    "nodhjelp_eksempler": lines("57-nodhjelp-og-akutte-situasjoner.md", 11, 13),
    "nodhjelp_grense": line("57-nodhjelp-og-akutte-situasjoner.md", 16),
    "nodhjelp_strom": line("57-nodhjelp-og-akutte-situasjoner.md", 29),
    "fravar_dag1": line("30-skolefravar-og-skolevegring.md", 12),
    "fravar_tidsbestemt": line("30-skolefravar-og-skolevegring.md", 15),
    "fravar_eskaler": line("30-skolefravar-og-skolevegring.md", 41),
    "fravar_bup": line("30-skolefravar-og-skolevegring.md", 41),
    "sh_kan": line("31-skolehelsetjenesten-i-dybden.md", 22),
    "sh_ikke": line("31-skolehelsetjenesten-i-dybden.md", 24),
    "sh_pbl": line("31-skolehelsetjenesten-i-dybden.md", 38),
    "hfu_nasjonal": line("25-kommunale-psykiske-tjenester-barn-unge.md", 75),
    "hfu_trd": line("70-lokalt/trondheim/01-barn-og-familie.md", 21),
    "henvisningsrett": line("25-kommunale-psykiske-tjenester-barn-unge.md", 31),
    "hull_15_4": line("69-kunnskapshullregister.md", 67),
    "hull_trygderetten": lines("69-kunnskapshullregister.md", 84, 85),
    "hull_nytt_barn": lines("69-kunnskapshullregister.md", 94, 95),
}

CASES = [
    {"case_id": "RC1B-0144", "claim": "Etter samlivsbrudd kan depositum plasseres pa vanlig depositumskonto, og belopet er som utgangspunkt inntil seks maneders leie etter husleieloven § 3-8.",
     "sources": [s("58-boligtrygghet-depositum-utkastelse.md", KB["dep_konto"])]},
    {"case_id": "RC1B-0145", "claim": "Alle kommuner er pliktige til a tilby kommunalt depositumslan til leietakere som ikke har egne midler til depositum.",
     "sources": [s("58-boligtrygghet-depositum-utkastelse.md", KB["dep_komm"])]},
    {"case_id": "RC1B-0146", "claim": "Nav-Kontoret gir alltid garanti for depositum nar du inngar leiekontrakt og ikke kan skaffe penger selv; dette er en automatisk rett.",
     "sources": [s("58-boligtrygghet-depositum-utkastelse.md", KB["dep_garanti"])]},
    {"case_id": "RC1B-0147", "claim": "Det er Nav-kontoret (sosialhjelp) eller kommunens boligkontor som beslutter depositumsspor, og ved utloser garanti kan kommunen kreve refusjon og innkreve som annen gjeld.",
     "sources": [s("58-boligtrygghet-depositum-utkastelse.md", KB["dep_beslutter"])]},
    {"case_id": "RC1B-0148", "claim": "For ordinrt startlan fra kommunen er det ikke krav om egenkapital, men inntekten ma dekke lanet og andre nodvendige utgifter.",
     "sources": [s("60-radgivning-startlan-og-gjeld.md", KB["startlan_egenkapital"])]},
    {"case_id": "RC1B-0149", "claim": "Startlan kan brukes som akutthjelp for a dekke neste maneds husleie etter et samlivsbrudd.",
     "sources": [s("60-radgivning-startlan-og-gjeld.md", KB["startlan_ikke_akutt"])]},
    {"case_id": "RC1B-0150", "claim": "Du kan sokr startlan til kommuner du ikke bor i, men mange kommuner gir bare lan til bosatte, og det er kommunalt skjonn uten rett til startlan.",
     "sources": [s("60-radgivning-startlan-og-gjeld.md", KB["startlan_soknad"])]},
    {"case_id": "RC1B-0151", "claim": "Gjeldsordningslovens paragrafnummer og naverende innfrielseperiode er verifisert i kunnskapbasen, og innfrielseperioden er normalt 3 ar.",
     "sources": [s("60-radgivning-startlan-og-gjeld.md", KB["gjeld_hull"])]},
    {"case_id": "RC1B-0152", "claim": "Etter sosialtjenesteloven § 27 er Nav forpliktet til a finne et midlertidig botilbud hvis du ikke har et sted a sove og oppholde seg det neste dognet, ogsa nar du midlertidig bor hos venner eller familie.",
     "sources": [s("59-midlertidig-botilbud-og-kommunal-bolig.md", KB["botilbud_plikt"]), s("59-midlertidig-botilbud-og-kommunal-bolig.md", KB["botilbud_venner"])]},
    {"case_id": "RC1B-0153", "claim": "Ved § 27-situasjon kan Nav-kontoret sette deg i vanlig soknadsk i stedet for a finne et forsvarlig botilbud for na.",
     "sources": [s("59-midlertidig-botilbud-og-kommunal-bolig.md", KB["botilbud_forsvarlig"])]},
    {"case_id": "RC1B-0154", "claim": "Vedtak om midlertidig botilbud kan klages, og klagefristen er tre uker.",
     "sources": [s("59-midlertidig-botilbud-og-kommunal-bolig.md", KB["botilbud_klage"])]},
    {"case_id": "RC1B-0155", "claim": "Nodhjelp kan dekke mat, reiseutgifter og regninger som hindrer at nodvendige tjenester som strom blir stengt.",
     "sources": [s("57-nodhjelp-og-akutte-situasjoner.md", KB["nodhjelp_eksempler"])]},
    {"case_id": "RC1B-0156", "claim": "Det finnes en lovfestet belopsgrense for nodhjelp pa 6000 kroner.",
     "sources": [s("57-nodhjelp-og-akutte-situasjoner.md", KB["nodhjelp_grense"])]},
    {"case_id": "RC1B-0157", "claim": "Stengingsvarsel frastromselskapet kan behandles som nodssituasjon, og regninger som hindrer at strommen stenges kan dekkes som nodhjelp.",
     "sources": [s("57-nodhjelp-og-akutte-situasjoner.md", KB["nodhjelp_strom"])]},
    {"case_id": "RC1B-0158", "claim": "Skolen skal folge opp elevfravar fra forste dagen eleven er borte, ikke bare hoyt eller langvarig fravar.",
     "sources": [s("30-skolefravar-og-skolevegring.md", KB["fravar_dag1"])]},
    {"case_id": "RC1B-0159", "claim": "I videregaende opplaring kan fravar over 10 prosent av arstimetallet i et fag gi tap av rett til vurdering med karakter, og fravar fores pa vitnemal.",
     "sources": [s("30-skolefravar-og-skolevegring.md", KB["fravar_tidsbestemt"])]},
    {"case_id": "RC1B-0160", "claim": "Ved omfattende skolefravar kobles PPT inn ved antatt faglig eller psykososial arsak, og BUP kan henvises av fastlege eller kommunalt psykisk helsetilbud.",
     "sources": [s("30-skolefravar-og-skolevegring.md", KB["fravar_eskaler"]), s("30-skolefravar-og-skolevegring.md", KB["fravar_bup"])]},
    {"case_id": "RC1B-0161", "claim": "Skolehelsetjenesten yter psykoterapi, stiller diagnoser og skriver ut legemidler ved angst og depresjon.",
     "sources": [s("31-skolehelsetjenesten-i-dybden.md", KB["sh_ikke"]), s("31-skolehelsetjenesten-i-dybden.md", KB["sh_kan"])]},
    {"case_id": "RC1B-0162", "claim": "En 13-arig elev kan samtykke til helsehjelp i skolehelsetjenesten i forhold foreldrene ikke er informert om.",
     "sources": [s("31-skolehelsetjenesten-i-dybden.md", KB["sh_pbl"])]},
    {"case_id": "RC1B-0163", "claim": "Alle kommuner skal ha et gratis HFU-tilbud for ungdom opptil 20 ar, og HFU Heimdal i Trondheim folger samme aldersgrense pa 13-21 ar.",
     "sources": [s("25-kommunale-psykiske-tjenester-barn-unge.md", KB["hfu_nasjonal"]), s("70-lokalt/trondheim/01-barn-og-familie.md", KB["hfu_trd"])]},
    {"case_id": "RC1B-0164", "claim": "Fastlegen, psykolog i kommunen og barnevernsleder har henvisningsrett til psykisk helsevern for barn og unge, men dette gjelder psykologer, ikke alle kommunale ansatte.",
     "sources": [s("25-kommunale-psykiske-tjenester-barn-unge.md", KB["henvisningsrett"])]},
    {"case_id": "RC1B-0165", "claim": "Lovendringen av folketrygdloven § 15-4 er vedtatt, og den har tradd i kraft per 30.08.2026.",
     "sources": [s("69-kunnskapshullregister.md", KB["hull_15_4"])]},
    {"case_id": "RC1B-0166", "claim": "Det er ikke verifisert hvordan Trygderetten vurderer kravet om saerlig tilsyn etter § 15-5 fjerde ledd, inkludert barn under utredning uten diagnose.",
     "sources": [s("69-kunnskapshullregister.md", KB["hull_trygderetten"])]},
    {"case_id": "RC1B-0167", "claim": "Regelverket og betingelsene nar en mottaker i overgangsgruppen far nytt barn og sokrer pa nytt, er fullt verifisert i kunnskapbasen.",
     "sources": [s("69-kunnskapshullregister.md", KB["hull_nytt_barn"])]},
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"candidates": CASES}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"wrote {len(CASES)} cases to {OUT}")
