"""Wave 4 Phase C cross-boundary contract test (spec section 33).

Synthetic fixture: PRODUCT discovery -> build_route_candidates (real
product code) -> serialized route object (same field mapping as the
frozen finalize.py) -> Measurement adapter -> observation. Proves
identity/target/access/condition/track/evidence preservation without the
product importing evaluator code. Writes cross-boundary-contract-tests.json.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "runtime"))
sys.path.insert(0, HERE)

from sut.phase2.routes import build_route_candidates  # noqa: E402
import measurement_route_adapter as A  # noqa: E402


DISCOVERY = {
    "state": "COMPLETED",
    "route_state": None,
    "evidence": [
        {"evidence_id": "E-1", "source_url": "https://example.org/muni",
         "text": "Kommunal psykologtjeneste tar imot selvhenvisning."},
        {"evidence_id": "E-2", "source_url": "https://example.org/spec",
         "text": "Spesialisttjenesten krever henvisning."},
    ],
    "services": [
        {"name": "Kommunal psykologtjeneste",
         "access_methods": ["self_referral"], "strong_access": True,
         "age_eligible": True, "target_group": "Barn og unge",
         "source_url": "https://example.org/muni"},
        {"name": "Spesialisttjeneste",
         "access_methods": ["referral_required"], "strong_access": False,
         "age_eligible": True, "target_group": "Voksne",
         "source_url": "https://example.org/spec"},
    ],
}


# Same field mapping as finalize.py structured_routes serialization.
def serialize(routes):
    out = []
    for r in routes:
        ev = [e["evidence_id"] for e in DISCOVERY["evidence"]
              if e["source_url"] == r["provenance_refs"][0]]
        entry = {}
        entry["route_id"] = r["route_id"]
        entry["service_identity"] = r["service_type"]
        entry["display_label"] = r["service_type"]
        entry["track_domain"] = r["track_domain"]
        entry["route_state"] = r["route_state"]
        entry["access_model"] = r["access_model"]
        entry["self_referral"] = r["self_referral"]
        entry["target_population"] = r["target_population"]
        entry["scope"] = r["scope"]
        entry["evidence_refs"] = ev
        entry["provenance_refs"] = r["provenance_refs"]
        entry["dims"] = {k: r.get(k) for k in (
            "service_exists", "age_eligible", "scenario_relevant",
            "access_verified", "contact_verified")}
        out.append(entry)
    return out


class CrossBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        routes = build_route_candidates(DISCOVERY, "mental_health", age=10)
        serialized = json.loads(json.dumps(serialize(routes)))
        cls.answer = {
            "routes": [e["display_label"] for e in serialized],
            "no_route_asserted": False,
            "evidence": {"structured_routes": serialized},
        }
        cls.obs = A.observe_routes(cls.answer)

    def test_product_pipeline_produces_structured_routes(self):
        self.assertEqual(self.obs["mode"], A.STRUCTURED)
        self.assertEqual(len(self.obs["routes"]), 2)

    def test_identity_preserved(self):
        ids = [r["identity"] for r in self.obs["routes"]]
        self.assertIn("Kommunal psykologtjeneste", ids)
        self.assertIn("Spesialisttjeneste", ids)

    def test_access_preserved(self):
        acc = {r["identity"]: r["access_model"]
               for r in self.obs["routes"]}
        self.assertEqual(acc["Kommunal psykologtjeneste"],
                         ["self_referral"])
        self.assertEqual(acc["Spesialisttjeneste"],
                         ["referral_required"])

    def test_conditions_preserved(self):
        dims = {r["identity"]: r["conditions"] for r in self.obs["routes"]}
        self.assertEqual(
            dims["Kommunal psykologtjeneste"]["access_verified"],
            "VERIFIED")
        self.assertEqual(dims["Spesialisttjeneste"]["age_eligible"],
                         "VERIFIED")

    def test_track_preserved(self):
        self.assertTrue(all(r["track_domain"] == "mental_health"
                            for r in self.obs["routes"]))

    def test_evidence_linkage_preserved(self):
        ev = {r["identity"]: r["evidence_refs"] for r in self.obs["routes"]}
        self.assertEqual(ev["Kommunal psykologtjeneste"], ["E-1"])
        self.assertEqual(ev["Spesialisttjeneste"], ["E-2"])

    def test_serialized_shape_matches_real_product_output(self):
        real_path = os.path.join(
            REPO, "evaluation", "full-sut-repair-wave-4-v1", "runs",
            "structural-120-replay-v1", "routing_cases", "predictions",
            "ROUT-021.json")
        real = json.load(open(real_path, encoding="utf-8"))
        real_keys = set(real["evidence"]["structured_routes"][0].keys())
        synth_keys = set(self.answer["evidence"]
                         ["structured_routes"][0].keys())
        self.assertEqual(real_keys, synth_keys)

    def test_product_does_not_import_evaluator(self):
        out = subprocess.run(
            ["grep", "-rn", "-i", "evaluation",
             os.path.join(REPO, "runtime", "sut"),
             "--include=*.py", "--exclude=test_*.py"],
            capture_output=True, text=True)
        offenders = [line for line in out.stdout.splitlines()
                     if "import" in line and "evaluation" in line]
        self.assertEqual(offenders, [],
                         "product imports evaluation: %s" % offenders)


def main():
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromModule(sys.modules["__main__"])
    names = sorted({t.id().split(".")[-1] for grp in suite for t in grp})
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    out = {
        "artifact": "cross-boundary-contract-tests",
        "pipeline": "discovery -> build_route_candidates -> serialize -> adapter -> observation",
        "total": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "pass": result.wasSuccessful(),
        "tests": names,
    }
    with open(os.path.join(HERE, "cross-boundary-contract-tests.json"),
              "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write(chr(10))
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
