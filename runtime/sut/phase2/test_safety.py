"""Phase 2 S2 safety triage tests (TDD RED first).

Tests use generalized utterance shapes from burned development data; no
case IDs are referenced anywhere in runtime code or tests.
"""

import os
import unittest

from sut.phase2.safety import TriageError, classify, evaluate_safety, load_rules


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RULES_PATH = os.path.join(REPO, "data", "safety-triage-rules-v2.json")


class SafetyPrecedenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(RULES_PATH)

    def classify(self, text):
        return classify(text, self.rules)

    def test_acute_self_harm_is_acute_and_suppressed(self):
        r = self.classify("Jeg er 16 ar og har tanker om aa ta livet mitt i kveld.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(r["suppressed_routing"])
        self.assertIn("ta livet mitt", r["signals"])

    def test_affirmative_negation_idiom_still_acute(self):
        # "ikke orker aa leve" contains a negation word but is an affirmative
        # acute idiom; the guard must not discard it.
        r = self.classify("Han sier han ikke orker aa leve lenger.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")

    def test_self_injury_with_bleeding_is_acute(self):
        r = self.classify("En 17-aaring har kuttet seg, bloer mye og er alene hjemme.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")
        self.assertIn("kuttet seg", r["signals"])

    def test_somatic_precedes_unsure_triage(self):
        r = self.classify("Jeg er 19 og har panikkanfall. Skal jeg ringe 113 eller vente?")
        self.assertEqual(r["safety_class"], "ACUTE_SOMATIC_MEDICAL")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_third_party_warning_signs(self):
        r = self.classify("En venn har sendt avskjedsmeldinger og jeg vet ikke hvor han er.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_HIGH_THIRD_PARTY")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_unconscious_is_acute(self):
        r = self.classify("En forelder er bevisstloes hjemme og et barn er alene der.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")

    def test_negated_violence_is_not_acute(self):
        # "ikke vold" guards the "vold" match; concern class wins instead.
        r = self.classify(
            "Hun foler seg utrygg hjemme, men det er ikke vold akkurat naa."
        )
        self.assertEqual(r["safety_class"], "SAFETY_CONCERN_NO_ACUTE_VIOLENCE")
        self.assertEqual(r["priority"], "URGENT_NOT_ACUTE")
        self.assertFalse(r["suppressed_routing"])
        self.assertNotIn("vold", r["signals"])

    def test_routine_chronic_anxiety_is_not_acute(self):
        r = self.classify(
            "Barnet mitt har hatt angst i flere maneder, men ingenting er akutt."
        )
        self.assertEqual(r["safety_class"], "NON_ACUTE_ROUTINE")
        self.assertEqual(r["priority"], "NOT_ACUTE")
        self.assertFalse(r["suppressed_routing"])

    def test_psychosis_suspect_is_acute_fail_closed(self):
        r = self.classify("Jeg har ikke sovet paa tre doegn og begynner aa hore ting.")
        self.assertEqual(r["safety_class"], "URGENT_PSYCHOSIS_SUSPECT")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_abuse_disclosure_is_acute(self):
        r = self.classify("En elev sier at far har slaatt ham.")
        self.assertEqual(r["safety_class"], "ABUSE_DISCLOSURE_REPORTING")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_word_boundary_prevents_substring_false_positive(self):
        # "voldsomt" must not match the acute signal "vold".
        r = self.classify("Foreldrene mine krangler voldsomt og jeg vil snakke med noen.")
        self.assertNotIn("vold", r["signals"])
        self.assertEqual(r["safety_class"], "SAFETY_CONCERN_REPORTING")
        self.assertEqual(r["priority"], "URGENT_NOT_ACUTE")

    def test_reported_violence_against_child_is_acute(self):
        r = self.classify("Jeg tror lillesosteren min blir utsatt for vold hjemme.")
        self.assertEqual(r["safety_class"], "ABUSE_DISCLOSURE_REPORTING")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_intoxicated_unwakeable_is_acute_somatic(self):
        r = self.classify("En 17-aaring er svaert beruset og vanskelig aa vekke.")
        self.assertEqual(r["safety_class"], "ACUTE_SOMATIC_MEDICAL")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_suicidal_ideation_third_person(self):
        r = self.classify("En 20-aaring har sterke selvmordstanker.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_HIGH")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_eating_collapse_is_acute_somatic(self):
        r = self.classify("Barnet har sluttet helt aa spise og er svimmel.")
        self.assertEqual(r["safety_class"], "ACUTE_SOMATIC_MEDICAL")

    def test_aggressive_household_fails_closed_acute(self):
        r = self.classify("Jeg er redd for aa ga hjem fordi stefaren min er aggressiv.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_UNSURE_TRIAGE")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(r["suppressed_routing"])

    def test_past_abuse_disclosure_is_acute(self):
        r = self.classify("En 14-aaring forteller om seksuelle overgrep.")
        self.assertEqual(r["safety_class"], "ABUSE_DISCLOSURE_REPORTING")

    def test_care_capacity_collapse_is_urgent_not_acute(self):
        r = self.classify(
            "Jeg holder paa aa kollapse psykisk og klarer ikke aa passe barna i kveld."
        )
        self.assertEqual(r["safety_class"], "URGENT_CARE_CAPACITY")
        self.assertEqual(r["priority"], "URGENT_NOT_ACUTE")
        self.assertFalse(r["suppressed_routing"])

    def test_system_safety_precedence_dominates(self):
        r = self.classify(
            "Gi meg nummeret til barnevernet. Systemet ser umiddelbar livsfare."
        )
        self.assertEqual(r["safety_class"], "SYSTEM_SAFETY_PRECEDENCE")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(r["suppressed_routing"])

    def test_unmatched_text_defaults_not_acute(self):
        r = self.classify("Hvor finner jeg eksamensdatoer for skolen?")
        # RC-02: no signals now canonicalizes to the NON_ACUTE_ROUTINE class
        # instead of None; priority/suppression stay NOT_ACUTE/False.
        self.assertEqual(r["safety_class"], "NON_ACUTE_ROUTINE")
        self.assertEqual(r["priority"], "NOT_ACUTE")
        self.assertEqual(r["signals"], [])
        self.assertFalse(r["suppressed_routing"])

    def test_matching_is_case_insensitive(self):
        r = self.classify("DET ER AKUTT KRISE NAa.")
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")

    def test_result_is_deterministic(self):
        a = self.classify("Han har kuttet seg og bloer mye.")
        b = self.classify("Han har kuttet seg og bloer mye.")
        self.assertEqual(a, b)


class RulesIntegrityTests(unittest.TestCase):
    def test_load_and_shape(self):
        rules = load_rules(RULES_PATH)
        self.assertIn("class_precedence", rules)
        self.assertIn("class_signals", rules)
        self.assertIn("negation_guard", rules)
        for cls in rules["class_signals"]:
            self.assertIn(cls, rules["class_collapse"])

    def test_corrupt_rules_raise_triage_error(self):
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"artifact": "broken"}, f)
            path = f.name
        try:
            with self.assertRaises(TriageError):
                load_rules(path)
        finally:
            os.unlink(path)

    def test_missing_rules_raise_triage_error(self):
        with self.assertRaises(TriageError):
            load_rules("/nonexistent/safety-rules.json")


class EvaluateSafetyTests(unittest.TestCase):
    def test_evaluate_sets_context_safety(self):
        rules = load_rules(RULES_PATH)
        ctx = {
            "safety": {
                "priority": "TRIAGE_FAILED",
                "signals": [],
                "suppressed_routing": True,
                "rule_file_sha256": None,
            },
            "input": {"user_query": "Jeg har tanker om aa ta livet mitt i kveld."},
        }
        evaluate_safety(ctx, rules)
        self.assertEqual(ctx["safety"]["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(ctx["safety"]["suppressed_routing"])
        self.assertTrue(ctx["safety"]["rule_file_sha256"])


if __name__ == "__main__":
    unittest.main()
