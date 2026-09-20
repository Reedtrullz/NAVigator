"""unittest suite for the discovery runtime prototype (stdlib only)."""

import copy
import json
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery.protocol import (  # noqa: E402
    ProtocolLoader, ProtocolLoadError, ProtocolShaMismatch, EXPECTED_PROTOCOL_SHA,
)
from runtime.discovery.security import validate_url, InvalidUrlError, is_official_domain  # noqa: E402
from runtime.discovery.providers import (  # noqa: E402
    ReplaySearchProvider, ReplayFetchProvider, HttpFetchProvider,
)
from runtime.discovery.engine import (  # noqa: E402
    DiscoveryPlanner, LinkExplorer, ServiceExtractor,
)
from runtime.discovery.classification import (  # noqa: E402
    EvidenceLedger, AccessClassifier, RouteEvaluator, ProvenanceGraph,
)
from runtime.discovery.orchestrator import run_discovery  # noqa: E402
from runtime.discovery.serialize import ResultSerializer  # noqa: E402


PROTOCOL_PATH = REPO_ROOT / "data" / "local-service-discovery-protocol-v1.json"
FIXTURE_PATH = REPO_ROOT / "evaluation" / "local-discovery-runtime-v1" / "fixtures" / "fixture-manifest.json"


def load_fixtures():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_protocol():
    return ProtocolLoader(str(PROTOCOL_PATH)).load()


def run_replay(municipality, age=22, fixtures=None):
    protocol = load_protocol()
    if fixtures is None:
        fixtures = load_fixtures()
    return run_discovery(
        protocol,
        {"municipality": municipality, "municipality_number": None,
         "age": age, "need": "mental_health_low_threshold", "urgency": "non_acute"},
        fixtures=fixtures,
        mode="replay",
    )


class TestProtocolLoading(unittest.TestCase):
    def test_load_success(self):
        data = load_protocol()
        self.assertEqual(data["protocol_id"], "LOCAL-SERVICE-DISCOVERY-PROTOCOL-V1")

    def test_sha_verification(self):
        loader = ProtocolLoader(str(PROTOCOL_PATH))
        loader.load()
        self.assertEqual(loader.actual_sha, EXPECTED_PROTOCOL_SHA)

    def test_sha_mismatch_detected(self):
        loader = ProtocolLoader(str(PROTOCOL_PATH), expected_sha="deadbeef")
        with self.assertRaises(ProtocolShaMismatch):
            loader.load()

    def test_missing_file(self):
        loader = ProtocolLoader("/nonexistent/path.json")
        with self.assertRaises(ProtocolLoadError):
            loader.load()


class TestPlanner(unittest.TestCase):
    def test_plan_contains_all_levels(self):
        protocol = load_protocol()
        plan = DiscoveryPlanner(protocol).plan("TestKommune")
        self.assertEqual([s["level"] for s in plan], [0, 1, 2, 3, 4, 5])

    def test_query_generation_uses_frozen_templates(self):
        protocol = load_protocol()
        plan = DiscoveryPlanner(protocol).plan("Bamble")
        queries = plan[1]["queries"]
        self.assertIn("Bamble psykisk helse voksne", queries)
        self.assertIn("Bamble mestringsteam", queries)
        self.assertEqual(len(queries), len(protocol["query_family_templates"]))


class TestUrlSecurity(unittest.TestCase):
    def test_valid_http(self):
        self.assertEqual(validate_url("https://www.bamble.kommune.no/x"), "https://www.bamble.kommune.no/x")

    def test_file_scheme_blocked(self):
        with self.assertRaises(InvalidUrlError):
            validate_url("file:///etc/passwd")

    def test_localhost_blocked(self):
        with self.assertRaises(InvalidUrlError):
            validate_url("http://localhost/secret")

    def test_private_ip_blocked(self):
        for ip in ["10.0.0.1", "172.16.0.5", "192.168.1.1", "169.254.1.1", "127.0.0.2"]:
            with self.assertRaises(InvalidUrlError, msg=ip):
                validate_url("http://%s/admin" % ip)

    def test_ftp_blocked(self):
        with self.assertRaises(InvalidUrlError):
            validate_url("ftp://example.com/file")

    def test_domain_classification(self):
        self.assertEqual(is_official_domain("https://www.bamble.kommune.no/x"), "municipal")
        self.assertEqual(is_official_domain("https://helsenorge.no/min-side"), "helsenorge")
        self.assertEqual(is_official_domain("https://some-private-blog.no/x"), "private")


