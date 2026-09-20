#!/usr/bin/env bash
# Download a page and print extracted text plus keyword links.
# usage: pagegrab.sh URL OUTFILE KEYWORD [KEYWORD...]
set -euo pipefail
URL="$1"; OUT="$2"; shift 2
curl -sL --max-time 25 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" "$URL" -o "$OUT"
python3 - "$OUT" "$@" <<'PYEOF'
import sys, html, re
import os
path = sys.argv[1]
keywords = [k.lower() for k in sys.argv[2:]]
limit = int(os.environ.get('TEXT_LIMIT', '6500'))
raw = open(path, encoding='utf-8', errors='replace').read()
raw = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', raw)
links = re.findall(r'href="([^"]+)"[^>]*>([^<]{2,140})', raw)
text = re.sub(r'<[^>]+>', ' ', raw)
text = html.unescape(re.sub(r'\s+', ' ', text))
print(text[:limit])
print('---LINKS---')
seen = set()
for href, label in links:
    combined = (href + ' ' + label).lower()
    if any(k in combined for k in keywords):
        key = (href, label.strip())
        if key not in seen:
            seen.add(key)
            print(f'{href} :: {label.strip()}')
PYEOF
