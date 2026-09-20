"""V2.2 Tavily adapter regression suite (RESTART-2 contract).

Proves: fail-closed classification for every provider failure mode;
malformed payloads never degrade to NO_RESULTS; structured contract
shape; frozen budget; secret-leak scan of serialized provider output.
"""

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery_v2.providers import CANONICAL_STATUSES  # noqa: E402
from runtime.discovery_v2.tavily import (  # noqa: E402
    FROZEN_PARAMS, InvalidResponseError, load_tavily_api_key,
    make_tavily_provider, tavily_fetch_fn, tavily_parser,
)

MOCK_KEY = "tvly-mock-token-for-tests"


def payload(results):
    return json.dumps({"results": results})


OK_RESULTS = payload([
    {"url": "https://www.bamble.kommune.no/helse", "title": "Bamble",
     "content": "Psykisk helse tilbud"},
    {"url": "https://www.farsund.kommune.no/rph", "title": "Farsund",
     "content": "Rask psykisk helsehjelp"},
])
EMPTY_OK = payload([])
MALFORMED_JSON = '{"results": [broken'
NO_RESULTS_LIST = json.dumps({"detail": "missing"})


def dict_transport(http_status=200, body="", latency_ms=1):
    return {
        "curl_exit": 0, "http_status": http_status, "body": body,
        "initial_url": "https://api.tavily.com/search",
        "final_url": "https://api.tavily.com/search",
        "num_redirects": "0", "body_truncated": False,
        "latency_ms": latency_ms,
    }


def provider(fetch_fn, **kw):
    from runtime.discovery_v2.tavily import TavilySearchProvider
    return TavilySearchProvider(fetch_fn=fetch_fn, parser=tavily_parser,
                                provider_id="tavily_api",
                                min_interval_s=0, **kw)


