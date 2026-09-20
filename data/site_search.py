#!/usr/bin/env python3
"""Site-limited DuckDuckGo discovery helper (task NAV-EXPLORE-18-23-LOCAL-ROUTING-GAP-V1)."""
import sys, re, html, subprocess, urllib.parse

site = sys.argv[1]
query = " ".join(sys.argv[2:])
url = "https://html.duckduckgo.com/html/?q=" + re.sub(r"\\s+", "+", f"site:{site} {query}")
t = subprocess.run(["curl", "-s", "-L", "--max-time", "25", "-A",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", url],
                   capture_output=True, text=True, timeout=30).stdout
links = re.findall(r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)
seen = 0
for href, title in links:
    m = re.search(r"uddg=([^&]+)", href)
    if m:
        href = urllib.parse.unquote(m.group(1))
    title = re.sub(r"<[^>]+>", "", title)
    print(html.unescape(title).strip(), "|", href)
    seen += 1
    if seen >= 8:
        break
if not links:
    print("NO_RESULTS")
