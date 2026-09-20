"""Deterministic engine probes: run with python3 test_engine_probes.py."""
import sys

from rc3_1_engine.proposition import (
    ctx_pairs, numbers, polarity, quantifier_pairs, range_pairs, ranges, toks,
)
from rc3_1_engine.decomposition import decompose_claim


def check(name, got, want):
    assert got == want, f"{name}: got {got!r}, want {want!r}"


def main():
    # Tokenization / numbers
    check("toks-merge", toks("ring 02 800"), ["ring", "02800"])
    check("numbers-phone", numbers("tlf 02800"), [2800])
    # Ranges
    check("ranges", ranges("barn 0-5 ar"), [(0, 5)])
    check("ranges-parguard", ranges("paragraf 3-4"), [])
    check("range_pairs", range_pairs("0-5 dager: 1277"), [((0, 5), 1277)])
    # Quantifiers
    check("quant", quantifier_pairs("alle kommuner opptil 20 kroner"), [("alle", 20)])
    # Context-bound numbers
    check("ctx-akutt", ctx_pairs("ved akutt behov ring 112"), [("akutt", 112)])
    check("ctx-ikke-akutt", ctx_pairs("ikke-akutt henvendelser pa 02800"),
          [("ikke-akutt", 2800)])
    # Polarity (clause-scoped)
    check("pol-neg", polarity("terapitjeneste", "Dette er ikke terapitjeneste"), True)
    check("pol-pos", polarity("terapitjeneste", "Dette er terapitjeneste"), False)
    check("pol-two-token", polarity("akutt", "det er ikke akutt"), True)
    check("pol-cross-clause", polarity("samtale", "Vi gir samtale. Det er ikke terapi."), False)
    # Decomposition
    check("dec-men", decompose_claim(
        "Barn under 18 far barnetrygd, men utbetalingen stopper ved 18 ar"),
        ["Barn under 18 far barnetrygd", "utbetalingen stopper ved 18 ar"])
    check("dec-comma-og", decompose_claim(
        "Sokeren mottar stonad, og betaler skatt av belopet"),
        ["Sokeren mottar stonad", "Sokeren betaler skatt av belopet"])
    check("dec-shared-subject", decompose_claim(
        "NAV gir stonad og dekker kostnader"),
        ["NAV gir stonad", "NAV dekker kostnader"])
    check("dec-ikke-tail", decompose_claim(
        "Tjenesten er gratis, ikke avgiftsbelagt"),
        ["Tjenesten er gratis", "Tjenesten er ikke avgiftsbelagt"])
    check("dec-condition", decompose_claim(
        "Hvis inntekten er lav, kan du fa stonad"),
        ["Hvis inntekten er lav", "kan du fa stonad"])
    check("dec-selv-om", decompose_claim(
        "Rett gjelder, selv om inntekten er hoy"),
        ["Rett gjelder", "Gjelder selv om inntekten er hoy"])
    check("dec-unntak", decompose_claim(
        "Alle faar stonad, med unntak for studenter"),
        ["Alle faar stonad", "Unntak: studenter"])
    check("dec-misleading-og", decompose_claim("Foreldre og barn har rett"),
          ["Foreldre og barn har rett"])
    # Determinism
    c = "Sokeren mottar stonad, og betaler skatt av belopet"
    check("determinism", decompose_claim(c), decompose_claim(c))
    print("ALL PROBES PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
