"""RC-02 triage granularity tests (generic mechanisms only).

Invariants:
- classification stays deterministic, frozen-rules based (no model authority)
- the 12-class vocabulary reaches the output as safety_class/safety_priority
- explicit acute triggers are never downgraded by the repair
- unknown/failed triage states stay fail-closed ACUTE_RISK_NOW
"""

import unittest

from sut.context import make_context
from sut.phase2.safety import classify, evaluate_safety, load_rules
from sut.phase3.finalize import finalize


REPO_RULES = "data/safety-triage-rules-v2.json"


def ctx_with(query):
    ctx = make_context({
        "case_id": "TRI-1",
        "user_query": query,
        "profile": {"age": 17},
    })
    evaluate_safety(ctx, RULES)
    ctx["epistemic_states"]["per_track"] = {}
    return ctx


RULES = load_rules(REPO_RULES)


class TestClassifyGranularity(unittest.TestCase):
    def test_acute_class_is_untouched(self):
        r = classify("Jeg har tanker om aa ta livet mitt i kveld.", RULES)
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(r["suppressed_routing"])

    def test_urgent_not_acute_class_kept(self):
        r = classify("Vi holder paa aa kollapse, kan noen hjelpe i dag?", RULES)
        self.assertEqual(r["safety_class"], "URGENT_CARE_CAPACITY")
        self.assertEqual(r["priority"], "URGENT_NOT_ACUTE")

    def test_safety_concern_class_kept(self):
        r = classify("Barnet foler seg utrygg hjemme.", RULES)
        self.assertEqual(r["safety_class"], "SAFETY_CONCERN_NO_ACUTE_VIOLENCE")
        self.assertEqual(r["priority"], "URGENT_NOT_ACUTE")

    def test_no_signals_maps_to_non_acute_routine(self):
        r = classify("Hvor kan vi fa hjelp til samlivsbrudd i familien?", RULES)
        self.assertEqual(r["safety_class"], "NON_ACUTE_ROUTINE")
        self.assertEqual(r["priority"], "NOT_ACUTE")

    def test_class_collapse_priorities_unchanged(self):
        for cls, mapping in RULES["class_collapse"].items():
            self.assertIn(mapping["priority"],
                          ("ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE"))


class TestEmissionGranularity(unittest.TestCase):
    def test_ctx_carries_safety_class(self):
        ctx = ctx_with("Jeg er bekymret for en venn som ikke vil leve.")
        self.assertIn("safety_class", ctx["safety"])

    def test_finalize_emits_class_and_collapsed_priority(self):
        """RC-11: the fine class survives at safety_priority; the collapsed
        3-level priority stays in safety.priority."""
        ctx = ctx_with("Jeg foler meg utrygg hjemme.")
        out = finalize(ctx)
        self.assertEqual(out["safety"]["safety_class"],
                         "SAFETY_CONCERN_NO_ACUTE_VIOLENCE")
        self.assertEqual(out["safety_priority"],
                         "SAFETY_CONCERN_NO_ACUTE_VIOLENCE")
        self.assertEqual(out["safety"]["priority"],
                         "URGENT_NOT_ACUTE")

    def test_fail_closed_unknown_priority_maps_acute(self):
        ctx = ctx_with("Hvor kan vi fa hjelp?")
        ctx["safety"]["priority"] = "SOMETHING_INVALID"
        ctx["safety"]["safety_class"] = "ALSO_INVALID"
        out = finalize(ctx)
        self.assertEqual(out["safety_priority"], "ACUTE_RISK_NOW")
        self.assertIsNone(out["safety"]["safety_class"])

    def test_triage_failed_default_stays_fail_closed(self):
        ctx = make_context({
            "case_id": "TRI-2",
            "user_query": "Hvor kan vi fa hjelp?",
            "profile": {"age": 20},
        })
        self.assertEqual(ctx["safety"]["priority"], "TRIAGE_FAILED")
        self.assertIsNone(ctx["safety"]["safety_class"])
        ctx["epistemic_states"]["per_track"] = {}
        out = finalize(ctx)
        self.assertEqual(out["safety_priority"], "ACUTE_RISK_NOW")


if __name__ == "__main__":
    unittest.main()
