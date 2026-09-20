"""Development CLI for discovery runtime V2.4 (root-resolution repair).

Usage:
  python -m runtime.discovery_v2.cli_v24 --municipality "Kommunenavn"

Thin V2.3 clone (new lineage): the only behavioral difference is the
canonical platform root from runtime.discovery_v2.roots_v24. No external
search provider exists on this path. Frozen V1 semantics are untouched.
"""

import argparse
import sys

from runtime.discovery.protocol import ProtocolLoader
from runtime.discovery.serialize import ResultSerializer

from .orchestrator import run_v2
from .cli_v23 import SiteDirectProviderV23, _FetchFnHttp
from .providers import CompositeDiscoveryProvider
from .render import RenderAwareFetchProvider, RenderFetchFn
from .roots_v24 import canonical_roots_v24


def build_v24_providers(municipality):
    site = SiteDirectProviderV23(
        fetch_fn=RenderFetchFn(_FetchFnHttp(), max_renders=4),
        roots=canonical_roots_v24(municipality))
    return CompositeDiscoveryProvider([site])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="NAV Explore Local Discovery Runtime V2.4")
    parser.add_argument("--municipality", required=True)
    parser.add_argument("--municipality-number", default=None)
    parser.add_argument("--age", type=int, default=None)
    parser.add_argument("--need", default="mental_health_low_threshold")
    parser.add_argument("--protocol",
                        default="data/local-service-discovery-protocol-v1.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    protocol = ProtocolLoader(args.protocol).load()
    providers = build_v24_providers(args.municipality)
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
