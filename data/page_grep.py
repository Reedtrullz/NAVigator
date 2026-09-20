#!/usr/bin/env python3
import sys, re, html, subprocess

url = sys.argv[1]
kws = sys.argv[2:]
t = subprocess.run(["curl", "-s", "-L", "--max-time", "25", "-A", "Mozilla/5.0", url],
                   capture_output=True, text=True, timeout=30).stdout
t = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
t = re.sub(r"<[^>]+>", " ", t)
t = html.unescape(t)
t = re.sub(r"\s+", " ", t)
for kw in kws:
    m = re.search(re.escape(kw), t, re.I)
    if m:
        s = max(0, m.start() - 80)
        e = min(len(t), m.end() + 120)
        print(f"  [{kw}] ...{t[s:e].strip()}...")
    else:
        print(f"  [{kw}] NOT FOUND")
