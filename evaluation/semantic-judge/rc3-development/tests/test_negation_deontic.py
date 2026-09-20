"""Phase A regressions: generalized negation/deontic shapes (spec 18).

Shapes are generalized from V4 failure classes; no case IDs, no literal
expected-label maps. Each entry: (name, claim, source, want_state).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
import engine_rc3 as eng

CASES = [
    # support phrase followed by negation (adjacent sentence, same subject)
    ("neg_after_span_adjacent",
     "Barns inntekt og formue tas med i bostoettevurderingen.",
     "Inntekt foer skatt for soeker og alle i husstanden over 20 aar "
     "telles med. Barns inntekt og formue er ikke med.",
     "ENGINE_UNSAFE"),
    # negation same sentence, after aligned span
    ("neg_after_span_same_sentence",
     "Detteet tilbud dekker alle kostnader.",
     "Detteet tilbud dekker alle kostnader, men dekker ikke reiseutgifter.",
     "ENGINE_PROOF_ACCEPTED"),
    # nested exception after aligned span
    ("nested_exception",
     "Familier har rett til stonad.",
    "Familier har rett til stonad, men unntak gjelder for familier "
    "som allerede mottar tilsvarende stonad fra kommunen.",
     "ENGINE_UNSAFE"),
    # kan vs skal (deontic flip)
    ("kan_vs_skal",
     "Ved fristbrudd kan behandlingsstedet selv velge a ignorere Helfo.",
     "Ved fristbrudd: behandlingsstedet skal kontakte Helfo, som kan "
     "finne alternativt tilbud.",
     "ENGINE_UNSAFE"),
    # ikke krav om
    ("ikke_krav_om",
     "Det er krav om dokumentasjon fra lege.",
    "Det er ikke krav om dokumentasjon fra lege for dette tilbudet.",
     "ENGINE_PROOF_ACCEPTED"),
    # bare dersom
    ("bare_dersom",
     "Du har rett til gratis transport.",
     "Du har rett til gratis transport bare dersom avstanden overstiger "
     "tre kilometer.",
     "ENGINE_UNSAFE"),
    # positive claim + negative exception clause
    ("positive_with_negative_exception",
     "Kommunen gir oekonomisk raadgivning.",
     "Kommunen gir oekonomisk raadgivning. Raadgivningen omfatter ikke "
     "gjeldsavvikling.",
     "ENGINE_UNSAFE"),
    # law-like cross-clause qualifier (som hovedregel)
    ("hovedregel_qualifier",
     "Man faar dekket opphold på senter.",
     "Som hovedregel faar man ikke dekket opphold på senter, men "
     "individuell vurdering kan gis.",
     "ENGINE_UNSAFE"),
    # clean support still auto (guard must not over-fire)
    ("clean_support_passes",
     "Barns inntekt og formue telles med i bruken av botilbud.",
     "Barns inntekt og formue telles med i bruken av botilbud.",
     "ENGINE_PROOF_ACCEPTED"),
    # clean support, adjacent sentence without subject overlap: guard
    # must NOT extend scope across unrelated topics
    ("clean_support_unrelated_adjacent",
     "Helsesykepleier gir helseraadgivning.",
     "Helsesykepleier gir helseraadgivning. Kommunen har eget "
     "oekonomisk tilbud.",
     "ENGINE_PROOF_ACCEPTED"),
    # negation inside claim itself matched by negated source: aligned
    # polarity agrees, no flip -> proof accepted
    ("negation_agreement",
     "Det er ikke krav om henvisning.",
     "Det er ikke krav om henvisning til dette tilbudet.",
     "ENGINE_PROOF_ACCEPTED"),
]


def test_negation_deontic():
    failed = []
    for name, claim, source, want in CASES:
        got = eng.judge_atom(claim, source)
        state = got["proof_state"]
        if state != want:
            failed.append((name, state, want))
    assert not failed, "guard mismatches: %s" % failed


if __name__ == "__main__":
    test_negation_deontic()
    print("negation/deontic regressions: %d/%d PASS"
          % (len(CASES), len(CASES)))
