#!/usr/bin/env python3
"""Build the 20-case contract calibration set (spec 16).

Cases are constructed from line-anchored KB spans located mechanically by
unique seed strings, so embedded evidence text is byte-identical to the
KB files by construction. Gold labels are embedded for the mechanical
agreement computation and validated against the v3 schema.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

SCHEMA = json.loads(
    (HERE / "annotation-contract-v3.schema.json").read_text(encoding="utf-8"))


def span(file_name, seed, before=0, after=0):
    lines = (ROOT / file_name).read_text(encoding="utf-8").splitlines()
    hits = [i for i, ln in enumerate(lines) if seed in ln]
    assert len(hits) == 1, (file_name, seed, hits)
    s = hits[0] - before
    e = hits[0] + after
    return {
        "kb_ref": file_name,
        "lines": [s + 1, e + 1],
        "text": "\n".join(lines[s:e + 1]),
    }


CAL2 = "--cal2" in sys.argv


F54 = "54-delt-barnetrygd-ordinar-og-utvidet.md"
F34 = "34-mekling-og-foreldresamarbeidsavtale.md"
F39 = "39-frivillige-hjelpetiltak.md"
F31 = "31-skolehelsetjenesten-i-dybden.md"
F28 = "28-ppt-i-dybden.md"
F25 = "25-kommunale-psykiske-tjenester-barn-unge.md"
F41 = "41-samtykke-pa-tvers-av-tjenester.md"

SPANS = {
    "S54_TABLE": span(F54, "| Ordinær barnetrygd | 2 012",
                      before=2, after=1),
    "S54_ITEMS": span(F54, "1. Ordinær barnetrygd følger barnet",
                      after=2),
    "S54_EX": span(F54, "3. Eksempel: en forelder"),
    "S54_ITEM4": span(F54, "4. En forelder med delt ordinær"),
    "S34": span(F34, "Foreldrene motter minst", after=3),
    "S39_31": span(F39, "Barnevernstjenesten skal tilby", after=1),
    "S39_34": span(F39, "§ 3-4: nar vilkarene"),
    "S28": span(F28, "Klagefrist: 3 uker"),
    "S25": span(F25, "Fritak fra egenandeler endres 01.08.2026"),
    "S41": span(F41, "barn over 16 ar (til og med 17) kan normalt"),
    "S54_HEADER": span(F54, "Satser fra 1. februar 2026"),
    "S31": span(F31, "i prinsippet"),
    "S31_V": span(F31, "helsesamtaler om trivsel"),
    "S28_KLAGE": span(F28, "kan klage på vedtak (3 uker)"),
    "S33": span("33-familievern-i-dybden.md",
                "foreldrene samtykker, men barnets mening"),
    "S38": span("38-barnevernet-hjelp-ikke-bare-inngrep.md",
                "undersokelse starter snarest"),
}


def g(cid, claim, span_ids, rel, qi, qt, vc, vs, role, temporal,
      comp, crel, duty, derived, rationale):
    return {
        "case_id": cid, "claim": claim,
        "span_ids": span_ids, "semantic_relation": rel,
        "quantity_identity": qi, "quantity_type": qt,
        "quantity_value_claim": vc, "quantity_value_source": vs,
        "role": role, "temporal_applicability": temporal,
        "comparator_applicable": comp, "comparator_relation": crel,
        "arithmetic_duty": duty, "derived_quantity": derived,
        "rationale": rationale,
    }


D_AGG = {
    "operands": ["1006 NOK", "1286 NOK"], "operation": "ADD",
    "value": "2292 NOK",
    "provenance_span_ids": ["S54_TABLE"],
    "quantity_identity": "SAME", "role": "AGGREGATE",
}

# GOLD_MARKER_PART2
GOLD2 = [
    g("CD3-001",
      "Meklingsattesten er gyldig i 3 maneder.",
      ["S34"], "CONTRADICTS", "SAME", "PERIOD", "3 MONTH", "6 MONTH",
      "DIRECT", "APPLICABLE", True, "SOURCE_STRONGER", "NOT_APPLICABLE",
      None,
      "Evidence states gyldig i 6 maneder, positively refuting 3 "
      "maneder for the same validity period."),
    g("CD3-002",
      "Foreldre kan be om inntil 3 frivillige meklingstimer i tillegg "
      "etter avsluttet obligatorisk mekling.",
      ["S34"], "ENTAILS", "SAME", "PERIOD", "3 HOUR", "3 HOUR", "DIRECT",
      "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence states inntil 3 frivillige timer i tillegg after the "
      "obligatory meeting."),
    g("CD3-003",
      "Foreldrene motter minst to obligatoriske meklingsmoter.",
      ["S34"], "CONTRADICTS", "SAME", "COUNT", "2 COUNT", "1 COUNT",
      "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER", "NOT_APPLICABLE",
      None,
      "Evidence states minst 1 obligatorisk meklingsmote, positively "
      "refuting a minimum of two."),
    g("CD3-004",
      "Meklingsattesten er gyldig i 6 maneder.",
      ["S34"], "ENTAILS", "SAME", "PERIOD", "6 MONTH", "6 MONTH",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Evidence states attesten er gyldig i 6 maneder verbatim."),
    g("CD3-005",
      "Frivillige hjelpetiltak etter § 3-1 kan iverksettes uten "
      "samtykke fra dem som har foreldreansvar.",
      ["S39_31"], "CONTRADICTS", "NOT_APPLICABLE", "NOT_APPLICABLE",
      None, None, "NOT_APPLICABLE", "APPLICABLE", False,
      "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence states tiltak iverksettes med samtykke and that uten "
      "samtykke kan ikke § 3-1-tiltak iverksettes."),
    g("CD3-006",
      "Barnevernet kan iverksette § 3-1-tiltak bare med samtykke.",
      ["S39_34"], "RELATED_BUT_INSUFFICIENT", "NOT_APPLICABLE",
      "NOT_APPLICABLE", None, None, "NOT_APPLICABLE", "APPLICABLE",
      False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence covers the § 3-4 exception (vedtak uten samtykke ved "
      "alvorlig fare), so the unconditional bare-claim cannot be "
      "established from this packet alone; one live reading remains."),
    g("CD3-007",
      "Barnevernets undersokelse skal konkluderes senest 6 maneder "
      "etter at total utvidelse er besluttet.",
      ["S38"], "ENTAILS", "SAME", "PERIOD", "6 MONTH", "6 MONTH",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Evidence states total utvidelse til 6 maneder for the "
      "undersokelse."),
    g("CD3-008",
      "Barnevernets undersokelse skal konkluderes senest 3 maneder "
      "etter 1-ukesfristen uten utvidelse.",
      ["S38"], "ENTAILS", "SAME", "PERIOD", "3 MONTH", "3 MONTH",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Evidence states konkluderes senest 3 maneder etter 1-ukesfristen "
      "as the baseline rule."),
    g("CD3-009",
      "En forelder med delt ordinaer barnetrygd uten utvidet "
      "barnetrygd faar 1006 kroner i maneden fra NAV, og meklingsattest "
      "er gyldig i 6 maneder.",
      ["S54_ITEM4"], "PARTIAL", "SAME", "MONEY", "1006 NOK", "1006 NOK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "The barnetrygd conjunct is stated verbatim (faar bare 1006 "
      "kroner); the attest conjunct is outside this packet, so PARTIAL "
      "binds quantity fields to the established conjunct."),
    g("CD3-010",
      "Delt utvidet barnetrygd er 1286 kroner i maneden per 2026, og "
      "en forelder uten rett til utvidet barnetrygd faar 1206 kroner i "
      "maneden.",
      ["S54_TABLE"], "PARTIAL", "SAME", "MONEY", "1206 NOK", "1006 NOK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "The rate-table conjunct is established; the 1206-conjunct is "
      "not addressed by the table, so the quantity fields bind to the "
      "unestablished conjunct per the deciding-conjunct rule."),
    g("CD3-011",
      "Ordinaer barnetrygd full sats er 2012 kroner per maned i 2026.",
      ["S54_TABLE"], "ENTAILS", "SAME", "MONEY", "2012 NOK", "2012 NOK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Rate table states Ordinaer barnetrygd full sats 2 012 kr/mnd "
      "with satser fra 1. februar 2026."),
    g("CD3-012",
      "Ordinaer barnetrygd full sats var 2012 kroner per maned i "
      "desember 2025.",
      ["S54_HEADER"], "RELATED_BUT_INSUFFICIENT", "DIFFERENT", "MONEY",
      "2012 NOK", "2012 NOK", "DIRECT", "HISTORICAL_ONLY", False,
      "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Rates apply from 1. februar 2026; the December 2025 period is "
      "before the stated validity start, so the packet cannot "
      "establish the claimed historical rate."),
    g("CD3-013",
      "Eleven kan i prinsippet mote pa drop-in uten time.",
      ["S31"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states eleven kan i prinsippet mote pa drop-in/aapen "
      "dor uten time."),
    g("CD3-014",
      "Helsesykepleier skal tilby helsesamtaler om trivsel, vennskap, "
      "mobbing, stress, bekymringer og familie.",
      ["S31_V"], "RELATED_BUT_INSUFFICIENT", "NOT_APPLICABLE",
      "NOT_APPLICABLE", None, None, "NOT_APPLICABLE", "APPLICABLE",
      False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence lists helsesamtaler om these topics under Kan (forskrift "
      "§ 6 + Helsenorge), a weaker modality than the claim's skal, and "
      "names no obligating subject for the full list."),
    g("CD3-015",
      "PPT-vedtak kan klages innen 3 uker.",
      ["S28_KLAGE"], "ENTAILS", "SAME", "PERIOD", "3 WEEK", "3 WEEK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Evidence states du kan klage pa vedtak (3 uker)."),
    g("CD3-016",
      "Familievernkontoret krever foreldres samtykke til samtaler for "
      "barn under 16 ar.",
      ["S33"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states foreldrene samtykker for barn under 16 ar "
      "(FVL § 6)."),
    g("CD3-017",
      "Barnets uttalelse skal gis stor vekt i familievernkontoret fra "
      "barnet fyller 12 ar.",
      ["S33"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states for barn 12-16 ar skal barnets uttalelse gis "
      "stor vekt."),
    g("CD3-018",
      "Klagefristen for PPT-vedtak er 8 uker fra mottak av vedtak.",
      ["S28"], "CONTRADICTS", "SAME", "PERIOD", "8 WEEK", "3 WEEK",
      "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER", "NOT_APPLICABLE",
      None,
      "Evidence states klagefrist 3 uker fra mottak av vedtak for the "
      "same vedtak type, positively refuting 8 uker."),
    g("CD3-019",
      "Barn under 18 ar slipper egenandeler for helsetjenester "
      "omfattet av frikortordningen.",
      ["S25"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states fritak for barn og ungdom under 18 ar from "
      "01.08.2026; the undated claim reads as the current rule."),
    g("CD3-020",
      "Barn over 16 ar kan normalt selv gi samtykke til helsehjelp, "
      "og foreldre kan alltid samtykke pa vegne av barn over 16 ar.",
      ["S41"], "PARTIAL", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "First conjunct is stated nearly verbatim; the alltid-foreldre "
      "conjunct is neither established nor refuted, and no quantity is "
      "involved."),
]


GOLD = [
    g("CC3-001",
      "En forelder med delt fast bosted og innvilget delt utvidet "
      "barnetrygd faar totalt 2292 kroner i maneden fra NAV.",
      ["S54_ITEMS"], "ENTAILS", "SAME", "MONEY", "2292 NOK", "2292 NOK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Evidence states the exact example: 1006 + 1286 = 2292 kroner i "
      "maneden for this parent."),
    g("CC3-002",
      "En forelder med delt fast bosted og innvilget delt utvidet "
      "barnetrygd faar totalt 2292 kroner i maneden fra NAV.",
      ["S54_TABLE"], "ENTAILS", "SAME", "MONEY", "2292 NOK", "2292 NOK",
      "AGGREGATE", "APPLICABLE", False, "NOT_APPLICABLE", "REQUIRED",
      D_AGG,
      "Component rates 1006 and 1286 are stated; their sum equals the "
      "claimed 2292."),
    g("CC3-003",
      "En forelder med delt fast bosted og innvilget delt utvidet "
      "barnetrygd faar totalt 2392 kroner i maneden fra NAV.",
      ["S54_ITEMS"], "CONTRADICTS", "SAME", "MONEY", "2392 NOK",
      "2292 NOK", "AGGREGATE", "APPLICABLE", True, "SOURCE_WEAKER",
      "REQUIRED", D_AGG,
      "Stated components sum to 2292, which positively refutes the "
      "claimed 2392 total."),
    g("CC3-004",
      "Delt utvidet barnetrygd er 1286 kroner per maned.",
      ["S54_TABLE"], "ENTAILS", "SAME", "MONEY", "1286 NOK", "1286 NOK",
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "Rate table states delt utvidet barnetrygd 1 286 kr/mnd."),
    g("CC3-005",
      "Delt utvidet barnetrygd er 1386 kroner per maned.",
      ["S54_TABLE"], "CONTRADICTS", "SAME", "MONEY", "1386 NOK",
      "1286 NOK", "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER",
      "NOT_APPLICABLE", None,
      "Rate table states 1286 kr/mnd for the same benefit, positively "
      "refuting 1386."),
    g("CC3-006",
      "En forelder med delt ordinaer barnetrygd faar 1006 kroner i "
      "maneden, og utvidet barnetrygd er 1286 kroner i maneden.",
      ["S54_ITEM4"], "PARTIAL", "UNRESOLVED", "MONEY", "1286 NOK", None,
      "DIRECT", "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE",
      None,
      "First conjunct is stated verbatim; the evidence does not address "
      "the utvidet rate conjunct."),
    g("CC3-007",
      "En forelder med delt ordinaer barnetrygd uten rett til utvidet "
      "barnetrygd faar 1206 kroner i maneden fra NAV.",
      ["S54_ITEM4"], "CONTRADICTS", "SAME", "MONEY", "1206 NOK",
      "1006 NOK", "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER",
      "NOT_APPLICABLE", None,
      "Evidence states this parent faar bare 1006 kroner i maneden, "
      "positively refuting 1206."),
    g("CC3-008",
      "Meklingsattesten er gyldig i 12 maneder.",
      ["S34"], "CONTRADICTS", "SAME", "PERIOD", "12 MONTH", "6 MONTH",
      "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER", "NOT_APPLICABLE",
      None,
      "Evidence states attesten er gyldig i 6 maneder, positively "
      "refuting 12 maneder."),
    g("CC3-009",
      "Etter obligatorisk mekling kan foreldre be om inntil 3 frivillige "
      "timer i tillegg.",
      ["S34"], "ENTAILS", "SAME", "PERIOD", "3 HOUR", "3 HOUR", "DIRECT",
      "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence states foreldrene kan deretter be om inntil 3 frivillige "
      "timer i tillegg."),
    g("CC3-010",
      "Frivillige hjelpetiltak etter barnevernloven § 3-1 kan ikke "
      "iverksettes uten samtykke.",
      ["S39_31"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states at uten samtykke kan ikke § 3-1-tiltak "
      "iverksettes."),
    g("CC3-011",
      "Barnevernet kan vedta tiltak uten samtykke nar vilkarene i "
      "§ 3-1 er oppfylt og det er nodvendig for a sikre barnet "
      "tilfredsstillende omsorg eller beskyttelse.",
      ["S39_34"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      None, "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states § 3-4 vedtak uten samtykke under nettopp disse "
      "vilkarene."),
    g("CC3-012",
      "Klagefristen for PPT-vedtak er 6 uker fra mottak av vedtak.",
      ["S28"], "CONTRADICTS", "SAME", "PERIOD", "6 WEEK", "3 WEEK",
      "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER", "NOT_APPLICABLE",
      None,
      "Evidence states klagefrist 3 uker fra mottak av vedtak, "
      "positively refuting 6 uker."),
    g("CC3-013",
      "PPT-vedtak kan klages innen 3 uker fra mottak av vedtak.",
      ["S28"], "ENTAILS", "SAME", "PERIOD", "3 WEEK", "3 WEEK", "DIRECT",
      "APPLICABLE", False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Evidence states klagefrist: 3 uker fra mottak av vedtak."),
    g("CC3-014",
      "Barn og ungdom under 18 ar slipper egenandeler for helsetjenester "
      "omfattet av frikortordningen fra 01.08.2026.",
      ["S25"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None, None,
      "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states fritaket gjelder under 18 ar fra 01.08.2026; the "
      "age is population scope, not a compared quantity."),
    g("CC3-015",
      "Barn og ungdom under 16 ar slipper egenandeler for helsetjenester "
      "omfattet av frikortordningen fra 01.08.2026.",
      ["S25"], "CONTRADICTS", "SAME", "AGE", "16 YEAR", "18 YEAR",
      "DIRECT", "APPLICABLE", True, "SOURCE_STRONGER", "NOT_APPLICABLE",
      None,
      "Evidence positively sets the threshold at under 18 ar for the "
      "same date, refuting an under-16 threshold."),
    g("CC3-016",
      "Barn over 16 ar kan normalt selv gi samtykke til helsehjelp.",
      ["S41"], "ENTAILS", "NOT_APPLICABLE", "NOT_APPLICABLE", None, None,
      "NOT_APPLICABLE", "APPLICABLE", False, "NOT_APPLICABLE",
      "NOT_APPLICABLE", None,
      "Evidence states barn over 16 ar kan normalt selv gi samtykke til "
      "helsehjelp."),
    g("CC3-017",
      "Foreldre kan alltid samtykke pa vegne av barn over 16 ar til "
      "helsehjelp.",
      ["S41"], "RELATED_BUT_INSUFFICIENT", "NOT_APPLICABLE",
      "NOT_APPLICABLE", None, None, "NOT_APPLICABLE", "APPLICABLE",
      False, "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Same topic, but the evidence addresses the child's own consent "
      "with modality normalt; it neither establishes nor refutes that "
      "foreldre alltid kan samtykke."),
    g("CC3-018",
      "En forelder med delt fast bosted og innvilget delt utvidet "
      "barnetrygd faar totalt 2292 kroner i maneden fra NAV i 2024.",
      ["S54_EX"], "RELATED_BUT_INSUFFICIENT", "DIFFERENT", "MONEY",
      "2292 NOK", "2292 NOK", "DIRECT", "HISTORICAL_ONLY", False,
      "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Same topic and amount, but the rates apply from 1. februar 2026; "
      "the claim asserts the 2024 period, which the packet cannot "
      "establish."),
    g("CC3-019",
      "Fra 01.01.2027 vil delt utvidet barnetrygd vaere 1286 kroner per "
      "maned.",
      ["S54_TABLE"], "RELATED_BUT_INSUFFICIENT", "DIFFERENT", "MONEY",
      "1286 NOK", "1286 NOK", "DIRECT", "UNRESOLVED", False,
      "NOT_APPLICABLE", "NOT_APPLICABLE", None,
      "Current-rate evidence cannot establish which rate will apply on "
      "the future date 01.01.2027."),
    g("CC3-020",
      "Meklingsattesten er gyldig i 6 maneder, og foreldre som skal til "
      "mekling motter minst to obligatoriske meklingsmoter.",
      ["S34"], "PARTIAL", "SAME", "COUNT", "2 COUNT", "1 COUNT",
      "DIRECT", "APPLICABLE", True, "SOURCE_WEAKER", "NOT_APPLICABLE",
      None,
      "Attest validity 6 maneder is established, but the evidence states "
      "minst 1 obligatorisk mote, leaving the second conjunct "
      "unestablished and in tension."),
]


def main():
    import jsonschema
    assert len(GOLD) == 20, len(GOLD)
    ids = [x["case_id"] for x in (GOLD2 if CAL2 else GOLD)]
    assert len(set(ids)) == 20
    pub_cases = []
    out_gold = GOLD2 if CAL2 else GOLD
    for x in out_gold:
        pub_cases.append({
            "case_id": x["case_id"],
            "claim": x["claim"],
            "evidence": [
                {"span_id": SPANS[s]["kb_ref"] + ":"
                 + str(SPANS[s]["lines"][0]), "text": SPANS[s]["text"]}
                for s in x["span_ids"]
            ],
        })
    set_id = "RC33-ANNOT-CONTRACT-CALIBRATION-%s" % ("2" if CAL2 else "1")
    public = {
        "set_id": set_id,
        "purpose": "development-only contract calibration (spec 16)",
        "case_count": len(pub_cases),
        "cases": pub_cases,
    }
    (HERE / ("contract-calibration-set-%s.json" % ("2" if CAL2 else "1"))
     ).write_text(
        json.dumps(public, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    gold_out = {"set_id": set_id, "gold": out_gold}
    (HERE / ("calibration-gold-%s.json" % ("2" if CAL2 else "1"))
     ).write_text(
        json.dumps(gold_out, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    for x in out_gold:
        obj = {k: v for k, v in x.items()
               if k not in ("claim", "span_ids")}
        jsonschema.validate(obj, SCHEMA)
    rel = {}
    for x in GOLD:
        rel[x["semantic_relation"]] = \
            rel.get(x["semantic_relation"], 0) + 1
    print("CALIBRATION_BUILD_OK n=20 set=%s" % set_id)
    print("relations", json.dumps(rel, sort_keys=True))
    print("comparator_applicable",
          sum(1 for x in GOLD if x["comparator_applicable"]))
    print("arithmetic_required",
          sum(1 for x in GOLD if x["arithmetic_duty"] == "REQUIRED"))
    print("temporal_unresolved",
          sum(1 for x in GOLD
              if x["temporal_applicability"] == "UNRESOLVED"))


if __name__ == "__main__":
    main()
