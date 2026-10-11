from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from . import security
from runtime.discovery.providers import HttpFetchProvider
from runtime.discovery_v2.render import RenderFetchFn, render_url
from runtime.discovery_v2.providers_v25 import SiteDirectProviderV25


class HostPolicyTests(unittest.TestCase):
    def test_authority_requires_exact_domain_or_dot_boundary(self):
        self.assertEqual(security.is_official_domain("https://www.helsenorge.no/a"), "helsenorge")
        self.assertEqual(security.is_official_domain("https://city.kommune.no/a"), "municipal")
        self.assertEqual(security.is_official_domain("https://a.city.no/a", ["city.no"]), "municipal")
        for host in ("helsenorge.no.evil.example", "evilhelsenorge.no", "fakekommune.no", "helse-nord.evil.example", "partner.example", "evilcity.no"):
            self.assertEqual(security.is_official_domain("https://" + host, ["city.no"]), "private", host)

    def test_nonpublic_literals_credentials_controls_and_ports_are_denied(self):
        for url in ("http://[::ffff:127.0.0.1]/", "http://0.1.2.3/", "http://192.0.2.1/", "http://example.com:22/",
                    "http://user:pass@example.com/", "http://example.com/\nprivate", "http://example.com\\@public.example/"):
            with self.subTest(url=url), self.assertRaises(security.InvalidUrlError):
                security.validate_url(url)

    def fetch(self, url="http://public.example/", addresses=None, responses=None):
        fetch = getattr(security, "fetch_public", None)
        self.assertTrue(callable(fetch), "shared pinned transport required")
        assert callable(fetch)
        responses = responses or [(200, b"public body", None)]
        connections = []
        def connection(*args, **kwargs):
            status, body, location = responses[len(connections)]
            conn = Mock()
            conn.getresponse.return_value = SimpleNamespace(status=status, read=lambda size: body,
                                                            getheader=lambda name: location if name == "Location" else None)
            connections.append(conn)
            return conn
        addresses = addresses or ["93.184.216.34"]
        def resolve(host, port, **kwargs):
            values = addresses[host] if isinstance(addresses, dict) else addresses
            return [(2, 1, 6, "", (ip, port)) for ip in values]
        with patch.object(security.socket, "getaddrinfo", side_effect=resolve) as resolver, \
                patch.object(security.socket, "create_connection") as connect, \
                patch.object(security.http.client, "HTTPConnection", side_effect=connection), \
                patch.object(security.ssl, "create_default_context") as tls:
            result = fetch(url)
        return result, resolver, connect, tls, connections

    def test_private_and_mixed_dns_are_blocked_before_connection(self):
        fetch = getattr(security, "fetch_public", None)
        self.assertTrue(callable(fetch), "shared pinned transport required")
        assert callable(fetch)
        for ips in (["127.0.0.1"], ["93.184.216.34", "10.0.0.1"]):
            with self.subTest(ips=ips), patch.object(security.socket, "getaddrinfo", return_value=[(2, 1, 6, "", (ip, 80)) for ip in ips]), \
                    patch.object(security.socket, "create_connection") as connect:
                with self.assertRaises(security.InvalidUrlError):
                    fetch("http://public.example/")
                connect.assert_not_called()

    def test_connection_pins_ip_and_tls_keeps_original_hostname(self):
        result, resolver, connect, tls, conns = self.fetch("https://public.example/")
        self.assertIsInstance(result, tuple)
        assert isinstance(result, tuple)
        self.assertEqual(result[:2], (200, "public body"))
        self.assertEqual(resolver.call_count, 1)
        self.assertEqual(connect.call_args.args[0], ("93.184.216.34", 443))
        self.assertEqual(tls.return_value.wrap_socket.call_args.kwargs["server_hostname"], "public.example")
        self.assertEqual(conns[0].auto_open, 0)

    def test_dns_change_cannot_replace_pinned_connection_address(self):
        conn = Mock()
        conn.getresponse.return_value = SimpleNamespace(status=200, read=lambda size: b"ok")
        with patch.object(security.socket, "getaddrinfo", side_effect=[[(2, 1, 6, "", ("93.184.216.34", 80))],
                                                                     [(2, 1, 6, "", ("127.0.0.1", 80))]]) as resolve, \
                patch.object(security.socket, "create_connection") as connect, \
                patch.object(security.http.client, "HTTPConnection", return_value=conn):
            security.fetch_public("http://public.example/")
        self.assertEqual(resolve.call_count, 1)
        self.assertEqual(connect.call_args.args[0], ("93.184.216.34", 80))

    def test_public_redirect_checks_each_hop_and_body_is_bounded(self):
        result, resolve, connect, _tls, _conns = self.fetch(
            responses=[(302, b"", "http://other.example/a"), (200, b"ok", None)])
        self.assertEqual(result, (200, "ok", "http://other.example/a"))
        self.assertEqual(resolve.call_count, 2)
        self.assertEqual(connect.call_count, 2)
        for origin, target in (("https://public.example/", "https://other.example/a"),
                               ("https://public.example/", "/a"),
                               ("http://public.example/", "https://other.example/a")):
            with self.subTest(origin=origin, target=target):
                result, resolve, connect, _tls, _conns = self.fetch(
                    origin, responses=[(302, b"", target), (200, b"ok", None)])
                self.assertEqual(result, (200, "ok", security.urljoin(origin, target)))
                self.assertEqual(resolve.call_count, 2)
                self.assertEqual(connect.call_count, 2)
        conn = Mock()
        conn.getresponse.return_value = SimpleNamespace(status=200, read=lambda size: b"oversize")
        with patch.object(security.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 80))]), \
                patch.object(security.socket, "create_connection"), \
                patch.object(security.http.client, "HTTPConnection", return_value=conn), \
                self.assertRaises(security.InvalidUrlError):
            security.fetch_public("http://public.example/", max_size=3)

    def test_redirect_target_is_revalidated_before_second_connection(self):
        fetch = getattr(security, "fetch_public", None)
        self.assertTrue(callable(fetch), "shared pinned transport required")
        assert callable(fetch)
        initial = Mock()
        initial.getresponse.return_value = SimpleNamespace(status=302, getheader=lambda name: "http://127.0.0.1/private")
        with patch.object(security.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 80))]), \
                patch.object(security.socket, "create_connection") as connect, \
                patch.object(security.http.client, "HTTPConnection", return_value=initial):
            with self.assertRaises(security.InvalidUrlError):
                fetch("http://public.example/")
            self.assertEqual(connect.call_count, 1)

        for target in ("http://other.example/a", "HTTP://other.example/a"):
            with self.subTest(target=target):
                initial.getresponse.return_value = SimpleNamespace(status=302, getheader=lambda name: target)
                with patch.object(security.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))]), \
                        patch.object(security.socket, "create_connection") as connect, \
                        patch.object(security.http.client, "HTTPConnection", return_value=initial), \
                        patch.object(security.ssl, "create_default_context"):
                    with self.assertRaisesRegex(security.InvalidUrlError, "HTTPS redirect downgrade"):
                        fetch("https://public.example/")
                    self.assertEqual(connect.call_count, 1)

    def test_providers_share_transport_and_render_cannot_bypass_it(self):
        with patch("runtime.discovery.security.fetch_public", create=True, side_effect=security.InvalidUrlError("PRIVATE_ADDRESS")) as fetch, \
                patch("subprocess.run", side_effect=AssertionError("network outside pinned transport")):
            result = HttpFetchProvider().fetch("http://public.example/")
        self.assertEqual(result.status, "failed")
        self.assertEqual(fetch.call_count, 1)
        render = Mock(return_value=(200, "unsafe"))
        inner = Mock(return_value=(200, ""))
        wrapper = RenderFetchFn(inner, render_fn=render)
        self.assertEqual(wrapper("http://127.0.0.1/"), (0, ""))
        inner.assert_not_called()
        render.assert_not_called()
        site = SiteDirectProviderV25(inner, roots=["http://127.0.0.1/"], render_fn=render)
        self.assertEqual(site._rendered_nav_links("http://127.0.0.1/"), [])
        render.assert_not_called()
        with patch("subprocess.Popen") as launch:
            self.assertEqual(render_url("https://city.kommune.no/"), (0, ""))
        launch.assert_not_called()
