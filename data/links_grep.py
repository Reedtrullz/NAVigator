#!/usr/bin/env python3
"""Print links on a page whose href or text matches keywords."""
import sys, re, html, subprocess

url = sys.argv[1]
kws = [k.lower() for k in sys.argv[2:]]
t = subprocess.run(["curl", "-s", "-L", "--max-time", "25", "-A", "Mozilla/5.0", url],
                   capture_output=True, text=True, timeout=30).stdout
base = re.match(r"(https?://[^/]+)", url).group(1)
seen = set()
for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, re.S | re.I):
    href, txt = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
    txt = html.unescape(re.sub(r"\s+", " ", txt)).strip()
    if href.startswith("/"):
        href = base + href
    blob = (href + " " + txt).lower()
    if any(k in blob for k in kws) and href not in seen and href.startswith("http"):
        seen.add(href)
        print(f"{txt[:80]} | {href}")
