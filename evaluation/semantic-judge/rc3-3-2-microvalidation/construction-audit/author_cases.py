#!/usr/bin/env python3
"""Author the RC3.3.2 fresh micro-validation (spec 19, 20).

Pass-1 gold labels are authored inline with each case. Public file
contains no label material. All evidence spans are verified verbatim
against the KB files before any output is written.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
KB = Path("/Users/reidar/Projectos/NAV Explore")
sys.path.insert(0, str(HERE))
import write_guard  # noqa: E402

S = {
    "33": (KB / "33-familievern-i-dybden.md", 1, 52),
    "34": (KB / "34-mekling-og-foreldresamarbeidsavtale.md", 1, 90),
    "35": (KB / "35-foreldreansvar-bosted-samvar.md", 1, 90),
    "36": (KB / "36-barnets-mening-og-barnets-beste.md", 1, 45),
    "38": (KB / "38-barnevernet-hjelp-ikke-bare-inngrep.md", 1, 70),
    "41": (KB / "41-samtykke-pa-tvers-av-tjenester.md", 1, 45),
    "31": (KB / "31-skolehelsetjenesten-i-dybden.md", 1, 75),
    "63": (KB / "63-overgangsstonad-endringsloven-og-kapittel-15.md", 1, 125),
    "68": (KB / "68-overgangsforskriften-i-dybden.md", 1, 95),
    "54": (KB / "54-delt-barnetrygd-ordinar-og-utvidet.md", 1, 65),
}
_LINES = {}


def lines(k):
    if k not in _LINES:
        path, lo, hi = S[k]
        text = path.read_text(encoding="utf-8").splitlines()
        _LINES[k] = {i + 1: text[i] for i in range(lo - 1, min(hi, len(text)))}
    return _LINES[k]


def span(k, n):
    t = lines(k).get(n)
    if t is None:
        raise ValueError(f"line {n} outside frozen range file {k}")
    return t


def L(k, *ns):
    return [span(k, n) for n in ns]


PS = {"E": "SUPPORTED", "C": "CONTRADICTED",
      "R": "REVIEW_REQUIRED", "I": "INSUFFICIENT_EVIDENCE"}

CASES = [
 dict(id="RC33M2-001",
      claim="En forelder med delt fast bosted og innvilget delt utvidet barnetrygd faar totalt 2292 kroner i maneden fra NAV.",
      rel="E", crit=True, group="aggcomp",
      flags=["quantity-money", "aggregate", "comparator-eq"],
      qty="MONEY:2292:NOK:AGGREGATE", tapp="CURRENT_MATCH",
      capp=True, crel="=", role="AGGREGATE", sup=["S1", "S2"],
      dim={"numeric_quantity": "NUMERIC_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("54", [14, 24]), ev=[("S1", ("54", 14)), ("S2", ("54", 24))]),
 dict(id="RC33M2-002",
      claim="En forelder med delt ordinær barnetrygd men uten rett til utvidet barnetrygd faar bare 1006 kroner i maneden.",
      rel="E", crit=False, group="aggcomp",
      flags=["quantity-money", "comparator-eq"],
      qty="MONEY:1006:NOK", tapp="CURRENT_MATCH",
      capp=True, crel="=", role="COMPONENT", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("54", [25, 25]), ev=[("S1", ("54", 25))]),
 dict(id="RC33M2-003",
      claim="En forelder med delt fast bosted og innvilget delt utvidet barnetrygd faar totalt 2392 kroner i maneden fra NAV.",
      rel="C", crit=True, group="aggcomp",
      flags=["quantity-money", "aggregate", "comparator-ne"],
      qty="MONEY:2392:NOK:AGGREGATE", tapp="CURRENT_MATCH",
      capp=True, crel="=", role="AGGREGATE", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("54", [14, 14]), ev=[("S1", ("54", 14))]),
 dict(id="RC33M2-004",
      claim="Full sats for utvidet barnetrygd er 2572 kroner per maned denne uken.",
      rel="R", crit=False, group="aggcomp",
      flags=["quantity-money", "temporal-hedge"],
      qty="MONEY:2572:NOK", tapp="UNKNOWN",
      capp=True, crel="=", role="STANDALONE", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("54", [15, 15]), ev=[("S1", ("54", 15))]),
 dict(id="RC33M2-005",
      claim="En forelder med delt ordinær barnetrygd faar 1184 kroner i maneden fra NAV.",
      rel="C", crit=False, group="aggcomp",
      flags=["quantity-money", "comparator-ne"],
      qty="MONEY:1184:NOK:DERIVED", tapp="CURRENT_MATCH",
      capp=True, crel="=", role="COMPONENT", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("54", [14, 14]), ev=[("S1", ("54", 14))]),
 dict(id="RC33M2-006",
      claim="En forelder med delt fast bosted og innvilget delt utvidet barnetrygd faar totalt 2292 kroner i maneden, som er mer enn 2200 kroner per maned.",
      rel="E", crit=False, group="comparator",
      flags=["quantity-money", "aggregate", "comparator-gt"],
      qty="MONEY:2292:NOK:AGGREGATE", tapp="CURRENT_MATCH",
      capp=True, crel=">", role="AGGREGATE", sup=["S1", "S2"],
      dim={"numeric_quantity": "NUMERIC_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("54", [14, 24]), ev=[("S1", ("54", 14)), ("S2", ("54", 24))]),
 dict(id="RC33M2-007",
      claim="Delt ordinær barnetrygd er na 1006 kroner per forelder per maned.",
      rel="E", crit=True, group="comparator",
      flags=["quantity-money", "comparator-eq"],
      qty="MONEY:1006:NOK", tapp="CURRENT_MATCH",
      capp=True, crel="=", role="COMPONENT", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("54", [14, 14]), ev=[("S1", ("54", 14))]),
 dict(id="RC33M2-008",
      claim="Delt ordinær barnetrygd er na minst 1106 kroner per forelder per maned.",
      rel="C", crit=True, group="comparator",
      flags=["quantity-money", "comparator-ge"],
      qty="MONEY:1106:NOK", tapp="CURRENT_MATCH",
      capp=True, crel=">=", role="COMPONENT", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("54", [14, 14]), ev=[("S1", ("54", 14))]),
 dict(id="RC33M2-009",
      claim="Barnevernet skal gjennomgaa en innsendt bekymringsmelding senest innen 1 uke.",
      rel="E", crit=True, group="periods",
      flags=["quantity-period"],
      qty="PERIOD:1:WEEK", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"clause_coverage": "EXACT_MATCH"},
      src=("38", [27, 27]), ev=[("S1", ("38", 27))]),
 dict(id="RC33M2-010",
      claim="Barnevernet skal gjennomgaa en innsendt bekymringsmelding innen 14 dager.",
      rel="C", crit=True, group="periods",
      flags=["quantity-period"],
      qty="PERIOD:14:DAY", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"numeric_quantity": "NUMERIC_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("38", [27, 27]), ev=[("S1", ("38", 27))]),
 dict(id="RC33M2-011",
      claim="Undersokelsen etter en bekymringsmelding skal vaere ferdig innen tre maneder.",
      rel="R", crit=False, group="periods",
      flags=["quantity-period"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"clause_coverage": "RELEVANT_BUT_UNRESOLVED"},
      src=("38", [28, 28]), ev=[("S1", ("38", 28))]),
 dict(id="RC33M2-012",
      claim="Undersokelsessaken hos barnevernet kan under ingen omstendigheter utvides utover 3 maneder totalt.",
      rel="C", crit=False, group="periods",
      flags=["quantity-period", "negation-exception"],
      qty="PERIOD:3:MONTH", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"exception": "EXCEPTION_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("38", [28, 28]), ev=[("S1", ("38", 28))]),
 dict(id="RC33M2-013",
      claim="Gyldigheten til en meklingsattest varer i seks maneder etter at meklingen er gjennomfort.",
      rel="E", crit=False, group="periods",
      flags=["quantity-period"],
      qty="PERIOD:6:MONTH", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"clause_coverage": "EXACT_MATCH"},
      src=("34", [32, 32]), ev=[("S1", ("34", 32))]),
 dict(id="RC33M2-014",
      claim="En forelder uten delt fast bosted kan faa utvidet barnetrygd pa 1286 kroner i maneden hvis vilkarene er oppfylt.",
      rel="R", crit=False, group="sameqty",
      flags=["quantity-money", "condition"],
      qty="MONEY:1286:NOK", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"condition": "EXACT_MATCH", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("54", [23, 23]), ev=[("S1", ("54", 23))]),
 dict(id="RC33M2-015",
      claim="Den obligatoriske meklingen gjelder ogsa ektefeller uten felles barn.",
      rel="R", crit=False, group="modality",
      flags=["actor", "condition"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "SAME_ACTOR", "condition": "EXACT_MATCH"},
      src=("34", [11, 11]), ev=[("S1", ("34", 11))]),
 dict(id="RC33M2-016",
      claim="Mekleren foerer ikke journal etter mekling.",
      rel="E", crit=False, group="negation",
      flags=["negation"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"polarity": "EXACT_MATCH", "clause_coverage": "EXACT_MATCH"},
      src=("34", [33, 33]), ev=[("S1", ("34", 33))]),
 dict(id="RC33M2-017",
      claim="Mekleren har en plikt til a foere journal etter mekling.",
      rel="C", crit=True, group="negation",
      flags=["negation", "modality-skal"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1", "S2"],
      dim={"polarity": "EXPLICIT_CONFLICT", "modality": "DEONTIC_OPPOSITION"},
      src=("34", [33, 38]), ev=[("S1", ("34", 33)), ("S2", ("34", 38))]),
 dict(id="RC33M2-018",
      claim="En samvarsforelder kan gi samtykke til helsehjelp for barn under 16 ar i kraft av samvaret.",
      rel="C", crit=True, group="negation",
      flags=["negation", "actor"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "DIFFERENT_ACTOR", "polarity": "EXPLICIT_CONFLICT"},
      src=("41", [11, 11]), ev=[("S1", ("41", 11))]),
 dict(id="RC33M2-019",
      claim="Barn under 12 ar kan selv gi samtykke til helsehjelp for forhold foreldrene ikke er informert om.",
      rel="R", crit=False, group="modality",
      flags=["actor", "condition", "negation"],
      qty="AGE:12:YEAR", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "SAME_ACTOR", "condition": "EXACT_MATCH", "exception": "EXACT_MATCH"},
      src=("41", [13, 13]), ev=[("S1", ("41", 13))]),
 dict(id="RC33M2-020",
      claim="Meninger fra barn 12 ar og eldre skal vege tungt i saker om fast bosted eller samvar.",
      rel="E", crit=False, group="modality",
      flags=["actor", "modality-skal"],
      qty="AGE:12:YEAR", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "SAME_ACTOR", "modality": "EXACT_MATCH"},
      src=("36", [11, 11]), ev=[("S1", ("36", 11))]),
 dict(id="RC33M2-021",
      claim="Fra 15 ar er barnet part i barnevernssaker.",
      rel="E", crit=False, group="modality",
      flags=["actor"],
      qty="AGE:15:YEAR", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "SAME_ACTOR", "clause_coverage": "EXACT_MATCH"},
      src=("36", [26, 26]), ev=[("S1", ("36", 26))]),
 dict(id="RC33M2-022",
      claim="Skolehelsetjenesten har henvisningsrett til BUP.",
      rel="C", crit=False, group="modality",
      flags=["actor", "modality-kan"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"actor": "DIFFERENT_ACTOR", "polarity": "EXPLICIT_CONFLICT"},
      src=("31", [64, 64]), ev=[("S1", ("31", 64))]),
 dict(id="RC33M2-023",
      claim="Skolehelsetjenesten kan i noen kommuner skrive ut legemidler.",
      rel="R", crit=False, group="modality",
      flags=["modality-kan", "exception"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"clause_coverage": "EXACT_MATCH", "polarity": "EXACT_MATCH"},
      src=("31", [14, 14]), ev=[("S1", ("31", 14))]),
 dict(id="RC33M2-024",
      claim="Overgangsforskriften FOR-2026-06-25-1361 trer i kraft 01.07.2026.",
      rel="E", crit=False, group="effdate",
      flags=["temporal-ikraft", "law-ref"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"temporal": "TEMPORAL_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("68", [4, 4]), ev=[("S1", ("68", 4))]),
 dict(id="RC33M2-025",
      claim="Overgangsforskriften FOR-2026-06-25-1361 var i kraft allerede 01.02.2026.",
      rel="C", crit=True, group="effdate",
      flags=["temporal-ikraft", "law-ref", "date-trap"],
      qty=None, tapp="PERIOD_MISMATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"temporal": "TEMPORAL_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("68", [4, 4]), ev=[("S1", ("68", 4))]),
 dict(id="RC33M2-026",
      claim="Endringen av overgangsforskriften ved FOR-2026-08-17-1633 trer i kraft 01.09.2026.",
      rel="R", crit=False, group="superseded",
      flags=["law-ref", "temporal-superseded"],
      qty=None, tapp="UNKNOWN",
      capp=False, crel=None, role="STANDALONE", sup=["S1", "S2"],
      dim={"temporal": "TEMPORAL_COMPATIBLE", "clause_coverage": "EXACT_MATCH"},
      src=("68", [4, 16]), ev=[("S1", ("68", 4)), ("S2", ("68", 16))]),
 dict(id="RC33M2-027",
      claim="En soknad sendt 15.06.2026 behandles etter de gamle reglene.",
      rel="R", crit=False, group="superseded",
      flags=["law-ref", "transition-rule"],
      qty=None, tapp="PERIOD_MISMATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"temporal": "TEMPORAL_COMPATIBLE", "numeric_quantity": "NUMERIC_COMPATIBLE"},
      src=("68", [48, 48]), ev=[("S1", ("68", 48))]),
 dict(id="RC33M2-028",
      claim="Overgangsforskriften opphorer a gjelde 30.06.2031.",
      rel="C", crit=False, group="superseded",
      flags=["temporal-superseded", "law-ref"],
      qty=None, tapp="SUPERSEDED",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"temporal": "TEMPORAL_CONFLICT", "clause_coverage": "PARTIAL_OVERLAP"},
      src=("68", [49, 49]), ev=[("S1", ("68", 49))]),
 dict(id="RC33M2-029",
      claim="Midlertidig bortfall kan gjelde ved medlemmets sykdom.",
      rel="R", crit=False, group="superseded",
      flags=["law-ref", "condition"],
      qty="PERIOD:1:MONTH", tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"condition": "EXACT_MATCH", "clause_coverage": "EXACT_MATCH"},
      src=("68", [47, 47]), ev=[("S1", ("68", 47))]),
 dict(id="RC33M2-030",
      claim="Skolehelsetjenesten er et behandlingstilbud for psykiske lidelser.",
      rel="C", crit=False, group="negation",
      flags=["negation", "scope"],
      qty=None, tapp="CURRENT_MATCH",
      capp=False, crel=None, role="STANDALONE", sup=["S1"],
      dim={"polarity": "EXPLICIT_CONFLICT", "scope": "SCOPE_CONFLICT"},
      src=("31", [24, 24]), ev=[("S1", ("31", 24))]),
]


def build_public_and_pass1():
    cases = []
    pass1 = {}
    for c in CASES:
        k, (a, b) = c["src"]
        srcs = [{"kb_ref": f"kb/{S[k][0].name}", "lines": [a, b],
                 "text": "\n".join(L(k, *range(a, b + 1)))}]
        ev = [{"span_id": sid, "text": span(k, n)} for sid, (kk, n) in c["ev"]]
        pub = {"case_id": c["id"], "claim": c["claim"],
               "sources": srcs, "evidence": ev,
               "compound": c["group"] == "aggcomp",
               "public_flags": c["flags"]}
        cases.append(pub)
        pass1[c["id"]] = {
            "semantic_relation": PS[c["rel"]],
            "critical": c["crit"],
            "group": c["group"],
            "semantic_quantity_identity": c["qty"],
            "temporal_applicability": c["tapp"],
            "comparator_applicable": c["capp"],
            "comparator_relation": c["crel"],
            "aggregate_component_role": c["role"],
            "supporting_spans": c["sup"],
            "expected_dimension_evidence": c["dim"],
        }
    return cases, pass1


def check_fidelity(cases):
    # mechanical source fidelity: every evidence span verbatim in KB line
    for c in cases:
        for sid, (k, n) in c["ev"]:
            if span(k, n) is None:
                raise SystemExit(f"FIDELITY_FAIL {c['id']} {sid}")


QUOTA_REQUIRED = {
    "entails": 10, "contradicts": 11, "rbi": 9, "critical": 9,
    "comparator_applicable": 8, "quantity_identity_applicable": 17,
    "temporal_applicable": 30, "non_numeric": 13,
    "negation_tagged": 6,
}


def main():
    check_fidelity(CASES)
    cases, pass1 = build_public_and_pass1()
    rel_counts = {}
    for v in pass1.values():
        rel_counts[v["semantic_relation"]] = rel_counts.get(
            v["semantic_relation"], 0) + 1
    quota = {
        "entails": rel_counts.get("SUPPORTED", 0),
        "contradicts": rel_counts.get("CONTRADICTED", 0),
        "rbi": rel_counts.get("REVIEW_REQUIRED", 0),
        "critical": sum(1 for v in pass1.values() if v["critical"]),
        "comparator_applicable": sum(
            1 for v in pass1.values() if v["comparator_applicable"]),
        "quantity_identity_applicable": sum(
            1 for v in pass1.values() if v["semantic_quantity_identity"]),
        "temporal_applicable": sum(
            1 for v in pass1.values()
            if v["temporal_applicability"] != "NOT_APPLICABLE"),
        "non_numeric": sum(
            1 for v in pass1.values()
            if not v["semantic_quantity_identity"]),
        "negation_tagged": sum(
            1 for c in CASES if "negation" in c["flags"]
            or "negation-exception" in c["flags"]),
    }
    if quota != QUOTA_REQUIRED:
        raise SystemExit(f"QUOTA_FAIL {quota} != {QUOTA_REQUIRED}")

    public = {"set_id": "RC33M2-MICROVAL-V1", "case_count": 30,
              "cases": cases}
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RC3.3.2 fresh micro-validation cases",
        "type": "object",
        "required": ["set_id", "case_count", "cases"],
        "properties": {
            "set_id": {"const": "RC33M2-MICROVAL-V1"},
            "case_count": {"type": "integer", "const": 30},
            "cases": {"type": "array", "minItems": 30, "maxItems": 30,
                      "items": {
                          "type": "object",
                          "required": ["case_id", "claim", "sources",
                                       "evidence"],
                          "properties": {
                              "case_id": {"pattern": "^RC33M2-[0-9]{3}$"},
                              "claim": {"type": "string", "minLength": 10},
                              "sources": {"type": "array"},
                              "evidence": {"type": "array", "items": {
                                  "type": "object",
                                  "required": ["span_id", "text"],
                                  "properties": {
                                      "span_id": {"type": "string"},
                                      "text": {"type": "string"}}}},
                              "compound": {"type": "boolean"},
                              "public_flags": {"type": "array",
                                               "items": {"type": "string"}},
                          },
                          "additionalProperties": False,
                      }},
        },
        "additionalProperties": False,
    }
    out_cases = json.dumps(public, ensure_ascii=False, indent=1) + "\n"
    write_guard.write_text(TASK / "microvalidation-cases.json", out_cases)
    write_guard.write_text(
        TASK / "microvalidation-cases.schema.json",
        json.dumps(schema, ensure_ascii=False, indent=1) + "\n")
    audit = {
        "pass1_labels": pass1,
        "quota_pass1": {"observed": quota,
                        "required": QUOTA_REQUIRED,
                        "pass": quota == QUOTA_REQUIRED},
        "coverage_tags": {
            "stale_or_current_numeric": [
                c["id"] for c in CASES if c["group"] in
                ("curhist", "comparator", "aggcomp", "sameqty", "periods",
                 "effdate", "superseded") and c["qty"]],
            "comparator": [c["id"] for c in CASES if c["capp"]],
            "quantity_identity": [c["id"] for c in CASES if c["qty"]],
            "aggregate_component_derived": [c["id"] for c in CASES
                                            if c["role"] in
                                            ("AGGREGATE", "COMPONENT")],
            "temporal": [c["id"] for c in CASES],
            "modality_condition_actor_scope": [c["id"] for c in CASES
                                               if c["group"] in
                                               ("modality", "sameqty",
                                                "effdate")],
            "negation": [c["id"] for c in CASES if c["group"] ==
                         "negation" or "negation-exception" in c["flags"]],
            "non_numeric": [c["id"] for c in CASES if not c["qty"]],
            "law_ref_traps": [c["id"] for c in CASES if "law-ref" in
                              c["flags"]],
        },
        "critical_ids": [c["id"] for c in CASES if c["crit"]],
    }
    write_guard.write_text(
        HERE / "pass1-labels.json",
        json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    sha = hashlib.sha256(out_cases.encode("utf-8")).hexdigest()
    print("AUTHOR_OK cases_sha256", sha)
    print("QUOTA", json.dumps(quota, sort_keys=True))


if __name__ == "__main__":
    main()
