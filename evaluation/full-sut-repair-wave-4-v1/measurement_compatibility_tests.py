"""Wave 4 Phase B measurement compatibility tests (spec sections 29-30).

Synthetic/generic fixtures only. No gold, no case IDs, no burned corpus
strings. Writes measurement-compatibility-tests.json.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import measurement_route_adapter as A


def structured_route(**over):
    base = {
        "route_id": "R-TEST-01",
        "service_identity": "Kommunal psykologtjeneste",
        "display_label": "Kommunal psykologtjeneste",
        "target_population": "Barn og unge",
        "access_model": ["self_referral"],
        "track_domain": "mental_health",
        "route_state": "FULLY_VERIFIED",
        "evidence_refs": ["E-1"],
        "provenance_refs": ["P-1"],
        "dims": {
            "service_exists": "VERIFIED", "age_eligible": "VERIFIED",
            "scenario_relevant": "VERIFIED", "access_verified": "VERIFIED",
            "contact_verified": "VERIFIED"},
    }
    base.update(over)
    return base


def answer_with(routes, labels=None, no_route=False):
    if labels is None:
        labels = [r.get("display_label") for r in routes]
    return {
        "routes": labels,
        "no_route_asserted": no_route,
        "evidence": {"structured_routes": routes},
    }


class AdapterObservationTests(unittest.TestCase):
    def test_01_correct_route_object_observed(self):
        obs = A.observe_routes(answer_with([structured_route()]))
        self.assertEqual(obs["mode"], A.STRUCTURED)
        r = obs["routes"][0]
        self.assertEqual(r["identity"], "Kommunal psykologtjeneste")
        self.assertEqual(r["access_model"], ["self_referral"])
        self.assertEqual(r["conditions"]["age_eligible"], "VERIFIED")
        self.assertEqual(r["track_domain"], "mental_health")
        self.assertEqual(r["evidence_refs"], ["E-1"])

    def test_02_wrong_service_target_remains_wrong(self):
        good = structured_route()
        wrong = structured_route(route_id="R-TEST-02",
                                 service_identity="Skattekontoret")
        obs = A.observe_routes(answer_with([good, wrong]))
        ids = [r["identity"] for r in obs["routes"]]
        self.assertNotEqual(ids[0], ids[1])
        self.assertIn("Skattekontoret", ids)

    def test_03_wrong_access_visible_under_required_access(self):
        r = structured_route(access_model=["referral_required"])
        obs = A.observe_routes(answer_with([r]))["routes"][0]
        self.assertEqual(obs["access_model"], ["referral_required"])

    def test_04_missing_condition_remains_incomplete(self):
        dims = structured_route()["dims"]
        dims["contact_verified"] = "UNRESOLVED"
        r = structured_route(dims=dims, route_state="EXISTENCE_ONLY")
        obs = A.observe_routes(answer_with([r]))["routes"][0]
        self.assertEqual(obs["conditions"]["contact_verified"], "UNRESOLVED")

    def test_05_provenance_only_is_not_evaluable(self):
        r = structured_route(route_state="UNVERIFIED")
        obs = A.observe_routes(answer_with([r]))["routes"][0]
        self.assertFalse(obs["evaluable"])
        self.assertTrue(obs["provenance_refs"])

    def test_06_display_label_mismatch_does_not_hide_identity(self):
        r = structured_route(display_label="Hjelp i kommunen")
        obs = A.observe_routes(answer_with([r]))["routes"][0]
        self.assertEqual(obs["identity"], "Kommunal psykologtjeneste")
        self.assertEqual(obs["display_label"], "Hjelp i kommunen")

    def test_07_evidence_from_wrong_route_does_not_bind(self):
        a = structured_route(route_id="R-A", evidence_refs=["E-A"])
        b = structured_route(route_id="R-B", service_identity="Annens tilbud",
                             evidence_refs=["E-B"])
        obs = A.observe_routes(answer_with([a, b]))["routes"]
        self.assertEqual(obs[0]["evidence_refs"], ["E-A"])
        self.assertEqual(obs[1]["evidence_refs"], ["E-B"])

    def test_08_two_routes_remain_distinct(self):
        a = structured_route(route_id="R-A")
        b = structured_route(route_id="R-B", service_identity="Familieteam")
        obs = A.observe_routes(answer_with([a, b]))["routes"]
        self.assertEqual(len(obs), 2)
        self.assertEqual(obs[0]["route_id"], "R-A")
        self.assertEqual(obs[1]["route_id"], "R-B")

    def test_09_legacy_labels_only_preserves_old_behavior(self):
        legacy = {"routes": ["Fastlege", "Helsestasjon"],
                  "no_route_asserted": False}
        obs = A.observe_routes_legacy(legacy)
        self.assertEqual(obs["mode"], A.LEGACY)
        self.assertEqual([r["display_label"] for r in obs["routes"]],
                         ["Fastlege", "Helsestasjon"])
        self.assertIsNone(obs["routes"][0]["identity"])
        self.assertIsNone(obs["routes"][0]["evaluable"])

    def test_10_structured_path_deterministic(self):
        ans = answer_with([structured_route()])
        one = json.dumps(A.observe_routes(ans), sort_keys=True)
        two = json.dumps(A.observe_routes(ans), sort_keys=True)
        self.assertEqual(one, two)

    def test_11_structured_presence_never_falls_back_to_labels(self):
        ans = answer_with([structured_route()], labels=["Annet navn"])
        obs = A.observe_routes(ans)
        self.assertEqual(obs["mode"], A.STRUCTURED)
        self.assertNotIn("Annet navn",
                         [r["display_label"] for r in obs["routes"]])

    def test_12_no_verdict_or_pass_semantics_in_observation(self):
        obs = A.observe_routes(answer_with([structured_route()]))
        blob = json.dumps(obs)
        for token in ("PASS", "FAIL", "CANONICAL_ACCEPTABLE",
                      "EQUIVALENT_ACCEPTABLE", "NO_ACCEPTABLE_ROUTE"):
            self.assertNotIn(token, blob)

    def test_13_counterfactual_c_evidence_alone_never_makes_route(self):
        r = structured_route(service_identity=None,
                             route_state="EXISTENCE_ONLY")
        obs = A.observe_routes(answer_with([r]))["routes"][0]
        self.assertFalse(obs["evaluable"])


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(
        sys.modules["__main__"])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    tests = []
    loader = unittest.defaultTestLoader
    for case in loader.loadTestsFromModule(sys.modules["__main__"])._tests:
        for t in case._tests:
            tests.append(t.id().split(".")[-1])
    out = {
        "artifact": "measurement-compatibility-tests",
        "module": "measurement_compatibility_tests",
        "total": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "pass": result.wasSuccessful(),
        "tests": sorted(set(tests)),
    }
    with open(os.path.join(HERE, "measurement-compatibility-tests.json"),
              "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
