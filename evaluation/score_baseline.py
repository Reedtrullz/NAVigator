#!/usr/bin/env python3
"""Baseline scorer: checks golden routes in expected-routing.json against the
knowledge base. Produces baseline-results.json with per-dimension scores.

Usage: python3 evaluation/score_baseline.py [output.json]
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def norm(s):
    s = s.lower()
    s = s.replace("ø", "o").replace("æ", "ae").replace("å", "a")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def load_corpus():
    corpus = {}
    for dirpath, _dirs, files in os.walk("."):
        if ".git" in dirpath or "node_modules" in dirpath:
            continue
        for f in files:
            if f.endswith((".md", ".json")):
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, ".")
                try:
                    corpus[rel] = norm(open(p, encoding="utf-8", errors="ignore").read())
                except OSError:
                    pass
    return corpus


CORPUS = load_corpus()


def resolve_source(src):
    src = src.strip()
    if src in CORPUS:
        return src
    base = src.split(" (")[0].strip().split(" ")[0].strip()
    if base in CORPUS:
        return base
    # Trondheim-style refs like "04-bup-habu (trondheim)" resolve to the
    # local folder file with the same numeric prefix.
    mref = re.match(r"^([0-9]+)-([a-z0-9-]+)$", base)
    if mref:
        num, slug = mref.groups()
        for c in CORPUS:
            if c.startswith("70-lokalt/") and os.path.basename(c).startswith(num + "-"):
                return c
            if os.path.basename(c).startswith(num + "-" + slug):
                return c
    if "/" in base:
        tail = base.rsplit("/", 1)[-1]
        dirpart = base.rsplit("/", 1)[0]
        mnum = re.match(r"^([0-9]+)(?:-[a-z0-9-]+)?(?:\.[a-z]+)?$", tail)
        if mnum:
            for c in CORPUS:
                if c.startswith(dirpart + "/") and os.path.basename(c).startswith(mnum.group(1) + "-"):
                    return c
        for c in CORPUS:
            if c.endswith("/" + tail) or os.path.basename(c) == tail:
                return c
    # numeric file references like "54"
    m = re.match(r"^([0-9]+)$", src)
    if m:
        for c in CORPUS:
            if os.path.basename(c).startswith(m.group(1) + "-") and c.endswith(".md"):
                return c
    if base.endswith(".json"):
        for c in CORPUS:
            if os.path.basename(c) == base:
                return c
    return None


def find(terms, sources):
    for t in terms:
        for s in sources:
            r = resolve_source(s)
            if r and t in CORPUS.get(r, ""):
                return True
    return False


# Per-scenario evidence queries: (dim_tag, topic_label, terms, extra_sources)
QUERIES = {
    "S01": [("faglig", "mekling-inngang", ["familievernkontor", "mekling"], None),
            ("juridisk", "bosted-folkeregister", ["bosted", "folkeregister"], None),
            ("faglig", "overgangsstonad-vilkar", ["alene"], ["63", "64"])],
    "S02": [("juridisk", "delt-bosted-vilkar", ["delt fast bosted", "skriftlig avtale"], ["54"]),
            ("faglig", "sats-ordinar", ["1 006"], ["54"]),
            ("faglig", "sats-utvidet", ["1 286"], ["54"])],
    "S03": [("faglig", "sats-delt", ["1 006"], ["54"]),
            ("faglig", "utvidet-halvsats", ["1 286"], ["54"]),
            ("juridisk", "avtale-krav", ["skriftlig avtale"], ["54"])],
    "S04": [("juridisk", "hovedregel-14mnd", ["14 maneder"], ["63", "64"]),
            ("faglig", "saerlig-tilsyn", ["saerlig tilsyn"], ["64", "65"]),
            ("faglig", "dokumentasjon-aleneomsorg", ["dokumentasjon"], ["65", "67"])],
    "S05": [("faglig", "mekling-bestilling", ["mekling"], ["34"]),
            ("juridisk", "obligatorisk-mekling", ["obligatorisk"], ["34", "33"])],
    "S06": [("faglig", "innkreving", ["innkreving"], ["48", "50"]),
            ("faglig", "bidragsforskudd", ["forskudd"], ["50", "48"]),
            ("faglig", "fastsetting", ["fastsetting"], ["48", "50"])],
    "S07": [("juridisk", "flytting-samtykke", ["flytting"], ["35", "37"]),
            ("juridisk", "samtykke-regel", ["samtykke"], ["41"]),
            ("juridisk", "manedsfrist-flytting", ["maneder", "flytting"], ["35", "37"])],
    "S08": [("faglig", "mekling", ["mekling"], ["33", "34"]),
            ("faglig", "foreldretvist", ["foreldretvist"], ["37"])],
    "S09": [("faglig", "normalreaksjon", ["normal"], ["16-livssituasjoner/04-barns-psykiske-helse.md", "32", "25"]),
            ("faglig", "foreldrestotte", ["foreldre"], ["25", "32"])],
    "S10": [("faglig", "fastlege-inngang", ["fastlege"], ["26", "25"]),
            ("faglig", "bup-henvisning", ["henvisning"], ["24", "26"]),
            ("faglig", "varighet-alvorlighet", ["alvorlig"], ["26", "24"])],
    "S11": [("faglig", "trygghet-rutiner", ["foreldresamtale"], ["70-lokalt/trondheim/08-mari-case.md"]),
            ("lokal", "trondheimshjelpa", ["trondheimshjelpa"], None)],
    "S12": [("faglig", "fastlege", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md", "26"]),
            ("faglig", "rph-tilbud", ["rask psykisk helsehjelp"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md", "26"]),
            ("faglig", "dps-henvisning", ["dps"], ["26", "16-livssituasjoner/05-voksnes-psykiske-helse.md"])],
    "S13": [("lokal", "avlastning-stottekontakt", ["avlastning"], ["70-lokalt/trondheim/01-barn-og-familie.md"]),
            ("faglig", "hjelpelinje", ["116 123"], ["70-lokalt/trondheim/08-mari-case.md", "26"]),
            ("faglig", "barnevern-ikke-automatisk", ["bekymringsmelding"], ["38", "40"])],
    "S14": [("faglig", "helsestasjon-05", ["helsestasjon"], ["25", "26"]),
            ("faglig", "sovnproblemer", ["sovn"], ["25", "26"])],
    "S15": [("lokal", "trondheimshjelpa", ["trondheimshjelpa"], None),
            ("lokal", "alder-24", ["ungdom"], None),
            ("faglig", "skolehelse", ["skolehelse"], ["25", "70-lokalt/trondheim/02-psykisk-helse.md"])],
    "S16": [("faglig", "egen-behandling", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md"]),
            ("faglig", "barnevern-grense", ["omsorgssvikt"], ["38", "39", "40"])],
    "S17": [("faglig", "kontaktlarer", ["kontaktlarer"], ["29", "32", "30"]),
            ("faglig", "skolehelse", ["skolehelse"], ["31", "32"]),
            ("faglig", "fravar-kartlegging", ["fravar"], ["30", "32"]),
            ("faglig", "ppt-rolle", ["ppt"], ["28"])],
    "S18": [("faglig", "ppt-kartlegging", ["ppt"], ["28", "32"]),
            ("juridisk", "henvisning-underskrift", ["underskriv"], ["70-lokalt/trondheim/04-bup-habu.md", "24", "25"]),
            ("faglig", "ikke-diagnose", ["diagnose"], ["28", "65"])],
    "S19": [("faglig", "dysleksi-ppt", ["lesing"], ["28", "29"]),
            ("faglig", "ppt-tilrettelegging", ["ppt"], ["28", "29"])],
    "S20": [("juridisk", "henvisning-bup", ["henvisning"], ["70-lokalt/trondheim/04-bup-habu.md", "24"]),
            ("faglig", "habu-grense", ["habu"], ["24", "70-lokalt/trondheim/04-bup-habu.md"]),
            ("faglig", "ppt-parallelt", ["ppt"], ["28"])],
    "S21": [("faglig", "habu-lege", ["habu"], ["70-lokalt/trondheim/04-bup-habu.md"]),
            ("lokal", "avlastning", ["avlastning"], ["70-lokalt/trondheim/01-barn-og-familie.md"]),
            ("faglig", "ppt", ["ppt"], ["28"])],
    "S22": [("faglig", "habu", ["habu"], ["70-lokalt/trondheim/04-bup-habu.md"]),
            ("faglig", "ito-skole", ["tilrettelagt"], ["29"]),
            ("faglig", "ppt", ["ppt"], ["28", "29"])],
    "S23": [("juridisk", "fra-12-selvkontakt", ["12 ar"], ["31", "41"]),
            ("juridisk", "samtykke-under-16", ["samtykke"], ["41"])],
    "S24": [("juridisk", "samtykke-16-18", ["16", "samtykke"], ["41", "31"]),
            ("faglig", "bup-henvisning", ["henvisning"], ["24", "31"])],
    "S25": [("juridisk", "pbl-4-4", ["4 4"], ["41", "25", "24"]),
            ("juridisk", "samrad", ["samrad"], ["25", "70-lokalt/trondheim/04-bup-habu.md", "24"])],
    "S26": [("juridisk", "hovedregel-14mnd", ["14 maneder"], ["63", "64"]),
            ("faglig", "saerlig-tilsyn", ["tilsyn"], ["64", "65"]),
            ("faglig", "ikke-diagnose", ["diagnose"], ["65", "67"])],
    "S27": [("faglig", "nodhjelp", ["nodhjelp"], ["57", "56"]),
            ("lokal", "hv-kontor", ["velferdskontor"], ["70-lokalt/trondheim/06-nav-okonomi-bolig.md", "57"]),
            ("faglig", "nav-telefon", ["55 55 33 33"], ["57"])],
    "S28": [("faglig", "strom-nod", ["strom"], ["57"]),
            ("faglig", "sosialhjelp", ["sosialhjelp"], ["56", "57"]),
            ("faglig", "bostotte", ["bostotte"], ["55"])],
    "S29": [("juridisk", "protest-frist", ["protest"], ["58", "57"]),
            ("faglig", "sosialtjenesten", ["sosialtjenesten"], ["58", "56"]),
            ("faglig", "bostotte", ["bostotte"], ["55"])],
    "S30": [("juridisk", "uke-varsel", ["to uker"], ["58"]),
            ("faglig", "sosialtjenesten", ["sosialtjenesten"], ["58"])],
    "S31": [("faglig", "depositum-garanti", ["garanti"], ["58"]),
            ("faglig", "ikke-automatisk", ["ikke"], ["58"])],
    "S32": [("faglig", "midlertidig-botilbud", ["botilbud"], ["59", "57"]),
            ("juridisk", "sotjl-plikt", ["sosialtjenesteloven"], ["59", "57"])],
    "S33": [("faglig", "sok-frist", ["25"], ["55"]),
            ("faglig", "beregning", ["beregning"], ["55"])],
    "S34": [("faglig", "innkreving", ["innkreving"], ["50", "48"]),
            ("faglig", "forskudd", ["forskudd"], ["50", "48"])],
    "S35": [("juridisk", "sokt-for-1-7", ["1 7"], ["68", "63"]),
            ("juridisk", "overgangsforskrift", ["1361"], ["68"]),
            ("juridisk", "gamle-regler", ["gamle"], ["63", "68"])],
    "S36": [("juridisk", "nye-regler", ["nye"], ["63", "68"]),
            ("faglig", "dokumentasjon", ["dokumentasjon"], ["64", "68"])],
    "S37": [("faglig", "barnetilsyn-64prosent", ["barnetilsyn"], ["64", "66", "68"]),
            ("faglig", "aap-samspill", ["aap"], ["64", "66"]),
            ("juridisk", "hovedperiode", ["14 maneder"], ["64"])],
    "S38": [("faglig", "fastlege", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md", "26"]),
            ("faglig", "lavterskel-varierer", ["varierer"], ["25", "26"])],
    "S39": [("lokal", "rph-trondheim", ["rask psykisk helsehjelp"], None),
            ("lokal", "helsami", ["helsami"], None)],
    "S40": [("faglig", "fastlege", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md", "26"]),
            ("faglig", "dps", ["dps"], ["26"])],
    "S41": [("faglig", "fastlege-vurdering", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md"]),
            ("faglig", "rph-dps", ["rask psykisk"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md", "26"])],
    "S42": [("lokal", "rph-alder", ["rask psykisk"], None),
            ("faglig", "fastlege", ["fastlege"], ["16-livssituasjoner/05-voksnes-psykiske-helse.md"])],
    "S43": [("faglig", "akutt-ruting", ["116 117", "113"], ["57", "42"]),
            ("faglig", "barnesikkerhet", ["trygg voksen", "forsvarlig omsorg"], ["57", "42"]),
            ("juridisk", "parorende-plikt", ["10 a", "parorende"], ["57", "18"]),
            ("juridisk", "akuttvedtak", ["uten omsorg", "akuttvedtak"], ["38", "57"]),
            ("faglig", "hjelpelinje", ["116 123"], ["42", "26"])],
    "S44": [("faglig", "113-legevakt", ["113"], ["70-lokalt/trondheim/07-akutt-og-sikkerhet.md", "42"]),
            ("faglig", "akuttenhet", ["akuttenhet"], ["70-lokalt/trondheim/07-akutt-og-sikkerhet.md"]),
            ("faglig", "barn-ikke-alene", ["barnet"], ["70-lokalt/trondheim/07-akutt-og-sikkerhet.md", "42"])],
    "S45": [("lokal", "akuttenheten", ["akuttenhet"], ["70-lokalt/trondheim/04-bup-habu.md", "70-lokalt/trondheim/07-akutt-og-sikkerhet.md"]),
            ("faglig", "legevakt", ["legevakt"], ["70-lokalt/trondheim/07-akutt-og-sikkerhet.md"])],
    "S46": [("faglig", "112-politi", ["112"], ["42", "45"]),
            ("faglig", "krisesenter", ["krisesenter"], ["42", "45"])],
    "S47": [("faglig", "politi", ["politi"], ["42"]),
            ("faglig", "barnehus", ["barnehus"], ["17", "42"]),
            ("faglig", "alarmtelefon", ["116 111"], ["42", "40", "26"])],
    "S48": [("faglig", "midlertidig-botilbud", ["botilbud"], ["59", "57"]),
            ("faglig", "kommune-akutt", ["kommunen"], ["57", "59"]),
            ("faglig", "barnevern-sikkerhet", ["barnevern"], ["40", "57"])],
}


def corpus_for_sources(sources):
    hay = ""
    for s in sources:
        r = resolve_source(s)
        if r:
            hay += " " + CORPUS.get(r, "")
    return hay


def evaluate():
    scenarios = json.load(open("evaluation/scenarios.json"))["scenarios"]
    routes = json.load(open("evaluation/expected-routing.json"))["routes"]
    results = []
    for s in scenarios:
        sid = s["id"]
        r = routes[sid]
        srcs = r.get("sources", [])
        hay = corpus_for_sources(srcs)
        topics = []
        for dim, label, terms, extra in QUERIES.get(sid, []):
            found = find(terms, srcs + (extra or []))
            topics.append({"dim": dim, "topic": label, "terms": terms, "pass": found})
        # route steps evidence: first and second actor words present in corpus
        for key in ("first", "second"):
            actor = r.get(key, "")
            stop = {"kontakt", "soknad", "sok", "ring", "oppsoek", "oppsok", "avklare", "hjelp", "sjekk",
                    "dokumentasjon", "ikke", "kan", "skal", "ved", "for", "dersom", "samme",
                    "uten", "etter", "gjelder", "dag", "var", "med"}
            words = []
            for w in re.findall(r"[a-z0-9]{3,}", norm(actor)):
                if w not in stop and w not in words:
                    words.append(w)
                if len(words) == 3:
                    break
            ok = any(w in hay for w in words) if words else False
            topics.append({"dim": "riktig_tjeneste", "topic": f"{key}_actor_evidence", "terms": words, "pass": ok})
        # forbidden structural checks
        forbidden_ok = True
        first_norm = norm(r.get("first", ""))
        if r.get("safety_critical"):
            if not re.search(r"112|113|116 117|116 123|legevakt|akutt|politi|barnehus", first_norm):
                forbidden_ok = False
        if sid in ("S09", "S11", "S14", "S15") and re.search(r"bup", first_norm):
            forbidden_ok = False
        if sid in ("S27", "S32", "S48") and re.search(r"bostotte", first_norm):
            forbidden_ok = False
        if sid == "S38" and re.search(r"trondheimshjelpa|helsami", first_norm):
            forbidden_ok = False
        if sid == "S46" and re.search(r"familievern", first_norm):
            forbidden_ok = False
        if sid == "S47" and re.search(r"lavterskel|samtale forst", first_norm):
            forbidden_ok = False
        if sid == "S45" and re.search(r"poliklinikk", first_norm):
            forbidden_ok = False
        # dimension scores
        def score(dim):
            rel = [t for t in topics if t["dim"] == dim]
            if not rel:
                return 5, []
            passed = sum(1 for t in rel if t["pass"])
            ratio = passed / len(rel)
            sc = round(ratio * 5)
            if sc == 0 and ratio > 0:
                sc = 1
            return max(sc, 1 if ratio > 0 else 0), rel

        fag, _ = score("faglig")
        jur, _ = score("juridisk")
        tj, _ = score("riktig_tjeneste")
        lok, _ = score("lokal")
        rekkefolge = 5
        if r.get("safety_critical") and not re.search(r"112|113|116 117|116 123|legevakt|akutt|politi|barnehus", first_norm):
            rekkefolge = 2
        if r.get("safety_critical") and (not r.get("not_relevant") or not r.get("forbidden")):
            rekkefolge = min(rekkefolge, 4)
        usikkerhet = 5 if r.get("forbidden") else 3
        if any(t["pass"] for t in topics) is False:
            usikkerhet = 2
        eskalering = 5
        if not r.get("not_relevant"):
            eskalering = 4
        if not forbidden_ok:
            eskalering = min(eskalering, 2)
        dokumentasjon = 5
        missing_sources = [x for x in srcs if not resolve_source(x)]
        if missing_sources:
            dokumentasjon = 3
        sikkerhet = 5
        if r.get("safety_critical"):
            acute = re.search(r"112|113|116 117|116 123|legevakt|akutt|politi|barnehus", first_norm)
            sikkerhet = 5 if acute else 2
        dims = {
            "faglig_korrekthet": fag,
            "juridisk_korrekthet": jur,
            "riktig_tjeneste": tj,
            "riktig_rekkefolge": rekkefolge,
            "lokal_korrekthet": lok,
            "usikkerhetshandtering": usikkerhet,
            "unngar_unodvendig_eskalering": eskalering,
            "dokumentasjon": dokumentasjon,
            "sikkerhet": sikkerhet,
        }
        forbidden_hit = not forbidden_ok
        if forbidden_hit:
            verdict = "FEILET"
        elif any(v <= 2 for v in dims.values()):
            verdict = "FEILET"
        elif any(v == 3 for v in dims.values()) or any(not t["pass"] for t in topics):
            verdict = "DELVIS"
        else:
            verdict = "BESTATT"
        results.append({
            "id": sid,
            "title": s["title"],
            "category": s["category"],
            "location": s["location"],
            "safety_critical": r.get("safety_critical", False),
            "verdict": verdict,
            "dimensions": dims,
            "forbidden_structure_ok": forbidden_ok,
            "missing_sources": missing_sources,
            "topics": topics,
        })
    out = {
        "meta": {
            "generated": "2026-08-30",
            "tool": "evaluation/score_baseline.py",
            "pass_rule": "BESTATT: alle dimensjoner >=4 og alle topics pass; DELVIS: ingen <=2 men >=1 topic fail eller 3-er; FEILET: dimensjon <=2 eller forbidden-strukturell treff.",
        },
        "results": results,
    }
    path = sys.argv[1] if len(sys.argv) > 1 else "evaluation/baseline-results.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=2)
    # summary
    verdicts = {"BESTATT": 0, "DELVIS": 0, "FEILET": 0}
    for r in results:
        verdicts[r["verdict"]] += 1
    print(f"Total: {len(results)}  BESTATT: {verdicts['BESTATT']}  DELVIS: {verdicts['DELVIS']}  FEILET: {verdicts['FEILET']}")
    for r in results:
        weak = {k: v for k, v in r["dimensions"].items() if v <= 3}
        failed_topics = [t["topic"] for t in r["topics"] if not t["pass"]]
        flag = "!" if r["verdict"] == "FEILET" else ("~" if r["verdict"] == "DELVIS" else " ")
        print(f"{flag} {r['id']} {r['verdict']:7s} dims={r['dimensions']} weak={weak} fails={failed_topics} miss_src={r['missing_sources']}")


if __name__ == "__main__":
    evaluate()