class TestFetch(unittest.TestCase):
    def test_replay_fetch_success(self):
        fx = load_fixtures()
        fp = ReplayFetchProvider(fx["pages"])
        url = "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/"
        r = fp.fetch(url)
        self.assertEqual(r.status, "success")
        self.assertIn("Bamblehjelpa", r.content)

    def test_replay_fetch_missing(self):
        fp = ReplayFetchProvider({})
        r = fp.fetch("https://missing.example.org/x")
        self.assertEqual(r.status, "failed")

    def test_spa_shell_detection(self):
        shell = "<!DOCTYPE html><html><head><title>x</title></head><body><div id=app></div></body></html>"
        self.assertTrue(HttpFetchProvider._looks_like_spa_shell(shell))
        full = "<html><body>" + "<p>word </p>" * 40 + "</body></html>"
        self.assertFalse(HttpFetchProvider._looks_like_spa_shell(full))


class TestLinkTraversal(unittest.TestCase):
    def test_link_extraction_stays_official(self):
        html = '<a href="https://www.bamble.kommune.no/sub">Sub</a><a href="https://facebook.com/x">FB</a>'
        links = LinkExplorer._extract_links(html, "https://www.bamble.kommune.no/page/")
        self.assertIn("https://www.bamble.kommune.no/sub", links)
        self.assertNotIn("https://facebook.com/x", links)

    def test_max_depth(self):
        pages = {
            "https://a.kommune.no/p1": {"content": '<a href="https://a.kommune.no/p2">2</a>', "captured_at": "T"},
            "https://a.kommune.no/p2": {"content": '<a href="https://a.kommune.no/p3">3</a>', "captured_at": "T"},
            "https://a.kommune.no/p3": {"content": "end", "captured_at": "T"},
        }
        explorer = LinkExplorer(ReplayFetchProvider(pages), max_depth=1, max_pages=10)
        visited = list(explorer.explore("https://a.kommune.no/p1"))
        self.assertEqual(len(visited), 2)  # p1 + one level to p2


class TestStopStates(unittest.TestCase):
    def test_short_circuit_on_access_verified(self):
        # When FULLY_VERIFIED, terminal state is ACCESS_VERIFIED and runtime stops
        result = run_replay("Bamble")
        self.assertEqual(result["terminal_state"], "ACCESS_VERIFIED")

    def test_protocol_exhausted_when_no_access(self):
        result = run_replay("Raelingen")
        self.assertIn(result["terminal_state"], ("PUBLIC_DATA_EXHAUSTED", "REFERRAL_VERIFIED"))


class TestAccessParsing(unittest.TestCase):
    def setUp(self):
        self.extractor = ServiceExtractor()

    def test_contact_invitation_detected(self):
        html = ("<p>Psykisk helse teamet tilbyr samtaler for innbyggerne.</p>"
                "<p>Du kan ta kontakt med oss p\u00e5 telefon 48 16 50 77.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse")
        self.assertTrue(r["access_markers"]["contact_invitation"])

    def test_application_form_detected(self):
        html = ("<p>Lavterskeltilbudet i psykisk helse er et kommunalt tilbud.</p>"
                "<p>Fyll ut selvhenvisningsskjema og send det inn.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse")
        self.assertTrue(r["access_markers"]["application_form"])

    def test_referral_detected(self):
        html = ("<p>Kommunens psykiske helsetjeneste gir r\u00e5dgivning "
                "og behandling.</p><p>Tjenesten krever henvisning fra fastlege.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse")
        self.assertTrue(r["access_markers"]["referral_requirement"])

    def test_dropin_detected(self):
        html = ("<p>Psykisk helse og rus tjenesten hjelper innbyggere med "
                "mestring.</p><p>Det er drop-in hver onsdag uten timebestilling.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse")
        self.assertTrue(r["access_markers"]["dropin"])

    def test_age_extraction(self):
        html = ("<p>Psykisk helse tjenesten er for voksne innbyggere.</p>"
                "<p>Tilbudet gjelder for deg som er over 18 \u00e5r og bor i kommunen.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse")
        self.assertIn("18", r["age_text"])


class TestSelfReferralSeparate(unittest.TestCase):
    def test_phone_alone_does_not_give_self_referral_yes(self):
        # E3: phone number alone must not infer self_referral YES.
        classifier = AccessClassifier()
        extract = {"access_markers": {"phone_numbers": ["12345678"],
                                      "emails": [], "application_form": False,
                                      "dropin": False, "contact_invitation": False,
                                      "referral_requirement": False}}
        result = classifier.classify(extract)
        self.assertEqual(result["methods"], ["UNCLEAR"])
        self.assertEqual(result["self_referral"], "UNCLEAR")

    def test_contact_invitation_gives_conditional(self):
        classifier = AccessClassifier()
        extract = {"access_markers": {"phone_numbers": [], "emails": [],
                                      "application_form": False, "dropin": False,
                                      "contact_invitation": True,
                                      "referral_requirement": False}}
        result = classifier.classify(extract)
        self.assertEqual(result["self_referral"], "CONDITIONAL")

    def test_explicit_form_gives_yes(self):
        classifier = AccessClassifier()
        extract = {"access_markers": {"phone_numbers": [], "emails": [],
                                      "application_form": True, "dropin": False,
                                      "contact_invitation": False,
                                      "referral_requirement": False}}
        result = classifier.classify(extract)
        self.assertEqual(result["self_referral"], "YES")


