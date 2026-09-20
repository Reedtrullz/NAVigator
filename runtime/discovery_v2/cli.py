"""Development CLI for discovery runtime V2.

Usage:
  python -m runtime.discovery_v2.cli --municipality "Kommunenavn" [--no-external]
"""

import argparse
import sys

from runtime.discovery.protocol import ProtocolLoader
from runtime.discovery.serialize import ResultSerializer

from .brave import make_brave_provider
from .orchestrator import run_v2
from .providers import CompositeDiscoveryProvider, SiteDirectProvider


class _FetchFnHttp:
    """Adapt V1 HttpFetchProvider to the (status_code, body) fetch_fn contract."""

    def __init__(self):
        from runtime.discovery.providers import HttpFetchProvider
        self.inner = HttpFetchProvider()

    def __call__(self, url):
        fr = self.inner.fetch(url)
        if fr.status == "success":
            return (200, fr.content or "")
        if fr.status == "render_required":
            return (200, "")
        m = re.search(r"HTTP (\d{3})", fr.error or "")
        return (int(m.group(1)) if m else 0, "")


def build_composite(municipality=None, external_enabled=True, roots=None):
    from .sitemap_fetch import bounded_fetch
    site = SiteDirectProvider(fetch_fn=_FetchFnHttp(), roots=roots,
                              sitemap_fetch_fn=bounded_fetch)
    providers = [site]
    if external_enabled:
        providers.append(make_brave_provider())
    return CompositeDiscoveryProvider(providers)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="NAV Explore Local Discovery Runtime V2")
    parser.add_argument("--municipality", required=True)
    parser.add_argument("--municipality-number", default=None)
    parser.add_argument("--age", type=int, default=None)
    parser.add_argument("--need", default="mental_health_low_threshold")
    parser.add_argument("--no-external", action="store_true",
                        help="Site-direct only (no external search fallback)")
    parser.add_argument("--protocol",
                        default="data/local-service-discovery-protocol-v1.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    protocol = ProtocolLoader(args.protocol).load()
    providers = build_composite(external_enabled=not args.no_external)
    input_data = {
        "municipality": args.municipality,
        "municipality_number": args.municipality_number,
        "age": args.age,
        "need": args.need,
        "urgency": "non_acute",
    }
    result = run_v2(protocol, input_data, providers)
    output_json = ResultSerializer.serialize(result)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json + "\n")
    print(output_json)


if __name__ == "__main__":
    main()
