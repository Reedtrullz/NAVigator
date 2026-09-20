import html as h
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.getcode(), r.read().decode("utf-8", "ignore")
    except Exception as e:
        return 0, str(e)


def text_of(raw):
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", " ", raw)))


PATS = r"(slik s\u00f8ker|slik søker|søkje|søker du|henvisning|tilvising|ta kontakt|ta direkte|sj\u00f8l|sj\u00f8lv|direkte|inntak|skjema)"

# Parent service page
code, raw = fetch("https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/")
print("parent", code)
txt = text_of(raw)
seen = set()
for m in re.finditer(PATS, txt, re.I):
    s, e = max(0, m.start() - 90), min(len(txt), m.end() + 120)
    key = txt[s:s + 60]
    if key not in seen:
        seen.add(key)
        print("   ..." + txt[s:e] + "...")

# Links from parent page to subpages
for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S | re.I):
    href, label = m.group(1), re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
    if re.search(r"psykisk|rus|hjelp|s\u00f8k|skjema", href + label, re.I):
        print("   LINK:", label[:50], "->", href[:110])
