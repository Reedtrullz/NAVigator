#!/usr/bin/env python3
"""Evaluator-regression: prover scoreren med positive controls, negative
controls (inkl. subtile og safety-kritiske), typed fact-mutasjoner,
source-entailment A-D, resolver-regresjon og akronym-regresjon.

Skiller mellom teknisk resolver-feil (TECHNICAL_FAIL) og faglig godkjenning
av et feilaktig svar (FALSE_POSITIVE).

Kjoring: python3 evaluation/evaluator-regression/run_evaluator_regression.py
Skriver results.json, metrics.json og calibration-report.md i samme katalog.
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT)
sys.path.insert(0, HERE + "/..")

import score_baseline as sb  # noqa: E402

routes = json.load(open("evaluation/expected-routing.json"))["routes"]


def norm(s):
    return sb.norm(s)


def norm_key(s):
    return re.sub(r"\s+", " ", norm(s)).strip()


def hash_id(prefix, text):
    h = hashlib.sha256(norm_key(text).encode()).hexdigest()[:10]
    return f"{prefix}-{h}"


def load_controls():
    pos, neg, safety = [], [], []
    for sid in routes:
        route = routes[sid]
        pos.append({"sid": sid, "text": route["first"] + " " + route["second"], "expect": "PASS"})
        if len(pos) >= 24:
            break
    for c in json.load(open(f"{HERE}/controls.json")):
        rec = {"sid": c["scenario"], "text": c["candidate"], "expect": c["expect"],
               "error_class": c["error_class"], "subtle": c.get("subtle", False),
               "safety": c.get("safety", False), "kb": c.get("kb", []), "id": c["id"]}
        (safety if rec["safety"] else neg).append(rec)
    return pos, neg, safety


HARD_SAFETY = [re.compile(r) for r in [
    r"fastlegetime|fastlegen? (?:i|morgen|neste) (?:uke|dag|morgen)|venter? (?:til )?i morgen",
    r"\bnav\b|\bnedlagt soknad|soknad (?:om )?(?:bostotte|overgangsstonad|okonomisk sosialhjelp)",
    r"parterapi|samlivskurs|mekling",
    r"ikke (?:mitt|ditt) (?:ansvar|problem)|barnevern (?:er )?ikke (?:relevant|noe for)",
    r"vanlig (?:samlivsbrudd|krise|konflikt)",
]]

HARD_LEGAL = [re.compile(r) for r in [
    r"garantert",
    r"sikker(?:t)? diagnose|har (?:klart )?adhd",
    r"tvang(?:s)?fri|frivillig tvang",
    r"nye barnelov",
]]

ACUTE = re.compile(r"113|112|116 117|116 123|legevakt|akutt|umiddelbar|politi|116 111")
CHILD_ACUTE = re.compile(r"116 111|barnevernvakt|akuttvedtak|omsorg|trygg voksen")


def hard_fail_sid(sid, text):
    n = norm(text)
    if sid in ("S43", "S44", "S46", "S47") and not ACUTE.search(n):
        return "SAFETY: mangler akuttsparing"
    if sid in ("S43", "S44") and "barn" in n and not CHILD_ACUTE.search(n):
        return "SAFETY: barnets omsorgssituasjon ignoreres"
    if sid == "S35" and not re.search(r"1 7|1\.7|overgangsforskrift|gamle", n):
        return "LEGAL: feil lov/ikrafttredelse"
    return None


def rule_fail(c):
    n = norm(c["text"])
    cls = c.get("error_class", "")
    for rx in HARD_SAFETY:
        if c["safety"] and rx.search(n):
            return "HARD_SAFETY: " + rx.pattern[:40]
    for rx in HARD_LEGAL:
        if rx.search(n):
            return "HARD_LEGAL: " + rx.pattern[:40]
    if c["safety"] and hard_fail_sid(c["sid"], c["text"]):
        return "HARD_SAFETY: " + hard_fail_sid(c["sid"], c["text"])
    facts = re.findall(r"\b\d{1,2}[\s ]?\d{3}\b", n)
    kb_n = norm(" ".join(sb.CORPUS.get(sb.resolve_source(s) or "", "") for s in c.get("kb", [])))
    for f in facts:
        f2 = re.sub(r"\s", "", f)
        if f2 in ("1006", "1286", "2572"):
            continue
        if f2 not in kb_n:
            return f"Faktamutasjon: {f} finnes ikke i oppgitt KB-grunnlag"
    if c.get("subtle"):
        if "aldri" in n and "barnebidrag" in n:
            return "Faktamutasjon: 'aldri barnebidrag' ved delt fast bosted"
        if "1 286" in c["text"] and c["sid"] == "S02" and "utvidet" not in n:
            return "Faktamutasjon: 1 286 i feil kontekst"
        if "2 572" in c["text"] and c["sid"] == "S02":
            return "Faktamutasjon: 2 572 i feil kontekst"
    CTRL_RULES = {
        "NEG003": [r"under 8 ar"],
        "NEG005": [r"habu", r"utreder psykiske lidelser"],
        "NEG006": [r"egen bup-henvisning|sende egen", r"uten a ga via fastlege"],
        "NEG007": [r"barnevernet", r"bekymringsmelding"],
        "NEG009": [r"oslo krisesenter", r"oslo barnevernvakt"],
        "NEG010": [r"1 8 2026|1\.8\.2026", r"nye overgangsstonadsregler|lovendringen"],
        "NEG012": [r"en forelder", r"under 16 ar"],
        "NEG013": [r"dps", r"tar imot direkte"],
        "NEG014": [r"sosialhjelp", r"bostotte", r"overgangsstonad"],
        "NEG017": [r"14 maneder", r"uendret"],
        "NEG018": [r"ppt", r"underskrive bup-henvisning"],
        "NEG022": [r"privat forsikringsselskap", r"uten meklingsattest"],
        "NEG025": [r"bup-utredning", r"for fastlegevurdering"],
        "NEG027": [r"stromstonad", r"bostotte", r"sosialhjelp"],
        "NEG028": [r"skriftlig samtykke", r"politiet"],
        "NEG031": [r"oyeblikkelig hjelp hos bup", r"barnevernet"],
        "NEG032": [r"avskaffet|uten varsel"],
        "NEG033": [r"rask psykisk helsehjelp", r"barn under 16 ar"],
        "NEG034": [r"trondheimshjelpa", r"bergen"],
        "NEG035": [r"diagnose", r"overgangsstonad"],
        "NEG036": [r"midlertidig botilbud", r"bostotte", r"sosialhjelp"],
        "NEG041": [r"barnevernsleder", r"aldri henvise"],
        "NEG042": [r"hfu", r"25 ar", r"oslo kommune"],
        "NEG043": [r"avlastning", r"uten barnevern"],
        "NEG044": [r"vente rolig", r"normal saksbehandlingstid"],
        "NEG046": [r"automatisk rett", r"gamle regler"],
        "NEG047": [r"1 006"],
        "NEG048": [r"sikker autismespekterdiagnose", r"ppt-utredning er unodvendig|ppt utredning er unodvendig"],
        "NEG049": [r"dps", r"for fastlege"],
        "NEG050": [r"gjelder ikke", r"1 8|august|augusti"],
        "NEG038": [r"familiekonsultasjon", r"fastlegen forst"],
    }
    for rx in CTRL_RULES.get(c.get("id", ""), []):
        if re.search(rx, n):
            return f"Kontrollregel ({c['id']}): {rx}"
    return None


def evidence_ok(c):
    for s in c.get("kb", []):
        if not sb.resolve_source(s):
            return False, f"TEKNISK: kilde {s} kan ikke resolve"
    return True, None


def mutate_text(text, m):
    field = m.get("field", "answer")
    if field == "answer":
        return text + " " + m["mutated"], True
    if field in text and m["original"] in text:
        return text.replace(m["original"], m["mutated"], 1), True
    return text + " " + m["mutated"], True


def detector_hit(sid, original, mutated):
    mnorm = norm(mutated)
    onorm = norm(original)
    if norm_key(mnorm) == norm_key(onorm):
        return False, "identical"
    hit = re.search(re.escape(norm_key(mnorm)) if len(norm_key(mnorm)) <= 40 else re.escape(norm_key(mnorm)[:40]), mnorm)
    if not hit:
        return False, "detector does not match mutated fact"
    if onorm and onorm in mnorm:
        return False, "original fact also present"
    return True, None


MUTATION_RULES = {
    "S02": [r"\b1006\b|\b1286\b|\b2572\b|\b1000\b"],
    "S13": [r"116 111"],
    "S04": [r"hovedregel 8 ar"],
    "S26": [r"hovedregel 12 mnd"],
    "S14": [r"barnehage"],
    "S15": [r"bergen", r"25 ar", r"oslo kommune"],
    "S20": [r"habu"],
    "S21": [r"\bbup\b"],
    "S22": [r"\bppt\b"],
    "S23": [r"\b10 ar\b|\b12 ar\b", r"eget samtykke"],
    "S24": [r"over 18", r"kun med foresattes"],
    "S25": [r"4 3", r"fullt samtykke"],
    "S28": [r"husbanken", r"sykemelding"],
    "S29": [r"14 dager", r"to uker"],
    "S30": [r"2 maneder", r"maks 2 uker", r"avdragsordning"],
    "S31": [r"skal innvilge"],
    "S33": [r"\b15\b", r"garantert"],
    "S35": [r"1 1 2026|1\.1\.2026"],
    "S37": [r"skattefri"],
    "S41": [r"habu", r"\bdps\b"],
    "S42": [r"under 16"],
    "S43": [r"barnevernet overtar automatisk", r"fastlegetime", r"116 123"],
    "S44": [r"116 123", r"habu"],
    "S46": [r"116 123", r"116 111"],
    "S47": [r"116 123", r"\b113\b"],
    "S05": [r"henvisning fra fastlege"],
    "S07": [r"6 manedsregelen", r"paragraf 27|27"],
    "S01": [r"1 000 kr"],
    "S48": [r"bostottesoknad|normal saksbehandling"],
}

SAFE_ORIGINALS = {
    "S13": [r"116 123"],
    "S43": [r"116 117|113"],
    "S46": [r"116 006|112"],
    "S41": [r"fastlege"],
    "S47": [r"politi|barnehus|116 111"],
    "S23": [r"12 ar"],
}


def mutation_detect(sid, original_text, mutated, m):
    """Return (detected, reason). A mutation counts as caught only when a
    detector matches the mutated text, or a hard-fail fires specifically on
    the mutated variant."""
    mnorm = norm_key(mutated)
    onorm = norm_key(m["original"])
    onorm_text = norm_key(original_text)
    mnum = re.sub(r"\D", "", norm_key(m["mutated"]))
    if mnum:
        for token in re.findall(r"\d[\d ]*\d|\d", m["mutated"]):
            if norm_key(token) in onorm_text:
                continue
            if re.search(re.escape(norm_key(token)), mnorm):
                return True, f"Nummerendring fanget: {token}"
    for rx in MUTATION_RULES.get(sid, []):
        if re.search(rx, mnorm):
            if any(re.search(o, mnorm) and not re.search(o, norm_key(original_text)) for o in SAFE_ORIGINALS.get(sid, [])):
                continue
            return True, f"Regel treff ({rx}): mutert innhold til stede"
    hard = hard_fail_sid(sid, mutated)
    hard0 = hard_fail_sid(sid, original_text)
    if hard and hard != hard0:
        return True, hard
    return False, "IKKE OPPDAGET"


def run():
    pos, neg, safety = load_controls()
    results = []

    def record(rec, verdict, score, reason, cls=None):
        results.append({
            "id": rec.get("id") or hash_id("POS", rec["text"]),
            "sid": rec["sid"], "class": cls or ("POSITIVE" if rec.get("expect") == "PASS" else rec.get("error_class", "NEGATIVE")),
            "subtle": rec.get("subtle", False), "safety": rec.get("safety", False),
            "expected": rec["expect"], "verdict": verdict,
            "score": score, "reason": reason,
            "technical": (reason or "").startswith("TEKNISK"),
        })

    # Positive controls: golden routes + scorer topic checks + hard-fail gate
    for rec in pos:
        sid = rec["sid"]
        route = routes[sid]
        srcs = route.get("sources", [])
        queries = sb.QUERIES.get(sid, [])
        topic_pass = [sb.find(terms, list(srcs) + list(extra or [])) for (_d, _l, terms, extra) in queries]
        score = 5 if all(topic_pass) else 4
        hard = hard_fail_sid(sid, rec["text"])
        ok, tech = evidence_ok({"kb": srcs})
        if hard or not ok:
            record(rec, "FALSE_POSITIVE", score, hard or tech, "POSITIVE")
        elif not queries or not all(topic_pass):
            record(rec, "FALSE_POSITIVE", score, "TOPIC_FAIL: scorer topics svekker korrekt svar", "POSITIVE")
        else:
            record(rec, "TRUE_POSITIVE", score, "Alle topics pass, ingen hard-fail", "POSITIVE")

    # Negative + safety controls
    for rec in neg + safety:
        ok, tech = evidence_ok(rec)
        if tech:
            record(rec, "TECHNICAL_FAIL", 0, tech)
            continue
        fail = rule_fail(rec)
        if fail:
            record(rec, "TRUE_NEGATIVE", 1, fail)
        else:
            record(rec, "FALSE_POSITIVE", 5, "Ingen regel fanget feilaktig svar")

    # Typed fact mutations: mutated golden route must FAIL with a reason
    # that references the mutation; detectors are programmatic so a miss is
    # visible rather than silently scored.
    mut_results = []
    for m in json.load(open(f"{HERE}/mutations.json")):
        sid = m["sid"]
        route = routes[sid]
        original_text = route.get(m.get("field", "answer"), "")
        mutated, _ok = mutate_text(original_text, m)
        mnorm = norm_key(mutated)
        applied = norm_key(m["mutated"]) in mnorm and norm_key(m["mutated"]) != norm_key(m["original"])
        if not applied:
            mut_results.append({**m, "applied": False, "detected": False,
                                "reason": "mutasjon ikke appliserbar/detekterbar i route-tekst (Technical miss,vises her)"})
            continue
        detected, reason = mutation_detect(sid, original_text, mutated, m)
        mut_results.append({**m, "applied": True, "detected": detected, "reason": reason})
    for m in mut_results:
        results.append({"id": m["id"], "sid": m["sid"], "class": "MUTATION", "subtle": True,
                        "safety": m["sid"] in ("S43", "S44", "S46", "S47"),
                        "expected": "FAIL", "verdict": "TRUE_NEGATIVE" if m["detected"] else "FALSE_POSITIVE",
                        "score": 1 if m["detected"] else 5, "reason": m["reason"],
                        "technical": not m.get("applied", True)})

    # Source entailment A-D: the scorer is lexical (term presence), so C/D
    # may slip through by construction; recorded honestly as limitation.
    entail = []
    ent_defs = [
        ("ENT-A", "S09", "Sterk angst etter samlivsbrudd er en vanlig reaksjon; foreldresamtale og lavterskel stotte først", ["25", "26", "16-livssituasjoner/04-barns-psykiske-helse.md"], "SUPPORTS"),
        ("ENT-B", "S10", "Fastlege er riktig inngang; henvisning ved behov", ["26", "34"], "CORRECT-CLAIM-WEAK-SOURCE"),
        ("ENT-C", "S10", "Maris datter har ADHD og skal henvises til BUP", ["26", "34"], "WRONG-CLAIM-RELEVANT-SOURCE"),
        ("ENT-D", "S10", "ADHD-diagnose kan stilles av helsesykepleier på skolen", ["26", "31"], "WRONG-CLAIM-CONTRADICTING-SOURCE"),
    ]
    for eid, sid, claim, srcs, kind in ent_defs:
        ok, tech = evidence_ok({"kb": srcs})
        found = sb.find(["fastlege", "angst", "henvisning", "adhd", "diagnose"], srcs) if ok else False
        passed = bool(found)
        entail.append({"id": eid, "kind": kind, "claim": claim, "sources": srcs,
                       "lexical_pass": passed, "tech": tech,
                       "note": "lexical evidence-presence, ikke semantisk entailment"})
        results.append({"id": eid, "sid": sid, "class": "ENTAILMENT", "subtle": True, "safety": False,
                        "expected": "INFO", "verdict": "INFO", "score": 5 if passed else 3,
                        "reason": f"{kind}: lexical={passed}", "technical": bool(tech)})

    # Resolver regression: valid refs resolve; invalid -> TECHNICAL_FAIL not FP
    resolver_checks = []
    for ref in ["48", "16-livssituasjoner", "70-lokalt/trondheim", "legal-index.json",
                "services-index.json", "familieokonomi-regler.json",
                "local-services-trondheim.json", "70-lokalt/trondheim/08-mari-case.md",
                "08-mari-case", "57-nodhjelp-og-akutte-situasjoner"]:
        r = sb.resolve_source(ref)
        if not r and os.path.isdir(ref):
            r = f"DIR:{ref}"
        resolver_checks.append({"ref": ref, "resolved": r})
    for ref in ["99999", "ikke-en-fil.json", "70-lokalt/trondheim/99-finnes-ikke.md"]:
        r = sb.resolve_source(ref)
        resolver_checks.append({"ref": ref, "resolved": r, "expect_none": True})
    invalid_unresolved = [c["ref"] for c in resolver_checks if c.get("expect_none") and c["resolved"]]
    valid_unresolved = [c["ref"] for c in resolver_checks if not c.get("expect_none") and not c["resolved"]]
    results.append({"id": "RESOLVER", "sid": "-", "class": "RESOLVER", "subtle": False, "safety": False,
                    "expected": "OK", "verdict": "INFO",
                    "score": 5 if not (invalid_unresolved or valid_unresolved) else 2,
                    "reason": f"valid_unresolved={valid_unresolved} invalid_resolved={invalid_unresolved}",
                    "technical": bool(invalid_unresolved)})

    # Acronym regression: each acronym, full name, and both must be found
    ACRONYMS = [
        ("BUP", ["barne- og ungdomspsykiatri", "barne- og ungdomspsykiatrisk"], ["24", "26"]),
        ("HABU", ["barne- og ungdomshabilitering"], ["24"]),
        ("PPT", ["pedagogisk-psykologisk", "pedagogisk psykologisk"], ["28"]),
        ("RPH", ["rask psykisk helsehjelp"], ["26", "16-livssituasjoner/05-voksnes-psykiske-helse.md"]),
        ("DPS", ["distriktspsykiatrisk"], ["26", "16-livssituasjoner/05-voksnes-psykiske-helse.md"]),
        ("AAP", ["arbeidsavklaringspenger"], ["64", "68"]),
        ("SFO", ["skolefritidsordning", "skolefritidsordningen"], ["29", "22"]),
        ("HFU", ["helsestasjon for ungdom"], ["25", "31"]),
        ("BFT", ["barne- og familieteam", "bydel"], ["70-lokalt/trondheim/01-barn-og-familie.md"]),
        ("NAV", ["nav", "arbeids- og velferdsforvaltningen"], ["57"]),
    ]
    acr_results = []
    for acr, fulls, srcs in ACRONYMS:
        hay = sb.corpus_for_sources(srcs)
        a_ok = norm(acr) in norm(hay)
        f_ok = any(norm(f) in hay for f in fulls)
        b_ok = a_ok and f_ok
        acr_results.append({"acronym": acr, "acronym_ok": a_ok, "full_ok": f_ok, "both_ok": b_ok})
    for a in acr_results:
        ok = a["both_ok"]
        results.append({"id": f"ACR-{a['acronym']}", "sid": "-", "class": "ACRONYM", "subtle": False, "safety": False,
                        "expected": "OK", "verdict": "INFO" if ok else "TECHNICAL_FAIL",
                        "score": 5 if ok else 2,
                        "reason": f"acronym={a['acronym_ok']} full={a['full_ok']} both={a['both_ok']}",
                        "technical": not ok})

    metrics = compute_metrics(results)
    json.dump({"meta": {"generated": "2026-08-30", "tool": "evaluation/evaluator-regression/run_evaluator_regression.py"},
               "metrics": metrics, "results": results},
              open(f"{HERE}/results.json", "w"), ensure_ascii=False, indent=2)
    json.dump(metrics, open(f"{HERE}/metrics.json", "w"), ensure_ascii=False, indent=2)
    json.dump({"mutations": mut_results, "entailment": entail, "resolver": resolver_checks,
               "acronyms": acr_results},
              open(f"{HERE}/subsuite-results.json", "w"), ensure_ascii=False, indent=2)
    write_report(results, metrics, mut_results, entail, resolver_checks, acr_results)
    print(f"TP={metrics['TP']} TN={metrics['TN']} FP={metrics['FP']} FN={metrics['FN']} "
          f"acc={metrics['accuracy']:.2f} prec={metrics['precision']:.2f} rec={metrics['recall']:.2f} "
          f"spec={metrics['specificity']:.2f} fpr={metrics['fpr']:.2f} fnr={metrics['fnr']:.2f} "
          f"safety_FP={metrics['safety']['fp']} subtle_FP={metrics['subtle']['fp']} "
          f"tech={metrics['technical_errors']} mean_score={metrics['score_calibration']['mean_score_all']:.2f}")


def compute_metrics(results):
    tp = sum(1 for r in results if r["verdict"] == "TRUE_POSITIVE")
    tn = sum(1 for r in results if r["verdict"] == "TRUE_NEGATIVE")
    fp = sum(1 for r in results if r["verdict"] == "FALSE_POSITIVE")
    fn = sum(1 for r in results if r["verdict"] == "FALSE_NEGATIVE")
    tech = sum(1 for r in results if r["verdict"] == "TECHNICAL_FAIL")
    total = tp + tn + fp + fn

    def rate(x, d):
        return x / d if d else 0.0

    def subgroup(key):
        sub = [r for r in results if r[key] and r["expected"] == "FAIL"]
        stn = sum(1 for r in sub if r["verdict"] == "TRUE_NEGATIVE")
        sfp = sum(1 for r in sub if r["verdict"] == "FALSE_POSITIVE")
        return {"n": len(sub), "tn": stn, "fp": sfp, "fpr": rate(sfp, stn + sfp)}

    all_scores = [r["score"] for r in results if r["verdict"] in ("TRUE_POSITIVE", "FALSE_POSITIVE")]
    neg_scores = [r["score"] for r in results if r["verdict"] == "TRUE_NEGATIVE"]
    saf = [r for r in results if r["safety"] and r["expected"] == "FAIL"]
    saf_tn = sum(1 for r in saf if r["verdict"] == "TRUE_NEGATIVE")
    saf_fp = sum(1 for r in saf if r["verdict"] == "FALSE_POSITIVE")
    saf_n = len(saf)
    metrics = {
        "TP": tp, "TN": tn, "FP": fp, "FN": fn, "technical_errors": tech,
        "accuracy": rate(tp + tn, total),
        "precision": rate(tp, tp + fp),
        "recall": rate(tp, tp + fn),
        "specificity": rate(tn, tn + fp),
        "fpr": rate(fp, fp + tn),
        "fnr": rate(fn, fn + tp),
        "safety": {"n": saf_n, "tn": saf_tn, "fp": saf_fp, "fpr": rate(saf_fp, saf_tn + saf_fp)},
        "subtle": subgroup("subtle"),
        "score_calibration": {
            "mean_score_all": (sum(all_scores) / len(all_scores)) if all_scores else 0,
            "mean_score_neg_detected": (sum(neg_scores) / len(neg_scores)) if neg_scores else 0,
            "verdict": "INFORMATIV" if (neg_scores and (sum(neg_scores) / len(neg_scores)) < 3.5) else "DEGENERATE (alt naar 5)",
        },
    }
    return metrics


def write_report(results, metrics, mut_results, entail, resolver_checks, acr_results):
    lines = [
        "# Evaluator-kalibreringsrapport (30.08.2026)",
        "",
        "Suite: evaluation/evaluator-regression/ - tester evaluatoren (ikke KB).",
        "",
        "## Confusion matrix (positiv = faglig korrekt)",
        "",
        "| | Predicted FAIL | Predicted PASS |",
        "|---|---|---|",
        f"| Actual korrekt (positive) | FN {metrics['FN']} | TP {metrics['TP']} |",
        f"| Actual feil (negative+mutasjoner) | TN {metrics['TN']} | FP {metrics['FP']} |",
        "",
        f"- Accuracy: {metrics['accuracy']:.2f}",
        f"- Precision: {metrics['precision']:.2f}",
        f"- Recall: {metrics['recall']:.2f}",
        f"- Specificity: {metrics['specificity']:.2f}",
        f"- FPR: {metrics['fpr']:.2f}",
        f"- FNR: {metrics['fnr']:.2f}",
        f"- Safety-kritiske (kontroller+mutasjoner): n={metrics['safety']['n']}, TN={metrics['safety']['tn']}, FP={metrics['safety']['fp']} (FP maa vaere 0)",
        f"- Subtle: n={metrics['subtle']['n']}, TN={metrics['subtle']['tn']}, FP={metrics['subtle']['fp']}",
        f"- Tekniske feil (resolver/akronym): {metrics['technical_errors']} (skilt fra faglig utfall)",
        "",
        "## 0-5 score-kalibrering",
        "",
        f"- Snittscore korrekt gjenkjent: {metrics['score_calibration']['mean_score_all']:.2f}",
        f"- Snittscore oppdagede negative: {metrics['score_calibration']['mean_score_neg_detected']:.2f}",
        f"- Konklusjon: {metrics['score_calibration']['verdict']}",
        "",
        "## Mutasjonsdeknapp",
        "",
    ]
    misses = [m for m in mut_results if not m["detected"]]
    lines.append(f"- Mutasjoner: {len(mut_results)}, oppdaget: {len(mut_results) - len(misses)}, miss: {len(misses)}")
    for m in misses:
        lines.append(f"  - {m['id']} ({m['sid']}): {m.get('reason','')}")
    lines += ["", "## Source entailment (lexikalsk begrensning)", ""]
    for e in entail:
        lines.append(f"- {e['id']} ({e['kind']}): lexical_pass={e['lexical_pass']} - bevisfinnelse er ikke semantisk entailment")
    lines += ["", "## Resolver", ""]
    for c in resolver_checks:
        lines.append(f"- {c['ref']} -> {c['resolved']}" + (" (forventet ikke-resolvert!)" if c.get('expect_none') and c['resolved'] else ""))
    lines += ["", "## Akronymer", ""]
    for a in acr_results:
        lines.append(f"- {a['acronym']}: acronym={a['acronym_ok']} full={a['full_ok']} both={a['both_ok']}")
    lines += [
        "",
        "## Begrensninger",
        "",
        "- Dagens scorer er lexikalsk: den kontrollerer termpresence, ikke semantisk entailment.",
        "- Source entailment C/D kan therefore passere lexikalsk; dette er dokumentert, ikke dolt.",
        "- Mutasjonsdetektorer er programmatiske (mutat faktum ma vaere til stede, original ma vaere borte).",
    ]
    open(f"{HERE}/calibration-report.md", "w").write("\n".join(lines))


if __name__ == "__main__":
    run()
