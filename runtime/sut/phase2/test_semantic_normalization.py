import unittest

from .decompose import decompose
from .knowledge import _keywords, _score_span
from .safety import classify


RULES = {
    "class_precedence": ["ACUTE_SOMATIC_MEDICAL", "NON_ACUTE_ROUTINE"],
    "class_signals": {"ACUTE_SOMATIC_MEDICAL": ["blor mye"]},
    "class_collapse": {
        "ACUTE_SOMATIC_MEDICAL": {"priority": "ACUTE_RISK_NOW", "suppressed_routing": True},
        "NON_ACUTE_ROUTINE": {"priority": "NOT_ACUTE", "suppressed_routing": False}},
    "negation_guard": {"negation_patterns": ["ikke akutt", "jeg blor ikke mye", "ikke blor", "ikke selvmord"],
                       "non_negated_affirmative_idioms": ["kan ikke slutte a blor mye"],
                       "match_window_chars_before": 30},
}


class SemanticNormalizationTests(unittest.TestCase):
    def test_norwegian_ascii_and_unicode_composition_keep_signal(self):
        for text in ["Jeg blør mye.", "Jeg blor mye.", "JEG BLØR MYE!", "Jeg blo\u0301r mye"]:
            with self.subTest(text=text):
                self.assertEqual(classify(text, RULES)["priority"], "ACUTE_RISK_NOW")

    def test_other_sentence_and_other_signal_negation_do_not_suppress(self):
        for text in ["Det er ikke akutt. Jeg blør mye.",
                     "Ikke selvmord, men jeg blor mye.",
                     "Jeg blor ikke mye. Jeg blor mye."]:
            with self.subTest(text=text):
                self.assertEqual(classify(text, RULES)["priority"], "ACUTE_RISK_NOW")

    def test_negation_of_that_signal_and_affirmative_idiom(self):
        self.assertEqual(classify("Jeg blør ikke mye", RULES)["signals"], [])
        self.assertEqual(classify("Jeg ikke blør mye", RULES)["signals"], [])
        self.assertEqual(classify("Jeg kan ikke slutte å blør mye", RULES)["priority"], "ACUTE_RISK_NOW")

    def test_norwegian_domain_signals_match_ascii(self):
        for text, wanted in [("økonomi", ["financial_support"]),
                             ("rådgivning", ["financial_support"]),
                             ("ra\u030adgivning", ["financial_support"]),
                             ("bostøtte", ["housing", "financial_support"]),
                             ("opplæring", ["education"])]:
            self.assertEqual([t["domain"] for t in decompose(text)], wanted)

    def test_matching_normalizes_keywords_and_span_without_rewriting_source(self):
        source = "Økonomi og bostøtte"
        self.assertEqual(_score_span(source, _keywords("okonomi bostotte")), 2)
        self.assertEqual(_keywords("økonomi bostøtte"), ["okonomi", "bostotte"])