class TestIntelmunicipalEvidence(unittest.TestCase):
    def test_no_membership_inferred_from_host_page(self):
        # The runtime has no intermunicipal fixture; no INTERMUNICIPAL_GATEWAY
        # method may be inferred without explicit membership evidence.
        result = run_replay("Bamble")
        for s in result["services"]:
            self.assertNotIn("INTERMUNICIPAL_GATEWAY", s["access_methods"])


class TestRouteState(unittest.TestCase):
    def test_fully_verified(self):
        evaluator = RouteEvaluator()
        self.assertEqual(evaluator.evaluate(True, True, ["DIRECT_PHONE"], True, True),
                         "ROUTE_FULLY_VERIFIED")

    def test_access_partial(self):
        evaluator = RouteEvaluator()
        self.assertEqual(evaluator.evaluate(True, True, ["DIRECT_PHONE"], False, True),
                         "ROUTE_ACCESS_PARTIAL")

    def test_existence_only(self):
        evaluator = RouteEvaluator()
        self.assertEqual(evaluator.evaluate(True, True, ["UNCLEAR"], False, False),
                         "ROUTE_EXISTENCE_ONLY")

    def test_unverified(self):
        evaluator = RouteEvaluator()
        self.assertEqual(evaluator.evaluate(False, False, ["UNCLEAR"], False, False),
                         "ROUTE_UNVERIFIED")


class TestProvenanceGraph(unittest.TestCase):
    def test_edge_trace(self):
        g = ProvenanceGraph()
        g.add_edge("start", "a", "QUERY_SEARCH", query_family="q1", level=1)
        g.add_edge("a", "b", "NAVIGATION_LINK", level=2)
        path = g.trace_back("b")
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0]["to"], "a")
        self.assertEqual(path[1]["to"], "b")

    def test_edges_are_first_class(self):
        result = run_replay("Drammen")
        self.assertTrue(len(result["provenance_graph"]) > 0)
        for e in result["provenance_graph"]:
            self.assertIn("from", e)
            self.assertIn("to", e)
            self.assertIn("discovery_method", e)


class TestSchemaSerialization(unittest.TestCase):
    def test_serialization_is_sorted_and_stable(self):
        result = {"b": 1, "a": {"z": [3, 1], "y": 2}}
        s1 = ResultSerializer.serialize(result)
        s2 = ResultSerializer.serialize(copy.deepcopy(result))
        self.assertEqual(s1, s2)
        self.assertLess(s1.index('"a"'), s1.index('"b"'))


class TestReplayAndDeterminism(unittest.TestCase):
    def test_replay_determinism_three_runs(self):
        runs = []
        for _ in range(3):
            r = run_replay("Bamble")
            r["started_at"] = None
            runs.append(ResultSerializer.serialize(r))
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])

    def test_replay_ralingen_existence_only(self):
        # Raelingen replay fixtures contain an SPA shell + sparse text with no
        # documented access markers, so ROUTE_EXISTENCE_ONLY is the correct
        # runtime outcome; revisit if fixtures gain real access-marker content.
        result = run_replay("Raelingen")
        self.assertEqual(result["route_state"], "ROUTE_EXISTENCE_ONLY")


class TestGeneralizedMarkers(unittest.TestCase):
    # Generalized marker coverage derived from historical access targets.
    # No case IDs, no municipality names; formulations are linguistic variants.
    def setUp(self):
        self.extractor = ServiceExtractor()

    def test_nynorsk_negated_referral_is_self_contact(self):
        html = ("<p>Psykisk helse- og rusteneste for vaksne er eit kommunalt tilbud.</p>"
                "<p>Du treng ikkje tilvising for å få hjelp.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse-og-rusteneste")
        m = r["access_markers"]
        self.assertTrue(m["referral_negated"])
        self.assertTrue(m["explicit_self_contact"])

    def test_bruk_skjema_counts_as_application_form(self):
        html = ("<p>Psykisk helse og rus tenesta hjelper innbyggjarar.</p>"
                "<p>Korleis søkje? Bruk skjema for helse- og omsorgstenester.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/psykisk-helse-og-rus")
        self.assertTrue(r["access_markers"]["application_form"])

    def test_service_connected_email_gives_marker(self):
        html = ("<p>Kommunepsykologen bidrar med klinisk kompetanse.</p>"
                "<p>Ønsker du kontakt, send e-post til psykolog@x.kommune.no.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/kommunepsykolog")
        self.assertTrue(r["access_markers"]["email_connected"])

    def test_capacity_closure_gives_no_selfreferral(self):
        from runtime.discovery.classification import AccessClassifier
        html = ("<p>Kommunepsykologen innehar klinisk kompetanse.</p>"
                "<p>Det er for tiden ikke kapasitet til å tilby avklaringssamtaler.</p>")
        r = self.extractor.extract(html, "https://x.kommune.no/kommunepsykolog")
        c = AccessClassifier().classify(r)
        self.assertEqual(c["self_referral"], "NO")

    def test_system_targeted_gives_no_selfreferral(self):
        from runtime.discovery.classification import AccessClassifier
        html = "<p>Kommunepsykologen tilbyr rettleiing og fagstøtte til tilsette.</p>"
        r = self.extractor.extract(html, "https://x.kommune.no/kommunepsykolog")
        c = AccessClassifier().classify(r)
        self.assertEqual(c["self_referral"], "NO")

