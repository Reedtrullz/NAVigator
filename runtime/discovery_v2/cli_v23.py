"""Development CLI for discovery runtime V2.3 (site-direct-only).

Usage:
  python -m runtime.discovery_v2.cli_v23 --municipality "Kommunenavn"

No external search provider exists on this path. Discovery is
root-pattern -> navigation -> sitemap, with bounded headless-Chrome render
fallback for SPA shells. Frozen V1 semantics are untouched.
"""

import argparse
import re
import sys

from runtime.discovery.protocol import ProtocolLoader
from runtime.discovery.serialize import ResultSerializer

from .orchestrator import run_v2
from .providers import CompositeDiscoveryProvider, SiteDirectProvider
from .render import RenderAwareFetchProvider, RenderFetchFn
from .roots import canonical_roots


class SiteDirectProviderV23(SiteDirectProvider):
    """V2.3 site-direct with a raised URL budget (16 vs frozen V2 default 8).

    A municipality can present several CMS-shell root variants before the
    working platform root, so the frozen V2 budget exhausts discovery before
    the first working candidate. The frozen SiteDirectProvider is untouched;
    V2.3 overrides the budget in this new-lineage subclass.
    """

    def __init__(self, fetch_fn, roots=None, provider_id="site_direct",
                 sitemap_fetch_fn=None):
        super().__init__(fetch_fn, roots=roots, provider_id=provider_id,
                         sitemap_fetch_fn=sitemap_fetch_fn)
        self._url_budget = 16


class _FetchFnHttp:
    """Adapt V1 HttpFetchProvider to the (status_code, body) contract."""

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


def build_v23_providers(municipality):
    site = SiteDirectProviderV23(
        fetch_fn=RenderFetchFn(_FetchFnHttp(), max_renders=4),
        roots=canonical_roots(municipality))
    return CompositeDiscoveryProvider([site])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="NAV Explore Local Discovery Runtime V2.3")
    parser.add_argument("--municipality", required=True)
    parser.add_argument("--municipality-number", default=None)
    parser.add_argument("--age", type=int, default=None)
    parser.add_argument("--need", default="mental_health_low_threshold")
    parser.add_argument("--protocol",
                        default="data/local-service-discovery-protocol-v1.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    protocol = ProtocolLoader(args.protocol).load()
    providers = build_v23_providers(args.municipality)
    input_data = {
        "municipality": args.municipality,
        "municipality_number": args.municipality_number,
        "age": args.age,
        "need": args.need,
        "urgency": "non_acute",
    }
    result = run_v2(protocol, input_data, providers,
                    fetch_provider=RenderAwareFetchProvider())
    output_json = ResultSerializer.serialize(result)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json + "\n")
    print(output_json)


if __name__ == "__main__":
    main()
