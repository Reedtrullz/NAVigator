#!/usr/bin/env python3
"""Unit tests for Tier-1 operators + validator (spec 18).

Assert-based, no frameworks. Exit 1 on any failure.
Canaries: N-R1 and ENT-C texts must never yield CONTRADICTED proofs.
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tier1_operators as ops
import proof_validator as pv

FAILS = []
COUNT = {"pass": 0, "fail": 0}


def check(name, cond):
    if cond:
        COUNT["pass"] += 1
    else:
        COUNT["fail"] += 1
        FAILS.append(name)


def res(p):
    return p["result"] if p else None


# ---------------- DIRECT_ASSERTION
da_pos = ops.direct_assertion("Ordningen er gratis.",
                              "Ordningen er kostnadsfritt for brukerne.")
check("DA positive support", da_pos is not None and
      res(da_pos) == "SUPPORTED" and da_pos["premises"] == ["S1"])
check("DA negative absent concept",
      ops.direct_assertion("Ordningen er rask.",
                           "Ordningen er kostnadsfritt.") is None)
check("DA missing subject precondition",
      ops.direct_assertion("Tjenesten er gratis.",
                           "Ordningen er kostnadsfritt.") is None)
check("DA universal-vs-source scope mismatch",
      ops.direct_assertion("Alle faar ordningen gratis.",
                           "Ordningen er kostnadsfritt.") is None)
check("DA temporal mismatch abstains",
      ops.direct_assertion("Ordningen var gratis 01.01.2020.",
                           "Ordningen er kostnadsfritt 01.01.2024.") is None)
check("DA different-concept near-miss abstains",
      ops.direct_assertion("Legen stiller diagnose.",
                           "Legen gir behandling.") is None)
da_neg = ops.direct_assertion("Ordningen koster 200 kr.",
                              "Ordningen har en kostnad pa 200 kr.")
check("DA equal-negative polarity support", da_neg is not None and
      res(da_neg) == "SUPPORTED")

# ---------------- EXPLICIT_NEGATION
en_contra = ops.explicit_negation("BUP stiller diagnoser.",
                                  "BUP stiller ikke diagnoser.")
check("EN valid contradiction", en_contra is not None and
      res(en_contra) == "CONTRADICTED")
en_support = ops.explicit_negation("Ordningen krever ikke henvisning.",
                                   "Ordningen krever henvisning.")
check("EN negation-on-claim support", en_support is not None and
      res(en_support) == "SUPPORTED")
check("EN different-axis negation near-miss abstains",
      ops.explicit_negation("Ordningen krever ikke henvisning.",
                            "Ordningen gir ikke behandling.") is None)
check("EN exception marker abstains",
      ops.explicit_negation(
          "BUP stiller diagnoser.",
          "BUP stiller ikke diagnoser; dette gjelder ikke voksne.") is None)
nr1 = ops.explicit_negation("Helsesykepleier stiller ADHD-diagnose.",
                            "Skolehelsetjenesten stiller ikke diagnoser.")
check("EN N-R1 canary: staff negation never binds", nr1 is None)
proofs_nr1, crashed1 = ops.run_operators(
    "Helsesykepleier stiller ADHD-diagnose.",
    "Skolehelsetjenesten stiller ikke diagnoser.")
check("N-R1 full gate: no CONTRADICTED proof",
      not crashed1 and not [p for p in proofs_nr1
                            if p["result"] == "CONTRADICTED"])
entc, crashed2 = ops.run_operators(
    "PPT kan stille ADHD-diagnose.",
    "PPT kartlegger pedagogiske behov og gir sakkyndige vurderinger. "
    "BUP utreder psykiske lidelser/nevroutviklingsforstyrrelser.")
check("ENT-C full gate: no CONTRADICTED proof",
      not crashed2 and not [p for p in entc
                            if p["result"] == "CONTRADICTED"])

# ---------------- NUMERIC_CONFLICT
num_ok = ops.numeric_conflict("Satsen er maksimalt 5000 kr.",
                              "Satsen er 6500 kr.")
check("NUM valid conflict", num_ok is not None and
      res(num_ok) == "CONTRADICTED")
check("NUM no framing abstains",
      ops.numeric_conflict("Det er 5000 kr.", "Det er 6500 kr.") is None)
check("NUM unit mismatch abstains",
      ops.numeric_conflict("Ventetiden er maksimalt 6 maneder.",
                           "Ventetiden er maksimalt 6 uker.") is None)
check("NUM missing subject abstains",
      ops.numeric_conflict("Andelen er 50 prosent.",
                           "Gjennomsnittet er 65 prosent.") is None)
check("NUM temporal mismatch abstains",
      ops.numeric_conflict("Satsen per 01.01.2023 er maksimalt 5000 kr.",
                           "Satsen per 01.01.2024 er 6500 kr.") is None)
check("NUM locale conflict abstains",
      ops.numeric_conflict("Satsen er maksimalt 5000 kr i Trondheim.",
                           "Satsen er 6500 kr i Bergen.") is None)
check("NUM G-unit conflict fires",
      res(ops.numeric_conflict(
          "Det er ingen stonad ved inntekt over 4 G.",
          "Ingen stonad ved pensjonsgivende inntekt over 6 G.")) ==
      "CONTRADICTED")
check("NUM G-word boundary does not lex as unit",
      ops.numeric_conflict(
          "Ventetiden er over 6 ganger lenger enn lovet.",
          "Ventetiden ble 12 ganger lenger.") is None)
check("NUM mixed conjuncts abstain (partial conflict)",
      ops.numeric_conflict(
          "Satsen er 100 kr per dag og maksimalt 5000 kr totalt.",
          "Satsen er 200 kr per dag.") is None)
check("NUM dummy-subject conflict fires",
      res(ops.numeric_conflict(
          "Det er ingen stonad ved inntekt over 4 G.",
          "Ingen stonad ved pensjonsgivende inntekt over 6 G.")) ==
      "CONTRADICTED")

# ---------------- longest-match normalization + fragment propagation
check("LMF: 'ingen kostnad' is positive free_of_charge",
      __import__("polarity_engine_v02")._concept_polarity(
          "Ingen kostnad.", "free_of_charge") == (1, "ingen kostnad"))
check("LMF: bare 'kostnad' stays negative",
      __import__("polarity_engine_v02")._concept_polarity(
          "Det er en kostnad.", "free_of_charge") == (-1, "kostnad"))
check("LMF: 'ingen henvisning' alias recognized",
      __import__("polarity_engine_v02")._concept_polarity(
          "Ingen henvisning.", "requires_referral") == (-1, "ingen henvisning"))
frag = ops.direct_assertion(
    "Trondheimshjelpa er et lavterskeltilbud man kan kontakte uten henvisning.",
    "Trondheimshjelpa er et lavterskeltilbud til familier. "
    "Gratis, ingen henvisning.")
check("DA fragment propagation support", frag is not None and
      res(frag) == "SUPPORTED")
check("DA fragment with own actor does not inherit subject",
      ops.direct_assertion(
          "Trondheimshjelpa tilbyr kurs.",
          "Trondheimshjelpa er et lavterskeltilbud. "
          "NAV tilbyr kurs og grupper.") is None)

# ---------------- TEMPORAL_CONFLICT
tmp_ok = ops.temporal_conflict("Fristen er 01.03.2024.",
                               "Fristen er 15.02.2024.")
check("TMP valid conflict", tmp_ok is not None and
      res(tmp_ok) == "CONTRADICTED")
check("TMP no shared topic abstains",
      ops.temporal_conflict("Fristen er 01.03.2024.",
                            "Regnskapsaret endte 31.12.2023.") is None)
check("TMP identical dates abstain",
      ops.temporal_conflict("Fristen er 01.03.2024.",
                            "Fristen er 01.03.2024.") is None)
check("TMP granularity mismatch abstains",
      ops.temporal_conflict("Fristen er i mars 2024.",
                            "Fristen er 01.03.2024.") is None)

# ---------------- SIMPLE_ARITHMETIC
ari_ok = ops.simple_arithmetic(
    "Satsen blir til sammen 8000 kr.",
    "Satsen har en grunnandel pa 5000 kr. Satsen har et tillegg pa 3000 kr.")
check("ARI valid sum", ari_ok is not None and res(ari_ok) == "SUPPORTED" and
      ari_ok["premises"] == ["S1", "S2"] and
      ari_ok["detail"]["relation"] == "sum")
ari_amb = ops.simple_arithmetic(
    "Satsen blir til sammen 8000 kr.",
    "Satsen har en grunnandel pa 5000 kr. Satsen har et tillegg pa 3000 kr. "
    "Satsen har en maksimal ramme pa 11000 kr.")
check("ARI ambiguity abstains", ari_amb is None)
check("ARI recompute mismatch abstains",
      ops.simple_arithmetic(
          "Satsen blir til sammen 9000 kr.",
          "Satsen har en grunnandel pa 5000 kr. Satsen har et tillegg pa "
          "3000 kr.") is None)
check("ARI unit mixing abstains",
      ops.simple_arithmetic(
          "Satsen blir til sammen 8000 kr.",
          "Andelen er 50 prosent. Andelen er 30 prosent.") is None)
check("ARI missing arithmetic framing abstains",
      ops.simple_arithmetic(
          "Satsen er 8000 kr.",
          "Satsen har en grunnandel pa 5000 kr. Satsen har et tillegg pa "
          "3000 kr.") is None)

# ---------------- PROOF VALIDATOR
good = ops.direct_assertion("Ordningen er gratis.",
                            "Ordningen er kostnadsfritt.")
ok, why = pv.validate(good, "Ordningen er gratis.",
                      "Ordningen er kostnadsfritt.")
check("VAL accepts valid proof", ok)
bad_span = dict(good)
bad_span["premises"] = ["S9"]
ok, why = pv.validate(bad_span, "Ordningen er gratis.",
                      "Ordningen er kostnadsfritt.")
check("VAL rejects missing span", not ok and "span" in why)
flipped = dict(good)
flipped["result"] = "CONTRADICTED"
ok, why = pv.validate(flipped, "Ordningen er gratis.",
                      "Ordningen er kostnadsfritt.")
check("VAL rejects flipped result", not ok and "mismatch" in why)
external = dict(good)
external["derived_fact"] = "helt annen paastand uten kildedekning her"
ok, why = pv.validate(external, "Ordningen er gratis.",
                      "Ordningen er kostnadsfritt.")
check("VAL rejects external fact", not ok and "external" in why)
ok, why = pv.validate({"operator": "NOPE"}, "a", "b")
check("VAL rejects unknown operator", not ok)

print("PASS", COUNT["pass"], "FAIL", COUNT["fail"])
for f in FAILS:
    print("  FAILED:", f)
sys.exit(1 if COUNT["fail"] else 0)