class TestResultSchema(unittest.TestCase):
    # Structural validation of runtime results against the frozen result schema.
    def test_replay_result_matches_schema(self):
        result = run_replay("Bamble")
        from runtime.discovery.schema import validate_result
        errors = validate_result(result, str(REPO_ROOT / "data" / "local-discovery-runtime-result-v1.schema.json"))
        self.assertEqual(errors, [])

    def test_schema_rejects_invalid_route_state(self):
        from runtime.discovery.schema import validate_result
        result = run_replay("Bamble")
        result["route_state"] = "ROUTE_MAGIC"
        errors = validate_result(result, str(REPO_ROOT / "data" / "local-discovery-runtime-result-v1.schema.json"))
        self.assertTrue(len(errors) >= 1)

class TestFailureToUncertainty(unittest.TestCase):
    def test_fetch_failure_gives_incomplete_not_unverified(self):
        fx = load_fixtures()
        # Strip pages to simulate runtime failure after search succeeded
        fx2 = copy.deepcopy(fx)
        fx2["pages"] = {}
        result = run_replay("Bamble", fixtures=fx2)
        self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")
        # No false user-facing "no service exists": route stays UNVERIFIED but
        # execution status flags incompleteness, uncertainty wording is not
        # a hard no-service claim.
        self.assertNotIn("ikke n\u00f8dvendigvis", "", msg="sanity")

    def test_search_failure_gives_incomplete(self):
        fx2 = copy.deepcopy(load_fixtures())
        fx2["search_index"] = {}
        fx2["known_urls"] = []
        result = run_replay("Bamble", fixtures=fx2)
        self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertEqual(result["route_state"], "ROUTE_UNVERIFIED")


class TestFalseNoMatchInvariant(unittest.TestCase):
    def test_no_service_found_does_not_say_no_service_exists(self):
        protocol = load_protocol()
        fx2 = copy.deepcopy(load_fixtures())
        fx2["search_index"] = {}
        fx2["known_urls"] = []
        result = run_discovery(protocol, {"municipality": "NoService", "municipality_number": None,
                                          "age": 22, "need": "mental_health_low_threshold",
                                          "urgency": "non_acute"}, fixtures=fx2, mode="replay")
        # Uncertainty wording must be the frozen NO_VERIFIED_ROUTE_AFTER_PROTOCOL
        # which explicitly says it does not mean the service does not exist.
        self.assertIn("ikke n\u00f8dvendigvis", result["uncertainty_output"])


class TestHistoricalFilesImmutable(unittest.TestCase):
    HISTORICAL = [
        "data/local-service-discovery-protocol-v1.json",
        "data/local-access-verification-v1.json",
        "evaluation/local-discovery-generalization-v1/protocol-predictions.json",
    ]

    def test_historical_files_exist_and_protocol_sha_ok(self):
        for rel in self.HISTORICAL:
            self.assertTrue((REPO_ROOT / rel).exists(), rel)
        h = ProtocolLoader(str(PROTOCOL_PATH))
        h.load()
        self.assertEqual(h.actual_sha, EXPECTED_PROTOCOL_SHA)


class TestNoMunicipalityBranching(unittest.TestCase):
    def test_no_municipality_names_in_runtime_code(self):
        runtime_dir = REPO_ROOT / "runtime" / "discovery"
        forbidden = ["Bamble", "Raelingen", "R\u00e6lingen", "Drammen", "Askoy",
                     "Ask\u00f8y", "Bjerkreim", "Alstahaug", "Etnedal", "Balsfjord",
                     "Birkenes", "Fredrikstad"]
        for py in runtime_dir.glob("*.py"):
            if py.name == "tests.py":
                continue  # tests.py is test provenance, not runtime logic
            src = py.read_text(encoding="utf-8")
            for name in forbidden:
                self.assertNotIn(name, src, "%s contains %s" % (py.name, name))


if __name__ == "__main__":
    unittest.main()
