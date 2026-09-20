"""Development CLI for the discovery runtime prototype.

Usage:
  python -m runtime.discovery.cli --municipality "Kommunenavn" --municipality-number 4012 \
      --age 22 --need mental_health_low_threshold --mode replay
"""

import argparse
import json
import sys
from pathlib import Path

from .protocol import ProtocolLoader
from .orchestrator import run_discovery


def main(argv=None):
    parser = argparse.ArgumentParser(description="NAV Explore Local Discovery Runtime V1")
    parser.add_argument("--municipality", required=True)
    parser.add_argument("--municipality-number", default=None)
    parser.add_argument("--age", type=int, default=None)
    parser.add_argument("--need", default="mental_health_low_threshold")
    parser.add_argument("--mode", choices=["replay", "live"], default="replay")
    parser.add_argument("--protocol", default="data/local-service-discovery-protocol-v1.json")
    parser.add_argument("--fixtures", default="evaluation/local-discovery-runtime-v1/fixtures/fixture-manifest.json")
    parser.add_argument("--output", default=None, help="Write result JSON to file")
    args = parser.parse_args(argv)

    protocol = ProtocolLoader(args.protocol).load()

    input_data = {
        "municipality": args.municipality,
        "municipality_number": args.municipality_number,
        "age": args.age,
        "need": args.need,
        "urgency": "non_acute",
    }

    if args.mode == "replay":
        fixture_path = Path(args.fixtures)
        if not fixture_path.exists():
            print("Fixture manifest not found: %s" % fixture_path, file=sys.stderr)
            sys.exit(2)
        with open(fixture_path, "r", encoding="utf-8") as f:
            fixtures = json.load(f)
        result = run_discovery(protocol, input_data, fixtures=fixtures, mode="replay")
    else:
        result = run_discovery(protocol, input_data, fixtures=None, mode="live")

    from .serialize import ResultSerializer
    output_json = ResultSerializer.serialize(result)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json + "\n")
    print(output_json)


if __name__ == "__main__":
    main()
