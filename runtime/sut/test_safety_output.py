"""RC-11 safety vocabulary output tests (spec section 26 matrix).

Invariants:
- the fine triage class reaches the output as top-level safety_priority
- safety.priority keeps the frozen collapsed 3-level contract
- known acute triggers are never downgraded (EMERGENCY_TRIGGER_LOGIC_CHANGED
  invariant: classification logic is untouched by this repair)
- negated acute signals stay guarded (no false acute), fail-closed unknowns
  stay ACUTE_RISK_NOW
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sut.context import make_context  # noqa: E402
from sut.phase2.safety import classify, evaluate_safety, load_rules  # noqa: E402
from sut.phase3.finalize import finalize  # noqa: E402


RULES = load_rules("data/safety-triage-rules-v2.json")


def _ctx(query, tracks=None):
    ctx = make_context({
        "case_id": "SAFE-1",
        "user_query": query,
        "profile": {"age": 17},
    })
    evaluate_safety(ctx, RULES)
    ctx["epistemic_states"]["per_track"] = {}
    if tracks:
        ctx["tracks"] = tracks
    return ctx


class SafetyVocabularyOutputTests(unittest.TestCase):
    def test_immediate_acute_danger(self):
        out = finalize(_ctx("Jeg har tanker om aa ta livet mitt i kveld."))
        self.assertEqual(out["safety_priority"], "ACUTE_RISK_NOW")
        self.assertEqual(out["safety"]["priority"], "ACUTE_RISK_NOW")
        self.assertTrue(out["safety"]["suppressed_routing"])

    def test_urgent_but_not_immediate(self):
        out = finalize(_ctx("Vi holder paa aa kollapse, kan noen hjelpe i dag?"))
        self.assertEqual(out["safety_priority"], "URGENT_CARE_CAPACITY")
        self.assertEqual(out["safety"]["priority"], "URGENT_NOT_ACUTE")

    def test_serious_non_acute_concern(self):
        out = finalize(_ctx("Barnet foler seg utrygg hjemme."))
        self.assertEqual(out["safety_priority"],
                         "SAFETY_CONCERN_NO_ACUTE_VIOLENCE")
        self.assertEqual(out["safety"]["priority"], "URGENT_NOT_ACUTE")

    def test_ordinary_service_navigation(self):
        out = finalize(_ctx("Hvor kan vi fa hjelp til samlivsbrudd i familien?"))
        self.assertEqual(out["safety_priority"], "NON_ACUTE_ROUTINE")
        self.assertEqual(out["safety"]["priority"], "NOT_ACUTE")

    def test_no_safety_signal(self):
        out = finalize(_ctx("Hvilke tilbud finnes for ungdom i kommunen?"))
        self.assertEqual(out["safety_priority"], "NON_ACUTE_ROUTINE")

    def test_ambiguous_negated_acute_signal_is_guarded(self):
        ctx = _ctx("Det er ikke livsfare naa.")
        # Negated acute signal is guarded -> no acute classification.
        self.assertNotEqual(ctx["safety"]["safety_class"], "ACUTE_RISK_NOW")
        self.assertEqual(ctx["safety"]["signals"], [])
        self.assertIn("livsfare", ctx["_s2"]["guarded_signals"])
        out = finalize(ctx)
        self.assertEqual(out["safety_priority"], "NON_ACUTE_ROUTINE")

    def test_affirmative_acute_trigger_not_downgraded(self):
        # Negated self-harm phrasing stays fail-closed acute (frozen trigger
        # logic, untouchable); the affirmative trigger must equally stay.
        negated = classify("jeg har ikke tanker om aa ta livet mitt", RULES)
        self.assertEqual(negated["safety_class"], "ACUTE_RISK_NOW")
        r = classify("jeg orker aa leve", RULES)
        self.assertEqual(r["safety_class"], "ACUTE_RISK_NOW")
        self.assertEqual(r["priority"], "ACUTE_RISK_NOW")

    def test_multi_track_one_acute_safety_track(self):
        ctx = _ctx("Jeg har tanker om aa ta livet mitt i kveld.", tracks=[
            {"track_id": "T1", "domain": "mental_health", "status": "PENDING"},
            {"track_id": "T2", "domain": "economy", "status": "PENDING"},
        ])
        out = finalize(ctx)
        self.assertEqual(out["safety_priority"], "ACUTE_RISK_NOW")
        self.assertTrue(out["safety"]["suppressed_routing"])
        self.assertTrue(out["no_route_asserted"])

    def test_fail_closed_unknown_stays_acute(self):
        ctx = _ctx("Hvor kan vi fa hjelp?")
        ctx["safety"]["priority"] = "NOT_A_REAL_PRIORITY"
        ctx["safety"]["safety_class"] = "ALSO_NOT_REAL"
        out = finalize(ctx)
        self.assertEqual(out["safety_priority"], "ACUTE_RISK_NOW")
        self.assertIsNone(out["safety"]["safety_class"])


if __name__ == "__main__":
    unittest.main()
