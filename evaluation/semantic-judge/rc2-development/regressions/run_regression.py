#!/usr/bin/env python3
"""RC2 generalized engine regression suite (RC2 spec section 34).

Generalized from BURNED_BLIND_V1_DEVELOPMENT_ONLY failures
(RC1B-0005/0086/0112/0122/0131 are named here for diagnosis only, never
in runtime engine code). Assert-based; exit 1 on any failure. Writes
results.json next to this file.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "engine")
T1PROOF = os.path.join(os.path.dirname(HERE), "..", "tier1-proof")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.abspath(T1PROOF))

import polarity_engine_v02 as E  # noqa: E402
import quote_aligner as QA  # noqa: E402
import tier1_operators as OPS  # noqa: E402


class Runner:
    def __init__(self):
        self.rows = []

    def case(self, group, name, claim, src, expect):
        try:
            verdict = E.judge_claim(claim, src)["verdict"]
            err = None
        except Exception as ex:  # runtime robustness is part of the gate
            verdict, err = "EXCEPTION", type(ex).__name__ + ": " + str(ex)[:80]
        ok = verdict in (expect if isinstance(expect, tuple) else (expect,))
        self.rows.append({"group": group, "name": name, "expect": expect,
                          "got": verdict, "pass": ok, "error": err})

    def qa_case(self, group, name, got, expect):
        ok = got == expect
        self.rows.append({"group": group, "name": name, "expect": expect,
                          "got": got, "pass": ok, "error": None})

    def ops_contra(self, group, name, claim, src, expect):
        try:
            proofs, crashed = OPS.run_operators(claim, src)
            got = "EXCEPTION" if crashed else (
                "CONTRADICTED" if any(p["result"] == "CONTRADICTED"
                                      for p in proofs) else "NO_CONTRA")
        except Exception as ex:
            got = "EXCEPTION: " + type(ex).__name__
        ok = got == expect
        self.rows.append({"group": group, "name": name, "expect": expect,
                          "got": got, "pass": ok, "error": None})

    def finish(self, path):
        fails = [r for r in self.rows if not r["pass"]]
        out = {"suite": "rc2-engine-regression-v1",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "total": len(self.rows),
               "passed": len(self.rows) - len(fails),
               "failed": len(fails), "rows": self.rows}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        for r in fails:
            print("FAIL", r["group"], r["name"], "expect", r["expect"],
                  "got", r["got"], r["error"] or "")
        print("RESULT: %d/%d passed" % (out["passed"], out["total"]))
        return 1 if fails else 0


R = Runner()

# ---- law-citation age negatives (burned RC1B-0122/0131 generalized)
R.case("law_age_negative", "statute section not age range",
       "Barn fra 16 ar kan samtykke selv etter pasient- og "
       "brukerrettighetsloven § 4-3.",
       "Tabell: 16+ kan selv (PRL § 4-3). § 4-3 gjelder samtykke.",
       "SUPPORTED")
R.case("law_age_negative", "FOR identifier not age range",
       "Overgangsforskriften (FOR-2026-06-25-1361) omfatter enslig "
       "mor/far som fyller vilkarene.",
       "§ 1 omfatter enslig mor/far som har vedtak om overgangsstønad "
       "(FOR-2026-06-25-1361), eller har søkt og fyller vilkårene.",
       "SUPPORTED")
R.case("law_age_negative", "old statute reference not age",
       "Overgangsstønad kan forlenges etter gamle § 15-8 andre ledd.",
       "Vedtak om overgangsstønad kan forlenges etter gamle § 15-8 "
       "andre, fjerde og femte ledd.",
       "SUPPORTED")
R.case("law_age_negative", "chapter/section numbers not age",
       "Kapittel 4 og ledd 2 i forskriften omhandler barnetrygd.",
       "Forskriften kapittel 4, ledd 2 omhandler barnetrygd.",
       "SUPPORTED")
R.case("law_age_negative", "ISO-like date in id not age",
       "Overgangsforskriften (LOV-2026-06-12-27) trer i kraft "
       "1. juli 2026.",
       "Overgangsforskriften (LOV-2026-06-12-27) trer i kraft "
       "1. juli 2026.",
       "SUPPORTED")
R.case("law_age_negative", "phone number not age",
       "Du kan ringe NAV på telefon 55 55 33 34 for å søke.",
       "NAV kundeservice: telefon 55 55 33 34, hverdager 09-15.",
       "SUPPORTED")
R.case("law_age_negative", "amount not age range",
       "Beløpet er 2 572 kroner per måned.",
       "Satsen er 2 572 kroner per måned for full sats.",
       "SUPPORTED")
R.case("law_age_negative", "G-beløp not age",
       "Ingen stønad ved inntekt over 4 G.",
       "Det er ingen stønad ved pensjonsgivende inntekt over 4 G.",
       "SUPPORTED")

# ---- true age positives must keep working
R.case("age_positive", "range stays detected",
       "Barn mellom 6 og 12 år har rett til SFO.",
       "Barn mellom 6 og 12 år har rett til skolefritidsordningen.",
       "SUPPORTED")
R.case("age_positive", "fra-til range stays detected",
       "Ordningen gjelder barn fra 16 til 18 år.",
       "Ordningen gjelder barn fra 16 til 18 år som bor hjemme.",
       "SUPPORTED")
R.case("age_positive", "real age conflict still fires",
       "Tilbudet gjelder barn under 3 år.",
       "Tilbudet gjelder barn fra 6 år som har startet på skolen.",
       "CONTRADICTED")
R.case("age_positive", "7-åring phrase stays detected",
       "Ordningen gjelder 7-åringer.",
       "Ordningen er for 7-åringer som går på skolen.",
       "SUPPORTED")

# ---- full/divided rate (burned RC1B-0005 generalized)
R.case("full_divided", "full vs halved not conflict",
       "Utvidet barnetrygd har full sats 2 572 kroner i måneden. "
       "Ved delt fast bosted halveres den til 1 286 kroner per forelder.",
       "Utvidet barnetrygd er 2 572 kroner i måneden. Delt utvidet "
       "barnetrygd er 1 286 kroner i måneden.",
       "SUPPORTED")
R.case("full_divided", "same full rate still supported",
       "Full sats er 2 572 kroner i måneden.",
       "Full sats er 2 572 kroner i måneden.",
       "SUPPORTED")
R.case("full_divided", "true same-quantity conflict kept",
       "Full sats for barnetrygd er 1 800 kroner i måneden.",
       "Full sats for barnetrygd er 2 572 kroner i måneden.",
       "CONTRADICTED")

# ---- aggregate vs component
R.case("agg_component", "total vs parts not conflict",
       "Total stønad var 5 000 kroner i måneden.",
       "Stønaden var 2 500 kroner for barnepass og 2 500 kroner for "
       "tannbehandling. Totalt ble det utbetalt 5 000 kroner i måneden.",
       "SUPPORTED")
R.case("agg_component", "double rate not conflict",
       "Hun mottar dobbelt barnetrygd, 5 144 kroner i måneden.",
       "Barnetrygd er 2 572 kroner per måned per barn. For to barn "
       "utbetales 5 144 kroner i måneden.",
       "SUPPORTED")

# ---- numeric conjunction (burned RC1B-0086 generalized)
R.case("numeric_conjunction", "cap plus total not self-conflict",
       "Undersøkelsen skal avsluttes senest 3 måneder etter "
       "1-ukesfristen, med mulighet for utvidelse til 6 måneder totalt.",
       "Undersøkelse: konklusjon senest 3 måneder etter 1-ukesfristen; "
       "utvidelse til 6 måneder totalt.",
       "INSUFFICIENT_EVIDENCE")

R.case("numeric_conjunction",
       "cross-subject value citation still conflicts",
       "Utvidet barnetrygd er 2 012 kroner i måneden fra 1.2.2026, "
       "samme sats som ordinær barnetrygd.",
       "Ordinær barnetrygd\n- Beløp: 2 012 kr/mnd per barn (0-18 år)\n"
       "Utvidet barnetrygd\n- Beløp: 2 572 kr/mnd per barn\n"
       "Finmarkstillegg: +512 kr/mnd per barn.",
       "CONTRADICTED")

# ---- runtime robustness (burned RC1B-0112 generalized + spec 31)
R.case("runtime_robust", "actor-family set bug repro",
       "Foreldre kan kontakte PPT på eget initiativ for råd og "
       "veiledning, og det er mulig å drøfte bekymringer med PPT "
       "anonymt før en eventuell henvisning.",
       "- Direkte kontakt: Foreldre kan kontakte PPT på eget initiativ "
       "for råd og veiledning (Udir).\n\nUdir: elever over 15 år, "
       "foreldre, barnehager, skoler og andre tverrfaglige tjenester "
       "kan ta kontakt med PPT for råd og veiledning. Det er mulig å "
       "drøfte bekymringer med PPT anonymt før en eventuell henvisning.",
       "SUPPORTED")
R.case("runtime_robust", "missing fields tolerated",
       "Dette er en test.", "Kilde uten relevante felt.", "INSUFFICIENT_EVIDENCE")
R.case("runtime_robust", "weird punctuation tolerated",
       "Satsen er 1 000 kr!!! ??",
       "Sats: 1 000 kr. --- | tabell | 1 000 kr | ...",
       ("SUPPORTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"))
R.case("runtime_robust", "empty claim tolerated",
       ".", "Kildetekst.", "INSUFFICIENT_EVIDENCE")

# ---- compound sanity
R.case("compound", "single atom compound support",
       "BUP utreder psykiske lidelser.",
       "BUP utreder psykiske lidelser og nevroutviklingsforstyrrelser.",
       "SUPPORTED")

# ---- ENT-C / N-R1 / N-A4 / ACT-25 canaries via tier1 operator gate
R.ops_contra("canaries", "ENT-C no contradiction",
             "PPT kan stille ADHD-diagnose.",
             "PPT kartlegger pedagogiske behov og gir sakkyndige "
             "vurderinger. BUP utreder psykiske lidelser/"
             "nevroutviklingsforstyrrelser.", "NO_CONTRA")
R.ops_contra("canaries", "N-R1 staff negation never binds",
             "Helsesykepleier stiller ADHD-diagnose.",
             "Skolehelsetjenesten stiller ikke diagnoser.", "NO_CONTRA")
R.case("canaries", "N-A4 henvisning mismatch stays review",
       "Henvendelse krever henvisning.",
       "Du kan kontakte helsestasjonen uten henvisning.",
       "CONTRADICTED")
R.case("canaries", "ACT-25 positive reference intact",
       "Psykolog i BUP kan gi terapi.",
       "BUP har psykologer og leger som gir behandling.",
       "SUPPORTED")

# ---- age parser unit checks (spec RC2 sections 6-7)
R.qa_case("age_parser", "statute not parsed as age",
          QA.extract_ages("Etter § 4-3 og § 15-8 andre ledd"), [])
R.qa_case("age_parser", "FOR id not parsed as age",
          QA.extract_ages("FOR-2026-06-25-1361 og LOV-2026-06-12-27"), [])
R.qa_case("age_parser", "date not parsed as age",
          QA.extract_ages("Frist 25.06.2026, telefon 22 33 44"), [])
R.qa_case("age_parser", "mellom parsed",
          [a["interval"] for a in QA.extract_ages("barn mellom 6 og 12 år")],
          [[6, 12]])
R.qa_case("age_parser", "fra X til Y parsed",
          [a["interval"] for a in QA.extract_ages("fra 16 til 18 år")],
          [[16, 18]])
R.qa_case("age_parser", "fylt parsed",
          [a["interval"] for a in QA.extract_ages("fylt 16 år")],
          [[16, 200]])
R.qa_case("age_parser", "under parsed",
          [a["interval"] for a in QA.extract_ages("barn under 18")],
          [[0, 17]])
R.qa_case("age_parser", "bare ar parsed",
          [a["interval"] for a in QA.extract_ages("barn som er 7 år")],
          [[7, 7]])
R.qa_case("age_parser", "aaring parsed",
          [a["interval"] for a in QA.extract_ages("7-åringer og 8-åringer")],
          [[7, 7], [8, 8]])

if __name__ == "__main__":
    sys.exit(R.finish(os.path.join(HERE, "results.json")))
