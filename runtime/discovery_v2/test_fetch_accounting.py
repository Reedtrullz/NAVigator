import hashlib
import unittest

from runtime.discovery.providers import FetchResult
from .orchestrator_v25 import run_v25, _official
from .providers import ProviderResponse


PROTOCOL = {"protocol_id": "SYNTHETIC", "levels": [{"id": 1, "name": "queries"}, {"id": 2, "name": "catalog"}],
            "query_family_templates": ["<kommune> a", "<kommune> b"],
            "uncertainty_outputs": {"VERIFIED_ROUTE": "verified", "SERVICE_FOUND_ACCESS_UNCLEAR": "unclear",
                                    "NO_VERIFIED_ROUTE_AFTER_PROTOCOL": "unknown"}}
URL = "https://synthetic.kommune.no/service"


class FakeDiscovery:
    def __init__(self, statuses=("SUCCESS", "SUCCESS"), urls=(URL,)):
        self.statuses, self.urls, self.calls = statuses, urls, []

    def discover(self, query):
        status = self.statuses[len(self.calls)]
        self.calls.append(query)
        return ProviderResponse(query, status, results=[{"url": u} for u in self.urls] if status == "SUCCESS" else [],
                                provider="SYNTHETIC", discovery_method="FIXTURE")

    def health(self):
        return {"fixture": True}


class FakeFetch:
    def __init__(self, status="success", content="", final_url=None):
        self.status, self.content, self.calls = status, content, []
        self.final_url = final_url

    def fetch(self, url):
        self.calls.append(url)
        if self.status == "timeout":
            raise TimeoutError("SYNTHETIC_TIMEOUT")
        return FetchResult(url, self.status, self.content, hashlib.sha256(self.content.encode()).hexdigest(),
                           "synthetic", "SYNTHETIC_TIME", error="SYNTHETIC_FAILURE", final_url=self.final_url)


class FetchAccountingTests(unittest.TestCase):
    def run_fixture(self, fetch, discovery=None, protocol=None, age: int | None = 19):
        return run_v25(protocol or PROTOCOL, {"municipality": "Synthetic", "age": age},
                       discovery or FakeDiscovery(), fetch_provider=fetch)

    def test_failed_timeout_and_render_do_not_count_as_success(self):
        for status in ("failed", "timeout", "render_required"):
            with self.subTest(status=status):
                result = self.run_fixture(FakeFetch(status))
                self.assertEqual(result["pages_fetched"], 0)
                self.assertEqual(result["execution"]["attempted_fetches"], 1)
                self.assertEqual(result["execution"]["successful_fetches"], 0)
                self.assertFalse(result["execution"]["protocol_completed"])
                self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")

    def test_empty_success_is_complete_without_claiming_service(self):
        d = FakeDiscovery()
        result = self.run_fixture(FakeFetch(), d)
        self.assertEqual(len(d.calls), 2)
        self.assertEqual(result["pages_fetched"], 1)
        self.assertEqual(result["execution"]["services_found"], 0)
        self.assertTrue(result["execution"]["protocol_completed"])
        self.assertEqual(result["execution_status"], "COMPLETE")
        named_empty = self.run_fixture(FakeFetch(), FakeDiscovery(urls=(URL + "/psykisk-helse",)))
        self.assertEqual(named_empty["services"], [])

    def test_provider_failure_after_success_stays_incomplete(self):
        result = self.run_fixture(FakeFetch(), FakeDiscovery(("SUCCESS", "TIMEOUT")))
        self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertEqual(len(result["provider_failures"]), 1)

    def test_valid_no_results_differs_from_unfinished_or_capped_protocol(self):
        result = self.run_fixture(FakeFetch(), FakeDiscovery(("NO_RESULTS", "NO_RESULTS")))
        self.assertEqual(result["execution_status"], "COMPLETE")
        self.assertEqual(result["execution"]["attempted_fetches"], 0)
        urls = tuple(URL + str(n) for n in range(11))
        capped = self.run_fixture(FakeFetch(), FakeDiscovery(urls=urls))
        self.assertFalse(capped["execution"]["protocol_completed"])
        unsupported = {**PROTOCOL, "levels": [*PROTOCOL["levels"], {"id": 3, "name": "unimplemented"}]}
        self.assertFalse(self.run_fixture(FakeFetch(), protocol=unsupported)["execution"]["protocol_completed"])

    def test_actual_extractor_uses_input_age_not_presence_of_age_text(self):
        body = "<title>Service A</title><p>Psykisk helse. For 18-25 år. Drop-in. Du kan ta kontakt selv.</p>"
        for age, expected in [(13, False), (19, True), (None, None)]:
            with self.subTest(age=age):
                result = self.run_fixture(FakeFetch(content=body), age=age)
                self.assertEqual(result["services"][0]["age_input_eligible"], expected)
                if expected is not True:
                    self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")

    def test_municipality_name_does_not_authorize_unrelated_host(self):
        self.assertFalse(_official("https://synthetic.evil.example/service"))

    def test_final_url_controls_source_authority_and_provenance_gate(self):
        body = "<title>Service A</title><p>Psykisk helse. For 18-25 år. Drop-in. Du kan ta kontakt selv.</p>"
        result = self.run_fixture(FakeFetch(content=body, final_url="https://synthetic.kommune.no/"),
                                  FakeDiscovery(urls=(URL + "/deep",)))
        self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")
        self.assertEqual(result["services"][0]["url"], "https://synthetic.kommune.no/")
        rejected = self.run_fixture(FakeFetch(content=body, final_url="https://unrelated.example/"))
        self.assertEqual(rejected["execution"]["successful_fetches"], 1)
        self.assertEqual(rejected["services"], [])
        self.assertFalse(rejected["execution"]["protocol_completed"])
