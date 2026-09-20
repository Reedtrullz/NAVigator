#!/usr/bin/env python3
"""Author wave 4 blind-set candidates (RC1B-0168..0193): genuine insufficiency, partial compounds, near-miss numerics."""
import json
import pathlib

ROOT = pathlib.Path("/Users/reidar/Projectos/NAV Explore")
OUT = ROOT / "evaluation/semantic-judge/blind-recertification/RC1-set/candidates/RC1B-candidates-w4-insufficiency.json"


def line(fname, n):
    return (ROOT / fname).read_text(encoding="utf-8").splitlines()[n - 1]


def s(kb_ref, n, sid="SRC1"):
    return {"source_id": sid, "kb_ref": kb_ref, "text": line(kb_ref, n)}


HULL = "69-kunnskapshullregister.md"
FOK = "51-familieokonomi-etter-samlivsbrudd.md"

CASES = [
    {"case_id": "RC1B-0168", "claim": "Mottatt barnebidrag er skattepliktig for mottakeren, og betaleren far skattefradrag for bidraget.",
     "sources": [s(HULL, 40)]},
    {"case_id": "RC1B-0169", "claim": "Etterbetalt barnebidrag for et barn pa 19 ar er ikke skattepliktig, fordi Skatteetaten har verifisert dette separat.",
     "sources": [s(HULL, 40), s(HULL, 41, "SRC2")]},
    {"case_id": "RC1B-0170", "claim": "Det er klagefrist pa tre uker for vedtak om saerbidrag.",
     "sources": [s("50-bidragsforskudd-og-innkreving.md", 170)]},
    {"case_id": "RC1B-0171", "claim": "Det finnes en nasjonal tallfestet ventetid for familievernkontorene i Norge.",
     "sources": [s("46-kildedokumentasjon-samlivsbrudd-familievern-barnevern.md", 77)]},
    {"case_id": "RC1B-0172", "claim": "Ventetiden for samtale ved familievernkontoret er nasjonalt tallfestet til seks uker.",
     "sources": [s("46-kildedokumentasjon-samlivsbrudd-familievern-barnevern.md", 77)]},
    {"case_id": "RC1B-0173", "claim": "Familievernkontorenes gruppetilbud har samme innhold og utvalg pa alle kontor.",
     "sources": [s("33-familievern-i-dybden.md", 47)]},
    {"case_id": "RC1B-0174", "claim": "PPT-utredning har en lovbestemt saksbehandlingsfrist pa seks uker.",
     "sources": [s("28-ppt-i-dybden.md", 126)]},
    {"case_id": "RC1B-0175", "claim": "Det finnes en lovbestemt saksbehandlingsfrist for PPT-utredning, og de kommunale fristene er lik over hele landet.",
     "sources": [s("28-ppt-i-dybden.md", 126)]},
    {"case_id": "RC1B-0176", "claim": "En enslig forsorger med barn under 3 ar har rett til omsorgspenger i 100 dager i 2026.",
     "sources": [s(FOK, 41)]},
    {"case_id": "RC1B-0177", "claim": "Aleneomsorg gir utvidet rett til omsorgspenger, og den eksakte dagsgrensen for 2026 er verifisert i kunnskapbasen.",
     "sources": [s(FOK, 41)]},
    {"case_id": "RC1B-0178", "claim": "Smabarnstillegg deles mellom foreldrene ved delt fast bosted pa samme mate som delt barnetrygd.",
     "sources": [s(FOK, 128)]},
    {"case_id": "RC1B-0179", "claim": "Delt barnetrygd er verifisert i kildene, og deling av smabarnstillegg ved delt fast bosted er ogsa fullt verifisert.",
     "sources": [s(FOK, 128)]},
    {"case_id": "RC1B-0180", "claim": "Den ovre inntektsgrensen for bostotte er 28 241 kroner i maneden for alle kommuner.",
     "sources": [s("55-bostotte-i-dybden.md", 80)]},
    {"case_id": "RC1B-0181", "claim": "Den ovre inntektsgrensen for bostotte er lik for hele landet og avhenger bare av antall personer i husstanden.",
     "sources": [s("55-bostotte-i-dybden.md", 80)]},
    {"case_id": "RC1B-0182", "claim": "Boutgiftstaket i bostottebehandlingen er fastsatt til 12 000 kroner i maneden over hele landet.",
     "sources": [s("55-bostotte-i-dybden.md", 35)]},
    {"case_id": "RC1B-0183", "claim": "BUP-ventetiden per enhet i Helse Midt-Norge er verifisert i kunnskapbasen.",
     "sources": [s("24-kildedokumentasjon-bup-og-habu.md", 332)]},
    {"case_id": "RC1B-0184", "claim": "St. Olav vurderer inntak til BUP innen 10 dager, og de fullstendige ventetidene per enhet i Helse Midt-Norge er dokumentert.",
     "sources": [s("24-kildedokumentasjon-bup-og-habu.md", 332)]},
    {"case_id": "RC1B-0185", "claim": "Bufdirs rolle knyttet til barne- og ungdomshabilitering, for eksempel NPU-rutiner, er verifisert i kunnskapbasen.",
     "sources": [s("24-kildedokumentasjon-bup-og-habu.md", 330)]},
    {"case_id": "RC1B-0186", "claim": "Tiller DPS og de andre DPS-enhetene i Trondheim har verifiserte ansvarsomrader i kunnskapbasen.",
     "sources": [s("70-lokalt/trondheim/02-psykisk-helse.md", 49)]},
    {"case_id": "RC1B-0187", "claim": "Trondheim familievernkontor garanterer meklingstime innen tre uker fra bestilling.",
     "sources": [s("70-lokalt/trondheim/05-familievern-barnevern.md", 15)]},
    {"case_id": "RC1B-0188", "claim": "Trondheim familievernkontor har et mal om meklingstime innen tre uker fra bestilling, men dette er ikke en garanti.",
     "sources": [s("70-lokalt/trondheim/05-familievern-barnevern.md", 15)]},
    {"case_id": "RC1B-0189", "claim": "Overgangsstonad kan kombineres med AAP, men stonaden avkortes, og ved sykdom uten sykemelding krever NAV legeerklaering pa egen sykdom.",
     "sources": [s(HULL, 49)]},
    {"case_id": "RC1B-0190", "claim": "Folketrygdloven § 15-4 bruker ordlyden 'minst 60 prosent av den daglige omsorgen', og NAVs brukerformulering er identisk med lovteksten.",
     "sources": [s(HULL, 76)]},
    {"case_id": "RC1B-0191", "claim": "Regelen om at du ikke har rett til overgangsstonad dersom andre kan ta vare pa barnet, finnes i gjeldende lov eller forskrift.",
     "sources": [s(HULL, 76)]},
    {"case_id": "RC1B-0192", "claim": "Trygderettens praksis for kravet om saerlig tilsyn etter § 15-5 fjerde ledd er hentet fra praksisdatabaser og fullt verifisert, inkludert barn under utredning uten diagnose.",
     "sources": [s(HULL, 84), s(HULL, 88, "SRC2")]},
    {"case_id": "RC1B-0193", "claim": "Kunnskapbasen fastslar hvilket regelverk som gjelder nar en mottaker i overgangsgruppen far nytt barn i 2027 og sokrer pa nytt.",
     "sources": [s(HULL, 94), s(HULL, 98, "SRC2")]},
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"candidates": CASES}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"wrote {len(CASES)} cases to {OUT}")
