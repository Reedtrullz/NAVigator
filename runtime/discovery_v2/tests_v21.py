"""V2.1 adapter-correctness regression suite (red-first, task
NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-V2_1-ADAPTER-CORRECTNESS).

Proves: process exit != HTTP status; challenge content beyond the old
5000-char head is classified; failure statuses are never folded into
NO_RESULTS; legacy (status, body) fetch tuples still work; real archived
Brave 429 challenge fixture classifies RATE_LIMITED, never NO_RESULTS.
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery.protocol import ProtocolLoader  # noqa: E402
from runtime.discovery.providers import ReplayFetchProvider  # noqa: E402

from runtime.discovery_v2 import brave as brave_mod  # noqa: E402
from runtime.discovery_v2.brave import (  # noqa: E402
    brave_fetch_fn, brave_parser, make_brave_provider,
)
from runtime.discovery_v2.orchestrator import run_v2  # noqa: E402
from runtime.discovery_v2.providers import (  # noqa: E402
    CompositeDiscoveryProvider, ExternalSearchProvider, SiteDirectProvider,
    classify_http_response,
)

FIXTURE_DIR = REPO_ROOT / "evaluation" / "local-discovery-provider-v2-1" / "fixtures"
FIXTURE_BODY = FIXTURE_DIR / "brave-429-challenge-001.html"
FIXTURE_META = FIXTURE_DIR / "fixture-001-meta.json"
PROTOCOL_PATH = REPO_ROOT / "data" / "local-service-discovery-protocol-v1.json"

RESULTS_HTML = (
    '<html><body>'
    '<a href="https://www.bamble.kommune.no/psykisk">Bamble psykisk</a>'
    '<a href="https://www.farsund.kommune.no/rph">Farsund RPH</a>'
    '</body></html>'
)
EMPTY_HTML = "<html><body><p>Ingen treff.</p>" + ("x" * 4000) + "</body></html>"
PLAIN_LONG_HTML = "<html><body><p>" + ("beskrivelse " * 600) + "</p></body></html>"
CHALLENGE_FAR = ("<html><body>" + ("f" * 6000) +
                 "<div>captcha challenge: verify you are human</div></body></html>")
NON_HTML_LONG = json.dumps({"error": "backend failure", "detail": "x" * 3500})


def dict_transport(http_status=200, body="", curl_exit=0, final_url=None,
                   num_redirects="0", initial_url=None, body_truncated=False):
    return {
        "curl_exit": curl_exit, "http_status": http_status, "body": body,
        "initial_url": initial_url or "https://search.brave.com/search?q=q",
        "final_url": final_url or initial_url or "https://search.brave.com/search?q=q",
        "num_redirects": num_redirects,
        "body_truncated": body_truncated,
    }


class TestCasesAtoH(unittest.TestCase):
    def test_case_a_success_on_results(self):
        p = ExternalSearchProvider(fetch_fn=lambda q: (200, RESULTS_HTML),
                                   parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "SUCCESS")

    def test_case_a_dict_transport_success(self):
        p = ExternalSearchProvider(
            fetch_fn=lambda q: dict_transport(200, RESULTS_HTML),
            parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "SUCCESS")

    def test_case_b_legitimate_empty_search(self):
        self.assertEqual(classify_http_response(200, EMPTY_HTML, []),
                         "NO_RESULTS")
        p = ExternalSearchProvider(fetch_fn=lambda q: (200, EMPTY_HTML),
                                   parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "NO_RESULTS")

    def test_case_c_429_is_rate_limited_even_with_challenge_body(self):
        body = FIXTURE_BODY.read_text(encoding="utf-8") if FIXTURE_BODY.exists() \
            else CHALLENGE_FAR
        self.assertEqual(classify_http_response(429, body, []), "RATE_LIMITED")
        p = ExternalSearchProvider(
            fetch_fn=lambda q: dict_transport(429, body, curl_exit=0),
            parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "RATE_LIMITED")

    def test_case_d_403_challenge_is_bot_blocked(self):
        self.assertEqual(classify_http_response(403, CHALLENGE_FAR, []),
                         "BOT_BLOCKED")

    def test_case_e_transport_failure_is_provider_unavailable(self):
        self.assertEqual(classify_http_response(0, "", []),
                         "PROVIDER_UNAVAILABLE")
        p = ExternalSearchProvider(
            fetch_fn=lambda q: dict_transport(0, "", curl_exit=7),
            parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "PROVIDER_UNAVAILABLE")

    def test_case_f_challenge_marker_after_5000_is_bot_blocked(self):
        self.assertEqual(classify_http_response(200, CHALLENGE_FAR, []),
                         "BOT_BLOCKED")
        self.assertGreater(CHALLENGE_FAR.find("captcha"), 5000)

    def test_case_g_long_plain_html_is_not_bot_blocked(self):
        self.assertEqual(classify_http_response(200, PLAIN_LONG_HTML, []),
                         "NO_RESULTS")

    def test_case_h_malformed_body_is_invalid_response(self):
        self.assertEqual(classify_http_response(200, NON_HTML_LONG, []),
                         "INVALID_RESPONSE")


class TestArchivedChallengeFixture(unittest.TestCase):
    def test_fixture_integrity(self):
        meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
        raw = FIXTURE_BODY.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         meta["body_sha256"])
        text = raw.decode("utf-8", errors="replace")
        first = min(text.find(m) for m in meta["markers_found"]
                    if text.find(m) >= 0)
        self.assertGreater(first, 5000)

    def test_fixture_429_classifies_rate_limited_never_no_results(self):
        body = FIXTURE_BODY.read_text(encoding="utf-8")
        self.assertNotEqual(classify_http_response(200, body, []),
                            "NO_RESULTS")
        self.assertEqual(classify_http_response(429, body, []),
                         "RATE_LIMITED")
        p = ExternalSearchProvider(
            fetch_fn=lambda q: dict_transport(429, body, curl_exit=0),
            parser=brave_parser, min_interval_s=0)
        resp = p.discover("q")
        self.assertEqual(resp.status, "RATE_LIMITED")
        self.assertNotEqual(resp.status, "NO_RESULTS")


class TestTransportContract(unittest.TestCase):
    def test_t1_legacy_tuple_still_supported(self):
        p = ExternalSearchProvider(fetch_fn=lambda q: (429, ""),
                                   min_interval_s=0)
        self.assertEqual(p.discover("q").status, "RATE_LIMITED")

    def test_t2_transport_metadata_in_attempts(self):
        p = ExternalSearchProvider(
            fetch_fn=lambda q: dict_transport(
                429, "b", curl_exit=0, final_url="https://x/final",
                num_redirects="2"),
            parser=brave_parser, min_interval_s=0)
        resp = p.discover("q")
        att = resp.attempts[0]
        self.assertEqual(att["curl_exit"], 0)
        self.assertEqual(att["http_status"], 429)
        self.assertEqual(att["final_url"], "https://x/final")
        self.assertEqual(att["num_redirects"], "2")
        self.assertFalse(att["body_truncated"])

    def test_t3_fetch_fn_uses_structural_write_out(self):
        captured = {}
        body = "<html><body>429 page</body></html>"
        meta = "429 https://search.brave.com/search?q=q 0"
        sentinel = brave_mod.TRANSPORT_META_SENTINEL

        class FakeProc:
            returncode = 0
            stdout = body + sentinel + meta

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            return FakeProc()

        orig = brave_mod.subprocess.run
        brave_mod.subprocess.run = fake_run
        try:
            out = brave_fetch_fn("q")
        finally:
            brave_mod.subprocess.run = orig
        self.assertIn("-w", captured["argv"])
        self.assertIn("%{http_code}",
                      captured["argv"][captured["argv"].index("-w") + 1])
        self.assertEqual(out["curl_exit"], 0)
        self.assertEqual(out["http_status"], 429)
        self.assertEqual(out["body"], body)
        self.assertEqual(out["final_url"],
                         "https://search.brave.com/search?q=q")

    def test_t3_curl_exit0_http429_never_http200(self):
        sentinel = brave_mod.TRANSPORT_META_SENTINEL

        class FakeProc:
            returncode = 0
            stdout = "challenge" + sentinel + "429 u 0"

        orig = brave_mod.subprocess.run
        brave_mod.subprocess.run = lambda argv, **kw: FakeProc()
        try:
            out = brave_fetch_fn("q")
        finally:
            brave_mod.subprocess.run = orig
        p = ExternalSearchProvider(fetch_fn=lambda q: out,
                                   parser=brave_parser, min_interval_s=0)
        self.assertEqual(p.discover("q").status, "RATE_LIMITED")

    def test_t4_curl_exit28_maps_to_timeout(self):
        class FakeProc:
            returncode = 28
            stdout = ""

        orig = brave_mod.subprocess.run
        brave_mod.subprocess.run = lambda argv, **kw: FakeProc()
        try:
            with self.assertRaises(TimeoutError):
                brave_fetch_fn("q")
            p = ExternalSearchProvider(
                fetch_fn=lambda q: (_ for _ in ()).throw(
                    TimeoutError("curl exit 28")),
                min_interval_s=0)
            self.assertEqual(p.discover("q").status, "TIMEOUT")
        finally:
            brave_mod.subprocess.run = orig

    def test_t5_body_truncated_at_2mib_and_scan_capped(self):
        from runtime.discovery_v2.providers import MAX_SCAN_BYTES
        # Complete, valid HTML document exactly filling the scan cap; the
        # challenge marker begins beyond it. Only within-cap evidence
        # classifies.
        head = "<html><body>"
        tail = "</body></html>"
        doc = head + "a" * (MAX_SCAN_BYTES - len(head) - len(tail)) + tail
        self.assertEqual(len(doc), MAX_SCAN_BYTES)
        sentinel_body = doc + "captcha challenge"
        self.assertNotIn("captcha", sentinel_body[:MAX_SCAN_BYTES])
        transport = dict_transport(200, sentinel_body, body_truncated=True)
        p = ExternalSearchProvider(
            fetch_fn=lambda q: transport,
            parser=brave_parser, min_interval_s=0)
        resp = p.discover("q")
        self.assertEqual(resp.status, "NO_RESULTS")
        self.assertTrue(resp.attempts[0]["body_truncated"])
        # full-bounded-scan evidence: a challenge within the cap is caught.
        within = "x" * 100 + " captcha challenge"
        self.assertEqual(classify_http_response(200, within, []),
                         "BOT_BLOCKED")


class TestFailureSemanticsInvariant(unittest.TestCase):
    def test_inv1_failures_never_no_results(self):
        for status in (429, 403, 401, 500, 503, 0):
            self.assertNotEqual(classify_http_response(status, "", []),
                                "NO_RESULTS")
        self.assertNotEqual(classify_http_response(200, CHALLENGE_FAR, []),
                            "NO_RESULTS")
        self.assertNotEqual(classify_http_response(200, NON_HTML_LONG, []),
                            "NO_RESULTS")

    def _protocol(self):
        return ProtocolLoader(str(PROTOCOL_PATH)).load()

    def test_inv2_all_provider_failure_is_discovery_incomplete(self):
        protocol = self._protocol()
        site = SiteDirectProvider(
            fetch_fn=lambda url: (403, "denied"),
            roots=["https://www.bamble.kommune.no/"])
        ext = ExternalSearchProvider(fetch_fn=lambda q: (429, ""),
                                     min_interval_s=0)
        comp = CompositeDiscoveryProvider([site, ext])
        result = run_v2(
            protocol,
            {"municipality": "Bamble", "municipality_number": None,
             "age": 22, "need": "mental_health_low_threshold",
             "urgency": "non_acute"},
            comp, fetch_provider=ReplayFetchProvider({}))
        self.assertEqual(result["execution_status"], "DISCOVERY_INCOMPLETE")
        self.assertTrue(result["provider_failures"])
        # composite returns the last provider's response per query; the
        # per-provider failure classes carry the BOT_BLOCKED evidence.
        chain = {h["provider"]: h["failure_class"]
                 for h in result["provider_chain"]}
        self.assertEqual(chain.get("site_direct"), "BOT_BLOCKED")
        self.assertEqual(chain.get("external_search"), "RATE_LIMITED")
        self.assertNotEqual(result["route_state"], "ROUTE_FULLY_VERIFIED")


if __name__ == "__main__":
    unittest.main()