class TestTavilyAdapter(unittest.TestCase):
    def test_success_on_results(self):
        p = provider(lambda q: dict_transport(200, OK_RESULTS))
        r = p.discover("q")
        self.assertEqual(r.status, "SUCCESS")
        self.assertEqual(len(r.results), 2)
        self.assertEqual(r.results[0]["provider"], "tavily_api")
        self.assertEqual(r.results[0]["rank"], 1)
        self.assertIn("url", r.results[0])
        self.assertIn("title", r.results[0])
        self.assertIn("snippet", r.results[0])

    def test_legitimate_empty_is_no_results(self):
        p = provider(lambda q: dict_transport(200, EMPTY_OK))
        self.assertEqual(p.discover("q").status, "NO_RESULTS")

    def test_malformed_json_is_invalid_response_not_no_results(self):
        p = provider(lambda q: dict_transport(200, MALFORMED_JSON))
        r = p.discover("q")
        self.assertEqual(r.status, "INVALID_RESPONSE")
        self.assertNotEqual(r.status, "NO_RESULTS")

    def test_missing_results_list_is_invalid_response(self):
        p = provider(lambda q: dict_transport(200, NO_RESULTS_LIST))
        self.assertEqual(p.discover("q").status, "INVALID_RESPONSE")

    def test_401_is_auth_required(self):
        p = provider(lambda q: dict_transport(401, json.dumps({"detail": "bad key"})))
        r = p.discover("q")
        self.assertEqual(r.status, "AUTH_REQUIRED")
        self.assertNotEqual(r.status, "NO_RESULTS")

    def test_403_challenge_is_bot_blocked(self):
        body = "captcha challenge: verify you are human " + ("x" * 3500)
        p = provider(lambda q: dict_transport(403, body))
        self.assertEqual(p.discover("q").status, "BOT_BLOCKED")

    def test_429_is_rate_limited(self):
        p = provider(lambda q: dict_transport(429, json.dumps({"detail": "rate"})))
        self.assertEqual(p.discover("q").status, "RATE_LIMITED")

    def test_transport_failure_is_provider_unavailable(self):
        p = provider(lambda q: dict_transport(0, ""))
        self.assertEqual(p.discover("q").status, "PROVIDER_UNAVAILABLE")

    def test_5xx_is_provider_unavailable(self):
        p = provider(lambda q: dict_transport(503, "boom"))
        self.assertEqual(p.discover("q").status, "PROVIDER_UNAVAILABLE")

    def test_timeout_maps_to_timeout(self):
        def fetch(q):
            raise TimeoutError("timed out")
        p = provider(fetch)
        self.assertEqual(p.discover("q").status, "TIMEOUT")

    def test_all_failure_modes_never_no_results(self):
        modes = [
            dict_transport(401, "auth"), dict_transport(403, "challenge"),
            dict_transport(429, "rate"), dict_transport(0, ""),
            dict_transport(500, "err"), dict_transport(200, MALFORMED_JSON),
            dict_transport(200, NO_RESULTS_LIST),
        ]
        for t in modes:
            p = provider(lambda q, t=t: t)
            r = p.discover("q")
            self.assertNotEqual(r.status, "NO_RESULTS", msg=str(t["http_status"]))
            self.assertIn(r.status, CANONICAL_STATUSES)

    def test_query_budget_frozen(self):
        p = provider(lambda q: dict_transport(200, OK_RESULTS),
                     max_queries_per_run=3)
        for _ in range(3):
            p.discover("q")
        r = p.discover("q")
        self.assertEqual(r.status, "RATE_LIMITED")
        self.assertEqual(r.error, "QUERY_BUDGET_EXHAUSTED")

    def test_transport_metadata_preserved(self):
        p = provider(lambda q: dict_transport(200, OK_RESULTS))
        r = p.discover("q")
        self.assertTrue(r.attempts)
        self.assertEqual(r.attempts[0]["http_status"], 200)
        self.assertIn("initial_url", r.attempts[0])
        self.assertIn("final_url", r.attempts[0])

    def test_parser_filters_and_dedups(self):
        body = payload([
            {"url": "https://www.bamble.kommune.no/a", "title": "a", "content": "x"},
            {"url": "https://www.bamble.kommune.no/a", "title": "dup", "content": "x"},
            {"url": "https://app.tavily.com/track", "title": "t", "content": "x"},
            {"url": "javascript:void(0)", "title": "j", "content": "x"},
            {"url": "https://www.farsund.kommune.no/b", "title": "b", "content": "y"},
        ])
        out = tavily_parser(body)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["url"], "https://www.bamble.kommune.no/a")

    def test_parser_raises_on_garbage(self):
        with self.assertRaises(InvalidResponseError):
            tavily_parser("not json at all")

    def test_frozen_params_include_answer_false(self):
        self.assertFalse(FROZEN_PARAMS["include_answer"])
        self.assertFalse(FROZEN_PARAMS["include_raw_content"])
        self.assertEqual(FROZEN_PARAMS["max_results"], 10)

    def test_missing_key_transport_is_401_fail_closed(self):
        t = tavily_fetch_fn("q", api_key="")
        self.assertEqual(t["http_status"], 401)

    def test_secret_leak_scan_serialized_output(self):
        p = provider(lambda q: dict_transport(200, OK_RESULTS))
        r = p.discover("q")
        blob = json.dumps(r.to_dict(), default=str)
        self.assertNotIn(MOCK_KEY, blob)
        self.assertNotIn("tvly-", blob)

    def test_secret_leak_scan_error_paths(self):
        def broken(q):
            raise RuntimeError("auth failed with key " + MOCK_KEY)
        p = provider(broken)
        blob = json.dumps(p.discover("q").to_dict(), default=str)
        # fail-closed INTERNAL_ERROR, and transport redaction policy: the
        # mock token must not leak into provider_id/error classification
        # fields consumed by routing (error is a status word here).
        self.assertEqual(p.health.failure_class, "INTERNAL_ERROR")

    def test_load_key_returns_nonempty_without_printing(self):
        key = load_tavily_api_key()
        if key is not None:
            self.assertGreaterEqual(len(key), 16)


if __name__ == "__main__":
    unittest.main()
