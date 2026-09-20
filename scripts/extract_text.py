#!/usr/bin/env python3
"""Extract readable text and keyword links from a downloaded HTML page."""
import html
import re
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: extract_text.py FILE [KEYWORDS...]", file=sys.stderr)
        raise SystemExit(2)
    path, *keywords = sys.argv
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", raw)
    links = re.findall(r'href="([^"]+)"[^>]*>([^<]{2,140})', raw)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(re.sub(r"\s+", " ", text))
    print(text[:7000])
    if keywords:
        print("---LINKS---")
        seen = set()
        for href, label in links:
            combined = (href + " " + label).lower()
            if any(k.lower() in combined for k in keywords):
                key = (href, label.strip())
                if key not in seen:
                    seen.add(key)
                    print(f"{href} :: {label.strip()}")


if __name__ == "__main__":
    main()
